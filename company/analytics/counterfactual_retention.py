"""What the retention offers we did NOT make would have been worth.

WHAT CHANGED, AND WHY IT WAS WRONG IN KIND (2026-08-28, roadmap R3 of
WORKER_FINDING_THE_SOURCED_ACQUISITION_MODEL_IS_UNWIRED_AND_THE_INVENTED_ONE_IS_LIVE.md).

Director: *"the retention one is wrong in kind, not just value: a retention offer is usually
margin sacrificed, not a cash payment — you keep the customer by charging them less, which lands
in revenue, not in a £50 cost line."*

This module used to hold `RESI_OFFER_COST_GBP = 50.0` and `IC_OFFER_COST_GBP = 200.0`, two
invented numbers with no source, charged flat per offer — while carrying 3%, 5% and 8% DISCOUNT
tiers in `_TIER_CLASS_BY_DISCOUNT` a few lines below. One intervention, priced twice and in two
incompatible shapes.

The published record settles the shape. Ofgem's SLC 22B, the Ban on Acquisition-only Tariffs, has
since April 2022 barred a supplier from offering a fixed deal to new customers that existing ones
cannot have; retention survives through the BAT's Market-wide Derogation, which in Ofgem's words
*"enables suppliers to offer bespoke, retention-only deals to their existing customers when they
are coming to the end of a fixed-term deal."* A retention offer is a TARIFF at a defined
contractual moment. It is not a payment, and no GB supplier has ever written a customer a cheque
to stay.

THREE CONSEQUENCES, and only the first is arithmetic:

 1. The cost is `discount_pct x term revenue`, not a flat sum. `run_phase2b` already computes
    exactly this for the offers it DOES make (`ret_cost = unit_rate * discount_pct * eac / 1000`),
    so this module was the only place still using the invented shape and the two halves of one
    decision disagreed.

 2. **An offer that fails costs nothing.** A discount only applies to a term the customer stays
    for; if they leave there is no term to discount. The flat cash model charged £50 whether or
    not the customer stayed, which makes offering look far more expensive than it is and is why
    the guard blocked tiers it should not have. This is the structural change, not the price one.

 3. It is UNSOURCEABLE at a flat rate anyway. The per-customer cost of a retention offer is a
    function of that customer's own consumption and rate, both of which we hold. There was never
    a number to look up.

WHAT IS STILL AN ASSUMPTION, said plainly rather than left to be discovered: the EFFECTIVENESS
figures (`_RETENTION_EFFECTIVENESS`, `ASSUMED_EFFECTIVENESS_PER_DISCOUNT_POINT`) have no source
and are not repaired here. R3 was about the cost's shape. How much a 3% discount actually moves
a household is a measurement this project has not made, and inventing a better-looking number for
it would be the same defect in a new place.
"""
from __future__ import annotations

from dataclasses import dataclass

#: How much of a churn risk an offer removes. UNSOURCED -- see the module docstring. Kept as a
#: named assumption rather than quietly folded into the arithmetic.
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
    #: Misses whose offer could not be priced because the record carries no term revenue. Every
    #: other total on this report is over the complement of this count.
    misses_that_could_not_be_priced: int = 0


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
    #: Misses in this class with no term revenue to discount. Every money figure on this row is
    #: over the complement; `lift_per_pound` in particular is a ratio over the priced subset.
    misses_that_could_not_be_priced: int = 0


@dataclass
class CounterfactualLiftReport:
    by_class: list
    misses: list


def margin_sacrificed_gbp(term_revenue_gbp, discount_pct, retained):
    """What a retention offer actually costs: the revenue given up to keep the customer.

    `None` when the miss record carries no term revenue, and that refusal is deliberate. The
    alternative to "we cannot price this offer" is 0.0, which reads as a free offer and would
    make every unpriceable miss look like the most attractive intervention in the book. An
    artefact written before `expected_term_revenue_gbp` existed is unpriceable, not free.

    Zero when the customer left anyway: there is no term to discount, so a failed offer costs
    nothing. That is not a rounding convenience -- it is the difference between a price and a
    payment, and it is the whole of what R3 changed.
    """
    if term_revenue_gbp is None:
        return None
    if not retained:
        return 0.0
    return term_revenue_gbp * discount_pct


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
        cost = margin_sacrificed_gbp(
            miss.get("expected_term_revenue_gbp"), assumed_discount_pct, counterfactual_retained,
        )
        value_recovered = expected_margin if counterfactual_retained else 0.0
        net_value = None if cost is None else value_recovered - cost

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
            was_worth_offering=net_value is not None and net_value > 0,
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
        # ON THE SURFACE, not in a footnote. A miss with no term revenue cannot be priced, and a
        # report that silently drops those reads as a complete one. If this is not zero, every
        # total above is over a SUBSET and the reader is entitled to know how big a subset.
        misses_that_could_not_be_priced=sum(1 for m in misses if m.retention_cost_gbp is None),
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
        cost = margin_sacrificed_gbp(
            miss.get("expected_term_revenue_gbp"), assumed_discount_pct, counterfactual_retained,
        )
        value_recovered = expected_margin if counterfactual_retained else 0.0
        net_value = None if cost is None else value_recovered - cost

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
            was_worth_offering=net_value is not None and net_value > 0,
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
        # PRICEABLE ONLY, and the count of the rest travels on the row. Summing `None` as zero
        # is the fail-open shape this whole change exists to remove: it would report a class as
        # costing nothing when what happened is that we could not price it.
        priced = [m for m in cls_misses if m.retention_cost_gbp is not None]
        total_cost = sum(m.retention_cost_gbp for m in priced)
        total_net = sum(m.net_value_of_offer_gbp for m in priced)
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
            misses_that_could_not_be_priced=len(cls_misses) - len(priced),
        ))

    return CounterfactualLiftReport(by_class=by_class, misses=misses)
