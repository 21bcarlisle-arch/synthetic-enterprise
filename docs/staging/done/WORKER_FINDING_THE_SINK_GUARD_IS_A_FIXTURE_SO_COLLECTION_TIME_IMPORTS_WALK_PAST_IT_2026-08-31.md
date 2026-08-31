# The sink guard is a fixture, so a collection-time import walks straight past it

**Class:** `controls_that_cannot_fail` — born archived (the class already holds this shape).
**Found:** 2026-08-31, while unwedging the publish gate at `3ba51f9cf`.
**Severity:** the guard is not wrong, but its coverage is narrower than its own docstring claims,
and the narrowing is invisible from the inside.

## What was measured

`tests/production_surface_guard.install()` is called from `tests/conftest.py::_no_real_state_write`,
an **autouse fixture**. A fixture runs per test. Module import happens at **collection**, before any
fixture exists.

So the guard covers a write reached from a test *body*, and does not cover a write reached from a
test *module's import*. The two are not hypothetical variants — today they produced opposite
outcomes on the same underlying write:

* `tests/tools/test_run_frozen_baseline.py` imports the module at line 6, module scope. Collection.
  **Green for months**, and every run wrote `docs/observability/book_growth_campaign.json`.
* `tests/background/test_process_run_complete.py::TestFrozenBaselineOutOfBandTrigger` imports the
  same module *inside the test body*. **Red**, and it wedged all publishing for six hours.

The write is identical. Only its position relative to the fixture differs.

## Why this matters beyond the wedge

The reason `docs/observability` became a whole `PROTECTED_SURFACE` this morning was measured: 23%
of `autonomous-runner-log.md` was written by pytest, and the delivery seat read that ledger and
reported a usage limit to the director that did not exist. The guard's own argument is that **a
production surface a test can write is not evidence.**

That argument is not fully discharged. `simulation/run_phase2b.py:217` runs
`CUSTOMERS = live_population()` in its module body, which reaches
`live_population._resolve_campaign` and writes `book_growth_campaign.json`. **Twelve** modules under
`tools/` and `background/` import a `simulation.run_phase*` entry point at module scope (measured by
grep, not estimated); of those, the six that import `run_phase2b` or `run_phase4c_on_phase2b`
reach the book build, and several of their test files import *those* at module scope in turn. Every
one of those writes still lands on the live file at collection time, guard installed or not.

## What was NOT done, and why it is left named rather than fixed

The instance is fixed: `tools/run_frozen_baseline.py` now imports the replay at call time
(`3ba51f9cf`). That removes one importer. It does not close the hole.

Two candidate class fixes, neither taken in a bounded tick:

1. **Install the guard at collection too** — a `pytest_collectstart`/plugin-level install rather
   than an autouse fixture. This is the honest fix and it is also the expensive one: it will red
   every module that currently builds the book at import, which is the whole point and also a
   large, unmeasured blast radius. **Measure the red count before doing this**, report-only.
2. **Stop `run_phase2b`'s module body from building the book.** The root cause, and a much larger
   refactor: `CUSTOMERS` is a module global with many readers.

Recorded now rather than after the next wedge, because the failure mode is that (1) looks like a
one-line change and is not.

## The falsifier, if someone wants to check this rather than believe it

Under pytest, `tests/production_surface_guard.protected_targets()` is a pure function and
`install()` takes a monkeypatch. A test that asserts the guard is active during
`pytest_collection` — not during a test — is the control this finding says does not exist.
