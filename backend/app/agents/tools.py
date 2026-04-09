"""
Agent tools registry.
Define tools here and they will be available to the assistant agent.

Usage:
    from app.agents.tools import tools
    model_with_tools = model.bind_tools(tools)
"""

import json
import logging

import yfinance as yf
from langchain_core.tools import tool
from tavily import TavilyClient

from app.rag import retriever
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.earnings import EarningsTranscript

logger = logging.getLogger(__name__)
settings = get_settings()


@tool
def get_stock_price(symbol: str) -> str:
    """Get the current stock price for a given ticker symbol (e.g. AAPL, TSLA)."""
    try:
        logger.info(f"Fetching stock price for {symbol}")
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if data.empty:
            msg = f"No data found for {symbol.upper()}"
            logger.warning(msg)
            return msg
        current_price = data["Close"].iloc[-1]
        result = f"Current price for {symbol.upper()}: ${current_price:.2f}"
        logger.info(f"Stock price result: {result}")
        return result
    except Exception as e:
        error_msg = f"Error fetching price for {symbol.upper()}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


@tool
def get_earnings_sentiment(symbol: str, quarter: str = "latest") -> str:
    """
    Get pre-computed earnings call sentiment scores for a stock from the database.
    Quarter format: '2025Q1'. Use 'latest' to get the most recent available quarter.
    Returns positive, neutral, and negative sentiment scores.
    """
    db = SessionLocal()
    try:
        query = db.query(EarningsTranscript).filter(
            EarningsTranscript.symbol == symbol.upper(),
            EarningsTranscript.positive.isnot(None),
        )
        if quarter.lower() == "latest":
            row = query.order_by(EarningsTranscript.analyzed_at.desc()).first()
        else:
            row = query.filter(EarningsTranscript.quarter == quarter).first()

        if not row:
            return (
                f"No pre-computed sentiment found for {symbol.upper()} {quarter}. "
                "Run scripts/ingest_transcripts.py to ingest data first."
            )

        return (
            f"Earnings sentiment for {row.symbol} {row.quarter}: "
            f"positive={row.positive:.2%}, neutral={row.neutral:.2%}, negative={row.negative:.2%} "
            f"(based on {row.sentences_analyzed} financial sentences)"
        )
    finally:
        db.close()


@tool
def search_earnings_transcripts(query: str, symbol: str = "", quarter: str = "") -> str:
    """
    Semantic search over ingested earnings call transcripts.
    Use this to answer questions like 'What did management say about margins?'
    or 'How did AAPL describe their AI strategy?'.
    Optionally filter by symbol (e.g. 'AAPL') and/or quarter (e.g. '2025Q1').
    """
    try:
        results = retriever.retrieve(query=query, symbol=symbol, quarter=quarter)

        if not results:
            return "No relevant transcript passages found. Make sure transcripts have been ingested."

        formatted = [
            f"[{i}] {r['symbol']} {r['quarter']} (chunk {r['chunk_index']}, dist={r['distance']}):\n{r['text']}"
            for i, r in enumerate(results, 1)
        ]
        return "\n\n".join(formatted)

    except Exception as e:
        logger.error("RAG search failed: %s", e, exc_info=True)
        return f"Search failed: {str(e)}"


@tool
def get_assetmanagement_web_search(query: str) -> str:
    """Get asset management view for a stock."""
    client = TavilyClient(settings.tavily_api_key)
    response = client.search(query=query, search_depth="advanced")
    return response


# ── Tool registry ─────────────────────────────────────────────────────────────
# Add new tools to this list to make them available to the agent.
tools = [
    get_stock_price,
    get_earnings_sentiment,
    search_earnings_transcripts,
    get_assetmanagement_web_search,
]
