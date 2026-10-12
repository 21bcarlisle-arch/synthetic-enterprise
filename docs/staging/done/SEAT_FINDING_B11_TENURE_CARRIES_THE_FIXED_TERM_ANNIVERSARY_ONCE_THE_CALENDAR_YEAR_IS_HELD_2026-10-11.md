**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# B11 slice 8 result: once the calendar year is held, tenure still carries something, and it is the fixed-term anniversary

**Fate (2026-10-12, clear-the-decks):** DONE -- 4a42f2e89. B11 slice 8 result graded: tenure carries fixed-term anniversary once calendar year held

Claim `b11-tenure-vs-calendar-on-a-second-founding-year`. The predictions were written before the
measurement and gated with the code that makes it. That was `47ee5bd4e`, committed before any exit
was counted. Origin moved before promotion, so the same bytes landed on the trunk as `dbad0fe64`:
`docs/staging/records/SEAT_PREREG_B11_EIGHTH_SLICE_TENURE_GIVEN_CALENDAR_YEAR_ON_THE_LATER_COHORTS_2026-10-11.md`.
This file grades them and leaves them as written.

## The premise

The item asked for a run whose book opens after 2016. **There is none.** All 4,950 distinct run
outputs on this machine open in 2016. A second founding year would need a new run, and choosing the
year the company is founded is the director's call.

**It was not needed for the young contract years.** The slice-5 book
(`/var/tmp/b11s5_run/run_output_b11s5.json`, 773 accounts) has 341 accounts in nine later cohorts,
2017 to 2025. Slice 7's collinearity holds for the 2016 cohort and for the oldest contract years.
It does not hold for contract years 0 to 4.

## The measurement

The later cohorts are the 341 accounts first supplied in 2017 or later. The book runs to 2025-06.
Each figure is observed exits over expected exits, with a 95% Poisson interval.

**M1. Tenure given calendar year.** Expected exits use the later cohorts' own rate for each
calendar year.

| contract year | months at risk | observed | expected | ratio (95%) | switch-only ratio (95%) |
|---|---|---|---|---|---|
| 0 | 3,640 | 34 | 58.3 | **0.58 (0.40, 0.81)** | **0.41 (0.24, 0.67)** |
| 1 | 2,519 | 54 | 37.9 | **1.43 (1.07, 1.86)** | **1.66 (1.19, 2.24)** |
| 2 | 1,868 | 26 | 24.0 | 1.08 (0.71, 1.58) | 1.25 (0.75, 1.95) |
| 3 | 1,378 | 19 | 14.0 | 1.36 (0.82, 2.12) | 1.59 (0.82, 2.78) |
| 4 | 912 | 12 | 8.1 | 1.48 (0.76, 2.58) | not graded (E 3.9) |

**M2. Calendar year given tenure.** Ratios wholly above 1: 2019, at 2.08 (1.42, 2.96). Ratios wholly
below 1: 2022, at 0.52 (0.27, 0.90), and 2023, at 0.40 (0.19, 0.73).

**M3. The 2016 cohort against the later cohorts' calendar-year rates.** Pooled over 2017 to 2025,
324 observed against 322.2 expected: **1.01 (0.90, 1.12)**.

## The predictions, graded

- **P1, that tenure carries nothing once the year is held: REFUTED.** Contract year 0 leaves at
  0.58× its calendar years' rate, and contract year 1 at 1.43×. Both intervals exclude 1.
- **P2, that the calendar year carries a lot: HELD.** 2019 is above 1, and 2022 and 2023 are below.
- **P3, that the 2016 cohort leaves less (between 0.5 and 0.95, excluding 1): REFUTED** at
  1.01 (0.90, 1.12). Read this with the diagnostic below: P1's refutation spoils the reference
  this comparison used.
- **P4, that switch-only reads as all-cause: HELD.** It has the same shape and is sharper:
  contract year 0 at 0.41, contract year 1 at 1.66.

## What the tenure signal is. Not pre-registered: diagnostics after the fact.

**Exits by month of tenure** (the last supplied month minus the first), later cohorts, as
all-cause / switch-only. Months 0 to 11 have 1 to 6 exits each. **Month 12 has 24 / 21. Month 13
has 8 / 5. Month 24 has 10 / 9.** Months 14 to 23 have 0 to 5 each.

So the "tenure effect" is **the fixed-term anniversary**: a switch away at term end, which lands in
the first month of the next contract year. Year 0 is low because it holds no term end. Year 1 is
high because it opens with one. The twelve-month bucket then smears that spike across the whole
year.

This is the industry's own shape, and slice 7 could not see it. On published evidence, switching
concentrates at fixed-term end. The world's per-ender rate at term end sits inside the published
bound for 2017 to 2021:
`SEAT_FINDING_THE_WORLD_LOSES_FORTY_PERCENT_AT_EACH_ANNIVERSARY_AGAINST_A_PUBLISHED_SIX_2026-10-08.md`
gives 14.2% within 42 days. Its 2024–25 leg is still open on the worker finding it names.

**M3 again, against later-cohort rates from contract year 1 onward only**, so that the reference
excludes year 0, which has no term end. The 2016 cohort's ratio is **0.74 (0.64, 0.84)**. So the
founders do leave less than the later cohorts did past their first year, in the same calendar years.
On this book that difference could be long tenure, the founder cohort, or the anniversary month
mix. A cut-free census cannot separate them, and **this is the only residue a second founding year
would be needed for**.

## Slice 7 corrected beside its claim

Slice 7 said the per-customer level is "a one-year recency estimator for the founder cohort … not a
tenure effect". For the founders' **oldest** contract year, that stands: it is fitted on the cut year
alone. **"Not a tenure effect" does not stand for the book as a whole.** On the young years, tenure
carries the anniversary, independently of the calendar year. The contract-year table is the wrong
shape to hold it.

## The decision, by the rule written before the run

P1 was refuted, so the next slice is owed:

1. **Replace the contract-year table's tenure key with the term-end month.** That means an
   in-term hazard and an at-anniversary hazard. Fit them standardised for calendar year, so that
   the regime stops leaking into them. A supplier knows each account's term end. It is on its own
   contract record, so this is on the right side of the epistemic wall.
2. **Grade the result as slice 6 did**, with the level and the ranking kept separate, at cuts 2020,
   2022 and 2023. The prediction is that a known term end improves the RANKING. Neither rule has
   ranked so far: AUC was "cannot tell" at every cut. The level stays the regime's.

The second founding year is proposed only if the founders' 0.74 residue turns out to matter after
step 1. It does not block anything now.
