"""Read-only reporting endpoints (feature 002). All GET; no mutations."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import read_repository as repo
from app.db.database import get_session
from app.db.repository import get_purchase_order_by_number
from app.schemas.purchase_order import PurchaseOrder
from app.schemas.reports import (
    InvoiceDetailResponse,
    InvoiceListResponse,
    PurchaseOrderListResponse,
    PurchaseOrderListRow,
    SummaryResponse,
    VendorListResponse,
    VendorRow,
)
from app.services import reporting_service as svc

router = APIRouter()


def _today():
    return datetime.now(timezone.utc).date()


def _window_since(window: str) -> datetime | None:
    now = datetime.now(timezone.utc)
    if window == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if window == "7d":
        return now - timedelta(days=7)
    if window == "30d":
        return now - timedelta(days=30)
    return None  # "all"


@router.get("/invoices", response_model=InvoiceListResponse)
def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int | None = Query(None, ge=1, le=100),
    verdict: str | None = Query(None, pattern="^(APPROVED|NEEDS_REVIEW)$"),
    window: str = Query("all", pattern="^(today|7d|30d|all)$"),
    q: str = Query(""),
    session: Session = Depends(get_session),
) -> InvoiceListResponse:
    settings = get_settings()
    size = page_size or settings.default_page_size
    records = repo.list_processed_invoices(session, verdict=verdict, since=_window_since(window))
    matched = [r for r in records if svc.search_matches(r, q)]
    rows = [svc.to_list_row(r) for r in matched]
    page_items, total = svc.paginate(rows, page, size)
    return InvoiceListResponse(items=page_items, total=total, page=page, page_size=size)


@router.get("/invoices/{record_id}", response_model=InvoiceDetailResponse)
def get_invoice(record_id: str, session: Session = Depends(get_session)) -> InvoiceDetailResponse:
    row = repo.get_processed_invoice(session, record_id)
    if row is None:
        raise HTTPException(status_code=404, detail="record not found")
    ca = row.created_at
    return InvoiceDetailResponse(
        record_id=row.record_id,
        conversation_id=row.conversation_id,
        created_at=ca.isoformat() if hasattr(ca, "isoformat") else str(ca),
        verdict=row.verdict,
        reasons=row.reason_codes or [],
        checks=row.checks or [],
        explanation=row.explanation or "",
        extracted_invoice=row.extracted_invoice or {},
        matched_po=row.matched_po,
    )


@router.get("/summary", response_model=SummaryResponse)
def summary(session: Session = Depends(get_session)) -> SummaryResponse:
    records = repo.list_processed_invoices(session)
    return svc.build_summary(records, _today(), get_settings().high_value_threshold)


@router.get("/purchase-orders", response_model=PurchaseOrderListResponse)
def list_purchase_orders(
    page: int = Query(1, ge=1),
    page_size: int | None = Query(None, ge=1, le=100),
    q: str = Query(""),
    session: Session = Depends(get_session),
) -> PurchaseOrderListResponse:
    size = page_size or get_settings().default_page_size
    pos = repo.list_purchase_orders(session)
    ql = q.strip().lower()
    if ql:
        pos = [p for p in pos if ql in (p.po_number or "").lower()]
    rows = [
        PurchaseOrderListRow(
            po_number=p.po_number,
            vendor_name=p.vendor.name if p.vendor else None,
            total_amount=float(p.total_amount) if p.total_amount is not None else None,
            currency=p.currency,
            po_date=p.po_date,
            due_date=p.due_date,
        )
        for p in pos
    ]
    start = (page - 1) * size
    return PurchaseOrderListResponse(items=rows[start:start + size], total=len(rows), page=page, page_size=size)


@router.get("/purchase-orders/{po_number}", response_model=PurchaseOrder)
def get_purchase_order(po_number: str, session: Session = Depends(get_session)) -> PurchaseOrder:
    po = get_purchase_order_by_number(session, po_number)
    if po is None:
        raise HTTPException(status_code=404, detail="purchase order not found")
    return po


@router.get("/vendors", response_model=VendorListResponse)
def list_vendors(q: str = Query(""), session: Session = Depends(get_session)) -> VendorListResponse:
    vendors = repo.list_vendors(session)
    ql = q.strip().lower()
    if ql:
        vendors = [v for v in vendors if ql in (v.name or "").lower()]
    rows = [
        VendorRow(
            name=v.name,
            tax_id=v.tax_id,
            address=", ".join(p for p in [v.street_address, v.city, v.state, v.zip_code] if p) or None,
            state=v.state,
        )
        for v in vendors
    ]
    return VendorListResponse(items=rows, total=len(rows))
