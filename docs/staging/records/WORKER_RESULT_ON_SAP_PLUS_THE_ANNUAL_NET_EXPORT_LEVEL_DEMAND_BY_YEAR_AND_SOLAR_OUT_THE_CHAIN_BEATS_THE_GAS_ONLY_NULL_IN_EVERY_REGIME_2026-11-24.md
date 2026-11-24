**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: on SAP plus the annual net-export level, demand by year and solar out, the chain beats the gas-only null in every regime (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in
`docs/staging/records/WORKER_PREREG_THE_BUILD_TERMS_RERUN_ON_SAP_PLUS_THE_ANNUAL_NET_EXPORT_LEVEL_2026-11-24.md`
(`df7cd4297`), which was pushed to origin before arms C1-C4 ran. Probe `/var/tmp/wpc_c/measure_c.py`, sha256
`36d656b8…`, unchanged. Run in a clean worktree at origin `27f086748`. Output `/var/tmp/wpc_c/out_c.json`.
**Nothing in `sim/` changes.***

## Outcomes (monthly, demand-weighted, £/MWh: MAE / bias)

| Arm | Pre | Crisis | Post | Post without 2025 |
|---|---|---|---|---|
| C0 control (= G2) | 4.77 / −0.35 | 20.88 / −4.09 | 13.00 / +12.28 | 11.71 / +10.76 |
| C1 + net export, year mean | 4.67 / −1.39 | 20.67 / −1.67 | 9.03 / +7.10 | 8.73 / +6.15 |
| C2 + demand year term | 5.06 / +0.02 | 19.92 / −6.96 | 7.43 / +2.70 | 7.38 / +2.21 |
| **C3 + solar out** | **4.22** / −0.00 | **16.81** / −7.96 | **6.18** / +2.51 | 5.47 / +1.71 |
| C4 + wind on FUELHH | 4.57 / +0.86 | 16.89 / −8.37 | 6.58 / +1.59 | 5.37 / −0.58 |
| null_S (daily OLS on SAP) | 4.97 / −1.03 | 17.44 / −9.45 | 9.84 / +8.89 | 9.03 / +9.03 |
| null_T (daily OLS on TTF) | 5.42 / +1.81 | 24.53 / −9.54 | 6.67 / +0.70 | 4.81 / +1.46 |
| Leg on real x, AGWS w+s | 4.45 / +0.29 | 16.16 / −6.01 | 5.58 / −0.91 | 4.64 / +1.33 |
| Leg on real x, AGWS wind | 4.21 / +0.29 | 15.22 / −6.49 | 5.03 / −0.48 | 4.62 / +1.35 |
| Leg on real x, FUELHH wind | 4.58 / +1.16 | 15.32 / −7.76 | 4.16 / −0.30 | 3.97 / −0.08 |

**Bias by year:**

| Year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| C0 | −5.44 | +0.02 | +2.09 | +1.14 | −0.66 | −1.62 | −10.70 | +8.65 | +11.68 | +16.86 |
| C3 | −3.38 | +1.85 | +3.73 | +0.79 | −2.47 | −7.18 | −8.92 | −0.76 | +2.41 | +4.91 |
| C4 | −1.90 | +3.09 | +4.90 | +1.08 | −2.25 | −5.73 | −9.35 | −3.37 | +0.22 | +8.07 |

**Refits** (A0 / A1 / A2, half-hourly MAE): R0 0.5170 / 0.9296 / 1.3960, 30.99. R 0.5492 / 0.9365 / 2.1667, 30.85.
S 0.5120 / 0.9416 / 2.0671, 31.15. W 0.5088 / 0.9660 / 2.0640, 31.18.

## Predictions against outcomes

| # | Prediction | Outcome | |
|---|---|---|---|
| C-P1 | C1 pre within 4.77 ± 0.75; post bias in [+6, +10.5]; crisis MAE in [16.5, 20.5] | 4.67; +7.10; **20.67** | **missed**, on the crisis leg by £0.17 |
| C-P2 | C2 \|x gap\| < 0.012 in 2017-24; 2025 > +0.10 | max 0.0082; 2025 +0.141 | **held** |
| C-P3 | C2 post-ex-2025 bias in [−3, +4]; post MAE below C1's | +2.21; 7.43 < 9.03 | **held** |
| C-P4 | C2 pre bias in [0, +3.5]; pre MAE in [4.3, 5.8]; crisis bias in [−11, −3] | +0.02; 5.06; −6.96 | **held** (pre bias at the band's edge) |
| C-P5 | C3 MAE at or below C2's in all three regimes | 4.22 / 16.81 / 6.18 against 5.06 / 19.92 / 7.43 | **held** |
| C-P6 | C4 post MAE above C3's; pre MAE at or below C3's | post 6.58 > 6.18; **pre 4.57 > 4.22** | **half wrong** |
| C-P7 | C3 beats null_S pre and post; crisis MAE in [15.5, 19.0] | 4.22 < 4.97; 6.18 < 9.84; 16.81 | **held** |
| C-P8 | In C2-C4, 2025 is the largest positive bias, above +5 | largest in all three, but C2 +4.15, C3 +4.91, C4 +8.07 | **missed** in C2 and C3 |

Five of eight held, one was half wrong, and two were missed. The misses stay here.

## What the rule says

- **Rule (a) fires.** C3 beats C0 and null_S in every regime: 4.22 / 16.81 / 6.18 against 4.97 / 17.44 / 9.84.
  C4 does too, but C3 is better in all three regimes, so the wind basis that would ship is AGWS. The form a
  build would ship is **SAP, the annual net-export level, demand by year, and solar out of the residual**.
- **This is the first time the chain beats a gas-only null on the faithful gas price in every regime at the
  month.** That is the steer's headline defect. It is on the record, on the form a build would ship. It is
  **not built**: `sim/weather_price_chain` still runs the step-B form (6.50 / 17.20 / 8.19).
- **The build waits on three named things**, as the rule filed them: the DIRECTION `not_now` hold on SAP; a
  forward demand path (electricity page §8a: FES publishes system demand, not ND); and the FES net-flow level
  (§5). None of them is this worker's to pick.

## Stated plainly, beside the headline

- **C2 and C1 take each record year's own level from outside the chain.** DY_y is the year's own mean INDO
  minus the chain's mean demand. NE_y is the year's own mean net export. On the record, both are the real
  year level. A forward year takes them from a published path. So C3's figures are the chain **given the
  right annual demand and net-flow levels**. A forward figure is that error plus the error in the path. It is
  not a forecast skill.
- **Against null_T, C3 loses post-crisis without 2025** (5.47 against 4.81). It wins every other cell. Both
  nulls are quoted, as the gas-input result asked.
- **The chain now adds little to the leg's own error.** C3 against the leg on real AGWS-wind x: +0.01 pre,
  +1.59 crisis, +1.15 post. What is left is mostly the price leg's error, above all in 2021-22 (−7.2, −8.9).
  Of that, about £2.6 of crisis monthly MAE is 2022's neighbour shortfall (`781ad788b`), which the annual
  level cannot carry.
- **FUELHH wind (C4) costs pre-crisis accuracy this time** (4.22 → 4.57), and it still costs post-crisis (6.18 →
  6.58). This is the same direction as B3 post-crisis, on a different form. On the leg with real inputs,
  FUELHH is the best basis post-crisis (4.16). The candidate is still the chain's narrow wind range (the
  windiest day is 12.8 GW against 21.0 GW). **I cannot yet say.**
- **2025's x gap is +0.13 in C3.** That is the fleet clamp (`acc387cbe`: 2025 cannot take its own fleet), and
  it gives +4.9 of bias on a part year. No decision is keyed on it.
- **Quarterly MAE was not measured.** The steer named both the month and the quarter. A build step should
  report both.

## Next

1. **A build is ready to be cut, but is held.** The form is C3. Its three dependencies are named above. What
   moves without the director is the forward demand path. Its K8 section exists (§8a). Next, pre-register how a
   forward year's DY comes from FES system demand, using the conversion that section names.
2. The neighbour-shortfall K8 section (French nuclear availability as GB export demand), before any mechanism
   for 2022's shape is built.
3. Unchanged: R's 2025 residual against the AGWS windows finding.

Reverse: delete this record.
