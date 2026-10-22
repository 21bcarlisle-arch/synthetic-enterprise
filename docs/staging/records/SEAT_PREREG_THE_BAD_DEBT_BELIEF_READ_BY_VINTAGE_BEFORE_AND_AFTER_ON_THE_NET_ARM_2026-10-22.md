**Severity:** RECORDED · **Lane:** 0 delivery · **Direction item:** `the-bad-debt-belief-cannot-go-negative`

# Pre-registration: the own-book bad-debt belief, whole-year charge against vintage reading, per cell

Written 22 Oct 2026, before any run of the fix. The fix is in the same landing as this file:
`company/pricing/default_belief.py` now learns each account-year's loss as the provision on that
year's own bills plus the write-offs against them, re-read at every later resolution of the
account. It used to learn the year's whole charge (closing less opening provision plus write-offs).
Knowledge: `docs/market_research/bad_debt_provisioning.md`, *The expected loss on new billing*.

## The question

On the retention-netting `net` arm's book (`tools._c29_retention_engagement_arm net`,
`CURRENT_POLICY` plus `retention_nets_bad_debt=True`), at every renewal that asks
`default_belief_rate`, what does each arrears-state cell's belief read under the old observation
and under the new one? The book and the decision dates are the same for both. The probe wraps the
consumer's door and computes the old belief from the pre-fix module on the same ledger. The run
prices with the new one, so its path is not the `1ac35d918` run's. The one variable is the
observation, on one book.

## Predictions (written before the run)

- **P1, no negative belief after.** 0 calls read below 0 under the new observation. The invariant
  refuses one, so a run that finishes is the evidence. Under the old observation, at least 1 call
  reads below 0 (the `1ac35d918` pair saw 3 guard rows). Refuted if the old observation never goes
  negative on this book: the defect would then not be reproduced here, and the fix would be
  untested at real inputs.
- **P2, the whole book does not move.** An account's latest vintage readings sum to its old
  telescoped charge at the same resolution, so the `*|*` charge share at report end differs by less
  than 0.0005 between old and new. Refuted at 0.0005 or more: something is lost or counted twice.
- **P3, the release moves from the arrears cells to the clean ones.** A household that incurs
  debt in a clean year and pays it down the next books the release, under the old observation, in
  the arrears cell it started the second year in. Under the new one the release lowers the clean
  year's reading. So at report end the `in_arrears_steady` and `worsening` cells' shares rise, and
  `no_debt` falls. Refuted if either arrears cell falls, or `no_debt` rises.
- **P4, the in-course effect is small.** The share of the new `*|*` charge that sits on
  pay-on-receipt bills under 30 days old at their reading is under 15%. This is the GAP the page
  names: a year-end reading carries a bill inside its terms. It is not measured by the probe as
  built, so P4 is marked UNGRADED unless the probe is extended. It is written here so that it
  cannot be added after the answer is known.

## What would change

P1 holding, with P2 holding, makes the fix the default: it already is, behind no switch, because
`own_book` is `CURRENT_POLICY`'s belief. P2 refuted reopens the build. P3 refuted means the
release was not where the defect said it was, and the record must say what did drive the negative
cells.
