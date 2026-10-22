# Eval summary (eu_only_hybrid)

run: 2026-10-22 00:44 · file: evals/questions_eu.jsonl · backend: qwen3:4b-q4_K_M · fingerprint: eu|sha=bba630444b32|size=800|overlap=150|embed=nomic-embed-text:v1.5|retriever=hybrid · 50s total

| Metric | Value |
|---|---|
| Recall@6 (any evidence page retrieved) | 3/6 |
| Recall@6 full (all evidence pages, 2-passage Qs count) | 3/6 |
| MRR | 0.22 |
| Citation support (answered Qs with >=1 citation, all retrieved) | 5/5 |
| Hallucinated citations (to pages never retrieved) | 0 |
| Correct abstentions | 1/1 |
| False abstentions (answerable but abstained) | 1/6 |
| Mean warm latency | 5.0s |
| Generation cost | $0 (local qwen3:4b-q4_K_M) |
