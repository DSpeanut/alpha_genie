"""
Retriever — used by the agent at query time.
Fetches relevant chunks from the vector store and formats them for the LLM prompt.
"""

from app.agents.rag import vectorstore


def retrieve(query: str, k: int = 5) -> str:
    """Return retrieved context as a formatted string ready to inject into a prompt."""
    # TODO:
    # 1. Call vectorstore.search(query, k)
    # 2. Format results into a context string
    raise NotImplementedError
