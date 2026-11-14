**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `unminted`
**Discharged:** `tests/simulation/test_a_book_reload_rebinds_the_modules_that_hold_the_book.py::test_a_kept_book_holds_the_reloaded_records_after_the_reload` -- the reload helper now swaps old records for their reloaded twins inside every kept book

# A book reload leaves the supply book holding the old records, so a later test reads a split book (2026-11-14)

**What was found** (H40 L2 record, `records/WORKER_RESULT_H40_L2_A_BOOK_RELOAD_LEAVES_THE_SUPPLY_BOOK_ON_THE_OLD_RECORDS_AND_HIDES_A_RED_2026-11-14.md`).
`tests/simulation/conftest.py::reload_with_binders(run_phase2b)` reloads the module. The re-import calls
`register_drawn_points` again, and that call is idempotent by `customer_id`, so it refuses the new dicts.
`company.interfaces.supply_book.DRAWN_CUSTOMERS` keeps the old ones. After a reload,
`run_phase2b.get_customer(cid) is roster_dict` holds for **9 of 576** electricity legs. On a fresh import it
holds for 576 of 576. The helper's identity scan finds modules that hold a *replaced container*. Here the
container was kept and its *elements* were replaced, so the scan misses it.

**What it costs.** Every test after `test_a_book_reload_rebinds_the_modules_that_hold_the_book.py` in a
serial session reads a split book. `main()` rewrites registry EACs into one set of dicts, and every
`get_customer` read sees the other set. Measured: the real red
`test_every_journey_opens_the_day_after_a_bill_the_ledger_made_due` reports 3 strays in that order and 4
alone. Re-pointing `DRAWN_CUSTOMERS` at the reloaded dicts restores 4, and that is the only variable moved.
So this pollution **hides** part of a red. A hidden red is worse than a false red, because nothing goes red
to make anyone look.

**Recommended fix (the class, not the instance).** The helper should restore identity in the books that
are kept as well as rebinding the modules that hold replaced containers. The narrowest form: after the
reload, for every loaded module, find each list or dict that is NOT one of the replaced containers but
holds an element whose `id` was an element of one. Replace those elements in place with the reloaded
object that has the same `customer_id`. A coarser alternative is `withdraw_drawn_points` followed by
`register_drawn_points` around the reload. It is simpler, but it covers only the supply book, and the next
kept book would pollute the same way.

**Its control.** Extend `test_a_book_reload_rebinds_the_modules_that_hold_the_book.py` with
`assert all(p2b.get_customer(c["customer_id"]) is c for c in p2b.ELEC_CUSTOMERS)` after the reload. That
assert is red today, at 9 of 576. Then run the mutation: with the element scan removed, the assert must go
red again.

**Not established.** Whether any other kept registry (for example `ACQUIRED_CUSTOMERS`, or the
successor or incoming-occupant books) splits the same way after a reload. The fix's own scan would find
out.

## Done

14 Nov, worker tick. The narrow form was built in `tests/simulation/conftest.py`:
`_swap_old_records_in_kept_books`, called at the end of `reload_with_binders`. It pairs old and new
records by `customer_id` in lists and by key in dicts. A list where an id repeats is left unpaired.
Only dict records swap, because a scalar's id is shared by every module. Then it rewrites any kept
list or dict in any loaded module, in place.

- **Control.** `test_a_kept_book_holds_the_reloaded_records_after_the_reload` is green. Mutation:
  with the call replaced by `pass`, it reds at "567 of 576 legs read an old record", the record's 9 of
  576 seen from the other side. Its precondition is "some records were replaced", not "all": 9 legs
  come from the static roster and survive the reload as the same object.
- **A bug caught on the way.** The first draft paired with `twin not in (None, rec)`. That compares
  dicts by `==`, and a reloaded record equals its old self, so nothing was paired and the swap moved
  nothing. It now uses identity.
- **The hidden red, predicted first.** Prediction: the ordered pair (reload test, then
  `test_a_collections_journey_opens_on_the_bill_the_ledger_made_due.py`) would report 4 strays, not 3.
  Result: 4, in 168 s. The pollution no longer hides part of that red. The red itself stays with the
  collections findings.
- **Not established, still.** Whether `ACQUIRED_CUSTOMERS` or the successor and incoming-occupant
  books split the same way. The swap covers them if they do, because it scans every kept list.
- **H40's level stays at 1.** Lane H still holds SITE1's BLOCKING Expert Hour finding. An uncommitted
  move to `done/` had hidden it from the writer-side check, so the move was undone. See the H40 L2
  record, section 0.
