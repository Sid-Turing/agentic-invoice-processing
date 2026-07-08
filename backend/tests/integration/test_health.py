from fastapi.testclient import TestClient

from app.main import app


def test_health_ok(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    from app.config import get_settings

    get_settings.cache_clear()
    with TestClient(app) as client:
        resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["database"] is True
    assert set(body["providers"]) == {"openai", "gemini"}
    get_settings.cache_clear()
