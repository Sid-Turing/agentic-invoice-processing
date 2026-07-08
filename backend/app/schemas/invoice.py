"""Domain schemas for an extracted invoice."""
from __future__ import annotations

from pydantic import BaseModel, Field


class VendorInfo(BaseModel):
    name: str | None = None
    tax_id: str | None = None
    street_address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    bank_name: str | None = None
    account_number: str | None = None
    routing_number: str | None = None
    swift_code: str | None = None
    tax_classification: str | None = None


class CustomerInfo(BaseModel):
    name: str | None = None
    tax_id: str | None = None
    street_address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None


class InvoiceLineItem(BaseModel):
    description: str
    quantity: float = 0.0
    unit_price: float = 0.0
    tax_rate: float | None = None  # decimal, e.g. 0.09125
    total_price: float = 0.0
    category: str | None = None


class ExtractedInvoice(BaseModel):
    invoice_number: str | None = None
    po_number: str | None = None
    invoice_date: str | None = None  # YYYY-MM-DD
    due_date: str | None = None
    currency: str | None = None
    subtotal: float | None = None
    tax_amount: float | None = None
    discount_amount: float | None = None
    shipping_charges: float | None = None
    total_amount: float | None = None
    payment_terms: str | None = None
    vendor: VendorInfo = Field(default_factory=VendorInfo)
    customer: CustomerInfo = Field(default_factory=CustomerInfo)
    line_items: list[InvoiceLineItem] = Field(default_factory=list)
