"""
Batch earnings transcript ingestion script.

Fetches transcripts for a ticker list, runs sentiment analysis,
saves results to the earnings_transcripts DB table, and chunks
transcripts into ChromaDB for RAG.

Usage:
    # From backend/ directory with venv activated:
    python scripts/ingest_transcripts.py
    python scripts/ingest_transcripts.py --tickers AAPL MSFT NVDA
    python scripts/ingest_transcripts.py --tickers AAPL --quarters 2025Q1 2024Q4
    python scripts/ingest_transcripts.py --tickers AAPL --force
"""

import asyncio
import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure backend/ is on the path when running from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.core.config import get_settings
from app.core.database import SessionLocal, init_db
from app.models.earnings import EarningsTranscript
from app.services.earning_call_transcript import EarningCallTranscript, get_recent_quarters
from app.rag.ingest import ingest_transcript

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Default ticker list — edit or override with --tickers
DEFAULT_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"]


async def process_ticker(
    symbol: str,
    quarters: list[str],
    api_key: str,
    force: bool,
) -> None:
    service = EarningCallTranscript()
    db = SessionLocal()

    try:
        for quarter in quarters:
            logger.info("[%s] Processing %s ...", symbol, quarter)

            # Skip if already ingested (unless --force)
            existing = (
                db.query(EarningsTranscript)
                .filter_by(symbol=symbol, quarter=quarter)
                .first()
            )
            if existing and not force:
                logger.info("[%s] %s already in DB, skipping (use --force to re-ingest)", symbol, quarter)
                continue

            # 1. Fetch transcript
            try:
                transcript = await service.fetch_transcript(symbol, quarter, api_key)
            except Exception as e:
                logger.warning("[%s] %s — fetch failed: %s", symbol, quarter, e)
                continue

            word_count = len(transcript.split())
            logger.info("[%s] %s — fetched %d words", symbol, quarter, word_count)

            # 2. Run sentiment pipeline
            try:
                await service.transcript_text_processing(transcript)
                await service.classify_financial_sentence()
                sentiment = await service.analyze_sentiment_score()
            except Exception as e:
                logger.warning("[%s] %s — sentiment analysis failed: %s", symbol, quarter, e)
                sentiment = None

            # 3. Save to DB (upsert)
            top_sentences_json = json.dumps({
                "top_positive": sentiment.get("top_positive_sentences", []) if sentiment else [],
                "top_neutral": sentiment.get("top_neutral_sentences", []) if sentiment else [],
                "top_negative": sentiment.get("top_negative_sentences", []) if sentiment else [],
            })

            if existing:
                existing.raw_transcript = transcript
                existing.word_count = word_count
                existing.fetched_at = datetime.now(timezone.utc)
                if sentiment:
                    existing.positive = sentiment["positive"]
                    existing.neutral = sentiment["neutral"]
                    existing.negative = sentiment["negative"]
                    existing.sentences_analyzed = sentiment["sentences_analyzed"]
                    existing.top_sentences_json = top_sentences_json
                    existing.analyzed_at = datetime.now(timezone.utc)
                row = existing
            else:
                row = EarningsTranscript(
                    symbol=symbol,
                    quarter=quarter,
                    raw_transcript=transcript,
                    word_count=word_count,
                    positive=sentiment["positive"] if sentiment else None,
                    neutral=sentiment["neutral"] if sentiment else None,
                    negative=sentiment["negative"] if sentiment else None,
                    sentences_analyzed=sentiment["sentences_analyzed"] if sentiment else None,
                    top_sentences_json=top_sentences_json,
                    analyzed_at=datetime.now(timezone.utc) if sentiment else None,
                )
                db.add(row)

            db.commit()
            logger.info("[%s] %s — saved to DB", symbol, quarter)

            # 4. Chunk into ChromaDB
            try:
                n_chunks = ingest_transcript(symbol, quarter, transcript, force=force)
                logger.info("[%s] %s — %d chunks ingested into ChromaDB", symbol, quarter, n_chunks)
            except Exception as e:
                logger.warning("[%s] %s — vector ingest failed: %s", symbol, quarter, e)

    finally:
        db.close()


async def main(tickers: list[str], quarters: list[str], force: bool) -> None:
    settings = get_settings()
    api_key = settings.earnings_api_key

    if not api_key:
        logger.error("EARNINGS_API_KEY not set in .env")
        sys.exit(1)

    init_db()

    tasks = [process_ticker(symbol.upper(), quarters, api_key, force) for symbol in tickers]
    await asyncio.gather(*tasks)
    logger.info("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch ingest earnings transcripts")
    parser.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS, help="Ticker symbols")
    parser.add_argument(
        "--quarters",
        nargs="+",
        default=get_recent_quarters(4),
        help="Quarters to fetch e.g. 2025Q1 2024Q4",
    )
    parser.add_argument("--force", action="store_true", help="Re-ingest even if already in DB")
    args = parser.parse_args()

    asyncio.run(main(tickers=args.tickers, quarters=args.quarters, force=args.force))
