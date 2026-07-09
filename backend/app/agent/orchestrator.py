"""Builds the orchestrator agent (OpenAI model + tools from the external MCP server
+ conversation window). All tools are remote — set MCP_TOOLS_URL. An AGENT_FACTORY
seam lets tests inject a deterministic fake agent."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.agent import mcp_tools
from app.agent.prompts import orchestrator_system_prompt
from app.config import get_settings

# Test seam: set to a callable (conversation_id) -> agent to bypass live providers.
AGENT_FACTORY: Callable[[str], Any] | None = None


def _default_build(conversation_id: str) -> Any:
    from strands import Agent
    from strands.agent.conversation_manager import SlidingWindowConversationManager
    from strands.models.openai import OpenAIModel

    settings = get_settings()
    if not settings.mcp_tools_url:
        raise RuntimeError("MCP_TOOLS_URL is not set — the agent has no tools to call")

    model = OpenAIModel(
        client_args={"api_key": settings.openai_api_key},
        model_id=settings.openai_model_id,
    )
    return Agent(
        model=model,
        system_prompt=orchestrator_system_prompt(conversation_id),
        tools=mcp_tools.get_remote_tools(),
        conversation_manager=SlidingWindowConversationManager(window_size=24),
        callback_handler=None,
    )


def build_agent(conversation_id: str) -> Any:
    if AGENT_FACTORY is not None:
        return AGENT_FACTORY(conversation_id)
    return _default_build(conversation_id)
