**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: on the daily SAP splice, the price leg's post-crisis miss changes sign, so the afternoon arms' "level" was the TTF proxy's 2022 premium (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in
`docs/staging/records/WORKER_PREREG_THE_PRICE_LEGS_INPUTS_ARM_DAILY_SAP_IN_PLACE_OF_THE_MONTHLY_TTF_PROXY_2026-11-24.md`
(`932409f6e`), which was promoted to origin before the probe ran. Run in a worktree at `932409f6e` with `sim/cache`
linked in. Outputs `/var/tmp/wpc_inputs/out_proxy.json` and `out_sap.json`. **Nothing in `sim/` changes.***

**Disclosure, the probe changed after filing.** The filed probe (sha256 `3829d151…`, kept as
`/var/tmp/wpc_inputs/measure_g_v1.py`) had two bugs. It imported `sim` before putting the repo on the path. Its
`sap` patch also replaced `load_nbp_history` with `load_gas_baseline_spliced`, which calls `load_nbp_history` and so
recursed. The run probe (`measure_g.py`, sha256 `7b57dff5…`) adds the path line. It captures the proxy loader first
and rebuilds the splice from `load_sap_daily` with the same seam and end. The landed splice returns 3,538 days,
2015-10-01 to 2025-06-07, and so does the run probe. The splice's gap check is not repeated, because the landed
loader already passed it on the same file. Nothing else in the probe changed, and the proxy output is
byte-identical before and after the fix.

## Correction, beside my own claim

The pre-registration said no SAP figure had been computed for this question. That is true of this form, the leg
alone on real daily x. It is not true of the question. The gas-input arm (`8be76e9495`, 11:15 today) already
swapped the same series into the CHAIN and found the same thing: the post bias went to +12.3, and 2022 to −10.7.
The interconnector arm (`c2f65d9e9`, 11:25) then took 2022 to −1.1 with GB's net export, on SAP. I did not read
either before filing, and G-P3 (the crisis improves) contradicts what `8be76e9495` had already published. This arm
is a replication on the leg's own form, not a new test of the mechanism. The predictions stay as filed.

## Outcomes (the leg alone, on real daily x; monthly, demand-weighted, £/MWh: MAE / bias)

| Form | Gas | Coefficients | HH MAE | Pre | Crisis | Post | Post without 2025 |
|---|---|---|---|---|---|---|---|
| R L0 | proxy | 0.2918 / 1.0790 / 2.8276 | 31.53 | 5.48 / −3.11 | 14.62 / −3.33 | 9.84 / −7.99 | 8.03 / −5.57 |
| R L0 | **SAP** | 0.5170 / 0.9296 / 1.3960 | **30.99** | **4.65** / +1.33 | 18.46 / −8.20 | **5.82** / +4.08 | 6.23 / +5.85 |
| R L1 | proxy | … / b0 **+£5.80** | 31.73 | 4.82 / +0.82 | 13.62 / −5.29 | 8.36 / −5.64 | 6.74 / −3.12 |
| R L1 | **SAP** | … / b0 **−£3.25** | 30.79 | 4.57 / −0.71 | 18.14 / −7.04 | 5.59 / +3.23 | 5.79 / +4.92 |
| W L0 | proxy | 0.2732 / 1.0534 / 3.0214 | 31.95 | 5.07 / −2.26 | 17.26 / −6.33 | 7.76 / −7.24 | 7.95 / −7.28 |
| W L0 | **SAP** | 0.4732 / 0.9629 / 1.3681 | 31.33 | 4.99 / +2.27 | 17.80 / −10.08 | 5.83 / +4.83 | 5.40 / +4.55 |
| W L1 | **SAP** | … / b0 −£4.28 | 31.06 | 4.43 / −0.40 | 17.37 / −8.59 | 5.16 / +3.69 | 4.73 / +3.30 |

**Bias by year, R L0:**

