**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` (parked; row untouched) · **Claim:** `b11-slice-13-why-the-flat-switch-level-over-predicts-held-back-departure` (Lane 0 delivery)

# Pre-registration: B11 slice 13, why the flat level over-predicts held-back departure, and one window

Written 2026-10-17 at origin `51ec26010`, before any figure below has been read from this book. Not
edited after the run. Results go in a separate finding, each graded beside its prediction here.

**Known and therefore NOT predicted.** Slice 12 found the flat rule's calibration, mean p minus the
realised rate, is +0.241 / +0.181 / +0.072 at cuts 2020 / 2022 / 2023 on this book, with realised
rates 0.423 / 0.234 / 0.184. Slices 6 and 7 measured the same split on a DIFFERENT book (slice 5's,
`3f1ebfac3`). There the switch term carried the whole miss at 2020 (+0.243, with move at −0.002),
and switching fell to 0.0013 per account-month in 2022. Those figures are my prior, not this
book's answer.

## A correction to the item's premise, made before measuring

Slice 12's finding says the switch level is high because "the fit window holds the 2021–22 crisis
exits". That cannot be right at cut 2020, whose fit window ends in December 2020 and holds no
2021–22 month. On slice 6's book the 2021–22 years were LOW-exit years, because switching collapsed
when fixed offers were withdrawn. So the pre-registered reading is the opposite of the premise. The
over-prediction comes from the pre-crisis years 2017–2020, which switched at a rate the held-back
years never returned to. Including 2021–22 in the window LOWERS the flat level. The by-year
decomposition below tests this directly.

## What is measured, defined before it is differenced

- **The flat level.** This is each segment's monthly departure hazard over the hazard window: exits
  over months at risk. The rule's p is 1 − (1 − h)^H over the horizon, and all three readings use
  the rule exactly as shipped (`run_backtest`).
- **The miss by cause.** This is `departure_calibration_by_cause`: the competing-risk incidence of
  switches and of moves, minus the share of graded accounts that left by each. The two sum to the
  all-cause miss.
- **The miss by fit-window calendar year.** This is a HAZARD identity, not a p identity. Pool the
  whole book, every account on supply, using `departures_by_calendar_year`. The fit window's pooled
  monthly rate h_fit = Σ_y w_y h_y, where w_y is year y's share of the window's months at risk.
  Then h_fit − h_hb = Σ_y w_y (h_y − h_hb), where h_hb is the pooled rate over the held-back
  months. Each year's term is its contribution to the excess hazard, and the same identity is
  computed for the switch rate. It is pooled over segments, so it describes the level, not one
  segment's rule. Departures are counted in the calendar year of their last supplied month.

## Predictions

- **D1 (cause, every cut).** The switch term's calibration is at least 80% of the all-cause flat
  miss at every cut. The move term's interval holds zero at every cut.
- **D2 (2020's miss is the pre-crisis switching).** At cut 2020, each of 2017, 2018, 2019 and 2020
  has a switch rate above the held-back 2021–2025 switch rate, and 2016 does not, because the
  founders' first year was a low-exit year. 2016's term is negative or within ±10% of the total.
- **D3 (2021–22 pull the level DOWN).** At cuts 2022 and 2023, the 2021 and 2022 terms in the
  switch identity sum to a NEGATIVE value: those years switched below the held-back rate. 2022 is
  the book's lowest switch-rate year.
- **D4 (the over-prediction is carried by 2017–2020 at every cut).** At cuts 2022 and 2023, the
  2017–2020 terms sum to more than the whole switch excess, and the crisis-year terms offset part
  of it.

## The one variable

The variable is `hazard_fit_from_year=2023` against the full window, at **cut 2023**. That is the
only cut at which a window "starting after the 2021–22 crisis" exists. At 2020 and 2022 it would
begin after the cut, which `run_backtest` refuses. Everything else is held fixed: the book, the
accounts graded, the margin fit, the horizon (2024-01..2025-06), and the flat rule.

- **W1 (sign).** With the window at 2023 alone, the flat calibration is NEGATIVE, with its point in
  [−0.10, −0.01]. The 2023 rate was a trough year, and switching was recovering in 2024–25 (on
  slice 6's book 2023 was 0.0062 against about 0.011 in 2024–25).
- **W2 (no cure).** |calibration| with the window from 2023 is at least 0.04. The window trades an
  over-prediction for an under-prediction. It does not close the level.
- **W3 (per-customer, reading only).** I do NOT predict the per-customer level under the window.

Readings, each labelled as NOT the one variable: windows from 2021 at cuts 2022 and 2023, and from
2022 at cut 2023. Each moves the level and I do not grade them against a prediction.

**Refutation.** If D3 fails, so that 2021–22 sit ABOVE the held-back switch rate, then slice 12's
premise was right for the later cuts and the correction above is wrong there. If W1 fails with a
positive calibration, then 2023 alone still switched above 2024–25, and the regime had not turned
by the cut.

**Decision rule, written before the run.** The default window does not change on this result,
whatever it shows. One book is DEVELOPMENT. A window chosen because it matched the held-back rate
is fitting to the answer (slice 6). What can land is the decomposition's verdict as a sharper
`LIMITATION_SWITCH_LEVEL_IS_THE_REGIME` wording: which years carry the excess.

**F11.** If the evidence is ambiguous, read it against the regime story, not for it.
