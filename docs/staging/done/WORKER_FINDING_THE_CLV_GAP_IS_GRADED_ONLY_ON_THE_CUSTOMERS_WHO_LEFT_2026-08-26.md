# The CLV gap is graded only on the customers who left, and the lifetime term it blamed is not the one that is wrong

**Severity:** HIGH — it mis-aimed a stretch of thesis-critical work
**Lane:** H_harness
**Rank:** FIXED IN THE SAME COMMIT. Filed as the record, not as a queue item.
**Class:** a scale error attributed to the estimator when the population was the cause
**Supersedes:** the "grade the lifetime term" direction recorded in the `18e8d215e` commit
message and in `docs/design/THE_VALUE_CYCLE_REALISED_AB.md` §"The loss is a horizon effect"

## What set this off, and why the wrong answer was so easy to reach

`EP1_clv_three_horizon` published `gap 2.5291` with `best_single_scale 0.204` and
`magnitude_inflated_accounts 27/33`: dividing every belief by five would beat no-skill, so the
error is in the LEVEL and not the RANKING. `couple_clv.magnitude_diagnostic`'s own docstring then
said what to do with that — a run of over-estimates "points R4 at the horizon, not the ranking" —
and the closing NTFY of 2026-08-26 committed the next stretch to the lifetime term on the strength
of it.

The docstring named one cause of a uniform scale error. There are two.

## What is on disk, measured not inherited

All figures below are `observed-with-evidence` (R9), reproduced by
`python3 -m tools.couple_clv` at `docs/reports/run_output_latest.json`.

### 1. The graded population is the accounts that left, and nothing else

`build_observations` counts an account only once its life has ENDED and excludes every
still-supplied account as `right_censored_lifetime`. That is unavoidable — you cannot know a
realised lifetime for a customer who is still alive — but it selects the population **on the
quantity being predicted**:

| population | n | mean realised (resi) |
|---|---|---|
| graded (life ended in the run) | 33 | £141.56 |
| excluded (still supplied) | 230 | £419.64 |

**2.96x, like for like within `resi`, and that is a LOWER BOUND** — the excluded side is censored
and still accruing.

The whole-book ratio is 45x, and that number is wrong to quote: this book's five I&C accounts
average £221,491 of lifetime margin, are all still supplied, and none is graded. I reached for the
45x first. `test_the_like_for_like_ratio_survives_a_segment_the_grading_never_touched` is that
mistake turned into a control.

### 2. The no-skill baseline is fitted on that same selected population

The divisor is "assign every account the MEAN realised lifetime margin" — £100.20, the mean of the
accounts that died. The company could not have formed that figure at belief time; the book it was
actually pricing was heading for a resi mean above £419. So `gap > 1` partly measures *a predictor
that already knows which accounts were short-lived, beating one that does not.*

A point-in-time-fair baseline (the mean realised value of accounts that had **already** ceased when
each belief was formed) gives **gap 2.193** rather than 2.529. The company's belief is still worse
than no-skill — this is not an acquittal — but 13% of the headline is the yardstick.

### 3. The lifetime term is not inflated. Measured two independent ways, it runs SHORT

Hazard belief against realised churn frequency, counted from `event_type` over 622 renewal
decisions — a belief against a **tally**, not against another probability:

| believed hazard | decisions | realised rate | believed/realised |
|---|---|---|---|
| 0.05 | 263 | 0.053 | **0.94x** |
| 0.08 | 95 | 0.011 | 7.60x |
| 0.29 | 12 | 0.083 | 3.48x |
| 0.38 | 56 | 0.161 | 2.36x |
| 0.41 | 135 | 0.111 | 3.69x |

The company **over-states** hazard in every elevated bucket, by 2.4x to 7.6x. An over-stated hazard
gives a SHORTER believed tenure and a SMALLER CLV. At portfolio level: mean believed tenure
**11.74 years** against a realised implied mean of **13.82**. Both directions agree, and both are
the opposite of the recorded hypothesis.

The reason a calibrated hazard still produced a 5x over-estimate on the graded set is line 1: all
33 graded accounts sat in the **h = 0.05 bucket, where the model is right to three decimal places
(0.05 believed, 0.053 realised)**. The harness then grades the model on precisely the 5% who left
and reports it as a five-fold over-estimate.

