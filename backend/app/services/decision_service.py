"""Pure decision/reconciliation helpers. No I/O, no model calls — deterministic
numeric logic the orchestrator (and tests) can rely on."""
from __future__ import annotations

from collections.abc import Iterable

from app.schemas.decision import Check, Decision, ReasonCode


def within(expected: float, actual: float, tolerance: float) -> bool:
    """Absolute tolerance comparison."""
    return abs(expected - actual) <= tolerance


def within_pct(expected: float, actual: float, pct: float) -> bool:
    """Relative tolerance; when expected is 0, require exact equality."""
    if expected == 0:
        return actual == 0
    return abs(expected - actual) / abs(expected) <= pct


def expected_tax(subtotal: float, tax_rate: float) -> float:
    return round(subtotal * tax_rate, 2)


def verdict_from_checks(checks: Iterable[Check]) -> str:
    """APPROVED iff no check failed; skipped checks do not block."""
    return "NEEDS_REVIEW" if any(c.status == "fail" for c in checks) else "APPROVED"


def reasons_from_checks(checks: Iterable[Check]) -> list[ReasonCode]:
    return [ReasonCode(code=c.id, detail=c.detail) for c in checks if c.status == "fail"]


def assemble_decision(
    *,
    extracted_invoice,
    checks: list[Check],
    matched_po=None,
    explanation: str = "",
) -> Decision:
    """Build a Decision with verdict/reasons derived from the checks, so the
    verdict can never contradict the trace."""
    return Decision(
        verdict=verdict_from_checks(checks),
        reasons=reasons_from_checks(checks),
        checks=checks,
        explanation=explanation,
        extracted_invoice=extracted_invoice,
        matched_po=matched_po,
    )
