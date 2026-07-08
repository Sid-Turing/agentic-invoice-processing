"""Test doubles: real PNG upload bytes, an extraction stub, and a deterministic
fake orchestrator agent that drives the real tools (no live providers)."""
from __future__ import annotations

import io

from app.agent import conversation
from app.agent.tools.extraction import extract_document
from app.agent.tools.math_tool import evaluate
from app.agent.tools.persistence import store_decision, store_purchase_order
from app.agent.tools.po_lookup import lookup_purchase_order
from app.config import get_settings
from app.schemas.decision import Check
from app.schemas.invoice import ExtractedInvoice, InvoiceLineItem, VendorInfo
from app.schemas.purchase_order import POLineItem, PurchaseOrder


def png_bytes() -> bytes:
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (8, 8), (255, 255, 255)).save(buf, format="PNG")
    return buf.getvalue()


# --- Canned extractions -------------------------------------------------- #

# Line items matching the seeded PO-54872 (subtotal 55615.00).
_PO_54872_LINES = [
    ("ECG Monitor", 2, 4250.0, 8500.0),
    ("Defibrillator", 1, 5800.0, 5800.0),
    ("Patient Monitor System", 3, 7200.0, 21600.0),
    ("Sterile Syringe Pack (100)", 10, 180.0, 1800.0),
    ("Infusion Pump", 2, 3350.0, 6700.0),
    ("Hospital Bed (Adjustable)", 4, 1580.0, 6320.0),
    ("Medical Cart (Steel)", 3, 795.0, 2385.0),
    ("Digital Thermometer (Batch of 25)", 2, 625.0, 1250.0),
    ("Oxygen Cylinder with Mask", 6, 210.0, 1260.0),
]
_SUBTOTAL = 55615.0
_TAX = round(_SUBTOTAL * 0.09125, 2)  # 5074.87 — consistent with the flat rate
_TOTAL = round(_SUBTOTAL + _TAX, 2)


def invoice_matching_po_54872(**overrides) -> ExtractedInvoice:
    inv = ExtractedInvoice(
        invoice_number="INV-9001",
        po_number="PO-54872",
        invoice_date="2025-05-01",
        currency="USD",
        subtotal=_SUBTOTAL,
        tax_amount=_TAX,
        discount_amount=0.0,
        shipping_charges=0.0,
        total_amount=_TOTAL,
        vendor=VendorInfo(name="MedEquip Diagnostics LLC", tax_id="12-3456789",
                          street_address="1450 Industrial Rd, Suite 300", city="San Carlos",
                          state="CA", zip_code="94070"),
        line_items=[
            InvoiceLineItem(description=d, quantity=q, unit_price=u, tax_rate=0.09125, total_price=t)
            for d, q, u, t in _PO_54872_LINES
        ],
    )
    return inv.model_copy(update=overrides)


def invoice_for_new_po(po_number="PO-NEW-1") -> ExtractedInvoice:
    return ExtractedInvoice(
        invoice_number="INV-NEW-1",
        po_number=po_number,
        invoice_date="2025-06-01",
        currency="USD",
        subtotal=100.0,
        tax_amount=round(100.0 * 0.09125, 2),
        discount_amount=0.0,
        shipping_charges=0.0,
        total_amount=round(100.0 + 100.0 * 0.09125, 2),
        vendor=VendorInfo(name="TechCore Solutions LLC", tax_id="99-9"),
        line_items=[InvoiceLineItem(description="Widget", quantity=2, unit_price=50.0,
                                    tax_rate=0.09125, total_price=100.0)],
    )


def uploaded_po(po_number="PO-NEW-1") -> PurchaseOrder:
    return PurchaseOrder(
        po_number=po_number,
        currency="USD",
        subtotal=100.0,
        total_amount=round(100.0 + 100.0 * 0.09125, 2),
        vendor=VendorInfo(name="TechCore Solutions LLC", tax_id="99-9"),
        line_items=[POLineItem(description="Widget", quantity=2, unit_price=50.0, total_price=100.0)],
    )


# --------------------------------------------------------------------------- #
# Deterministic check logic (reference impl for tests; prod uses the LLM prompt)
# --------------------------------------------------------------------------- #


def _run_invoice_checks(inv: ExtractedInvoice) -> list[Check]:
    s = get_settings()
    checks: list[Check] = []

    missing = [
        f
        for f, v in {
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date,
            "subtotal": inv.subtotal,
            "total_amount": inv.total_amount,
            "currency": inv.currency,
            "vendor_name": inv.vendor.name,
        }.items()
        if v in (None, "")
    ]
    checks.append(
        Check(id="mandatory_fields", status="pass" if not missing else "fail",
              detail="all present" if not missing else f"missing: {missing}", compared={"missing": missing})
    )

    cur_ok = (inv.currency or "").upper() in s.supported_currencies
    checks.append(Check(id="currency", status="pass" if cur_ok else "fail",
                        detail=f"{inv.currency} supported={cur_ok}"))

    line_bad = []
    for li in inv.line_items:
        expected = evaluate(f"{li.quantity}*{li.unit_price}")
        if abs(expected - li.total_price) > s.line_tolerance:
            line_bad.append(li.description)
    checks.append(Check(id="line_item_math", status="pass" if not line_bad else "fail",
                        detail="ok" if not line_bad else f"bad: {line_bad}"))

    if inv.subtotal is not None and inv.tax_amount is not None:
        expected_tax = round(inv.subtotal * s.tax_rate, 2)
        tax_ok = abs(expected_tax - inv.tax_amount) <= s.tax_discrepancy_tolerance
        checks.append(Check(id="sales_tax", status="pass" if tax_ok else "fail",
                            compared={"expected": expected_tax, "actual": inv.tax_amount}))
    else:
        checks.append(Check(id="sales_tax", status="skipped", detail="tax inputs unavailable"))

    ft_ok = True
    compared = {}
    if inv.subtotal is not None and inv.total_amount is not None:
        computed = inv.subtotal + (inv.tax_amount or 0) + (inv.shipping_charges or 0) - (inv.discount_amount or 0)
        compared = {"expected": round(computed, 2), "actual": inv.total_amount}
        ft_ok = abs(computed - inv.total_amount) <= s.total_tolerance
    checks.append(Check(id="financial_totals", status="pass" if ft_ok else "fail", compared=compared))
    return checks


