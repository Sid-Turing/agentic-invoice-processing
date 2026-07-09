"""Builds the orchestrator agent (OpenAI model + the five tools + conversation
window). An AGENT_FACTORY seam lets tests inject a deterministic fake agent."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import logging

from app.agent import mcp_tools
from app.agent.prompts import orchestrator_system_prompt
from app.agent.tools.extraction import extract_document
from app.agent.tools.math_tool import calculate
from app.agent.tools.persistence import store_decision, store_purchase_order
from app.agent.tools.po_lookup import lookup_purchase_order
from app.config import get_settings

logger = logging.getLogger(__name__)

# Always in-process (need request-scoped state): extraction + decision persistence.
_LOCAL_ALWAYS = [extract_document, store_decision]
# Externalizable (DB-only): served by the MCP tools server when MCP_TOOLS_URL is set.
_LOCAL_EXTERNALIZABLE = [calculate, lookup_purchase_order, store_purchase_order]

# Test seam: set to a callable (conversation_id) -> agent to bypass live providers.
AGENT_FACTORY: Callable[[str], Any] | None = None


def _build_tools() -> list:
    """Remote MCP tools for the DB-only three when configured; else all in-process.
    Falls back to local if the MCP server can't be reached."""
    if get_settings().mcp_tools_url:
        try:
            remote = mcp_tools.get_remote_tools()
            if remote:
                return [*_LOCAL_ALWAYS, *remote]
        except Exception as exc:  # MCP server down/unreachable -> degrade gracefully
            logger.warning("MCP tools unavailable (%s); using in-process tools", exc)
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
