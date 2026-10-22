# Eval summary (eu)

run: 2026-10-22 00:40 · file: evals/questions_eu.jsonl · backend: qwen3:4b-q4_K_M · fingerprint: nist|sha=7576edb531d9|size=800|overlap=150|embed=nomic-embed-text:v1.5+eu|sha=bba630444b32|size=800|overlap=150|embed=nomic-embed-text:v1.5|retriever=dense · 54s total

| Metric | Value |
|---|---|
| Recall@6 (any evidence page retrieved) | 5/6 |
| Recall@6 full (all evidence pages, 2-passage Qs count) | 4/6 |
| MRR | 0.40 |
| Citation support (answered Qs with >=1 citation, all retrieved) | 6/6 |
| Hallucinated citations (to pages never retrieved) | 0 |
| Correct abstentions | 0/1 |
| False abstentions (answerable but abstained) | 0/6 |
| Mean warm latency | 5.5s |
| Generation cost | $0 (local qwen3:4b-q4_K_M) |
