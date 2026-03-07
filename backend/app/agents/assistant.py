"""
AI Assistant Agent — main entry point for the AI Assistant panel.
Extend this with RAG, subagents, tool use, etc.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.core.config import get_settings
from app.agents.tools import tools

_settings = get_settings()

model = ChatOpenAI(
    model=_settings.openai_model,
    temperature=0.1,
    max_tokens=1000,
    timeout=30,
).bind_tools(tools)


async def run(question: str) -> str:
    result = await model.ainvoke([HumanMessage(content=question)])
    return result.content
