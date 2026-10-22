# Retros


## 2026-10-21 Milestones 1-3 (skeleton, ingest, ask)
- Preflight: `ollama run qwen3.5:9b` took 169 s because thinking mode was on; via API with `think:false` it was 14 s at 32 tok/s but 15% CPU spill at num_ctx 8192. Chose `qwen3:4b` (100% GPU, ~19 s cold / ~8 s warm). Rule added to CLAUDE.md.
- PDF: 48 physical pages, 177 chunks of 800/150. Extraction is clean on prose pages; tables not yet checked.
- First two questions: core functions answered with (nist, 25) citation; EU AI Act abstained correctly.
- Bug: abstention check used `startswith`; the model prefaces the token with a sentence. Changed to a contains check. Lesson: never assume a small model follows "reply exactly" literally; score on content, not position.
- Model cited as `(doc=nist, page=25)` not `(nist, 25)`; the citation parser in run_evals.py must accept both.
