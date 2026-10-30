**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# `tests/company/billing` run whole at origin cd4fc5b8d8 reds 41 tests that pass alone (2026-10-30)

This was found in the pretest for `the-fresh-run-at-the-meter-fixes`. The run was at origin `cd4fc5b8d8`, in
worktree `/var/tmp/fresh-run-wt-cd4fc5b8d8`, using `python3 -m pytest tests/company/billing -q -rfE`.

## What was measured

- **Run whole:** 2,486 passed, 25 failed, 16 errors, in 58 s. The reds are in four files:
  - `test_invoice.py` (e.g. `test_correct_vat_from_bill_line_items`);
  - `test_invoice_characterization.py` (the schema census and schema-creation tests);
  - `test_collections_journey.py` (five live-run tests, all ERROR at setup);
  - `test_hh_consumption.py` (eleven, all ERROR at setup).
- **Those four files run alone:** 188 passed, 0 failed, in 137 s.
- **One failing test run alone:** it passes.

So the reds depend on order. An earlier test in the directory leaves state behind: a schema, a database path,
a cwd or a module-level cache. That state breaks these tests. They are not broken on origin.

## Why it matters

- On 29 Oct, 08a9fbcc1 read this directory as green (2,498 passed). Something landed since then made a test
  pollute, and nobody saw it, because each landing runs its own selection. That is the open class in the
  stretch log: nothing ties a change to a billing basis to the tests that drive it.
- A whole-directory pretest that reds on order cannot tell a broken origin from a polluting test. The next
  pretest would have to re-derive the split, as this one did.
- **Separately, the first whole `tests/company/billing tests/simulation` read in this pretest died with no exit
  line at about 55%.** It had shown 52 E and 17 F, and the process was gone with no exit line written. This is
  the third such death of a whole `tests/simulation` read on this box. The fresh run was therefore gated on
  billing only, and `tests/simulation` is read after the run.

## Not established

- **Which earlier test pollutes.** This is a bisection over the directory's order that I have not run. The
  cheapest test is `pytest -p no:randomly tests/company/billing/<file before test_hh_consumption.py>
  tests/company/billing/test_hh_consumption.py`, walking backwards until one pair reds.
- **Whether the simulation reds were order as well.**

NEXT: none -- the bisection is a tick-sized item, not drawn here
