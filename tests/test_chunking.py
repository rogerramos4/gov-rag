"""Unit tests that need no Ollama or Chroma: pure chunking and abstention logic."""
import pytest

from ask import ABSTAIN, classify_abstention
from ingest import chunk_page


def test_windows_overlap_and_cover_tail():
    text = "".join(chr(ord("a") + i % 26) for i in range(2000))  # distinguishable positions
    chunks = chunk_page(text, size=800, overlap=150)
    assert chunks[0] == text[0:800]
    assert chunks[1] == text[650:1450]
    assert chunks[2] == text[1300:2000]
    assert len(chunks) == 3
    assert chunks[0][-150:] == chunks[1][:150]  # real overlap


def test_empty_page_gives_no_chunks():
    assert chunk_page("   \n ", 800, 150) == []


def test_short_page_is_one_chunk():
    assert chunk_page("short text", 800, 150) == ["short text"]


@pytest.mark.parametrize("size,overlap", [(0, 0), (800, 800), (800, 900), (800, -1)])
def test_invalid_args_rejected(size, overlap):
    with pytest.raises(ValueError):
        chunk_page("x" * 100, size, overlap)


def test_abstention_detection():
    assert classify_abstention(ABSTAIN)
    assert classify_abstention("The documents do not cover this. NOT IN DOCUMENTS.")
    assert not classify_abstention('The RMF says "NOT IN DOCUMENTS" is used when... (nist, 12)')
    assert not classify_abstention("GOVERN, MAP, MEASURE, MANAGE (nist, 25)")
