"""ask.py: answer one question from the NIST document with page citations, or abstain.

Why a CLI: evals/run_evals.py imports `answer()` so the exact same code path is scored.
"""
import argparse
import json
import os
import time
from pathlib import Path

import chromadb
import requests

from ingest import embed

OLLAMA = "http://localhost:11434"
GEN_MODEL = os.environ.get("GEN_MODEL", "qwen3.5:9b-q4_K_M")
ABSTAIN = "NOT IN DOCUMENTS"

SYSTEM = (
    "You answer questions using ONLY the numbered passages provided. "
    "Cite every claim as (doc, page) using the doc and page shown on the passage. "
    f"If the passages do not contain the answer, reply exactly: {ABSTAIN}"
)


def retrieve(question: str, collection: str = "nist_800", k: int = 6) -> list[dict]:
    """Return the k nearest chunks as dicts with id, doc, page, text.

    Why a plain list of dicts: evals need the ids and pages, the prompt needs the text,
    and neither should have to know Chroma's return shape.
    """
    client = chromadb.PersistentClient(path="./chroma_db")
    col = client.get_collection(collection)
    q = embed([question], prefix="search_query: ")[0]
    res = col.query(query_embeddings=[q], n_results=k, include=["documents", "metadatas", "distances"])
    out = []
    for cid, text, meta, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]):
        out.append({"id": cid, "doc": meta["doc"], "page": meta["page"], "text": text, "distance": dist})
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


def answer(question: str, collection: str = "nist_800", k: int = 6, passages: list[dict] | None = None) -> dict:
    """Full pipeline for one question; logs a record to runs.jsonl and returns it.

    `passages=[]` forces the no-context baseline used in evals.
    """
    t0 = time.time()
    if passages is None:
        passages = retrieve(question, collection, k)
    text, usage = generate_local(SYSTEM, build_prompt(question, passages))
    rec = {
        "ts": time.time(), "backend": GEN_MODEL, "collection": collection, "question": question,
        "retrieved_ids": [p["id"] for p in passages], "answer": text,
        "abstained": text.strip().upper().startswith(ABSTAIN),
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
