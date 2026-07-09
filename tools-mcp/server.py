"""MCP server exposing the invoice-processing tools that only need the database.

Transport: streamable-HTTP at /mcp (works remotely, e.g. GCP Cloud Run).
Tools: calculate, lookup_purchase_order, store_purchase_order.
(store_decision and extract_document stay in the backend — they need request state.)
"""
from __future__ import annotations

import os
from typing import Literal

from mcp.server.fastmcp import FastMCP

import calc
import extraction
import repo
from db import session_scope
from schemas import Decision

mcp = FastMCP(
    "invoice-tools",
    host="0.0.0.0",
    port=int(os.getenv("PORT", "8080")),   # Cloud Run injects $PORT
    streamable_http_path="/mcp",
    stateless_http=True,                    # each call independent — ideal for serverless
)


@mcp.tool()
def calculate(expression: str) -> float:
    """Evaluate an arithmetic expression deterministically (totals, tax, tolerance checks).

    Args:
        expression: e.g. '4250.00 * 2 + 5800.00'.
    """
    return calc.evaluate(expression)


@mcp.tool()
def lookup_purchase_order(po_number: str) -> dict:
    """Look up a purchase order (with vendor and line items) by PO number.

    Args:
        po_number: The PO number extracted from the invoice.
    """
    with session_scope() as s:
        po = repo.get_purchase_order_by_number(s, po_number)
    return {"found": True, "purchase_order": po} if po else {"found": False}


@mcp.tool()
def store_purchase_order(purchase_order: dict) -> dict:
    """Persist an uploaded, extracted purchase order (upsert by PO number).

    Args:
        purchase_order: A PurchaseOrder object (po_number, vendor, line_items, totals, ...).
    """
    with session_scope() as s:
        po_number = repo.upsert_purchase_order(s, purchase_order)
    return {"stored": True, "po_number": po_number}


@mcp.tool()
def extract_document(attachment_id: str, document_type: Literal["invoice", "purchase_order"]) -> dict:
    """Extract structured data from an uploaded document image/PDF using the vision model.

    Args:
        attachment_id: Id of the uploaded file (from the message's Attachments list).
        document_type: Whether to extract an 'invoice' or a 'purchase_order'.
    """
    with session_scope() as s:
        data, mime = repo.get_upload(s, attachment_id)
    if data is None:
        return {"error": f"no attachment with id '{attachment_id}'", "kind": "missing"}
    try:
        result = extraction.extract(data, mime, document_type)
    except ValueError as exc:
        return {"error": str(exc), "kind": "unreadable"}
    except Exception as exc:  # provider error
        return {"error": str(exc), "kind": "provider"}
    return result.model_dump()


@mcp.tool()
def store_decision(decision: dict, conversation_id: str | None = None) -> dict:
    """Persist the final invoice decision. Call exactly once at the end of a processing turn.

    Args:
        decision: A Decision object (verdict, reasons, checks, explanation, extracted_invoice, matched_po).
        conversation_id: The conversation id from the system prompt.
    """
    model = Decision.model_validate(decision)
    with session_scope() as s:
        record_id = repo.persist_decision(s, model.model_dump(), conversation_id)
    return {"record_id": record_id}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
