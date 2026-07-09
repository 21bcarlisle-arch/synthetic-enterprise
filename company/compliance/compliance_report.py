"""Compliance function -- Phase 4 of DOMAIN_SENSE_AND_COMPLIANCE.md.

Owns company/compliance/obligations_register.py as live data and produces
the risk-tiered compliance report the director's principle 3 calls for:
depth, frequency, and visibility follow risk tier. Company-side (inside the
wall) -- a real compliance function does exactly this: maintain the
register, monitor whatever controls exist, and roll the result up into one
report a Head of Compliance would present.

This module does not invent new monitoring -- for the two obligations
Phase 3's pre-bill gate actually enforces (billing accuracy, VAT-by-
segment), status comes from the gate's own live exception-queue count
(site/state/billing_ledger.json's held_bill_count). Every other obligation
reports its existing_tracker pointer (from the register) rather than a
fabricated status -- an obligation with no live automated check is reported
as MANUAL, not silently upgraded to a false GREEN.
"""
from __future__ import annotations

from company.compliance.obligations_register import REGISTER, RiskTier


def _status_for_obligation(obligation, held_bill_count: int) -> tuple[str, str]:
    """Returns (status, basis). status is GREEN/RED for gate-covered Tier-1
    obligations (live, from the pre-bill gate's exception queue), MANUAL for
    everything else (tracked by an existing module, not yet an automated
    live check feeding this report)."""
    if obligation.id in ("slc_6_7_billing_accuracy", "vat_by_segment"):
        if held_bill_count > 0:
            return "RED", f"{held_bill_count} bill(s) held by the pre-bill validation gate"
        return "GREEN", "0 bills held by the pre-bill validation gate (Phase 3)"
    if obligation.existing_tracker:
        return "MANUAL", f"Tracked by {obligation.existing_tracker}"
    return "MANUAL", "No automated live check wired to this report yet"


def build_compliance_report(held_bill_count: int = 0) -> dict:
    """The risk-tiered compliance report: obligations grouped by tier, each
    with a real status derived from whatever live signal actually exists
    for it (see _status_for_obligation). `held_bill_count` should be read
    from site/state/billing_ledger.json's meta.held_bill_count by the
    caller (kept as a plain int here so this module has no file-I/O and
    stays independently testable)."""
    by_tier: dict[str, list[dict]] = {tier.value: [] for tier in RiskTier}
    red_count = 0
    for o in REGISTER:
        status, basis = _status_for_obligation(o, held_bill_count)
        if status == "RED":
            red_count += 1
        by_tier[o.risk_tier.value].append({
            "id": o.id,
            "name": o.name,
            "source": o.source,
            "impact": o.impact.value,
            "likelihood": o.likelihood.value,
            "control_type": o.control_type.value,
            "testing_depth": o.testing_depth.value,
            "testing_frequency": o.testing_frequency.value,
            "reporting_visibility": o.reporting_visibility.value,
            "status": status,
            "basis": basis,
            "rationale": o.rationale,
        })
    overall_rag = "RED" if red_count > 0 else "GREEN"
    return {
        "overall_rag": overall_rag,
        "held_bill_count": held_bill_count,
        "obligation_count": len(REGISTER),
        "by_tier": by_tier,
    }
