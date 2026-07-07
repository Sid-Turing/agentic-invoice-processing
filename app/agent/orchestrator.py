"""Builds the orchestrator agent (OpenAI model + the five tools + conversation
window). An AGENT_FACTORY seam lets tests inject a deterministic fake agent."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.agent.prompts import orchestrator_system_prompt
from app.agent.tools.extraction import extract_document
from app.agent.tools.math_tool import calculate
from app.agent.tools.persistence import store_decision, store_purchase_order
from app.agent.tools.po_lookup import lookup_purchase_order
from app.config import get_settings

TOOLS = [extract_document, lookup_purchase_order, store_purchase_order, store_decision, calculate]

# Test seam: set to a callable (conversation_id) -> agent to bypass live providers.
AGENT_FACTORY: Callable[[str], Any] | None = None


def _default_build(conversation_id: str) -> Any:
    from strands import Agent
    from strands.agent.conversation_manager import SlidingWindowConversationManager
    from strands.models.openai import OpenAIModel

    settings = get_settings()
    model = OpenAIModel(
        client_args={"api_key": settings.openai_api_key},
        model_id=settings.openai_model_id,
        params={"temperature": 0.0},
    )
    return Agent(
        model=model,
        system_prompt=orchestrator_system_prompt(),
        tools=TOOLS,
        conversation_manager=SlidingWindowConversationManager(window_size=24),
        callback_handler=None,
    )


def build_agent(conversation_id: str) -> Any:
    if AGENT_FACTORY is not None:
        return AGENT_FACTORY(conversation_id)
    return _default_build(conversation_id)
