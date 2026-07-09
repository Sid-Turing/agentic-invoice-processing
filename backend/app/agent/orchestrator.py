"""Builds the orchestrator agent (OpenAI model + the five tools + conversation
window). An AGENT_FACTORY seam lets tests inject a deterministic fake agent."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.agent import mcp_tools
from app.agent.prompts import orchestrator_system_prompt
from app.agent.tools.extraction import extract_document
from app.agent.tools.math_tool import calculate
from app.agent.tools.persistence import store_decision, store_purchase_order
from app.agent.tools.po_lookup import lookup_purchase_order
from app.config import get_settings

# Always in-process (need request-scoped state): extraction + decision persistence.
_LOCAL_ALWAYS = [extract_document, store_decision]
# Externalizable (DB-only): used in-process ONLY when no MCP server is configured.
_LOCAL_EXTERNALIZABLE = [calculate, lookup_purchase_order, store_purchase_order]

# Test seam: set to a callable (conversation_id) -> agent to bypass live providers.
AGENT_FACTORY: Callable[[str], Any] | None = None


def _build_tools() -> list:
    """When MCP_TOOLS_URL is set the DB-only three come exclusively from the remote
    MCP server — no local fallback (a connection failure propagates and the turn
    fails with 503). Only when no MCP server is configured do they run in-process."""
    if get_settings().mcp_tools_url:
        return [*_LOCAL_ALWAYS, *mcp_tools.get_remote_tools()]
    return [*_LOCAL_ALWAYS, *_LOCAL_EXTERNALIZABLE]


def _default_build(conversation_id: str) -> Any:
    from strands import Agent
    from strands.agent.conversation_manager import SlidingWindowConversationManager
    from strands.models.openai import OpenAIModel

    settings = get_settings()
    # No temperature param: reasoning models (gpt-5.x / o-series) reject it.
    model = OpenAIModel(
        client_args={"api_key": settings.openai_api_key},
        model_id=settings.openai_model_id,
    )
    return Agent(
        model=model,
        system_prompt=orchestrator_system_prompt(),
        tools=_build_tools(),
        conversation_manager=SlidingWindowConversationManager(window_size=24),
        callback_handler=None,
    )


def build_agent(conversation_id: str) -> Any:
    if AGENT_FACTORY is not None:
        return AGENT_FACTORY(conversation_id)
    return _default_build(conversation_id)
