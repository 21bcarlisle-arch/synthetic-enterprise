# Phase 144 -- Gas Daily Balancing and Nomination Model

**Status:** PROPOSED (2026-06-26)

Every UK gas shipper must nominate daily gas quantities to Xoserve (UNC obligations).
If actual demand exceeds nomination, the company is short and buys the difference at
within-day NBP spot. This drove supplier failures in 2021-22 (NBP hit 10 GBP/therm).
Completely absent from the current model.

## Design: company/market/gas_nominations.py

DailyNomination(date, gas_account_id, nominated_kwh, actual_kwh, nbp_spot_gbp_per_therm)

GasNominationBook:
- nominate(nom) -> record a days nomination vs actual
- imbalance_kwh(date, account) -> actual - nominated (negative = short)
- cash_out_cost_gbp(date, account) -> short pays spot; long gets 0.85x credit
- nomination_accuracy_pct() -> pct days within +-5% of actual
- monthly_cashout_gbp(year, month) -> aggregate imbalance cost
- annual_cashout_gbp(year) -> annual rollup
- worst_imbalance_periods(n=5) -> top-n cash-out events
- balancing_summary() -> accuracy, total_cashout, period count

Short cost: imbalance_kwh / 29.31 * nbp_spot_gbp_per_therm
Long credit: imbalance_kwh / 29.31 * nbp_spot_gbp_per_therm * 0.85

2022: 1000 kWh short at 3.50 GBP/therm = 119 GBP. 2016 at 0.35 GBP/therm = 12 GBP.

~10 tests. Closes the last major daily operational gap in the company layer.
