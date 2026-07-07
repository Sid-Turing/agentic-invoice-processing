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
_current_conversation_id: ContextVar[str | None] = ContextVar("current_conversation_id", default=None)

# Decisions flow OUT of store_decision (which runs in a Strands worker thread) via a
# plain module-level dict keyed by conversation_id — a contextvar set inside the tool
# thread would NOT propagate back to the request handler's context.
_results: dict[str, dict] = {}


def set_attachments(attachments: dict[str, Attachment]):
    _attachments.set(attachments)


def get_attachment(attachment_id: str) -> Attachment | None:
    return _attachments.get().get(attachment_id)


def set_current_conversation_id(conversation_id: str | None):
    _current_conversation_id.set(conversation_id)


def get_current_conversation_id() -> str | None:
    return _current_conversation_id.get()


def reset_request_context(conversation_id: str | None = None):
    _attachments.set({})
    _current_conversation_id.set(None)
    if conversation_id is not None:
        _results.pop(conversation_id, None)


def stash_decision(conversation_id: str | None, decision: dict):
    if conversation_id is not None:
        _results[conversation_id] = decision


def pop_decision(conversation_id: str) -> dict | None:
    return _results.pop(conversation_id, None)


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
    _results.clear()
