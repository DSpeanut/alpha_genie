from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents import assistant
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])

logger.info("Agent router initialized")


class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    response: str


@router.post("/assistant", response_model=AgentResponse)
async def assistant_endpoint(request: AgentRequest):
    """AI Assistant with tools - can fetch stock prices, search, etc."""
    logger.info(f"🚀 Endpoint hit! Query: {request.message}")
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        logger.info(f"Agent received query: {request.message}")
        response = await assistant.run(request.message)
        logger.info(f"Agent response: {response}")
        return AgentResponse(response=response)
    except Exception as e:
        logger.error(f"❌ Agent error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
