"""Decision schemas: the verdict, reason codes, and per-check trace."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.invoice import ExtractedInvoice
from app.schemas.purchase_order import PurchaseOrder

# Fixed reason-code / check taxonomy (FR-014/016).
CheckId = Literal[
    "mandatory_fields",
    "currency",
    "line_item_math",
    "sales_tax",
    "financial_totals",
    "po_vendor_match",
    "po_line_items_match",
    "extraction_quality",
]

Verdict = Literal["APPROVED", "NEEDS_REVIEW"]


class Check(BaseModel):
    id: CheckId
    status: Literal["pass", "fail", "skipped"]
    detail: str = ""
    compared: dict | None = None
    confidence: float | None = None
    rationale: str | None = None


class ReasonCode(BaseModel):
    code: CheckId
    detail: str = ""


class Decision(BaseModel):
    verdict: Verdict
    reasons: list[ReasonCode] = Field(default_factory=list)
    checks: list[Check] = Field(default_factory=list)
    explanation: str = ""
    extracted_invoice: ExtractedInvoice
    matched_po: PurchaseOrder | None = None
    record_id: str | None = None
