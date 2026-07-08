"""Seed the read-only PO reference tables from the project CSVs.

Idempotent: skips entirely if any PO/vendor rows already exist (mirrors the
original app's seed_purchase_order_data). Preserves the CSV ids so the
vendor_id / po_id foreign keys line up.
"""
from __future__ import annotations

import csv
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import models


def _s(value: str | None) -> str | None:
    value = (value or "").strip()
    return value or None


def _num(value: str | None) -> float | None:
    value = _s(value)
    return float(value) if value is not None else None


def _bool(value: str | None) -> bool:
    return (value or "").strip().lower() in {"t", "true", "1", "yes"}


def seed_reference_data(session: Session, data_dir: Path) -> dict[str, int]:
    """Load vendors, POs, and line items. Returns counts; {} if skipped."""
    existing = session.scalar(select(func.count()).select_from(models.PurchaseOrder))
    existing_v = session.scalar(select(func.count()).select_from(models.PoVendor))
    if (existing or 0) > 0 or (existing_v or 0) > 0:
        return {}

    data_dir = Path(data_dir)
    counts = {"vendors": 0, "purchase_orders": 0, "line_items": 0}

    with open(data_dir / "po_vendors_data.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            session.add(
                models.PoVendor(
                    id=r["id"],
                    name=_s(r.get("name")),
                    tax_id=_s(r.get("tax_id")),
                    state=_s(r.get("state")),
                    street_address=_s(r.get("street_address")),
                    city=_s(r.get("city")),
                    zip_code=_s(r.get("zip_code")),
                    bank_name=_s(r.get("bank_name")),
                    account_number=_s(r.get("account_number")),
                    routing_number=_s(r.get("routing_number")),
                    swift_code=_s(r.get("swift_code")),
                    tax_classification=_s(r.get("tax_classification")),
                    tax_exempt=_bool(r.get("tax_exempt")),
                    backup_withholding=_bool(r.get("backup_withholding")),
                    tax_exemption_number=_s(r.get("tax_exemption_number")),
                    ifsc_code=_s(r.get("ifsc_code")),
                )
            )
            counts["vendors"] += 1

    with open(data_dir / "purchase_orders_data.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            session.add(
                models.PurchaseOrder(
                    id=r["id"],
                    po_number=r["po_number"],
                    vendor_id=_s(r.get("vendor_id")),
                    po_date=_s(r.get("po_date")),
                    due_date=_s(r.get("due_date")),
                    subtotal=_num(r.get("subtotal")),
                    total_tax_amount=_num(r.get("total_tax_amount")),
                    total_amount=_num(r.get("total_amount")),
                    currency=_s(r.get("currency")),
                    payment_terms=_s(r.get("payment_terms")),
                    destination_state=_s(r.get("destination_state")),
                    status=_s(r.get("status")),
                )
            )
            counts["purchase_orders"] += 1

    session.flush()

    with open(data_dir / "purchase_order_line_items_data.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            session.add(
                models.PoLineItem(
                    po_id=r["po_id"],
                    description=_s(r.get("description")),
                    quantity=_num(r.get("quantity")),
                    unit_price=_num(r.get("unit_price")),
                    item_tax_rate=_num(r.get("item_tax_rate")),
                    total_price=_num(r.get("total_price")),
                    category=_s(r.get("category")),
                )
            )
            counts["line_items"] += 1

    session.flush()
    return counts
