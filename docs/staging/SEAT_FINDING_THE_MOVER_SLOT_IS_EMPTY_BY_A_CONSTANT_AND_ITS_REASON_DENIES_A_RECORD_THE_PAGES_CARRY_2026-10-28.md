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
