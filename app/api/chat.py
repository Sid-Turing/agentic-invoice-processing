"""POST /chat (complete response) and POST /chat/stream (SSE step-by-step)."""
from __future__ import annotations

import json
from dataclasses import dataclass

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.agent import conversation
from app.config import get_settings
from app.schemas.chat import ChatResponse
from app.schemas.decision import Decision

router = APIRouter()

_ALLOWED = {"application/pdf", "image/png", "image/jpeg", "image/jpg"}


async def _read_upload(file: UploadFile, hint: str) -> conversation.Attachment:
    data = await file.read()
    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail=f"{hint} file exceeds {get_settings().max_upload_mb} MB")
    if file.content_type and file.content_type not in _ALLOWED and not (file.filename or "").lower().endswith(
        (".pdf", ".png", ".jpg", ".jpeg")
    ):
        raise HTTPException(status_code=415, detail=f"unsupported {hint} file type: {file.content_type}")
    return conversation.Attachment(data=data, mime=file.content_type, doc_hint=hint)


@dataclass
class _Turn:
    conversation_id: str
    prompt: str
    attachments: dict[str, conversation.Attachment]


async def _prepare(message, conversation_id, invoice, po) -> _Turn:
    conv_id = conversation_id or conversation.new_conversation_id()
    attachments: dict[str, conversation.Attachment] = {}
    lines: list[str] = []
    if invoice is not None:
        attachments["invoice_1"] = await _read_upload(invoice, "invoice")
        lines.append(f"invoice=invoice_1 ({invoice.content_type or 'unknown'})")
    if po is not None:
        attachments["po_1"] = await _read_upload(po, "purchase_order")
        lines.append(f"po=po_1 ({po.content_type or 'unknown'})")
    text = message or ("Process the attached document(s)." if attachments else "")
    prompt = f"{text}\nAttachments: {'; '.join(lines)}" if lines else text
    return _Turn(conversation_id=conv_id, prompt=prompt, attachments=attachments)


def _bind_context(turn: _Turn) -> None:
    conversation.reset_request_context(turn.conversation_id)
    conversation.set_attachments(turn.attachments)
    conversation.set_current_conversation_id(turn.conversation_id)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(default=""),
    conversation_id: str | None = Form(default=None),
    invoice: UploadFile | None = File(default=None),
    po: UploadFile | None = File(default=None),
) -> ChatResponse:
    turn = await _prepare(message, conversation_id, invoice, po)
    _bind_context(turn)
    entry = conversation.get_or_create(turn.conversation_id)
    try:
        async with entry.lock:
            result = await entry.agent.invoke_async(turn.prompt)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"transient processing failure: {exc}") from exc

    stashed = conversation.pop_decision(turn.conversation_id)
    decision = Decision.model_validate(stashed) if stashed else None
    return ChatResponse(conversation_id=turn.conversation_id, message=str(result), decision=decision)


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/chat/stream")
async def chat_stream(
    message: str = Form(default=""),
    conversation_id: str | None = Form(default=None),
    invoice: UploadFile | None = File(default=None),
    po: UploadFile | None = File(default=None),
) -> StreamingResponse:
    """Same inputs as /chat, but streams the turn as Server-Sent Events:
    `meta` (conversation id) → `tool` (each tool the agent invokes) → `token`
    (assistant text chunks) → `decision` (structured result) → `done`."""
    turn = await _prepare(message, conversation_id, invoice, po)

    async def event_stream():
        _bind_context(turn)
        entry = conversation.get_or_create(turn.conversation_id)
        yield _sse("meta", {"conversation_id": turn.conversation_id})
        seen_tools: set[str] = set()
        try:
            async with entry.lock:
                async for event in entry.agent.stream_async(turn.prompt):
                    tool = event.get("current_tool_use") if isinstance(event, dict) else None
                    if tool and tool.get("toolUseId") and tool["toolUseId"] not in seen_tools:
                        seen_tools.add(tool["toolUseId"])
                        yield _sse("tool", {"name": tool.get("name"), "input": tool.get("input")})
                    elif isinstance(event, dict) and event.get("data"):
                        yield _sse("token", {"text": event["data"]})
        except Exception as exc:
            yield _sse("error", {"detail": f"transient processing failure: {exc}"})
            return
        stashed = conversation.pop_decision(turn.conversation_id)
        yield _sse("decision", stashed)
        yield _sse("done", {"conversation_id": turn.conversation_id})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
