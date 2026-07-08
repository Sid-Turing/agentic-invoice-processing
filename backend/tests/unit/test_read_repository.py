from datetime import datetime, timezone

from app.db import read_repository as repo


def test_list_all_newest_first(seed_reports, db_session):
    rows = repo.list_processed_invoices(db_session)
    assert len(rows) == 4
    # newest-first: the two 'now' records precede the two 'older' ones
    times = [r.created_at for r in rows]
    assert times == sorted(times, reverse=True)


def test_list_filtered_by_verdict(seed_reports, db_session):
    rows = repo.list_processed_invoices(db_session, verdict="NEEDS_REVIEW")
    assert len(rows) == 1 and rows[0].invoice_number == "INV-R"


def test_list_since_window(seed_reports, db_session):
    since = datetime(2026, 7, 1, tzinfo=timezone.utc)
    rows = repo.list_processed_invoices(db_session, since=since)
    assert {r.invoice_number for r in rows} == {"INV-P", "INV-S"}


def test_get_by_record_id(seed_reports, db_session):
    rid = seed_reports["review"]
    assert repo.get_processed_invoice(db_session, rid).invoice_number == "INV-R"
    assert repo.get_processed_invoice(db_session, "nope") is None


def test_list_reference_data(seed_reports, db_session):
    assert len(repo.list_purchase_orders(db_session)) == 2
    assert len(repo.list_vendors(db_session)) == 2
