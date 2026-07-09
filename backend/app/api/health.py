"""GET /health — liveness/readiness probe."""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.db.database import session_scope
from app.schemas.chat import HealthResponse

router = APIRouter()


def _db_ok() -> bool:
    try:
        with session_scope() as session:
            session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    providers = {
        "openai": bool(settings.openai_api_key),   # orchestrator model
        "mcp_tools": bool(settings.mcp_tools_url),  # external tools server configured
    }
    database = _db_ok()
    status = "ok" if (database and providers["openai"] and providers["mcp_tools"]) else "degraded"
    return HealthResponse(status=status, providers=providers, database=database)
