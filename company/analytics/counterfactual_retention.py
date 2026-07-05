from __future__ import annotations

from dataclasses import dataclass
from typing import Any

RESI_OFFER_COST_GBP: float = 50.0
IC_OFFER_COST_GBP: float = 200.0
_RETENTION_EFFECTIVENESS: float = 0.20

_TIER_CLASS_BY_DISCOUNT: list[tuple[float, str]] = [
    (0.08, "uneconomical_high"),
    (0.05, "uneconomical_medium"),
    (0.03, "uneconomical_low"),
]
_DETECTION_GATE_HYPOTHETICAL_DISCOUNT_PCT: float = 0.03

ASSUMED_EFFECTIVENESS_PER_DISCOUNT_POINT: float = 0.04

INTERVENTION_CLASS_LABELS: dict[str, str] = dict(
    detection_gate="Detection gate (never scored above offer threshold)",
    uneconomical_high="High-risk tier (8% discount) blocked by cost/benefit guard",
    uneconomical_medium="Medium-risk tier (5% discount) blocked by cost/benefit guard",
    uneconomical_low="Low-risk tier (3% discount) blocked by cost/benefit guard",
    uneconomical_other="Other tier blocked by cost/benefit guard",
)


def classify_intervention(no_offer_reason, would_be_discount_pct):
    if no_offer_reason == "uneconomical" and would_be_discount_pct is not None:
        for pct, label in _TIER_CLASS_BY_DISCOUNT:
            if abs(would_be_discount_pct - pct) < 1e-9:
                return label, would_be_discount_pct
        return "uneconomical_other", would_be_discount_pct
    return "detection_gate", _DETECTION_GATE_HYPOTHETICAL_DISCOUNT_PCT


def effectiveness_for_discount(discount_pct):
    return min(0.95, ASSUMED_EFFECTIVENESS_PER_DISCOUNT_POINT * discount_pct * 100.0)


@dataclass
class CounterfactualMiss:
    customer_id: str
    event_date: str
    company_churn_estimate: float
    sim_churn_probability: float
    random_roll: float
    effective_p_retain: float
    expected_term_margin_gbp: float
    segment: str
    counterfactual_retained: bool
    retention_cost_gbp: float
    value_recovered_gbp: float
    net_value_of_offer_gbp: float
    was_worth_offering: bool
    intervention_class: str = "detection_gate"
    assumed_discount_pct: float = _DETECTION_GATE_HYPOTHETICAL_DISCOUNT_PCT


@dataclass
class CounterfactualRetentionReport:
    misses: list
    total_value_at_stake_gbp: float
    total_recoverable_gbp: float
    total_net_value_gbp: float
    recoverable_count: int
    would_have_been_retained_count: int


@dataclass
class InterventionClassLift:
    intervention_class: str
    label: str
    assumed_discount_pct: float
    assumed_effectiveness: float
    miss_count: int
    total_expected_margin_at_stake_gbp: float
    total_offer_cost_gbp: float
    would_have_been_retained_count: int
    total_value_recovered_gbp: float
    net_value_gbp: float
    lift_per_pound: object


@dataclass
class CounterfactualLiftReport:
    by_class: list
    misses: list


def _offer_cost(segment):
    if segment.startswith("ic") or segment in ("ic", "I&C", "ic_hh", "ic_nhh", "ic_gas"):
        return IC_OFFER_COST_GBP
    return RESI_OFFER_COST_GBP


def compute_counterfactual_retention(
    no_offer_churn_log,
    customer_events,
    customers=None,
    retention_effectiveness=_RETENTION_EFFECTIVENESS,
):
    events_by_key = {}
    for e in customer_events:
        key = (e["customer_id"], e.get("event_date", e.get("term_start", "")))
        events_by_key[key] = e

    seg_by_cid = {}
    if customers:
        for c in customers:
            seg_by_cid[c["customer_id"]] = c.get("segment", "resi")

    misses = []
    for miss in no_offer_churn_log:
        cid = miss["customer_id"]
        event_date = miss["event_date"]
        company_est = miss.get("company_churn_estimate", 0.0)
        expected_margin = miss.get("expected_term_margin_gbp", 0.0)
        intervention_class, assumed_discount_pct = classify_intervention(
            miss.get("no_offer_reason"), miss.get("would_be_discount_pct"),
        )

        evt = events_by_key.get((cid, event_date), {})
        sim_p = evt.get("realized_churn_probability", evt.get("churn_probability", 0.0))
        roll = evt.get("random_roll", 0.0)
        eff_p_retain = evt.get("effective_retention_probability", 1.0 - sim_p)

        p_churn = 1.0 - eff_p_retain
        counterfactual_p_retain = 1.0 - p_churn * (1.0 - retention_effectiveness)
        counterfactual_retained = roll <= counterfactual_p_retain

        segment = seg_by_cid.get(cid, evt.get("segment", "resi"))
        cost = _offer_cost(segment)
        value_recovered = expected_margin if counterfactual_retained else 0.0
        net_value = value_recovered - cost

        misses.append(CounterfactualMiss(
            customer_id=cid,
            event_date=event_date,
            company_churn_estimate=company_est,
            sim_churn_probability=sim_p,
            random_roll=roll,
            effective_p_retain=eff_p_retain,
            expected_term_margin_gbp=expected_margin,
            segment=segment,
            counterfactual_retained=counterfactual_retained,
            retention_cost_gbp=cost,
            value_recovered_gbp=value_recovered,
            net_value_of_offer_gbp=net_value,
            was_worth_offering=net_value > 0,
            intervention_class=intervention_class,
            assumed_discount_pct=assumed_discount_pct,
        ))

    total_at_stake = sum(m.expected_term_margin_gbp for m in misses)
    total_recoverable = sum(m.value_recovered_gbp for m in misses)
    total_net = sum(m.net_value_of_offer_gbp for m in misses if m.was_worth_offering)
    recoverable_count = sum(1 for m in misses if m.was_worth_offering)
    retained_count = sum(1 for m in misses if m.counterfactual_retained)

    return CounterfactualRetentionReport(
        misses=misses,
        total_value_at_stake_gbp=total_at_stake,
        total_recoverable_gbp=total_recoverable,
        total_net_value_gbp=total_net,
        recoverable_count=recoverable_count,
        would_have_been_retained_count=retained_count,
    )


