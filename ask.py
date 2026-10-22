"""ask.py: answer one question from the NIST document with page citations, or abstain.

Why a CLI: evals/run_evals.py imports `answer()` so the exact same code path is scored.
"""
import argparse
import json
import os
import re
import time
from pathlib import Path

import chromadb
import requests

from ingest import embed

OLLAMA = "http://localhost:11434"
GEN_MODEL = os.environ.get("GEN_MODEL", "qwen3:4b-q4_K_M")  # 9B spilled 15% to CPU on the 5060; 4B is 100% GPU
ABSTAIN = "NOT IN DOCUMENTS"

SYSTEM = (
    "You answer questions using ONLY the numbered passages provided. "
    "Cite every claim as (doc, page) using the doc and page shown on the passage. "
    f"If the passages do not contain the answer, reply exactly: {ABSTAIN}"
)


RETRIEVER = os.environ.get("RETRIEVER", "dense")  # dense | hybrid
_BM25_CACHE: dict[str, tuple] = {}


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens for BM25. Why so simple: the doc is English prose and we
    want keyword matches like 'GOVERN 1.6' to survive; no stemming keeps it explainable."""
    return re.findall(r"[a-z0-9][a-z0-9.\-]*", text.lower())


def rrf(rankings: list[list[str]], k: int = 60) -> list[str]:
    """Reciprocal rank fusion: score(id) = sum over lists of 1 / (k + rank).

    Why RRF over score mixing: BM25 scores and cosine distances live on different
    scales; ranks are comparable, scores are not. k=60 is the standard constant.
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking, start=1):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=lambda c: (-scores[c], c))


def _bm25_index(col):
    """Build (or reuse) a BM25 index over every chunk in the collection."""
    from rank_bm25 import BM25Okapi
    if col.name not in _BM25_CACHE:
        allrows = col.get(include=["documents", "metadatas"])
        ids, docs, metas = allrows["ids"], allrows["documents"], allrows["metadatas"]
        _BM25_CACHE[col.name] = (BM25Okapi([tokenize(d) for d in docs]), ids, dict(zip(ids, docs)), dict(zip(ids, metas)))
    return _BM25_CACHE[col.name]


def retrieve(question: str, collection: str = "nist_800", k: int = 6, retriever: str | None = None) -> list[dict]:
    """Return the top-k chunks as dicts with id, doc, page, text.

    retriever='dense' queries Chroma only. 'hybrid' takes the top-20 from dense and the
    top-20 from BM25 and fuses them with RRF. Why a plain list of dicts: evals need the
    ids and pages, the prompt needs the text, and neither should know Chroma's shape.
    """
    retriever = retriever or RETRIEVER
    client = chromadb.PersistentClient(path="./chroma_db")
    col = client.get_collection(collection)
    fingerprint = (col.metadata or {}).get("fingerprint", collection) + f"|retriever={retriever}"
    pool = k if retriever == "dense" else 20
    q = embed([question], prefix="search_query: ")[0]
    res = col.query(query_embeddings=[q], n_results=pool, include=["documents", "metadatas", "distances"])
    dense = {cid: {"id": cid, "doc": m["doc"], "page": m["page"], "text": t, "distance": d, "fingerprint": fingerprint}
             for cid, t, m, d in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0])}
    if retriever == "dense":
        return list(dense.values())

    bm25, ids, text_of, meta_of = _bm25_index(col)
    scores = bm25.get_scores(tokenize(question))
    bm_rank = [ids[i] for i in sorted(range(len(ids)), key=lambda i: -scores[i])[:pool]]
    out = []
    for cid in rrf([list(dense), bm_rank])[:k]:
        if cid in dense:
            out.append(dense[cid])
        else:
            m = meta_of[cid]
            out.append({"id": cid, "doc": m["doc"], "page": m["page"], "text": text_of[cid], "distance": None, "fingerprint": fingerprint})
    return out


def build_prompt(question: str, passages: list[dict]) -> str:
    """Format passages so the model can cite them; returns the user turn."""
    blocks = [f"[{i}] (doc={p['doc']}, page={p['page']})\n{p['text']}" for i, p in enumerate(passages, 1)]
    return "PASSAGES:\n\n" + "\n\n".join(blocks) + f"\n\nQUESTION: {question}"


