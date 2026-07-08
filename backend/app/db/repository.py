"""Pure data-access. The only writes are upsert_purchase_order and persist_decision
(SEC-004 / FR-022): no deletes of reference data; a stored PO changes only via
upsert of a freshly uploaded PO of the same number."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models
from app.schemas.decision import Decision
from app.schemas.invoice import VendorInfo
from app.schemas.purchase_order import POLineItem, PurchaseOrder


def get_purchase_order_by_number(session: Session, po_number: str) -> PurchaseOrder | None:
    """Read a PO (with vendor + line items) by number. Returns None if absent."""
    row = session.scalar(select(models.PurchaseOrder).where(models.PurchaseOrder.po_number == po_number))
    if row is None:
        return None
    vendor = row.vendor
    return PurchaseOrder(
        po_number=row.po_number,
        po_date=row.po_date,
        due_date=row.due_date,
        subtotal=float(row.subtotal) if row.subtotal is not None else None,
        total_tax_amount=float(row.total_tax_amount) if row.total_tax_amount is not None else None,
        total_amount=float(row.total_amount) if row.total_amount is not None else None,
        currency=row.currency,
        payment_terms=row.payment_terms,
        destination_state=row.destination_state,
        status=row.status,
        vendor=VendorInfo(
            name=vendor.name if vendor else None,
            tax_id=vendor.tax_id if vendor else None,
            street_address=vendor.street_address if vendor else None,
            city=vendor.city if vendor else None,
            state=vendor.state if vendor else None,
            zip_code=vendor.zip_code if vendor else None,
            bank_name=vendor.bank_name if vendor else None,
            account_number=vendor.account_number if vendor else None,
            routing_number=vendor.routing_number if vendor else None,
            swift_code=vendor.swift_code if vendor else None,
            tax_classification=vendor.tax_classification if vendor else None,
        ),
        line_items=[
            POLineItem(
                description=li.description or "",
                quantity=float(li.quantity) if li.quantity is not None else 0.0,
                unit_price=float(li.unit_price) if li.unit_price is not None else 0.0,
                item_tax_rate=float(li.item_tax_rate) if li.item_tax_rate is not None else None,
                total_price=float(li.total_price) if li.total_price is not None else 0.0,
                category=li.category,
            )
            for li in row.line_items
        ],
        source="database",
    )


def _resolve_or_create_vendor(session: Session, vendor: VendorInfo) -> models.PoVendor:
    row = None
    if vendor.name:
        stmt = select(models.PoVendor).where(models.PoVendor.name == vendor.name)
        if vendor.tax_id:
            stmt = stmt.where(models.PoVendor.tax_id == vendor.tax_id)
        row = session.scalar(stmt)
    if row is None:
        row = models.PoVendor(id=str(uuid.uuid4()))
        session.add(row)
    row.name = vendor.name
    row.tax_id = vendor.tax_id
    row.state = vendor.state
    row.street_address = vendor.street_address
    row.city = vendor.city
    row.zip_code = vendor.zip_code
    row.bank_name = vendor.bank_name
    row.account_number = vendor.account_number
    row.routing_number = vendor.routing_number
    row.swift_code = vendor.swift_code
    row.tax_classification = vendor.tax_classification
    session.flush()
    return row


def upsert_purchase_order(session: Session, po: PurchaseOrder) -> str:
    """Create or update a PO by po_number; replace its line items. Returns po_number."""
    vendor = _resolve_or_create_vendor(session, po.vendor)
    row = session.scalar(
        select(models.PurchaseOrder).where(models.PurchaseOrder.po_number == po.po_number)
    )
    if row is None:
        row = models.PurchaseOrder(id=str(uuid.uuid4()), po_number=po.po_number)
        session.add(row)
    row.vendor_id = vendor.id
    row.po_date = po.po_date
    row.due_date = po.due_date
    row.subtotal = po.subtotal
    row.total_tax_amount = po.total_tax_amount
    row.total_amount = po.total_amount
    row.currency = po.currency
    row.payment_terms = po.payment_terms
    row.destination_state = po.destination_state
    row.status = po.status
    # Replace line items (orphans deleted via cascade).
    row.line_items.clear()
    session.flush()
    for li in po.line_items:
        row.line_items.append(
            models.PoLineItem(
                description=li.description,
                quantity=li.quantity,
                unit_price=li.unit_price,
                item_tax_rate=li.item_tax_rate,
                total_price=li.total_price,
                category=li.category,
            )
        )
    session.flush()
    return row.po_number


def persist_decision(session: Session, decision: Decision, conversation_id: str | None) -> str:
    """Insert one processed_invoices row. Returns the record_id."""
    record_id = str(uuid.uuid4())
    row = models.ProcessedInvoice(
        record_id=record_id,
        conversation_id=conversation_id,
        invoice_number=decision.extracted_invoice.invoice_number,
        verdict=decision.verdict,
        reason_codes=[r.model_dump() for r in decision.reasons],
        checks=[c.model_dump() for c in decision.checks],
        explanation=decision.explanation,
        extracted_invoice=decision.extracted_invoice.model_dump(),
        matched_po_number=decision.matched_po.po_number if decision.matched_po else None,
        matched_po_source=decision.matched_po.source if decision.matched_po else None,
        matched_po=decision.matched_po.model_dump() if decision.matched_po else None,
    )
    session.add(row)
    session.flush()
    return record_id
