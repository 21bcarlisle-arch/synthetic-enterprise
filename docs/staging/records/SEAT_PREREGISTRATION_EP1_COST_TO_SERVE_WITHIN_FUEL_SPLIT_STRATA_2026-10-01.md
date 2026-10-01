**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# Pre-registration: does the per-leg cost-to-serve step explain why the gross rate out-ranks EP1's net input?

Claim `ep1-cost-to-serve-costs-margin-ranking-fuel-stratified-control`. The draw's duplicate-work
note named this same id as "already held". That was this draw's own write: no rival seat or
`surgical_land` held it (`ps`, 05:35). Filed BEFORE any stratified number is computed.

## What is already measured (the premise)

The source is `SEAT_FINDING_EP1_ROUTE_DOES_NOT_RANK_TENURE_..._2026-10-01.md` §4. It used 300
later snapshots, within-cutoff Spearman and paired per-account cluster CIs. Against the forward
margin net of cost to serve, the gross rate I2 out-ranks the belief's input I1
(`settled_year_margins`) by **+0.062 [+0.031, +0.099]**.

## Say what cost to serve IS here before splitting on it

I read `saas/cost_to_serve.py` before filing. Cost to serve is **fixed overhead only**. It is
£55/yr per leg for resi (SME £120, I&C £500), and it accrues per settlement period of each leg.
`revenue_gbp` is in the signature but unused. There is no bad-debt term in this figure, despite
`BAD_DEBT_RATE` in the same module. So per settled year, an account's cost to serve is
55 × (its leg-months ÷ its distinct account-months). That is 55 for single fuel and 110 for dual
fuel when both legs settle in the same months, and something else when they do not.

## Instrument

This reuses `/tmp/ep1s/ctl.py` unchanged: the same run (`/tmp/ep1bk/run.pkl`), the same rows
(`snaprows.json`), the same I1, I2 and forward net target `fn`. The one change is the stratum key
of the within-stratum Spearman: (cutoff) becomes (cutoff, legs at the cutoff, segment). Legs are
the commodities the account's records settle up to the cutoff. A stratum needs n ≥ 3 to count.
The cluster bootstrap resamples accounts, 1000 draws, seed 0.

## Predictions

- **P1 — manipulation check (credence 90%).** Within (cutoff, legs, segment), sp(I1, I2) ≥ 0.95,
  because inside a stratum I1 should be I2 minus a near-constant. If P1 fails, cost to serve per
  settled year is not a per-leg constant. Leg-month asymmetry (one leg settling fewer months)
  then becomes a candidate in its own right.
- **P2 — the hypothesis (credence 65%).** Within strata, the gap sp(I2, fn) − sp(I1, fn) lies in
  [−0.02, +0.02] and its cluster CI contains 0. If so, the whole +0.062 lives BETWEEN fuel strata,
  and the fix is how cost to serve enters EP1's margin.
- **P3 — the population is unchanged (credence 85%).** On the exact rows the stratified grade
  keeps, the cutoff-only gap still reads above +0.03. This rules out the alternative where
  stratifying changes the answer only by dropping rows.
- **P4 — the mechanism, if P2 holds (credence 40%; I do not know the sign of the effect).** The
  same 55·L sits in both the input and the target, so subtracting it should HELP across strata.
  If it hurts, something else differs between strata. My guess is that dual-fuel accounts' forward
  gross rate exceeds single-fuel's by more than their to-date rate does. I will print the
  median I2, I1, fr and fn by legs to see.

If P2 fails, the per-leg step is ruled out as the cause, and the finding says the cause is still
open.
