# Eval summary (claude)

run: 2026-10-22 00:31 · file: evals/questions.jsonl · backend: claude-haiku-5-5 · fingerprint: nist|sha=7576edb531d9|size=800|overlap=150|embed=nomic-embed-text:v1.5|retriever=dense · 150s total

| Metric | Value |
|---|---|
| Recall@6 (any evidence page retrieved) | 14/14 |
| Recall@6 full (all evidence pages, 2-passage Qs count) | 14/14 |
| MRR | 0.90 |
| Citation support (answered Qs with >=1 citation, all retrieved) | 13/14 |
| Hallucinated citations (to pages never retrieved) | 0 |
| Correct abstentions | 6/6 |
| False abstentions (answerable but abstained) | 0/14 |
| Correctness PASS (judge) | 19/20 |
| Groundedness PASS (judge) | 20/20 |
| Judge calls unparsed or errored | 0 of 40 |
| Judge cost (total, claude-haiku-5-5) | $0.0058 for 48557 tokens |
| Mean warm latency | 3.4s |
| Generation cost | $0.0050 for 20 answers (claude-haiku-5-5, 36080 tokens) |
