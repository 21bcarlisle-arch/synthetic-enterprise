**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# Pre-registration: B11 slice 6, why both rules over-predict held-back departure

Written 2026-10-11, before any calendar-year rate, recency-window fit, calibration interval or AUC
interval had been computed on the run below. Claim `b11-departure-level-calibration`. It lands in
the same commit as the code that measures it, and that commit precedes the measurement. Results go
in a separate finding. This file is not edited after the run.

## What is already known, and is therefore NOT a prediction

From slice 5 (`docs/staging/SEAT_FINDING_B11_THE_SPLIT_BY_OUTCOME_GRADES_THE_RULES_DEPARTURE_LEVEL_NOT_WHAT_THEY_KNOW_2026-10-11.md`),
on `/var/tmp/b11s5_run/run_output_b11s5.json` (run at `3f1ebfac3`, home moves on), cut 2020,
247 graded accounts: mean held-back departure p 0.790 per-customer and 0.671 flat, against 0.429
realised. AUC departed-vs-stayed 0.515 and 0.524; switcher-vs-stayer 0.583 and 0.588;
mover-vs-stayer 0.432 and 0.447. Departures 264 switches + 101 moves in the fit window, 77 + 61
held back.

The new code must reproduce these. **C1:** calibration-in-the-large (mean p − realised rate) is
+0.361 per-customer and +0.242 flat, each with an interval that excludes zero, and the AUCs match
the figures above to three places. A mismatch is a defect in the new code, not a finding.

## The question

Both rules over-predict departure by 0.24–0.36 over 4.5 years. Slice 5 offered one explanation:
**H1, founder churn** — the hazard is fitted on 2016–2020, when 365 accounts left, and that early
churn is projected forward. Two others the evidence allows:

- **H2, the held-back world moved.** Departure in 2021–2025 fell for a reason no fit on 2016–2020
  could see. In GB, fixed offers were withdrawn from autumn 2021 and switching collapsed until
  2023. If the world carries that, no calibration of the fit window fixes the level.
- **H3, a calendar confound in the tenure table.** Per-customer predicts MORE departure than flat.
  The per-customer hazard for a graded account is mostly the oldest contract year's rate, and in a
  book that opened in 2016 the oldest contract years ARE the last calendar years. So the tenure
  table may be reading calendar time, not tenure.

## What is measured

The book's monthly departure rate by calendar year (departures ÷ months at risk, every account on
supply, departures split by cause from the register); the calibration-in-the-large of each rule
with its 95% interval; the hazard refitted on 2020 alone (left-truncated, tenure still counted
from each account's first month); and the AUC of each rule's p, departers against held-back
stayers, per outcome, with a DeLong 95% interval and the paired per-customer − flat difference.

## Predictions

- **P1 (H1).** REFUTED: the book's 2016–2017 monthly departure rate is NOT above 1.25 × its
  2019–2020 rate. Basis: per-customer > flat says the oldest contract year's hazard is above the
  book average, and the oldest contract years are the latest calendar years.
- **P2 (recency does not fix it).** With the hazard fitted on 2020 alone, the flat rule's
  calibration-in-the-large stays at +0.19 or above, interval excluding zero.
- **P3 (H2).** The book's monthly departure rate in 2021–2022 is below 0.6 × its 2020 rate.
  Confidence low: it depends on whether the world carries the 2021–23 switching collapse.
- **P4 (cause).** The fall is in switches. The held-back switch rate per account-month is below
  0.6 × the fit window's; the held-back move rate is between 0.7 and 1.4 × the fit window's.
- **P5 (ranking).** The paired AUC difference, per-customer − flat, cannot tell on the whole book,
  on switchers and on movers.

## What would change what we do

- P1 refuted and P3 held: the level miss is the world's regime in the held-back years. A
  calibration constant fitted to it would be fitted to the answer; the next slice is a later cut
  (2022 or 2023), where the fit sees the regime, not a recency knob.
- P1 held, or P2 refuted: the fit window's composition is the cause, and a recency-weighted hazard
  is a candidate rule — graded at a second cut before it is adopted.
- H3 supported (2019–2020 rates highest in the fit window): the per-customer tenure table is
  confounded with calendar time, and its "knowledge" is a calendar effect. Separating tenure from
  period is then owed before EP17's varied population can test what the rule knows.
