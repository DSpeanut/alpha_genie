"""
Data ingestion — run via scripts/ingest_transcripts.py.
"""

from app.rag import vectorstore

CHUNK_SIZE = 1000  # characters


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """Split text into fixed-size character chunks."""
    return [text[i: i + chunk_size] for i in range(0, len(text), chunk_size)]


def ingest_transcript(symbol: str, quarter: str, transcript: str, force: bool = False) -> int:
    """
    Chunk a single transcript and upsert into ChromaDB.
    Returns the number of chunks ingested.
    """
    if force:
        vectorstore.delete_by_symbol_quarter(symbol, quarter)

    chunks = chunk_text(transcript)
    ids = [f"{symbol}_{quarter}_{i}" for i in range(len(chunks))]
    metadatas = [
        {"symbol": symbol, "quarter": quarter, "chunk_index": i, "source": "earnings_transcript"}
        for i in range(len(chunks))
    ]
    vectorstore.add(texts=chunks, metadatas=metadatas, ids=ids)
    return len(chunks)
