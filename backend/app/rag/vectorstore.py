"""
Vector store interface backed by ChromaDB (local, file-based at data/chroma/).
To migrate to Pinecone: reimplement add() and search() below, keep signatures identical.
"""

import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

from app.core.config import get_settings

CHROMA_DIR = Path(__file__).resolve().parents[3] / "data" / "chroma"
COLLECTION_NAME = "earnings_transcripts"

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        settings = get_settings()
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key,
            model_name="text-embedding-3-small",
        )
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add(texts: list[str], metadatas: list[dict], ids: list[str]) -> None:
    """Embed and upsert chunks into ChromaDB."""
    collection = _get_collection()
    collection.upsert(documents=texts, metadatas=metadatas, ids=ids)


def search(query: str, k: int = 5, where: dict | None = None) -> list[dict]:
    """Embed query and return top-k similar chunks with metadata and distances."""
    collection = _get_collection()
    kwargs = {"query_texts": [query], "n_results": k}
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)
    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append({"text": doc, "metadata": meta, "distance": dist})
    return output


def delete_by_symbol_quarter(symbol: str, quarter: str) -> None:
    """Remove all chunks for a given symbol+quarter (used on re-ingest)."""
    collection = _get_collection()
    collection.delete(where={"$and": [{"symbol": symbol}, {"quarter": quarter}]})
