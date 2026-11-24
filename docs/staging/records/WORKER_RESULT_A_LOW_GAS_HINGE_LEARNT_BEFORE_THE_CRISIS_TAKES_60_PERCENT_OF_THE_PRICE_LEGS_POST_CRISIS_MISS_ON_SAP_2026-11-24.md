**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: a low-gas hinge learnt before the crisis takes about 60% of the price leg's post-crisis miss, on SAP (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in
`docs/staging/records/WORKER_PREREG_DOES_A_LOW_GAS_HINGE_LEARNT_BEFORE_THE_CRISIS_CARRY_THE_PRICE_LEGS_POST_CRISIS_MISS_ON_SAP_2026-11-24.md`
(`1df5c3237`), which was pushed to origin before the probe ran. Probe `/var/tmp/shape_sap/probe.py`, sha256
`053d6857a305b9c1…`, unchanged. It ran in a worktree at `1df5c3237`. There was no `sim/` or `simulation/`
change since the 2025 arm's `42ec42e7c`. Output is `/var/tmp/shape_sap/out.json`. **Nothing in `sim/` changes.***

## Outcomes (monthly, demand-weighted, £/MWh: MAE / bias)

Leg P on real CCGT running:

| Arm | hinge coef | pre | crisis | post | post without 2025 | 2025 |
|---|---|---|---|---|---|---|
| S0 (control) | — | 3.06 / −0.30 | 9.44 / −1.78 | 6.97 / +6.16 | 6.45 / +5.79 | 8.55 / +7.25 |
| **S1** (pre only) | −0.1014 | 3.07 / −0.31 | 9.33 / −3.14 | **4.89 / +2.44** | 4.62 / +2.12 | 5.68 / +3.43 |
| S2 (leave one year out) | −0.096 to −0.109 | 3.08 / −0.43 | 10.47 / −5.05 | 4.85 / +2.49 | 4.53 / +2.15 | 5.81 / +3.49 |
| S3 (in sample) | −0.1024 | 3.06 / −0.44 | 9.60 / −3.62 | 4.82 / +2.33 | 4.48 / +2.04 | 5.83 / +3.18 |

The composite, on the chain's own gas running (Y1's c_hat):

| Arm | pre | crisis | post | post without 2025 | 2025 |
|---|---|---|---|---|---|
| S0 | 4.06 / +0.02 | 14.05 / −1.71 | 8.17 / +7.04 | 7.33 / +5.83 | 10.67 / +10.67 |
| **S1** | 4.04 / +0.06 | 13.76 / −2.39 | 7.94 / +3.63 | 7.21 / +1.57 | 10.12 / +9.84 |

Post-crisis ratio of price to floor by real CCGT band (fit against record):

| CCGT GW | days | S0 | S1 | record |
|---|---|---|---|---|
| 0-4 | 90 | 0.865 | 0.611 | 0.569 |
| 4-6 | 151 | 0.903 | 0.808 | 0.801 |
| 6-8 | 109 | 0.951 | 0.964 | 0.964 |
| 8-14 | 251 | 1.038 | 1.041 | 1.019 |
| 14+ | 107 | 1.268 | 1.267 | 1.174 |

| # | Prediction | Outcome |
|---|---|---|
| H-P0 | S0 reproduces the 2025 arm's rows | **Held**, to every printed figure, leg P and Y1 composite |
| H-P1 | S1's hinge coefficient is in [−0.12, −0.03] | **Held.** −0.1014 |
| H-P2 | S1 post bias in [+1.0, +4.5]; MAE in [4.5, 6.5] | **Held.** +2.44; 4.89 |
| H-P3 | S1 pre MAE within ±0.15 of 3.06 | **Held.** 3.07 |
| H-P4 | S1 crisis bias falls by £0.5-3.5 | **Held.** By £1.36, to −3.14 |
| H-P5 | S2 post bias within ±£2.5; MAE no higher than S1's | **Held, at its edge.** +2.49; 4.85 against 4.89 |
| H-P6 | S3's coefficient is more negative than S1's | **Held, but only by 0.001.** That is effectively equal, and it is the finding |
| H-P7 | S1 composite post bias falls by £1.0-4.0 | **Held.** By £3.41, to +3.63 |

Eight of eight held. The predictions were informed by the §1b table, as the pre-registration says, so
getting all eight right shows the table was read correctly. It is not evidence of foresight.

## What the rule says

- **(a) fires.** Fitted on the 62 pre-crisis days under 6 GW alone, the hinge takes post-crisis bias from +6.16
  to +2.44 and MAE from 6.97 to 4.89. Pre-crisis MAE moves by £0.01. **The low-gas depth is a stable multiple
  of the floor:** about −0.10 of the floor per GW below 6 GW. It is the same whichever year is left out
  (−0.096 to −0.109) and the same in sample (−0.102). It is a build term for the price leg.
- **It fits the record by band.** On post-crisis days the hinge brings 0-4 GW from 0.865 to 0.611 (record
  0.569) and 4-6 GW from 0.903 to 0.808 (record 0.801).
- **What is left after the crisis (+2.4) sits at the top.** On 107 post-crisis days above 14 GW, the leg prices
  at 1.27 of the floor where the record clears at 1.17. This is §1b's "post-crisis dip at 14-18 GW". It is
  not attributed.
- **The cost is in the crisis.** Bias goes from −1.78 to −3.14, and with the year left out to −5.05, while MAE
  barely moves (9.33 in S1; 10.47 in S2). The crisis's low-gas days (76) get a deeper discount than they
  cleared at (§1b: 0.62 at 0-4 GW, 0.91 at 4-6 GW).
- **On the chain's own gas running it helps the bias, not the MAE.** The composite post bias goes from +7.04 to
  +3.63, and from +5.83 to +1.57 without 2025. MAE moves by only £0.2, because the chain's low-gas days are
  not the record's. 2025 keeps +9.8. That is the +1.4 GW wind level the 2025 arm left.

## Caveats

- The 6 GW knot was read off the §1b table before the run. A different knot was not tried.
- Real CCGT running is a record observable. Here it diagnoses the leg. A forward world prices from the chain's
  own gas running, which is what the composite row shows.
- This is leg P from the two-leg diagnostic form. The shipped chain is one-leg (price from residual demand).
  The build carries the hinge in whichever form ships. In the one-leg form the hinge's x is the residual
  that sets gas running, not real CCGT.

## Next, still item 4

1. The 14 GW+ post-crisis top (1.27 against 1.17, 107 days), with its prediction filed first.
2. The shippable record-years build: SAP, the annual net-export level, demand by year, solar out, the 2025
   basis rule, and now the low-gas hinge. This build is carried by the SAP splice finding's place in the
   switch order.

Reverse: delete this record.
