"""Decision schemas: the verdict, reason codes, and per-check trace."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.invoice import ExtractedInvoice
from app.schemas.purchase_order import PurchaseOrder

# Canonical reason-code / check taxonomy (FR-014/016). Documented as the intended
# set and used in the prompt; the schema accepts any string so a slightly-off id
# from the model does not block the whole decision (it is surfaced as-is).
CANONICAL_CHECK_IDS = (
    "mandatory_fields",
    "currency",
    "line_item_math",
    "sales_tax",
    "financial_totals",
    "po_vendor_match",
    "po_line_items_match",
    "extraction_quality",
)

Verdict = Literal["APPROVED", "NEEDS_REVIEW"]


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
        # Accept a bare string, or a dict keyed by code/id/name/reason/type.
        if isinstance(v, str):
            return {"code": v}
        if isinstance(v, dict) and "code" not in v:
            for k in ("id", "name", "reason", "type"):
                if k in v:
                    return {**v, "code": v[k]}
            return {**v, "code": "unspecified"}
        return v


class Decision(BaseModel):
    verdict: Verdict
    reasons: list[ReasonCode] = Field(default_factory=list)
    checks: list[Check] = Field(default_factory=list)
    explanation: str = ""
    extracted_invoice: ExtractedInvoice
    matched_po: PurchaseOrder | None = None
    record_id: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_matched_po(cls, data):
        """Tolerate the model's no-PO variants: a null, a placeholder object, or a
        PO nested under 'purchase_order'. Anything without a real po_number → None."""
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
        po = {**po, "source": src if src in ("uploaded", "database") else "database"}
        data["matched_po"] = po
        return data
