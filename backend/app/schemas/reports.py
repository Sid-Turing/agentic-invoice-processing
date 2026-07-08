"""Read-only projection schemas for the reporting surface (feature 002)."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.decision import Check, ReasonCode
from app.schemas.invoice import ExtractedInvoice
from app.schemas.purchase_order import PurchaseOrder

AgingBucketName = Literal["overdue", "due_today", "due_1_7", "due_8_14", "due_15_plus", "undated"]
PriorityReason = Literal["high_value", "overdue", "due_soon"]


class InvoiceListRow(BaseModel):
    record_id: str
    invoice_number: str | None = None
    vendor_name: str | None = None
    total_amount: float | None = None
    currency: str | None = None
    verdict: str
    matched_po_number: str | None = None
    matched_po_source: str | None = None
    created_at: str


class InvoiceListResponse(BaseModel):
    items: list[InvoiceListRow] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 25


class InvoiceDetailResponse(BaseModel):
    record_id: str
    conversation_id: str | None = None
    created_at: str
    verdict: str
    reasons: list[ReasonCode] = Field(default_factory=list)
    checks: list[Check] = Field(default_factory=list)
    explanation: str = ""
    extracted_invoice: ExtractedInvoice
    matched_po: PurchaseOrder | None = None


class AgingBucket(BaseModel):
    bucket: AgingBucketName
    count: int = 0
    amount: float = 0.0


class PriorityItem(BaseModel):
    record_id: str
    invoice_number: str | None = None
    vendor_name: str | None = None
    total_amount: float | None = None
    currency: str | None = None
    due_date: str | None = None
    reasons: list[PriorityReason] = Field(default_factory=list)


class SummaryResponse(BaseModel):
    total_processed: int = 0
    approved_count: int = 0
    needs_review_count: int = 0
    total_approved_amount: float = 0.0
    processed_today: int = 0
    aging: list[AgingBucket] = Field(default_factory=list)
    priority: list[PriorityItem] = Field(default_factory=list)


class PurchaseOrderListRow(BaseModel):
    po_number: str
    vendor_name: str | None = None
    total_amount: float | None = None
    currency: str | None = None
    po_date: str | None = None
    due_date: str | None = None


class PurchaseOrderListResponse(BaseModel):
    items: list[PurchaseOrderListRow] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 25


# PurchaseOrderDetailResponse is just the reused PurchaseOrder schema.


class VendorRow(BaseModel):
    name: str | None = None
    tax_id: str | None = None
    address: str | None = None
    state: str | None = None


class VendorListResponse(BaseModel):
    items: list[VendorRow] = Field(default_factory=list)
    total: int = 0
