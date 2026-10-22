# Eval summary (frozen)

run: 2026-10-22 00:28 · file: evals/questions.jsonl · backend: qwen3:4b-q4_K_M · fingerprint: nist|sha=7576edb531d9|size=800|overlap=150|embed=nomic-embed-text:v1.5|retriever=dense · 207s total

| Metric | Value |
|---|---|
| Recall@6 (any evidence page retrieved) | 14/14 |
| Recall@6 full (all evidence pages, 2-passage Qs count) | 14/14 |
| MRR | 0.90 |
| Citation support (answered Qs with >=1 citation, all retrieved) | 14/14 |
| Hallucinated citations (to pages never retrieved) | 0 |
| Correct abstentions | 5/6 |
| False abstentions (answerable but abstained) | 0/14 |
| Correctness PASS (judge) | 19/20 |
| Groundedness PASS (judge) | 20/20 |
| Judge calls unparsed or errored | 0 of 40 |
| Judge cost (total, claude-haiku-5-5) | $0.0062 for 48892 tokens |
| Mean warm latency | 5.0s |
| Generation cost | $0 (local qwen3:4b-q4_K_M) |
| No-context baseline: answered without abstaining | 4/5 of 5 |
| No-context baseline: judge FAILED groundedness (the negatives we want it to catch) | 4/5 |
| No-context baseline: judge FAILED correctness | 4/5 |
