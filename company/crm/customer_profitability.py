"""Customer-level profitability tracking from observable billing records — Phase 44a.

The company observes its own billing records: revenue charged, wholesale cost (from
hedge P&L decomposition), policy and network costs billed. From these it can estimate
whether each customer's last term was profitable.

Epistemic constraint: uses only company-observable accounting data — records the
company itself produced (bills sent, costs it paid). No simulation internals.
"""

from __future__ import annotations

from datetime import date

# Uplift applied to renewal rate when prior-term net margin was negative.
# Set at £3/MWh — enough to move a marginally-negative customer to breakeven,
# with £1/MWh headroom. Smaller than the £2/MWh base target so large chronic
# losers still churn (the market rejects over-priced customers naturally).
NET_NEGATIVE_UPLIFT_GBP_PER_MWH = 3.0

# Minimum prior-term records needed to make a profitability judgement.
# If fewer records exist (e.g. first term), return no adjustment.
MIN_RECORDS_FOR_JUDGEMENT = 48  # at least 1 month of HH data


def estimate_prior_term_net_margin(
    customer_id: str,
    term_start: str,
    all_records: list[dict],
) -> float | None:
    """Estimate net margin (£) the company earned from this customer in their most
    recent completed term before term_start.

    Uses only company-observable fields present in settlement records:
    - revenue_gbp
    - wholesale_cost_gbp (or can be derived from hedge_pnl_gbp + implied cost)
    - policy_cost_gbp + network_cost_gbp (passed through)
    - capital_cost_gbp
    - net_margin_gbp (directly observable — the company knows its own books)

    Returns None if insufficient history (first term or < MIN_RECORDS_FOR_JUDGEMENT records).
    Returns total net margin £ over the most recent prior term.
    """
    prior_records = [
        r for r in all_records
        if r.get("customer_id") == customer_id
        and r.get("settlement_date", "") < term_start
        and r.get("commodity") == "electricity"
        and "net_margin_gbp" in r
    ]
    if len(prior_records) < MIN_RECORDS_FOR_JUDGEMENT:
        return None

    # Find the most recent term_start in the prior records
    terms_seen: dict[str, list[dict]] = {}
    for r in prior_records:
        ts = r.get("term_start", r.get("settlement_date", "")[:10])
        terms_seen.setdefault(ts, []).append(r)

    if not terms_seen:
        return None

    most_recent_term = max(terms_seen.keys())
    term_records = terms_seen[most_recent_term]

    if len(term_records) < MIN_RECORDS_FOR_JUDGEMENT:
        return None

    return sum(r["net_margin_gbp"] for r in term_records)


def compute_profitability_uplift(
    customer_id: str,
    term_start: str,
    all_records: list[dict],
) -> float:
    """Return a unit rate uplift (£/MWh) for renewal pricing based on prior-term P&L.

    Returns NET_NEGATIVE_UPLIFT_GBP_PER_MWH if the prior term was net-negative,
    0.0 otherwise (including when there's insufficient history).

    A real supplier's commercial team would identify loss-making accounts and
    quote them a higher renewal rate — or decline to retain them and let them churn.
    The churn model will handle the latter outcome: a higher rate increases churn
    probability, naturally filtering out price-sensitive customers.
    """
    prior_net = estimate_prior_term_net_margin(customer_id, term_start, all_records)
    if prior_net is None:
        return 0.0
    return NET_NEGATIVE_UPLIFT_GBP_PER_MWH if prior_net < 0.0 else 0.0
