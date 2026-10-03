# The payment-method seam now follows a stopped DD at the renewal

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB8_a_households_payment_channel_changes_over_its_tenure`

**Drawn as:** `pb8-l2-the-seam-follows-the-stopped-mandate` (Lane 0), the second half of PB8 L2.
The money side has followed the stop since `dd7bbce0f`
(`SEAT_FINDING_A_STOPPED_DD_NOW_REACHES_THE_MONEY_SIDE_AND_PUBLISHED_BAD_DEBT_DOES_NOT_MOVE_2026-10-03.md`).
The premise was re-measured at draw time and still held: `LiveSimInterface.get_payment_method` returned
`payment_channel_for_customer(...)`, the fixed-for-life draw, and both `run_phase2b` reads (the renewal
price's provision row and the PB7 engagement antecedent) used it.

## Pre-registration (written before the probe's output was read)

1. Over a short real run (to 2019-12-31), the board's answer at every (resi DD supply point,
   1st and 15th of every month) equals the money side's full register cut at that date: **0
   disagreements**.
2. Some renewals in that window are priced on `standard_credit` because of a stop, so the branch is
   taken in a real run: **at least 1**.

## Result (probe `/tmp/pb8l2/probe.py`, run to 2019-12-31, 404 s)

1. **Held.** 8,256 (resi DD supply point × 1st/15th of each month) questions. 359 of them were on a
   household that had been told by then. **0 disagreements** with the money side's register over the
   run's own `issued_bills(build_monthly_bills(all_records, churned))`, which has 3,669 bills and
   10 stops. The board was fed every record, so this also shows nothing after the date leaks in.
2. **Held.** 818 dated seam reads in the run. **24** answered `standard_credit` where the drawn method
   was `direct_debit`, for example PROS-2016-0098 at its renewals from 2018-07-01 on. The board adds
   no visible run time: 404 s for the window, and 16 s for the 8,256 post-hoc questions.

## What the question was, and the answer

*Can the stress trajectory a stop needs be had per customer before that customer's renewals?* **Yes.**
`HouseholdDemandRegister` draws every household's life events when it is built, before the first
term, so `income_stress_trajectory` is fixed from the start. Stress was never the obstacle.

**The bills were the obstacle.** A stop is decided on the supplier's monthly bills, and those are
assembled in `run_phase4c_on_phase2b`, after `run_phase2b` returns. At a renewal they do not exist.
The term loop is a heap on `(term_start, cid)`, though, so a customer's earlier terms are already
settled into `all_records` when its renewal is priced. `StopNoticeBoard` bills those records by the
money side's own route (`build_monthly_bills` → `issued_bills` → the rails), using only calendar
months that ended before the date.

**One thing made that unequal to the money side, and it is fixed.** The rails drew the ARUDD
notification lag from one stream walked in customer order. A household's notice date therefore
depended on how many failures sorted before it, and could not be had from its own bills. Each
customer now has its own lag stream. Which bills succeed or fail does not move (the outcome is drawn
per bill and passed in). Only lag days and notice dates move, and the rails surface is the only
thing that reads them.

## What changed

- `simulation/dd_collection_book.py`: per-customer rails lag stream. `_run_rails` records each stop's
  notice date. New `supplier_dd_stop_notices`, plus `StopNoticeBoard`, which a run installs and the
  seam reads.
- `company/interfaces/sim_interface.py`: `get_payment_method(account, fuel, as_of=None)`. When given a
  date, a DD household that had been told its DD was stopped by then reports `standard_credit`. With a
  date and no board, it **refuses by name** instead of answering the drawn method.
- `simulation/run_phase2b.py`: builds the board, feeds it beside `all_records`, and passes
  `as_of=term_start` at both seam reads.

## Not done (named remainder)

- `_book_method_of`, the method register that the own-book default belief learns over (non-default
  policy only), still asks without a date and caches per run. Making it dated means the board
  re-bills every DD account in the book at every renewal, and it is read only when
  `renewal_default_belief == own_book`.
- The triad (`background/live_payment_triad`) draws its own in-run DD outcomes. A household that the
  rails stopped can still post DD successes there. That is a third stream for one fact, and it is
  not touched here.
