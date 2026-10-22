"""Scoring logic tests: no Ollama, no Chroma, no API."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))

from run_evals import citation_support, parse_citations, retrieval_scores  # noqa: E402


def test_parse_citation_formats():
    text = "A (nist, 25). B (doc=nist, page=12). C (nist, page 7). D (NIST, p. 3). E (nist,  9 )."
    assert parse_citations(text) == [("nist", 25), ("nist", 12), ("nist", 7), ("nist", 3), ("nist", 9)]


def test_parse_ignores_non_citations():
    assert parse_citations("See section (3.2) and Figure (5) and (2022)") == []


def test_retrieval_scores_single_evidence():
    s = retrieval_scores([10, 25, 30], [25])
    assert s["recall_any"] and s["recall_all"] and s["rr"] == 0.5


def test_retrieval_scores_two_passage_partial():
    s = retrieval_scores([30, 13, 2], [13, 37])
    assert s["recall_any"] and not s["recall_all"] and s["rr"] == 0.5


def test_retrieval_scores_miss_and_unanswerable():
    assert retrieval_scores([1, 2], [9]) == {"recall_any": False, "recall_all": False, "rr": 0.0}
    assert retrieval_scores([1, 2], []) == {"recall_any": None, "recall_all": None, "rr": None}


def test_citation_support_flags_unretrieved_page():
    passages = [{"doc": "nist", "page": 25}, {"doc": "nist", "page": 26}]
    ok = citation_support("Four functions (nist, 25).", passages)
    assert ok["supported"] and ok["n_unsupported"] == 0
    bad = citation_support("Four functions (nist, 25) and fines (nist, 9999).", passages)
    assert not bad["supported"] and bad["unsupported"] == [("nist", 9999)]
    none = citation_support("No citations here.", passages)
    assert not none["supported"] and none["n_citations"] == 0
