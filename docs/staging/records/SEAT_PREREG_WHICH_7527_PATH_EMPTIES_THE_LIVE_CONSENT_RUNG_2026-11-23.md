# Pre-registration: which 7527a2e36c path empties the live Consent rung? (23 Nov 2026, 08:20Z)

```
PRE-REGISTRATION 2026-11-23 (delivery seat, verify-gas-only-win-landing-from-the-6c-resume-chain)
Subject: SEAT_FINDING_ORIGIN_IS_RED_ON_THE_LIVE_CONSENT_OFFER_SINCE_7527A2E36_..._2026-11-23.md, done-means 1.
Measurement: two 2016 runs (plan_take_up_share at "high", report_end 2016-12-31) on origin 6903ea3d86,
  A as is, B with LivePaymentTriad.record_period forced to closing=False (7527's only runtime change).
  Each records every 90-day prepayment rung stage, ACC-SYN-2016-005's journeys, its final_month_nets
  rows, and whether any of its legs is in the end-of-run `_legs_that_left`.
Predictions, written before either run:
  P1 (80%): B restores an offered rung for ACC-SYN-2016-005 (A has none). If not, 7527 is not the
      whole mechanism and the bisect pin is wrong or something later also moves it.
  P2 (50%): a leg of ACC-SYN-2016-005 IS in `_legs_that_left` at end of run (closed by something other
      than its churn roll), so its own end-of-run final bill now asks face plus the level debit.
  P3 (35%): no 005 leg is closing; its rung moves only through state shared with other leavers' final
      bills (a draw or a desk-wide advance), i.e. 7527's "no seed moves" is wrong.
What changes on each answer: P2 true -> the control stood on a household the world now closes, the
  control is re-keyed to the property (done-means 2, second branch). P3 true -> 7527's defect, fixed at
  its source (done-means 2, first branch).
```
