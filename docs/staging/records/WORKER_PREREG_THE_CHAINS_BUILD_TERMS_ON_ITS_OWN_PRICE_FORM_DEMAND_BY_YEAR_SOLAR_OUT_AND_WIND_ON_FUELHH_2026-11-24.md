**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: the chain's build terms on its own price form, with demand by year, solar out and wind on FUELHH (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is Next 1 of the wind-target arm's result,
`docs/staging/records/WORKER_RESULT_MEAN_MATCHED_TO_FUELHH_THE_CHAINS_WIND_CLOSES_ITS_POST_CRISIS_GAS_RUNNING_MISS_OUTSIDE_2025_2026-11-24.md`
(`9ed9bdfa7`). Filed and landed before the probe runs. **Nothing in `sim/` changes.***

## Why an arm and not the build directly

The arms that named these three terms (G0-G4, W0-W1) were measured on a TWO-leg form. Leg H maps the residual
to CCGT GW, and leg P maps CCGT GW to price. `sim/weather_price_chain` does not ship that form. It ships
`price_engine`'s ONE-leg form: x = (demand − renewable) / 35,000 MW, and price = floor × (A0 + A1·x +
A2·max(0, x − 0.70)²), with A0-A2 refitted on the half-hourly record with carbon in the floor. Whether the
terms help the shipped form is a separate question, and the build waits on it.

## Design (one variable per arm, cumulative)

| Arm | Chain side | Price leg (half-hourly real x) | Refit |
|---|---|---|---|
| B0 | as shipped | (INDO − AGWS wind − AGWS solar)/cap | none: shipped A0-A2 |
| B1 | + demand year term Δ_y | unchanged | none (INDO already carries each year's level) |
| B2 | + solar out of the residual | (INDO − AGWS wind)/cap | A0-A2 |
| B3 | + wind × s_y (FUELHH basis) | (INDO − FUELHH WIND)/cap | A0-A2 |

- **Δ_y** is the mean INDO minus the mean chain demand over each year's record days. **s_y** is the FUELHH
  wind mean over the AGWS wind mean by year, the file the wind-target arm used. Both are in-sample by year,
  like the per-year wind fleet the chain already ships.
- **Must-run by year is NOT in this build.** In the shipped form, nuclear sits in the fixed 35 GW
  denominator, and the refit absorbs a constant must-run. Its by-year fall of 2.7 GW is the one G4 term
  left out. The result names it if a by-year trend survives B3.
- **The construction check:** in B3, the chain's mean x by year should equal the record's mean x on the W
  basis. The demand term matches INDO's mean, and the wind fleet times s_y matches FUELHH's mean. Both
  sides exclude solar.
- **Diagnostic:** for each basis, the price leg run on REAL daily x (no chain). This is the leg's own error.

## Seen before the run (disclosed)

- **B0 control** (`b0.py`), monthly demand-weighted MAE / bias: pre 6.50 / −5.29, crisis 17.20 / +2.39,
  post 8.19 / +1.84, and post without 2025 8.12 / +0.18. Bias by year: 2016 −9.17, 2017 −4.56, 2018 −4.32,
  2019 −3.85, 2020 −4.99, 2021 −8.79, 2022 +13.19, 2023 −4.11, 2024 +1.89, 2025 +6.81.
- **Δ_y (MW):** 2016 +2,665, 2017 +2,157, 2018 +1,788, 2019 +918, 2020 −1,018, 2021 −115, 2022 −1,369,
  2023 −2,002, 2024 −1,675, 2025 −2,270. The chain's demand has no year term, so it runs 2 GW too high
  after the crisis and 2.7 GW too low in 2016.
- **Linearised hand calculation** (`linear_calc.py`, not the arm): dP = floor × (A1 + A2·dkick/dx) × Δ_y /
  cap at each day's own floor and x. This is B1's first-order move. By year: +3.0, +3.2, +3.5, +1.3, −1.1,
  −0.4, −10.9, −6.8, −4.5, −8.4. By regime: pre +1.74, crisis −7.48, post −5.69, post without 2025 −4.91.

**The hypothesis this tests:** B0's post-crisis bias sits near zero (+0.18 without 2025) because two errors
cancel. Demand runs about 2 GW too high, and the price leg is too low after the crisis. If so, the demand
term should expose a negative post-crisis leg bias, and the leg-on-real diagnostic should show it directly.

## Predictions

| # | Prediction |
|---|---|
| B-P0 | B0 reproduces the shipped chain (max abs daily difference < £0.01) and `fit_price_leg` (A0-A2 to 4 dp on the full row set) |
| B-P1 | B1 pre bias in [−4.5, −2.8]; crisis bias in [−8, −2]; post bias in [−6, −2]; post without 2025 bias in [−7, −3] |
| B-P2 | B1 pre MAE in [5.0, 6.3], below B0; post MAE in [8.5, 11.0], above B0 |
| B-P3 | B2 moves each regime's bias by under £1.5 and each MAE by under £1.0 from B1 |
| B-P4 | B3 construction check: \|chain mean x − record mean x\| < 0.01 in every year |
| B-P5 | B3 pre-crisis bias range over 2016-2020 (max − min) < £4.0 (B0: 5.32) |
| B-P6 | B3 post bias in [−8, −1]; crisis MAE ≤ 17.20; pre MAE ≤ 6.50 |
| B-P7 | The leg on real W-basis inputs has a post-crisis bias ≤ −2 (the cancellation hypothesis) |

## Decision rule

- **(a) Ship B3's three terms** (with the B3 refit, as one change, landed with tests) if B-P4 holds and
  B3's pre and crisis monthly MAE are each no more than £0.5 above B0's, AND post MAE is no more than £1.5
  above B0's.
- **(b) Hold the build** if post MAE worsens by more than £1.5 and B-P7 holds. The demand term then exposes
  the price leg's post-crisis level. The next arm is the leg's shape (§1b of the electricity page), and the
  build ships with it, because shipping a correct demand on a leg that only worked by cancelling would
  make forward years worse.
- **(c) Attribute before shipping** if B2 or B3 moves any regime's MAE by more than £2 against the arm
  before it. That is not the small effect expected.
- If B-P4 fails, the result is about the construction, not the price, and nothing ships.

## Probe

`/var/tmp/wpc_build/measure_b.py`, sha256 `24eaceab…2ea17074`. Its inputs are `/var/tmp/wpc_build/b0_out.json`
(`0111b0e4…`) and `/var/tmp/wtp_worker/s_y.json` (`f7299380…`). It runs in a worktree at origin/main with
`sim/cache` linked.

Reverse: delete this record.
