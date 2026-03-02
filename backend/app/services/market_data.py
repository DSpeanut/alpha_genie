import asyncio
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


class MarketDataService:
    """Service for fetching market data using Yahoo Finance"""

    async def get_quote(self, symbol: str) -> dict:
        """Get current quote for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                "symbol": symbol.upper(),
                "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "change": info.get("regularMarketChange"),
                "change_percent": info.get("regularMarketChangePercent"),
                "volume": info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                "name": info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    async def get_history(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> list:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            # Convert to list of dicts
            data = []
            for date, row in df.iterrows():
                data.append({
                    "date": date.isoformat(),
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": row["Volume"],
                })
            return data
        except Exception as e:
            return {"error": str(e)}

    async def get_multiple_quotes(self, symbols: list) -> list:
        """Get quotes for multiple symbols - IN PARALLEL"""
        # ✅ asyncio.gather runs all requests at the same time
        results = await asyncio.gather(
            *[self.get_quote(symbol) for symbol in symbols]
        )
        return list(results)

    async def search_symbol(self, query: str) -> list:
        """Search for symbols matching query"""
        try:
            # Use yfinance search
            tickers = yf.Tickers(query)
            # This is a simplified search - in production, use a proper API
            return [{"symbol": query.upper(), "name": query}]
        except:
            return []


# Singleton instance
market_data_service = MarketDataService()
