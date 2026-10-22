"""run_evals.py: score the frozen question set and write results/.

Why a separate runner: ask.py answers one question; this measures the whole system
the same way every time so numbers in the write-up are reproducible.

Usage (from the project root):
  .\\.venv\\Scripts\\python.exe evals\\run_evals.py            # code-only metrics
  .\\.venv\\Scripts\\python.exe evals\\run_evals.py --judge    # + Claude Haiku judges
  .\\.venv\\Scripts\\python.exe evals\\run_evals.py --file evals/dev_questions.jsonl --tag dev
"""
import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ask import ABSTAIN, answer, parse_citations, retrieve  # noqa: E402
from rubrics import CORRECTNESS, GROUNDEDNESS  # noqa: E402

JUDGE_MODEL = "claude-haiku-5-5"
# Claude Haiku 5.5 list price per million tokens (prompts <= 100K). Used only for reporting.
JUDGE_PRICE_IN, JUDGE_PRICE_OUT = 0.10, 0.50

def retrieval_scores(retrieved_pages: list[int], evidence_pages: list[int]) -> dict:
    """Recall@k (any evidence page retrieved), full coverage, and reciprocal rank.

    Why page-level: evidence is labelled by page, and a chunk from the right page
    is what a reader would need to verify the answer.
    """
    if not evidence_pages:
        return {"recall_any": None, "recall_all": None, "rr": None}
    hits = [p for p in evidence_pages if p in retrieved_pages]
    first_rank = next((i + 1 for i, p in enumerate(retrieved_pages) if p in evidence_pages), None)
    return {
        "recall_any": bool(hits),
        "recall_all": len(hits) == len(set(evidence_pages)),
        "rr": (1.0 / first_rank) if first_rank else 0.0,
    }


def citation_support(answer_text: str, passages: list[dict]) -> dict:
    """Every cited (doc, page) must be among the retrieved passages.

    Why: a citation to a page the model never saw is a hallucinated citation,
    even if the page happens to be right.
    """
    cites = parse_citations(answer_text)
    retrieved = {(p["doc"], p["page"]) for p in passages}
    unsupported = [c for c in cites if c not in retrieved]
    return {"n_citations": len(cites), "n_unsupported": len(unsupported), "unsupported": unsupported,
            "supported": (len(cites) > 0 and not unsupported)}


def judge(client, rubric: str, user_block: str) -> dict:
    """One Pass/Fail judge call. Returns verdict, reason, token usage.

    Why hide the backend name: the judge must not know which model it is grading.
    """
    import anthropic  # local import so code-only runs never need the SDK configured
    try:
        resp = client.messages.create(
            model=JUDGE_MODEL, max_tokens=2048, output_config={"effort": "low"},  # Haiku 5.5 thinks first; 256 starved the text block once
            system=rubric, messages=[{"role": "user", "content": user_block}],
        )
    except anthropic.APIStatusError as e:
        return {"verdict": "ERROR", "reason": f"{e.status_code}: {e.message}", "tokens_in": 0, "tokens_out": 0}
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    if resp.stop_reason == "max_tokens" and not text:
        text = f"(no text: stop_reason=max_tokens after {resp.usage.output_tokens} output tokens)"
    verdict = "PASS" if text.upper().startswith("PASS") else "FAIL" if text.upper().startswith("FAIL") else "UNPARSED"
    return {"verdict": verdict, "reason": text, "tokens_in": resp.usage.input_tokens, "tokens_out": resp.usage.output_tokens}


def fmt_passages(passages: list[dict]) -> str:
    return "\n\n".join(f"[{i}] (doc={p['doc']}, page={p['page']})\n{p['text']}" for i, p in enumerate(passages, 1)) or "(none)"


