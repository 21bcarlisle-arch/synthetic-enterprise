**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# B11 slice 7 result: the move term of departure transfers across the crisis and the switch term does not

Claim `b11-later-cut-and-regime-caveated-departure`. The predictions were written before the
measurement and landed with the code that makes it, in `375ec5772`:
`docs/staging/records/SEAT_PREREG_B11_SEVENTH_SLICE_LATER_CUTS_AND_THE_DEPARTURE_LEVEL_BY_CAUSE_2026-10-11.md`.
This file grades them and leaves them as written.

## The run

This is the same book as slices 5 and 6: `/var/tmp/b11s5_run/run_output_b11s5.json`, run at
`3f1ebfac3` with home moves on. Each figure below is `backtest_run_output(path, cut)` at
`375ec5772`. The default hazard window is used throughout.

| cut | held back | graded | realised | per-customer p | flat p | per-customer calibration | flat calibration |
|---|---|---|---|---|---|---|---|
| 2020 | 2021-01..2025-06 | 247 | 0.429 | 0.790 | 0.671 | +0.361 (+0.299, +0.423) | +0.241 (+0.180, +0.303) |
| 2022 | 2023-01..2025-06 | 253 | 0.249 | 0.272 | 0.418 | **+0.023 (−0.035, +0.081)** | +0.169 (+0.116, +0.223) |
| 2023 | 2024-01..2025-06 | 260 | 0.200 | 0.187 | 0.257 | −0.013 (−0.062, +0.037) | +0.057 (+0.008, +0.106) |

The flat rule's level, split into competing switch and move incidences that sum to it:

| cut | switch predicted / realised | switch calibration | move predicted / realised | move calibration |
|---|---|---|---|---|
| 2020 | 0.490 / 0.247 | **+0.243 (+0.190, +0.297)** | 0.180 / 0.182 | **−0.002 (−0.050, +0.046)** |
| 2022 | 0.293 / 0.150 | +0.143 (+0.098, +0.187) | 0.126 / 0.099 | +0.027 (−0.010, +0.064) |
| 2023 | 0.179 / 0.131 | +0.049 (+0.008, +0.090) | 0.078 / 0.069 | +0.008 (−0.023, +0.039) |

## The predictions, graded

- **P1 (cut 2022, flat, between +0.12 and +0.24, excludes zero): HELD.** It came in at +0.169.
  Slice 6's point 3 put flat p at about 0.42 against about 0.24 realised. The measurement is 0.418
  against 0.249.
- **P2 (cut 2023, flat, between +0.03 and +0.13, excludes zero narrowly): HELD.** It came in at
  +0.057, with a lower bound of +0.008.
- **P3 (per-customer above flat at both cuts): REFUTED, and the cause is not the one it seems.**
  At cut 2022 the per-customer rule is calibrated, at +0.023 with an interval that holds zero, and
  flat is not. See the next section before reading this as the tenure table working.
- **P4 (neither rule ranks): HELD.** The paired AUC difference is +0.003 (−0.068, +0.075) at 2022
  and +0.084 (−0.007, +0.175) at 2023, so both are "cannot tell". 2023's lower bound is near zero
  and its point estimate favours per-customer, but it does not clear.
- **P5 (at cut 2020 the switch term carries the whole miss): HELD.** The switch term is +0.243 and
  the move term is −0.002. All of the flat rule's +0.241 miss is in the switch term.
- **P6 (at cut 2022 the switch miss is at least 2× the move miss): HELD.** The switch miss is
  +0.143 and the move miss is +0.027, about 5×. The move interval holds zero.

Neither refutation condition in the pre-registration fired. The move term did not miss with the
switch term. The flat level at 2023 is not inside its interval, though it is close.

## Why per-customer is calibrated at the later cuts. Not pre-registered: a diagnostic after the fact.

At every cut, the per-customer hazard's oldest contract year is fitted on **the cut year alone**.
That year holds for every later month of tenure, and 40% of graded accounts sit in it.

| cut | oldest contract year | its rate | fitted on | graded accounts in it |
|---|---|---|---|---|
| 2020 | 4 | 0.0293 | 2020 only (921 months) | 132 of 247 |
| 2022 | 6 | **0.0029** | 2022 only (680 months) | 106 of 253 |
| 2023 | 7 | 0.0047 | 2023 only (638 months) | 96 of 260 |

So for the founders, the per-customer level IS the latest year's rate. At cut 2020 that year was
the book's second-highest year, and the rule over-predicted most. At cut 2022 it was the collapse
year, and the rule landed on the answer. **This is a one-year recency estimator for the founder
cohort, produced by the book's age. It is not a tenure effect.** It is slice 6's H3, a calendar
confound in the tenure table, in a sharper form than slice 6 could state from one cut. Slice 6
called H3 "not supported as stated". That verdict is corrected beside the claim. A recency
estimator on one year will be right whenever next year looks like this year, and wrong at every
turn of the regime. That is exactly what it did at 2020.

## The decision, by the rule written before the run

P5 held, so **the departure level is published as two terms, and no calibrated constant replaces
either**:

- **The move term is the part that transferred.** Its calibration interval holds zero at all
  three cuts, across the crisis.
- **The switch term carries the regime caveat.** It over-predicts at all three cuts, by +0.24,
  +0.14 and +0.05. The miss shrinks only as the collapse years enter the fit window. Fitting its
  level to a held-back rate would be fitting to the answer.

On the result surface (`company/analytics/forward_clv.py`, `375ec5772` and this commit):

- `LIMITATION_SWITCH_LEVEL_IS_THE_REGIME` is on every result that carries a register.
- When the oldest contract year was fitted on one calendar year, the result names it. It does so
  on this book at every cut, so a reader of the per-customer level is told it is recency, not
  tenure.
- `departure_incidence_by_cause` and `departure_calibration_by_cause` carry the split.

The forecast itself is unchanged. All-cause survival still drives the margin sum, because margin
stops however the account leaves.

## What is still open

- **Whether a cause-separated survival should drive the forecast.** For example, a switch term
  scenario-banded by regime with a move term taken as fitted. That is a design choice for whoever
  consumes forward value: `company/crm/next_best_action.py` borrows only the paired comparison
  today. Nothing consumes the level yet, so nothing is owed now.
- **Tenure against calendar time cannot be separated on one book.** That needs a book whose cohorts
  open in different years, or a second run with a different founding year. EP17 still blocks the
  L3 claim.
