import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from app.core.config import get_settings
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
