from app.schemas.decision import Decision
from app.schemas.invoice import ExtractedInvoice


def test_extracted_invoice_defaults_null_numerics():
    inv = ExtractedInvoice(invoice_number="INV-1")
    assert inv.subtotal is None and inv.total_amount is None
    assert inv.line_items == [] and inv.vendor.name is None


def test_check_and_reason_coercions():
    from app.schemas.decision import Check, ReasonCode

    assert Check.model_validate({"name": "currency", "status": "pass"}).id == "currency"
    assert ReasonCode.model_validate("financial_totals").code == "financial_totals"
    assert ReasonCode.model_validate({"id": "sales_tax"}).code == "sales_tax"
    assert ReasonCode.model_validate({"detail": "x"}).code == "unspecified"


def test_decision_roundtrip():
    d = Decision(verdict="APPROVED", extracted_invoice=ExtractedInvoice(invoice_number="INV-9"))
    dumped = d.model_dump()
    assert Decision.model_validate(dumped).verdict == "APPROVED"
