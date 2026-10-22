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
| No-context baseline, judged | correctness FAIL 4/5, groundedness FAIL 4/5 | the 5 deliberately bad answers; the one groundedness miss is a pipeline bug, see error analysis |
| Judge vs. 50 labels, correctness | TPR 20/20, TNR 5/5 | negatives: q14 plus 4 no-context fabrications |
| Judge vs. 50 labels, groundedness | TPR 20/20, TNR 4/5 | the miss is q01 no-context: the judge was shown the normalized sentinel instead of the raw fabrication |
| No-context baseline (5 answerable Qs, no passages) | 4/5 answered anyway | without retrieval the model invents answers; see bad answer 2 |
| Mean warm latency | ~5 s | first call after model load ~8 s |
| Generation cost | $0 | local |
| Judge cost | $0.0062 per full run | 40 Haiku calls, ~49k tokens, effort low |

"Accuracy" is deliberately absent: each row measures one failure mode.

### Second document: EU AI Act (144 pages, 960 chunks) added to the corpus

Seven new questions in `evals/questions_eu.jsonl` (5 single-document, 1 cross-document on how each text defines "risk", 1 false premise asking for "the fine for violating the NIST RMF"). Retrieval merges both collections by cosine distance. Local generator throughout.

| | NIST set, NIST only (baseline) | NIST set, both docs | EU set, both docs | EU set, EU only, dense | EU set, EU only, hybrid |
|---|---|---|---|---|---|
| Recall@6 | 14/14 | 13/14 | 5/6 | 4/6 | 3/6 |
| MRR | 0.90 | 0.88 | 0.40 | 0.32 | 0.22 |
| Citation support | 14/14 | 13/14 | 6/6 | 6/6 | 5/5 |
| Correct abstentions | 5/6 | 4/6* | 0/1 | 1/1 | 1/1 |

\* One of the two "misses" is a stale label: q16 ("What does the EU AI Act say about high-risk systems?") was unanswerable on the NIST-only corpus and is answerable now; the model answered it correctly from the EU text. The frozen set's `answerable` flags are relative to the NIST-only corpus and were not edited.

What the second document taught:

- **Retrieval is the bottleneck at 144 pages, not generation.** e03 ("from what date does the Act apply?") lives in Article 113 on p123; the six retrieved chunks were all recital pages (118–121) that discuss application dates in general terms. e04 (definition of "AI system") came back at rank 6 behind recital paraphrases, and the model cited the recital on p1 rather than Article 3. Legal texts say everything twice, once in recitals and once in articles, and the embedding cannot tell which is normative.
- **Hybrid retrieval failed again**, MRR 0.22 vs 0.32 on the EU document alone, despite the hypothesis that article numbers and defined terms would favour keyword search. Two negative results on two documents; BM25 is now a settled "no" for this project.
- **Cross-document leakage.** e07 asked for the maximum fine under the NIST RMF. The model recited the EU Act's fines from p117 ("up to EUR 1 500 000 ... EUR 750 000", which are the Article 100 fines for Union institutions, not even the headline Article 99 figures), then appended `NOT IN DOCUMENTS`. The citation rule correctly scores this as an answer, not an abstention.
- **Interference.** Adding the EU chunks pushed q07 (GOVERN 1.6) out of the NIST top-6 entirely; five of the six retrieved chunks were EU pages. Recall@6 of 14/14 on one document said nothing about two, which is the point the Chroma context-rot study makes at larger scale.

### Generator comparison: local 4B vs. Claude Haiku 5.5, identical retrieval and prompt

| | `qwen3:4b-q4_K_M` (local) | `claude-haiku-5-5` (API) |
|---|---|---|
| Recall@6 / MRR | 14/14 / 0.90 | same (retrieval is shared) |
| Citation support | 14/14 | 13/14 as run; 14/14 after the parser learned `(nist, page=25; nist, page=8)` |
| Correct abstentions | 5/6 | **6/6** (used the sentinel on the near-miss q17 where the local model abstained in prose) |
| False abstentions | 0/14 | 0/14 |
| Correctness PASS (judge) | 19/20 | 19/20, **same failure**: both chose MANAGE 4.1 over 2.4 on q14 |
| Groundedness PASS (judge) | 20/20 | 20/20 |
| Mean warm latency | 5.0 s | 3.4 s |
| Mean answer length | 57 tokens | 169 tokens |
| Generation cost, 20 answers | $0 | $0.005 |

On this document the hosted model buys one thing: reliable instruction-following on the abstention format. Content quality is indistinguishable at n=20, and both models made the identical subcategory error, which points at the retrieval order (p38 ranked above p37) or the reference answer rather than at either generator. The local model answers in a third of the tokens.

### Chunk-size sweep: dense retrieval, same generator, overlap held at ~19%

