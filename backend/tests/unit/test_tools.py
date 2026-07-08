import pytest

from app.agent import conversation
from app.agent.tools.math_tool import calculate, evaluate
from app.agent.tools.persistence import store_decision, store_purchase_order
from app.agent.tools.po_lookup import lookup_purchase_order
from app.schemas.invoice import VendorInfo
from app.schemas.purchase_order import POLineItem, PurchaseOrder


def test_calculate_arithmetic():
    assert calculate("4250*2 + 5800") == 14300.0
    assert evaluate("(10-2)/4") == 2.0


def test_calculate_rejects_names_and_calls():
    for bad in ["__import__('os')", "a+1", "len([1])"]:
        with pytest.raises((ValueError, SyntaxError)):
            evaluate(bad)


def test_lookup_not_found(db_session):
    assert lookup_purchase_order("MISSING") == {"found": False}


def test_store_po_then_lookup(db_session):
    po = PurchaseOrder(
        po_number="PO-XY",
        currency="USD",
        vendor=VendorInfo(name="Vend Co"),
        line_items=[POLineItem(description="Item", quantity=1, unit_price=5, total_price=5)],
    )
    out = store_purchase_order(po.model_dump())
    assert out == {"stored": True, "po_number": "PO-XY"}
    found = lookup_purchase_order("PO-XY")
    assert found["found"] and found["purchase_order"]["vendor"]["name"] == "Vend Co"


def test_store_decision_returns_record_and_stashes(db_session):
    conversation.set_current_conversation_id("conv-1")
    decision = {
        "verdict": "APPROVED",
        "reasons": [],
        "checks": [{"id": "currency", "status": "pass"}],
        "explanation": "ok",
        "extracted_invoice": {"invoice_number": "INV-1"},
        "matched_po": None,
    }
    out = store_decision(decision)
    assert "record_id" in out
    stashed = conversation.pop_decision("conv-1")
    assert stashed["record_id"] == out["record_id"]
    assert stashed["verdict"] == "APPROVED"


def test_extract_document_missing_attachment():
    from app.agent.tools.extraction import extract_document

    conversation.set_attachments({})
    out = extract_document("nope", "invoice")
    assert out["kind"] == "missing"
