# Contract: Read/Reporting Endpoints

**Feature**: `002-read-reporting` | Satisfies SCH-001..005 | All `GET`, read-only

Base URL: the existing backend (default `http://localhost:8010`). CORS already open
for the frontend. Errors use the FastAPI `{"detail": ...}` shape.

## `GET /invoices` — processed-invoice history (per-run)
Query params:
| Param | Type | Default | Notes |
|---|---|---|---|
| `page` | int ≥ 1 | 1 | |
| `page_size` | int 1–100 | 25 | |
| `verdict` | `APPROVED`\|`NEEDS_REVIEW` | — | optional filter |
| `window` | `today`\|`7d`\|`30d`\|`all` | `all` | on `created_at` |
| `q` | string | — | case-insensitive substring over invoice#, vendor, PO# |

`200` → `InvoiceListResponse`:
```json
{
  "items": [
    {"record_id":"…","invoice_number":"INV-…","vendor_name":"…","total_amount":343.76,
     "currency":"USD","verdict":"APPROVED","matched_po_number":null,
     "matched_po_source":null,"created_at":"2026-07-08T14:13:08Z"}
  ],
  "total": 26, "page": 1, "page_size": 25
}
```
Empty/no-match → `items: []`, `total: 0` (not an error).

## `GET /invoices/{record_id}` — decision detail
`200` → `InvoiceDetailResponse` (record metadata + the stored `Decision`):
```json
{
  "record_id":"…","conversation_id":"…","created_at":"…",
  "verdict":"APPROVED","reasons":[],"checks":[{"id":"mandatory_fields","status":"pass","detail":"…"}],
  "explanation":"…","extracted_invoice":{ "…":"ExtractedInvoice" },
  "matched_po": null
}
```
Unknown id → `404 {"detail":"record not found"}`.

## `GET /summary` — dashboard
`200` → `SummaryResponse`:
```json
{
  "total_processed": 26, "approved_count": 18, "needs_review_count": 8,
  "total_approved_amount": 12345.67, "processed_today": 4,
  "aging": [
    {"bucket":"overdue","count":3,"amount":900.0},
    {"bucket":"due_today","count":1,"amount":100.0},
    {"bucket":"due_1_7","count":2,"amount":540.0},
    {"bucket":"due_8_14","count":0,"amount":0.0},
    {"bucket":"due_15_plus","count":5,"amount":3000.0},
    {"bucket":"undated","count":15,"amount":7800.0}
  ],
  "priority": [
    {"record_id":"…","invoice_number":"INV-…","vendor_name":"…","total_amount":8200.0,
     "currency":"USD","due_date":"2025-05-01","reasons":["high_value","overdue"]}
  ]
}
```
Empty system → zeroed counts, all buckets at 0, `priority: []`.

## `GET /purchase-orders` — PO list
Query params: `page`, `page_size`, `q` (substring on PO number).
`200` → `PurchaseOrderListResponse` (`items` of PO rows + `total`/`page`/`page_size`).

## `GET /purchase-orders/{po_number}` — PO detail
`200` → `PurchaseOrderDetailResponse` (full PO: header, vendor, line items).
Unknown number → `404 {"detail":"purchase order not found"}`.

## `GET /vendors` — vendor list
Query params: `q` (substring on name).
`200` → `VendorListResponse` (`items` of vendor rows + `total`).

## Status codes
| Code | When |
|---|---|
| `200` | success (including empty/no-match results) |
| `404` | unknown record id / PO number |
| `422` | invalid query params (e.g. page_size out of range) |
| `503` | database unreachable (retryable) — distinct from an empty result |

No `POST`/`PUT`/`PATCH`/`DELETE` — the surface is strictly read-only (SEC-002).
