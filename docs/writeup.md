# gov-rag: retrieval over the NIST AI RMF, with evals

*Roger Ramos · 2026-10-21 · results from `results/frozen/` · one page*

## What it does

Answers questions about the NIST AI Risk Management Framework (AI RMF 1.0) from the PDF itself, cites the physical page for every claim, and replies exactly `NOT IN DOCUMENTS` when the answer is not there. A frozen 20-question set measures retrieval, citation honesty, correctness, groundedness and abstention separately. Everything runs locally on a consumer GPU; a Claude Haiku 5.5 judge is the only paid component.

## Architecture

1. `ingest.py`: pypdf text per physical page → 800-char chunks, 150 overlap, never across a page → `nomic-embed-text:v1.5` via Ollama → Chroma (cosine). 48 pages → 177 chunks in ~16 s warm.
2. `ask.py`: embed the question → top-6 chunks → `qwen3:4b-q4_K_M` via Ollama, thinking off, 8192 context → answer with `(doc, page)` citations or the abstention sentinel. Every call logged to `runs.jsonl` with an index fingerprint.
3. `evals/run_evals.py`: Recall@6 and MRR (code), citation support (code), abstention (code), correctness and groundedness as two separate PASS/FAIL judge calls (Claude Haiku 5.5, rubrics in `evals/rubrics.py`, backend name hidden).
4. No frameworks: `requests`, `chromadb`, `pypdf`, `anthropic`.

## Setup facts

| | |
|---|---|
| Document | NIST AI 100-1, sha256 `7576edb531d9…` (full hash in `data/hashes.txt`) |
| Index fingerprint | `nist\|sha=7576edb531d9\|size=800\|overlap=150\|embed=nomic-embed-text:v1.5` |
| Generator | `qwen3:4b-q4_K_M` (2.6 GB), 100% GPU. `qwen3.5:9b-q4_K_M` spilled 15% to CPU at 8192 context and was not used. |
| Judge | `claude-haiku-5-5`, effort low, max 256 output tokens |
| Test set | 20 questions: 14 answerable (10 single-page, 2 two-passage, 2 subcategory details), 6 unanswerable (2 off-topic, 2 near-miss, 2 false-premise). Frozen at commit `2dece60`. Every evidence quote is verified against the page text by pytest. |
| PC | Ryzen 5 5600X, 32 GB RAM, RTX 5060 8 GB, Windows 11, Python 3.12.10, Ollama 0.40.7, chromadb 1.5.9, pypdf 6.21.2, anthropic 2.1.0 |

## Results (frozen set, local generator)

| Metric | Value | Reads as |
|---|---|---|
| Recall@6 (an evidence page is among the 6 retrieved) | 14/14 | retrieval is not the bottleneck on one 48-page document |
| Recall@6, all evidence pages (2-passage questions must get both) | 14/14 | |
| MRR | 0.90 | evidence page is usually rank 1; twice it was rank 3 |
| Citation support (every cited page was actually retrieved) | 14/14 | |
| Hallucinated citations | 0 | |
| Correct abstentions | 5/6 | the miss is described below |
| False abstentions on answerable questions | 0/14 | |
| Correctness PASS (judge) | 19/20 | the FAIL is bad answer 3 below; the abstention miss on q17 still PASSED correctness, which is right: content, not format |
| Groundedness PASS (judge) | 20/20 | nothing stated beyond the passages, including on q14 where the content was wrong but traceable |
| Judge calls unparsed or errored | 0 of 40 | first judge run had 1 unparsed; see error analysis |
| Judge TPR / TNR vs. 40 hand labels | pending | `results/frozen/labels.csv`, sheet in `results/frozen/labels_sheet.md` |
| No-context baseline (5 answerable Qs, no passages) | 4/5 answered anyway | without retrieval the model invents answers; see bad answer 2 |
| Mean warm latency | ~5 s | first call after model load ~8 s |
| Generation cost | $0 | local |
| Judge cost | $0.0062 per full run | 40 Haiku calls, ~49k tokens, effort low |

"Accuracy" is deliberately absent: each row measures one failure mode.

## Two bad answers

