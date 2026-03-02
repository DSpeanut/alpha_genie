import asyncio
import httpx
import pandas as pd
import numpy as np
import torch
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any, List
import nltk
from nltk.tokenize import sent_tokenize
from transformers import pipeline, BertTokenizer, BertForSequenceClassification

# Download nltk data (run once)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')


def get_recent_quarters(num_quarters: int = 4) -> List[str]:
    """Get list of recent quarters with available earnings (module-level function)"""
    today = datetime.now()
    year = today.year
    month = today.month

    # Determine current quarter
    if month <= 3:
        current_q = 1
    elif month <= 6:
        current_q = 2
    elif month <= 9:
        current_q = 3
    else:
        current_q = 4

    quarters = []
    q = current_q
    y = year

    for _ in range(num_quarters):
        # Alpha Vantage uses format: 2025Q4 (not Q4_2025)
        quarters.append(f"{y}Q{q}")
        q -= 1
        if q == 0:
            q = 4
            y -= 1

    return quarters


class EarningCallTranscript:
    """Service for fetching earning call transcript and perform sentiment analysis"""

    def __init__(self):
        self.financial_sentence_classifier = None
        self.finbert_sentiment_model = None
        self.finbert_tokenizer = None
        self.earning_class_df = None
        self.earning_financial_sentence = None
        self._models_loaded = False

    def _load_models(self):
        """Lazy load models only when needed"""
        if not self._models_loaded:
            self.financial_sentence_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            self.finbert_sentiment_model = BertForSequenceClassification.from_pretrained(
                "ahmedrachid/FinancialBERT-Sentiment-Analysis",
                num_labels=3
            )
            self.finbert_tokenizer = BertTokenizer.from_pretrained(
                "ahmedrachid/FinancialBERT-Sentiment-Analysis"
            )
            self._models_loaded = True

    async def fetch_transcript(self, symbol: str, quarter: str, api_key: str) -> str:
        """Get transcript for a symbol and specific quarter"""
        earning_call_url = (
            f'https://www.alphavantage.co/query?function=EARNINGS_CALL_TRANSCRIPT'
            f'&symbol={symbol}&quarter={quarter}&apikey={api_key}'
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(earning_call_url, timeout=30.0)
            earning_call_data = response.json()

        # Check for API errors or missing data
        if 'transcript' not in earning_call_data:
            # Check if it's a rate limit or error message
            if 'Information' in earning_call_data:
                raise ValueError(f"API limit: {earning_call_data['Information']}")
            if 'Error Message' in earning_call_data:
                raise ValueError(f"API error: {earning_call_data['Error Message']}")
            raise ValueError(f"No transcript found for {symbol} {quarter}")

        # Check for empty transcript list
        if not earning_call_data['transcript'] or len(earning_call_data['transcript']) == 0:
            raise ValueError(f"Empty transcript for {symbol} {quarter}")

        full_transcript = ''
        for item in earning_call_data['transcript']:
            full_transcript += item['content'] + ' '

        if not full_transcript.strip():
            raise ValueError(f"Transcript content is empty for {symbol} {quarter}")

        return full_transcript.strip()

    async def fetch_latest_transcript(self, symbol: str, api_key: str) -> Tuple[str, str]:
        """
        Try to fetch the latest available transcript.
        Starts from current quarter and falls back to previous quarters.
        Returns (transcript, quarter) tuple.
        """
        quarters = get_recent_quarters(6)  # Try up to 6 quarters back

        for quarter in quarters:
            try:
                transcript = await self.fetch_transcript(symbol, quarter, api_key)
                return transcript, quarter
            except ValueError:
                # No transcript for this quarter, try next
                continue
            except Exception as e:
                # API error, try next quarter
                continue

        raise Exception(f"No transcript found for {symbol} in recent quarters: {quarters}")

    async def transcript_text_processing(self, transcript: str) -> pd.DataFrame:
        """Process transcript text into sentences"""
        try:
            transcript_lower = transcript.lower()
            print(f"[DEBUG] Transcript length: {len(transcript_lower)} chars")
            earning_report_sentences = sent_tokenize(transcript_lower)
            print(f"[DEBUG] Tokenized into {len(earning_report_sentences)} sentences")
            self.earning_class_df = pd.DataFrame({
                'earning_sentence': earning_report_sentences
            })
            return self.earning_class_df

        except Exception as e:
            print(f"[DEBUG] transcript_text_processing error: {str(e)}")
            raise Exception(f"Failed to process transcript: {str(e)}")

    async def classify_financial_sentence(self) -> pd.DataFrame:
        """Classify financial specific sentences"""
        try:
            self._load_models()

            financial_keywords = {
                'revenue', 'profit', 'earnings', 'ebitda', 'margin', 'quarter', 'quarterly',
                'fiscal', 'dividend', 'shareholder', 'equity', 'liability', 'asset',
                'cash flow', 'roi', 'market cap', 'yoy', 'qoq', 'eps', 'operating income',
                'net income', 'gross margin', 'guidance', 'forecast', 'balance sheet',
                'stock', 'shares', 'valuation', 'growth rate', 'sales', 'expenses',
                'invest', 'financial', 'acquisition', 'merger', 'debt', 'credit',
                'earning', 'value'
            }

            def detect_financial_sentences(sentence: str) -> Tuple[int, float]:
                for keyword in financial_keywords:
                    if keyword in sentence:
                        return 1, 1.0
                return 0, 0.0

            def detect_financial_sentences_lm(sentence: str) -> Tuple[int, float]:
                labels = ["financial", "general"]
                result = self.financial_sentence_classifier(sentence, labels)
                label = 1 if result['labels'][0] == "financial" else 0
                score = np.round(result['scores'][0], 2)
                return label, score

            # Apply keyword detection (using list comprehension for robustness)
            keyword_results = [detect_financial_sentences(s) for s in self.earning_class_df['earning_sentence']]
            self.earning_class_df['keyword_search_label'] = [r[0] for r in keyword_results]
            self.earning_class_df['keyword_search_score'] = [r[1] for r in keyword_results]
            keyword_matches = sum(r[0] for r in keyword_results)
            print(f"[DEBUG] Keyword detection: {keyword_matches} financial sentences found")

            # Apply LM classification (using list comprehension for robustness)
            print(f"[DEBUG] Starting LM classification on {len(self.earning_class_df)} sentences...")
            lm_results = [detect_financial_sentences_lm(s) for s in self.earning_class_df['earning_sentence']]
            self.earning_class_df['keyword_classified_label'] = [r[0] for r in lm_results]
            self.earning_class_df['keyword_classified_score'] = [r[1] for r in lm_results]
            lm_matches = sum(r[0] for r in lm_results)
            print(f"[DEBUG] LM classification: {lm_matches} financial sentences found")

            # Filter financial sentences with high confidence
            self.earning_financial_sentence = self.earning_class_df[
                (self.earning_class_df['keyword_classified_label'] == 1) &
                (self.earning_class_df['keyword_classified_score'] > 0.90)
            ].copy()
            print(f"[DEBUG] After 0.90 threshold filter: {len(self.earning_financial_sentence)} sentences")

            # If no sentences pass the filter, lower the threshold
            if len(self.earning_financial_sentence) == 0:
                self.earning_financial_sentence = self.earning_class_df[
                    self.earning_class_df['keyword_classified_label'] == 1
                ].copy()
                print(f"[DEBUG] After lowered threshold: {len(self.earning_financial_sentence)} sentences")

            # If still empty, use keyword-matched sentences
            if len(self.earning_financial_sentence) == 0:
                self.earning_financial_sentence = self.earning_class_df[
                    self.earning_class_df['keyword_search_label'] == 1
                ].copy()
                print(f"[DEBUG] Using keyword fallback: {len(self.earning_financial_sentence)} sentences")

            return self.earning_financial_sentence

        except Exception as e:
            raise Exception(f"Failed to classify sentences: {str(e)}")

    async def analyze_sentiment_score(self) -> Dict[str, Any]:
        """Analyze financial sentence sentiment"""
        try:
            # Check if we have sentences to analyze
            if self.earning_financial_sentence is None or len(self.earning_financial_sentence) == 0:
                return {
                    "positive": 0.0,
                    "neutral": 0.0,
                    "negative": 0.0,
                    "sentences_analyzed": 0,
                    "top_positive_sentences": [],
                    "top_neutral_sentences": [],
                    "top_negative_sentences": [],
                }

            self._load_models()

            def get_finbert_sentiment_scores(text: str) -> Tuple[float, float, float]:
                inputs = self.finbert_tokenizer(
                    text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                )
                with torch.no_grad():
                    outputs = self.finbert_sentiment_model(**inputs)
                    logits = outputs.logits
                    probabilities = torch.softmax(logits, dim=1)[0]

                return (
                    np.round(probabilities[2].item(), 4),  # positive
                    np.round(probabilities[1].item(), 4),  # neutral
                    np.round(probabilities[0].item(), 4),  # negative
                )

            # Apply sentiment analysis (using list comprehension for robustness)
            sentiment_results = [get_finbert_sentiment_scores(s) for s in self.earning_financial_sentence['earning_sentence']]
            self.earning_financial_sentence['finbert_positive_score'] = [r[0] for r in sentiment_results]
            self.earning_financial_sentence['finbert_neutral_score'] = [r[1] for r in sentiment_results]
            self.earning_financial_sentence['finbert_negative_score'] = [r[2] for r in sentiment_results]

            # Calculate average scores
            positive_score = float(self.earning_financial_sentence['finbert_positive_score'].mean())
            neutral_score = float(self.earning_financial_sentence['finbert_neutral_score'].mean())
            negative_score = float(self.earning_financial_sentence['finbert_negative_score'].mean())

            # Get top 3 sentences for each sentiment class
            df = self.earning_financial_sentence

            top_positive = df.nlargest(3, 'finbert_positive_score')[
                ['earning_sentence', 'finbert_positive_score']
            ].to_dict('records')

            top_neutral = df.nlargest(3, 'finbert_neutral_score')[
                ['earning_sentence', 'finbert_neutral_score']
            ].to_dict('records')

            top_negative = df.nlargest(3, 'finbert_negative_score')[
                ['earning_sentence', 'finbert_negative_score']
            ].to_dict('records')

            return {
                "positive": round(positive_score, 4),
                "neutral": round(neutral_score, 4),
                "negative": round(negative_score, 4),
                "sentences_analyzed": len(self.earning_financial_sentence),
                "top_positive_sentences": [
                    {"text": s['earning_sentence'], "score": s['finbert_positive_score']}
                    for s in top_positive
                ],
                "top_neutral_sentences": [
                    {"text": s['earning_sentence'], "score": s['finbert_neutral_score']}
                    for s in top_neutral
                ],
                "top_negative_sentences": [
                    {"text": s['earning_sentence'], "score": s['finbert_negative_score']}
                    for s in top_negative
                ],
            }

        except Exception as e:
            raise Exception(f"Failed to analyze sentiment: {str(e)}")

    async def analyze(self, symbol: str, quarter: str, api_key: str) -> Dict[str, Any]:
        """Full pipeline: fetch transcript and analyze sentiment"""
        # Check if user wants latest quarter
        if quarter.lower() == "latest":
            transcript, actual_quarter = await self.fetch_latest_transcript(symbol, api_key)
        else:
            transcript = await self.fetch_transcript(symbol, quarter, api_key)
            actual_quarter = quarter

        # Process text
        await self.transcript_text_processing(transcript)
        total_sentences = len(self.earning_class_df)

        # Classify financial sentences
        await self.classify_financial_sentence()
        financial_sentences = len(self.earning_financial_sentence) if self.earning_financial_sentence is not None else 0

        # Analyze sentiment
        sentiment = await self.analyze_sentiment_score()

        return {
            "symbol": symbol,
            "quarter": actual_quarter,
            "sentiment": sentiment,
            "summary": f"Analyzed {sentiment['sentences_analyzed']} financial sentences (from {total_sentences} total, {financial_sentences} classified as financial)"
        }

    async def analyze_text(self, transcript: str) -> Dict[str, Any]:
        """Analyze provided transcript text"""
        # Process text
        await self.transcript_text_processing(transcript)

        # Classify financial sentences
        await self.classify_financial_sentence()

        # Analyze sentiment
        sentiment = await self.analyze_sentiment_score()

        return {
            "sentiment": sentiment,
            "summary": f"Analyzed {sentiment['sentences_analyzed']} financial sentences"
        }


# Singleton instance
earning_call_service = EarningCallTranscript()
