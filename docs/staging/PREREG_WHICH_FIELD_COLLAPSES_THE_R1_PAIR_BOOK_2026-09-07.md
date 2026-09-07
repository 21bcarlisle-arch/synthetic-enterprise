# PRE-REGISTRATION — which field collapses the R1 pair book, and why

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

**Written:** 2026-09-07, BEFORE the measurement, by the delivery seat.
**Claim:** `r1-ceiling-coverage-is-what-buys-a-magnitude`

## The question

A49's magnitude gate reads `magnitude_three_way_split.estimate` and gets `None`. The stated cause
is coverage: 164 households in the book, 69 carrying both fields of the winning pair, and at 69 the
three-way split gives 5.00 households per cell on the fit fold against the 8 `MIN_HOUSEHOLDS_PER_CELL`
requires, and 19 on the estimate fold against the 20 `MIN_FOLD_HOUSEHOLDS` requires.

`docs/staging/` records the direction's diagnosis: `perceived_bill_saving_gbp`,
`portfolio_premium_pct` and `mean_recent_margin_rate` are the fields that collapse 164 to 69. That
is a CLAIM TO CHECK, not a finding to build on. What follows is what I expect to find, written
before I look, so the record shows the experiment was designed before its answer was known.

## What I predict

1. The newest run output yields ~164 households under `observable_rows`.
2. The coverage is NOT uniform across the three named fields. I expect
   `perceived_bill_saving_gbp` to be the binding one, at ~69, because `run_phase2b` appends
   `churn_journey_log` only inside the priced-renewal branch — a household that never reaches a
   renewal window in the simulated span has no row carrying it at all.
3. `portfolio_premium_pct` and `mean_recent_margin_rate` come from a different log family
   (rate decomposition) and I expect them to cover a LARGER set than 69 — so the three-field
   intersection is set by `perceived_bill_saving_gbp` alone.
4. Therefore the fix is a WRITE-SIDE one: the fields must be emitted for every household the book
   holds, not only for those that happened to take a branch.

## What would refute each

1. A household count materially different from 164 refutes the frame — the collapse is then not
   the one described and the direction's arithmetic was computed on a different book.
2. If all three fields cover the same ~69 households, prediction 2 is wrong and the cause is a
   shared upstream gate (one branch, three fields), not three independent write sites.
3. If `portfolio_premium_pct` covers FEWER than 69, it is the binding field and I named the wrong
   one.
4. If every field already covers ~164 and the pair grid still gives 69, then the collapse is in the
   PAIR construction (`_pair_grid`'s per-pair intersection) and not in field coverage at all —
   which would mean the work is to widen a different seam entirely.

## What "done" means for this claim

Not "the estimate is no longer None" — that is a result I do not control and must not target.
Done is: **every household in the book that could carry the pair fields does carry them, the
coverage number is published, and whatever the gate then reads is reported honestly, including
`cannot tell`.** A magnitude that appears because the book got bigger is a finding; a magnitude
that appears because a threshold moved is a defect.
