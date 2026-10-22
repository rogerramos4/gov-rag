# gov-rag

RAG system over the NIST AI Risk Management Framework (data/nist_ai_rmf.pdf) with a frozen
evaluation set. Portfolio project: retrieval + evals + measured trade-offs, not a chatbot.

## Layout
- `ingest.py`   PDF -> page-bounded 800-char chunks -> nomic embeddings (Ollama) -> Chroma
- `ask.py`      question -> top-6 retrieval -> cited answer, or exactly `NOT IN DOCUMENTS`
- `evals/questions.jsonl`      frozen 20-question test set (14 answerable, 6 unanswerable). NEVER edit after first reported run.
- `evals/dev_questions.jsonl`  5 scratch questions for tuning, never reported
- `evals/run_evals.py`         Recall@6, MRR, citation support, Pass/Fail judges, abstention -> results/
- `results/`    results.csv + one JSON per question
- `docs/retros.md`, `docs/writeup.md`
- `tests/`      pytest

## Rules
- No frameworks (no LangChain/LlamaIndex). `requests` + `chromadb` + `pypdf` + `anthropic` only.
- Always run Python as `.\.venv\Scripts\python.exe` (no activation).
- Every function has a docstring that says WHY it exists, not just what it does.
- Every HTTP call has a timeout and `raise_for_status()`.
- Ollama: embeddings `nomic-embed-text:v1.5` with `search_document:` / `search_query:` prefixes;
  generation `qwen3.5:9b-q4_K_M` (fallback `qwen3:4b-q4_K_M`), `num_ctx` 8192, `stream: false`.
- Cite PHYSICAL PDF pages from 1 (NIST printed page 1 = physical page 6).
- Run `.\.venv\Scripts\python.exe -m pytest` before saying anything is done.
- Append a short retro to `docs/retros.md` at the end of each milestone.
- Explain briefly as you go; Roger is learning Python/RAG/PowerShell.
