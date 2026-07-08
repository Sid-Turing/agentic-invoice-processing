# Data Model: Read & Reporting Surface

**Feature**: `002-read-reporting` | **Date**: 2026-07-08

**No new persistence.** This feature reads feature 001's existing tables and adds
read-only projection schemas (Pydantic) for the API responses. Source tables:
`processed_invoices` (results) and `po_vendors` / `purchase_orders` /
`purchase_order_line_items` (reference). Nothing is written; no migration.

---

## 1. Source data (read; defined by feature 001)

- **`processed_invoices`**: `record_id`, `conversation_id`, `invoice_number`,
  `verdict`, `reason_codes` (JSON), `checks` (JSON), `explanation`,
  `extracted_invoice` (JSON — holds vendor, amounts, currency, `due_date`, line
  items), `matched_po_number`, `matched_po_source`, `matched_po` (JSON), `created_at`.
- **`purchase_orders`** / **`po_vendors`** / **`purchase_order_line_items`**: as in 001.

Columns available for SQL filtering: `verdict`, `created_at`, `invoice_number`,
`matched_po_number`. Everything else is derived by parsing `extracted_invoice` JSON.

---

## 2. Projection schemas (Pydantic — new, read-only)

### InvoiceListRow
`record_id: str`, `invoice_number: str | None`, `vendor_name: str | None`,
`total_amount: float | None`, `currency: str | None`, `verdict: str`,
`matched_po_number: str | None`, `matched_po_source: str | None`,
`created_at: str` (ISO). Derived per record (vendor/amount/currency from
`extracted_invoice`).

### InvoiceListResponse
`items: list[InvoiceListRow]`, `total: int`, `page: int`, `page_size: int`.

### InvoiceDetailResponse
`record_id: str`, `conversation_id: str | None`, `created_at: str`, plus the stored
decision fields — `verdict`, `reasons: list[ReasonCode]`, `checks: list[Check]`,
`explanation`, `extracted_invoice: ExtractedInvoice`, `matched_po: PurchaseOrder | None`
(reuses 001's `Decision` component schemas).

### AgingBucket
`bucket: Literal["overdue","due_today","due_1_7","due_8_14","due_15_plus","undated"]`,
`count: int`, `amount: float` (sum of `total_amount` in the bucket).

### PriorityItem
`record_id: str`, `invoice_number: str | None`, `vendor_name: str | None`,
`total_amount: float | None`, `currency: str | None`, `due_date: str | None`,
`reasons: list[Literal["high_value","overdue","due_soon"]]`.

### SummaryResponse
`total_processed: int`, `approved_count: int`, `needs_review_count: int`,
`total_approved_amount: float`, `processed_today: int`,
`aging: list[AgingBucket]`, `priority: list[PriorityItem]`.
*All computed at per-run grain over every record (no de-dup).*

### PurchaseOrderListRow
`po_number: str`, `vendor_name: str | None`, `total_amount: float | None`,
`currency: str | None`, `po_date: str | None`, `due_date: str | None`.

### PurchaseOrderListResponse
`items: list[PurchaseOrderListRow]`, `total: int`, `page: int`, `page_size: int`.

### PurchaseOrderDetailResponse
The full `PurchaseOrder` (reused from 001: header, vendor, line items).

### VendorRow / VendorListResponse
`VendorRow`: `name: str | None`, `tax_id: str | None`, `address: str | None`
(assembled from street/city/state/zip), `state: str | None`.
`VendorListResponse`: `items: list[VendorRow]`, `total: int`.

---

## 3. Query/derivation rules (reporting service — pure functions)

- **List**: SQL fetch of `processed_invoices` filtered by `verdict` (if given) and
  `created_at >= window_start`, ordered `created_at DESC`; then parse each row's
  `extracted_invoice` to build `InvoiceListRow`, apply case-insensitive substring
  **search** over invoice_number / vendor_name / matched_po_number, then **paginate**
  (page/page_size) and count `total`.
- **Time windows**: `today` (created today), `7d`, `30d`, `all` → `window_start`.
- **Detail**: fetch one row by `record_id`; 404 if absent; map to `InvoiceDetailResponse`.
- **Summary**: over ALL records — counts by verdict, `total_approved_amount` =
  Σ `total_amount` where `verdict == APPROVED`, `processed_today` = records with
  `created_at` date == today. **Aging**: bucket each record by `extracted_invoice.due_date`
  vs today. **Priority**: records with `total_amount > threshold` AND (overdue OR due ≤ 7d).
- **Date parsing**: `YYYY-MM-DD`; unparseable/missing → `undated`, excluded from priority.
- **PO list/detail & vendors**: read reference tables via 001's repository
  (`get_purchase_order_by_number`) + new list reads; assemble rows.

**Invariant**: no write operations anywhere in the read repository or service (SEC-002).
