# gov-rag

Question answering over the **NIST AI Risk Management Framework** with page citations, honest abstention, and a frozen evaluation set. Runs locally on an 8 GB GPU; no frameworks. Built to show retrieval **plus measurement**, not a chatbot.

Full write-up with error analysis: [`docs/writeup.md`](docs/writeup.md). Build log: [`docs/retros.md`](docs/retros.md).

## Results (frozen 20-question set, `qwen3:4b` local, 800-char chunks)

| Metric | Value |
|---|---|
| Recall@6 | 14/14 |
| MRR | 0.90 |
| Citation support (cited pages were retrieved) | 14/14, 0 hallucinated citations |
| Correct abstentions on unanswerable questions | 5/6 |
| False abstentions on answerable questions | 0/14 |
| Correctness PASS (Claude Haiku 5.5 judge) | 19/20 |
| Groundedness PASS (Claude Haiku 5.5 judge) | 20/20 |
| Mean warm latency | ~5 s · generation $0 · judge $0.006 per run |
| Hybrid BM25 + RRF (ablation, `--retriever hybrid`) | Recall 13/14, MRR 0.81: **worse** than dense on this document; see write-up |
| Chunk sweep (`--chunk 400` / `1200`) | MRR 0.82 / 0.80 vs **0.90** at 800; 400 splits definitions, 1200 dilutes embeddings |
| Claude Haiku 5.5 as generator (`--model claude`) | same correctness 19/20, abstentions 6/6 vs 5/6, 3.4 s, $0.005 per 20 answers |
| Judge vs. 50 labels (incl. 5 deliberately bad no-context answers) | correctness TNR 5/5, groundedness TNR 4/5 |

Not called "accuracy" on purpose: each row is one failure mode. Judge vs. 40 labels: 0 disagreements, but the labels were model-written and contain only one negative, so this validates little yet (see limitations in the write-up). `evals\judge_validation.py` computes TPR/TNR from `labels.csv`.

## Run it (Windows, PowerShell)

Prereqs: Python 3.12, [Ollama](https://ollama.com), an NVIDIA GPU with ~4 GB free.

```powershell
ollama pull nomic-embed-text:v1.5; ollama pull qwen3:4b-q4_K_M
py -3.12 -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe ingest.py
.\.venv\Scripts\python.exe evals\run_evals.py
```

Ask one question:

```powershell
.\.venv\Scripts\python.exe ask.py "What are the four core functions of the NIST AI RMF?"
```

Judges (optional, under $0.01 per run): set `$env:ANTHROPIC_API_KEY` in the same terminal and add `--judge`.

The PDF ships in `data/` with its SHA-256 in `data/hashes.txt`, so a clean clone reproduces the index fingerprint printed by `ingest.py`.

## Layout

```
ingest.py           PDF -> page-bounded chunks -> Ollama embeddings -> Chroma
ask.py              question -> top-6 -> cited answer or NOT IN DOCUMENTS
evals/questions.jsonl      frozen test set (never edited after first reported run)
evals/dev_questions.jsonl  5 scratch questions for tuning
evals/run_evals.py         Recall@6, MRR, citation support, abstention, PASS/FAIL judges
evals/rubrics.py           judge rubrics, verbatim
results/frozen/            per-question JSON traces, results.csv, summary.md, labels.csv
tests/                     chunking, scoring, and quote-on-page checks (pytest)
```

## Design choices

- **Page-bounded 800/150 chunks** so every citation names a page a human can open. Cost: tables that span pages lose their label (see limitations in the write-up).
- **Deterministic chunk ids and an index fingerprint** (`doc|sha|size|overlap|embed`) logged with every answer, so results from different builds cannot be confused.
- **Build-then-swap ingest**: a crashed run never destroys the previous index.
- **Binary PASS/FAIL judges, one per failure mode**, rubric text in the repo, backend hidden from the judge.
- **Hybrid retrieval measured, then not adopted**: BM25 fused with dense via reciprocal rank fusion helped questions with exact identifiers and hurt semantic ones; net negative on a single document with uniform vocabulary. Kept as an option, reported as a negative result.
- **Quotes verified by test**: every evidence quote in the question set must appear on its cited page, so a labelling slip cannot masquerade as a retrieval miss.

## Where this sits in the AI RMF

The evaluation harness is the framework's **MEASURE** function turned on itself: documented test sets and metrics (MEASURE 2.1), performance demonstrated under deployment-like conditions (2.3), and the metrics themselves checked against human labels (2.13). The abstention and citation controls are **MANAGE** outcomes: decline rather than guess (MANAGE 2.4) and keep every answer traceable (4.1).

## License

MIT. Personal learning project on a public document; not affiliated with NIST or any employer.