def compute_counterfactual_lift_by_class(
    no_offer_churn_log,
    customer_events,
    customers=None,
):
    events_by_key = {}
    for e in customer_events:
        key = (e["customer_id"], e.get("event_date", e.get("term_start", "")))
        events_by_key[key] = e

    seg_by_cid = {}
    if customers:
        for c in customers:
            seg_by_cid[c["customer_id"]] = c.get("segment", "resi")

    misses = []
    for miss in no_offer_churn_log:
        cid = miss["customer_id"]
        event_date = miss["event_date"]
        company_est = miss.get("company_churn_estimate", 0.0)
        expected_margin = miss.get("expected_term_margin_gbp", 0.0)
        intervention_class, assumed_discount_pct = classify_intervention(
            miss.get("no_offer_reason"), miss.get("would_be_discount_pct"),
        )
        effectiveness = effectiveness_for_discount(assumed_discount_pct)

        evt = events_by_key.get((cid, event_date), {})
        sim_p = evt.get("realized_churn_probability", evt.get("churn_probability", 0.0))
        roll = evt.get("random_roll", 0.0)
        eff_p_retain = evt.get("effective_retention_probability", 1.0 - sim_p)

        p_churn = 1.0 - eff_p_retain
        counterfactual_p_retain = 1.0 - p_churn * (1.0 - effectiveness)
        counterfactual_retained = roll <= counterfactual_p_retain

        segment = seg_by_cid.get(cid, evt.get("segment", "resi"))
        cost = _offer_cost(segment)
        value_recovered = expected_margin if counterfactual_retained else 0.0
        net_value = value_recovered - cost

        misses.append(CounterfactualMiss(
            customer_id=cid,
            event_date=event_date,
            company_churn_estimate=company_est,
            sim_churn_probability=sim_p,
            random_roll=roll,
            effective_p_retain=eff_p_retain,
            expected_term_margin_gbp=expected_margin,
            segment=segment,
            counterfactual_retained=counterfactual_retained,
            retention_cost_gbp=cost,
            value_recovered_gbp=value_recovered,
            net_value_of_offer_gbp=net_value,
            was_worth_offering=net_value > 0,
            intervention_class=intervention_class,
            assumed_discount_pct=assumed_discount_pct,
        ))

    by_class = []
    class_order = ("detection_gate", "uneconomical_high", "uneconomical_medium",
                    "uneconomical_low", "uneconomical_other")
    for cls in class_order:
        cls_misses = [m for m in misses if m.intervention_class == cls]
        if not cls_misses:
            continue
        total_cost = sum(m.retention_cost_gbp for m in cls_misses)
        total_net = sum(m.net_value_of_offer_gbp for m in cls_misses)
        by_class.append(InterventionClassLift(
            intervention_class=cls,
            label=INTERVENTION_CLASS_LABELS.get(cls, cls),
            assumed_discount_pct=cls_misses[0].assumed_discount_pct,
            assumed_effectiveness=effectiveness_for_discount(cls_misses[0].assumed_discount_pct),
            miss_count=len(cls_misses),
            total_expected_margin_at_stake_gbp=sum(m.expected_term_margin_gbp for m in cls_misses),
            total_offer_cost_gbp=total_cost,
            would_have_been_retained_count=sum(1 for m in cls_misses if m.counterfactual_retained),
            total_value_recovered_gbp=sum(m.value_recovered_gbp for m in cls_misses),
            net_value_gbp=total_net,
            lift_per_pound=(total_net / total_cost) if total_cost > 0 else None,
        ))

    return CounterfactualLiftReport(by_class=by_class, misses=misses)
