"""POST /chat — conversational, multimodal entry point (thin handler)."""
from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

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


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(default=""),
    conversation_id: str | None = Form(default=None),
    invoice: UploadFile | None = File(default=None),
    po: UploadFile | None = File(default=None),
) -> ChatResponse:
    conv_id = conversation_id or conversation.new_conversation_id()

    # Collect uploads into the request-scoped attachment store.
    attachments: dict[str, conversation.Attachment] = {}
    attachment_lines: list[str] = []
    if invoice is not None:
        attachments["invoice_1"] = await _read_upload(invoice, "invoice")
        attachment_lines.append(f"invoice=invoice_1 ({invoice.content_type or 'unknown'})")
    if po is not None:
        attachments["po_1"] = await _read_upload(po, "purchase_order")
        attachment_lines.append(f"po=po_1 ({po.content_type or 'unknown'})")

    conversation.reset_request_context(conv_id)
    conversation.set_attachments(attachments)
    conversation.set_current_conversation_id(conv_id)

    user_text = message or ("Process the attached document(s)." if attachments else "")
    prompt = user_text
    if attachment_lines:
        prompt = f"{user_text}\nAttachments: {'; '.join(attachment_lines)}"

    entry = conversation.get_or_create(conv_id)
    try:
        async with entry.lock:
            result = await entry.agent.invoke_async(prompt)
    except HTTPException:
        raise
    except Exception as exc:  # provider/DB failure -> transient, retryable
        raise HTTPException(status_code=503, detail=f"transient processing failure: {exc}") from exc

    stashed = conversation.pop_decision(conv_id)
    decision = Decision.model_validate(stashed) if stashed else None

    return ChatResponse(conversation_id=conv_id, message=str(result), decision=decision)
