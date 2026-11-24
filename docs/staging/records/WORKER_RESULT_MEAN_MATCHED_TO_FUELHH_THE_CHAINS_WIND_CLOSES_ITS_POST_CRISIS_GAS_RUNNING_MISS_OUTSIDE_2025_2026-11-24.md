**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: mean-matched to FUELHH instead of AGWS, the chain's wind closes its post-crisis gas-running miss outside 2025 (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in
`docs/staging/records/WORKER_PREREG_DOES_MEAN_MATCHING_THE_CHAINS_WIND_TO_FUELHH_TAKE_OUT_WHAT_THE_IDENTITY_FORM_LEAVES_2026-11-24.md`
(`5b1589639`), which was promoted to origin before the probe ran. Probe `/var/tmp/wtp_worker/measure_w.py`, sha256
`0847aa93...`, unchanged. It was run in a worktree at `5b1589639`. Output is `/var/tmp/wtp_worker/out_w.json`.
**Nothing in `sim/` changes.***

## Outcomes (c_hat − c in GW; composite in £/MWh, monthly, demand-weighted)

| Arm | k | Pre R² | Crisis c_hat − c / bias | Post c_hat − c | Post without 2025 | Post days < 6 GW (record 241) | Post composite MAE / bias | Post without 2025, MAE / bias |
|---|---|---|---|---|---|---|---|---|
| G4 | −0.614 | 0.493 | +0.71 / +1.67 | +1.86 | +1.62 | 79 | 10.79 / +10.39 | 9.68 / +9.15 |
| W0 (control) | −0.614 | 0.493 | +0.71 / +1.67 | +1.86 | +1.62 | 79 | 10.79 / +10.39 | 9.68 / +9.15 |
| **W1** | −0.335 | **0.513** | **−0.12 / −1.71** | **+0.71** | **−0.02** | 179 | **9.41 / +8.29** | **7.33 / +5.83** |

For reference, leg P on real gas running gives 6.97 / +6.16 post and 6.45 / +5.79 post without 2025.

| # | Prediction | Outcome |
|---|---|---|
| W-P0 | W0 reproduces G4 | **Held**, to every printed figure |
| W-P1 | Post in [+0.6, +1.3] GW | **Held.** +0.71 |
| W-P2 | Post without 2025 in [−0.4, +0.4] GW | **Held.** −0.02 |
| W-P3 | Crisis 0.4-1.2 GW below G4, and crisis bias below +1.67 | **Held.** 0.83 GW lower; bias −1.71 |
| W-P4 | Pre R² within ±0.03 of 0.493 | **Held.** 0.513 |
| W-P5 | Post days under 6 GW in [100, 170] | **Wrong.** 179, all of them in 2023-24 (179 of the record's 193 there), and none in 2025 (the record has 48) |
| W-P6 | Post bias in [+7.0, +9.5], MAE ≤ 10.0 | **Held.** +8.29, 9.41 |

## What the rule says

- **(a) fires.** W-P1, W-P2 and W-P4 hold. The chain's wind target is the defect behind what the identity form
  left. Mean-matched to the transmission-metered series that the identity uses, the chain's gas running is
  unbiased after the crisis outside 2025 (−0.02 GW). It is unbiased in the crisis too (−0.12 GW), and the
  pre-crisis fit improves.
- **The build term:** the chain's per-year wind fleet is mean-matched to FUELHH wind instead of AGWS. It lands
  with solar out of the residual, because the identity needs both, and with the demand year term. The demand
  term waits on the curriculum's joint demand-and-fleet band (§8a of the electricity page), so on the record
  it is the year's ND.
- **2025, reported beside it rather than averaged away.** 2025's 158 days carry about +3.25 GW of miss [calc
  from the two post rows]. That accounts for the whole of W1's +0.71 post figure. In 2025 AGWS wind runs above
  FUELHH (s = 0.81, the only post-crisis year below 1), and the renewable fleet is clamped to 2024. Both are
  candidates, and neither is attributed.
- **What is left is the price leg.** Outside 2025, W1's composite post bias (+5.83) is within £0.04 of leg P
  on REAL gas running (+5.79). Gas running is now right on average, so the remaining post-crisis bias is the
  floor multiple on low-gas days. That is the separating arm's shape question (§1b), and it now returns as
  the next arm.

## Caveats

- **s_y is in-sample.** It uses each record year's own FUELHH wind, as the chain's per-year fleet already does
  with AGWS. A forward year needs a FUELHH-basis fleet path, which is curriculum.
- **Why AGWS and FUELHH part is still GAP 9** of the electricity page. This arm shows which of the two the
  identity needs. It does not show why they differ.
- **W-P5's overshoot:** the arm now runs gas under 6 GW on 179 of 193 such record days in 2023-24, so the low tail
  is about right there. 2025 has none against 48. That is the same 2025 term.

## Next

1. **Build** (rule (a)): in `sim/weather_price_chain`, the wind fleet mean-matched to FUELHH by year, solar out
   of the residual, and the demand year term on the record. It needs one-variable predictions filed before the
   change, and the step-B constants re-fitted on the new residual.
2. **2025:** the AGWS-above-FUELHH flip and the clamped fleet, one at a time.
3. **The price-leg shape arm** (§1b), now that gas running is right on average.

Reverse: delete this record.
