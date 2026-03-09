"""
Agent tools registry.
Define tools here and they will be available to the assistant agent.

Usage:
    from app.agents.tools import tools
    model_with_tools = model.bind_tools(tools)
"""

from langchain_core.tools import tool
from tavily import TavilyClient

settings = get_settings()

# ── Example placeholder tools ────────────────────────────────────────────────
# Replace / extend these with real implementations.

@tool
def get_stock_price(symbol: str) -> str:
    """Get the current stock price for a given ticker symbol (e.g. AAPL, TSLA)."""
    # TODO: wire up to market_data_service.get_quote()
    return f"[placeholder] Price for {symbol.upper()} not yet implemented."


@tool
def get_earnings_sentiment(symbol: str, quarter: str = "latest") -> str:
    """Get earnings call sentiment for a stock. Quarter format: 2025Q1 or 'latest'."""
    # TODO: wire up to earning_call_service.analyze()
    return f"[placeholder] Sentiment for {symbol.upper()} {quarter} not yet implemented."

@tool
def get_assetmanagement_web_search(query: str) -> str:
    """Get asset management view for a stock."""
    client = TavilyClient(settings.tavily_api_key)
    response = client.search(
        query=query,
        search_depth="advanced"
    )
    return response

# ── Tool registry ─────────────────────────────────────────────────────────────
# Add new tools to this list to make them available to the agent.
tools = [
    get_stock_price,
    get_earnings_sentiment,
    get_assetmanagement_web_search
]