| Gas | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| proxy | −4.67 | −0.97 | −0.09 | −2.29 | −5.91 | −8.45 | +3.25 | −10.53 | −2.68 | −15.25 |
| SAP | −1.96 | +2.77 | +5.39 | +2.40 | −1.47 | −1.20 | **−17.85** | +3.31 | +7.74 | −1.24 |
| gas mean, proxy | 11.30 | 15.33 | 21.09 | 11.79 | 8.41 | 43.14 | 101.00 | 34.28 | 29.06 | 35.25 |
| gas mean, SAP | 11.30 | 15.33 | 20.78 | 11.91 | 8.49 | 39.48 | 71.65 | 34.41 | 28.67 | 35.05 |
| carbon mean £/t | 22.3 | 23.1 | 31.6 | 39.6 | 39.8 | 67.2 | 93.1 | 70.9 | 55.0 | 60.3 |

| # | Prediction | Outcome |
|---|---|---|
| G-P0 | Proxy reproduces the shape result's L0/L1 rows within £0.01 | **Held.** All cells identical; `synthetic_price` within 1.1e-13 a day |
| G-P1 | SAP raises a0 + a1·XL by at least 5% | **Held.** 0.9372 → 1.0730, +14.5% |
| G-P2 | Post bias moves toward zero by at least £2 and stays outside ±£3 | **Held as written** (−7.99 → +4.08). The spirit failed: it crossed zero, overshooting by £4 |
| G-P3 | Crisis MAE falls by at least £2 | **Wrong.** 14.62 → 18.46 |
| G-P4 | 2023 bias moves toward zero by at least £1.5 | **Held.** −10.53 → +3.31 |
| G-P5 | 2021 bias moves by less than £2 | **Wrong.** −8.45 → −1.20 |
| G-P6 | Pre-crisis MAE moves by less than £1.0 | **Held.** 5.48 → 4.65 |

Five of seven held. The two that were wrong both come from the same mistake. I expected the crisis to fit better
on the gas GB power was priced against. Instead, a lower 2022 floor exposes a markup over SAP that one multiplier
cannot carry. `8be76e9495` had already shown this.

## What the rule says

- **(b) fires as written, and its reading is wrong.** The post bias moves by £12 and lands outside ±£3, but on the
  other side of zero. So the input is not "part of the gap". The input made the gap. On SAP, the leg runs £4-6
  HIGH after the crisis, not £6-8 low.
- **The non-gas constant does not survive the swap.** L1's b0 goes from +£5.80 on the proxy to −£3.25 (R) and
  −£4.28 (W) on SAP. The shape result offered "a constant of about £5-6 that helps every regime" as a build
  candidate. That constant was the proxy's artefact, and it is withdrawn as a candidate.
- **2021, 2023 and 2025 were not a lagging input.** Their low years close on SAP (−8.5 / −10.5 / −15.3 →
  −1.2 / +3.3 / −1.2). Their annual gas means barely move, except 2021 at −8%. They close because the multiplier
  rises once 2022 stops teaching it a low value. The fit's level was set by 2022.

## Interconnection: what this does to the afternoon's arms

The build-terms and shape arms (`ea3a93cc4`, `79fc1fbdb`) priced the leg from `load_nbp_history`, the TTF proxy.
The shape probe is read above, and the shape result records build-terms' rows as its control. So their conclusions
about the price leg's post-crisis LEVEL were measured on an input known since 11:15 to carry a 29% premium in 2022.
Those conclusions are build-terms' "about £7 low", shape's "a level, not a shape", and the £5-6 constant. They
need re-reading on SAP before any build uses them. Conclusions about how much gas RUNS (the gas-running and
wind-target arms) do not read the gas price, and they are not affected. The efficiency, CCGT-band and separating
arms were not re-checked here. This record does not revise any of them in place.

## Next

1. **The leg on real x, on SAP, plus GB's real net export** (the interconnector arm's term, `c2f65d9e9`): the
   one-leg form that the build would ship, combining the two inputs already shown to matter. Control: this record's
   SAP R L0 row. Pre-register it, citing `8be76e9495` and `c2f65d9e9`.
2. Rerun the build-terms B1-B3 on SAP before any build reads their price-leg rows.
3. Any build that fits the leg on SAP waits on the same DIRECTION `not_now` hold as the world's baseline splice.

Reverse: delete this record.
