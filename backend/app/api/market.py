from fastapi import APIRouter, Query
from typing import List
from app.services.market_data import market_data_service

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    """Get current quote for a symbol"""
    return await market_data_service.get_quote(symbol)


@router.get("/quotes")
async def get_multiple_quotes(symbols: str = Query(..., description="Comma-separated symbols")):
    """Get quotes for multiple symbols"""
    symbol_list = [s.strip() for s in symbols.split(",")]
    return await market_data_service.get_multiple_quotes(symbol_list)


@router.get("/history/{symbol}")
async def get_history(
    symbol: str,
    period: str = Query("1mo", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("1d", description="Interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
):
    """Get historical price data"""
    return await market_data_service.get_history(symbol, period, interval)


@router.get("/search")
async def search_symbol(q: str = Query(..., description="Search query")):
    """Search for symbols"""
    return await market_data_service.search_symbol(q)
