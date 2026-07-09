"""Chat endpoints: POST /chat (complete JSON) and POST /chat/stream (SSE).

Tools run on the external MCP server. Uploaded file bytes are pushed to the DB
`uploads` table (the remote extraction tool reads them); the decision is read back
from the DB after the turn.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.agent import conversation
from app.config import get_settings
from app.db.database import session_scope
from app.db.repository import delete_conversation_uploads, get_latest_decision, save_upload
from app.schemas.chat import ChatResponse

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


def _pre_turn(turn: _Turn) -> str | None:
    """Push upload bytes to the DB so the remote extraction tool can read them, and
    return the conversation's current latest decision id (to detect a new one)."""
    with session_scope() as s:
        for aid, att in turn.attachments.items():
            save_upload(s, aid, turn.conversation_id, att.mime, att.data)
        prev = get_latest_decision(s, turn.conversation_id)
        return prev.record_id if prev else None


def _resolve_decision(conversation_id: str, prev_record_id: str | None):
    """Read the decision back from the DB (only if this turn created a new record),
    then clean up the conversation's uploads."""
    with session_scope() as s:
        d = get_latest_decision(s, conversation_id)
        delete_conversation_uploads(s, conversation_id)
    return d if (d and d.record_id != prev_record_id) else None


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(default=""),
    conversation_id: str | None = Form(default=None),
    invoice: UploadFile | None = File(default=None),
    po: UploadFile | None = File(default=None),
) -> ChatResponse:
    turn = await _prepare(message, conversation_id, invoice, po)
    prev = _pre_turn(turn)
    entry = conversation.get_or_create(turn.conversation_id)
    try:
        async with entry.lock:
            result = await entry.agent.invoke_async(turn.prompt)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"transient processing failure: {exc}") from exc

    decision = _resolve_decision(turn.conversation_id, prev)
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
    """Same inputs as /chat, streamed as Server-Sent Events in true order:
    `meta` -> `tool` (each tool invoked) -> `tool_result` (what it returned) ->
    `token` (assistant text chunks) -> `decision` (structured result) -> `done`."""
    turn = await _prepare(message, conversation_id, invoice, po)

    async def event_stream():
        prev = _pre_turn(turn)
        entry = conversation.get_or_create(turn.conversation_id)
        yield _sse("meta", {"conversation_id": turn.conversation_id})
        seen_tools: set[str] = set()
        seen_results: set[str] = set()
        tool_names: dict[str, str] = {}
        try:
            async with entry.lock:
                async for event in entry.agent.stream_async(turn.prompt):
                    if not isinstance(event, dict):
                        continue
                    tool = event.get("current_tool_use")
                    if tool and tool.get("toolUseId"):
                        tid = tool["toolUseId"]
                        if tool.get("name"):
                            tool_names[tid] = tool["name"]
                        if tid not in seen_tools:
                            seen_tools.add(tid)
                            yield _sse("tool", {"name": tool.get("name")})
                    if event.get("data"):
                        yield _sse("token", {"text": event["data"]})
                    msg = event.get("message")
                    if isinstance(msg, dict):
                        for block in msg.get("content") or []:
                            tr = block.get("toolResult") if isinstance(block, dict) else None
                            if not tr or tr.get("toolUseId") in seen_results:
                                continue
                            seen_results.add(tr["toolUseId"])
                            text = "".join(
                                c.get("text", "") for c in (tr.get("content") or []) if isinstance(c, dict)
                            )
                            if len(text) > 600:
                                text = text[:600] + "…"
                            yield _sse(
                                "tool_result",
                                {"name": tool_names.get(tr["toolUseId"]), "status": tr.get("status"), "output": text},
                            )
        except Exception as exc:
            yield _sse("error", {"detail": f"transient processing failure: {exc}"})
            return
        decision = _resolve_decision(turn.conversation_id, prev)
        yield _sse("decision", decision.model_dump() if decision else None)
        yield _sse("done", {"conversation_id": turn.conversation_id})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
