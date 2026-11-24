**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the chain's 2025 gas-running miss is mostly the basis of the fleet it is clamped to (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in
`docs/staging/records/WORKER_PREREG_IS_THE_CHAINS_2025_GAS_RUNNING_MISS_THE_BASIS_OF_THE_FLEET_IT_IS_CLAMPED_TO_2026-11-24.md`
(`42ec42e7c`), which was promoted to origin before the probe ran. Probe `/var/tmp/r2025/probe.py`, sha256
`bc4d8129f667a174…`, unchanged. It ran in a worktree at `42ec42e7c`. Output is `/var/tmp/r2025/out.json`.
**Nothing in `sim/` changes.***

## Inputs printed by the run

On 2025's 158 days the chain's unscaled wind averages 4.57 GW and AGWS averages 9.01 GW. FUELHH is
0.812 × AGWS, about 7.31 GW [calc]. 2025's scale is 0.812 in W1, 1.221 in Y1 and 1.599 in Y2.

## Outcomes (c_hat − c in GW; composite in £/MWh, monthly, demand-weighted)

| Arm | 2025 c_hat − c | 2025 days < 6 GW (record 48) | 2025 composite MAE / bias | Post c_hat − c | Post composite MAE / bias |
|---|---|---|---|---|---|
| W1 (control) | +3.27 | 0 | 15.64 / +15.64 | +0.71 | 9.41 / +8.29 |
| **Y1** | **+1.40** | 18 | 10.67 / +10.67 | **+0.29** | **8.17 / +7.04** |
| Y2 (oracle) | −0.33 | 43 | 7.94 / +6.27 | −0.09 | 7.49 / +5.94 |

The pre, crisis and post-without-2025 rows are identical in all three arms: pre R² 0.513, crisis −0.12 GW /
−1.71, and post without 2025 −0.02 GW at 7.33 / +5.83.

| # | Prediction | Outcome |
|---|---|---|
| Y-P0 | W1 reproduces the published W1 | **Held**, to every printed figure |
| Y-P1 | Y1's 2025 is in [+0.8, +2.2] GW | **Held.** +1.40, which takes 57% of the miss |
| Y-P2 | Y2's 2025 is in [−0.8, +0.8] GW | **Held.** −0.33 |
| Y-P3 | Y1's post is in [+0.15, +0.55] GW | **Held.** +0.29 |
| Y-P4 | The non-2025 rows do not move | **Held** |
| Y-P5 | Y1's post bias is £0.4-1.5 below +8.29 | **Held.** £1.25 below, at +7.04 |
| Y-P6 | Y2 runs gas under 6 GW on 10-48 of 2025's days | **Held.** 43 |

## What the rule says

- **(a) fires.** In W1, 2025's wind was scaled by 2025's FUELHH ÷ AGWS ratio. The wind it scaled came from
  2024's fleet, which sits on 2024's basis. Carrying the fleet's own basis takes 57% of 2025's miss.
  **Build rule: a clamped year inherits its source year's fleet and its basis together.** In the
  shippable form this is one line. The FUELHH scale belongs to the fleet's year, not the calendar year.
- **What Y1 leaves (+1.40 GW) is wind level, not another leg.** Y2 closes it with the chain's own daily
  shape. Y-P2 is close to true by construction, because Y2 sets the level in-sample. What it adds is that
  rule (c) does not fire: demand, solar and must-run in 2025 carry no miss of their own. The remaining
  1.7 GW of wind [calc: 7.31 − 1.221 × 4.57] is the calm-year curve together with the fleet growth after
  2024 that the clamp cannot see. On record years these two cannot be separated without a 2025 fleet
  from outside AGWS (DUKES 2025 is not yet published, and the trajectory clamps it). The build reports
  that +1.4 GW beside 2025's number.
- **With 2025's gas running right, its price miss is the price leg's.** Y2's 2025 composite bias is +6.27,
  against +5.83 for the post-crisis years without 2025. 2025 is not a special case of the price leg. That
  closes the 2025 candidate left unattributed in step B. What remains after the crisis is the floor
  multiple on low-gas days (§1b), the shape arm already named.

## Caveats

- 2025 is part of a year (158 days, January to early June) and calm (3.23 m/s town wind). The 57% figure is
  for this half-year, not a rate.
- Y2 is an oracle. It is not a build option, because a forward or part year has no FUELHH mean of its own
  to match.

## Next, still item 4

1. The shippable form (SAP, the annual net-export level, demand by year, solar out, wind on FUELHH) takes
   this rule when it is built. That build is carried by the SAP splice finding's placement in the switch
   order.
2. The price-leg shape arm on low-gas days (§1b). This is now the largest post-crisis term in every year,
   2025 included.

Reverse: delete this record.
