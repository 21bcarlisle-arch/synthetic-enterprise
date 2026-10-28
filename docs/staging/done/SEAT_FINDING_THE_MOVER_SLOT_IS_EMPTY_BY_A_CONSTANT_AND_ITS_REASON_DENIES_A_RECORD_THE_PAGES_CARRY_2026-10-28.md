**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The mover slot is empty by a constant, and its reason denies a record the pages carry (2026-10-28)

**Found by** the second cold read's grade of leg two (the reading is
`docs/staging/SEAT_READING_THE_SECOND_COLD_READ_ON_THE_1691EC0ECD_BOOK_2026-10-28.md`). BLOCKING
because the correctness stretch cannot exit while one of the eight slots is not honestly empty
(director's ruling of 26 Oct, step 5 and the exit test).

## What is wrong

- `_score_mover` in `tools/generate_explore_cast.py` is `return None` with no condition. The slot
  never ranks a household. Its "0 matched" is the constant, not a count.
- The printed reason (`MOVER_EMPTY_REASON`) says: "The published record carries no move-out event
  and no final-bill marker". On the 1691ec0ecd book's regenerated pages, a `final_bill` timeline event
  stands on 866 accounts and `moved_out` on 259. On the live pages, C1 carries `final_bill` on
  2016-04-20 and `moved_out` on 2016-04-21. Both come from
  `tools/generate_customer_reaction_chain.py` (`_MOVE_EVENT_TYPES`).
- The reason's third clause is still true. No OCC- account names the household it replaced: the
  run's `incoming_occupant_of` is not on the customer pages. The run has the link (`home_move_ins`
  carries `premise` → `customer_id`), and the page does not publish it.
- The reason's "What closes it … the next published run is the first that can fill this slot" was
  written as a prediction. A fresh full run has now been published and graded, and the slot still
  cannot fill, because the rule does not read the record.

This is CLAUDE.md's "a guard that refuses everything passes all of them", with a reason that has
rotted under it.

## What closes it

1. Publish the occupant link on the incoming occupant's page. The supplier knows it: the meter
   point is the same and the account opened on the move date, so it passes the epistemic wall.
2. Make `_score_mover` rank households that carry `moved_out` + `final_bill` and an occupant page
   that names them. Keep the validity predicate (final bill on or before the move date, the
   occupant's supply starting on or after it) and add a control that the slot CAN fill on a book
   that has moves.
3. Until both are done, the reason must name the one check that fails (no occupant link on the
   record), not the two that pass.

GAP: none. This is code, not evidence.

## Pre-registration (2026-10-28, written before the measurement below)

Re-measured at draw: every OCC- page on the 1691ec0ecd book already carries `predecessor_account_id`
(251 of 251), so the finding's third clause ("the page does not publish it") is spent. The link is
the supplier-held succession at a meter point it already supplies (`docs/market_research/home_moves.md`
§8.8, choice 6), not world truth.

Seen on one account before measuring (SYN-2016-569): `final_bill` 2021-11-09, `moved_out` 2021-11-10.
**Prediction:** on most movers the page dates the final bill the day BEFORE the move-out (the event
takes `issue_date or period_end`, and the closing period ends the day before), so a predicate
"final bill on or after the move-out" fails on most of them. Second prediction: every mover's
closing balance is settled (refund or payment) on its ledger within the window; I do not know the share.

## Result against the pre-registration

- **Prediction 1 held.** 249 of 257 move-outs on the pages date `final_bill` one day before `moved_out`.
  The timeline dates a final bill at its period end, which is the company's own issue rule
  (`home_moves.md` §8.8, choice 2). The ledger raises the bill the next day. Read that way, 203 of 257
  final bills are issued on or after the move-out, and 54 are issued before it.
- **Prediction 2 was wrong.** Of 257 moved legs, 173 close at zero with no write-off, 88 write their
  closing balance off, 21 leave it owed and 7 end in credit. Only the 1691ec0ecd pages carry a
  `refund_debit` ledger entry, so a closing credit can be shown refunded on that book alone.

## Done (2026-10-28)

**The slot fills validly on the 1691ec0ecd book with SYN-2016-417**, a dual-fuel home on supply from
20 Sep 2016:
- It moves out on 5 Feb 2021, and both legs close that day.
- Both final bills are on an actual closing read: electricity £9.81 for 66 kWh, gas £3.95 for 97 kWh,
  each covering use to 4 Feb.
- Both are collected by direct debit, and the accounts are clear on 2 Mar 2021.
- OCC-a03b34fb68c1 opens on the electricity meter point on 5 Feb.

The published 4ae8da9b0f pages pick the same household. The cast was rebuilt from
`/var/tmp/second-cold-read-1691/tree` into `/var/tmp/mover-slot-1691/explore_cast.json`, with 7 of 8
slots filled and storage heating empty.

**What changed in `tools/generate_explore_cast.py`:**
- `_score_mover` reads the `moved_out` and `final_bill` events, the ledger's raise date for the final
  bill, the closing balance, and the account that opened next on the meter point. That last one is the
  occupant page's `predecessor_account_id`, a link the supplier holds (§8.8, choice 6). It never reads
  world truth.
- The slot ranks by the longest time on supply.
- Its checks, beside the suite:
  - the final bill is issued on or after the move-out;
  - no bill is raised after the final bill;
  - the closing balance is not written off, not left owed, and any credit is shown refunded;
  - a later account on the meter point names the household and opens on or after the move;
  - a dual-fuel home's other leg also moves out;
  - the closing read is actual.
- The actual-read check is the shock slot's own rule, added because the longest-supplied passer
  before it (SYN-2016-565) had a final bill estimated at 34 kWh a day after actual reads of 5. The
  use band cannot catch that, because the band is drawn over estimated bills too.
- `MOVER_EMPTY_REASON` now states only what is true when it shows: no household carries both a
  move-out and a final bill. A household that matches and fails is named by the checks it fails.
- The `mover` entry in `ACCOUNTED_BY` is dropped because its gap is closed.

**On the 1691ec0ecd book:** 155 households match and 5 pass: PROS-2020-0399, PROS-2024-0110,
SYN-2016-013, SYN-2016-322 and SYN-2016-417. The failures, counted once per household:
- closing read estimated: 124;
- closing balance written off: 71;
- final bill issued before the move-out: 49;
- id not in public format: 30;
- a bill raised after the final bill: 11;
- balance still owed: 7;
- credit not shown refunded: 6;
- prepayment yet sent estimated credit bills: 5;
- other fuel without a move-out: 4;
- no successor: 3;
- use outside the band: 6.

The per-leg counts in "Result against the pre-registration" above count a dual-fuel home twice.

**Tests** (`tests/tools/test_generate_explore_cast.py`):
- A synthetic book with one mover must fill the slot before anything checks what it shows.
- Four refusal legs each name their check.
- The empty reason appears only when nobody moves.
- The real-book "each scorer can fill and refuse" test no longer skips the mover.
- Restoring `return None` reds 6 tests.

The two defects this surfaced are filed in
`SEAT_FINDING_A_SUCCESSOR_PAGE_PRINTS_A_DIFFERENT_MPAN_AND_ESTIMATES_RUN_FIVE_TIMES_THE_METER_2026-10-28.md`.
