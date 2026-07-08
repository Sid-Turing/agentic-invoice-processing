"""Integration tests for the read/reporting endpoints over a seeded store."""
from fastapi.testclient import TestClient

from app.main import app


def _client():
    return TestClient(app)


# --- GET /invoices -------------------------------------------------------- #

def test_invoices_list_paginated_newest_first(seed_reports):
    with _client() as c:
        r = c.get("/invoices", params={"page": 1, "page_size": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 4 and len(body["items"]) == 2 and body["page"] == 1
    # newest-first: created-today records lead
    assert body["items"][0]["invoice_number"] in {"INV-P", "INV-S"}


def test_invoices_filter_by_verdict(seed_reports):
    with _client() as c:
        r = c.get("/invoices", params={"verdict": "NEEDS_REVIEW"})
    body = r.json()
    assert body["total"] == 1 and body["items"][0]["invoice_number"] == "INV-R"


def test_invoices_search(seed_reports):
    with _client() as c:
        r = c.get("/invoices", params={"q": "acme"})
    body = r.json()
    assert body["total"] == 1 and body["items"][0]["vendor_name"] == "Acme LLC"


def test_invoices_search_no_match(seed_reports):
    with _client() as c:
        r = c.get("/invoices", params={"q": "zzzzz"})
    assert r.json() == {"items": [], "total": 0, "page": 1, "page_size": 25}


def test_invoices_bad_page_size_422(seed_reports):
    with _client() as c:
        r = c.get("/invoices", params={"page_size": 9999})
    assert r.status_code == 422


# --- GET /invoices/{id} --------------------------------------------------- #

def test_invoice_detail(seed_reports):
    rid = seed_reports["priority"]
    with _client() as c:
        r = c.get(f"/invoices/{rid}")
    assert r.status_code == 200
    body = r.json()
    assert body["record_id"] == rid and body["verdict"] == "APPROVED"
    assert body["extracted_invoice"]["vendor"]["name"] == "Acme LLC"
    assert len(body["checks"]) >= 1


def test_invoice_detail_not_found(seed_reports):
    with _client() as c:
        r = c.get("/invoices/does-not-exist")
    assert r.status_code == 404


# --- GET /summary --------------------------------------------------------- #

def test_summary_counts_and_priority(seed_reports):
    with _client() as c:
        r = c.get("/summary")
    body = r.json()
    assert body["total_processed"] == 4
    assert body["approved_count"] == 3 and body["needs_review_count"] == 1
    assert body["total_approved_amount"] == 9400.0
    assert {b["bucket"] for b in body["aging"]} == {
        "overdue", "due_today", "due_1_7", "due_8_14", "due_15_plus", "undated"
    }
    # the high-value overdue invoice is flagged priority
    assert any(p["invoice_number"] == "INV-P" for p in body["priority"])


def test_summary_empty_system():
    with _client() as c:  # no seed_reports -> reference seeded by startup, no processed invoices
        r = c.get("/summary")
    body = r.json()
    assert body["total_processed"] == 0 and body["priority"] == []
    assert sum(b["count"] for b in body["aging"]) == 0


# --- POs & vendors -------------------------------------------------------- #

def test_purchase_orders_list_and_detail(seed_reports):
    with _client() as c:
        lst = c.get("/purchase-orders").json()
        assert lst["total"] == 2
        detail = c.get("/purchase-orders/PO-54872")
    assert detail.status_code == 200
    assert len(detail.json()["line_items"]) == 9


def test_purchase_order_not_found(seed_reports):
    with _client() as c:
        r = c.get("/purchase-orders/NOPE")
    assert r.status_code == 404


def test_vendors_list_and_search(seed_reports):
    with _client() as c:
        allv = c.get("/vendors").json()
        assert allv["total"] == 2
        one = c.get("/vendors", params={"q": "medequip"}).json()
    assert one["total"] == 1


# --- read-only invariant (SC-008) ---------------------------------------- #

def test_read_only_no_writes(seed_reports, db_session):
    from app.db import models
    from sqlalchemy import func, select

    def counts(s):
        return (
            s.scalar(select(func.count()).select_from(models.ProcessedInvoice)),
            s.scalar(select(func.count()).select_from(models.PurchaseOrder)),
            s.scalar(select(func.count()).select_from(models.PoVendor)),
        )

    before = counts(db_session)
    rid = seed_reports["soon"]
    with _client() as c:
        c.get("/invoices")
        c.get(f"/invoices/{rid}")
        c.get("/summary")
        c.get("/purchase-orders")
        c.get("/purchase-orders/PO-54872")
        c.get("/vendors")
    db_session.expire_all()
    assert counts(db_session) == before
