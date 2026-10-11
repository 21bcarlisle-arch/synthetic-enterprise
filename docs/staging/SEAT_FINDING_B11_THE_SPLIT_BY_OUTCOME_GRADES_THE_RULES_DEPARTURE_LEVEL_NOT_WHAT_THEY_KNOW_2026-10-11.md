**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# B11 slice 5 result: graded by outcome, each rule's departure LEVEL decides the result, not what it knows about customers

Claim `the-forward-value-backtest-splits-switches-from-moves`. The predictions were written before
the run (`docs/staging/records/SEAT_PREREG_B11_FIFTH_SLICE_FORWARD_VALUE_ERROR_SPLIT_BY_STAYERS_SWITCHERS_AND_MOVERS_2026-10-11.md`,
landed in `60c3a92f2`). This file grades them and does not edit them.

## The run

A full book from `tools.run_annual_report` at `3f1ebfac3`, launched through `launch_long_job` as
`longjob-b11s5-full-run` (Result=success, 02:15 BST). `c4fb2931b` is an ancestor and home moves
are on. Read with `backtest_run_output(path, 2020, None, LiveSimInterface().monthly_wholesale_prices("gas"))`.
The output was kept in `/var/tmp/b11s5_run/run_output_b11s5.json` (91 MB) and was not committed.

The cut is 2020. The fit window is 2016-01 to 2020-12 and the held-back window is 2021-01 to
2025-06. The deviation window is the fit window, because there is no wholesale all-time high
between 2019-01 and the cut. 247 accounts are graded. 161 are excluded because they joined after
the cut, and 365 because they left before it.

| outcome | n | margin abs error, pc − flat (95%) | Brier, pc − flat (95%) | signed margin miss pc / flat (GBP) |
|---|---|---|---|---|
| whole book | 247 | +23.5 (+9.1, +38.0) flat better | +0.073 (+0.058, +0.089) flat better | −498 / −446 |
| stayer | 141 | +39.5 (+21.5, +57.5) flat better | +0.176 (+0.171, +0.181) flat better | −849 / −809 |
| switcher | 61 | −2.3 (−30.2, +25.6) cannot tell | −0.062 (−0.064, −0.059) pc better | −72 / +23 |
| mover | 45 | +8.3 (−31.2, +47.8) cannot tell | −0.064 (−0.067, −0.061) pc better | +26 / +54 |

Departures by cause: 264 switches and 101 moves in the fit window; 77 switches and 61 moves held back.

## The predictions, graded

- **P1, moves reach the backtest: HELD.** The run carries a register and the held-back window has 61 moves.
- **P2, movers are 10–50% of held-back departures: HELD.** 61 of 138 is 44%.
- **P3, stayers Brier, per-customer better: REFUTED, in the opposite direction.** Flat is better
  by 0.176.
- **P4, switchers Brier, flat better or cannot tell: REFUTED.** Per-customer is better.
- **P5, movers Brier, cannot tell with a positive point estimate: REFUTED.** Per-customer is better.
- **P6, margin error cannot tell in all three outcomes: PARTLY REFUTED.** Flat is better on
  stayers, and that also makes flat better on the whole book. The other two outcomes cannot tell.
- **P7, the movers' signed miss is above the stayers' under both rules: HELD.** +26 and +54
  against −849 and −809.

**The mechanism behind P3–P5 was wrong in sign.** I said the contract-year hazard gives a
long-tenured account a *lower* departure probability than its segment average. It gives everyone a
*higher* one. Measured over the 247 graded accounts:

| rule | mean p | sd | range | p, departed vs stayed | AUC |
|---|---|---|---|---|---|
| per-customer | 0.790 | 0.036 | 0.696–0.866 | 0.791 vs 0.789 | 0.515 |
| flat | 0.671 | 0.025 | 0.651–0.713 | 0.672 vs 0.669 | 0.524 |

The realised held-back departure rate is **0.429**.

## What this means

1. **The per-outcome Brier is a test of each rule's departure level, not of what it knows about
   customers.** Within one outcome the realised value is a constant: 0 for stayers and 1 for
   departers. A rule that predicts a higher p everywhere therefore wins on every departure outcome
   and loses on stayers, whatever it knows. Both rules are almost constant (sd 0.03) and neither
   ranks departers above stayers (AUC about 0.52), so the whole table above is the 0.79 vs 0.67
   level difference read three ways. Asking the outcome split for Brier was a measurement design
   error in slice 5. What it can answer is the **ranking within outcome against stayers**:
   - switcher vs stayer: AUC 0.583 per-customer, 0.588 flat;
   - mover vs stayer: AUC 0.432 per-customer, 0.447 flat.

   *Corrected 2026-10-11 (slice 6): these four were hand-computed and wrong in the third place.
   `forward_clv`'s ranking and sklearn agree on switcher 0.575 / 0.583 and mover 0.433 / 0.444.
   The reading below does not change.*

   With n = 61 or 45 against 141, each AUC carries a standard error of about ±0.045, so this is
   weak evidence. Both rules rank movers slightly *below* stayers, which fits the view that a move
   does not follow supply tenure. Neither rule tells movers from switchers better than the other.
2. **Both rules over-predict departure badly: 0.67 and 0.79 against 0.43 realised.** That is a
   calibration miss of 0.24 to 0.36 over 4.5 years. It explains P7's large negative miss on
   stayers: both rules weight the margin by survival and expect most stayers to leave. It is also
   the largest error in the backtest. One explanation is that the hazards are fitted on 2016–2020,
   when 365 of the accounts present left. That window holds the founder cohort's early churn, and
   the hazard projects it forward. I have not tested this; it is the next slice.
3. **The thesis test still reads "flat better or cannot tell" on this book.** The per-customer rule
   adds a higher level and no ranking.

## Disposition

- **B7 comes off B11's `blocked_on`** under P1's stated consequence: moves now reach the backtest.
- **EP17 stays.** Separating the two rules needs accounts that differ. On one book, with a
  departure-p sd of 0.03, neither rule has anything to rank. A varied population draw is what
  could give the per-customer rule something to know, and that is the director's curriculum
  call (R13). EP17 blocks the L3 claim. It does not block the next slice.
- **Next slice, company code, needs no director:** calibrate the departure level. Grade the
  calibration-in-the-large of each rule's held-back p, find out whether the fit window's founder
  churn causes the 0.24–0.36 over-prediction, and replace the per-outcome Brier with the
  within-outcome ranking (AUC against stayers, with its interval) as the slice-5 statistic.
  Handed on as a continuation.
