"""Payment behaviour model — Phase 4c-5 (physical simulation layer).

Replaces `saas/cost_to_serve.py`'s flat `BAD_DEBT_RATE` (2% resi / 1% SME of
revenue) with a per-customer credit-risk segment: low/medium/high/vulnerable.
Each segment carries:

- a default probability (`DEFAULT_PROBABILITY_BY_CREDIT_RISK`), used as the
  bad-debt provision rate in place of the flat percentage, and
- a payment-timing distribution (`PAYMENT_TIMING_DAYS_BY_CREDIT_RISK`) — the
  typical number of days after a bill's period-end a payment is received.

Not yet wired into `saas/cost_to_serve.py` or `simulation/portfolio_pnl.py`
— like 4c-2's `simulation/demand_model.py`, this is a standalone module ready
for integration (see `docs/status/LATEST.md`'s Phase 4c-5 entry for the
flagged next step).

`CREDIT_RISK_BY_CUSTOMER` and the segment constants below are seed estimates
pending the `customer-archetype-data-enrichment` background task — see
`saas/property_model.py`'s module docstring for the same caveat.

This module is pure: plain dicts/lists in, plain dicts out. No imports from
`sim/`.
"""

from datetime import date, timedelta

CREDIT_RISK_SEGMENTS = ("low", "medium", "high", "vulnerable")

# Bad-debt provision rate (fraction of revenue), replacing
# saas.cost_to_serve.BAD_DEBT_RATE's flat 2% (resi) / 1% (SME).
DEFAULT_PROBABILITY_BY_CREDIT_RISK = {
    "low": 0.005,
    "medium": 0.02,
    "high": 0.05,
    "vulnerable": 0.08,
}

# Typical number of days after a bill's period-end a payment is received.
PAYMENT_TIMING_DAYS_BY_CREDIT_RISK = {
    "low": 5,
    "medium": 14,
    "high": 30,
    "vulnerable": 45,
}

VULNERABLE_SEGMENT = "vulnerable"
DEFAULT_CREDIT_RISK = "medium"

# Seed estimate — credit-risk segment per current resi customer.
CREDIT_RISK_BY_CUSTOMER = {
    "C1": "low",
    "C2": "medium",
    "C3": "vulnerable",
    "C4": "low",
}


def bad_debt_provision_gbp(credit_risk: str, revenue_gbp: float) -> float:
    """Bad-debt provision (£) for one bill, given its `credit_risk` segment
    and `revenue_gbp` (total_amount_gbp from `saas.bill_generator.generate_bill`).

    Unknown `credit_risk` values fall back to DEFAULT_CREDIT_RISK's rate.
    """
    rate = DEFAULT_PROBABILITY_BY_CREDIT_RISK.get(
        credit_risk, DEFAULT_PROBABILITY_BY_CREDIT_RISK[DEFAULT_CREDIT_RISK]
    )
    return revenue_gbp * rate


def expected_payment_date(bill_period_end: str, credit_risk: str) -> str:
    """Expected payment date (ISO date string) for a bill whose billing
    period ends on `bill_period_end`, based on `credit_risk`'s typical
    payment-timing delay.

    Unknown `credit_risk` values fall back to DEFAULT_CREDIT_RISK's timing.
    """
    days = PAYMENT_TIMING_DAYS_BY_CREDIT_RISK.get(
        credit_risk, PAYMENT_TIMING_DAYS_BY_CREDIT_RISK[DEFAULT_CREDIT_RISK]
    )
    return (date.fromisoformat(bill_period_end) + timedelta(days=days)).isoformat()


def build_payment_behaviour(bills: list[dict]) -> dict:
    """For each bill (from `saas.bill_generator.generate_bill()`), attach
    credit-risk segment, bad-debt provision, expected payment date, and a
    vulnerability flag.

    Returns a dict keyed by `customer_id`, each value a list of records (in
    `bills` order):
      {customer_id, period_end, total_amount_gbp, credit_risk,
       bad_debt_provision_gbp, expected_payment_date, is_vulnerable}

    Customers not in CREDIT_RISK_BY_CUSTOMER default to DEFAULT_CREDIT_RISK.
    """
    results: dict[str, list[dict]] = {}
    for bill in bills:
        customer_id = bill["customer_id"]
        credit_risk = CREDIT_RISK_BY_CUSTOMER.get(customer_id, DEFAULT_CREDIT_RISK)
        results.setdefault(customer_id, []).append({
            "customer_id": customer_id,
            "period_end": bill["period_end"],
            "total_amount_gbp": bill["total_amount_gbp"],
            "credit_risk": credit_risk,
            "bad_debt_provision_gbp": bad_debt_provision_gbp(credit_risk, bill["total_amount_gbp"]),
            "expected_payment_date": expected_payment_date(bill["period_end"], credit_risk),
            "is_vulnerable": credit_risk == VULNERABLE_SEGMENT,
        })
    return results
