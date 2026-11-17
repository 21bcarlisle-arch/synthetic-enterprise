**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `DD_seasonal_cashflow_physics`

# D5 switch-on: rows 4 and 7 pre-registered before any book carries it (2026-11-17)

*BLOCKING: rows 4 and 7 are two of the rows refusing the publish (25 consecutive failures, no book newer than 9 Nov).
This file is written before the switch-on commit and before any run on it. Knowledge page: `docs/market_research/home_moves.md` s.8.8f.*

## What is graded already (the baseline, measured 17 Nov 00:30Z)

The f7e17b1316 book is the shared tree's `docs/state/billing_ledger.json`, whose `meta.source_json` is
`run_output_f7e17b1316_20261116T070501Z.json`. It was graded with this landing's runner and nothing else changed
(`_left_level_owed`, choice 27):

| row | f7e17b1316 as refused | runner choice 27 only |
|---|---|---|
| `INV_OVERDUE_WITHIN_BALANCE` (4) | 4 | **0** (SYN-2016-024, -075, PROS-2021-0315, SYN-2016-471) |
| `INV_OVERDUE_WITHIN_PAGE_BALANCE` (7) | 7 | 7: SYN-2016-001 15 Aug 2023 (2 steps, 386.23 against 329.71); SYN-2016-471 (5 steps, 38.13 against 28.77) |

**Row 4's 0 does not count as a pass.** On f7e17b1316 the switch was off, so no final bill asked the debit. The runner
now dates a level leaver's debit from its final bill's due date whether or not that bill asked it. That is the shape
the 16 Nov constraint warned about (the 17:20 entry in the 2026-11-07 level-DD finding). This landing accepts it
because the switch-on lands in the same push, and `next_book_requires.yaml` admits no book built without the
switch-on commit. A re-grade of an older book with this runner reads row 4 too kindly. Rows 7 and the gas row still
refuse f7e17b1316, so that book does not publish.

## Predictions for the first book carrying the switch-on commit

The book carries every commit between f7e17b1316 and the switch-on, so it is **not** a one-variable run. A row value
that matches these predictions is consistent with D5 and does not attribute the change to D5.

1. **Row 4 reads at most 1.** A final collection that fails now opens on the debit from the final bill's due date,
   and the runner reads that debit as owed (s.8.8f prediction). The four f7e17b1316 openings are not among them.
2. **Row 7 reads 2: SYN-2016-001's two steps only.** That case is not D5 and nothing in this landing touches it.
3. **SYN-2016-471 leaves row 7 even though its desk misdating is NOT fixed.** On f7e17b1316 the desk opened on
   30 Mar 2021 over 9.36, three days after final bill 45884 (14.10, due 27 Mar). It then asked 38.13 (bill 45883's
   face, 9.36 of it already met) against the page's 28.77. With the switch on, that final bill asks 14.10 plus the
   ledger debit, and the household's outcome draw, keyed by period, is unchanged (success on 29 Mar). So nothing stays
   owed, and no journey opens to misdate. **If 471 still appears, the prediction is refuted**, and the desk
   misdating (company `left_level_asks` reading 45883 as an on-receipt bill) is the next trace.
4. **Level-leaver write-offs at move-out fall.** How far: I cannot yet say. The size goes beside the 6fe7827ab2
   figure (choice 28).

## What is not done

- **SYN-2016-471's desk misdating is not traced to a line.** The arithmetic fits `left_level_asks` putting the leave on
  1 Mar, which makes 45883 off the schedule and dates its face from 15 Mar. Without a desk replay that is a
  hypothesis. Prediction 3 says the switch-on stops this path being reached. Whether it fires anywhere else is
  unmeasured.
- **SYN-2016-001** (row 7, 2 steps) has no owner in `next_book_requires.yaml`.

## SYN-2016-001 traced to a class (worker, 17 Nov)

- **What the desk read.** The household's 2022-25 journey (ACC-SYN-2016-001, `collections_journeys[966]`
  on f7e17b1316) has 42 desk steps. 40 print an overdue figure equal to the page's two-fuel balance
  that day, to the penny. The two that do not are both the 15 Aug 2023 steps, each 56.52 over. 56.52
  is the gas lump the world settled on 15 Aug (bill 21608, `world_payment_truth.repayments`). Every
  step after it agrees with the page again, so the cash did reach the company's ledger. It got
  there after the desk had decided 15 Aug.
