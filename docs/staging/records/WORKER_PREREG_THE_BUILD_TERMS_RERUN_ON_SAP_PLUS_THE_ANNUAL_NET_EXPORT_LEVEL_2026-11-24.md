**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: the build terms rerun on SAP plus the annual net-export level (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is Next 1 of the leave-one-year-out result (`781ad788b`), and Next 3 of the build-terms result
(`ea3a93cc4`). Filed and landed before arms C1-C4 run. Probe `/var/tmp/wpc_c/measure_c.py`, sha256
`36d656b8…`. **Nothing in `sim/` changes.***

## The question

The build-terms arms B1-B3 (`ea3a93cc4`) were run on the monthly TTF proxy with no net export. Since then
the leg's form has moved twice: gas is the daily SAP splice (`44fab345e`), and net export enters residual
demand as each year's mean (`4984c3dbc`, `781ad788b`). The annual level is the only net-flow term a forward
build can carry. **On that form, which build terms should the chain ship, and does the chain then beat a
gas-only null on SAP in each regime?**

## Arms (cumulative, one variable each, on the chain's daily record)

Each arm refits A0-A2 on the half-hourly record, with the same residual definition as the chain side.

| Arm | Leg fitted on (MW) | Chain residual |
|---|---|---|
| C0 control (= G2) | INDO − AGWS wind+solar | chain demand − chain wind+solar |
| C1 + net export, year mean | INDO + NE_y − AGWS w+s | + NE_y |
| C2 + demand year term | same as C1 | + DY_y (`b0_out.json`, from INDO and chain demand only) |
| C3 + solar out | INDO + NE_y − AGWS wind | renewable = chain wind only |
| C4 + wind on FUELHH | INDO + NE_y − FUELHH WIND | chain wind × s_y |

NE_y is each calendar year's mean FUELHH net export over the probe's half-hours. It runs −1.8 to −3.9 GW,
and +0.5 GW in 2022. The probe also reports the leg on REAL daily x for each basis, and null_S / null_T.

## Controls, run before filing (disclosed)

The probe was run in `control` mode, which computes C0 and the leg-on-real R basis only. No C1-C4 figure
and no S or W refit was computed.

- C0 reproduces G2 to the penny: 4.77 / 20.88 / 13.00 monthly MAE, with A0-A2 = 0.5169 / 0.9295 / 1.3943.
- The leg on real R with the year-mean net export reproduces the `am` arm: 4.45 / 16.16 / 5.58, with
  0.5492 / 0.9365 / 2.1667.
- null_S is 4.97 / 17.44 / 9.84. C0's x gap (chain minus record) is +0.047 to +0.056 in 2022-24 and +0.206 in
  2025. That is the demand gap DY corrects, plus 2025's fleet clamp.

## Predictions (monthly, demand-weighted, £/MWh)

| # | Prediction |
|---|---|
| C-P1 | C1: pre MAE within 4.77 ± 0.75; post bias in [+6, +10.5]; crisis MAE in [16.5, 20.5] |
| C-P2 | C2: \|x gap\| < 0.012 in every year 2017-2024, and 2025's x gap > +0.10 (its clamp) |
| C-P3 | C2: post-ex-2025 bias in [−3, +4]; post MAE below C1's |
| C-P4 | C2: pre bias in [0, +3.5]; pre MAE in [4.3, 5.8]; crisis bias in [−11, −3] |
| C-P5 | C3: MAE at or below C2's in all three regimes (solar out is definitional) |
| C-P6 | C4: post MAE above C3's, as B3 was above B2; pre MAE at or below C3's |
| C-P7 | C3 beats null_S pre (< 4.97) and post (< 9.84); its crisis MAE is in [15.5, 19.0] |
| C-P8 | In C2-C4, 2025 is the year with the largest positive bias, above +5 |

## Decision rule (filed with the predictions)

- **(a)** If C3 or C4 beats both C0 and null_S in all three regimes, it is the form a build would ship: SAP,
  the annual net-export level, demand by year, and solar out, with wind on the better basis. The build is a
  later step with its own prediction. It still waits on the DIRECTION `not_now` hold on SAP, a forward
  demand path (electricity page §8a: FES publishes system demand, not ND), and the FES net-flow level (§5).
- **(b)** If it beats null_S pre and post but not in the crisis, (a)'s build stands. Every forward figure
  carries the crisis error beside it, with the 2022 neighbour shortfall (about £2.6, `781ad788b`) named as
  outside the form.
- **(c)** If C-P2 fails in 2017-2024, the result is about the construction, not the price, and nothing is
  ranked.
- **2025** is a part year, and the fleet is clamped to 2024 (`acc387cbe`). It is reported with and without.
  No decision is keyed on it.

Reverse: delete this record.
