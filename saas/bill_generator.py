"""Bill generation — Phase 4c-4 / Phase 9a (physical simulation layer).

Aggregates a customer's per-settlement-period records (from
`simulation/settlement.run_settlement`) for one billing month into a bill:
total consumption, total amount due, average unit rate, and a *clarity
score* in [0, 1] (1 = very clear, 0 = very confusing).

Per the Key Domain Insight (CLAUDE.md): customer reaction to bills is
non-rational, and arithmetically correct bills frequently produce complaints
when they're hard to understand or jump unexpectedly month-to-month. Two
factors reduce clarity, both seed estimates pending real data:

1. **Tariff structure complexity** — `BASE_CLARITY_BY_CONTRACT_TYPE`. All
   current contracts are `"fixed_1yr"` (single flat rate) — maximally
   clear. Future multi-rate tariffs (e.g. Phase 5's time-of-use) would get a
   lower base.
2. **Consumption volatility within the month** — the coefficient of
   variation (stdev/mean) of daily consumption. A bill covering wildly
   uneven days (e.g. a cold spell, per Phase 4c-2/4c-3) is harder to
   reconcile against a flat unit rate than one covering steady days.
3. **Bill shock** — the percentage change in total amount due versus the
   previous month's bill, if supplied. A big swing is confusing even if both
   bills were individually correct.

Phase 9a: bills now include non-commodity pass-through (network charges +
levies), standing charge, and VAT via saas.non_commodity. The commodity
amount (from settlement records) is separated from non-commodity and
standing so the ledger can track pass-through costs correctly.

This module is pure: plain dicts/lists in, plain dict out. No imports from
`sim/`.
"""

import datetime
import statistics

from saas.non_commodity import non_commodity_rate, standing_charge_rate, vat_rate

BASE_CLARITY_BY_CONTRACT_TYPE = {
    "fixed_1yr": 1.0,
}
DEFAULT_BASE_CLARITY = 0.7

# Reduction in clarity score per unit of consumption coefficient-of-variation
# (stdev/mean of daily consumption_kwh across the billing period).
CONSUMPTION_CV_PENALTY_FACTOR = 0.5

# Reduction in clarity score per 100% change in total bill amount versus the
# previous month, capped at a 100% change (pct change beyond that doesn't
# further reduce clarity — the bill is already as confusing as it gets).
BILL_SHOCK_PENALTY_FACTOR = 0.5

MIN_CLARITY_SCORE = 0.0
MAX_CLARITY_SCORE = 1.0


def consumption_coefficient_of_variation(settlement_records: list[dict]) -> float:
    """Coefficient of variation (population stdev / mean) of total daily
    consumption_kwh across the distinct settlement_dates in
    `settlement_records`. Returns 0.0 if there's only one day or the mean is
    zero (no variation to report)."""
    daily_totals: dict[str, float] = {}
    for record in settlement_records:
        daily_totals[record["settlement_date"]] = (
            daily_totals.get(record["settlement_date"], 0.0) + record["consumption_kwh"]
        )

    totals = list(daily_totals.values())
    if len(totals) < 2:
        return 0.0
    mean = statistics.mean(totals)
    if mean == 0:
        return 0.0
    return statistics.pstdev(totals) / mean


def generate_bill(
    customer_id: str,
    settlement_records: list[dict],
    contract_type: str,
    previous_bill_total_gbp: float | None = None,
    segment: str = "resi",
    commodity: str = "electricity",
) -> dict:
    """Aggregate one customer's `settlement_records` for one billing month.

    Phase 9a: bills include non-commodity pass-through, standing charge, VAT.

    Returns:
      {customer_id, period_start, period_end, total_consumption_kwh,
       commodity_amount_gbp, non_commodity_amount_gbp, standing_charge_gbp,
       vat_gbp, total_amount_gbp, average_unit_rate_gbp_per_mwh,
       clarity_score, bill_shock_pct, segment, commodity}

    Raises ValueError if `settlement_records` is empty.
    """
    if not settlement_records:
        raise ValueError("settlement_records must be non-empty")

    dates = sorted(record["settlement_date"] for record in settlement_records)
    total_consumption_kwh = sum(record["consumption_kwh"] for record in settlement_records)
    commodity_amount_gbp = sum(record["revenue_gbp"] for record in settlement_records)

    # Non-commodity pass-through: network charges + environmental levies
    billing_year = int(dates[0][:4])
    non_commodity_amount_gbp = total_consumption_kwh / 1000 * non_commodity_rate(commodity, segment, year=billing_year)

    # Standing charge: pure supplier margin (covers metering, admin, data)
    period_start_date = datetime.date.fromisoformat(dates[0])
    period_end_date = datetime.date.fromisoformat(dates[-1])
    days_in_period = (period_end_date - period_start_date).days + 1
    standing_charge_gbp = days_in_period * standing_charge_rate(commodity, segment)

    # VAT on full pre-tax bill (5% domestic, 20% business)
    subtotal_gbp = commodity_amount_gbp + non_commodity_amount_gbp + standing_charge_gbp
    vat_gbp = subtotal_gbp * vat_rate(segment)
    total_amount_gbp = subtotal_gbp + vat_gbp

    average_unit_rate_gbp_per_mwh = (
        commodity_amount_gbp / (total_consumption_kwh / 1000) if total_consumption_kwh > 0 else 0.0
    )

    clarity_score = BASE_CLARITY_BY_CONTRACT_TYPE.get(contract_type, DEFAULT_BASE_CLARITY)
    clarity_score -= consumption_coefficient_of_variation(settlement_records) * CONSUMPTION_CV_PENALTY_FACTOR

    bill_shock_pct = None
    if previous_bill_total_gbp is not None and previous_bill_total_gbp != 0:
        bill_shock_pct = abs(total_amount_gbp - previous_bill_total_gbp) / previous_bill_total_gbp
        clarity_score -= min(bill_shock_pct, 1.0) * BILL_SHOCK_PENALTY_FACTOR

    clarity_score = max(MIN_CLARITY_SCORE, min(MAX_CLARITY_SCORE, clarity_score))

    return {
        "customer_id": customer_id,
        "period_start": dates[0],
        "period_end": dates[-1],
        "total_consumption_kwh": total_consumption_kwh,
        "commodity_amount_gbp": commodity_amount_gbp,
        "non_commodity_amount_gbp": non_commodity_amount_gbp,
        "standing_charge_gbp": standing_charge_gbp,
        "vat_gbp": vat_gbp,
        "total_amount_gbp": total_amount_gbp,
        "average_unit_rate_gbp_per_mwh": average_unit_rate_gbp_per_mwh,
        "clarity_score": clarity_score,
        "bill_shock_pct": bill_shock_pct,
        "segment": segment,
        "commodity": commodity,
        # Calculation-transparency breakdown (2026-07-10, director page comment
        # on /customers/: "Days x standing charges. Prices x days at that
        # price. We need to be able to explain the maths properly"). Both
        # days_in_period and standing_charge_gbp_per_day were already computed
        # locally above to derive standing_charge_gbp -- simply never exposed.
        # Full time-of-use (multiple rate bands per day) is a separate,
        # larger architecture gap -- the tariff engine has no multi-rate-per-
        # day concept at all yet -- registered separately, not attempted here.
        "days_in_period": days_in_period,
        "standing_charge_gbp_per_day": standing_charge_rate(commodity, segment),
    }
