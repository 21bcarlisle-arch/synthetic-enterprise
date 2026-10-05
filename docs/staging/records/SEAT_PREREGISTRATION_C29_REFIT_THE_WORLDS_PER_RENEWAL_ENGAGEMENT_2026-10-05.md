# Pre-registration — refit the world's per-renewal engagement to Ofgem's sustained-engagement control arm

*Delivery seat, 2026-10-05, claim `c29-refit-the-worlds-per-renewal-engagement-to-ofgems-sustained-engagement-control`.
Written BEFORE the fit was run. Results go in the finding beside it.*

## What is measured, and how

The same instrument as `docs/market_research/does_a_households_renewal_engagement_persist.md` §2:
20,000 synthetic ids, each through `active_renewal_probability_for_customer(household_of(id))`
(archetype × channel). The 3+-year default cohort is each id weighted by (1−p)³. The 17-month window
is one anniversary for sure plus a second with probability 5/12. Persistence is
P(choose at A2 | chose at A1) ÷ P(choose at A2 | did not), inside the cohort.

## Three moments, three unknowns

1. **Population mean per-renewal p ≈ 0.35.** Held, not fitted. It is the sourced
   "fixed at expiry → active switch ~35%" (`svt_rates_active_passive_2016_2025.md` §4) that the
   current triple was tuned to. Holding it keeps the aggregate where it was; this refit moves WHO
   chooses, not how many.
2. **Cohort 17-month choose rate ≈ 0.33** (Ofgem 2020 control arm, n=5,000).
3. **Within-cohort persistence ratio ≈ 0.94, and at most ~1.2** (31% vs 33%; the 95% interval on the
   31% is about 23–39%, so ~1.18 is the ceiling the source allows).

Shares stay 0.45 / 0.35 / 0.20 (R13). Order stays ACTIVE ≥ PASSIVE ≥ DISENGAGED.

## Predictions

- **Replication first.** The current triple reproduces the research note: 0.149, ×2.7, mean 0.347.
  If it does not, the instrument differs from the note's and nothing below is read.
- **A monotone triple meeting all three exists.** By hand, ignoring the channel: PASSIVE and
  DISENGAGED end up close together, both near 0.20, and ACTIVE near 0.55. The persistence ratio comes
  out at about 1.1–1.2, NOT 0.94. ACTIVE's share of the cohort and the channel multiplier both add
  dispersion that the source does not have, and holding the aggregate keeps ACTIVE high.
- **What the fit cannot do.** It cannot reach ×0.94 while the mean is held and ACTIVE ≥ PASSIVE.
  Any persistence the world keeps is at least the channel's. If the best ratio is above 1.2, that is
  a finding against the channel multiplier or the held aggregate, and I report it rather than pick.
