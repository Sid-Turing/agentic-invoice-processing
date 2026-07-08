"""Read tool: look up a purchase order by number."""
from __future__ import annotations

from strands import tool

from app.db.database import session_scope
from app.db.repository import get_purchase_order_by_number


@tool
def lookup_purchase_order(po_number: str) -> dict:
    """Look up a purchase order (with vendor and line items) by PO number in the database.

    Args:
        po_number: The PO number extracted from the invoice.
    """
    with session_scope() as session:
        po = get_purchase_order_by_number(session, po_number)
    if po is None:
        return {"found": False}
    return {"found": True, "purchase_order": po.model_dump()}
