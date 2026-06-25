"""Gas daily settlement for fixed-rate gas customers.

Gas settlement differs from electricity in three ways:
  1. Daily granularity (one period per gas day, not 48 half-hours)
  2. Seasonal daily consumption = AQ_kwh / 365 × monthly_profile × weather_factor
  3. Price feed is NBP SAP (sim/gas_data/nbp_sap.csv) not Elexon SSP

The hedging mechanic mirrors electricity: a fixed fraction of consumption is
settled at the forward price (locked in at contract signing), the remainder at
the daily spot (NBP SAP).

Phase 30b adds gas-side policy costs per settlement day:
  gas_ccl_gbp      = CCL for non-domestic gas (resi exempt; SME/I&C pay)
  gas_network_cost_gbp = GDN + NTS charges (all segments)
  ggl_gbp          = Green Gas Levy (all segments, from Nov 2021)
  gas_policy_cost_gbp = gas_ccl + ggl (network kept separate like electricity)
  net_margin_gbp deducts gas_policy_cost + gas_network_cost + capital cost.

Capital cost allocation mirrors hedged_settlement.py: monthly_cost_of_capital_gbp
is divided evenly across all settled days in each calendar month, producing
capital_cost_gbp and net_margin_gbp per record.

This module is called by run_phase2b.py for each gas customer term.
"""

from collections import defaultdict
from datetime import date, timedelta

from sim.risk_engine import compute_net_margin
from simulation.policy_costs import (
    get_gas_ccl_per_mwh,
    get_gas_network_cost_per_mwh,
    get_gas_standing_charge_per_day,
    get_ggl_per_mwh,
)

# Phase 45b: gas pass-through contracts bill at actual daily spot + this service fee.
# The 20% risk premium in company_fwd is not appropriate for pass-through — the customer
# takes all commodity price risk; the company earns only a thin handling margin.
# Calibrated at £2/MWh to match the fixed tariff TARGET_MARGIN (saas/tariff_pricing.py).
GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH = 2.0

# Phase 59: within-year seasonal consumption profile for resi/SME gas.
# Derived from UK DUKES Table 4.3 residential gas monthly shares (2016-2020 avg).
# Daily factor = monthly_pct * 365 / days_in_month, normalised so annual avg = 1.0.
# Jan:Jul ratio ≈ 5.3x (matches UK peak/trough for residential heating demand).
GAS_CONSUMPTION_MONTHLY_PROFILE: dict[int, float] = {
    1: 1.8839, 2: 1.8250, 3: 1.2952, 4: 0.8517, 5: 0.5887, 6: 0.3650,
    7: 0.3532, 8: 0.3532, 9: 0.4867, 10: 0.8242, 11: 1.4600, 12: 1.7661,
}

# Phase 60: I&C gas is process-heat-dominated; much flatter seasonal shape.
# Source: UK industrial gas consumption (DUKES Table 4.3) — process heat near-flat,
# slight winter uplift from building heating. Jan:Jul ratio ≈ 1.18x vs 5.3x for resi.
# Monthly pct: Jan/Dec 9.1%, Feb/Nov 8.4%, others 7.9-8.0%.
GAS_IC_CONSUMPTION_MONTHLY_PROFILE: dict[int, float] = {
    1: 1.0746, 2: 1.1258, 3: 1.0168, 4: 0.9910, 5: 0.9590, 6: 0.9432,
    7: 0.9128, 8: 0.9128, 9: 0.9910, 10: 0.9590, 11: 1.0507, 12: 1.0746,
}


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
    segment: str = "resi",
    pass_through: bool = False,
    weather_factor: float = 1.0,
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
    segment : customer segment for CCL exemption ('resi' -> CCL exempt)
    weather_factor : HDD-based scaling for resi/SME gas consumption (1.0 = average)
    """
    spot_index = {r["settlementDate"]: r["systemSellPrice"] for r in gas_price_records}
    base_daily_kwh = _daily_consumption_kwh(aq_kwh)

    records = []
    current = date.fromisoformat(term_start)
    end = date.fromisoformat(term_end)

    while current < end:
        d = current.isoformat()
        spot_price = spot_index.get(d)
        if spot_price is not None:
            # Phase 59/60: per-day seasonal profile × Phase 58 weather factor.
            # Phase 60: I&C gas uses near-flat process-heat profile (1.18x ratio vs 5.3x resi).
            _profile = GAS_IC_CONSUMPTION_MONTHLY_PROFILE if segment == "I&C" else GAS_CONSUMPTION_MONTHLY_PROFILE
            seasonal = _profile.get(current.month, 1.0)
            daily_kwh = base_daily_kwh * seasonal * weather_factor
            daily_mwh = daily_kwh / 1000.0
            hedged_mwh = daily_mwh * hedge_fraction
            unhedged_mwh = daily_mwh * (1.0 - hedge_fraction)

            billed_gbp = daily_mwh * unit_rate_gbp_mwh
            cost_gbp = hedged_mwh * forward_price + unhedged_mwh * spot_price

            # Phase 30b: gas-side policy costs per settlement day.
            gas_ccl = get_gas_ccl_per_mwh(d, segment) * daily_mwh
            gas_network_cost = get_gas_network_cost_per_mwh(d) * daily_mwh
            ggl = get_ggl_per_mwh(d, aq_kwh) * daily_mwh
            gas_policy_cost = gas_ccl + ggl

            # Phase 40b: pass-through gas — actual policy+network added to revenue.
            # Phase 45b: pass-through bills at actual daily spot + service fee (not
            # locked company forward with 20% risk premium). Customer takes commodity
            # price risk; company earns only GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH.
            if pass_through:
                pt_billed = daily_mwh * (spot_price + GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH)
                revenue_gbp = pt_billed + gas_policy_cost + gas_network_cost
            else:
                revenue_gbp = billed_gbp
            # Phase 62: gas standing charge -- fixed daily charge for resi/SME meters.
            # I&C industrial gas (e.g. C_IC3g) uses transportation tariffs; SC=0.
            gas_sc_gbp = get_gas_standing_charge_per_day(d, segment)
            revenue_gbp += gas_sc_gbp
            margin_gbp = revenue_gbp - cost_gbp

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
                "revenue_gbp": round(revenue_gbp, 6),
                "wholesale_cost_gbp": round(cost_gbp, 6),
                "margin_gbp": round(margin_gbp, 6),
                "consumption_kwh": round(daily_kwh, 4),
                "gas_ccl_gbp": round(gas_ccl, 8),
                "ggl_gbp": round(ggl, 8),
                "gas_policy_cost_gbp": round(gas_policy_cost, 8),
                "gas_network_cost_gbp": round(gas_network_cost, 8),
                "gas_standing_charge_gbp": round(gas_sc_gbp, 8),
                "weather_factor": round(weather_factor, 4),
                "seasonal_factor": round(seasonal, 4),
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
            # Phase 30b: deduct gas policy cost (CCL + GGL) and network charges
            # from the gross margin before computing net_margin, mirroring electricity.
            rec["net_margin_gbp"] = round(
                compute_net_margin(
                    rec["margin_gbp"]
                    - rec["gas_policy_cost_gbp"]
                    - rec["gas_network_cost_gbp"],
                    cap_per_day,
                ),
                8,
            )

    return records
