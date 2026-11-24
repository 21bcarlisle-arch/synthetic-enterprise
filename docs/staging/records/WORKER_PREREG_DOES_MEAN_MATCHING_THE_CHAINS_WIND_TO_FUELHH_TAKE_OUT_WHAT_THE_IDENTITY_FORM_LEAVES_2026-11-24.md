**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: does mean-matching the chain's wind to FUELHH instead of AGWS take out what the identity form leaves of its gas-running miss (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is the second "Next" of the gas-running arm's result,
`docs/staging/records/WORKER_RESULT_A_DEMAND_YEAR_TERM_TAKES_HALF_THE_CHAINS_GAS_RUNNING_MISS_AND_THE_IDENTITY_FORM_LEAVES_1_9_GW_UNEXPLAINED_2026-11-24.md`.
Filed and landed before the probe runs. **Nothing in `sim/` changes.***

## The question

G4, the identity form on the chain's residual with demand by year, must-run by year and solar out, still runs
+1.86 GW more gas than the record after the crisis (+1.62 GW without 2025). §4a of the electricity page found
that the chain's wind is mean-matched to AGWS, and AGWS wind is not FUELHH wind. The identity that closes on
the record (R² 0.993-0.998) uses FUELHH. Does moving the wind leg's target from AGWS to FUELHH, and changing
nothing else, take out the rest?

## What is seen before the run (inputs only, disclosed)

AGWS and FUELHH wind means by calendar year, on the chain's own record days (FUELHH days with at least 46
periods). s_y = FUELHH / AGWS, in `/var/tmp/wtp_worker/s_y.json`:

| Year | AGWS GW | FUELHH GW | s_y |
|---|---|---|---|
| 2016 | 3.111 | 2.259 | 0.726 |
| 2017 | 4.262 | 3.707 | 0.870 |
| 2018 | 4.745 | 4.467 | 0.942 |
| 2019 | 5.134 | 5.300 | 1.032 |
| 2020 | 6.102 | 6.226 | 1.020 |
| 2021 | 5.665 | 5.541 | 0.978 |
| 2022 | 6.548 | 7.066 | 1.079 |
| 2023 | 5.895 | 7.237 | 1.228 |
| 2024 | 6.120 | 7.473 | 1.221 |
| 2025 (to 7 Jun) | 9.005 | 7.313 | 0.812 |

These by-year gaps are larger than §4a's regime means (AGWS −0.36 GW post). The windows differ: §4a used every
FUELHH day, and this uses the chain's record days. Why AGWS and FUELHH part is still GAP 9 of that page. This
arm does not answer it.

## The probe

`/var/tmp/wtp_worker/measure_w.py`, sha256 `0847aa93e067ddf069d8157f71cde1110699816f8b39fff7c9b47cd3a3327aba`.
It is `/var/tmp/mk27/measure_g.py` (sha256 `75553019...`) unchanged except for its docstring and two arms
added after G4:

- **W0** sets s_y = 1 for every year. It is the control and must reproduce G4.
- **W1** rescales the chain's wind (renewable minus the chain's solar) each year by s_y. It then refits the
  identity offset k on pre-crisis days only, as G4 does.

Run from a worktree at this commit, with `sim/cache` present.

## Predictions, filed before the run

The arithmetic: W1 changes the residual by −(s_y − 1) × the chain's wind. That is about +0.3 GW on pre-crisis
days, which k absorbs, and about −0.7 GW on post-crisis days (2023-24 at −1.35, 2025 at +1.69). Post, c_hat
should fall by about 0.9 GW; without 2025, by about 1.6 GW. The price conversion, about £2.4/MWh per GW, is
read off G1 (1.39 GW moved the bias £3.31). It is an approximation, not a fit.

| # | Prediction |
|---|---|
| W-P0 | W0 reproduces G4: post +1.86 GW, post composite 10.79 / +10.39, crisis composite bias +1.67, pre daily R² 0.493 |
| W-P1 | W1 post c_hat − c in [+0.6, +1.3] GW |
| W-P2 | W1 post without 2025 in [−0.4, +0.4] GW |
| W-P3 | W1 crisis c_hat − c is 0.4 to 1.2 GW below G4's, and the crisis composite bias is below +1.67 |
| W-P4 | W1 pre daily R² within ±0.03 of 0.493 |
| W-P5 | W1 post days with c_hat under 6 GW in [100, 170] (record 241, G4 79) |
| W-P6 | W1 post composite bias in [+7.0, +9.5], and MAE ≤ 10.0 |

## Decision rule, filed before the run

- **(a) The target is the wind leg's defect.** Fires if W-P1 and W-P2 hold and W-P4 holds. The chain's wind
  fleet becomes mean-matched to FUELHH by year: a build term, landed together with solar out of the residual
  (the identity needs both). 2025's sign flip is reported beside it, not averaged away.
- **(b) The target is not the source.** Fires if the post miss falls by less than 0.4 GW. The next candidate is
  the chain's demand inside each year (the temperature-only leg, R² about 0.55).
- **(c) Partial.** Anything else. Report by year (post hoc, labelled), and do not build.
- **Void.** If W-P0 fails, the probe is not the G4 probe, and no W1 outcome is read.

Reverse: delete this record.
