from sqlalchemy import Column, Integer, String, DateTime, Text, Float, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class EarningsTranscript(Base):
    __tablename__ = "earnings_transcripts"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    quarter = Column(String, nullable=False)  # e.g. "2025Q1"

    # Raw transcript
    raw_transcript = Column(Text, nullable=False)
    word_count = Column(Integer)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())

    # Sentiment scores (pre-computed)
    positive = Column(Float)
    neutral = Column(Float)
    negative = Column(Float)
    sentences_analyzed = Column(Integer)
    top_sentences_json = Column(Text)  # JSON string of top positive/neutral/negative sentences
    analyzed_at = Column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint("symbol", "quarter", name="uq_symbol_quarter"),)