def run_one(q: dict, client, out_dir: Path, no_context: bool = False, collection: str = "nist_800") -> dict:
    """Answer one question, score it, save the full trace as JSON."""
    rec = answer(q["question"], collection=collection, passages=[] if no_context else None)
    # Re-fetch passage objects for scoring (answer() only logs ids).
    passages = [] if no_context else retrieve(q["question"], collection)
    retrieved_pages = [p["page"] for p in passages]
    evidence_pages = [e["page"] for e in q["evidence"]]

    row = {
        "id": q["id"] + ("_noctx" if no_context else ""), "kind": q["kind"] + ("/no-context" if no_context else ""), "answerable": q["answerable"], "question": q["question"],
        "answer": rec["answer"], "raw_answer": rec["raw_answer"], "abstained": rec["abstained"], "backend": rec["backend"],
        "fingerprint": rec.get("fingerprint"), "seconds": rec["seconds"],
        "tokens_in": rec["tokens_in"], "tokens_out": rec["tokens_out"],
        "retrieved_ids": rec["retrieved_ids"], "retrieved_pages": retrieved_pages, "evidence_pages": evidence_pages,
        **retrieval_scores(retrieved_pages, evidence_pages),
        **citation_support(rec["answer"], passages),
        "correct_abstention": (not q["answerable"]) and rec["abstained"],
        "false_abstention": q["answerable"] and rec["abstained"],
        "judge_correct": None, "judge_grounded": None, "judge_reason_correct": "", "judge_reason_grounded": "",
        "judge_tokens_in": 0, "judge_tokens_out": 0,
    }

    if client is not None:
        c = judge(client, CORRECTNESS,
                  f"QUESTION: {q['question']}\n\nREFERENCE ANSWER: {q['reference_answer']}\n\nSYSTEM ANSWER: {rec['answer']}")
        g = judge(client, GROUNDEDNESS,
                  f"PASSAGES:\n{fmt_passages(passages)}\n\nSYSTEM ANSWER: {rec['answer']}")
        row.update(judge_correct=c["verdict"], judge_grounded=g["verdict"],
                   judge_reason_correct=c["reason"], judge_reason_grounded=g["reason"],
                   judge_tokens_in=c["tokens_in"] + g["tokens_in"], judge_tokens_out=c["tokens_out"] + g["tokens_out"])

    (out_dir / f"{q['id']}{'_noctx' if no_context else ''}.json").write_text(
        json.dumps({**row, "passages": passages, "reference_answer": q["reference_answer"]}, indent=2), encoding="utf-8")
    return row


