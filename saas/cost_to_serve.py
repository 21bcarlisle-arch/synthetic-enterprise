"""Cost-to-serve model — operational overheads per customer account.

Phase 4a-1 (customer value layer). `simulation/portfolio_pnl.py` reports
`margin_gbp` as revenue minus wholesale cost only — it does not capture the
operational cost of actually serving an account: billing and customer
service systems and smart meter operation. This module adds that layer on
top of settlement records, producing a "net of cost-to-serve" margin per
customer and per portfolio.

Cost-to-serve is fixed overhead only — billing/IT/customer-service plus
smart-meter operation, an annual £ figure per account divided evenly across
settlement periods. SME accounts cost more to serve in absolute terms
(dedicated account management, more complex billing) but far less per kWh
given their much larger consumption.

Bad debt is deliberately NOT a cost-to-serve component (removed here in the
CTS ledger-reconciliation fix, docs/staging/drafts/NEXT_PHASE.md option B).
Bad debt is owned end-to-end by the real, emergent arrears model
(`simulation/arrears_engine.py`, ledger account 6001 "Bad Debt Expense") since
Phase QD found the flat `BAD_DEBT_RATE` formula below overstated true bad debt
~30x. `BAD_DEBT_RATE`/`get_bad_debt_rate()` remain in this module only because
`simulation/run_phase2b.py` still uses them as a real-time placeholder,
overwritten once bills exist and `apply_emergent_bad_debt()` runs — they are
no longer part of the cost-to-serve figure itself, to avoid double-counting
the same economic event as two different bad-debt lines on one P&L.

Each commodity contract (electricity or gas) is billed as its own account,
so a dual-fuel household (e.g. C1 + C1g) carries fixed overhead twice — this
mirrors the separate billing/metering relationships dual-fuel customers
actually have with a supplier, even when bundled commercially.

This module is pure: it takes plain dicts/lists as input (settlement
records plus the CUSTOMERS roster from saas/customers.py) and returns plain
dicts. No imports from `sim/`.
"""

SETTLEMENT_PERIODS_PER_YEAR = 17_520  # 48 periods/day * 365 days

# Annual fixed overhead per account (£), by segment: billing/IT/customer
# service plus smart-meter operation.
FIXED_OVERHEAD_GBP_PER_YEAR = {
    "resi": 55.00,
    "SME": 120.00,
    "I&C": 500.00,  # dedicated account management, complex settlement, credit facility
}

# Bad debt provision as a fraction of revenue, by segment. SME accounts
# carry a lower rate — credit-checked at acquisition and faster to
# disconnect/recover on default.
BAD_DEBT_RATE = {
    "resi": 0.02,
    "SME": 0.01,
    "I&C": 0.005,  # I&C customers credit-checked at acquisition; lower default rate
}

FIXED_OVERHEAD_GBP_PER_PERIOD = {
    segment: annual / SETTLEMENT_PERIODS_PER_YEAR
    for segment, annual in FIXED_OVERHEAD_GBP_PER_YEAR.items()
}


_BAD_DEBT_RATE_BY_YEAR: dict[int, dict[str, float]] = {
    2016: {"resi": 0.02, "SME": 0.01, "I&C": 0.005},
    2017: {"resi": 0.02, "SME": 0.01, "I&C": 0.005},
    2018: {"resi": 0.02, "SME": 0.01, "I&C": 0.005},
    2019: {"resi": 0.02, "SME": 0.01, "I&C": 0.005},
    2020: {"resi": 0.02, "SME": 0.01, "I&C": 0.005},
    2021: {"resi": 0.04, "SME": 0.015, "I&C": 0.005},
    2022: {"resi": 0.08, "SME": 0.03, "I&C": 0.01},
    2023: {"resi": 0.05, "SME": 0.02, "I&C": 0.005},
    2024: {"resi": 0.03, "SME": 0.012, "I&C": 0.005},
}

def get_bad_debt_rate(year: int, segment: str) -> float:
    """Return the bad debt rate (fraction of revenue) for a given year and segment.

    Phase 57: year-varying rates reflect the 2021-2022 UK energy crisis payment
    default surge. Years outside 2016-2024 fall back to the segment baseline.
    """
    year_rates = _BAD_DEBT_RATE_BY_YEAR.get(year, BAD_DEBT_RATE)
    return year_rates.get(segment, BAD_DEBT_RATE.get(segment, 0.02))

