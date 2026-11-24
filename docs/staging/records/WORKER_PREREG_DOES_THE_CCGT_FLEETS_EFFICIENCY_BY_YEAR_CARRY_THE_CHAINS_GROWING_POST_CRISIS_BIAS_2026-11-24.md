**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: does the CCGT fleet's efficiency by year carry the chain's growing post-crisis bias? (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer, step 2 of the interconnector
result's "Next" list
(`docs/staging/records/WORKER_RESULT_GB_NET_EXPORT_CARRIES_THE_2022_MARKUP_BUT_LEAVES_TWO_THIRDS_OF_THE_POST_CRISIS_GAP_2026-11-24.md`).
Filed before the probe `/var/tmp/mk23/measure.py` is run. Nothing in `sim/` changes.*

## The question

On arm X (SAP, plus real net export in residual demand), the post-crisis monthly bias is +8.23, and by year
it grows: 2023 +5.6, 2024 +6.9, 2025 +11.3. The interconnector record named two candidates. This arm tests
the first one: a fleet more efficient than the engine's 0.50 constant.

## What is already known, said before the run

- **A constant efficiency cannot move anything. That is an equivalence, not a test.** The price leg is
  `floor × (a0 + a1·x + a2·kick)` with no intercept, and `floor = (gas + carbon·EF) / efficiency`. Moving
  0.50 to any other constant rescales the floor, and the refit's a0-a2 absorb it exactly. Only the
  efficiency's movement from year to year can change a monthly bias.
- **The published movement is small, and it runs the wrong way.** DUKES 5.10.C, CCGT fleet efficiency, gross
  CV (`docs/market_research/ssp_multiplant_srmc_stack_heat_rates_2026-07-25.md` §1a): 48.93, 48.69, 48.94,
  48.78, 48.44, 49.00, 49.11, **49.91**, 48.93 for 2016-2024. 2023 is the highest year of the decade, and 2024
  is back at the mean. A bias that grows from 2023 to 2025 would need efficiency rising across those years.
  It peaks at the start. 2025 is not held (DUKES 2026 edition not read). It is a **GAP**, and the arm holds
  2025 at 2024's value.
- **The size is bounded before the run.** 2023's floor falls by about 1.9% against the mean year. On a
  post-crisis floor of roughly £80-90/MWh that is about £1.5-1.7, and 2024 and 2025 barely move.

## The arm

One variable. XE is X with the floor's divisor set to each year's DUKES efficiency. That is the same as scaling
gas and carbon by 0.50 / eff(year) on each row, in the half-hourly refit and on the daily record. The control
is X, rerun in the same probe.

## Predictions

| # | Prediction |
|---|---|
| E1 | The control reproduces X: 4.89 / 17.02 / 10.38 monthly MAE, pre / crisis / post, to ±0.01 |
| E2 | Post-crisis monthly bias moves by less than £1.5 from +8.23, and stays above +6.5 |
| E3 | 2023's bias falls by £0.5-2.5. 2024's and 2025's each move by less than £1.0 |
| E4 | Pre-crisis and crisis monthly MAE each stay within ±0.5 of X's |
| E5 | The growth from 2023 to 2025 does not shrink. It widens, because 2023 falls and 2025 does not |

## Decision rule, filed now

- **(a) E2 holds: efficiency is ruled out** as the second mechanism, and the steer's candidate list loses it
  with a reason. The next arm is the other named candidate: the traded price (MID) against SSP, on X.
- **(b) The post-crisis bias falls below +6.5:** efficiency carries part of the gap. The result says how much,
  and the by-year table is shipped only once a forward efficiency source exists (2025 is a GAP).

Reverse: delete this record.
