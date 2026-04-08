"""
AI Assistant Agent — main entry point for the AI Assistant panel.
Extend this with RAG, subagents, tool use, etc.
"""

import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from app.core.config import get_settings
from app.agents.tools import tools

from langchain_classic import hub
from langchain_openai import ChatOpenAI
from langchain_classic.agents import (
    AgentExecutor,
    create_openai_tools_agent,
)


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("🔧 Initializing Assistant...")
_settings = get_settings()
logger.info(f"Settings loaded: model={_settings.openai_model}, has_key={bool(_settings.openai_api_key)}")

model = ChatOpenAI(
    model=_settings.openai_model,
    temperature=0.1,
    max_tokens=1000,
    timeout=30,
)


from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

async def run(question: str) -> str:
    logger.info(f"Assistant running: {question}")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are Alpha Genie, an AI investment assistant for asset management."),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),  # FIXED
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_openai_tools_agent(model, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    result = agent_executor.invoke({"input": question})  # matches prompt

    logger.info(f"Agent execution result: {result}")

    if not result:
        logger.warning("No text returned from model")
        return "I'm unable to provide a response at this time."

    return result["output"]  # FIXED