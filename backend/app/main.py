"""FastAPI application entry point (backend API only — the UI is a separate repo).

Schema is created out-of-band by `alembic upgrade head`. On startup we seed the
reference tables (skip-if-exists).
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, health, reports
from app.config import get_settings
from app.db.database import session_scope
from app.db.seed import seed_reference_data

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    try:
        with session_scope() as session:
            counts = seed_reference_data(session, settings.data_dir)
        if counts:
            logger.info("seeded reference data: %s", counts)
    except Exception as exc:  # DB not migrated/reachable yet — surfaced via /health
        logger.warning("startup seeding skipped: %s", exc)

    if settings.mcp_tools_url:
        from app.agent import mcp_tools
        try:
            mcp_tools.get_remote_tools()  # warm + validate the MCP connection
            logger.info("MCP tools connected: %s", settings.mcp_tools_url)
        except Exception as exc:
            # No local fallback: chat turns will 503 until the MCP server is reachable.
            logger.warning("MCP tools unreachable at %s (%s); chat will fail until it is up",
                           settings.mcp_tools_url, exc)
    yield
    from app.agent import mcp_tools
    mcp_tools.shutdown()


app = FastAPI(title="Agentic Invoice Processing", lifespan=lifespan)

# Local single-user tool: allow the separate frontend dev server to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(reports.router)
