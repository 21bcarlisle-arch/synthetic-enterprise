"""Gas daily settlement for fixed-rate gas customers.

Gas settlement differs from electricity in three ways:
  1. Daily granularity (one period per gas day, not 48 half-hours)
  2. Flat daily consumption = AQ_kwh / 365 (no profile class, no weather shape)
  3. Price feed is NBP SAP (sim/gas_data/nbp_sap.csv) not Elexon SSP

The hedging mechanic mirrors electricity: a fixed fraction of consumption is
settled at the forward price (locked in at contract signing), the remainder at
the daily spot (NBP SAP).

Capital cost allocation mirrors hedged_settlement.py: monthly_cost_of_capital_gbp
is divided evenly across all settled days in each calendar month, producing
capital_cost_gbp and net_margin_gbp per record.

This module is called by run_phase2b.py for each gas customer term.
"""

from collections import defaultdict
from datetime import date, timedelta

from sim.risk_engine import compute_net_margin


def _daily_consumption_kwh(aq_kwh: int) -> float:
    """Flat daily consumption: AQ / 365."""
    return aq_kwh / 365.0


def run_gas_term(
    customer_id: str,
    term_start: str,
    term_end: str,
    aq_kwh: int,
    unit_rate_gbp_mwh: float,
    hedge_fraction: float,
    forward_price: float,
    monthly_cost_of_capital_gbp: float,
    gas_price_records: list[dict],
) -> list[dict]:
    """Settle one gas contract term, returning one record per gas day.

    Parameters
    ----------
    customer_id : str
    term_start, term_end : YYYY-MM-DD inclusive bounds (term_end is exclusive)
    aq_kwh : annualised quantity (kWh/year)
    unit_rate_gbp_mwh : fixed tariff unit rate (£/MWh)
    hedge_fraction : fraction of daily volume hedged at forward_price
    forward_price : forward NBP price locked at contract signing (£/MWh)
    monthly_cost_of_capital_gbp : capital cost per calendar month for this term
    gas_price_records : list of {settlementDate, systemSellPrice} daily records
    """
    spot_index = {r["settlementDate"]: r["systemSellPrice"] for r in gas_price_records}
    daily_kwh = _daily_consumption_kwh(aq_kwh)

    records = []
    current = date.fromisoformat(term_start)
    end = date.fromisoformat(term_end)

    while current < end:
        d = current.isoformat()
        spot_price = spot_index.get(d)
        if spot_price is not None:
            daily_mwh = daily_kwh / 1000.0
            hedged_mwh = daily_mwh * hedge_fraction
            unhedged_mwh = daily_mwh * (1.0 - hedge_fraction)

            billed_gbp = daily_mwh * unit_rate_gbp_mwh
            cost_gbp = hedged_mwh * forward_price + unhedged_mwh * spot_price
            margin_gbp = billed_gbp - cost_gbp

            records.append({
                "customer_id": customer_id,
                "settlement_date": d,
                "settlement_period": 1,  # gas has one period per day
                "commodity": "gas",
                "daily_kwh": round(daily_kwh, 4),
                "spot_price_gbp_mwh": round(spot_price, 4),
                "forward_price_gbp_mwh": round(forward_price, 4),
                "unit_rate_gbp_per_mwh": round(unit_rate_gbp_mwh, 4),
                "hedge_fraction": hedge_fraction,
                "hedged_mwh": round(hedged_mwh, 6),
                "unhedged_mwh": round(unhedged_mwh, 6),
                "revenue_gbp": round(billed_gbp, 6),
                "wholesale_cost_gbp": round(cost_gbp, 6),
                "margin_gbp": round(margin_gbp, 6),
                "consumption_kwh": round(daily_kwh, 4),
            })
        current += timedelta(days=1)

    # Allocate capital cost proportionally across days in each calendar month
    records_by_month: dict[str, list] = defaultdict(list)
    for rec in records:
        records_by_month[rec["settlement_date"][:7]].append(rec)

    for month_recs in records_by_month.values():
        cap_per_day = monthly_cost_of_capital_gbp / len(month_recs)
        for rec in month_recs:
            rec["capital_cost_gbp"] = round(cap_per_day, 8)
            rec["net_margin_gbp"] = round(compute_net_margin(rec["margin_gbp"], cap_per_day), 8)

    return records
