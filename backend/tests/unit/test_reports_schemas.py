from app.schemas.reports import (
    AgingBucket,
    InvoiceListResponse,
    InvoiceListRow,
    PriorityItem,
    SummaryResponse,
)


def test_list_row_and_response_defaults():
    row = InvoiceListRow(record_id="r1", verdict="APPROVED", created_at="2026-07-08T00:00:00Z")
    resp = InvoiceListResponse(items=[row], total=1, page=1, page_size=25)
    assert resp.items[0].vendor_name is None
    assert resp.total == 1


def test_aging_bucket_enum():
    assert AgingBucket(bucket="overdue", count=1, amount=10.0).bucket == "overdue"


def test_priority_item_reasons():
    p = PriorityItem(record_id="r", reasons=["high_value", "overdue"])
    assert p.reasons == ["high_value", "overdue"]


def test_summary_defaults():
    s = SummaryResponse()
    assert s.total_processed == 0 and s.aging == [] and s.priority == []
