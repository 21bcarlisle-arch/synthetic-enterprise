# Phase 58 Proposal: Weather-adjusted gas consumption (heating degree days)

**The gap:** Gas consumption in the simulation uses a fixed seasonal multiplier
(`GAS_MONTH_SEASONAL_MULTIPLIER` in `sim/forward_curve.py`) that is the same every year.
In reality, UK gas demand is tightly correlated with heating degree days (HDD): a warm
winter reduces residential gas consumption by 15-25% vs the seasonal average; a cold
snap increases it. We have per-customer daily weather data in `sim/weather_data/` from
2016-2025 (Phase 1b). This is unused.

Key real-world data points:
- UK winter 2019-2020: warmest on record (HDD ~30% below average) → gas demand -20%
- UK Jan 2021: cold snap (HDD well above seasonal avg) → gas demand spike
- 2022: overall mild winter → gas consumption lower than price-implied crisis severity
- Gas consumption drives: customer bills, wholesale cost, gas policy costs, gas network costs

**What to build:**

1. `sim/weather.py` (new): `get_hdd(date_str, customer_id)` — heating degree days for one day
   at one customer's location. HDD = max(0, HDD_BASE_TEMP - mean_temp). Standard UK base 15.5°C.
   `get_monthly_hdd(year, month, customer_id)` — sum over month.
   `get_reference_monthly_hdd(month)` — 30-year UK climate normal (2001-2020 baseline) per month,
   used to compute weather_factor = actual_hdd / reference_hdd.

2. `simulation/gas_settlement.py`: add `weather_factor` param to `run_gas_term()`.
   Residential/SME gas consumption per period = base_consumption × weather_factor.
   I&C pass-through gas: weather adjustment also applies (process heat not temperature-sensitive for
   large industrial, but resi-equivalent I&C gas is heating-dominated — use customer segment to gate).
   Gate: weather adjustment only for resi and SME; I&C process gas unchanged.

3. `simulation/run_phase2b.py`: compute `weather_factor` per customer per gas term from
   `sim/weather.py`; pass into `run_gas_term()`.

4. Annual report: add weather_factor column (or % deviation from seasonal baseline) to gas P&L table.

5. Tests (~10 new):
   - `test_hdd_is_zero_above_base_temp` — warm day → HDD=0
   - `test_hdd_positive_below_base_temp` — cold day → correct HDD
   - `test_monthly_hdd_sums_days` — sum check
   - `test_weather_factor_warm_winter_below_1` — 2019-2020 London factor < 1.0
   - `test_weather_factor_cold_snap_above_1` — Jan 2021 factor > 1.0
   - `test_ic_segment_not_adjusted` — I&C process gas unchanged
   - `test_gas_term_consumption_scales_with_weather` — warm year → less gas consumed
   - `test_reference_hdd_all_months_positive` — climate normals are sensible
   - `test_weather_factor_clipped_to_sane_range` — no factor > 2.0 or < 0.3
   - `test_gas_consumption_2020_below_2018` — warm 2019-2020 winter suppresses demand

**Expected impact:** Year-to-year gas consumption now varies with actual UK weather. The
2019-2020 warm winter reduces gas costs and bills; the Jan 2021 cold snap increases them.
Resi gas customers see weather-driven bill variance. Margin on fixed-rate gas is higher in
warm years (supplier locked in price, consumption lower = lower cost but revenue same).
Adds the "weather is a real business driver" dimension that was always in the backlog.

**Files changed:** `sim/weather.py` (new), `simulation/gas_settlement.py`,
`simulation/run_phase2b.py`, `saas/reporting/annual_report.py`,
`tests/sim/test_weather_hdd.py` (new), ~10 tests.
