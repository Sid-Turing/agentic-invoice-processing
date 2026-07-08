"""Vision extraction via a Gemini-backed Strands structured-output call.

The actual model call lives in `_vision_structured_output`, isolated so tests can
stub it without hitting the provider. Prompts come from app.agent.prompts.
"""
from __future__ import annotations

from typing import Literal, TypeVar

from pydantic import BaseModel

from app.agent.prompts import INVOICE_EXTRACTION_PROMPT, PO_EXTRACTION_PROMPT
from app.config import get_settings
from app.schemas.invoice import ExtractedInvoice
from app.schemas.purchase_order import PurchaseOrder

T = TypeVar("T", bound=BaseModel)

DocumentType = Literal["invoice", "purchase_order"]


def _image_blocks(images: list[bytes]) -> list[dict]:
    return [{"image": {"format": "png", "source": {"bytes": img}}} for img in images]


def _vision_structured_output(prompt: str, images: list[bytes], output_model: type[T]) -> T:
    """Run one Gemini structured-output call over the prompt + page images.

    Isolated for testing — monkeypatch this in unit tests.
    """
    from strands import Agent
    from strands.models.gemini import GeminiModel

    settings = get_settings()
    model = GeminiModel(
        client_args={"api_key": settings.gemini_api_key},
        model_id=settings.gemini_model_id,
        params={"temperature": 0.1},
    )
    agent = Agent(model=model, callback_handler=None)
    content = [{"text": prompt}, *_image_blocks(images)]
    result = agent(content, structured_output_model=output_model)
    return result.structured_output


def extract(images: list[bytes], document_type: DocumentType) -> ExtractedInvoice | PurchaseOrder:
    """Extract a typed model from rendered page images. Raises ValueError if the
    model returns nothing usable."""
    if not images:
        raise ValueError("no page images to extract from")
    if document_type == "invoice":
        result = _vision_structured_output(INVOICE_EXTRACTION_PROMPT, images, ExtractedInvoice)
    else:
        result = _vision_structured_output(PO_EXTRACTION_PROMPT, images, PurchaseOrder)
    if result is None:
        raise ValueError("extraction produced no structured data")
    return result
