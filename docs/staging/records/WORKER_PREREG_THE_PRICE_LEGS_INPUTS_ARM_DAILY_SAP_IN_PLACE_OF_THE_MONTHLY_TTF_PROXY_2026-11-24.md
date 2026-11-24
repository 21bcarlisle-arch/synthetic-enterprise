**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: the price leg's inputs arm, the daily SAP splice in place of the monthly TTF proxy, against its by-year level miss (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is Next 1 of the shape result,
`docs/staging/records/WORKER_RESULT_THE_PRICE_LEGS_POST_CRISIS_MISS_IS_A_LEVEL_NOT_A_SHAPE_A_NON_GAS_CONSTANT_HELPS_EVERY_REGIME_2026-11-24.md`
(`79fc1fbdb`). Filed and landed before the probe runs. **Nothing in `sim/` changes.***

## The question

On real daily x, the shipped price leg runs low by year: −8.5 (2021), +3.3 (2022), −10.5 (2023), −2.7 (2024),
−15.3 (2025), £/MWh on the R basis. The shape arm ruled out shape. The candidate it named is an INPUT. The leg's
gas input, in both its half-hourly fit and its daily evaluation, is `load_nbp_history`. That series is FRED
`PNGASEUUSDM`, the IMF monthly TTF price, converted at a fixed 1.28 $/£ and spread flat over each month. GB power
was priced against GB gas. The landed splice `load_gas_baseline_spliced` is GB daily SAP from 2018-01-01, with the
proxy before it, clipped to the same end date. **Does swapping the gas series, and nothing else, move the
by-year level miss?**

The carbon input has no second series on the record to swap. `carbon_on` already reads CPS plus EUA to 2020 and
the UKA auction VWAP from 2021. The secondary-market UKA price is the electricity page's open gap. Carbon's mean
by year is printed beside the biases, but it is not graded.

## Design

- One variable: the gas series, in the fit and in the evaluation together. The same days, the same 157,010
  common half-hours, the same forms L0 (the shipped form) and L1 (plus a constant that does not scale with gas),
  each refit by half-hourly OLS, on bases R and W. Evaluation is exactly the shape probe's.
- Probe `/var/tmp/wpc_inputs/measure_g.py`, sha256 `3829d15151bfd715dc0475e3856022bbcee108970587b75006596c330072f908`.
  It is the shape probe with L2-L3 dropped, the gas loader patched by `argv[1]` (`proxy` or `sap`), and the
  by-year gas and carbon means added. It runs in a worktree at the commit that lands this record, with `sim/cache`
  linked in.
- **Seen before the run, and disclosed:** the proxy rows, which are the shape result's L0 and L1 rows. The annual
  proxy-against-SAP means are also published on the splice page: 2021 −8%, 2022 −29%, 2023 0%, 2024 −1%, 2025 H1
  −1% (SAP minus proxy). No SAP-arm figure was computed before this filing.

## Predictions

| # | Prediction |
|---|---|
| G-P0 | The proxy run reproduces the shape result's R and W L0 and L1 rows within £0.01 |
| G-P1 | On SAP, the R L0 effective multiplier at the median x (a0 + a1·XL) rises by at least 5% against the proxy's |
| G-P2 | On SAP, the R L0 post-crisis bias moves toward zero by at least £2 (to −6.0 or above) and stays outside ±£3 |
| G-P3 | On SAP, the R L0 crisis monthly MAE falls by at least £2 (14.62 → 12.62 or below) |
| G-P4 | On SAP, the R L0 2023 bias moves toward zero by at least £1.5 |
| G-P5 | On SAP, the R L0 2021 bias moves by less than £2 in either direction |
| G-P6 | On SAP, the R L0 pre-crisis monthly MAE moves by less than £1.0 |

The reasoning: the OLS is weighted in pounds, so the crisis half-hours dominate it. In 2022 the proxy runs 29%
above GB gas, so the proxy fit learns a LOW multiplier on gas, to match GB power with too high a floor. That low
multiplier then prices every later year low, where proxy and SAP agree. On SAP the crisis floor falls, the
multiplier rises, and the post-crisis years are lifted. That is a fit artefact, not a lag. 2021 (proxy 8% above SAP)
gets a lower floor and a higher multiplier, which roughly offset, so G-P5 says 2021 is not explained by this
variable. 2023's annual means agree, so any move there is the multiplier alone (G-P4). The prediction that the post
bias stays outside ±£3 (G-P2) is a bet that the input is part of the gap, not all of it.

## Decision rule, filed now

- **(a) The input carries the gap** if SAP brings the R L0 post-crisis bias inside ±£3 without raising the
  pre-crisis MAE by more than £0.50. Then the leg's fit moves to the SAP splice. That build waits on the same
  DIRECTION `not_now` hold as the world's baseline splice, because it changes what the chain prices from. It is
  named there, not done around it.
- **(b) The input is part of the gap** if the post bias moves toward zero by at least £2 but stays outside ±£3.
  The remainder is re-measured on SAP. L1's constant is re-read on SAP as a named candidate, and 2021 and 2025
  are the next attributions.
- **(c) The input is not the cause** if the post bias moves by less than £2. The lagging-input candidate is then
  refuted for gas. The next arm is the R basis's 2025 residual (R −15.3 against W −7.1).

Reverse: delete this record.
