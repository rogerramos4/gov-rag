"""Guard the frozen test set: every evidence quote must really be on the cited physical page.

Why: a wrong page number would silently make Recall@6 report a miss that is the
labeller's fault, not the retriever's. This runs in pytest so it can never drift.
"""
import json
from pathlib import Path

import pytest

from ingest import load_pages

FILES = ["evals/questions.jsonl", "evals/dev_questions.jsonl"]


@pytest.fixture(scope="module")
def pages():
    return {n: " ".join(t.split()) for n, t in load_pages(Path("data/nist_ai_rmf.pdf"))}


def rows(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


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
            assert " ".join(e["quote"].split()) in pages[e["page"]], f'{q["id"]}: "{e["quote"]}" not on p{e["page"]}'
