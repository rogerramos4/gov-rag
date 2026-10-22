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
