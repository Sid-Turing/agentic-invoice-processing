"""US3: graceful handling of a non-processing (plain-text) message."""
from fastapi.testclient import TestClient

from app.main import app
from tests import support


def test_plaintext_message_no_decision(monkeypatch):
    support.install_fake_agent(monkeypatch, {"invoice": support.invoice_matching_po_54872()})
    with TestClient(app) as client:
        resp = client.post("/chat", data={"message": "Hi, what can you do?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["decision"] is None
    assert body["message"]
    assert body["conversation_id"]
