"""Guard the frozen test set: every evidence quote must really be on the cited physical page.

Why: a wrong page number would silently make Recall@6 report a miss that is the
labeller's fault, not the retriever's. This runs in pytest so it can never drift.
"""
import json
from pathlib import Path

import pytest

from ingest import load_pages

FILES = ["evals/questions.jsonl", "evals/dev_questions.jsonl", "evals/questions_eu.jsonl"]
PDFS = {"nist": "data/nist_ai_rmf.pdf", "eu": "data/eu_ai_act.pdf"}


@pytest.fixture(scope="module")
def pages():
    """{doc: {page: normalized text}} for every document the question files cite."""
    return {doc: {n: " ".join(t.split()) for n, t in load_pages(Path(pdf))} for doc, pdf in PDFS.items()}


def rows(path):
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_frozen_set_shape():
    qs = rows("evals/questions.jsonl")
    assert len(qs) == 20
    assert sum(q["answerable"] for q in qs) == 14
    assert len({q["id"] for q in qs}) == 20
    assert sum(q["kind"] == "multi" for q in qs) == 2
    for kind in ("off_topic", "near_miss", "false_premise"):
        assert sum(q["kind"] == kind for q in qs) == 2, kind


@pytest.mark.parametrize("path", FILES)
def test_evidence_matches_answerable(path):
    for q in rows(path):
        assert q["answerable"] == bool(q["evidence"]), q["id"]


@pytest.mark.parametrize("path", FILES)
def test_quotes_are_on_cited_pages(path, pages):
    for q in rows(path):
        for e in q["evidence"]:
            assert " ".join(e["quote"].split()) in pages[e["doc"]][e["page"]], f'{q["id"]}: "{e["quote"]}" not on {e["doc"]} p{e["page"]}'
