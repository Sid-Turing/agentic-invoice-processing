from datetime import date, datetime, timezone
from types import SimpleNamespace

from app.services import reporting_service as svc

TODAY = date(2026, 7, 8)


def _rec(record_id, verdict, vendor, total, due, created, invoice_number=None, po=None):
    return SimpleNamespace(
        record_id=record_id,
        invoice_number=invoice_number or record_id,
        verdict=verdict,
        matched_po_number=po,
        matched_po_source="database" if po else None,
        created_at=created,
        extracted_invoice={
            "due_date": due,
            "currency": "USD",
            "total_amount": total,
            "vendor": {"name": vendor},
        },
    )


def _dataset():
    now = datetime(2026, 7, 8, 12, tzinfo=timezone.utc)
    old = datetime(2026, 6, 1, 12, tzinfo=timezone.utc)
    return [
        _rec("P", "APPROVED", "Acme LLC", 8200.0, "2026-07-01", now, po="PO-54872"),   # overdue, priority
        _rec("S", "APPROVED", "Beta Inc", 200.0, "2026-07-11", now),                    # due_1_7
        _rec("R", "NEEDS_REVIEW", "Gamma Co", 500.0, None, old),                        # undated
        _rec("F", "APPROVED", "Delta LLC", 1000.0, "2026-09-01", old),                  # due_15_plus
    ]


def test_to_list_row_derives_fields():
    row = svc.to_list_row(_dataset()[0])
    assert row.vendor_name == "Acme LLC" and row.total_amount == 8200.0 and row.currency == "USD"


def test_search_matches_invoice_vendor_po():
    r = _dataset()[0]
    assert svc.search_matches(r, "acme")
    assert svc.search_matches(r, "po-548")
    assert svc.search_matches(r, "P")  # invoice number
    assert not svc.search_matches(r, "zzz")


def test_paginate():
    items = list(range(10))
    page, total = svc.paginate(items, page=2, page_size=3)
    assert total == 10 and page == [3, 4, 5]


def test_aging_buckets():
    assert svc.aging_bucket("2026-07-01", TODAY) == "overdue"
    assert svc.aging_bucket("2026-07-08", TODAY) == "due_today"
    assert svc.aging_bucket("2026-07-11", TODAY) == "due_1_7"
    assert svc.aging_bucket("2026-07-20", TODAY) == "due_8_14"
    assert svc.aging_bucket("2026-09-01", TODAY) == "due_15_plus"
    assert svc.aging_bucket(None, TODAY) == "undated"
    assert svc.aging_bucket("garbage", TODAY) == "undated"


def test_priority_high_value_and_overdue_only():
    recs = _dataset()
    prio = svc.derive_priority(recs, TODAY, threshold=3000.0)
    assert [p.record_id for p in prio] == ["P"]
    assert set(prio[0].reasons) == {"high_value", "overdue"}


def test_build_summary_per_run_grain():
    s = svc.build_summary(_dataset(), TODAY, threshold=3000.0)
    assert s.total_processed == 4
    assert s.approved_count == 3 and s.needs_review_count == 1
    assert s.total_approved_amount == 9400.0
    assert s.processed_today == 2                       # P and S created today
    buckets = {b.bucket: b.count for b in s.aging}
    assert buckets == {"overdue": 1, "due_today": 0, "due_1_7": 1, "due_8_14": 0, "due_15_plus": 1, "undated": 1}
    assert [p.record_id for p in s.priority] == ["P"]
