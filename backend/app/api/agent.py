from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents import assistant

router = APIRouter(prefix="/agent", tags=["agent"])


class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    response: str


@router.post("/assistant", response_model=AgentResponse)
async def assistant_endpoint(request: AgentRequest):
    """AI Assistant panel endpoint — routes user input through the assistant agent."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    response = await assistant.run(request.message)
    return AgentResponse(response=response)
