"""Domain schemas for a purchase order (reference data / uploaded PO)."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.invoice import VendorInfo


class POLineItem(BaseModel):
    description: str
    quantity: float = 0.0
    unit_price: float = 0.0
    item_tax_rate: float | None = None
    total_price: float = 0.0
    category: str | None = None


class PurchaseOrder(BaseModel):
    po_number: str
    po_date: str | None = None
    due_date: str | None = None
    subtotal: float | None = None
    total_tax_amount: float | None = None
    total_amount: float | None = None
    currency: str | None = None
    payment_terms: str | None = None
    destination_state: str | None = None
    status: str | None = None
    vendor: VendorInfo = Field(default_factory=VendorInfo)
    line_items: list[POLineItem] = Field(default_factory=list)
    # Set only when the PO is used in a decision.
    source: Literal["uploaded", "database"] | None = None
