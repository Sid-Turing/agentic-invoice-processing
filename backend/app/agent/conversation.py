"""Per-conversation agent registry.

Each conversation_id gets its own Agent (message history) + an asyncio.Lock to
serialize turns. Tool execution and request state now live outside the process
(the MCP tools server + the DB uploads/decision tables), so this module no longer
holds attachment bytes or decision stashes — just the agents.
"""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass


@dataclass
class Attachment:
    data: bytes
    mime: str | None
    doc_hint: str  # "invoice" | "purchase_order" | "unknown"


@dataclass
class _Entry:
    agent: object
    lock: asyncio.Lock


_registry: dict[str, _Entry] = {}


def new_conversation_id() -> str:
    return str(uuid.uuid4())


def get_or_create(conversation_id: str) -> _Entry:
    entry = _registry.get(conversation_id)
    if entry is None:
        from app.agent.orchestrator import build_agent

        entry = _Entry(agent=build_agent(conversation_id), lock=asyncio.Lock())
        _registry[conversation_id] = entry
    return entry


def clear_registry():
    _registry.clear()
