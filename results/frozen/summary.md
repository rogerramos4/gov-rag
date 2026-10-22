# Eval summary (frozen)

run: 2026-10-21 22:22 · file: evals/questions.jsonl · backend: qwen3:4b-q4_K_M · fingerprint: nist|sha=7576edb531d9|size=800|overlap=150|embed=nomic-embed-text:v1.5 · 150s total

| Metric | Value |
|---|---|
| Recall@6 (any evidence page retrieved) | 14/14 |
| Recall@6 full (all evidence pages, 2-passage Qs count) | 14/14 |
| MRR | 0.90 |
| Citation support (answered Qs with >=1 citation, all retrieved) | 14/14 |
| Hallucinated citations (to pages never retrieved) | 0 |
| Correct abstentions | 5/6 |
| False abstentions (answerable but abstained) | 0/14 |
| Mean warm latency | 4.8s |
| Generation cost | $0 (local qwen3:4b-q4_K_M) |
| No-context baseline: answered without abstaining | 4/5 of 5 |
