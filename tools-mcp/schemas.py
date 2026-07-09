"""Pydantic schemas (self-contained copy of the backend's invoice/PO/decision shapes)."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


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
    tax_rate: float | None = None
    total_price: float = 0.0
    category: str | None = None


class ExtractedInvoice(BaseModel):
    invoice_number: str | None = None
    po_number: str | None = None
    invoice_date: str | None = None
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
    source: Literal["uploaded", "database"] | None = None


class Check(BaseModel):
    id: str
    status: Literal["pass", "fail", "skipped"]
    detail: str = ""
    compared: dict | None = None
    confidence: float | None = None
    rationale: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, v):
        if isinstance(v, dict) and "id" not in v and "name" in v:
            v = {**v, "id": v["name"]}
        return v


class ReasonCode(BaseModel):
    code: str
    detail: str = ""

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, v):
        if isinstance(v, str):
            return {"code": v}
        if isinstance(v, dict) and "code" not in v:
            for k in ("id", "name", "reason", "type"):
                if k in v:
                    return {**v, "code": v[k]}
            return {**v, "code": "unspecified"}
        return v


class Decision(BaseModel):
    verdict: Literal["APPROVED", "NEEDS_REVIEW"]
    reasons: list[ReasonCode] = Field(default_factory=list)
    checks: list[Check] = Field(default_factory=list)
    explanation: str = ""
    extracted_invoice: ExtractedInvoice
    matched_po: PurchaseOrder | None = None
    record_id: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_matched_po(cls, data):
        if not isinstance(data, dict) or "matched_po" not in data:
            return data
        mp = data["matched_po"]
        if mp is None:
            return data
        if not isinstance(mp, dict):
            data["matched_po"] = None
            return data
        po = mp.get("purchase_order") if isinstance(mp.get("purchase_order"), dict) else mp
        if not isinstance(po, dict) or not po.get("po_number"):
            data["matched_po"] = None
            return data
        src = mp.get("source") or po.get("source")
        data["matched_po"] = {**po, "source": src if src in ("uploaded", "database") else "database"}
        return data
