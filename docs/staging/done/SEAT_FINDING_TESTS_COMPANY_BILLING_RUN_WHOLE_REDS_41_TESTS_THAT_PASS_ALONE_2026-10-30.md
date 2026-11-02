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

## An observation, not a bisection (2026-10-30, seat executor, gas volume build)

In an isolated worktree at origin 792adb1a96, with the gas volume build applied (it touches no file the four red
files import beyond `company/billing/monthly_bill_assembly.py`), `python3 -m pytest -p no:cacheprovider -q
tests/company/billing` read **2,535 passed, 0 failed** (158.9 s). I cannot say from one run whether the order
dependence was fixed by another landing, depends on `.pytest_cache` (disabled here), or depends on the shared
tree's state. The next step is the same run with the cache provider on, and then on the shared tree.

## The cache provider on, at origin 85b044be54 (2026-11-02, Lane 0 `the-fresh-run-after-the-pc2-and-gas-fixes`)

The step the note above names. In a clean worktree at origin 85b044be54 (the gas build on origin), with the cache
provider on, `python3 -m pytest tests/company/billing -q -rfE` read **2,536 passed, 0 failed** (157.8 s). The 41 reds
do not reproduce with the cache provider on or off, so `.pytest_cache` was not the cause.

What this does not establish: which commit removed the order dependence between cd4fc5b8d8 and here, or whether it
depended on the cd4fc5b8d8 worktree's own state. No bisection was run, because there is no red to bisect. If the
whole-directory read reds again, that is a new episode and a fresh finding.

## Done

The reds do not reproduce at origin HEAD, so the pretest gate the fresh run needs is clean. Moved to done/ under
DIRECTION item `the-fresh-run-after-the-pc2-and-gas-fixes`. Left: nothing on this finding. The open class it names
(nothing ties a billing basis change to the tests that drive it) belongs to the stretch log, not here.
