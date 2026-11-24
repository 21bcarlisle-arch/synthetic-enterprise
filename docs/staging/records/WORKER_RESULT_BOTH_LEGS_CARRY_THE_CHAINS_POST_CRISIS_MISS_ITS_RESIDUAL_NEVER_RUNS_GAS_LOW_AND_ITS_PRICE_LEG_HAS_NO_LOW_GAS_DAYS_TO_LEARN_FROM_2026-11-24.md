**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: both legs carry the chain's post-crisis miss. Its residual never runs gas low, and its price leg has no low-gas days to learn from (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in `4f9e788e7`, which landed and was promoted to origin before the probe ran:
`docs/staging/records/WORKER_PREREG_IS_THE_CHAINS_POST_CRISIS_MISS_IN_ITS_PRICE_LEG_OR_IN_HOW_MUCH_GAS_IT_RUNS_2026-11-24.md`.
The probe is `/var/tmp/mk25/measure_s.py`, sha256 `3cee2860…8853f21`, checked unchanged at run time. It ran in
a worktree at `4f9e788e7`, and its output is `/var/tmp/mk25/out_s.json`. **Nothing in `sim/` changes.***

Fitted on pre-crisis days only: leg P b = (0.789, 0.0233, 0.0200), so SSP/floor is 0.79 + 0.023·c, plus
0.020 per GW above 14. Leg H h = (8.09, −0.0169, 0.0124) on r in GW.

## Predictions and outcomes

| # | Filed | Outcome | Held? |
|---|---|---|---|
| S1 | leg P post: MAE ≤ 7.0 and bias +1..+6 | MAE 6.97, bias **+6.16** | **missed** (bias, by 0.16) |
| S2 | leg P crisis: MAE ≤ 15.0 | 9.44 | held |
| S3 | leg P pre: MAE ≤ 4.89 | 3.06 | held |
| S4 | leg P post, real c < 6 GW: mean residual 0..+12 | **+13.78** (241 days) | **missed** |
| S5 | composite post: bias ≥ +5 | +11.75 | held |
| S6 | post: c_hat − c ≥ 1.5 GW; c_hat days < 6 GW under 121 | +3.12 GW (12.04 against 8.92); **0** days | held |

Four of six held.

## The numbers, monthly MAE / bias, £/MWh

| | chain X | leg P (real gas running) | composite (gas running from the chain's residual) |
|---|---|---|---|
| pre | 4.89 / −0.95 | 3.06 / −0.30 | 3.51 / −0.75 |
| crisis | 17.02 / −1.50 | 9.44 / −1.78 | 13.78 / −1.09 |
| post | 10.38 / +8.23 | 6.97 / +6.16 | 11.92 / +11.75 |

For comparison, the gas-only nulls are 5.4 / 24.5 / 6.7 on TTF, and 17.44 in the crisis on SAP.

## What it says

1. **Given how much gas really ran, a price that is a multiple of the floor beats every comparator in every
   regime**, out of sample in the crisis and after it. Post-crisis MAE falls from 10.38 to 6.97 and crisis MAE
   from 17.02 to 9.44. This is a diagnostic, not a buildable chain: real CCGT is a record observable.
2. **The leg P bias that remains is on the low-gas days.** On the 241 post-crisis days under 6 GW, the residual
   is +13.78, which is about £4.7 of the +6.16 [calc: 241 × 13.78 ÷ 708]. The pre-crisis record has 62 such
   days, and the line extrapolates through them. That is S4's miss: the depth below 6 GW is a shape the
   training window barely contains. It is not evidence against the multiplicative form at 6-14 GW, where §1b
   shows the ratio holds.
3. **The chain's residual demand cannot produce a low-gas day.** Fitted on pre-crisis, c_hat never falls below
   6 GW in any regime, against 241 real post-crisis days. Leg H is nearly flat in r, because the
   pre-crisis record moves CCGT on things the chain's residual does not hold: coal, nuclear by year, and pumped
   storage. Net imports are already in X's residual. After the crisis it overstates gas running by 3.1 GW on average. This is the larger term:
   the composite's post bias (+11.75) is about twice leg P's (+6.16).
4. **Before and during the crisis the composite already beats the shipped chain** (3.51 against 4.89, and 13.78
   against 17.02). It also beats both nulls there. It loses after the crisis, for reason 3.

## Decision

**The filed rule fires (b).** S1 missed on its bias leg, by £0.16, and the rule is applied as filed: the
multiplicative form is not cleared out of sample, and the shape arm returns. **Said plainly beside it:** the
rule did not foresee S5 and S6 holding as strongly as they did. The next build is therefore two arms, in this
order, each pre-registered.

- **Gas running from residual demand first** (point 3, the larger term). What displaces gas after 2022 enters x:
  nuclear by year (§4), imports (already in X), and storage. This needs K8 work on embedded generation and
  batteries before the arm.
- **The shape arm second**, fitted with low-gas days in sample. It must hold point 1's 6-14 GW ratio as a
  control.

Nothing ships from this arm.

Reverse: delete this record.