| | 400 / 75 (343 chunks) | **800 / 150 (177 chunks)** | 1200 / 225 (120 chunks) |
|---|---|---|---|
| Recall@6 | 14/14 | 14/14 | 13/14 |
| Recall@6, all evidence pages | 14/14 | 14/14 | 13/14 |
| MRR | 0.82 | **0.90** | 0.80 |
| Citation support | 13/14 | 14/14 | 14/14 |
| Correct / false abstentions | 5/6, 0/14 | 5/6, 0/14 | 5/6, 0/14 |
| Warm latency | 4.9 s | 5.0 s | 5.0 s |

800 wins on MRR and is the only setting with no retrieval or citation regressions. At **400**, the right page is still retrieved but the definition sentence gets split across chunk boundaries: on q08 the p13 chunk that came back did not contain the residual-risk definition, so the model wrote "the AI RMF does not explicitly define residual risk" without citing anything, a wrong answer that is neither an abstention nor a hallucination. At **1200**, fewer, longer chunks dilute the embedding: q08 lost p13 entirely and q10/q13 dropped to rank 2. Three settings on 20 questions is a direction, not a curve; full traces in `results/chunk400/` and `results/chunk1200/`.

### Retrieval ablation: dense vs. hybrid (BM25 + RRF), same chunks, same generator

| | Dense (nomic) | Hybrid (dense top-20 ∪ BM25 top-20, RRF k=60) |
|---|---|---|
| Recall@6 | 14/14 | 13/14 |
| Recall@6, all evidence pages | 14/14 | 12/14 |
| MRR | 0.90 | 0.81 |
| Citation support | 14/14 | 13/14 |
| Correct abstentions | 5/6 | 5/6 |

Hybrid **helped** the two subcategory-id questions (q07 GOVERN 1.6, q08 residual risk: rank 3 → 2) and **hurt** three semantic ones: q03 "how does the RMF define risk?" lost its page entirely because "risk" appears on every page and BM25 floods the fusion with high-frequency matches; both two-passage questions (q13, q14) lost their second evidence page to BM25 noise. On one document with this uniform a vocabulary, keyword search adds more noise than signal. Dense stays the default; hybrid is kept behind `--retriever hybrid` for the EU AI Act stretch, where article numbers and defined terms should favour it. Full traces in `results/hybrid/`.

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
| Definition split across chunk boundary → "not defined" answer with no citation | 1 | q08 at 400-char chunks | evidence that 400 is too small here; 800 kept |
| Judge shown the normalized `NOT IN DOCUMENTS` instead of the raw guess-then-abstain text | 1 | q01 no-context | judges now receive `raw_answer`; numbers above are as-run, before the fix |
| Citation parser missed `(nist, page=25; nist, page=8)` | 1 | q01, Claude backend | regex extended; reported both as-run and re-parsed |
| Same wrong subcategory from two different generators | 2 | q14, local and Claude | flagged for review of retrieval order and of the reference answer |
| Recital pages outrank the normative article (legal-text structure) | 2 | e03, e04 | candidate fix: metadata filter or boost for pages after the "HAVE ADOPTED THIS REGULATION" line |
| Cross-document leakage into a false-premise question | 1 | e07 | prompt experiment: name the document in the question or require per-doc citations |
| Second document displaces first document's evidence | 1 | q07 on corpus | per-document top-k then merge, or a reranker |

## Limitations

- 20 questions is far below the 100–200 per failure mode that judge validation properly needs. Treat every rate above as a smoke test, not an estimate.
- **The 40 labels in `results/frozen/labels.csv` were written by Claude (Fable 5.1, reading the passages), not by a human.** The author reviewed the approach but did not grade independently. So "judge validation" here means a stronger model agreeing with a cheaper one, which is weaker evidence than human labels. Two labels are marked DEBATABLE in the file (q14 correctness, q17 format).
- Negatives are still few: 5 for correctness, 5 for groundedness, all from the no-context baseline. TNR 5/5 and 4/5 are a first signal, not a rate.
- Tables split across pages lose their row label (GOVERN 4 spans physical pages 28–29). Page-bounded chunking is a deliberate trade for verifiable citations.
- Citations use physical PDF pages; NIST's printed page 1 is physical page 6.
- Two documents now, and the second one shows the first one's numbers were flattering: MRR drops to 0.40 on the EU set. The full-document baseline (whole PDF in one Haiku prompt) remains the honest comparison for the NIST document and is still a stretch item.
- Seven EU questions is a smoke test. Recital-vs-article confusion needs a dedicated question set to measure properly.

## Next steps

Re-run judges on raw answers (fix is in, numbers above predate it) → human re-grade of the 50 labels → article-vs-recital page filter for the EU document and re-score the EU set → per-document top-k merge to stop interference → more negatives (perturbed answers) as a second document with its own question file.

## How this maps to the AI RMF itself

The eval harness is the **MEASURE** function applied to the system that answers questions about MEASURE: test sets, metrics and tools are documented (MEASURE 2.1), performance is demonstrated under deployment-like conditions (2.3), and metric effectiveness is itself evaluated via judge validation (2.13). The abstention and citation checks are **MANAGE** controls: the system declines rather than guess (MANAGE 2.4, disengage when outcomes are inconsistent with intended use), and every answer is traceable to a page (MANAGE 4.1, monitoring and appeal).
