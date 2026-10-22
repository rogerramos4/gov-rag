"""Unit tests that need no Ollama or Chroma: pure chunking logic."""
from ingest import chunk_page


def test_chunk_sizes_and_overlap():
    text = "a" * 2000
    chunks = chunk_page(text, size=800, overlap=150)
    assert all(len(c) <= 800 for c in chunks)
    assert chunks[1] == text[650:1450]  # start advances by size - overlap


def test_empty_page_gives_no_chunks():
    assert chunk_page("   \n ", 800, 150) == []


def test_short_page_is_one_chunk():
    assert chunk_page("short text", 800, 150) == ["short text"]
