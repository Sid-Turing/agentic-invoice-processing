"""SSE streaming — step-by-step events (meta/tool/tool_result/token/decision/done)."""
import json

from fastapi.testclient import TestClient

from app.main import app
from tests import support


def _parse_sse(text: str):
    events = []
    for block in text.strip().split("\n\n"):
        ev, data = None, None
        for line in block.splitlines():
            if line.startswith("event: "):
                ev = line[len("event: "):]
            elif line.startswith("data: "):
                data = json.loads(line[len("data: "):])
        if ev:
            events.append((ev, data))
    return events


def test_stream_emits_tool_result_and_decision(monkeypatch):
    support.install_fake_agent(monkeypatch, {"invoice": support.invoice_matching_po_54872()})
    with TestClient(app) as client:
        resp = client.post(
            "/chat/stream",
            data={"message": "Process."},
            files={"invoice": ("inv.png", support.png_bytes(), "image/png")},
        )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    events = _parse_sse(resp.text)
    kinds = [e for e, _ in events]
    assert kinds[0] == "meta"
    assert "tool" in kinds
    assert "tool_result" in kinds
    assert "token" in kinds
    assert kinds[-1] == "done"
    decision = next(d for e, d in events if e == "decision")
    assert decision["verdict"] == "APPROVED"
    assert decision["matched_po"]["source"] == "database"
