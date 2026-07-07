"""US3: the structured decision trace is complete and consistent."""
from fastapi.testclient import TestClient

from app.main import app
from tests import support


def test_trace_completeness_and_po_source(monkeypatch):
    support.install_fake_agent(monkeypatch, {"invoice": support.invoice_matching_po_54872()})
    with TestClient(app) as client:
        resp = client.post(
            "/chat",
            data={"message": "Process."},
            files={"invoice": ("inv.png", support.png_bytes(), "image/png")},
        )
    d = resp.json()["decision"]
    ids = {c["id"] for c in d["checks"]}
    # Every expected check appears in the trace.
    assert {
        "mandatory_fields",
        "currency",
        "line_item_math",
        "sales_tax",
        "financial_totals",
        "po_vendor_match",
        "po_line_items_match",
    } <= ids
    # Semantic check carries a confidence.
    vendor_check = next(c for c in d["checks"] if c["id"] == "po_vendor_match")
    assert vendor_check["confidence"] is not None
    # Resolved PO source is present.
    assert d["matched_po"]["source"] == "database"
    # Verdict is consistent with the checks.
    has_fail = any(c["status"] == "fail" for c in d["checks"])
    assert d["verdict"] == ("NEEDS_REVIEW" if has_fail else "APPROVED")
