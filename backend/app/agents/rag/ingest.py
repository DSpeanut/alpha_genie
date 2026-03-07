"""
Data ingestion job — run manually when you have new data to load.

Usage:
    python -m app.agents.rag.ingest

Sources to ingest (add more as needed):
- Uploaded documents (PDFs, DOCX, TXT)
- Earnings call transcripts
"""

from app.agents.rag import vectorstore


def ingest_documents() -> None:
    """Load and ingest uploaded documents into the vector store."""
    # TODO:
    # 1. Load files from data/uploads/
    # 2. Extract text (reuse document_service.extract_text)
    # 3. Chunk text
    # 4. Call vectorstore.add(chunks, metadatas)
    raise NotImplementedError


def ingest_transcripts() -> None:
    """Load and ingest earnings transcripts into the vector store."""
    # TODO:
    # 1. Fetch transcripts via earning_call_service
    # 2. Chunk transcript text
    # 3. Call vectorstore.add(chunks, metadatas)
    raise NotImplementedError


if __name__ == "__main__":
    print("Starting ingestion...")
    ingest_documents()
    ingest_transcripts()
    print("Ingestion complete.")
