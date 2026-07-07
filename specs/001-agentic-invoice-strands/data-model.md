# Data Model: Agentic Invoice Processing (Strands)

**Feature**: `001-agentic-invoice-strands` | **Date**: 2026-07-07

Two layers: **domain schemas** (Pydantic — the wire/tool contracts and in-memory
shapes) and **persistence** (SQLAlchemy ORM — SQLite tables). PO reference tables
are seeded from the project CSVs and upserted on PO upload; `processed_invoices`
is the new results store.

---

## 1. Domain schemas (Pydantic v2)

### VendorInfo
`name: str | None`, `tax_id: str | None`, `street_address: str | None`,
`city: str | None`, `state: str | None`, `zip_code: str | None`,
`bank_name: str | None`, `account_number: str | None`,
`routing_number: str | None`, `swift_code: str | None`,
`tax_classification: str | None`.

### CustomerInfo
`name`, `tax_id`, `street_address`, `city`, `state`, `zip_code` — all `str | None`.

### InvoiceLineItem
`description: str`, `quantity: float`, `unit_price: float`,
`tax_rate: float | None` (decimal, e.g. 0.09125), `total_price: float`,
`category: str | None`.

### ExtractedInvoice
`invoice_number: str | None`, `po_number: str | None`,
`invoice_date: str | None` (YYYY-MM-DD), `due_date: str | None`,
`currency: str | None`, `subtotal: float | None`, `tax_amount: float | None`,
`discount_amount: float | None`, `shipping_charges: float | None`,
`total_amount: float | None`, `payment_terms: str | None`,
`vendor: VendorInfo`, `customer: CustomerInfo`,
`line_items: list[InvoiceLineItem]`.
*Validation*: numeric fields default `null`; the agent flags missing mandatory
fields (`invoice_number`, `invoice_date`, `subtotal`, `total_amount`, `currency`,
vendor name+address) rather than the schema rejecting them — extraction must not
hard-fail on incomplete invoices.

### POLineItem
`description: str`, `quantity: float`, `unit_price: float`,
`item_tax_rate: float | None`, `total_price: float`, `category: str | None`.

### PurchaseOrder
`po_number: str`, `po_date: str | None`, `due_date: str | None`,
`subtotal: float | None`, `total_tax_amount: float | None`,
`total_amount: float | None`, `currency: str | None`,
`payment_terms: str | None`, `destination_state: str | None`,
`status: str | None`, `vendor: VendorInfo`, `line_items: list[POLineItem]`,
`source: Literal["uploaded", "database"] | None` (set when used in a decision).

### Check
`id: str` — one of `mandatory_fields | currency | line_item_math | sales_tax |
financial_totals | po_vendor_match | po_line_items_match | extraction_quality`.
`status: Literal["pass", "fail", "skipped"]`, `detail: str`,
`compared: dict | None` (values compared, e.g. `{"expected": 60908.87, "actual": 60900.0}`),
`confidence: float | None` (semantic checks), `rationale: str | None`.

### ReasonCode
`code: str` (same taxonomy as `Check.id`), `detail: str`.

### Decision
`verdict: Literal["APPROVED", "NEEDS_REVIEW"]`,
`reasons: list[ReasonCode]` (empty iff APPROVED),
`checks: list[Check]`, `explanation: str`,
`extracted_invoice: ExtractedInvoice`,
`matched_po: PurchaseOrder | None`,
`record_id: str | None` (assigned by `store_decision`).
*Rule*: `verdict == APPROVED` iff every non-`skipped` check is `pass`; any `fail`
check contributes a `ReasonCode` and forces `NEEDS_REVIEW`.

### ChatResponse
`conversation_id: str`, `message: str`, `decision: Decision | None`.

### HealthResponse
`status: Literal["ok", "degraded"]`,
`providers: dict[str, bool]` (`openai`, `gemini`), `database: bool`.

---

## 2. Persistence (SQLAlchemy ORM → SQLite)

### `po_vendors` (reference; seeded, upsertable)
`id: str PK` (uuid), `name`, `tax_id`, `state`, `street_address`, `city`,
`zip_code`, `bank_name`, `account_number`, `routing_number`, `swift_code`,
`tax_classification`, `tax_exempt: bool`, `backup_withholding: bool`,
`tax_exemption_number`, `ifsc_code`, `created_at`, `updated_at`.

### `purchase_orders` (reference; seeded, upsertable)
`id: str PK` (uuid), `po_number: str UNIQUE NOT NULL` (indexed),
`vendor_id → po_vendors.id`, `po_date`, `due_date`, `subtotal: Numeric`,
`total_tax_amount: Numeric`, `total_amount: Numeric`, `currency`,
`payment_terms`, `destination_state`, `status`, `created_at`, `updated_at`.

### `purchase_order_line_items` (reference; seeded, upsertable)
`id: int PK` (autoincrement), `po_id → purchase_orders.id` (indexed),
`description`, `quantity: Numeric`, `unit_price: Numeric`,
`item_tax_rate: Numeric`, `total_price: Numeric`, `category`,
`created_at`, `updated_at`.

### `processed_invoices` (results; new — write target for `store_decision`)
`record_id: str PK` (uuid), `conversation_id: str NULL` (indexed),
`invoice_number: str NULL` (indexed), `verdict: str`,
`reason_codes: JSON`, `checks: JSON`, `explanation: Text`,
`extracted_invoice: JSON`, `matched_po_number: str NULL`,
`matched_po_source: str NULL` (`uploaded | database`), `matched_po: JSON NULL`,
`created_at`.

**Relationships**: `purchase_orders.vendor_id → po_vendors.id` (many-to-one);
`purchase_order_line_items.po_id → purchase_orders.id` (many-to-one). The invoice
↔ PO link stays a **soft link** on `po_number` (as in the original) — no FK from
`processed_invoices` to `purchase_orders`, so a result can reference an uploaded
PO or one on file uniformly.

---

## 3. Repository operations (pure data-access, no transport)

- **`seed_reference_data(session, data_dir)`** → loads the three CSVs into
  `po_vendors` / `purchase_orders` / `purchase_order_line_items`. **Skips if any
  rows already exist** (mirrors the original's `seed_purchase_order_data`). Idempotent.
- **`get_purchase_order_by_number(session, po_number)`** → `PurchaseOrder | None`
  (joins vendor + line items into the aggregate). Read-only. Backs `lookup_purchase_order`.
- **`upsert_purchase_order(session, po: PurchaseOrder)`** → `po_number`. Resolves/creates
  the vendor (match by `name` + `tax_id`, else create), upserts the PO by `po_number`,
  and **replaces** its line items. Backs `store_purchase_order`. No deletes of other rows.
- **`persist_decision(session, decision: Decision, conversation_id)`** → `record_id`.
  Inserts one `processed_invoices` row. Backs `store_decision`.

**Write invariants (SEC-004 / FR-022)**: the only writes are `upsert_purchase_order`
and `persist_decision`. No `DELETE` anywhere. Stored POs change only via upsert of a
freshly uploaded PO of the same number.

---

## 4. Runtime (non-persisted) state

- **Conversation registry** (in-memory): `conversation_id → (Agent, asyncio.Lock)`.
  Holds the Strands `Agent` and its message history for the life of the process.
- **Attachment store** (request-scoped `contextvar`):
  `{attachment_id: (bytes, mime, hint)}` — raw upload bytes, discarded when the
  request ends (SEC-003). Never written to the DB.
