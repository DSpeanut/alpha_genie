"""
Retrieval layer — sits between vectorstore and the agent tools.
Control chunking, filtering, distance thresholds, and result formatting here.
"""

from app.rag import vectorstore

# Cosine distance threshold — chunks above this are too dissimilar to be useful
DISTANCE_THRESHOLD = 0.7
DEFAULT_K = 5

def retrieve(
    query: str,
    k: int = DEFAULT_K,
    symbol: str = "",
    quarter: str = "",
    distance_threshold: float = DISTANCE_THRESHOLD,
) -> list[dict]:
    """
    Retrieve the top-k relevant transcript chunks for a query.

    Filters:
    - symbol: restrict to a specific ticker
    - quarter: restrict to a specific quarter
    - distance_threshold: drop chunks with cosine distance above this value

    Returns list of dicts: {text, symbol, quarter, chunk_index, distance}
    """
    where = _build_where(symbol, quarter)
    results = vectorstore.search(query=query, k=k, where=where)

    filtered = [r for r in results if r["distance"] <= distance_threshold]

    return [
        {
            "text": r["text"],
            "symbol": r["metadata"].get("symbol"),
            "quarter": r["metadata"].get("quarter"),
            "chunk_index": r["metadata"].get("chunk_index"),
            "distance": round(r["distance"], 4),
        }
        for r in filtered
    ]


def _build_where(symbol: str, quarter: str) -> dict | None:
    if symbol and quarter:
        return {"$and": [{"symbol": symbol.upper()}, {"quarter": quarter}]}
    if symbol:
        return {"symbol": symbol.upper()}
    if quarter:
        return {"quarter": quarter}
    return None
