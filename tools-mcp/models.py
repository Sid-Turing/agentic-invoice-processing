"""ORM for the PO reference tables (mirrors the backend schema). Read + upsert only."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON, Boolean, DateTime, ForeignKey, Integer, LargeBinary, Numeric, String, Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class PoVendor(Base):
    __tablename__ = "po_vendors"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String, nullable=True)
    state: Mapped[str | None] = mapped_column(String, nullable=True)
    street_address: Mapped[str | None] = mapped_column(String, nullable=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String, nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String, nullable=True)
    account_number: Mapped[str | None] = mapped_column(String, nullable=True)
    routing_number: Mapped[str | None] = mapped_column(String, nullable=True)
    swift_code: Mapped[str | None] = mapped_column(String, nullable=True)
    tax_classification: Mapped[str | None] = mapped_column(String, nullable=True)
    tax_exempt: Mapped[bool] = mapped_column(Boolean, default=False)
    backup_withholding: Mapped[bool] = mapped_column(Boolean, default=False)
    tax_exemption_number: Mapped[str | None] = mapped_column(String, nullable=True)
    ifsc_code: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(back_populates="vendor")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    po_number: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    vendor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("po_vendors.id"), nullable=True)
    po_date: Mapped[str | None] = mapped_column(String, nullable=True)
    due_date: Mapped[str | None] = mapped_column(String, nullable=True)
    subtotal: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    total_tax_amount: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    total_amount: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String, nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String, nullable=True)
    destination_state: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
    vendor: Mapped[PoVendor | None] = relationship(back_populates="purchase_orders")
    line_items: Mapped[list["PoLineItem"]] = relationship(
        back_populates="purchase_order", cascade="all, delete-orphan"
    )


class PoLineItem(Base):
    __tablename__ = "purchase_order_line_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    po_id: Mapped[str] = mapped_column(String(36), ForeignKey("purchase_orders.id"), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    quantity: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    unit_price: Mapped[float | None] = mapped_column(Numeric(18, 5), nullable=True)
    item_tax_rate: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    total_price: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
    purchase_order: Mapped[PurchaseOrder] = relationship(back_populates="line_items")


class Upload(Base):
    __tablename__ = "uploads"
    attachment_id: Mapped[str] = mapped_column(String, primary_key=True)
    conversation_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    mime: Mapped[str | None] = mapped_column(String, nullable=True)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ProcessedInvoice(Base):
    __tablename__ = "processed_invoices"
    record_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    conversation_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    invoice_number: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    verdict: Mapped[str] = mapped_column(String, nullable=False)
    reason_codes: Mapped[list] = mapped_column(JSON, default=list)
    checks: Mapped[list] = mapped_column(JSON, default=list)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_invoice: Mapped[dict] = mapped_column(JSON, default=dict)
    matched_po_number: Mapped[str | None] = mapped_column(String, nullable=True)
    matched_po_source: Mapped[str | None] = mapped_column(String, nullable=True)
    matched_po: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
