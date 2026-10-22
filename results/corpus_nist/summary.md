# Eval summary (corpus_nist)

run: 2026-10-22 00:42 · file: evals/questions.jsonl · backend: qwen3:4b-q4_K_M · fingerprint: nist|sha=7576edb531d9|size=800|overlap=150|embed=nomic-embed-text:v1.5+eu|sha=bba630444b32|size=800|overlap=150|embed=nomic-embed-text:v1.5|retriever=dense · 142s total

| Metric | Value |
|---|---|
| Recall@6 (any evidence page retrieved) | 13/14 |
| Recall@6 full (all evidence pages, 2-passage Qs count) | 13/14 |
| MRR | 0.88 |
| Citation support (answered Qs with >=1 citation, all retrieved) | 13/14 |
| Hallucinated citations (to pages never retrieved) | 0 |
| Correct abstentions | 4/6 |
| False abstentions (answerable but abstained) | 0/14 |
| Mean warm latency | 5.1s |
| Generation cost | $0 (local qwen3:4b-q4_K_M) |
