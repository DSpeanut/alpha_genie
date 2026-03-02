from openai import OpenAI
from anthropic import Anthropic
from app.core.config import get_settings

settings = get_settings()


class LLMService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None

        if settings.openai_api_key:
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
        if settings.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)

    async def summarize(self, text: str, provider: str = None) -> str:
        """Summarize text using LLM"""
        provider = provider or settings.default_llm

        prompt = f"""Please provide a concise summary of the following document.
Focus on key points, important metrics, and actionable insights.

Document:
{text[:8000]}  # Limit context

Summary:"""

        if provider == "openai" and self.openai_client:
            return await self._openai_complete(prompt)
        elif provider == "anthropic" and self.anthropic_client:
            return await self._anthropic_complete(prompt)
        else:
            return "No LLM provider configured. Please set API keys in .env"

    async def qa(self, document_content: str, question: str, provider: str = None) -> str:
        """Answer questions about a document"""
        provider = provider or settings.default_llm

        prompt = f"""Based on the following document, please answer the question.
If the answer is not in the document, say so.

Document:
{document_content[:8000]}

Question: {question}

Answer:"""

        if provider == "openai" and self.openai_client:
            return await self._openai_complete(prompt)
        elif provider == "anthropic" and self.anthropic_client:
            return await self._anthropic_complete(prompt)
        else:
            return "No LLM provider configured. Please set API keys in .env"

    async def chat(self, prompt: str, provider: str = None) -> str:
        """General chat completion"""
        provider = provider or settings.default_llm

        if provider == "openai" and self.openai_client:
            return await self._openai_complete(prompt)
        elif provider == "anthropic" and self.anthropic_client:
            return await self._anthropic_complete(prompt)
        else:
            return "No LLM provider configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in backend/.env"

    async def analyze_sentiment(self, text: str, provider: str = None) -> dict:
        """Analyze sentiment of text"""
        provider = provider or settings.default_llm

        prompt = f"""Analyze the sentiment of the following text.
Return a JSON object with:
- overall_sentiment: positive, negative, or neutral
- confidence: 0-1
- key_themes: list of main themes

Text:
{text[:4000]}

JSON Response:"""

        if provider == "openai" and self.openai_client:
            response = await self._openai_complete(prompt)
        elif provider == "anthropic" and self.anthropic_client:
            response = await self._anthropic_complete(prompt)
        else:
            return {"error": "No LLM provider configured"}

        # Parse JSON response (basic)
        try:
            import json
            return json.loads(response)
        except:
            return {"raw_response": response}

    async def _openai_complete(self, prompt: str) -> str:
        """Call OpenAI API"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )
        return response.choices[0].message.content

    async def _anthropic_complete(self, prompt: str) -> str:
        """Call Anthropic API"""
        response = self.anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


# Singleton instance
llm_service = LLMService()
