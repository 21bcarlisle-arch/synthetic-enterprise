**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `unminted`

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