def generate_local(system: str, user: str) -> tuple[str, dict]:
    """Call Ollama /api/chat non-streaming. Returns (text, usage).

    Why stream=false: the default streams newline-delimited JSON, which breaks .json().
    """
    resp = requests.post(
        f"{OLLAMA}/api/chat",
        json={"model": GEN_MODEL, "stream": False, "think": False,
              "options": {"num_ctx": 8192, "temperature": 0},
              "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
        timeout=300,
    )
    resp.raise_for_status()
    j = resp.json()
    usage = {"tokens_in": j.get("prompt_eval_count"), "tokens_out": j.get("eval_count")}
    return j["message"]["content"].strip(), usage


BACKEND = os.environ.get("BACKEND", "local")  # local | claude
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-5-5")


def generate_claude(system: str, user: str) -> tuple[str, dict]:
    """Same prompt through the Claude API. Returns (text, usage).

    Why Haiku 5.5: it is the cheapest current Claude model, so the comparison is
    'small local model vs small hosted model', not 'small vs frontier'. Effort low keeps
    thinking short; max_tokens leaves room for thinking plus the answer.
    """
    import anthropic  # imported here so local-only runs never need the SDK configured
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=2048, output_config={"effort": "low"},
        system=system, messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    if resp.stop_reason == "refusal":
        text = f"(refusal: {getattr(resp.stop_details, 'category', None)})"
    return text, {"tokens_in": resp.usage.input_tokens, "tokens_out": resp.usage.output_tokens}


def backend_name() -> str:
    return CLAUDE_MODEL if BACKEND == "claude" else GEN_MODEL


# Matches "(nist, 25)", "(doc=nist, page=25)", "(nist, page 25)", "(nist, p. 25)", and
# several inside one parenthesis: "(nist, page=25; nist, page=8)". Extended 2026-10-22 after the
# Claude-backend run used the semicolon form; disclosed in docs/retros.md.
CITE_RE = re.compile(r"[(;]\s*(?:doc\s*=\s*)?([A-Za-z_]+)\s*,\s*(?:page\s*=?\s*|p\.?\s*)?(\d+)\s*(?=[);])", re.I)


def parse_citations(text: str) -> list[tuple[str, int]]:
    """Pull (doc, page) pairs out of an answer.

    Why tolerant: small models vary the format ("doc=nist, page=25" vs "nist, 25");
    punishing format instead of substance would measure the wrong thing.
    """
    return [(d.lower(), int(p)) for d, p in CITE_RE.findall(text)]


def classify_abstention(text: str) -> bool:
    """True only if the reply is an abstention, not an answer that merely mentions the token.

    Rule: the sentinel appears AND the reply cites no passage. A reply that cites a page is
    making a claim from the documents, so it is an answer even if it also says the token.
    (Changed 2026-10-21 after the first frozen run: the earlier 200-char limit wrongly
    rejected a long but correct abstention on q20. Disclosed in docs/retros.md.)
    """
    return ABSTAIN in text.upper() and not parse_citations(text)

def answer(question: str, collection: str = "nist_800", k: int = 6, passages: list[dict] | None = None) -> dict:
    """Full pipeline for one question; logs a record to runs.jsonl and returns it.

    `passages=[]` forces the no-context baseline used in evals.
    """
    t0 = time.time()
    if passages is None:
        passages = retrieve(question, collection, k)
    generate = generate_claude if BACKEND == "claude" else generate_local
    text, usage = generate(SYSTEM, build_prompt(question, passages))
    raw_text = text
    abstained = classify_abstention(text)
    if abstained:
        text = ABSTAIN  # normalize so downstream code sees the documented exact sentinel
    rec = {
        "ts": time.time(), "backend": backend_name(), "collection": collection,
        "fingerprint": passages[0]["fingerprint"] if passages else None, "question": question,
        "retrieved_ids": [p["id"] for p in passages], "answer": text, "raw_answer": raw_text,
        "abstained": abstained,
        **usage, "seconds": round(time.time() - t0, 2),
    }
    with Path("runs.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--collection", default="nist_800")
    ap.add_argument("-k", type=int, default=6)
    a = ap.parse_args()
    r = answer(a.question, a.collection, a.k)
    print(r["answer"])
    print(f"\n-- {r['backend']}  retrieved={r['retrieved_ids']}  in={r['tokens_in']} out={r['tokens_out']}  {r['seconds']}s")
