"""Read-only data access for the reporting surface. No writes anywhere here."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models


def list_processed_invoices(
    session: Session,
    verdict: str | None = None,
    since: datetime | None = None,
) -> list[models.ProcessedInvoice]:
    """All processed-invoice records, newest-first, optionally filtered by verdict
    and a created_at lower bound. Per-run grain (no de-duplication)."""
    stmt = select(models.ProcessedInvoice)
    if verdict:
        stmt = stmt.where(models.ProcessedInvoice.verdict == verdict)
    if since is not None:
        stmt = stmt.where(models.ProcessedInvoice.created_at >= since)
    stmt = stmt.order_by(models.ProcessedInvoice.created_at.desc())
    return list(session.scalars(stmt))


def get_processed_invoice(session: Session, record_id: str) -> models.ProcessedInvoice | None:
    return session.get(models.ProcessedInvoice, record_id)


def list_purchase_orders(session: Session) -> list[models.PurchaseOrder]:
    stmt = select(models.PurchaseOrder).order_by(models.PurchaseOrder.po_number)
    return list(session.scalars(stmt))


def list_vendors(session: Session) -> list[models.PoVendor]:
    stmt = select(models.PoVendor).order_by(models.PoVendor.name)
    return list(session.scalars(stmt))
