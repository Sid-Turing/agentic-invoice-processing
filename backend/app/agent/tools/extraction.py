"""Vision extraction tool: reads an uploaded attachment into structured data."""
from __future__ import annotations

from typing import Literal

from strands import tool

from app.agent import conversation
from app.services import extraction_service, pdf_service


@tool
def extract_document(attachment_id: str, document_type: Literal["invoice", "purchase_order"]) -> dict:
    """Extract structured data from an uploaded document image/PDF using the vision model.

    Args:
        attachment_id: Id of the uploaded file (from the message's Attachments list).
        document_type: Whether to extract an 'invoice' or a 'purchase_order'.
    """
    att = conversation.get_attachment(attachment_id)
    if att is None:
        return {"error": f"no attachment with id '{attachment_id}'", "kind": "missing"}
    try:
        pages = pdf_service.to_png_pages(att.data, att.mime)
    except ValueError as exc:
        return {"error": str(exc), "kind": "unreadable"}
    try:
        result = extraction_service.extract(pages, document_type)
    except ValueError as exc:
        return {"error": str(exc), "kind": "empty"}
    return result.model_dump()
