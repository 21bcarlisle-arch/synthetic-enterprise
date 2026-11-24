**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: GB's net interconnector export carries the 2022 markup on SAP, but leaves two-thirds of the post-crisis gap (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer, on origin `ef4b0ef19`, in a clean
worktree. Pre-registered in
`docs/staging/records/WORKER_PREREG_DOES_GB_NET_EXPORT_CARRY_THE_2022_MARKUP_THE_CHAINS_PRICE_LEG_CANNOT_FIT_ON_SAP_2026-11-24.md`,
which landed and was promoted at 11:23 UTC, before the probe `/var/tmp/mk22/measure.py` was run.
**Correction, beside the claim:** that record says "Filed 11:25 UTC". That was a guess ahead of the clock.
The promotion line, at 11:23:19 UTC, is the evidence for the order. **Knowledge (K8):**
`docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md` §5. **Nothing in `sim/` changes.***

## The control holds

G2 reproduces the gas-input arm to the penny: 4.77 / 20.88 / 13.00 monthly MAE, with A0-A2 = 0.517 / 0.930
/ 1.394. So the run is valid. Arm X is G2 with the real net export added to demand. Of 157,106 half-hours in
the refit, 96 had no cable reading and took 0. Every record day was covered. The patch reached the record's
two demand calls (the printed count is 2).

## The predictions, and the outcome beside each

| # | Filed | Outcome | Held? |
|---|---|---|---|
| X1 | half-hourly leg MAE below G2's | 31.13 against 30.99 (R² 0.4487 against 0.4479) | **missed** |
| X2 | 2022 monthly bias within ±£5 (G2 −10.7) | **−1.10** | **held** |
| X3 | post-crisis monthly bias below +£8 (G2 +12.28) | +8.23 | **missed**, by £0.23 |
| X4 | crisis monthly MAE below 20.88 and below B's 17.20, so it beats null_S (17.44) | 17.02 | **held** |
| X5 | post-crisis MAE below 13.00, not reaching B's 8.19 | 10.38 | **held** |
| X6 | pre-crisis MAE within 4.77 ± 0.75 | 4.89 | **held** |
| X7 | refit a1 above G2's 0.930 | 0.998 (a2 from 1.394 to 1.736) | **held** |

**Five held and two missed.** X1 missed because least squares on the half-hour weights the in-day spikes.
Net export moves the level by month and does little within the day, so a fit that improves every month can
still lose a little half-hourly MAE. X3 missed at its edge.

## The numbers

Monthly MAE / monthly bias, £/MWh. Every row is on SAP except B.

| Arm | pre | crisis | post |
|---|---|---|---|
| B, shipped (TTF) | 6.50 / −5.29 | 17.20 / +2.39 | **8.19** / +1.84 |
| G2, SAP | **4.77** / −0.35 | 20.88 / −4.09 | 13.00 / +12.28 |
| **X, SAP + net export** | 4.89 / −0.95 | **17.02** / −1.50 | 10.38 / +8.23 |
| null_T | 5.42 / +1.81 | 24.53 / −9.54 | 6.67 / +0.70 |
| null_S | 4.97 / −1.03 | 17.44 / −9.45 | 9.84 / +8.89 |

Mean monthly bias by year, G2 → X: 2016 −5.4 → −5.6; 2019 +1.1 → +0.3; 2021 −1.6 → **−4.7**;
**2022 −10.7 → −1.1**; 2023 +8.7 → +5.6; 2024 +11.7 → +6.9; 2025 +16.9 → +11.3.

## What it says

1. **Net export is the mechanism behind 2022's markup over the floor.** Decision rule (b), as filed: the
   2022 bias moves 90% of the way to zero, and the crisis MAE beats both nulls and the shipped chain. This
   is the first arm that beats every comparator in the crisis. In 2022 France's demand ran on GB's gas
   plant, and a residual demand built on INDO could not see it. On TTF the proxy's 29% premium stood in
   for this. The "crisis mis-scaling at high gas" in the steer's grade was **a missing demand, not a
   scaling error**.
2. **It closes only about a third of the post-crisis gap (+12.3 → +8.2), and what is left grows each
   year** (+5.6, +6.9, +11.3). A second mechanism is needed, and decision rule (b) names the candidates.
   One is a post-crisis fleet more efficient than the 0.50 constant. That would be a level gap that grows
   with gas share and time. The other is SSP against MID (page §10a: the traded price sat £9.80 below
   gas-plus-carbon SRMC after the crisis). Interconnector imports are now in, so the effect that remains is
   not the 23-33 TWh of imports. **I cannot yet say which**, and one arm per candidate is the way to find out.
3. **2021 gets worse (−1.6 → −4.7).** The steer's ask was a level for 2022, so this is exploratory. 2021 had
   the year's largest net import before 2024 (24.8 TWh), and the refit raised a1. This is a cost of the
   term and stays beside it.
4. **Against the steer's "add interconnector coupling or state why not": add it.** The 64fd7f5f8a "why
   not, for now" was about the chain's slope against wind, and it still stands for that. On level, the flow
   is the largest single gap measured so far in 2022.

## Decision

**Nothing ships in `sim/` from this arm**, as filed. Shipping SAP together with net export needs a
**forward flow mechanism**. The flow is set by the continental price against GB's (`sim/elexon_fuel_outturn.py`
docstring), so forward years cannot replay the record's flow. Until that exists the chain keeps TTF, and
the known error stated in the gas-input record stays beside every forward figure.

**Next, under item 4, in order:**
1. K8 first. Add to the electricity page §5 how a forward flow is formed: the spread to the continental
   price, by link capacity by year. Then add the design choice, either a drawn flow in a sourced band or a
   spread-driven flow, with GAP labels.
2. The second-mechanism arm, pre-registered, run on X: the thermal efficiency by year against the 0.50
   constant, one variable.
