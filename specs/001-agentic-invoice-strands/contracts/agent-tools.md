# Contract: Agent Tools (internal interface)

**Feature**: `001-agentic-invoice-strands` | Satisfies FR-004/005/006/010–014/020/021/022

The orchestrator agent is given exactly these five `@tool` functions. Signatures
are the contract Strands turns into tool schemas (name = function name, params
from type hints, description from docstring). Tools return JSON-serializable
dicts. Validation/reconciliation are NOT tools — the orchestrator performs them by
reasoning over these tools' outputs, using `calculate` for arithmetic.

## `extract_document`
```python
@tool
def extract_document(attachment_id: str, document_type: Literal["invoice", "purchase_order"]) -> dict:
    """Extract structured data from an uploaded document image/PDF using the vision model.

    Args:
        attachment_id: Id of the uploaded file (from the message's Attachments list).
        document_type: Whether to extract an 'invoice' or a 'purchase_order'.
    """
```
- Reads bytes from the request-scoped attachment store; renders PDF→PNG (300 dpi);
  runs the Gemini structured-output call → `ExtractedInvoice` or `PurchaseOrder`.
- Returns the extracted model as a dict, or `{"error": "...", "kind": "unreadable|unsupported|empty"}`
  on failure (the agent surfaces this as an extraction-quality issue, not a crash).

## `lookup_purchase_order` (read)
```python
@tool
def lookup_purchase_order(po_number: str) -> dict:
    """Look up a purchase order (with vendor and line items) by PO number in the database.

    Args:
        po_number: The PO number extracted from the invoice.
    """
```
- Returns `{"found": true, "purchase_order": <PurchaseOrder with source="database">}`
  or `{"found": false}`. Read-only.

## `store_purchase_order` (write — upsert)
```python
@tool
def store_purchase_order(purchase_order: dict) -> dict:
    """Persist an uploaded, extracted purchase order to the database (upsert by PO number).

    Args:
        purchase_order: A PurchaseOrder object (from extract_document with document_type='purchase_order').
    """
```
- Validates against `PurchaseOrder`, upserts vendor + PO + line items by `po_number`.
- Returns `{"stored": true, "po_number": "..."}`. Never deletes; only upserts.

## `store_decision` (write — persist result; terminal)
```python
@tool
def store_decision(decision: dict) -> dict:
    """Persist the final invoice decision. Call this exactly once when a processing turn concludes.

    Args:
        decision: A Decision object (verdict, reasons, checks, explanation, extracted_invoice, matched_po).
    """
```
- Validates against `Decision`, inserts one `processed_invoices` row, stashes the
  persisted object in a request-scoped contextvar for the handler, returns
  `{"record_id": "..."}`.

## `calculate` (math)
```python
@tool
def calculate(expression: str) -> float:
    """Evaluate an arithmetic expression deterministically (for totals, tax, tolerance checks).

    Args:
        expression: An arithmetic expression, e.g. '4250.00 * 2 + 5800.00'.
    """
```
- Safe AST-based evaluation (numbers and `+ - * / ( )` only; no names/calls).
  Used by the orchestrator for line-item math, tax, and financial-total checks so
  arithmetic is never left to the LLM.

## Orchestrator system-prompt obligations (behavioral contract)

The system prompt instructs the agent to: extract the invoice; resolve the PO
(prefer an uploaded PO → `extract_document` then `store_purchase_order`; else
`lookup_purchase_order` by the invoice's PO number; else skip reconciliation with
the distinguishing reason); run all invoice-internal checks (mandatory fields,
currency, line-item math via `calculate`, sales tax at the configured flat rate,
financial totals) and, when a PO is resolved, vendor + line-item reconciliation
within the configured tolerances; assemble a `Decision` and call `store_decision`
**once**; reply conversationally; ask a clarifying question instead of fabricating
when input is ambiguous or incomplete; and answer follow-up questions from
conversation context without re-processing.
