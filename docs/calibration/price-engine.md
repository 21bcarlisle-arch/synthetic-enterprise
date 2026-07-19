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

---

## Addendum — Redesign: Statistical Regression Model (2026-06-11)

Per direction from Rich, the merit-order physics model above is **deferred to
Regime 3** (see `docs/instructions/MASTER_BACKLOG.md` Phase 3b) — `sim/price_engine.py`
and its 15 tests remain in the repo (correct and tested in isolation), but are
no longer the active Phase 3b deliverable. The replacement deliverable is a
statistical regression model, fit directly on real data.

### What Was Built
- `sim/generation_demand_history.aggregate_wind_generation()` — new function,
  sums AGWS quantity across Wind Onshore + Wind Offshore only (excludes Solar),
  returning `{(date, period): wind_mw}`.
- `sim/prefetch_demand_generation.py` — one-off prefetch of full-window
  (2016-03-01..2025-06-07) demand/outturn and AGWS records to
  `sim/cache/elexon_demand_full.json` (161,536 records) and
  `sim/cache/elexon_agws_full.json` (474,726 records), so the regression
  doesn't re-fetch ~600 API requests on every run.
- `simulation/run_phase3b_regression.py` — fits an OLS regression of
  `SSP ~ gas_price + demand_mw + wind_mw` (intercept included) via
  `numpy.linalg.lstsq`, on every settlement period 2016-03-01..2025-06-07
  with all four real inputs available (157,106 of 165,386 periods in the
  simulation window — the gap is the pre-2016-03-01 AGWS/demand data
  boundary documented in `generation_demand_history.py`).
- `tests/sim/test_generation_demand_history.py` — 2 new tests for
  `aggregate_wind_generation` / `aggregate_renewable_generation`.
- `tests/simulation/test_run_phase3b_regression.py` — 2 new tests for
  `_fit_ols` (exact recovery of a known linear relationship; MAE/R^2 sanity
  on an imperfect fit).

### Methodology
Features: `gas_price` (NBP daily £/MWh), `demand_mw` (national
`initialDemandOutturn`), `wind_mw` (Wind Onshore + Wind Offshore AGWS,
excluding Solar — isolating wind specifically per the brief). Target: real
SSP (`sim/cache/elexon_ssp_full.json`). Fit by ordinary least squares
(`numpy.linalg.lstsq`, closed-form normal equations) — sklearn is not
installed in this environment.

### Results — Full Window (2016-03-01..2025-06-07, n=157,106)

| Metric | Value |
|---|---|
| SSP mean | £77.19/MWh |
| SSP std dev | £92.04/MWh |
| Intercept | -44.76 |
| coef(gas_price) | +1.8897 |
| coef(demand_mw) | +0.002521 |
| coef(wind_mw) | -0.001145 |
| **MAE** | **£33.96/MWh** |
| RMSE | £72.13/MWh |
| **R^2** | **0.3858** |

### Results — Per-Year Refit (shows fit quality across regimes)

| Year | n | SSP mean £ | MAE £ | RMSE £ | R^2 |
|---|---|---|---|---|---|
| 2016 | 14,484 | 39.32 | 20.07 | 44.21 | 0.0810 |
| 2017 | 17,169 | 44.40 | 17.69 | 29.56 | 0.1098 |
| 2018 | 17,305 | 57.27 | 18.55 | 28.66 | 0.1052 |
| 2019 | 17,226 | 41.75 | 16.40 | 20.51 | 0.1805 |
| 2020 | 16,576 | 34.79 | 17.45 | 34.18 | 0.1419 |
| 2021 | 16,833 | 115.06 | 48.29 | 130.72 | 0.1752 |
| 2022 | 14,963 | 200.07 | 81.30 | 127.63 | 0.2950 |
| 2023 | 17,457 | 94.56 | 42.17 | 53.99 | 0.2693 |
| 2024 | 17,523 | 71.14 | 27.78 | 35.60 | 0.2707 |
| 2025 | 7,570 | 89.85 | 32.43 | 100.10 | 0.1251 |

### Interpretation
The regression is a dramatic improvement over the physics model — coefficients
have sensible signs and magnitudes (gas_price coefficient ≈1.89 is close to
the merit-order intuition of "SSP tracks gas price roughly 1:1 to 2:1 via
thermal efficiency", demand has a small positive effect, wind a small negative
effect, both physically plausible). MAE of £33.96/MWh against a mean of
£77.19/MWh (≈44% relative error) and R^2≈0.39 mean the model explains a
meaningful share of variance but leaves substantial unexplained residual —
expected for a 3-feature linear model of a market also driven by carbon
prices, interconnector flows, plant outages, and non-linear merit-order
effects (price spikes are not linear in the inputs, as the per-year table
shows: fit is weakest in 2016 (low-variance year, R^2=0.08) and strongest in
2022 (the gas-crisis year, R^2=0.295), where gas price dominates).

