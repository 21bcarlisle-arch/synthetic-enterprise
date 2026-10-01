**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# EP1's remaining over-valuation is the margin divided by renewal points, and H2 counts survival twice

Claim `ep1-remaining-overvaluation-decomposed`. The prediction and every number are in
`docs/staging/records/SEAT_PREREGISTRATION_EP1_REMAINING_OVERVALUATION_MARGIN_TERM_VERSUS_LIFETIME_TERM_2026-10-01.md`.
The ledger row is not re-measured: this is a diagnosis on the `run_output_latest.json` graded set,
and nothing in the company code changed.

## What the residual is

On the belief HEAD's code actually produces (66 graded leavers, gap **1.173**), the error splits
as follows. Belief = margin × discounted life-years; realised = realised annual margin × realised
tenure.

- **Margin over-states: +£11.1k.** On 43 of the 45 over-stating rows it is the larger term. The
  belief's annual margin averages £115 against £55 realised. Its ranking carries almost nothing:
  Spearman(m_b, m_r) is 0.12.
- **Lifetime under-states: −£8.2k.** Selection on exit pushes the other way (+£13.6k: every
  graded row is a leaver), but discounting, the pre-snapshot window and a truncation in H2 together
  outweigh it.

So the next build is the margin, not the hazard, and not the harness.

## Defect 1 — the margin is a cumulative total divided by a count of renewal points

`saas/clv_model.build_clv` sets `avg_annual_net_margin_gbp = net / len(churn_risk[account])`,
and EP1 reads it as an ANNUAL margin (`customer_value_view._clv_observables`).
`WORKER_FINDING_THE_BOOK_VALUES_NINE_ACCOUNTS_AND_PUBLISHES_EIGHT_AND_DIVIDES_BY_RENEWALS_2026-08-17`
found exactly this and queued it at +11–20% on the mature book. It was left alone because
`build_clv`'s sBG lifetime is in renewal periods too, so that module is internally consistent.
**That defence does not cover EP1.** EP1 multiplies the per-renewal-point margin by its OWN
per-YEAR life table, so the units disagree. On the young book EP1 grades, every row has P = 1
renewal point against 1.67 settled years. That is a ~70% over-statement, not 11–20%. Dividing by
settled years alone (arm A) takes the gap from 1.173 to 1.036, and Σ(b − t) from +£2.9k to −£4.9k.

## Defect 2 — H2 weights by survival AND truncates at the expected tenure

`survival_discounted_value_by_year_gbp` sums Σ S(t)/(1+r)^t, but only out to t = E[T]. The
expected value of a margin under a hazard is the untruncated sum. Survival weighting already
prices the exit, and stopping at E[T] prices it again. At h = 0.2, undiscounted, it counts 2.69
life-years where the expectation is 4.00 (Σ_{t≥1} S(t)). On these rows it is 3.36 against 5.08.
Fixed alone (arm B) it RAISES the gap to 1.310, because it adds life to the over-stated margin.
**The two defects hide each other.** The pair (arm C) gives 1.066 with the level near balanced
(37/66 over, Σ −£2.4k).

## What survives both fixes

Gap ~1.07 with Spearman ~0.12. With the level removed, the remainder is per-account information
the belief does not have. A first-year margin does not rank a lifetime margin. That is the
question after these two, and it is not one a constant can answer.

## A correction beside an earlier claim

The life-table headline (1.558 → **1.275** on 69 rows, landed `7e2503507`) was measured on a
RECONSTRUCTED belief. `/tmp/se_ep1_measure_lt.py` divides H1 by `sdv(1, rec['hazard'], r, 1)`,
but H1 is priced on the latest churn probability over the contract term. The margin it recovers
is off by up to 7.1×. Its hazard side is exact, so the comparison BETWEEN hazard arms holds in
direction. The level does not: the true life-table belief is 1.173 on the 66 rows that have a
table. The next re-measurement should read `annual_margin_gbp` and H2 off a rebuilt view, never
re-derive them from H1.

## Next (handed on)

EP1 values on a margin per SETTLED YEAR, computed in `customer_value_view` from the company's own
records (the view already has `observed_tenure_positions`'s span), and H2 sums survival
untruncated. Land both together and say so, because either alone moves the level the wrong way
on one side. `build_clv`'s own unit question (08-17 item 1) stays its own. The gap is a
diagnostic, never a target: both changes are definitions, and the 1.07 is reported, not aimed at.

## Landed together (2026-10-01, claim `ep1-margin-per-settled-year-and-untruncated-h2`)

Both fixes are code now. `customer_value_view.settled_year_margins` gives EP1 its margin per
settled year: cumulative `net_of_all_costs` over the account's distinct settled months ÷ 12.
Who gets valued is unchanged: an account `build_clv` does not value is still blank under its
named reason. `survival_discounted_value_by_year_gbp` is the untruncated Σ S(t)/(1+r)^t, and the
two constant-hazard H2 paths now call it, so H2 has one definition. On the rebuilt snapshots
the result is gap 1.066 on 66 rows, Spearman 0.122, Σ(b − t) −£2.4k. That matches arm C exactly
(P10). The harness's `recover_hazard` inverts the OLD truncated ratio. It is reached only for
snapshots that publish no hazard, which no production snapshot now does, so it still reads the
legacy artefacts it was written for. `build_clv`'s own unit (08-17 item 1) is still its own
question.
