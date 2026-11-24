**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: does GB's net interconnector export carry the 2022 markup that the chain's price leg cannot fit on SAP?

**Filed:** 24 Nov 2026, 11:25 UTC, by the worker, and landed before the measure is written or run. The
only figures read so far are **inputs**: GB net import by year from the cached FUELHH, set out below.
No arm has been fitted, and no price has been compared.

**For:** item 4 of `docs/staging/WORKER_FINDING_THE_WEATHER_TO_PRICE_CHAIN_STEER_IS_HALF_ANSWERED_AND_ITS_REST_HAD_NO_WORK_ITEM_2026-11-24.md`
("Add interconnector coupling or state why not"). This is the next step that
`docs/staging/records/WORKER_RESULT_ON_THE_REAL_GB_GAS_PRICE_THE_CHAINS_ONE_PRICE_LEG_CANNOT_FIT_THE_CRISIS_AND_THE_YEARS_AFTER_IT_2026-11-24.md`
names: on SAP, one fitted price leg puts 2022 £10.7 low and 2023-25 £9-17 high.

**Knowledge (K8):** `docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md` §5 and §9 item 4.
In 2022 GB was a net exporter for the only time in the series, because French nuclear was out. Exports
act as extra demand on GB plant, and imports push gas off the margin.

## Why this candidate, and why first

The price leg reads residual demand as `x = (INDO − AGWS wind and solar) / 35,000 MW`. INDO is Elexon's
initial national demand outturn, and it **excludes interconnector exports**. So x leaves out the cables in
both directions. An import is treated as GB thermal output, and an export is not seen at all. In 2022 the
leg saw no French demand on GB plant. In 2023-25 it saw none of the 23-33 TWh of imports that displaced
GB gas. Of the record's s.10 candidates, this one is in the cache, can be measured as one variable, and
would move 2022 and 2023-25 in opposite directions. That is the shape of the miss.

## Inputs (read before filing: an input, not an outcome)

Net GB import by year, summed from the signed FUELHH interconnector rows, latest publish per half-hour
and cable (`/var/tmp/mk22/inputs.py`), in TWh, with DUKES 5.13 (page §5) in brackets:
2016 17.84 (17.7), 2017 15.67 (14.8), 2018 19.23 (19.1), 2019 21.25 (21.2), 2020 18.34 (17.9),
2021 24.81 (24.6), **2022 −4.21 (−5.3)**, 2023 23.39 (23.8), 2024 33.30 (33.4), 2025 31.96 (29.7).
There are 17,499-17,568 half-hours a year, so the series is complete. FUELHH has no Greenlink row, and
DUKES is on a UK basis, so the 2022 and 2025 differences are expected.

## The arms (all on SAP, all with carbon in the floor, as G2)

- **G2** (control) reproduces the gas-input arm: SAP in the call and in the A0-A2 refit. It should
  return 4.77 / 20.88 / 13.00. If it does not, the run is void.
- **X** (one variable): as G2, with **net export added to demand** wherever the leg reads demand.
  In the half-hourly refit, `demand_mw + net_export_mw` for that half-hour, where net export is minus
  the signed FUELHH sum. On the record, the chain's weather-derived demand plus the day's mean real net
  export. A half-hour with no cable reading takes 0, and the run prints how many there are.
- Nulls as before: `null_T` (gas-only OLS on TTF) and `null_S` (on SAP). B, the shipped chain on TTF,
  is quoted from the gas-input record (6.50 / 17.20 / 8.19).
- "Monthly" is the demand-weighted monthly mean, and the regimes are the steer's.

The real flow is a **world-side observable on the record**, the same class as the INDO and AGWS this leg
already reads. Nothing in the arm crosses to the company.

## Predictions (X against G2 unless stated)

| # | Prediction |
|---|---|
| X1 | X's half-hourly leg MAE is below G2's. |
| X2 | X's 2022 mean monthly bias is within ±£5 (G2: −10.7). |
| X3 | X's post-crisis monthly bias is below +£8 (G2: +12.28). |
| X4 | X's crisis monthly MAE is below G2's 20.88 and below B's 17.20, so X beats null_S (17.44) in the crisis. |
| X5 | X's post-crisis monthly MAE is below G2's 13.00 and does not reach B's 8.19. |
| X6 | X's pre-crisis monthly MAE is within 4.77 ± 0.75. |
| X7 | X's refit a1 is above G2's 0.930. |

## Decision rule, filed now

- **(a) Named.** If X2 and X3 both hold, net export is the leading mechanism for the 2022 markup and for
  the post-crisis level gap. The build becomes the chain's interconnector term. Forward years then need a
  flow **mechanism**: the flow is set by the continental price against GB's (`sim/elexon_fuel_outturn.py`
  docstring), so forward years cannot replay it. That design goes on the electricity page as K8 before
  anything is built.
- **(b) Partly.** If 2022's bias moves at least halfway (to −5.35 or above) and the post-crisis bias stays
  at +£8 or more, the flow carries 2022, and the post-crisis gap is a second mechanism. The next candidates
  are a post-crisis fleet more efficient than the 0.50 constant, and SSP against MID (page §10a: the
  traded price sat £9.80 below gas-plus-carbon SRMC after the crisis).
- **(c) Not this.** If 2022's bias moves less than halfway, net export is ruled out as the main mechanism.
  That answers "add interconnector coupling or state why not" with *why not*, on the record.
- **Whatever the outcome, nothing in `sim/` changes in this step.** The chain keeps TTF and its known
  error until a mechanism lets SAP fit.
