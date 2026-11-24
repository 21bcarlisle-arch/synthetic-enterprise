**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: is the chain's post-crisis miss in its price leg, or in how much gas it runs? (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Filed and landed before the probe runs. The probe is `/var/tmp/mk25/measure_s.py`, sha256
`3cee28607dee55c223a00a781f77a6bd2a096ec64a7fb840ede1f009f8853f21`. It will run in a worktree at the origin
commit this lands on. **Nothing in `sim/` changes.***

## Why this arm, and not the shape arm the last record named

Electricity page §1b (this commit) bins the record on fixed 2 GW steps of real CCGT output. At a given
amount of gas running, SSP is the same multiple of the gas floor in all three regimes, within about 0.05
from 6 to 14 GW, while the floor moved fourfold. What changed after the crisis is the mix of days: 241 of
708 post-crisis days run under 6 GW of CCGT. So a new price-leg shape may be refitting a leg that already
has the right form. This arm separates the two legs first.

**Disclosed before filing:** the binned ratio tables in §1b were seen before these predictions were
written. What has not been seen is how a fitted form does out of sample, or the composite.

## Definitions

Arm X inputs as in mk24: SAP in the call and the refit, and real net export in the chain's demand. Floor =
(SAP + carbon × EF) ÷ 0.50. c = real daily mean FUELHH CCGT, in GW. Regimes: pre 2016-01..2021-06,
crisis 2021-07..2023-06, post 2023-07 onwards. MAE and bias are monthly and demand-weighted, as in mk24.

- **Leg P (the price leg, given real gas running):** SSP = floor × (b0 + b1·c + b2·max(0, c − 14)), least
  squares on PRE days only, then applied to every regime with real c.
- **Leg H (gas running, from the chain's own weather):** c_hat = h0 + h1·r + h2·r², where r is the chain's
  residual_mw ÷ 1000, least squares on PRE days only.
- **Composite:** floor × gP(c_hat). This is the chain with leg P as its price leg, and the gas it runs
  decided by its own residual demand.

## Predictions

| # | Prediction |
|---|---|
| S1 | Leg P, post: monthly MAE ≤ 7.0 (X: 10.38), and bias between +1 and +6 |
| S2 | Leg P, crisis: monthly MAE ≤ 15.0 (X: 17.02) |
| S3 | Leg P, pre (in sample): monthly MAE ≤ 4.89 (X's) |
| S4 | Leg P, post, on days with real c < 6 GW: mean daily residual between 0 and +12 (the chain's is about +25 on Q1). It is positive, because the line is extrapolated below the pre record's 4 GW |
| S5 | Composite, post: bias ≥ +5 (most of X's +8.23 survives) |
| S6 | Post: mean c_hat exceeds mean real c by ≥ 1.5 GW, and c_hat has fewer than half as many days under 6 GW as the record's 241 |

## Decision rule, filed now

- **(a) S1 and S5 hold.** The miss is in the leg that decides how much gas runs, not in the price leg's form.
  The next step is a K8 section, then an arm, on what displaces gas in residual demand after 2022: nuclear by
  year, embedded generation, batteries and pumped storage. Imports are already in X. The price leg's form is
  kept.
- **(b) S1 fails.** The multiplicative form is not supported out of sample, and the shape arm named in the
  CCGT-band record returns.
- **(c) S1 holds and S5 fails.** Both legs share the miss. Report it as it falls, with no build.

Nothing ships from this arm under any outcome. It decides which leg the build is in.

Reverse: delete this record.
