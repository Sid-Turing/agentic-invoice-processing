"""Write tools: persist an uploaded PO (upsert) and the final decision."""
from __future__ import annotations

from strands import tool

from app.agent import conversation
from app.db.database import session_scope
from app.db.repository import persist_decision, upsert_purchase_order
from app.schemas.decision import Decision
from app.schemas.purchase_order import PurchaseOrder


@tool
def store_purchase_order(purchase_order: dict) -> dict:
    """Persist an uploaded, extracted purchase order to the database (upsert by PO number).

    Args:
        purchase_order: A PurchaseOrder object from extract_document(document_type='purchase_order').
    """
    po = PurchaseOrder.model_validate(purchase_order)
    with session_scope() as session:
        po_number = upsert_purchase_order(session, po)
    return {"stored": True, "po_number": po_number}


@tool
def store_decision(decision: dict) -> dict:
    """Persist the final invoice decision. Call this exactly once when a processing turn concludes.

    Args:
        decision: A Decision object (verdict, reasons, checks, explanation, extracted_invoice, matched_po).
    """
    model = Decision.model_validate(decision)
    conversation_id = conversation.get_current_conversation_id()
    with session_scope() as session:
        record_id = persist_decision(session, model, conversation_id)
    model.record_id = record_id
    # Stash for the request handler to build the ChatResponse (keyed by conversation
    # so it survives the Strands worker-thread boundary).
    conversation.stash_decision(conversation_id, model.model_dump())
    return {"record_id": record_id}
