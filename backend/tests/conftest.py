"""Test harness: in-memory SQLite schema (portable ORM types), provider-free
extraction stub, and a deterministic fake orchestrator agent via AGENT_FACTORY."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import database as db_module
from app.db.models import Base


@pytest.fixture()
def engine():
    # StaticPool keeps ONE shared connection so the in-memory DB is visible across
    # sessions and threads (TestClient runs the app in a worker thread).
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture()
def session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(autouse=True)
def _wire_db(engine, session_factory, monkeypatch):
    """Point app.db.database at the in-memory engine for every test."""
    monkeypatch.setattr(db_module, "_engine", engine, raising=False)
    monkeypatch.setattr(db_module, "_SessionLocal", session_factory, raising=False)
    monkeypatch.setattr(db_module, "get_engine", lambda: engine)
    monkeypatch.setattr(db_module, "get_sessionmaker", lambda: session_factory)
    yield


@pytest.fixture(autouse=True)
def _clean_conversation_state():
    from app.agent import conversation

    conversation.clear_registry()
    conversation.reset_request_context()
    yield
    conversation.clear_registry()
    conversation.reset_request_context()


@pytest.fixture()
def db_session(session_factory):
    s = session_factory()
    try:
        yield s
    finally:
        s.rollback()
        s.close()
