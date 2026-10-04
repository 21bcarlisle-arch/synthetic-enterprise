**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# EP1: the fuel split carries most of the forward-margin ranking, and subtracting cost to serve partly erases it

Claim `ep1-cost-to-serve-costs-margin-ranking-fuel-stratified-control`. The pre-registration is
`records/SEAT_PREREGISTRATION_EP1_COST_TO_SERVE_WITHIN_FUEL_SPLIT_STRATA_2026-10-01.md`, filed before any
stratified number was computed. The instrument is `/tmp/ep1s/ctl.py`'s, with the stratum key
widened (scripts `/tmp/ep1s/strat.py`, `mech.py`, `ci.py`). The population is 300 later snapshots,
with 296 kept in strata of at least 3. Strata are 164 single-fuel and 136 dual-fuel snapshots; 297
are resi.

## Results against the predictions

| | Prediction | Result |
|---|---|---|
| P1 | within-stratum sp(I1, I2) ≥ 0.95 | **0.9988.** Within cutoff only it is 0.9588. Leg-months ÷ account-months is exactly 1 or 2 on every row, so cost to serve per settled year is a pure per-leg constant. |
| P2 | within-stratum gap I2 − I1 in [−0.02, +0.02], CI contains 0 | **−0.004, cluster CI [−0.017, +0.009]. HELD.** |
| P3 | cutoff-only gap on the kept rows still > +0.03 | **+0.065 [+0.033, +0.098]. HELD.** It reproduces +0.062 [+0.031, +0.099] on all 300 rows. |
| P4 | dual-fuel forward gross outgrows its to-date rate more than single fuel does | **Not supported.** Median to-date → forward gross is +112/yr for single fuel and +109/yr for dual fuel. |

**The cause is attributed: the whole +0.062 lives BETWEEN fuel strata.** Within a stratum,
subtracting cost to serve is a constant shift and costs nothing.

## What the control showed that was not asked

- **The leg count on its own ranks forward net margin better than either margin rate:**
  - legs alone: within-cutoff +0.545, cluster CI [+0.40, +0.65];
  - gross rate I2: +0.451;
  - the belief's input I1: +0.387.
- **Within a fuel stratum, the to-date margin rate barely ranks forward net margin:**
  - I1 reads +0.191, CI [−0.01, +0.38];
  - I2 reads +0.188, CI [−0.02, +0.37].
- **This corrects the earlier finding's §3.** It read "the belief DOES rank forward margin (+0.427)"
  and "what the belief knows about an account's value is margin persistence". Most of that is the
  belief knowing which accounts are dual fuel. Margin persistence within a fuel type is weak and
  not distinguishable from zero at this n.
- **Sweeping the per-leg offset k in I2 − k·L is monotone.**
  - At each k, sp vs the forward net target reads:

    | k (£/yr per leg) | −110 | −55 | 0 | 27.5 | 55 (= I1) | 82.5 | 110 |
    |---|---|---|---|---|---|---|---|
    | sp | +0.504 | +0.490 | +0.451 | +0.425 | +0.386 | +0.310 | +0.204 |

  - Ranking improves the more a dual-fuel account is *credited*.
  - The leg count carries forward-margin information the to-date rate does not. Cost to serve
    pulls the strata together and throws some of that away. That is why the gross rate wins, even
    against a target that carries the same £55/£110.

## What this does and does not license

- **Cost to serve is correct accounting.** It is a pure per-leg constant, and it is in the target
  too. Removing it from EP1's margin would be the wrong fix: it would rank better and value worse.
- **The defect is in the forecast.**
  - EP1 projects an account's to-date net rate forward as its future rate.
  - That rate carries little within-fuel-type information.
  - The fuel split it ignores carries more.
- A company-side forecast that uses the fuel split as a covariate is the candidate. A supplier
  knows its accounts' legs, so it is wall-clean. **It is not built.** In-sample attempts are not
  evidence:
  - a level-space OLS (fn ~ I2 + L) is too noisy to use, b CI [−0.21, 1.46];
  - shrinkage to the stratum mean with that b read +0.400, worse than I2.
  - Any such forecast must be graded out of sample (leave-one-cutoff-out) and pre-registered.
- **Still open:** why dual-fuel accounts out-earn their to-date rate *in rank* when the medians
  move alike. Candidates are dispersion (single-fuel forward rates spread wider) and the
  composition of later cohorts. Neither is measured.
