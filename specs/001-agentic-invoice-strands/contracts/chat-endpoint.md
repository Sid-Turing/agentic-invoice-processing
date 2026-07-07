# Contract: `POST /chat` (conversational, multimodal)

**Feature**: `001-agentic-invoice-strands` | Satisfies SCH-001, FR-001/002/017/024

The single conversational entry point. Accepts free text and/or uploaded files
(invoice and/or PO) across multi-turn conversations; replies in natural language
and, on processing turns, includes the structured `Decision`.

## Request — `multipart/form-data`

| Part | Type | Required | Notes |
|---|---|---|---|
| `message` | text | no | Free-text user message (may be empty when only files are sent). |
| `conversation_id` | text | no | Omit to start a new conversation; the response returns the id to reuse. |
| `invoice` | file | no* | The invoice document (PDF/PNG/JPEG). |
| `po` | file | no | The purchase-order document (PDF/PNG/JPEG). |

\* A turn need not include a file (e.g. a follow-up "why?"), but a *processing*
turn requires an invoice either in this turn or retained from an earlier turn.
Distinct form fields (`invoice`, `po`) disambiguate the document type; a generic
`files[]` fallback is allowed, in which case the agent asks for clarification if
the type is ambiguous (FR-019, US3 scenario 2).

**Validation** (before the agent runs): each file's declared type ∈ {PDF, PNG,
JPEG}; size ≤ configured max (default 10 MB). Rejections return `415`/`413` with
an RFC-7807-style body — they are input errors, not `NEEDS_REVIEW`.

## Response — `200 application/json` → `ChatResponse`

```json
{
  "conversation_id": "b1c2...",
  "message": "I reconciled invoice INV-1002 against PO-54872. It's APPROVED — all line items and totals matched within tolerance.",
  "decision": {
    "record_id": "9f3a...",
    "verdict": "APPROVED",
    "reasons": [],
    "checks": [
      {"id": "mandatory_fields", "status": "pass", "detail": "All required fields present", "compared": null, "confidence": null, "rationale": null},
      {"id": "financial_totals", "status": "pass", "detail": "subtotal+tax+shipping-discount == total", "compared": {"expected": 60908.87, "actual": 60908.87}},
      {"id": "po_vendor_match", "status": "pass", "detail": "Vendor matches PO", "confidence": 0.98, "rationale": "Exact name + tax id match"},
      {"id": "po_line_items_match", "status": "pass", "detail": "9/9 items matched within tolerance"}
    ],
    "explanation": "Reconciled against PO-54872 (source: database). ...",
    "extracted_invoice": { "...": "ExtractedInvoice" },
    "matched_po": { "po_number": "PO-54872", "source": "database", "...": "PurchaseOrder" }
  }
}
```

- `decision` is `null` on non-processing turns (greetings, follow-up questions,
  clarification requests).
- On a `NEEDS_REVIEW` turn, `reasons` is non-empty and each failing `Check` has
  `status: "fail"`; `matched_po` is `null` when reconciliation was skipped, and a
  `Check` with `id` in {`po_vendor_match`,`po_line_items_match`} appears as
  `skipped` with the reason (`no PO number` / `PO not found`).

## Streaming variant (SHOULD, FR-024 / R9)

When the client requests streaming (e.g. `Accept: text/event-stream`), the same
turn is delivered as SSE: incremental `data:` events carry assistant text chunks
(bridged from `agent.stream_async`), and a terminal event
`event: decision\ndata: <Decision JSON>` carries the structured result. Baseline
v1 tests target the JSON form above; streaming is additive.

## Status codes

| Code | When |
|---|---|
| `200` | Turn processed (APPROVED, NEEDS_REVIEW, or a non-processing reply). |
| `413` / `415` | Attachment too large / unsupported type (input error). |
| `422` | Malformed multipart / bad `conversation_id` format. |
| `503` | Transient failure — model provider or database unavailable (FR-023). Retryable; never a `NEEDS_REVIEW`. |

**Note**: `NEEDS_REVIEW` is a `200` business outcome, **not** an error status.
`503` is reserved for retryable infrastructure failures (provider/DB), keeping the
transient / review / not-found trichotomy distinct.
