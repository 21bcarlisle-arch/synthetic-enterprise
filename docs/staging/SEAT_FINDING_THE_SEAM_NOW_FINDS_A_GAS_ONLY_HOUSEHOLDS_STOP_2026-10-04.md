# The seam now finds a gas-only household's DD stop on the leg the run billed

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB8_a_households_payment_channel_changes_over_its_tenure`

**Drawn as:** `the-seam-keys-a-gas-only-households-stop-on-the-supply-point-the-run-billed` (Lane 0).
Closes the first follow-on in `SEAT_FINDING_THE_TRIADS_DD_OUTCOMES_NOW_FOLLOW_THE_SUPPLIER_STOP_2026-10-04.md`.

## Premise, re-measured at draw

The cited commit (f2bc0cff2) is on origin; the defect it left was still live at origin/main 4bf859f0b:
`get_payment_method(id, "gas", as_of=)` asked the board for `household_of(id) + "g"`. The duplicate
claim the draw named is this item's own id, with no rival `surgical_land` running, so not a second piece of work.

**16 of the book's 66 gas legs are gas-only** (`SYN-2016-002`, `-005`, `-013`, ...): one leg, no suffix.
Every stop on those 16 was invisible to the seam. They read `direct_debit` at each later renewal
(price provision row, PB7 engagement antecedent) while the triad and money side paid them on receipt.

## Change

- `StopNoticeBoard.observe` indexes `(household_of(customer_id), commodity) -> customer_id`, and
  `supply_point_billed(household, fuel)` returns it. The leg is ASKED of what the run billed, not
  spelled from the id.
- The seam's gas branch asks `board.supply_point_billed(household_of(id), "gas")`. Nothing billed means
  nothing stopped, so it answers the drawn method.

Control: `test_the_gas_question_finds_the_stop_on_the_leg_the_run_billed`, over a real board, one leg
for each id shape. The old spelling reds only the gas-only leg, and an index that returns None reds both.

## Not done, and noted

- The **electricity** branch still asks the board for `account_id` as given. `_book_method_of` in
  `run_phase2b` asks `"electricity"` for every resi account in the triad, gas legs included. So a gas
  leg (`C1g`), or a gas-only household, can have its GAS stop answer an electricity question. That
  is the same shape the triad probe fell into. I left it alone here because changing it moves a run
  figure (the own-book default belief), and that is a second variable. It only matters when
  `renewal_default_belief == own_book`, and the fix is for that caller to pass the account's own
  commodity, not to change the seam.
