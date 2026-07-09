"""PDF→image rendering + Gemini structured extraction (self-contained)."""
from __future__ import annotations

import io
import os

from schemas import ExtractedInvoice, PurchaseOrder

_MAX_DIM = 1600

INVOICE_PROMPT = """\
Extract information from this INVOICE image into the structured schema. Focus on accuracy.
- If a value is not present, use null. Normalize currency to a 3-letter ISO code; treat "$" as "USD".
- Dates must be YYYY-MM-DD. Line-item tax_rate: convert any percentage to a decimal.
- Capture the vendor + customer blocks, all line items, and the PO number if referenced.
"""
PO_PROMPT = """\
Extract information from this PURCHASE ORDER image into the structured schema. Focus on accuracy.
- If a value is not present, use null. Dates must be YYYY-MM-DD; item_tax_rate as a decimal.
- Capture the po_number, vendor block, totals, and every line item.
"""


def to_png_pages(data: bytes, mime: str | None = None) -> list[bytes]:
    from PIL import Image

    def _png(img) -> bytes:
        img = img.convert("RGB")
        w, h = img.size
        if max(w, h) > _MAX_DIM:
            scale = _MAX_DIM / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    if data[:4] == b"%PDF" or (mime or "").endswith("pdf"):
        from pdf2image import convert_from_bytes
        pages = convert_from_bytes(data, dpi=300)   # PPM (dodges poppler libpng issues)
        if not pages:
            raise ValueError("PDF produced no pages")
        return [_png(p) for p in pages]
    with Image.open(io.BytesIO(data)) as im:
        return [_png(im)]


def _vision(prompt: str, images: list[bytes], output_model):
    from strands import Agent
    from strands.models.gemini import GeminiModel

    model = GeminiModel(
        client_args={"api_key": os.getenv("GEMINI_API_KEY", "")},
        model_id=os.getenv("GEMINI_MODEL_ID", "gemini-3.5-flash"),
        params={"temperature": 0.1},
    )
    agent = Agent(model=model, callback_handler=None)
    content = [{"text": prompt}, *({"image": {"format": "png", "source": {"bytes": img}}} for img in images)]
    return agent(content, structured_output_model=output_model).structured_output


def extract(data: bytes, mime: str | None, document_type: str):
    pages = to_png_pages(data, mime)
    if document_type == "invoice":
        return _vision(INVOICE_PROMPT, pages, ExtractedInvoice)
    return _vision(PO_PROMPT, pages, PurchaseOrder)