def summarize(rows: list[dict], noctx_rows: list[dict]) -> str:
    """Build the markdown summary table. Never call anything here 'accuracy'."""
    ans = [r for r in rows if r["answerable"]]
    una = [r for r in rows if not r["answerable"]]
    n_a, n_u = len(ans), len(una)
    rate = lambda xs: f"{sum(xs)}/{len(xs)}" if xs else "n/a"
    judged = [r for r in rows if r["judge_correct"] in ("PASS", "FAIL")]
    unparsed = sum(1 for r in rows for k in ("judge_correct", "judge_grounded") if r[k] in ("UNPARSED", "ERROR"))
    lines = [
        "| Metric | Value |", "|---|---|",
        f"| Recall@6 (any evidence page retrieved) | {rate([r['recall_any'] for r in ans])} |",
        f"| Recall@6 full (all evidence pages, 2-passage Qs count) | {rate([r['recall_all'] for r in ans])} |",
        f"| MRR | {sum(r['rr'] for r in ans) / n_a:.2f} |" if n_a else "| MRR | n/a |",
        f"| Citation support (answered Qs with >=1 citation, all retrieved) | {rate([r['supported'] for r in ans if not r['abstained']])} |",
        f"| Hallucinated citations (to pages never retrieved) | {sum(r['n_unsupported'] for r in rows)} |",
        f"| Correct abstentions | {rate([r['correct_abstention'] for r in una])} |",
        f"| False abstentions (answerable but abstained) | {rate([r['false_abstention'] for r in ans])} |",
    ]
    if judged:
        lines += [
            f"| Correctness PASS (judge) | {rate([r['judge_correct'] == 'PASS' for r in judged])} |",
            f"| Groundedness PASS (judge) | {rate([r['judge_grounded'] == 'PASS' for r in rows if r['judge_grounded'] in ('PASS', 'FAIL')])} |",
            f"| Judge calls unparsed or errored | {unparsed} of {2 * len(rows)} |",
        ]
        jin = sum(r["judge_tokens_in"] for r in rows); jout = sum(r["judge_tokens_out"] for r in rows)
        cost = jin / 1e6 * JUDGE_PRICE_IN + jout / 1e6 * JUDGE_PRICE_OUT
        lines.append(f"| Judge cost (total, {JUDGE_MODEL}) | ${cost:.4f} for {jin + jout} tokens |")
    secs = [r["seconds"] for r in rows[1:]]  # drop first (cold) call
    lines.append(f"| Mean warm latency | {sum(secs) / len(secs):.1f}s |" if secs else "| Mean warm latency | n/a |")
    backend = rows[0]["backend"]
    if backend.startswith("claude"):
        gin = sum(r["tokens_in"] or 0 for r in rows); gout = sum(r["tokens_out"] or 0 for r in rows)
        gcost = gin / 1e6 * JUDGE_PRICE_IN + gout / 1e6 * JUDGE_PRICE_OUT  # Haiku 5.5 prices; adjust if CLAUDE_MODEL changes
        lines.append(f"| Generation cost | ${gcost:.4f} for {len(rows)} answers ({backend}, {gin + gout} tokens) |")
    else:
        lines.append(f"| Generation cost | $0 (local {backend}) |")
    if noctx_rows:
        lines.append(f"| No-context baseline: answered without abstaining | {rate([not r['abstained'] for r in noctx_rows])} of {len(noctx_rows)} |")
        nj = [r for r in noctx_rows if r["judge_grounded"] in ("PASS", "FAIL")]
        if nj:
            lines.append(f"| No-context baseline: judge FAILED groundedness (the negatives we want it to catch) | {rate([r['judge_grounded'] == 'FAIL' for r in nj])} |")
            lines.append(f"| No-context baseline: judge FAILED correctness | {rate([r['judge_correct'] == 'FAIL' for r in nj])} |")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="evals/questions.jsonl")
    ap.add_argument("--tag", default="frozen", help="results subfolder name")
    ap.add_argument("--judge", action="store_true", help="run Claude Haiku Pass/Fail judges (needs ANTHROPIC_API_KEY)")
    ap.add_argument("--no-context-baseline", type=int, default=5, help="answerable Qs to run with no passages (0 to skip)")
    ap.add_argument("--retriever", choices=["dense", "hybrid"], default=None, help="override RETRIEVER env (dense | hybrid)")
    ap.add_argument("--chunk", type=int, default=800, help="chunk size; selects collection nist_<size>")
    ap.add_argument("--model", choices=["local", "claude"], default=None, help="generator backend (default: BACKEND env or local)")
    args = ap.parse_args()
    import ask
    if args.retriever:
        ask.RETRIEVER = args.retriever
    if args.model:
        ask.BACKEND = args.model
    collection = f"nist_{args.chunk}"

    qs = [json.loads(l) for l in (ROOT / args.file).read_text(encoding="utf-8").splitlines() if l.strip()]
    out_dir = ROOT / "results" / args.tag
    out_dir.mkdir(parents=True, exist_ok=True)

    client = None
    if args.judge:
        import anthropic
        client = anthropic.Anthropic()

    t0 = time.time()
    rows = []
    for q in qs:
        rows.append(run_one(q, client, out_dir, collection=collection))
        r = rows[-1]
        flag = "ABSTAIN" if r["abstained"] else f"cites={r['n_citations']} unsupported={r['n_unsupported']}"
        print(f"{q['id']} {q['kind']:<14} recall={r['recall_any']} rr={r['rr']} {flag} {r['seconds']}s", file=sys.stderr)

    noctx = []
    for q in [q for q in qs if q["answerable"]][: args.no_context_baseline]:
        # Judged too: these are the deliberately bad answers that give the judge real negatives.
        noctx.append(run_one(q, client, out_dir, no_context=True, collection=collection))
        print(f"{q['id']} no-context -> {'ABSTAIN' if noctx[-1]['abstained'] else 'answered anyway'}", file=sys.stderr)

    fields = [k for k in rows[0] if k not in ("retrieved_ids", "unsupported")]
    with (out_dir / "results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows + noctx)

    labels = out_dir / "labels.csv"
    if not labels.exists():  # never overwrite hand labels
        with labels.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["id", "human_correct", "human_grounded", "note"])
            for r in rows + noctx: w.writerow([r["id"], "", "", ""])

    summary = summarize(rows, noctx)
    meta = f"run: {time.strftime('%Y-%m-%d %H:%M')} · file: {args.file} · backend: {rows[0]['backend']} · fingerprint: {rows[0]['fingerprint']} · {time.time() - t0:.0f}s total"
    (out_dir / "summary.md").write_text(f"# Eval summary ({args.tag})\n\n{meta}\n\n{summary}\n", encoding="utf-8")
    print(f"\n{meta}\n\n{summary}\n\nwrote {out_dir}")


if __name__ == "__main__":
    main()
