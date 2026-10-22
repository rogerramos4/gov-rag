"""ingest.py: turn data/nist_ai_rmf.pdf into embedded chunks in a local Chroma collection.

Why a separate script: ingestion is slow and deterministic, so we run it once and
reuse the vector store for every question and every eval run.
"""
import argparse
import hashlib
import sys
import time
from pathlib import Path

import chromadb
import requests
from pypdf import PdfReader

OLLAMA = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text:v1.5"


def load_pages(pdf_path: Path) -> list[tuple[int, str]]:
    """Return (physical_page_number, text) pairs, numbered from 1.

    Why physical pages: the NIST PDF's printed page numbers start at physical page 6,
    so citing physical pages is the only thing a reader can verify by scrolling.
    """
    reader = PdfReader(str(pdf_path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        pages.append((i, page.extract_text() or ""))
    return pages


def chunk_page(text: str, size: int, overlap: int) -> list[str]:
    """Split one page's text into fixed-size overlapping windows.

    Why never cross pages: a chunk that spans two pages has no single page to cite.
    Why validate: overlap >= size would loop forever; negative overlap would skip text.
    """
    if size <= 0 or not (0 <= overlap < size):
        raise ValueError(f"need size > 0 and 0 <= overlap < size, got size={size} overlap={overlap}")
    text = " ".join(text.split())  # collapse whitespace so chunk sizes are meaningful
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start : start + size])
        if start + size >= len(text):
            break
        start += size - overlap
    return chunks


def embed(texts: list[str], prefix: str = "search_document: ") -> list[list[float]]:
    """Embed a batch of texts with Ollama.

    Why the prefix: nomic-embed is trained with task prefixes; chunks get
    'search_document:' and questions get 'search_query:' or retrieval quality drops.
    """
    resp = requests.post(
        f"{OLLAMA}/api/embed",
        json={"model": EMBED_MODEL, "input": [prefix + t for t in texts], "truncate": False},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"]


def main() -> None:
    """Ingest one PDF into one Chroma collection named for its chunk size."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default="data/nist_ai_rmf.pdf")
    ap.add_argument("--doc", default="nist", help="short doc id used in chunk ids and citations")
    ap.add_argument("--size", type=int, default=800)
    ap.add_argument("--overlap", type=int, default=150)
    ap.add_argument("--batch", type=int, default=32)
    args = ap.parse_args()

    t0 = time.time()
    pdf_path = Path(args.pdf)
    sha = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    pages = load_pages(pdf_path)

    ids, docs, metas = [], [], []
    for page_no, text in pages:
        for c_idx, chunk in enumerate(chunk_page(text, args.size, args.overlap), start=1):
            ids.append(f"{args.doc}-p{page_no:03d}-c{c_idx:02d}")
            docs.append(chunk)
            metas.append({"doc": args.doc, "page": page_no, "sha256": sha[:12]})

    if args.batch <= 0:
        raise ValueError("--batch must be > 0")
    client = chromadb.PersistentClient(path="./chroma_db")
    name = f"{args.doc}_{args.size}"
    # Why build into a temp collection first: if Ollama dies mid-run, the old index
    # must survive untouched. We swap names only after every chunk is embedded.
    tmp_name = f"{name}__building"
    existing = {c.name for c in client.list_collections()}
    if tmp_name in existing:
        client.delete_collection(tmp_name)
    fingerprint = f"{args.doc}|sha={sha[:12]}|size={args.size}|overlap={args.overlap}|embed={EMBED_MODEL}"
    col = client.create_collection(tmp_name, embedding_function=None,
                                   metadata={"hnsw:space": "cosine", "fingerprint": fingerprint})

    for i in range(0, len(docs), args.batch):
        vecs = embed(docs[i : i + args.batch])
        col.add(ids=ids[i : i + args.batch], embeddings=vecs, documents=docs[i : i + args.batch], metadatas=metas[i : i + args.batch])
        print(f"  embedded {min(i + args.batch, len(docs))}/{len(docs)}", end="\r", file=sys.stderr)

    if col.count() != len(docs):
        raise RuntimeError(f"expected {len(docs)} chunks, stored {col.count()}; old index left intact")
    if name in existing:
        client.delete_collection(name)
    col.modify(name=name)
    print(f"\n{pdf_path.name} sha256={sha[:12]}  pages={len(pages)}  chunks={len(docs)}  "
          f"collection={name}  fingerprint={fingerprint}  {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
