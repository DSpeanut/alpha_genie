import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.config import get_settings
from app.core.database import get_db
from app.models.earnings import EarningsTranscript
from app.services.earning_call_transcript import earning_call_service, get_recent_quarters

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/earnings", tags=["earnings"])

settings = get_settings()


@router.get("/quarters")
async def get_available_quarters() -> List[str]:
    """Get list of recent quarters (for dropdown)"""
    return get_recent_quarters(8)


class TranscriptResponse(BaseModel):
    symbol: str
    quarter: str
    transcript: str | None = None
    sentiment: dict | None = None


class AnalysisResponse(BaseModel):
    symbol: str
    quarter: str
    sentiment: dict
    summary: str | None = None


@router.get("/transcript/{symbol}")
async def get_transcript(
    symbol: str,
    quarter: str = Query(..., description="Quarter in format: Q1_2024, Q2_2024, etc.")
) -> TranscriptResponse:
    """
    Fetch earning call transcript from external API

    - symbol: Stock ticker (e.g., AAPL)
    - quarter: Quarter format Q1_2024
    """
    # API key from environment
    api_key = settings.earnings_api_key

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="EARNINGS_API_KEY not configured in .env"
        )

    try:
        transcript = await earning_call_service.fetch_transcript(
            symbol=symbol.upper(),
            quarter=quarter,
            api_key=api_key
        )
        return TranscriptResponse(
            symbol=symbol.upper(),
            quarter=quarter,
            transcript=transcript
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{symbol}")
async def analyze_earning_call(
    symbol: str,
    quarter: str = Query(..., description="Quarter in format: Q1_2024, Q2_2024, etc.")
) -> AnalysisResponse:
    """
    Fetch transcript and run sentiment analysis

    - symbol: Stock ticker (e.g., AAPL)
    - quarter: Quarter format Q1_2024
    """
    api_key = settings.earnings_api_key

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="EARNINGS_API_KEY not configured in .env"
        )

    try:
        logger.info("Starting analysis for %s %s", symbol.upper(), quarter)
        result = await earning_call_service.analyze(
            symbol=symbol.upper(),
            quarter=quarter,
            api_key=api_key
        )
        logger.info("Analysis complete: %s", result.get("summary"))
        return AnalysisResponse(
            symbol=symbol.upper(),
            quarter=quarter,
            sentiment=result.get("sentiment", {}),
            summary=result.get("summary")
        )
    except Exception as e:
        logger.exception("Analysis failed for %s %s", symbol.upper(), quarter)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-text")
async def analyze_transcript_text(
    transcript: str,
    symbol: str = Query(None),
    quarter: str = Query(None)
) -> AnalysisResponse:
    """
    Analyze a transcript you provide directly (no external API call)
    """
    try:
        result = await earning_call_service.analyze_text(transcript)
        return AnalysisResponse(
            symbol=symbol or "UNKNOWN",
            quarter=quarter or "UNKNOWN",
            sentiment=result.get("sentiment", {}),
            summary=result.get("summary")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class StoredSentimentResponse(BaseModel):
    symbol: str
    quarter: str
    positive: Optional[float]
    neutral: Optional[float]
    negative: Optional[float]
    sentences_analyzed: Optional[int]
    top_sentences: Optional[dict]
    analyzed_at: Optional[str]
    word_count: Optional[int]


@router.get("/sentiment/{symbol}")
async def get_stored_sentiment(
    symbol: str,
    quarter: str = Query(..., description="Quarter e.g. 2025Q1"),
    db: Session = Depends(get_db),
) -> StoredSentimentResponse:
    """
    Return pre-computed sentiment from DB (populated by ingest_transcripts.py).
    Falls back to on-the-fly analysis if not found.
    """
    row = (
        db.query(EarningsTranscript)
        .filter_by(symbol=symbol.upper(), quarter=quarter)
        .first()
    )

    if row and row.positive is not None:
        return StoredSentimentResponse(
            symbol=row.symbol,
            quarter=row.quarter,
            positive=row.positive,
            neutral=row.neutral,
            negative=row.negative,
            sentences_analyzed=row.sentences_analyzed,
            top_sentences=json.loads(row.top_sentences_json) if row.top_sentences_json else None,
            analyzed_at=row.analyzed_at.isoformat() if row.analyzed_at else None,
            word_count=row.word_count,
        )

    # Fallback: run on-the-fly
    api_key = settings.earnings_api_key
    if not api_key:
        raise HTTPException(status_code=500, detail="EARNINGS_API_KEY not configured")

    try:
        result = await earning_call_service.analyze(
            symbol=symbol.upper(), quarter=quarter, api_key=api_key
        )
        sentiment = result.get("sentiment", {})
        return StoredSentimentResponse(
            symbol=symbol.upper(),
            quarter=quarter,
            positive=sentiment.get("positive"),
            neutral=sentiment.get("neutral"),
            negative=sentiment.get("negative"),
            sentences_analyzed=sentiment.get("sentences_analyzed"),
            top_sentences={
                "top_positive": sentiment.get("top_positive_sentences", []),
                "top_neutral": sentiment.get("top_neutral_sentences", []),
                "top_negative": sentiment.get("top_negative_sentences", []),
            },
            analyzed_at=None,
            word_count=None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stored")
async def list_stored_transcripts(
    db: Session = Depends(get_db),
) -> List[dict]:
    """List all tickers/quarters that have been ingested."""
    rows = db.query(
        EarningsTranscript.symbol,
        EarningsTranscript.quarter,
        EarningsTranscript.word_count,
        EarningsTranscript.positive,
        EarningsTranscript.negative,
        EarningsTranscript.analyzed_at,
    ).all()
    return [
        {
            "symbol": r.symbol,
            "quarter": r.quarter,
            "word_count": r.word_count,
            "positive": r.positive,
            "negative": r.negative,
            "analyzed_at": r.analyzed_at.isoformat() if r.analyzed_at else None,
        }
        for r in rows
    ]