**1. q17, near-miss: "What monetary penalty does the AI RMF impose on organizations that fail to comply?"**
> The provided documents do not mention any specific monetary penalty that the AI RMF imposes on organizations that fail to comply.

Substantively right, formally wrong: the model abstained in its own words and skipped the required sentinel, so the scorer counts it as an answer. A 4B model follows "reply exactly" loosely. Fix candidates: a one-shot example of the sentinel in the prompt, or a second-pass check; neither was applied before freezing these numbers.

**2. q01, no-context baseline: "What are the four core functions of the NIST AI RMF?"**
> The four core functions of the NIST AI RMF are: (1) Risk Management Framework (RMF) for AI, (2) Risk Assessment, (3) Risk Mitigation, and (4) Risk Monitoring. … Therefore, the answer is NOT IN DOCUMENTS.

With no passages the model fabricates four plausible-sounding functions (the real ones are GOVERN, MAP, MEASURE, MANAGE), then abstains anyway. This is exactly the behaviour retrieval plus citation checks exist to prevent, and the reason the groundedness judge is needed as a backstop: code alone sees the sentinel and calls this an abstention.

**3. q14, two-passage: "...which MANAGE subcategory covers deactivating such systems?"**
> The MANAGE subcategory that covers deactivating such systems is MANAGE 4.1, which involves post-deployment AI system monitoring plans, including … decommissioning … (doc=nist, page=38).

Reference is MANAGE 2.4 ("supersede, disengage, or deactivate AI systems"). The model chose a neighbouring subcategory that mentions "decommissioning", cited the page it actually read, and the groundedness judge correctly passed it while the correctness judge correctly failed it. This is why the two judges are separate: the answer is faithful to its source and still wrong.

## Error analysis (before any tuning)

| Failure | Count | Where | Drove |
|---|---|---|---|
| Soft abstention without sentinel | 1 | q17 | listed as the next prompt experiment; not changed |
| Scorer rejected a long, correct abstention (200-char rule) | 1 | q20 | scorer fixed to "sentinel present and no citations"; disclosed, question set untouched; 4/6 → 5/6 |
| Evidence page at rank 3 | 2 | q07, q08 | none yet; MRR 0.90 is acceptable |
| Guess-then-abstain counted as abstention | 1 | q01 no-context | groundedness judge is the backstop |
| Extra supported citation beyond the labelled evidence | 1 | q13 cited p35 too | none; it was retrieved and relevant |
| Plausible neighbouring subcategory (MANAGE 4.1 for 2.4) | 1 | q14 | none yet; candidate for the Claude-backend comparison |
| Judge returned no text (256-token cap consumed by Haiku's thinking) | 1 of 40 calls | q14 groundedness, first run | cap raised to 2048, stop_reason checked, unparsed calls now reported as their own row |

## Limitations

- 20 questions is far below the 100–200 per failure mode that judge validation properly needs. Treat every rate above as a smoke test, not an estimate.
- One judge model, one run; TPR/TNR against hand labels is the number that matters and is pending. Judge agreement with the code checks is encouraging (it failed the one wrong answer and passed the one soft abstention) but is not validation.
- Tables split across pages lose their row label (GOVERN 4 spans physical pages 28–29). Page-bounded chunking is a deliberate trade for verifiable citations.
- Citations use physical PDF pages; NIST's printed page 1 is physical page 6.
- One document. Recall@6 of 14/14 says little about corpus-scale retrieval; the full-document baseline (whole PDF in one Haiku prompt) is the honest comparison and is a stretch item.

## Next steps

Run the judges and label 40 answers → Claude backend row → hybrid BM25 + RRF row → chunk-size sweep (400 / 1200) → EU AI Act as a second document with its own question file.

## How this maps to the AI RMF itself

The eval harness is the **MEASURE** function applied to the system that answers questions about MEASURE: test sets, metrics and tools are documented (MEASURE 2.1), performance is demonstrated under deployment-like conditions (2.3), and metric effectiveness is itself evaluated via judge validation (2.13). The abstention and citation checks are **MANAGE** controls: the system declines rather than guess (MANAGE 2.4, disengage when outcomes are inconsistent with intended use), and every answer is traceable to a page (MANAGE 4.1, monitoring and appeal).
