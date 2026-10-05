**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# Pre-registration: B11 slice 2, attributing why the per-customer and flat verdicts reverse between two books

Written 2026-10-05 before any number below was computed. Claim
`b11-second-slice-attribute-the-two-books-verdicts`. Results go in a separate finding. This file
is not edited after the runs.

## What the "seeds" leg can and cannot be

Every run output on disk since 2026-10-04 is deterministic. The six `70dee3c7c` runs and the
`77bf72bab` run hash identically on their 2018 `per_customer_monthly`. Re-running a commit gives
the same book, so "the same code on two seeds" needs a book seed. A non-default book seed is
`EP17_varied_population_draw`, the director's open `whether-per-customer-pricing-beats-a-flat`
row, refused by `tools/book_seed_authorisation.py` until he records the activation file. This
slice does not run it. DIRECTION.yaml puts B11's attribution FIRST so that it can say whether
book count is the binding variable.

The between-commit leg substitutes for it. Hourly production runs exist for many commits between
book B (`fe895db3a`, 2026-09-09) and book A (`77bf72bab`). Each run is deterministic, so each
adjacent pair differs only by the code and world that landed between them. Grading the backtest
on each, in commit order, locates where the margin verdict flips.

## Test 1: the filed hypothesis (crisis-margin carry-forward)

Book A, cut 2022. Filed result: flat better on margin by £115 (17, 214).

Hypothesis (from the B11 first-slice finding): the per-customer rule loses at the late cut
because its credibility weight carries each account's 2021–22 crisis margin forward, and that
margin does not persist.

Arms, all at cut 2022 and graded over 2023-01 onward on the same accounts:
- **(b) deviation-early** (the test): per-customer = segment mean fitted through 2022 + w × (own
  − segment), with own, segment and k all taken from 2016–2020. The level is the flat rule's, so
  only WHICH accounts sit above or below their segment comes from the early years. With the
  early window equal to the cut, this is exactly the shipped formula.
- **(a) literal**: the whole per-customer margin (own, segment, k) fitted on 2016–2020; flat
  fitted through 2022. Reported, but it also moves the level, so it is two variables.

**Prediction for (b):** the 2022-cut margin loss disappears, meaning the interval straddles zero
or favours per-customer. Confidence about 60%. Reasoning: crisis-year account margins scale
volume by a per-kWh margin whose sign flipped in 2021–22. Volume persists, so the 2016–20
deviations should place accounts in 2023–25 better than the 2021–22 ones do.
**Refuted if** (b) is still "flat better". In that case pre-crisis deviations do not persist
either, and the carry-forward is not the cause.

**Prediction for (a):** worse than (b), because the 2016–20 level is far from the 2023–25 level.
Probably "flat better".

## Test 2: where the cut-2020 margin verdict flips between book B and book A

Every per-commit run output on disk from `fe895db3a` to `77bf72bab` (one per commit, the latest
when there are several), graded at cut 2020.

**Prediction:** the flip is not gradual. It sits at one or two commits that change the book's
SIZE or composition (graded count 72 → 53), not at commits that change only prices. Confidence
about 55%. **Refuted if** the margin difference drifts across many commits while the graded count
stays fixed, or if it flips at a commit that leaves the graded count unchanged.

For each run the record carries graded n, the margin difference with its paired 95% CI, and the
Brier difference with its CI.
