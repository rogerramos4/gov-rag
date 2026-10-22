"""Hybrid retrieval pieces that need no Chroma or Ollama."""
from ask import rrf, tokenize


def test_rrf_prefers_items_in_both_lists():
    fused = rrf([["a", "b", "c"], ["c", "d", "a"]])
    assert fused[:2] == ["a", "c"]  # both appear in both lists
    assert "b" in fused and "d" in fused


def test_rrf_ties_are_deterministic():
    assert rrf([["x"], ["y"]]) == ["x", "y"]  # equal scores -> alphabetical


def test_tokenize_keeps_subcategory_ids():
    assert "govern" in tokenize("GOVERN 1.6: Mechanisms are in place")
    assert "1.6" in tokenize("GOVERN 1.6: Mechanisms are in place")