def _run_po_checks(inv: ExtractedInvoice, po: PurchaseOrder | None, skip_reason: str) -> list[Check]:
    if po is None:
        return [
            Check(id="po_vendor_match", status="skipped", detail=skip_reason),
            Check(id="po_line_items_match", status="skipped", detail=skip_reason),
        ]
    s = get_settings()
    name_match = (inv.vendor.name or "").lower() == (po.vendor.name or "").lower()
    tax_match = (inv.vendor.tax_id or "") == (po.vendor.tax_id or "")
    confidence = 1.0 if (name_match and tax_match) else 0.8 if name_match else 0.2
    v_status = "pass" if confidence >= s.vendor_match_threshold else "fail"
    checks = [Check(id="po_vendor_match", status=v_status, confidence=confidence,
                    rationale=f"name_match={name_match} tax_match={tax_match}")]

    po_by_desc = {(li.description or "").lower(): li for li in po.line_items}
    bad = []
    for li in inv.line_items:
        match = po_by_desc.get((li.description or "").lower())
        if match is None:
            bad.append(li.description)
            continue
        qty_ok = match.quantity == 0 or abs(match.quantity - li.quantity) / abs(match.quantity) <= s.po_qty_tolerance
        price_ok = match.total_price == 0 or abs(match.total_price - li.total_price) / abs(match.total_price) <= s.po_total_price_tolerance
        if not (qty_ok and price_ok):
            bad.append(li.description)
    checks.append(Check(id="po_line_items_match", status="pass" if not bad else "fail",
                        detail="ok" if not bad else f"mismatch: {bad}"))
    return checks


class FakeAgent:
    """Replays the orchestrator workflow deterministically by calling the real tools."""

    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.last_invoice: dict | None = None

    async def invoke_async(self, prompt: str):
        has_invoice = conversation.get_attachment("invoice_1") is not None
        has_po = conversation.get_attachment("po_1") is not None

        # Non-processing turn: no new invoice and none retained -> just answer.
        if not has_invoice and self.last_invoice is None and not has_po:
            return "How can I help with your invoice?"

        if has_invoice:
            extracted = extract_document("invoice_1", "invoice")
            if "error" in extracted:
                return f"I couldn't read the invoice: {extracted['error']}"
            self.last_invoice = extracted

        if self.last_invoice is None:
            return "Please upload an invoice to process."

        inv = ExtractedInvoice.model_validate(self.last_invoice)

        po: PurchaseOrder | None = None
        skip_reason = "no PO number"
        if has_po:
            po_dict = extract_document("po_1", "purchase_order")
            if "error" not in po_dict:
                store_purchase_order(po_dict)
                po = PurchaseOrder.model_validate(po_dict)
                po.source = "uploaded"
        elif inv.po_number:
            found = lookup_purchase_order(inv.po_number)
            if found.get("found"):
                po = PurchaseOrder.model_validate(found["purchase_order"])
                po.source = "database"
            else:
                skip_reason = "PO not found"

        checks = _run_invoice_checks(inv) + _run_po_checks(inv, po, skip_reason)
        verdict = "NEEDS_REVIEW" if any(c.status == "fail" for c in checks) else "APPROVED"
        reasons = [{"code": c.id, "detail": c.detail} for c in checks if c.status == "fail"]
        decision = {
            "verdict": verdict,
            "reasons": reasons,
            "checks": [c.model_dump() for c in checks],
            "explanation": f"Verdict {verdict}. PO source: {po.source if po else 'none'}.",
            "extracted_invoice": inv.model_dump(),
            "matched_po": po.model_dump() if po else None,
        }
        result = store_decision(decision)
        return f"{verdict}. Recorded as {result['record_id']}."

    async def stream_async(self, prompt: str):
        """Emit a couple of tool events + a token, then run the same processing so
        pop_decision is populated (mirrors Strands' stream_async event shape)."""
        if conversation.get_attachment("invoice_1") is not None:
            yield {"current_tool_use": {"toolUseId": "t1", "name": "extract_document", "input": {"document_type": "invoice"}}}
        text = await self.invoke_async(prompt)
        yield {"data": text}


def install_fake_agent(monkeypatch, extraction_map: dict):
    """Wire the AGENT_FACTORY seam and stub vision extraction with canned models.

    extraction_map: {"invoice": ExtractedInvoice, "purchase_order": PurchaseOrder}
    """
    from app.agent import orchestrator
    from app.services import extraction_service

    agents: dict[str, FakeAgent] = {}

    def factory(conversation_id: str):
        if conversation_id not in agents:
            agents[conversation_id] = FakeAgent(conversation_id)
        return agents[conversation_id]

    monkeypatch.setattr(orchestrator, "AGENT_FACTORY", factory)

    def fake_extract(images, document_type):
        return extraction_map[document_type]

    monkeypatch.setattr(extraction_service, "extract", fake_extract)
    return agents