def cost_to_serve_for_period(segment: str, revenue_gbp: float) -> float:
    """Return the cost-to-serve (£) for one settlement period for one account.

    segment: "resi" or "SME" — must be a key in FIXED_OVERHEAD_GBP_PER_YEAR.
    revenue_gbp: this period's billed revenue for the account. Currently
        unused (cost-to-serve is fixed overhead only, see module docstring)
        but kept in the signature for call-site stability and in case a
        future revenue-scaled component (e.g. transaction fees) is added.
    """
    return FIXED_OVERHEAD_GBP_PER_PERIOD[segment]


def build_cost_to_serve(settlement_records: list[dict], customers: list[dict]) -> dict:
    """Aggregate cost-to-serve across settlement records.

    Returns:
      {
        "portfolio": {cost_to_serve_gbp, margin_gbp, net_margin_gbp},
        "by_customer": {
          "<customer_id>": {cost_to_serve_gbp, margin_gbp, net_margin_gbp},
          ...  # in first-encountered order
        },
      }

    `margin_gbp` here is the pre-existing revenue-minus-wholesale-cost figure
    (as in simulation/portfolio_pnl.py); `net_margin_gbp` is `margin_gbp`
    minus `cost_to_serve_gbp`. An empty input returns zeroed/empty structures
    rather than raising.

    Raises KeyError if a settlement record references a customer_id not
    present in `customers`.
    """
    segment_by_customer = {c["customer_id"]: c["segment"] for c in customers}

    portfolio = {
        "cost_to_serve_gbp": 0.0,
        "margin_gbp": 0.0,
        "net_margin_gbp": 0.0,
    }
    by_customer: dict[str, dict] = {}

    for record in settlement_records:
        customer_id = record["customer_id"]
        segment = segment_by_customer[customer_id]
        cost = cost_to_serve_for_period(segment, record["revenue_gbp"])
        margin = record["margin_gbp"]

        if customer_id not in by_customer:
            by_customer[customer_id] = {
                "cost_to_serve_gbp": 0.0,
                "margin_gbp": 0.0,
                "net_margin_gbp": 0.0,
            }

        entry = by_customer[customer_id]
        entry["cost_to_serve_gbp"] += cost
        entry["margin_gbp"] += margin
        entry["net_margin_gbp"] += margin - cost

        portfolio["cost_to_serve_gbp"] += cost
        portfolio["margin_gbp"] += margin
        portfolio["net_margin_gbp"] += margin - cost

    return {"portfolio": portfolio, "by_customer": by_customer}


def build_cost_to_serve_ledger_events(
    settlement_records: list[dict], customers: list[dict],
) -> list[dict]:
    """Aggregate cost-to-serve into monthly totals for the double-entry ledger.

    CTS reconciliation fix (docs/staging/drafts/NEXT_PHASE.md option B):
    `company/finance/double_entry.py` account 6100 ("Cost to Serve") existed
    but nothing ever emitted a matching ledger event, so it always netted to
    £0 against the non-zero figure this module reports for customer-value/
    pricing decisions. Returns one entry per calendar month present in
    `settlement_records`, keyed the same way `saas.ledger.make_fixed_cost_event`
    keys `fixed_cost_event` (month bucket, not per-customer), so downstream
    monthly/annual management accounts get a real, non-zero 6100 balance
    without a per-settlement-period explosion of ledger entries.

    Returns: [{"month": "YYYY-MM", "amount_gbp": float}, ...] sorted by month.
    """
    segment_by_customer = {c["customer_id"]: c["segment"] for c in customers}
    by_month: dict[str, float] = {}

    for record in settlement_records:
        month = record["settlement_date"][:7]
        segment = segment_by_customer[record["customer_id"]]
        cost = cost_to_serve_for_period(segment, record["revenue_gbp"])
        by_month[month] = by_month.get(month, 0.0) + cost

    return [
        {"month": month, "amount_gbp": by_month[month]}
        for month in sorted(by_month)
    ]
