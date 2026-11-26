**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# A credit bill on one leg paid the other leg's scheme debit, so the desk dunned that debit three weeks early

Delivery seat, 26 Nov 2026, draw `the-cb93f7760c-book-publishes-or-its-refusal-is-closed-cause-by-cause`.
Found on the cb93f7760c book (`run_output_cb93f7760c_20261126T013243Z.json`), the ledger rebuilt by
5e63e640ef.

## Where the refusal stands

On origin 5e63e640ef, re-graded over the cb93f7760c ledger, four rows still refuse the publish:
gas repeats 7, INV_OVERDUE_WITHIN_PAGE_BALANCE 8 (SYN-2016-099), INV_OVERDUE_WITHIN_BALANCE 1
(SYN-2016-107), and 1 closing refund outside its class (PROS-2023-0338g). EPG, estimate-follows-reads
and both EBSS rows were already spent on origin (10bf51c370, 204b68cca5, 5e63e640ef). This landing
closes INV_OVERDUE_WITHIN_BALANCE.

## SYN-2016-107: fixed

**What happened.** The desk opened a journey on 16 Oct 2018 printing GBP 25.70 overdue. The
electricity leg had left level DD on its final bill of 7 Oct with a GBP 25.70 scheme debit. That debit
is owed on the leg's closing statement, due 4 Nov. The gas leg paid its GBP 20.30 final bill on its due
date, 15 Oct. By the evaluator's reading nothing was owed on 16 Oct, and it is right.

**Why.** `arrears_engine.left_level_asks` meets each leg's bills with that leg's own cash first
(`cash_leg`), then pools whatever names no leg. `cash_leg` named no leg for a credit bill's note
(`credit:<leg>:<period>`), although the note's id carries the leg. The triad's own leg balance
(`live_payment_triad.py`, `own = (observed_cash_event_id(leg), f"credit:{customer_id}:")`) already
counts the note as that leg's cash, and so does `leg_leave_dates` (`_credit_note_leg`). So gas's
GBP 31.70 credit bill of Sep 2017 went into the account-wide pool. There it met the oldest owed bill,
which was the electricity debit. The gas final bill was then asked at GBP 46.00 on its own due date,
and the debit moved with it, from 4 Nov to 15 Oct.

**Reproduced before fixing.** The company ledger is not in the run output. I rebuilt it from the
household's page ledger and the export's level collections (`/tmp/seat_ov/replay2.py`) and called the
desk's own `left_level_asks` and `age_left_level`. On 16 Oct the result was GBP 25.70 overdue, due
15 Oct, one day: the same figure and age the desk printed.

**Fix.** `cash_leg` returns `_credit_note_leg(e)` when the event is a credit note. That is one
function, and `left_level_asks` is its only caller.

**Control.** `test_a_credit_bill_meets_its_own_legs_bills_not_the_other_legs_scheme_debit` in
`tests/company/billing/test_a_leavers_cash_meets_its_own_legs_bills_first.py`. It takes both legs of
the partition at once: a leg-named note gives 0.0 overdue, and a note naming no leg still pools and
gives 25.0. The mutation (drop the new branch) turns it red. The other three tests in the file are
unchanged and pass.

**Reach on this book.** I replayed every one of the 953 journey openings, with the fix and without it.
108 of them are on a household that has left level DD. Four move:

| household | opened | overdue unfixed | overdue fixed | evaluator |
|---|---|---|---|---|
| SYN-2016-107 | 2018-10-16 | 25.70 | 0 | nothing owed (the breach) |
| SYN-2016-542 | 2019-04-16 | 21.91 | 0 | gas scheme debit owed |
| PROS-2018-0359 | 2022-07-16 | 1.69 | 0 | gas scheme debit owed |
| SYN-2016-183 | 2022-06-03 | 67.22 | 69.25 | owes; page balance 79.35 |

Neither row can breach the other way. For SYN-2016-542, cash after leaving meets every ask due by
16 Apr, and the gas scheme debit (GBP 123.24) is asked on the gas leg's statement on 29 Apr. So the
journey opens later. It does not vanish.

**A second divergence, found here and NOT fixed.** The evaluator reads a leg that leaves on its final
bill as demanded the debit by that bill, due on that bill's own due date (home_moves.md s.8.8f
choice 27, `_left_level_owed`). The desk always dates the leg's debit at `left + 28`
(`leg_leave_dates`, `leg_due`). So for SYN-2016-542 the evaluator counts the debit owed from 15 Apr,
and the desk from 29 Apr. The difference makes the desk lenient, so it can only open a journey later,
never early, and no row breaches on it. It is still two homes for one rule. It goes in the handoff,
not this landing.

## Prediction for the next book, filed before it is built

On the next book built on a commit carrying this fix, over the same world:
- **INV_OVERDUE_WITHIN_BALANCE: 0** (from 1). SYN-2016-107 opens no journey on 16 Oct 2018.
- INV_OVERDUE_WITHIN_PAGE_BALANCE: still 8, all on SYN-2016-099. That is a different cause (below),
  which this fix does not touch.
- Journeys: at most 2 fewer opened on the days above (SYN-2016-542 and PROS-2018-0359 open later). I
  cannot yet say what the later openings print.

## SYN-2016-099: named, not fixed

The desk printed GBP 1.30 overdue from 31 Mar 2017, and wrote off GBP 1.30 on 5 Mar 2018 (the page
says "GBP 1.30 on the account" and prints -0.68). The household's pages sum to GBP 0.68. The
difference is exactly the GBP 0.62 the export records as collected, successfully, on 16 Mar 2017 for
the electricity stub bill INV27115 (1 Mar 2017 only, issued 2 Mar).

The arithmetic: the household owed GBP 15.93 (electricity 1.30, gas 14.63) before 16 Mar. The desk's
GBP 1.30 is that less the gas GBP 14.63 alone. **So the electricity GBP 0.62 cash never reached the
company ledger.** The page-ledger replay with that cash reads GBP 0.68. The desk aged the debt from
30 Mar, which is the gas leg's statement (left 2 Mar + 28).

The cause is in the crossing of a final stub bill's direct debit onto the company ledger after the
account closed ("its own record holds the account closed after 2017-03-01"). It is not in ageing. The
next step is to run the triad on this household's electricity leg through March 2017 and see whether
the INV27115 settlement is posted. **Prediction:** it is not posted, or it is posted to an account id
other than `ACC-SYN-2016-099`.

## Still open after this landing

- SYN-2016-099, above.
- PROS-2023-0338g's closing refund (GBP 30.68 against a bound of 0.00), read: **the N29 class in
  substance, outside it by its own rule, and the class must not be widened.** Gas refunded its
  GBP 30.68 credit on 13 Dec 2024 while the electricity leg owed GBP 34.63. Electricity's next payment,
  on 15 Dec, was GBP 58.68: the debt plus a GBP 24.05 overpayment, itself refunded on 31 Dec. Because
  that payment is not the debt's sum, `_owed_is_collected_after` refuses the class. The remedy is the
  exception's own `retired_by` (`n29-close-set-off-nets-issued-debt`): the world's closing set-off nets
  the other leg's issued, unpaid bill on the refund day. That is a world-writer fix, and it retires
  all 8 rows, not this one. **Prediction once it lands:** INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT
  0 of 8 on this world.
- INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 7 (4df2b4f892: the run's own settlement rows for
  PROS-2017-0192g are the next step).
- The final-bill leaver's debit date, which has two homes (above).
