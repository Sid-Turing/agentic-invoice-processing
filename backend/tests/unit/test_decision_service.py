from app.schemas.decision import Check
from app.schemas.invoice import ExtractedInvoice
from app.services import decision_service as ds


def test_within_absolute():
    assert ds.within(100.0, 100.01, 0.02)
    assert not ds.within(100.0, 100.5, 0.02)


def test_within_pct_and_zero_expected():
    assert ds.within_pct(100.0, 105.0, 0.05)
    assert not ds.within_pct(100.0, 110.0, 0.05)
    assert ds.within_pct(0.0, 0.0, 0.05)
    assert not ds.within_pct(0.0, 1.0, 0.05)


def test_expected_tax():
    assert ds.expected_tax(1000.0, 0.09125) == 91.25


def test_assemble_decision_derives_verdict_and_reasons():
    checks = [Check(id="currency", status="pass"), Check(id="financial_totals", status="fail", detail="off")]
    d = ds.assemble_decision(extracted_invoice=ExtractedInvoice(invoice_number="INV-1"), checks=checks)
    assert d.verdict == "NEEDS_REVIEW"
    assert [r.code for r in d.reasons] == ["financial_totals"]
