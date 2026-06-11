# Price Engine Calibration Report — Phase 3b

## What Was Built
- `sim/price_engine.py` — the three components specified in MASTER_BACKLOG Phase 3b:
  - `gas_floor_price(gas_price, thermal_efficiency=0.50)` = `gas_price / thermal_efficiency`
  - `system_margin_price(gas_floor, demand_mw, renewable_generation_mw, gamma)` = `gas_floor * (demand/renewable_generation)^gamma`, gamma constrained to `[1.5, 2.5]`
  - `wind_power_output_fraction(wind_speed_ms, rated_power_mw)` — idealised cubic turbine power curve (cut-in 3 m/s, cubic ramp to 12 m/s, rated plateau to 25 m/s, cut-out above)
  - `synthetic_price(...)` — chains the first two for a single settlement-period price
- `sim/generation_demand_history.py` — real Elexon data ingestion for the model's inputs:
  - `/demand/outturn` (INDO/ITSDO) for `demand_mw`, fetched in 28-day chunks (API-enforced max range)
  - `/generation/actual/per-type/wind-and-solar` (AGWS) for `renewable_generation_mw` (Wind Onshore + Wind Offshore + Solar, summed), fetched in 7-day chunks (API-enforced max range)
- `simulation/run_phase3b_calibration.py` — calibration run comparing `synthetic_price()` against real SSP for two sample years (2019 calm, 2022 crisis), scanning `gamma` across `[1.5, 2.5]` in steps of 0.1
- `tests/sim/test_price_engine.py` — 15 tests covering all three formula components (boundary conditions, monotonicity, gamma validation, cubic ramp shape)

## Calibration Methodology
For each settlement period in 2019 and 2022 with all four inputs available (real SSP from `sim/cache/elexon_ssp_full.json`, `demand_mw`, `renewable_generation_mw`, and NBP `gas_price`), computed `synthetic_price()` for `gamma ∈ {1.5, 1.6, ..., 2.5}` and measured MAE, RMSE, mean bias (synthetic − actual), and Pearson correlation against actual SSP.

**Data availability**: both Elexon endpoints return no data before ~2016-03-01 (a real boundary, probed directly) — about two months into the simulation window. Periods with `renewable_generation_mw <= 0` are skipped (none occurred in either sample year). 2019: 17,226/17,520 periods matched across all four sources; 2022: 14,963/17,520 (2022 has more gaps in the AGWS dataset).

## Key Findings — Gate Does Not Clear As Specified

| Year | Actual SSP mean | Best gamma in [1.5,2.5] | MAE @ best | Bias @ best | Correlation |
|------|-----------------|--------------------------|------------|-------------|-------------|
| 2019 | £41.75/MWh | 1.5 (the floor of the allowed range) | £496.33 | +£496.20 | 0.203 |
| 2022 | £200.07/MWh | 1.5 (the floor of the allowed range) | £3,212.08 | +£3,211.95 | 0.244 |

**The formula as specified — `gas_floor * (demand_mw / renewable_generation_mw)^gamma` with raw national-MW inputs — systematically overestimates SSP by roughly 10x even at gamma=1.5, the lowest value in the spec'd range, and gets monotonically worse as gamma increases toward 2.5** (MAE reaches £8,922 at gamma=2.5 for 2019, and £56,181 for 2022). Correlation with real SSP is weak (0.1-0.3) across the whole range and *decreases* as gamma increases.

**Diagnosis**: in 2022, `gas_floor_price()` alone (median £175/MWh from NBP at thermal_efficiency=0.50) is already close to the actual SSP mean (£200/MWh) — the gas floor is doing most of the work correctly. But `demand_mw / renewable_generation_mw` has a median of 3.46 and mean of 5.20 (national demand ~26.6 GW vs wind+solar ~8.0 GW typical). Raising even this median ratio to gamma=1.5 multiplies the gas floor by ~6.4x, pushing synthetic prices into the thousands of £/MWh — far beyond real SSP, which rarely exceeds a few hundred £/MWh even during the 2022 crisis.

To confirm this isn't simply a gamma-tuning problem, I extended the gamma search down to `[0.0, 1.5]` (outside the spec'd range, for diagnostic purposes only):
- **2022**: gamma=0.0 (i.e. `synthetic_price = gas_floor`, ignoring the demand/renewable ratio entirely) is the *best fit in [0, 1.5]* — MAE £88.72 (44% of mean), bias only +£2.83.
- **2019**: gamma=0.25 is best — MAE £17.23 (41% of mean), bias −£5.41.

In other words: **the demand/renewable margin term, in its current raw-MW-ratio form, does not improve the fit over the gas floor alone — at any gamma in the spec'd range it makes the fit dramatically worse.** Even at its best (gamma≈0), the gas floor alone leaves ~40-45% MAE, so neither the floor term nor the margin term as currently formed fully explains SSP's variance.

## Wind Cubic Physics — Implemented, Not Yet Validated
`wind_power_output_fraction()` is implemented and unit-tested against the spec'd cut-in/ramp/rated/cut-out boundaries, but has **not** been validated against real wind-speed → AGWS-generation data in this pass — that validation (converting Open-Meteo wind speeds at representative locations to a power-curve estimate and comparing to AGWS Wind Onshore/Offshore output) is a separate piece of work, deferred pending direction on the margin-term redesign below (no point validating the wind-to-power conversion before the price formula that consumes it is fixed).

## Recommendation — Escalation to Rich
The `[REVIEW_GATE]` does not clear: the price engine as specified in MASTER_BACKLOG does not produce price distributions matching real SSP within any reasonable bound, for either a calm or crisis year. Before further investment, a decision is needed on how to redefine the system-margin term. Two candidate directions (not yet implemented):

1. **Normalize the ratio around its historical typical value** — e.g. `(demand/renewable) / median(demand/renewable)` so the term is ≈1 in typical conditions and only deviates when the margin is unusually tight/loose, with `gamma` then controlling sensitivity to *deviations* rather than the absolute ratio.
2. **Use a residual-demand-share formulation** — e.g. `(demand - renewable) / demand` (the fraction of demand that must be met by thermal generation), which is bounded in `[~-something, 1]` and closer in scale to a multiplier gas plants would actually apply.

Either redesign should be re-run through `simulation/run_phase3b_calibration.py` (extend to the full 2016-2025 window once a candidate formula clears this sample-year bar) before the gate is reconsidered.

## Token Efficiency
- Frontier: `price_engine.py`, `generation_demand_history.py`, `run_phase3b_calibration.py`, and the test suite — all hand-written (new physics-engine module + data ingestion, schema-defining work per the Phase 1d delegation lesson).
- Local: none this session.
- Output: one new pure module (~120 lines), one new data-ingestion module (~110 lines), one calibration script (~110 lines), 15 new tests, two real-data calibration runs (2019, 2022; ~9s combined).
