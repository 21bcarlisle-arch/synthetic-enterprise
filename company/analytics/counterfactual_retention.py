from __future__ import annotations

from dataclasses import dataclass
from typing import Any

RESI_OFFER_COST_GBP: float = 50.0
IC_OFFER_COST_GBP: float = 200.0
_RETENTION_EFFECTIVENESS: float = 0.20


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


@dataclass
class CounterfactualRetentionReport:
    misses: list[CounterfactualMiss]
    total_value_at_stake_gbp: float
    total_recoverable_gbp: float
    total_net_value_gbp: float
    recoverable_count: int
    would_have_been_retained_count: int


def _offer_cost(segment: str) -> float:
    if segment.startswith("ic") or segment in ("ic", "I&C", "ic_hh", "ic_nhh", "ic_gas"):
        return IC_OFFER_COST_GBP
    return RESI_OFFER_COST_GBP


def compute_counterfactual_retention(
    no_offer_churn_log: list[dict[str, Any]],
    customer_events: list[dict[str, Any]],
    customers: list[dict[str, Any]] | None = None,
    retention_effectiveness: float = _RETENTION_EFFECTIVENESS,
) -> CounterfactualRetentionReport:
    """For each no-offer churn, compute the counterfactual outcome had an offer been made."""
    events_by_key: dict[tuple, dict] = {}
    for e in customer_events:
        key = (e["customer_id"], e.get("event_date", e.get("term_start", "")))
        events_by_key[key] = e

    seg_by_cid: dict[str, str] = {}
    if customers:
        for c in customers:
            seg_by_cid[c["customer_id"]] = c.get("segment", "resi")

    misses: list[CounterfactualMiss] = []
    for miss in no_offer_churn_log:
        cid = miss["customer_id"]
        event_date = miss["event_date"]
        company_est = miss.get("company_churn_estimate", 0.0)
        expected_margin = miss.get("expected_term_margin_gbp", 0.0)

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
