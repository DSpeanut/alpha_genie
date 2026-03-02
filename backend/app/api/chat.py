from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm import llm_service
from app.core.config import get_settings

router = APIRouter(prefix="/chat", tags=["chat"])

settings = get_settings()


class ChatRequest(BaseModel):
    message: str
    context: str | None = None


class ChatResponse(BaseModel):
    response: str


SYSTEM_PROMPT = """You are Alpha Genie, an AI investment assistant for asset management professionals.
You help with:
- Market analysis and insights
- Portfolio strategy discussions
- Financial concepts explanation
- Investment research questions
- Risk assessment discussions

Be concise, professional, and data-driven in your responses.
If you don't have specific real-time data, acknowledge that and provide general guidance.
Always remind users that this is not financial advice and they should consult professionals for investment decisions."""


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the AI investment assistant"""

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # Build the prompt
        full_prompt = f"""{SYSTEM_PROMPT}

User Question: {request.message}

Assistant Response:"""

        # Try to get response from LLM
        response = await llm_service.chat(full_prompt)

        return ChatResponse(response=response)

    except Exception as e:
        # Fallback response if LLM is not configured
        return ChatResponse(
            response=f"I apologize, but I'm currently unable to process your request. Please ensure the LLM API keys are configured in the backend. Error: {str(e)}"
        )


@router.post("/analyze")
async def analyze_with_context(request: ChatRequest):
    """Chat with additional context (e.g., document content)"""

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        context_section = ""
        if request.context:
            context_section = f"\n\nContext/Document:\n{request.context[:4000]}\n"

        full_prompt = f"""{SYSTEM_PROMPT}
{context_section}
User Question: {request.message}

Assistant Response:"""

        response = await llm_service.chat(full_prompt)

        return ChatResponse(response=response)

    except Exception as e:
        return ChatResponse(
            response=f"Unable to process request. Error: {str(e)}"
        )
