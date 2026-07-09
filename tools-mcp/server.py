"""MCP server exposing the invoice-processing tools that only need the database.

Transport: streamable-HTTP at /mcp (works remotely, e.g. GCP Cloud Run).
Tools: calculate, lookup_purchase_order, store_purchase_order.
(store_decision and extract_document stay in the backend — they need request state.)
"""
from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

import calc
import repo
from db import session_scope

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


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
