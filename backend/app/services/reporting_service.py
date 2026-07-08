"""Pure reporting logic: build list rows, search, paginate, aging, priority, summary.

Operates on 'record-like' objects exposing: record_id, invoice_number, verdict,
matched_po_number, matched_po_source, created_at (datetime), extracted_invoice (dict).
No I/O — the read repository supplies the records.
"""
from __future__ import annotations

from datetime import date, datetime

from app.schemas.reports import (
    AgingBucket,
    InvoiceListRow,
    PriorityItem,
    SummaryResponse,
)

_AGING_ORDER = ["overdue", "due_today", "due_1_7", "due_8_14", "due_15_plus", "undated"]


def _ei(record) -> dict:
    return record.extracted_invoice or {}


def vendor_name(record) -> str | None:
    v = _ei(record).get("vendor") or {}
    return v.get("name")


def total_amount(record) -> float | None:
    amt = _ei(record).get("total_amount")
    return float(amt) if isinstance(amt, (int, float)) else None


def currency(record) -> str | None:
    return _ei(record).get("currency")


def due_date(record) -> str | None:
    return _ei(record).get("due_date")


def _created_iso(record) -> str:
    ca = record.created_at
    return ca.isoformat() if isinstance(ca, datetime) else str(ca)


def to_list_row(record) -> InvoiceListRow:
    return InvoiceListRow(
        record_id=record.record_id,
        invoice_number=record.invoice_number,
        vendor_name=vendor_name(record),
        total_amount=total_amount(record),
        currency=currency(record),
        verdict=record.verdict,
        matched_po_number=record.matched_po_number,
        matched_po_source=record.matched_po_source,
        created_at=_created_iso(record),
    )


def search_matches(record, q: str) -> bool:
    q = q.strip().lower()
    if not q:
        return True
    haystay = [record.invoice_number, vendor_name(record), record.matched_po_number]
    return any(h and q in str(h).lower() for h in haystay)


def paginate(items: list, page: int, page_size: int) -> tuple[list, int]:
    total = len(items)
    start = (page - 1) * page_size
    return items[start:start + page_size], total


def _parse_due(due: str | None) -> date | None:
    if not due:
        return None
    try:
        return datetime.strptime(due.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


def aging_bucket(due: str | None, today: date) -> str:
    d = _parse_due(due)
    if d is None:
        return "undated"
    delta = (d - today).days
    if delta < 0:
        return "overdue"
    if delta == 0:
        return "due_today"
    if delta <= 7:
        return "due_1_7"
    if delta <= 14:
        return "due_8_14"
    return "due_15_plus"


def build_aging(records, today: date) -> list[AgingBucket]:
    buckets = {name: {"count": 0, "amount": 0.0} for name in _AGING_ORDER}
    for r in records:
        b = aging_bucket(due_date(r), today)
        buckets[b]["count"] += 1
        buckets[b]["amount"] += total_amount(r) or 0.0
    return [AgingBucket(bucket=name, count=buckets[name]["count"], amount=round(buckets[name]["amount"], 2))
            for name in _AGING_ORDER]


def priority_reasons(record, today: date, threshold: float) -> list[str]:
    amt = total_amount(record)
    if amt is None or amt <= threshold:
        return []
    d = _parse_due(due_date(record))
    if d is None:
        return []
    delta = (d - today).days
    reasons = ["high_value"]
    if delta < 0:
        reasons.append("overdue")
    elif delta <= 7:
        reasons.append("due_soon")
    else:
        return []  # high value but not overdue/due-soon -> not priority
    return reasons


def derive_priority(records, today: date, threshold: float) -> list[PriorityItem]:
    out: list[PriorityItem] = []
    for r in records:
        reasons = priority_reasons(r, today, threshold)
        if reasons:
            out.append(PriorityItem(
                record_id=r.record_id,
                invoice_number=r.invoice_number,
                vendor_name=vendor_name(r),
                total_amount=total_amount(r),
                currency=currency(r),
                due_date=due_date(r),
                reasons=reasons,
            ))
    return out


def build_summary(records, today: date, threshold: float) -> SummaryResponse:
    records = list(records)
    approved = [r for r in records if r.verdict == "APPROVED"]
    needs_review = [r for r in records if r.verdict == "NEEDS_REVIEW"]
    total_approved_amount = round(sum(total_amount(r) or 0.0 for r in approved), 2)
    processed_today = sum(
        1 for r in records if isinstance(r.created_at, datetime) and r.created_at.date() == today
    )
    return SummaryResponse(
        total_processed=len(records),
        approved_count=len(approved),
        needs_review_count=len(needs_review),
        total_approved_amount=total_approved_amount,
        processed_today=processed_today,
        aging=build_aging(records, today),
        priority=derive_priority(records, today, threshold),
    )