### 4. And the horizon carried no per-account lifetime information at all

Recovering the hazard from EP1's own published output — `tenure_expected / contract_term` depends
on the hazard alone, so it inverts without re-running anything or reading any private field:

**All 33 graded accounts recover to the identical hazard, 0.05: one distinct value, a flat 20-year
tenure for every account graded.**

So whatever ranking that CLV produced came **entirely from the margin term**. "The error is in the
level, not the ranking" was not a diagnosis of the lifetime term — the lifetime term had no
variance to contribute a ranking with. The hazard is `0.05 + 0.03 x bill_shock_count`
(`saas/churn_model.py`), a step function of one integer counter, and for 42% of all renewal
decisions in the run that counter is zero.

## What this is NOT

Not a wall breach. The recovered hazards match `customer_events["churn_probability"]`'s
distribution because both are the same company-side bill-shock formula; `simulation/customer_events.py`
records in its own comment that this field "was never the number the dice roll used". I checked
this before writing it down, having first mis-read the distribution match as the company reading
world truth.

Not an acquittal of the value arm. The A/B loss — **net −£93,555, enterprise value −£118,252 over
ten years** — is a realised P&L measurement over the whole book and carries none of this selection.
What changes is the *explanation*: the lifetime term is not the leading candidate and, on this
evidence, is not a candidate at all in the direction assumed. `THE_VALUE_CYCLE_REALISED_AB.md` had
already demoted it once in a later section (the standing charge missing from `expected_value_gbp`);
the summary I carried forward was quoting the superseded paragraph.

## What changed

- **`tools/clv_gap_selection.py`** (new, HARNESS): `selection_profile`, `hazard_calibration`,
  `lifetime_level`.
- **`tools/couple_clv.py`**: publishes all three beside `error_decomposition`; prints them next to
  the attribution line, because a reader who stops at that line is the reader this pair already
  misled; `baseline` and the published note now declare SURVIVORSHIP, not only the truth-window
  bias they already declared at length.
- **`magnitude_diagnostic`'s docstring**: the sentence that mis-aimed the work is replaced by one
  naming both causes.

**R10 class fix:** `test_the_scale_attribution_is_never_published_alone` fails if a future edit
emits `error_decomposition` without all three companions available — including if one is present
but silently unavailable, which would leave the same one-sided story in a different shape.

**R15:** 38 tests, six mutations proven to fire — the pairing control on a producer that stops
publishing selection and on the key being dropped; the constant-hazard control against one
hard-coded to say CONSTANT; the note control against a note with SURVIVORSHIP removed; the
selection control against a profile that cannot see a shift; the hazard control against a
calibration graded on a probability instead of an outcome. Every "fires on" test has a partner
asserting it stays quiet on a clean fixture. `recover_hazard` re-derives the closed form rather
than calling the company function it grades, with an agreement test between the two (TAUTOLOGY).

**R12:** every row carries "diagnostic, never a target". Nothing was tuned; no scale was applied.

## What remains open

1. **The baseline is still fitted in-sample.** Measured, declared, not changed — replacing a
   published divisor moves a headline, and that is a decision to take deliberately rather than
   inside a diagnosis commit. The point-in-time alternative and its number (2.193) are recorded
   above.
2. **The class beyond EP1.** `tools/couple_supply_start.py` normalises against "the no-skill
   baseline (predict the mean tenure)" and `couple_pb3_book_growth.py` and
   `couple_value_based_pricing.py` also publish an in-sample `g0`. Whether any of those grades an
   outcome-conditioned population is unchecked. The general rule — *a no-skill baseline computed on
   the graded population is not no-skill* — is what a ratchet across `tools/couple_*.py` would
   enforce.
3. **The tenure horizon's flatness is EP1's to fix, not the harness's.** A hazard that is a step
   function of one integer, zero for 42% of decisions, is why the horizon is constant. Grading it
   was worth doing; it is now graded, and it says the level is roughly right and the DISPERSION is
   absent. That is a different and more interesting defect than the one being hunted.