### Status
This regression model is the active Phase 3b/Regime 2 deliverable for
synthetic SSP generation beyond the historical window. It has not been
tuned further (no feature transforms, interactions, or non-linear terms) —
that is left as a documented option for a future iteration if forward
projections built on it prove materially miscalibrated.

---

## Addendum — Recalibration of the physics engine (2026-07-19, Epoch-2)

Per director instruction (Epoch-2 campaign, "recalibrate the wholesale price engine
`sim/price_engine.py` to fix its documented ~10x SSP overestimate"), the merit-order physics model
above (deferred to Regime 3 in the 2026-06-11 addendum) was revisited and **structurally fixed** —
this is a BASELINE FIDELITY correction, decided blind to company P&L (R12/R13). The engine remains
gated off in every production phase, so this changes only a generative code path nothing currently
reads — it cannot perturb current results.

**Two root causes, both addressed:**
1. **No carbon term in the gas floor.** `gas_floor_price()` now takes an optional
   `carbon_price_gbp_per_tonne` parameter (default 0.0, back-compat-preserving):
   `P_gas_floor = (gas_price + carbon_price * EF_GAS_TCO2_PER_MWH_TH) / thermal_efficiency`,
   `EF_GAS_TCO2_PER_MWH_TH = 0.184` tCO2/MWh(th) (R10 simplification — DESNZ/DEFRA convention).
2. **The raw demand/renewable ratio form is replaced with a residual-demand scarcity form.**
   `system_margin_price()` no longer computes `(demand/renewable)^gamma` (which had median ratio
   ~3.46, exploding the gas floor 6.4x even at gamma=1.5 — the diagnosed root cause of the original
   ~10x overestimate). It now computes:
   ```
   RD = demand_mw - renewable_generation_mw
   x  = RD / DISPATCHABLE_CAPACITY_MW   (~35,000 MW, GB dispatchable fleet, R10 simplification)
   multiplier = A0 + A1*x + A2 * max(0, x - X_TIGHT) ** SCARCITY_EXPONENT
   ```
   fit against the full real 2016-03-01..2025-06-07 window (n=157,106) via
   `simulation/run_phase3b_recalibration.py`: `A0=0.326998, A1=1.334629, A2=3.828327,
   X_TIGHT=0.70, SCARCITY_EXPONENT=2.0`.

**Data-quality finding surfaced during this recalibration:** `sim/generation_demand_history.py`'s
`aggregate_renewable_generation()`/`aggregate_wind_generation()` sum every AGWS record matching a
key across *all* revision publishes — a handful of heavily-republished settlement periods (3 of
471,453 keys have 50+ duplicate publishes, one has 564) produce a summed renewable figure in the
hundreds of thousands to millions of MW, physically impossible (GB's entire wind+solar fleet is
under 30 GW) and a severe leverage outlier for least-squares fitting. `run_phase3b_recalibration.py`
dedupes to the latest `publishTime` per `(settlementDate, settlementPeriod, psrType)` before
summing (max renewable figure drops from 1,480,897 MW to a physically sane 28,456 MW). This is a
real bug in the shared aggregator, not fixed there in this pass (out of this atom's file_scope) —
logged as a finding for a future touch of `generation_demand_history.py`.

**Result — the gate clears against the hard bar:**

| Metric | Target band | Achieved |
|---|---|---|
| Median | £40-70 | £48.75 |
| Mean | £65-90 | £69.24 |
| P95 | £180-270 | £217.15 |
| Min | negative | -£10.47 (capability confirmed; magnitude/frequency gap named) |
| MAE | ≤ £34/MWh | **£32.79/MWh** |
| R² | (informational) | 0.4190 (beats both the £35.78-MAE naive gas-floor baseline and the £33.96-MAE / R²=0.3858 OLS regression above) |

Full fitted constants, per-year table, lift-over-naive-baseline analysis, honesty notes on the
negative-price frequency/magnitude gap, and every R10 simplification's provenance:
`docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md`. This 2026-06-11 addendum's OLS regression
report above is preserved unchanged as the record of what was tried before the physics form was
fixed — it remains the active Regime-3 deliverable; the recalibrated physics engine is a validated
but **not yet wired-in** alternative (no live consumer, no coupled-triad company-side test yet).
