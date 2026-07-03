from __future__ import annotations

from dataclasses import dataclass

_SHADOW_OFFER_DISCOUNT_PCT = 0.08   # shadow strategy offers 8% discount (same as live policy)
_SHADOW_ACCEPT_PROBABILITY_FACTOR = 0.9  # P(accept) = (1 - churn_estimate) * factor


@dataclass(frozen=True)
class ShadowRetentionEvent:
    customer_id: str
    year: int
    expected_margin_gbp: float
    company_churn_estimate: float
    p_accept: float              # estimated probability customer accepts offer
    shadow_margin_retained_gbp: float  # expected_margin * p_accept * (1 - discount)
    shadow_offer_cost_gbp: float       # expected_margin * p_accept * discount
    shadow_net_gain_gbp: float         # retained - cost (positive = profitable to have offered)


@dataclass(frozen=True)
class ShadowRetentionSummary:
    year: int
    no_offer_count: int
    shadow_retained_count_estimate: float  # expected number who would accept
    actual_margin_lost_gbp: float          # sum of expected_term_margin for no-offer churns
    shadow_margin_retained_gbp: float      # under universal strategy
    shadow_offer_cost_gbp: float
    shadow_net_gain_gbp: float             # net benefit of shadow strategy vs actual


def _build_event(entry: dict) -> ShadowRetentionEvent:
    cid = entry["customer_id"]
    year = int((entry.get("event_date") or "2020-01-01")[:4])
    margin = entry.get("expected_term_margin_gbp", 0.0)
    estimate = entry.get("company_churn_estimate", 0.5)

    p_accept = max(0.0, min(1.0, (1.0 - estimate) * _SHADOW_ACCEPT_PROBABILITY_FACTOR))
    retained = margin * p_accept * (1.0 - _SHADOW_OFFER_DISCOUNT_PCT)
    cost = margin * p_accept * _SHADOW_OFFER_DISCOUNT_PCT
    net_gain = retained - cost  # = margin * p_accept * (1 - 2*discount) approx

    return ShadowRetentionEvent(
        customer_id=cid,
        year=year,
        expected_margin_gbp=margin,
        company_churn_estimate=estimate,
        p_accept=p_accept,
        shadow_margin_retained_gbp=retained,
        shadow_offer_cost_gbp=cost,
        shadow_net_gain_gbp=net_gain,
    )


def build_shadow_retention_analysis(run_data: dict) -> tuple[list[ShadowRetentionEvent], list[ShadowRetentionSummary]]:
    """Returns (events, per-year summaries) for shadow universal-retention strategy."""
    no_offer_log = run_data.get("no_offer_churn_log", [])
    events = [_build_event(e) for e in no_offer_log]

    # Aggregate by year
    year_groups: dict[int, list[ShadowRetentionEvent]] = {}
    for ev in events:
        year_groups.setdefault(ev.year, []).append(ev)

    summaries = []
    for yr in sorted(year_groups.keys()):
        evs = year_groups[yr]
        summaries.append(ShadowRetentionSummary(
            year=yr,
            no_offer_count=len(evs),
            shadow_retained_count_estimate=sum(e.p_accept for e in evs),
            actual_margin_lost_gbp=sum(e.expected_margin_gbp for e in evs),
            shadow_margin_retained_gbp=sum(e.shadow_margin_retained_gbp for e in evs),
            shadow_offer_cost_gbp=sum(e.shadow_offer_cost_gbp for e in evs),
            shadow_net_gain_gbp=sum(e.shadow_net_gain_gbp for e in evs),
        ))

    return events, summaries
