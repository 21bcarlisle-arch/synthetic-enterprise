**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# Pre-registration: B11 slice 9, the per-customer hazard keyed to the term end and standardised for calendar year

Written 2026-10-11, before the term-end rule's level, Brier score or AUC had been computed on any
held-back month. Claim `b11-term-end-hazard-standardised-for-calendar-year`. It lands with the code
that measures it (`term_phase`, `term_phase_ratios` and `run_backtest(tenure_key="term_end")` in
`company/analytics/forward_clv.py`), and that commit precedes the measurement. Results go in a
separate finding. This file is not edited after the run.

**What was already known when this was written.** The flat and contract-year rules' level and AUC
at these cuts are on record from slices 6 and 7 (flat over-predicts; neither rule ranks better than
the other). The predictions below are about the NEW rule, which had not been graded.

## The rule

Slice 8 (`SEAT_FINDING_B11_TENURE_CARRIES_THE_FIXED_TERM_ANNIVERSARY_ONCE_THE_CALENDAR_YEAR_IS_HELD_2026-10-11.md`)
found the tenure signal is the fixed-term anniversary. The per-customer hazard's tenure key becomes
two phases: the TERM-END month (tenure 12, 24, 36… months, where a switch at term end lands) and IN
TERM (every other month, all of year 0). Each phase's ratio to its calendar year's rate is fitted on
the fit window by indirect standardisation, the book as its own reference, so the ratios move where
an exit is expected without changing how many. The per-customer hazard is the segment's flat hazard
times its phase's ratio. The level stays the flat rule's; only the ranking can change.

**Observable.** The run's renewal events (`customer_events`, 600) fall in the acquisition month's
anniversary: 585 at tenure ≡ 0 mod 12, 15 at ≡ 11 (a month-end date). Term end is read from the
account's own first supplied month, which a supplier holds.

## What was read before this file (fit side only — no held-back outcome)

On `/var/tmp/b11s5_run/run_output_b11s5.json` (773 accounts), the fitted phase ratios:

| cut | in term (95%) | term end (95%) |
|---|---|---|
| 2020 | 0.75 (0.66, 0.84) | 4.17 (3.44, 5.02) |
| 2022 | 0.75 (0.67, 0.84) | 4.09 (3.42, 4.85) |
| 2023 | 0.75 (0.67, 0.84) | 4.03 (3.38, 4.77) |

The spread of per-customer p across graded accounts (no outcome read): term-end rule sd 0.028,
0.024, 0.023 at the three cuts; flat sd 0.025, 0.016, 0.009; contract-year rule sd 0.036, 0.186,
0.102. Every account crosses nearly the same number of anniversaries over a horizon of 18 to 54
months, so the term-end key barely separates accounts. That is why P2 below predicts a null.

## The measurement

`run_backtest(..., move_out_month_by_account=register, tenure_key=k)` for k in `contract_year`,
`term_end`, at cuts 2020, 2022, 2023, whole fit window. For each: the level (mean p − realised
rate, with interval) and the ranking (AUC departers vs stayers, DeLong interval, paired against
flat). Plus the term-end rule paired directly against the contract-year rule (DeLong on the same
accounts) and the per-customer Brier score paired against flat.

## Predictions

- **P1 (level).** The term-end rule's level miss is within ±0.02 of the flat rule's at every cut,
  and has the flat rule's sign. It over-predicts with an interval wholly above zero at 2020 and 2022.
- **P2 (ranking against flat).** The paired AUC difference, term-end − flat: "cannot tell" at all
  three cuts.
- **P3 (ranking alone).** The term-end rule's AUC interval includes 0.5 at 2020 and 2022. At 2023
  (18 months held back, so an account crosses one or two anniversaries) the point estimate is above
  0.5; I predict its interval still includes 0.5.
- **P4 (Brier).** Per-customer Brier under the term-end key, paired against flat: "cannot tell" at
  all three cuts.

## Decision rule, written now

- The per-customer default becomes `term_end` only if, at no cut, it ranks worse than the
  contract-year key (paired AUC difference wholly below zero) AND its |level miss| is no larger than
  the contract-year key's at two of the three cuts. Otherwise the default stays `contract_year`
  and the key stays reachable as an argument.
- If P2 and P3 hold, the full-horizon AUC is the wrong instrument for a term-end key: what a
  supplier acts on is the NEXT term end. The next slice grades departure over the account's next
  term end only (a 12-month horizon from the cut), where the key can separate accounts.
