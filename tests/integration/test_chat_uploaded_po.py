"""US1: single-turn processing with an uploaded PO (extract -> upsert -> reconcile)."""
from fastapi.testclient import TestClient

from app.agent.tools.po_lookup import lookup_purchase_order
from app.main import app
from tests import support


def test_uploaded_po_is_extracted_persisted_and_used(monkeypatch):
    support.install_fake_agent(
        monkeypatch,
        {"invoice": support.invoice_for_new_po(), "purchase_order": support.uploaded_po()},
    )
    with TestClient(app) as client:
        resp = client.post(
            "/chat",
            data={"message": "Invoice plus its PO."},
            files={
                "invoice": ("inv.png", support.png_bytes(), "image/png"),
                "po": ("po.png", support.png_bytes(), "image/png"),
            },
        )
    assert resp.status_code == 200
    d = resp.json()["decision"]
    assert d["matched_po"]["source"] == "uploaded"
    assert d["verdict"] == "APPROVED", d["reasons"]

    # PO is now retrievable from the database.
    found = lookup_purchase_order("PO-NEW-1")
    assert found["found"] is True
    assert found["purchase_order"]["vendor"]["name"] == "TechCore Solutions LLC"
