import pytest

from app.schemas.invoice import ExtractedInvoice
from app.schemas.purchase_order import PurchaseOrder
from app.services import extraction_service


def test_extract_invoice_routes_to_vision_and_returns_model(monkeypatch):
    captured = {}

    def fake_vision(prompt, images, output_model):
        captured["prompt"] = prompt
        captured["model"] = output_model
        return output_model(invoice_number="INV-42") if output_model is ExtractedInvoice else output_model(po_number="PO-1")

    monkeypatch.setattr(extraction_service, "_vision_structured_output", fake_vision)
    result = extraction_service.extract([b"png"], "invoice")
    assert isinstance(result, ExtractedInvoice)
    assert result.invoice_number == "INV-42"
    assert captured["model"] is ExtractedInvoice
    assert "INVOICE" in captured["prompt"]


def test_extract_purchase_order_uses_po_model(monkeypatch):
    monkeypatch.setattr(
        extraction_service,
        "_vision_structured_output",
        lambda prompt, images, model: PurchaseOrder(po_number="PO-77"),
    )
    result = extraction_service.extract([b"png"], "purchase_order")
    assert isinstance(result, PurchaseOrder) and result.po_number == "PO-77"


def test_extract_no_images_raises():
    with pytest.raises(ValueError):
        extraction_service.extract([], "invoice")


def test_extract_none_result_raises(monkeypatch):
    monkeypatch.setattr(extraction_service, "_vision_structured_output", lambda *a, **k: None)
    with pytest.raises(ValueError):
        extraction_service.extract([b"png"], "invoice")
