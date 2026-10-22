# Eval summary (chunk400)

run: 2026-10-21 23:59 · file: evals/questions.jsonl · backend: qwen3:4b-q4_K_M · fingerprint: nist|sha=7576edb531d9|size=400|overlap=75|embed=nomic-embed-text:v1.5|retriever=dense · 138s total

| Metric | Value |
|---|---|
| Recall@6 (any evidence page retrieved) | 14/14 |
| Recall@6 full (all evidence pages, 2-passage Qs count) | 14/14 |
| MRR | 0.82 |
| Citation support (answered Qs with >=1 citation, all retrieved) | 13/14 |
| Hallucinated citations (to pages never retrieved) | 0 |
| Correct abstentions | 5/6 |
| False abstentions (answerable but abstained) | 0/14 |
| Mean warm latency | 4.9s |
| Generation cost | $0 (local qwen3:4b-q4_K_M) |
