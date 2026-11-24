**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the price leg's post-crisis miss is a level, not a shape; a non-gas constant helps every regime but leaves it £5.6 low (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in
`docs/staging/records/WORKER_PREREG_THE_PRICE_LEGS_SHAPE_ARM_A_NON_GAS_CONSTANT_AND_A_LOW_X_DEPTH_AGAINST_ITS_POST_CRISIS_LEVEL_2026-11-24.md`
(`8e2faf1a3`), which was promoted to origin before the probe ran. Probe `/var/tmp/wpc_shape/measure_s.py`, sha256
`9d53c7cd…`, unchanged. Run in a worktree at `8e2faf1a3`. Output `/var/tmp/wpc_shape/out_s.json`.
**Nothing in `sim/` changes.***

## Outcomes (the leg alone, on real daily x; monthly, demand-weighted, £/MWh: MAE / bias)

| Form | Coefficients | HH MAE | Pre | Crisis | Post | Post without 2025 |
|---|---|---|---|---|---|---|
| R L0 (control) | 0.2918 / 1.0790 / 2.8276 | 31.53 | 5.48 / −3.11 | 14.62 / −3.33 | 9.84 / −7.99 | 8.03 / −5.57 |
| R L1 + b0 | … / b0 £5.80 | 31.73 | **4.82** / +0.82 | **13.62** / −5.29 | 8.36 / −5.64 | 6.74 / −3.12 |
| R L2 + low-x depth | … / a3 −0.78 | 31.47 | 5.33 / −3.32 | 15.40 / −2.45 | 9.69 / −7.92 | 7.59 / −5.23 |
| R L3 both | … / a3 −0.90, b0 £6.20 | 31.70 | 4.64 / +0.84 | 13.81 / −4.42 | **8.16** / −5.40 | 6.24 / −2.58 |
| W L0 (control) | 0.2732 / 1.0534 / 3.0214 | 31.95 | 5.07 / −2.26 | 17.26 / −6.33 | 7.76 / −7.24 | 7.95 / −7.28 |
| W L1 + b0 | … / b0 £5.13 | 32.13 | 4.84 / +1.19 | 15.62 / −8.00 | 6.27 / −5.16 | 6.29 / −5.08 |
| W L2 + low-x depth | … / a3 −1.00 | 31.86 | 4.98 / −2.57 | 17.90 / −5.23 | 7.31 / −6.71 | 7.44 / −6.65 |
| W L3 both | … / a3 −1.08, b0 £5.40 | 32.07 | 4.64 / +1.04 | 16.10 / −6.89 | 5.70 / −4.49 | 5.66 / −4.29 |

XL (the window median of half-hourly real x) is 0.598 on R and 0.634 on W. The fit uses the 157,010 common half-hours.

**Bias by year (R L0 → R L3):**

| Year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| R L0 | −4.67 | −0.97 | −0.09 | −2.29 | −5.91 | −8.45 | +3.25 | −10.53 | −2.68 | −15.25 |
| R L3 | −0.48 | +2.89 | +3.07 | +1.85 | −1.10 | −7.29 | +0.79 | −8.36 | +0.30 | −13.89 |
| W L0 | −2.98 | +0.28 | +1.08 | −2.18 | −5.90 | −8.29 | +1.73 | −14.55 | −5.36 | −7.10 |

| # | Prediction | Outcome |
|---|---|---|
| S-P0 | L0 reproduces the leg-on-real rows within £0.01, and `synthetic_price` within £1e-6 a day | **Held.** All twelve cells identical; max daily difference 1.1e-13 |
| S-P1 | L1's b0 positive and below £10; R pre bias up by at least £1 | **Held.** b0 £5.80 (R) and £5.13 (W); pre bias −3.11 → +0.82 |
| S-P2 | L1's R post bias stays at or below −£5 | **Held.** −5.64 |
| S-P3 | L2's a3 negative on both bases | **Held.** −0.78 (R), −1.00 (W) |
| S-P4 | L2 moves each R MAE by less than £1.0 | **Held.** −0.15, +0.78, −0.15 |
| S-P5 | No form takes the R post bias inside ±£3 | **Held.** −5.64, −7.92, −5.40 |
| S-P6 | Every form's half-hourly MAE within 2% of L0's | **Held.** Largest move +0.6% |

Seven of seven held.

## What the rule says

- **(b) fires: the post-crisis gap is a level, not a shape. Nothing ships.** No form brings the R post bias
  inside ±£3. The best is L3 at −5.40.
- **The low-x depth (L2) is real in sign and small in effect.** a3 is negative on both bases, so the bottom is
  deeper than the linear form draws. But L2 alone moves no regime's R bias by more than £0.9, and it worsens the
  crisis MAE by £0.78. This agrees with the electricity page §1b. Read at a given amount of gas running, the
  record's ratio to the floor does not change across regimes, so the shape has little left to fix.

## What it shows beyond the rule

- **A constant that does not scale with gas, of about £5-6/MWh, lowers monthly MAE in every regime on both bases**
  (R: −0.66, −1.00, −1.48), while the half-hourly MAE rises by 0.6%. The OLS minimises squared half-hourly error,
  which the crisis half-hours dominate. The monthly MAE is a different loss. This is the electricity page §1b's
  "wear part does not scale with gas" in size, but **I cannot yet say** that it is wear and not a fit artefact.
  It is a candidate for the build only after the level gap below is placed, because a constant would also absorb
  part of that gap.
- **The post-crisis level is not one level.** On R L0 it is 2023 (−10.5) and 2025 (−15.3), with 2024 at −2.7.
  2021 is −8.5 on every form and both bases. 2021 and 2023 are the years the gas price moved fastest, into the
  crisis and out of it. That is consistent with an INPUT that lags, such as the gas series the record carries
  against the daily SAP splice. It is a candidate, not an attribution. 2025 differs by £8 between bases (R −15.3,
  W −7.1), so part of 2025 is the R basis's residual. 2025 is also the year whose fleet the end-year clamp arm
  could not match.

## Next

1. **The leg's inputs, by year, before any build** (rule (b)): the record's gas price against the daily SAP splice,
   and carbon, in 2021, 2023 and 2025. Pre-register the attribution with the R L0 by-year biases above as its
   control. Then the build-terms rerun can carry the L1 constant as a named candidate, not as a fit.
2. Unchanged: the end-year clamps on a FUELHH-basis fleet (`acc387cbe`'s Next 2), then rerun B1-B3.

Reverse: delete this record.
