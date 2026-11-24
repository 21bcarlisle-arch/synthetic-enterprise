**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: does the chain's post-crisis bias sit on the days gas is off the margin? (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is the arm the SRMC-gap record (`11778a0621`) names as next. Filed before the probe
`/var/tmp/mk24/measure.py` is run. Nothing in `sim/` changes.*

## The question

On arm X (SAP in the call and the refit, real net export in residual demand), the chain's post-crisis
monthly bias is +8.23. The record's own gap below gas SRMC after the crisis is a mixture. When CCGT output is
high, power clears £14-24 above fleet SRMC. In the lowest CCGT quintile it clears £37-42 below. Does the
chain's +8.23 sit on the low-CCGT days, as the record's gap does?

## Definitions, before any number

- **Residual** = the chain's daily price − the real daily SSP, on arm X. This is the series the chain is
  graded against.
- **CCGT band** = the quintile of that day's mean FUELHH CCGT output, taken within each calendar year. It
  uses the real record (`load_cached_thermal`, latest publish per key). High output is the observable proxy
  for "gas is marginal". It is a proxy, and page GAP 4 (no marginal-unit series) stays open. A daily mean
  blurs the half-hourly split. A windy day still has gas at the margin in its evening peak, so every
  band's depth will be shallower than the half-hourly −£37-42.
- **Floor** = (SAP + carbon × EF) ÷ 0.50, which is the chain's own floor. `ssp_minus_floor` is the record's
  gap on that floor, and `chain_minus_floor` is the chain's.
- **Regimes** as in every arm so far: pre to 2021-06, crisis 2021-07 to 2023-06, post 2023-07 to 2025-06-07.

## What is known before the run

The price leg is `floor × (a0 + a1·x + a2·kick)`, where x = (demand − renewables) ÷ 35 GW. It has no
intercept and is fitted once across 2016-2025. On X, a0 is about 0.52 and a1 about 1.0. So the chain's
discount below its floor on a low-x day is one fixed fraction of the floor in every year. The record's is
not. Before the crisis the low-band depth was £6-13 on a floor of about £40-45, or 15-30%. After it, the
depth was about £40 on a floor of about £90, or about 45%. A fixed fraction that splits the difference
should under-discount the post-crisis low days, which puts a positive residual on the low-CCGT band.

## Predictions

| # | Prediction |
|---|---|
| C1 | The control reproduces X: monthly MAE 4.89 / 17.02 / 10.38 and post-crisis bias +8.23, to ±0.01 |
| C2 | Post-crisis, the mean daily residual is ≥ +12 in Q1 (lowest CCGT) and ≤ +6 in Q5, so Q1 − Q5 ≥ £8 |
| C3 | Post-crisis, the residual falls from Q1 to Q5, with at most one inversion |
| C4 | Pre-crisis, \|Q1 − Q5\| ≤ £6 |
| C5 | Post-crisis, the record's own `ssp_minus_floor` in Q1 is ≤ −£20, and in Q5 it is ≥ 0 |
| C6 | Post-crisis, Q1 + Q2 carry more than 60% of the summed daily residual |
| C7 | By year (2023 H2, 2024, 2025 H1), Q1's residual is the largest of the five bands in each |

## Decision rule, filed now

- **(a) C2 and C4 hold.** The price leg's depth below gas is mis-scaled, because one fixed fraction is used
  across floor levels. Next: a K8 note on what sets the price when gas is not marginal (wind and nuclear
  offers, CfD negative bidding, imports). Then an arm that adds a sub-gas shape scaling with the floor,
  refit on the same window, with its prediction filed first.
- **(b) Q1 − Q5 < £4 post-crisis.** The bias is a level, not the mix. Next candidate: the chain's inputs in
  2023-25 (demand from weather against the fall in real demand, and embedded solar). Compare the chain's
  residual demand with the record's by year.
- **(c) The residual is largest in Q5.** The multiplier mis-scales at high gas, which is the steer's
  third gap. Next: the crisis-scaling arm.
- Anything else is reported as it falls, and no build follows from it.

Reverse: delete this record.
