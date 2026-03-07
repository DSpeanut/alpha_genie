"""
Vector store interface.
Currently: ChromaDB (local, file-based)
To migrate to Pinecone: reimplement add() and search() below, keep signatures identical.
"""

# TODO: import chromadb and initialize client + collection


def add(texts: list[str], metadatas: list[dict]) -> None:
    """Embed and store texts into the vector store."""
    # TODO: embed texts and upsert into ChromaDB collection
    raise NotImplementedError


def search(query: str, k: int = 5) -> list[dict]:
    """Embed query and return top-k similar chunks with metadata."""
    # TODO: embed query, run similarity search, return results
    raise NotImplementedError
