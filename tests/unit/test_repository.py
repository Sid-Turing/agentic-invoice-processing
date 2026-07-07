from app.db import repository
from app.schemas.decision import Check, Decision, ReasonCode
from app.schemas.invoice import ExtractedInvoice, VendorInfo
from app.schemas.purchase_order import POLineItem, PurchaseOrder


def _po(number="PO-1", qty=2.0, total=100.0):
    return PurchaseOrder(
        po_number=number,
        subtotal=total,
        total_amount=total,
        currency="USD",
        vendor=VendorInfo(name="Acme LLC", tax_id="12-3456789"),
        line_items=[POLineItem(description="Widget", quantity=qty, unit_price=50.0, total_price=total)],
    )


def test_lookup_missing_returns_none(db_session):
    assert repository.get_purchase_order_by_number(db_session, "NOPE") is None


def test_upsert_creates_then_reads_back(db_session):
    repository.upsert_purchase_order(db_session, _po())
    db_session.commit()
    got = repository.get_purchase_order_by_number(db_session, "PO-1")
    assert got is not None
    assert got.vendor.name == "Acme LLC"
    assert got.source == "database"
    assert len(got.line_items) == 1 and got.line_items[0].description == "Widget"


def test_upsert_updates_by_number_and_replaces_line_items(db_session):
    repository.upsert_purchase_order(db_session, _po(qty=2.0, total=100.0))
    db_session.commit()
    repository.upsert_purchase_order(db_session, _po(qty=5.0, total=250.0))
    db_session.commit()
    got = repository.get_purchase_order_by_number(db_session, "PO-1")
    assert got.total_amount == 250.0
    assert len(got.line_items) == 1 and got.line_items[0].quantity == 5.0


def test_persist_decision_returns_record_id(db_session):
    decision = Decision(
        verdict="NEEDS_REVIEW",
        reasons=[ReasonCode(code="currency", detail="EUR unsupported")],
        checks=[Check(id="currency", status="fail")],
        extracted_invoice=ExtractedInvoice(invoice_number="INV-5"),
    )
    rid = repository.persist_decision(db_session, decision, conversation_id="c1")
    db_session.commit()
    assert rid
    from app.db.models import ProcessedInvoice

    row = db_session.get(ProcessedInvoice, rid)
    assert row.verdict == "NEEDS_REVIEW" and row.conversation_id == "c1"
    assert row.reason_codes[0]["code"] == "currency"
