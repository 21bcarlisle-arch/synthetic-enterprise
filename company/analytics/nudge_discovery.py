"""Nudge Physics discovery layer (NUDGE_PHYSICS.md Layer 1).

The company never sees simulation/nudge_physics.py's hidden loss-aversion
susceptibility model or its framing_effectiveness_multiplier -- it only
observes, for each retention offer it made, the framing_type attribute it
itself chose (company/policy/decision_policy.py::framing_type_for) and the
outcome (retained / churned_despite_offer). This module aggregates those two
observables from the real retention_log to let the company discover,
empirically, which framing tends to work better for which segment --
without ever learning why. This is the "discovered-lift table" the design
note asks for, distinct from company/analytics/counterfactual_retention.py's
existing lift-by-discount-tier engine (that one re-rolls offers that were
never made; this one compares offers that were actually made, split by an
attribute rather than a discount tier).

assess_framing_consumer_duty() is the "police its own discovered nudges"
ethics check the design note asks for. company/regulatory/vulnerable_customer_
register.py exists but has no populated caller in this sim, so a direct
vulnerability cross-reference isn't available yet -- this uses "resi" segment
concentration as a weaker, already-real proxy: if loss-framed offers lift
retention disproportionately more for residential customers than other
segments, that is flagged for review rather than asserted as fact.
"""
from __future__ import annotations

from dataclasses import dataclass

from company.compliance.consumer_duty import DutyOutcome, OutcomeAssessment, OutcomeRAG

_RESI_CONCENTRATION_AMBER_THRESHOLD = 0.15  # 15 percentage points


@dataclass(frozen=True)
class FramingSegmentLift:
    framing_type: str
    segment: str
    offers_made: int
    retained_count: int
    retention_rate: float


def compute_framing_lift_by_segment(retention_log: list[dict], customers: list[dict]) -> list[FramingSegmentLift]:
    """Empirical retention rate by (framing_type, segment) from real offers made."""
    seg_by_id = dict((c["customer_id"], c.get("segment", "resi")) for c in customers)
    groups: dict[tuple[str, str], list[bool]] = dict()
    for entry in retention_log:
        framing_type = entry.get("framing_type")
        outcome = entry.get("outcome")
        if framing_type is None or outcome not in ("retained", "churned_despite_offer"):
            continue
        segment = seg_by_id.get(entry.get("customer_id"), "resi")
        key = (framing_type, segment)
        groups.setdefault(key, []).append(outcome == "retained")

    results: list[FramingSegmentLift] = []
    for key in sorted(groups.keys()):
        framing_type, segment = key
        outcomes = groups[key]
        n = len(outcomes)
        retained = sum(outcomes)
        results.append(FramingSegmentLift(
            framing_type=framing_type,
            segment=segment,
            offers_made=n,
            retained_count=retained,
            retention_rate=round(retained / n, 4) if n else 0.0,
        ))
    return results


def assess_framing_consumer_duty(lift_by_segment: list[FramingSegmentLift], as_of: str) -> OutcomeAssessment:
    """Flag AMBER if loss-framed uplift over gain-framed concentrates in the
    residential segment well above other segments -- a proxy for exploitative
    fear-based framing, pending a populated vulnerable-customer register."""
    by_key = dict(((r.framing_type, r.segment), r) for r in lift_by_segment)

    def uplift_for(segment: str) -> float | None:
        loss = by_key.get(("loss_framed", segment))
        gain = by_key.get(("gain_framed", segment))
        if loss is None or gain is None:
            return None
        return loss.retention_rate - gain.retention_rate

    resi_uplift = uplift_for("resi")
    other_uplifts = [u for u in (uplift_for("SME"), uplift_for("I&C")) if u is not None]

    if resi_uplift is None or not other_uplifts:
        return OutcomeAssessment(
            outcome=DutyOutcome.CONSUMER_UNDERSTANDING,
            assessment_date=as_of,
            rag=OutcomeRAG.GREEN,
            metric_value=0.0,
            metric_name="loss_framing_resi_concentration_gap",
            narrative="Insufficient segment coverage this run to assess framing concentration.",
        )

    other_avg = sum(other_uplifts) / len(other_uplifts)
    gap = resi_uplift - other_avg
    rag = OutcomeRAG.AMBER if gap > _RESI_CONCENTRATION_AMBER_THRESHOLD else OutcomeRAG.GREEN
    narrative = (
        "Loss-framed retention uplift over gain-framed is "
        + str(round(gap * 100, 1))
        + "pp higher for residential customers than the average of other segments. "
    )
    if rag == OutcomeRAG.AMBER:
        narrative += (
            "Monitor: fear-based framing may be disproportionately effective on "
            "the residential book -- review for Consumer Duty exploitation risk."
        )
    else:
        narrative += "No material concentration detected."

    return OutcomeAssessment(
        outcome=DutyOutcome.CONSUMER_UNDERSTANDING,
        assessment_date=as_of,
        rag=rag,
        metric_value=round(gap, 4),
        metric_name="loss_framing_resi_concentration_gap",
        narrative=narrative,
    )


# --- NUDGE_PHYSICS.md remaining mechanism: debt-collection letter tone
# (2026-07-10). Same discovery pattern as compute_framing_lift_by_segment()
# above, applied to real persisted payment records (site/state/
# billing_ledger.json's per-customer "payments" list, each carrying the
# "tone" attribute the company itself chose via company/policy/
# decision_policy.py::tone_for() and the real "outcome" of that payment) --
# never simulation/nudge_physics.py's hidden tone-susceptibility.

@dataclass(frozen=True)
class ToneSegmentLift:
    tone: str
    segment: str
    payments_observed: int
    successful_count: int
    success_rate: float


def compute_tone_lift_by_segment(payments_by_customer: dict, customers: list[dict]) -> list[ToneSegmentLift]:
    """Empirical payment-success rate by (tone, segment) from real persisted
    payment records. `payments_by_customer` maps customer_id -> list of
    payment dicts (site/state/billing_ledger.json's own shape -- each with
    "tone" and "outcome" keys)."""
    seg_by_id = dict((c["customer_id"], c.get("segment", "resi")) for c in customers)
    groups: dict[tuple[str, str], list[bool]] = dict()
    for cid, payments in payments_by_customer.items():
        segment = seg_by_id.get(cid, "resi")
        for entry in payments:
            tone = entry.get("tone")
            outcome = entry.get("outcome")
            if tone is None or outcome not in ("success", "failed", "dispute"):
                continue
            key = (tone, segment)
            groups.setdefault(key, []).append(outcome == "success")

    results: list[ToneSegmentLift] = []
    for key in sorted(groups.keys()):
        tone, segment = key
        outcomes = groups[key]
        n = len(outcomes)
        successful = sum(outcomes)
        results.append(ToneSegmentLift(
            tone=tone,
            segment=segment,
            payments_observed=n,
            successful_count=successful,
            success_rate=round(successful / n, 4) if n else 0.0,
        ))
    return results
