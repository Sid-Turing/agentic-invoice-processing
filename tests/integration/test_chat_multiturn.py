"""US2: multi-turn — invoice first, PO in a later turn reconciles the retained invoice."""
from fastapi.testclient import TestClient

from app.main import app
from tests import support


def test_po_arrives_in_later_turn(monkeypatch):
    # Invoice references a PO number that is NOT on file yet -> turn 1 skips reconciliation.
    inv = support.invoice_for_new_po(po_number="PO-LATER-1")
    support.install_fake_agent(
        monkeypatch,
        {"invoice": inv, "purchase_order": support.uploaded_po(po_number="PO-LATER-1")},
    )
    with TestClient(app) as client:
        r1 = client.post(
            "/chat",
            data={"message": "Process this invoice."},
            files={"invoice": ("inv.png", support.png_bytes(), "image/png")},
        )
        conv = r1.json()["conversation_id"]
        d1 = r1.json()["decision"]
        # reconciliation skipped (PO not found)
        skipped = {c["id"]: c for c in d1["checks"]}
        assert skipped["po_vendor_match"]["status"] == "skipped"
        assert "PO not found" in skipped["po_vendor_match"]["detail"]

        # Turn 2: upload the PO under the same conversation; no invoice re-upload.
        r2 = client.post(
            "/chat",
            data={"message": "Here is the PO for that invoice.", "conversation_id": conv},
            files={"po": ("po.png", support.png_bytes(), "image/png")},
        )
    assert r2.json()["conversation_id"] == conv
    d2 = r2.json()["decision"]
    assert d2["matched_po"]["source"] == "uploaded"
    assert d2["extracted_invoice"]["invoice_number"] == "INV-NEW-1"  # retained from turn 1
    assert d2["verdict"] == "APPROVED", d2["reasons"]
