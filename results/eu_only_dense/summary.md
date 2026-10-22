# Eval summary (eu_only_dense)

run: 2026-10-22 00:43 · file: evals/questions_eu.jsonl · backend: qwen3:4b-q4_K_M · fingerprint: eu|sha=bba630444b32|size=800|overlap=150|embed=nomic-embed-text:v1.5|retriever=dense · 51s total

| Metric | Value |
|---|---|
| Recall@6 (any evidence page retrieved) | 4/6 |
| Recall@6 full (all evidence pages, 2-passage Qs count) | 4/6 |
| MRR | 0.32 |
| Citation support (answered Qs with >=1 citation, all retrieved) | 6/6 |
| Hallucinated citations (to pages never retrieved) | 0 |
| Correct abstentions | 1/1 |
| False abstentions (answerable but abstained) | 0/6 |
| Mean warm latency | 5.3s |
| Generation cost | $0 (local qwen3:4b-q4_K_M) |
