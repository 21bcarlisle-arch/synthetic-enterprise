# Pre-registration: a split-path control variate for the selection residual

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

Written 2026-10-03, before any run that carries the per-renewal record (372802d3f) has finished.

## Why

Over the six 2025 seeds, the selection residual's variance is the sum of independent accounts
(design effect 1.02), and it sits on SPLIT PATHS. A split is a renewal where the shared churn roll
falls between the two arms' P(stay), so one arm keeps the account and the other loses it. Per
seed, split accounts carried mean -4,753 and sd 3,677; accounts priced differently on the same
path carried +1,248 and sd 1,411. A split is a coin flip on an account's whole remaining life.
How often splits happen is known in advance: at each renewal, P(split) = |P_v - P_l| exactly,
because the roll is shared and uniform.

## The estimator (a control variate, unbiased by construction)

For each renewal r that both arms face on the same date:

- `x_r` = (value arm kept) - (level arm kept), in {-1, 0, +1}, realised;
- `e_r` = P_v - P_l, its exact expectation given the two arms' P(stay);
- `w_r` = an EX-ANTE size, fixed before the roll: the value arm's own believed expected value at
  that renewal (`believed_expected_value_gbp`, logged per renewal).

C = sum over r of w_r (x_r - e_r) has expectation zero whatever the arms do. The adjusted
residual is S* = S - beta·C, with beta = Cov(S, C) / Var(C) pooled across seeds. Its mean
equals S's mean (up to the small bias of an estimated beta), and its variance is
Var(S)·(1 - rho²).

## What has already been tried, so it is not re-counted as new

On the six seeds, using the FIRST renewal only (the only one recorded then) and w = 1: rho = 0.19
seed-level and 0.31 account-level, an sd reduction of 2%. The unsigned version gave rho = -0.01. An
earlier "multiply split accounts by |dp|" figure was BIASED toward zero (unsplit accounts carry the
same chance) and is withdrawn; it is not this estimator.

## Predictions

- **Q1.** On runs carrying every renewal and w = believed EV, seed-level rho is at least 0.5, i.e.
  sd falls by at least 13%. I hold this weakly: the first-renewal-only trial gave 0.19, and the gain
  rests on later splits plus value weighting carrying most of the split variance.
- **Q2.** The adjusted mean stays inside one raw standard error of the raw mean on the same seeds.
  If it moves further, beta is being fitted on too few seeds to be trusted, and the estimator
  stays a diagnostic.
- **Q3.** If Q1 fails, the noise is NOT mostly the split coin after all, and the decomposition's
  reading is wrong. That gets said beside this file, not quietly dropped.

## What it needs that does not exist yet

`believed_expected_value_gbp` joined per renewal into the A/B artefact (the belief fields landing
carries the debt figures, and this adds one more), and both arms' per-renewal P(stay), which
372802d3f now records.
