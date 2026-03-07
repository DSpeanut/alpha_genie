"""
Centralized ML model registry.
All HuggingFace / local models are lazy-loaded here so they are:
  - shared across the app (loaded once)
  - only initialized when first used
Add new models here as the agent suite grows.
"""

from transformers import pipeline, BertTokenizer, BertForSequenceClassification


class _MLModels:
    def __init__(self):
        self._financial_sentence_classifier = None
        self._finbert_sentiment_model = None
        self._finbert_tokenizer = None

    @property
    def financial_sentence_classifier(self):
        if self._financial_sentence_classifier is None:
            print("[models] Loading financial sentence classifier (bart-large-mnli)...")
            self._financial_sentence_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
        return self._financial_sentence_classifier

    @property
    def finbert_sentiment_model(self):
        if self._finbert_sentiment_model is None:
            print("[models] Loading FinancialBERT sentiment model...")
            self._finbert_sentiment_model = BertForSequenceClassification.from_pretrained(
                "ahmedrachid/FinancialBERT-Sentiment-Analysis",
                num_labels=3
            )
        return self._finbert_sentiment_model

    @property
    def finbert_tokenizer(self):
        if self._finbert_tokenizer is None:
            print("[models] Loading FinancialBERT tokenizer...")
            self._finbert_tokenizer = BertTokenizer.from_pretrained(
                "ahmedrachid/FinancialBERT-Sentiment-Analysis"
            )
        return self._finbert_tokenizer


# Singleton — import and use `ml_models` everywhere
ml_models = _MLModels()
