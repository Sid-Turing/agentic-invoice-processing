from app.schemas.decision import Check, Decision
from app.schemas.invoice import ExtractedInvoice
from app.services.decision_service import verdict_from_checks


def test_extracted_invoice_defaults_null_numerics():
    inv = ExtractedInvoice(invoice_number="INV-1")
    assert inv.subtotal is None and inv.total_amount is None
    assert inv.line_items == [] and inv.vendor.name is None


def test_verdict_approved_when_no_fail():
    checks = [Check(id="currency", status="pass"), Check(id="sales_tax", status="skipped")]
    assert verdict_from_checks(checks) == "APPROVED"


def test_verdict_needs_review_on_any_fail():
    checks = [Check(id="currency", status="pass"), Check(id="financial_totals", status="fail")]
    assert verdict_from_checks(checks) == "NEEDS_REVIEW"


def test_decision_roundtrip():
    d = Decision(verdict="APPROVED", extracted_invoice=ExtractedInvoice(invoice_number="INV-9"))
    dumped = d.model_dump()
    assert Decision.model_validate(dumped).verdict == "APPROVED"