- **So this is the walk's ordering, not D5 and not the grader.** A lump that crosses on or before a
  day the journey has already been walked through leaves that day's step reading the balance
  without it. Which walk passed 15 Aug first is **not established** from the code. `_settle_held`
  sorts lumps by date and the bound read here looks sound, so I cannot yet say.
- **The diagnostic is now in the run.** Every lump that crosses behind its walk is counted, with
  the walk that went past its day: `settlements_behind_the_walk` in the run summary
  (`LivePaymentTriad._walk`). The next book names the path.
- **A fully clearing crossing behind the walk fails differently.** The desk's R10 check raises
  (`DunningOfAClearedDebtError`), so the run stops. Only partial ones, like this one, get through
  silently.
- **Prediction 2 stands.** Row 7 reads 2 on the next book unless that book's draws move this lump.
  If it does, the book is refused again. That refusal is this class, and the counter will name its
  walk.
- **Also fixed here: the shared tree's `background/live_payment_triad.py` held the pre-switch-on
  bytes** (`FINAL_BILL_ASKS_THE_LEVEL_DEBIT = False`, mtime 16 Nov 20:22, identical to
  341df4965^). The same was true of its test. 341df4965 landed without writing either file.
  `sim_runner.code_admission` would have deferred every book on it once memory freed. Both now
  hold HEAD's bytes.

## A second path behind the walk, found and fixed. It is not SYN-2016-001's (worker, 17 Nov 17:30Z)

- **What was found.** `record_period` delivers pending lumps through the bill's due date, then
  pushes this bill's own lumps, then walks the account to the previous due date. A level
  collection is presented inside its month, on the payment day, and a returned one is re-presented
  14 days later (`REPRESENTATION_DAYS_AFTER_DUE`). That re-presentation, or an early-contact check
  dated `presented_on + EARLY_WINDOW_DAYS`, can fall on or before the previous due date. It sits
  in the heap, undelivered, while the walk passes its day.
- **Measured.** A synthetic level leg (collected on the 2nd, bills due on the 20th, 12 months, ids
  `LVL-0..399`) puts 102 of 400 accounts behind the walk, all `walked_by: record_period`. After the
  fix the same count is 0. The fix: the walk block delivers through `previous_due`
  (`_deliver_settlements_through`) instead of only settling what is already held.
- **Control.** `test_a_re_presented_level_collection_crosses_before_the_walk_passes_its_day` fails
  with the fix reverted. It asserts the lump crossed before asserting that it is not behind.
- **SYN-2016-001 is NOT this class.** On f7e17b1316 its gas leg pays `standard_credit`. Its payment
  day would be the 12th, so a level re-presentation would land on 28 Aug, not 15 Aug. 15 Aug 2023
  is also the due date of gas bill 21611. **Prediction 2 stands unchanged.** The D5-on book reads
  2 on row 7 and names a walk for SYN-2016-001 in `settlements_behind_the_walk`. That book was
  built before this fix, so any of its `record_period` rows on level legs may be this class and not
  SYN-2016-001's. Tell them apart by `leg` and `settled_on`.
- **What this does to row 7 on later books.** I cannot yet say. The f7e17b1316 grade printed no
  level-leg case of this shape on row 7, so this fix may change no published row. What it changes
  is that a returned level collection's cure is on the ledger the day the desk decides.

## Graded on the D5-on book (18f201c5bf, 17 Nov 20:18Z)

Prediction 1 **held** (row 4 reads 0). Prediction 2 **refuted** (row 7 reads 20, not 2). SYN-2016-001's two steps are
unchanged, but SYN-2016-471 (5), SYN-2016-523 (5, new) and SYN-2016-546 (8, new) are also on the row. Prediction 3
**refuted**: 471 still appears, and its journey opens on 24 Apr 2021. By this file's own words, the desk misdating in
`left_level_asks` is the next trace. Prediction 4 was not read. `settlements_behind_the_walk` never reaches the run
output, so "the next book names the path" cannot happen as written. Detail and owners: §9 of
`SEAT_FINDING_THE_VAT_ROWS_LAST_BREACH_IS_AN_OPEN_ESTIMATED_RUN_AND_THE_16_NOV_BOOK_IS_REFUSED_AS_PREDICTED_2026-11-16.md`.
