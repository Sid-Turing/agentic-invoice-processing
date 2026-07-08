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


@pytest.fixture()
def seed_reports(session_factory):
    """Insert a labelled set of processed_invoices + reference data for reporting
    tests. Returns a dict of useful record ids. Uses fixed dates relative to a
    pinned 'today' the tests pass to the service (2026-07-08)."""
    from datetime import datetime, timezone

    from app.db import models, seed
    from app.config import get_settings

    def _rec(session, *, invoice_number, verdict, vendor, total, currency="USD",
             due_date=None, po_number=None, po_source=None, created_at):
        row = models.ProcessedInvoice(
            conversation_id="c",
            invoice_number=invoice_number,
            verdict=verdict,
            reason_codes=[],
            checks=[{"id": "mandatory_fields", "status": "pass", "detail": "ok"}],
            explanation="",
            extracted_invoice={
                "invoice_number": invoice_number,
                "due_date": due_date,
                "currency": currency,
                "total_amount": total,
                "vendor": {"name": vendor},
                "line_items": [{"description": "Item", "quantity": 1, "unit_price": total, "total_price": total}],
            },
            matched_po_number=po_number,
            matched_po_source=po_source,
            matched_po=None,
            created_at=created_at,
        )
        session.add(row)
        session.flush()
        return row.record_id

    s = session_factory()
    try:
        seed.seed_reference_data(s, get_settings().data_dir)  # POs + vendors
        now = datetime(2026, 7, 8, 12, 0, 0, tzinfo=timezone.utc)          # "today"
        older = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        ids = {
            # high value + overdue -> priority
            "priority": _rec(s, invoice_number="INV-P", verdict="APPROVED", vendor="Acme LLC",
                             total=8200.0, due_date="2026-07-01", po_number="PO-54872",
                             po_source="database", created_at=now),
            # approved, due in 3 days, low value -> not priority, bucket due_1_7
            "soon": _rec(s, invoice_number="INV-S", verdict="APPROVED", vendor="Beta Inc",
                         total=200.0, due_date="2026-07-11", created_at=now),
            # needs review, undated
            "review": _rec(s, invoice_number="INV-R", verdict="NEEDS_REVIEW", vendor="Gamma Co",
                           total=500.0, due_date=None, created_at=older),
            # approved, far future (15+)
            "future": _rec(s, invoice_number="INV-F", verdict="APPROVED", vendor="Delta LLC",
                           total=1000.0, due_date="2026-09-01", created_at=older),
        }
        s.commit()
        return ids
    finally:
        s.close()
