# Retros


## 2026-10-21 Milestones 1-3 (skeleton, ingest, ask)
- Preflight: `ollama run qwen3.5:9b` took 169 s because thinking mode was on; via API with `think:false` it was 14 s at 32 tok/s but 15% CPU spill at num_ctx 8192. Chose `qwen3:4b` (100% GPU, ~19 s cold / ~8 s warm). Rule added to CLAUDE.md.
- PDF: 48 physical pages, 177 chunks of 800/150. Extraction is clean on prose pages; tables not yet checked.
- First two questions: core functions answered with (nist, 25) citation; EU AI Act abstained correctly.
- Bug: abstention check used `startswith`; the model prefaces the token with a sentence. Changed to a contains check. Lesson: never assume a small model follows "reply exactly" literally; score on content, not position.
- Model cited as `(doc=nist, page=25)` not `(nist, 25)`; the citation parser in run_evals.py must accept both.

## 2026-10-21 Codex review applied
- Applied: arg validation (overlap >= size would loop forever), build-then-swap collection so a crashed ingest never destroys the old index, ingestion fingerprint (doc|sha|size|overlap|embed model) stored on the collection and logged per answer, abstention classified (short, no citation) and normalized to the exact sentinel, tests use distinguishable text and cover invalid args.
- Deferred to run_evals.py by design: citation validation against retrieved pages (plan's "citation support" metric).
- Deferred to limitations: tables spanning pages (GOVERN 4 on p28-29) lose their label when split; page-bounded chunking is a deliberate trade for verifiable citations.
- Lesson: a second model reviewing finds process bugs (destructive-before-success) that a passing test suite hides.

## 2026-10-21 Milestone 4: frozen test set
- Roger asked me to write the questions rather than write them himself; trade-off noted (less content learning, faster to evals). 14 answerable (10 single-page lookups/details, 2 two-passage), 6 unanswerable (2 off-topic, 2 near-miss, 2 false-premise). 5 dev questions separate.
- Every evidence quote is checked by pytest against the actual page text, so a mislabelled page can never masquerade as a retrieval miss.
- Frozen at this commit. Do not edit evals/questions.jsonl after run_evals.py reports numbers.

## 2026-10-21 Milestone 5: run_evals.py, first frozen run
- Code-only metrics on qwen3:4b, 800/150 chunks: Recall@6 14/14, MRR 0.90, citation support 14/14, 0 hallucinated citations, correct abstentions 5/6, false abstentions 0/14, warm latency ~5 s. No-context baseline: 4/5 answered anyway (one invented four fake "core functions" then said NOT IN DOCUMENTS). Judges not yet run (no API key on this machine).
- Failure taxonomy (first run, 2 abstention misses): (a) q17 "soft abstention": said the documents do not mention a penalty but never used the sentinel -> scored as an answer. Left as-is; this is a real prompt-adherence failure of the 4B model. (b) q20: correct, long abstention rejected by an arbitrary 200-char rule in classify_abstention -> scorer bug.
- SCORER CHANGE AFTER SEEING FROZEN RESULTS (disclosed): classify_abstention now = sentinel present AND no citations parsed. Dropped the length rule. This moved q20 from miss to hit (4/6 -> 5/6). The question set was not touched. raw_answer is now logged so normalization never hides what the model actually said.
- Known scorer limitation: a reply that guesses and then abstains (q01 no-context) counts as an abstention. The groundedness judge is the backstop for that pattern.
- Judge rubrics live in evals/rubrics.py; Claude Haiku 5.5, effort low, binary PASS/FAIL per failure mode; results/frozen/labels.csv is the empty template for Roger's 40 hand labels.

## 2026-10-21 Milestones 6-7: write-up, README, clean-run
- Clean-run check passed: fresh clone into a scratch folder, new venv from requirements.txt, 19 tests pass, ingest gives the identical fingerprint, eval reproduces every number (14/14, 0.90, 14/14, 0, 5/6, 0/14). Latency 4.9 s vs 4.8 s.
- Still pending, blocked on an Anthropic API key: judge run (`--judge`), 40 hand labels in results/frozen/labels.csv, TPR/TNR row. Not yet pushed to GitHub (no remote; Roger's call, and check KPMG outside-activities policy first).

## 2026-10-21 Judge run
- Haiku 5.5 judges: correctness 19/20, groundedness 20/20, $0.006 for 40 calls. The one FAIL (q14, MANAGE 4.1 vs 2.4) is a genuine wrong answer that is nonetheless grounded in a retrieved page; the two judges disagreeing on it is the whole argument for separate failure modes.
- First judge run had 1 UNPARSED of 40: max_tokens=256 was consumed by Haiku 5.5's default thinking, leaving no text block. Fixed: max_tokens 2048, stop_reason checked, and unparsed/errored calls are now a reported row instead of silently shrinking the denominator. Lesson: when a model thinks by default, budget output tokens for the thinking, not just the answer.
- labels_sheet.md generated with judge verdicts hidden so Roger's 40 labels are independent.
- Roger pasted the API key into chat twice; told him to rotate it.

## 2026-10-21 Labels and judge validation
- Roger could not grade the 20 answers tonight (dense material, late). Claude Fable 5.1 wrote all 40 labels from the passages; disclosed in writeup limitations and in labels.csv notes. Two marked DEBATABLE (q14 correctness, q17 format).
- judge_validation.py: correctness TPR 19/19, TNR 1/1; groundedness TPR 20/20, TNR n/a. Zero disagreements. Honest reading: the judge was never tested on an ungrounded answer. Next: label and judge the 5 no-context outputs, which are real negatives.
- Lesson: a test set with no negatives for a failure mode cannot validate a judge for that mode, no matter how good the agreement looks.
