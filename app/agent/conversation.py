"""Per-conversation agent registry + request-scoped context.

- Attachments flow INTO tools via a contextvar (raw bytes, request-scoped only).
- The persisted Decision flows OUT of the store_decision tool via a contextvar
  so the handler can build the ChatResponse.
- Each conversation_id gets its own Agent (message history) + an asyncio.Lock to
  serialize turns. Provider clients/tools are shared; only the Agent is per-convo.
"""
from __future__ import annotations

import asyncio
import uuid
from contextvars import ContextVar
from dataclasses import dataclass

# --------------------------------------------------------------------------- #
# Request-scoped context
# --------------------------------------------------------------------------- #


@dataclass
class Attachment:
    data: bytes
    mime: str | None
    doc_hint: str  # "invoice" | "purchase_order" | "unknown"


_attachments: ContextVar[dict[str, Attachment]] = ContextVar("attachments", default={})
_stashed_decision: ContextVar[dict | None] = ContextVar("stashed_decision", default=None)
_current_conversation_id: ContextVar[str | None] = ContextVar("current_conversation_id", default=None)


def set_attachments(attachments: dict[str, Attachment]):
    _attachments.set(attachments)


def get_attachment(attachment_id: str) -> Attachment | None:
    return _attachments.get().get(attachment_id)


def set_current_conversation_id(conversation_id: str | None):
    _current_conversation_id.set(conversation_id)


def get_current_conversation_id() -> str | None:
    return _current_conversation_id.get()


def reset_request_context():
    _attachments.set({})
    _stashed_decision.set(None)
    _current_conversation_id.set(None)


def stash_decision(decision: dict):
    _stashed_decision.set(decision)


def get_stashed_decision() -> dict | None:
    return _stashed_decision.get()


# --------------------------------------------------------------------------- #
# Conversation registry
# --------------------------------------------------------------------------- #


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
