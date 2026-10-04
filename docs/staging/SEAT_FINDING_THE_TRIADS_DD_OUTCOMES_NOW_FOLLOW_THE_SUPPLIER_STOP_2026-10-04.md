# The company's own ledger now stops filing a stopped household as direct debit

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB8_a_households_payment_channel_changes_over_its_tenure`

**Drawn as:** `the-triads-dd-outcomes-follow-the-supplier-stop` (Lane 0).

## Premise, re-measured at draw (2026-10-04)

- `_book_method_of` in `run_phase2b` is **already dated** on origin/main: it asks the seam with
  `as_of=on`. That half of the item was spent. Nothing done for it.
- `LivePaymentTriad.record_period` was **not** following the stop. Every month of a drawn-DD supply
  point was a DD collection request, a DD remittance and an ARUDD line in the company's ledger, even
  after the supplier had cancelled the mandate and told the household. That ledger is what
  `arrears_state` and the receivable read at renewal.

## Change

1. `record_period(..., dd_stopped_by=)`: a drawn-DD bill whose due date is on or after the board's
   stop notice is paid on receipt (`standard_credit`). No collection request, an ambiguous remittance
   reference, no ARUDD and no ADDACS. The outcome draw is unchanged because the calibrated core has
   one resi tier, so only the channel moves.
2. `run_phase2b` hands it `StopNoticeBoard.notice_as_of(cid, due)`. That is the seam's rule, on the
   run's own board.
3. **An ordering defect the wiring would have created, closed in the same change.** Month bills were
   posted inside the term's record loop, while the board takes the term's records only after that
   loop. A board asked at month M's due date would have seen none of this term's earlier months.
   It would then cache `_clear_through = M`, so the triad, and the seam with it for any date in
   that window, would read "not stopped". The loop's month posts are now deferred and flushed right
   after `_dd_stop_board.observe`. Nothing in the loop reads the triad, and the next customer's
   term starts after the flush, so the posting order across the book is unchanged.
4. `SEAM_CHANNEL_FOR_METHOD` maps `standard_credit` to the seam's `standard_credit`.

## Pre-registration (written before the probe ran)

Probe over a real run to 2019-12-31, the same window as the seam finding (10 stops, 404 s):

1. **Agreement.** For every triad record of a drawn-DD supply point, the label is `standard_credit`
   if and only if the board's final notice for that supply point is on or before the due date.
   Predicted: **0 disagreements**.
2. **Reachable.** At least one triad record is `standard_credit` from a stop. Predicted: tens to low
   hundreds (10 stops, each with roughly 5–30 remaining months in the window).
3. **Cost.** Run time within +10% of 404 s.

## Result (probe `/tmp/triadstop/probe.py`, run to 2019-12-31)

1. **Held. 0 disagreements** on the agreement leg over 3,670 triad records. The probe printed 46
   rows, and they are the probe's own fault: it guessed fuel from the id suffix and so asked
   SYN-2016-021, a gas-only household, for its electricity method (prepayment; its gas method is DD).
   That household has exactly 46 months in the window (acquired 2016-03-22).
2. **Held. 129 records** are pay-on-receipt, across **10** supply points, which is exactly the
   board's 10 stops.
3. **Held.** 409 s against 404 s.

The ordering control (`test_the_board_holds_every_earlier_month_whenever_the_ledger_asks_it`), run
with the post moved back inside the loop, failed: **401 of 626** questions reached the board before
it held the months they depend on. The defect in Change 3 would have been the common case.

## Follow-on, not done here

- **The seam cannot see a gas-only household's stop.** `get_payment_method(id, "gas", as_of=)` asks
  the board for `household_of(id) + "g"`, but a gas-only household's only leg carries no suffix
  (`SYN-2016-021`), and the board keys records by the run's own id. Such a household reads `direct_debit`
  at every renewal after a stop, while the triad and the money side now pay it on receipt. It is
  the interface steward's line to fix: the seam should key on the supply point the run billed.
