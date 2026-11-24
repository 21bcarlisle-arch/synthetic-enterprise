**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: on the SAP splice, does GB's real net export take out the price leg's crisis miss on the leg's own form? (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is Next 1 of the inputs result,
`docs/staging/records/WORKER_RESULT_ON_THE_SAP_SPLICE_THE_PRICE_LEGS_POST_CRISIS_MISS_CHANGES_SIGN_THE_LEVEL_WAS_THE_PROXYS_2022_PREMIUM_2026-11-24.md`
(`44fab345e`). Filed and landed before the `ne` arm runs. **Nothing in `sim/` changes.***

## The question

On the SAP splice, the leg alone on real daily x (R L0) misses the crisis badly: monthly MAE £18.46, bias −8.20,
and 2022 at −17.85. After the crisis it runs high, at +4.08. Two arms have already tested net export, but on the
CHAIN's form rather than the leg's own. The gas-input arm (`8be76e9495`) put SAP into the chain. The
interconnector arm (`c2f65d9e9`) then added GB's real FUELHH net export to demand on SAP. That moved the chain's
2022 bias from −10.7 to −1.1 and its post bias from +12.3 to +8.2. The leg's residual demand is INDO, which
excludes exports. **On the leg's own one-leg form, does adding the same net export, and nothing else, take out
the crisis miss, and where does it leave the post-crisis level?**

## Design

- **One variable:** net export (minus the signed FUELHH interconnector sum, per half-hour) is added to INDO
  wherever the leg reads demand. That covers the half-hourly OLS refit and the record's real daily x, which is
  the day's mean of the same half-hourly x. Everything else is the inputs probe's SAP arm, unchanged. That means
  the same 157,010 common half-hours, form L0 (the shipped form), bases R (INDO − AGWS renewables) and W
  (INDO − FUELHH wind), and the same evaluation. L1 is dropped, because the inputs result withdrew its constant.
- **Input:** `/var/tmp/mk22/net_import_hh.json`, the interconnector arm's own file (sha256 `eb4e1d3a…`). It is
  built from the cached FUELHH `INT*` rows, one value per half-hour and cable. It covers all 157,010 common
  half-hours (0 missing).
- **Probe:** `/var/tmp/wpc_ne/measure_ne.py`, sha256 `0de881e9f92abf06d260f403a8f2b92b718c40fb8850416fb9acae7cf21a0f2a`.
  It is `/var/tmp/wpc_inputs/measure_g.py` with gas fixed to SAP, L1 dropped and `argv[1]` in {`base`, `ne`}. It
  runs in a worktree at origin `95af8ab77` with `sim/cache` linked in.
- **Seen before filing, and disclosed:**
  - The `base` arm has already run. It is the control, and its figures were already published. It reproduces
    the inputs result's SAP R L0 and W L0 rows exactly: coefficients, every regime cell and every year.
    `synthetic_price` agrees to within 1.1e-13.
  - Net export by year, in MW mean over the common half-hours (positive means export): 2016 −1,914, 2017 −1,781,
    2018 −2,200, 2019 −2,444, 2020 −2,075, 2021 −2,831, **2022 +506**, 2023 −2,668, 2024 −3,793, 2025 −3,863.
  - Both chain-form results above.
  - No `ne` figure has been computed.

## Predictions (R L0 unless stated; monthly, demand-weighted, £/MWh)

| # | Prediction |
|---|---|
| NE-P0 | `base` reproduces the inputs result's SAP R L0 and W L0 rows exactly (**already run: held**, disclosed above) |
| NE-P1 | 2022's bias moves toward zero by at least £6 (−17.85 → −11.85 or above) |
| NE-P2 | Crisis monthly MAE falls by at least £2 (18.46 → 16.46 or below) |
| NE-P3 | Post-crisis bias falls by at least £1.5 (+4.08 → +2.58 or below) |
| NE-P4 | Post-crisis bias lands inside ±£3 |
| NE-P5 | Pre-crisis monthly MAE moves by less than £0.50 (4.65) |
| NE-P6 | 2024's bias falls by more than 2023's does (imports 1.1 GW larger in 2024) |
| NE-P7 | W L0 moves in the same direction as R L0 on P1, P2 and P3 |

The reasoning is as follows. In 2022 GB exported on average, so adding net export raises x in 2022 alone. That
lifts the leg's price where it runs £18 low. Imports are larger after the crisis than before it (2.7-3.9 GW
against 1.8-2.4 GW), so the same term lowers post-crisis x more than pre-crisis x, which pulls the +4 post bias
down. The refit has no intercept, so a near-constant pre-crisis shift is mostly absorbed by a0 and a1 (P5).
P1 bets on less than the chain's +9.6, because the leg's 2022 miss is larger and the refit will share it out.

## Decision rule, filed now

- **(a) The leg's form is found.** P2 and P4 both hold, and pre-crisis MAE does not rise by more than £0.50.
  Then the one-leg form on SAP plus net export is the leg a build would ship. It waits on two things: the forward
  net-flow K8 section (electricity page §5, still owed), because forward years need a flow path; and the
  DIRECTION `not_now` hold on the SAP splice. The next arm is build-terms B1-B3, rerun on this form.
- **(b) Net export is the crisis term only.** P2 holds and the post bias stays outside ±£3. The post-crisis
  remainder is then re-measured by rerunning B1-B3 on SAP plus net export.
- **(c) It does not carry to the leg's own form.** Crisis MAE moves by less than £2. The chain-form result
  (`c2f65d9e9`) then does not hold on the leg's form. The next arm attributes the difference between the two
  forms: the chain's weather-derived demand against INDO, with the two-leg fit against the one-leg fit.

Reverse: delete this record.
