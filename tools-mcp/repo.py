"""Read + upsert data access over the PO reference tables. Dict in / dict out."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import PoLineItem, PoVendor, ProcessedInvoice, PurchaseOrder, Upload


def _num(v):
    return float(v) if v is not None else None


def get_purchase_order_by_number(session: Session, po_number: str) -> dict | None:
    row = session.scalar(select(PurchaseOrder).where(PurchaseOrder.po_number == po_number))
    if row is None:
        return None
    v = row.vendor
    return {
        "po_number": row.po_number,
        "po_date": row.po_date,
        "due_date": row.due_date,
        "subtotal": _num(row.subtotal),
        "total_tax_amount": _num(row.total_tax_amount),
        "total_amount": _num(row.total_amount),
        "currency": row.currency,
        "payment_terms": row.payment_terms,
        "destination_state": row.destination_state,
        "status": row.status,
        "vendor": {
            "name": v.name if v else None,
            "tax_id": v.tax_id if v else None,
            "street_address": v.street_address if v else None,
            "city": v.city if v else None,
            "state": v.state if v else None,
            "zip_code": v.zip_code if v else None,
            "bank_name": v.bank_name if v else None,
            "account_number": v.account_number if v else None,
            "routing_number": v.routing_number if v else None,
            "swift_code": v.swift_code if v else None,
            "tax_classification": v.tax_classification if v else None,
        },
        "line_items": [
            {
                "description": li.description,
                "quantity": _num(li.quantity),
                "unit_price": _num(li.unit_price),
                "item_tax_rate": _num(li.item_tax_rate),
                "total_price": _num(li.total_price),
                "category": li.category,
            }
            for li in row.line_items
        ],
        "source": "database",
    }


def get_upload(session: Session, attachment_id: str):
    row = session.get(Upload, attachment_id)
    return (row.data, row.mime) if row else (None, None)


def persist_decision(session: Session, decision: dict, conversation_id: str | None) -> str:
    import uuid as _uuid
    inv = decision.get("extracted_invoice") or {}
    mp = decision.get("matched_po")
    record_id = str(_uuid.uuid4())
    session.add(ProcessedInvoice(
        record_id=record_id,
        conversation_id=conversation_id,
        invoice_number=inv.get("invoice_number"),
        verdict=decision["verdict"],
        reason_codes=decision.get("reasons") or [],
        checks=decision.get("checks") or [],
        explanation=decision.get("explanation") or "",
        extracted_invoice=inv,
        matched_po_number=(mp or {}).get("po_number") if mp else None,
        matched_po_source=(mp or {}).get("source") if mp else None,
        matched_po=mp,
    ))
    session.flush()
    return record_id


def _resolve_or_create_vendor(session: Session, vendor: dict) -> PoVendor:
    name = vendor.get("name")
    tax_id = vendor.get("tax_id")
    row = None
    if name:
        stmt = select(PoVendor).where(PoVendor.name == name)
        if tax_id:
            stmt = stmt.where(PoVendor.tax_id == tax_id)
        row = session.scalar(stmt)
    if row is None:
        row = PoVendor(id=str(uuid.uuid4()))
        session.add(row)
    for f in ("name", "tax_id", "state", "street_address", "city", "zip_code",
              "bank_name", "account_number", "routing_number", "swift_code", "tax_classification"):
        setattr(row, f, vendor.get(f))
    session.flush()
    return row


def upsert_purchase_order(session: Session, po: dict) -> str:
    po_number = po["po_number"]
    vendor = _resolve_or_create_vendor(session, po.get("vendor") or {})
    row = session.scalar(select(PurchaseOrder).where(PurchaseOrder.po_number == po_number))
    if row is None:
        row = PurchaseOrder(id=str(uuid.uuid4()), po_number=po_number)
        session.add(row)
    row.vendor_id = vendor.id
    for f in ("po_date", "due_date", "subtotal", "total_tax_amount", "total_amount",
              "currency", "payment_terms", "destination_state", "status"):
        setattr(row, f, po.get(f))
    row.line_items.clear()
    session.flush()
    for li in po.get("line_items") or []:
        row.line_items.append(PoLineItem(
            description=li.get("description"),
            quantity=li.get("quantity"),
            unit_price=li.get("unit_price"),
            item_tax_rate=li.get("item_tax_rate"),
            total_price=li.get("total_price"),
            category=li.get("category"),
        ))
    session.flush()
    return po_number
