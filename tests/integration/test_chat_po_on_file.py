"""US1: single-turn processing against a PO already on file (seeded PO-54872)."""
from fastapi.testclient import TestClient

from app.main import app
from tests import support


def _client():
    return TestClient(app)


def _post_invoice(client, files_bytes):
    return client.post(
        "/chat",
        data={"message": "Please process this invoice."},
        files={"invoice": ("invoice.png", files_bytes, "image/png")},
    )


def test_matching_invoice_approved(monkeypatch):
    support.install_fake_agent(monkeypatch, {"invoice": support.invoice_matching_po_54872()})
    with _client() as client:  # startup seeds PO-54872
        resp = _post_invoice(client, support.png_bytes())
    assert resp.status_code == 200
    body = resp.json()
    d = body["decision"]
    assert d["verdict"] == "APPROVED", d["reasons"]
    assert d["matched_po"]["source"] == "database"
    assert d["record_id"]


def test_financial_total_tamper_needs_review(monkeypatch):
    tampered = support.invoice_matching_po_54872(total_amount=99999.0)
    support.install_fake_agent(monkeypatch, {"invoice": tampered})
    with _client() as client:
        resp = _post_invoice(client, support.png_bytes())
    d = resp.json()["decision"]
    assert d["verdict"] == "NEEDS_REVIEW"
    assert "financial_totals" in [r["code"] for r in d["reasons"]]


def test_line_item_divergence_needs_review(monkeypatch):
    inv = support.invoice_matching_po_54872()
    inv.line_items[0].quantity = 20  # ECG Monitor qty 2 -> 20 (breaks PO match + line math)
    inv.line_items[0].total_price = 8500.0
    support.install_fake_agent(monkeypatch, {"invoice": inv})
    with _client() as client:
        resp = _post_invoice(client, support.png_bytes())
    d = resp.json()["decision"]
    assert d["verdict"] == "NEEDS_REVIEW"
    codes = [r["code"] for r in d["reasons"]]
    assert "po_line_items_match" in codes or "line_item_math" in codes
