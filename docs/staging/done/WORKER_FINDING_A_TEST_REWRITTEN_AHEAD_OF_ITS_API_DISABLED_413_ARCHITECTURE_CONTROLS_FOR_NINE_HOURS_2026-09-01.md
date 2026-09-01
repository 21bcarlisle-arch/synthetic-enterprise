# [WORKER FINDING] A test rewritten ahead of its API disabled 413 architecture controls for nine hours

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** unminted
**Found:** 2026-09-01 07:5xZ, by the delivery seat, running `pytest tests/architecture/` before a commit.

## Class registration

Belongs to `uncommitted_and_orphaned_work`.

## What was found

`tests/architecture/test_a_departure_reading_declares_its_population.py` was rewritten in the
working tree at **2026-08-31 21:32** — 440 insertions, 307 deletions — to test an API that was
never written. It imports eight names that exist nowhere in the repository, on any branch, in any
worktree:

    from tools.departure_population import BOOK_BOUND, BOOK_DENOMINATOR, ROUTE_CAUSES,
                                           book_departure_level
    from tools.fit_year_level_anchor import book_emission_refusal, fit_year_anchor_on_book,
                                            outside_comparison_window

`git log --all -S book_departure_level` returns nothing. `git worktree list` shows six other
worktrees and none of them holds it. The implementing lane wrote the proof and stopped.

## Why this is BLOCKING and not a housekeeping note

**It is not one control that went red. It is a collection error, so the whole directory stops.**

    ImportError while importing test module '.../test_a_departure_reading_declares_its_population.py'
    !!!!! Interrupted: 1 error during collection !!!!!

With the file restored, `pytest tests/architecture/` collects **413 tests**. With it in place,
pytest collects none of them and exits before running one. So for **nine and a half hours** every
architecture control in this repository — the population-floor ratchet, the unlanded-falsifier
controls, the constant-origin gate, the cited-constant caller check — was not merely failing but
*not running*, and any gate whose selection reaches that directory reported the interruption rather
than the controls.

That is the shape this project already has a class for, at a new address:
`WORKER_FINDING_THE_COMMIT_GATE_SELECTS_TESTS_BUT_AN_IMPORTERROR_COSTS_THE_WHOLE_SUITE_2026-08-28`
found the same mechanism inside the commit gate three days ago. **One unimportable module is not
one lost control; it is every control that shares its directory.**

## Why nothing said so

The lane that wrote it did not commit, so no gate ran against it. Nothing scans the working tree
for a test file that cannot import — the pre-commit gate selects tests by changed path, and this
path was changed by a lane that never reached the gate. A red is loud; **an uncollectable
directory is quiet**, because the thing that would have complained is inside it.

## Disposition taken

**Not deleted, and not implemented in a hurry.** The rewrite is real work and its docstring
contains a genuine finding — that a whole-book departure level taken as a mean over *decisions*
rather than over *account-years* mixes a per-segment probability with an annual one, and reads
3.6–7.5% against a 2.9–23.0% band on the committed capture. That is worth building properly.

1. The rewrite is parked verbatim at
   `docs/staging/in_progress/PARKED_test_a_departure_reading_declares_its_population_2026-09-01.py.txt`
   — a `.txt` suffix under `docs/` so pytest cannot collect it, and every line preserved.
2. `tests/architecture/test_a_departure_reading_declares_its_population.py` is restored to its
   committed version, which imports only names that exist. The directory collects again.
3. Implementing `book_departure_level` and its five siblings is queued as real work, against the
   departure-level findings already live in the staging root. **It is not this document's repair
   and must not be done to make a suite go green.**

## What is owed beyond the instance

There is no control that would catch this, and the one-leg version is narrow enough to be worth
building: **every `test_*.py` in the working tree must be importable.** Not "must pass" — a red
test is a working control — but *importable*, because an unimportable one silences its neighbours.
That is a property, it is checkable in seconds, and it fails loudly on exactly the state found
here. Filed as the next work on `uncommitted_and_orphaned_work`, whose register
(`docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md`) already records that
its four existing controls each cover one record type and that a fifth is uncovered by
construction. This is the fifth.
