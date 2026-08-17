# WORKER RECORD — the test-process write to a live measurement ledger is now refused at the choke point, not at the one caller that was caught

**Severity:** RECORDED · **Lane:** H_harness · **Disposition:** BUILT (the refusal); one named sub-item of the parent finding remains OWED

**Discharges:** item 1 of
`WORKER_FINDING_THE_ONLY_DOOR_PAIR_A_TEST_RUN_CAN_REPUBLISH_IS_THE_ONE_NOTHING_COMPARED_TO_ITS_LEDGER_2026-08-17.md`
("**The write itself is not stopped.**"), drawn as the RUNG-1c BLOCKING finding on lane
H_harness by the 2026-08-17 scheduled tick.

## What the parent finding left, and what was actually wrong with its own fix

The finding named the fix as `simulation/run_phase2b.py:2448` — default `ledger_path` →
redirect or refuse under a test process — and queued it because that file carries another
lane's uncommitted hunks at `:160` and `:834` (verified still true in this tree: the B12
`live_dwellings()` / `live_drawn_households()` work).

**One number the parent finding under-counted, re-measured here:** it said "ten-plus test
modules" import `run_phase2b`. `grep -rln run_phase2b tests/ | wc -l` returns **67**
(2026-08-17). The mechanism does not depend on the count, but the blast radius does.

**That fix would have been an instance fix, and R10 forbids closing this class with one.**
`run_phase2b` is the caller that happened to get caught. The shape — a defaulted `ledger_path`
resolving to a live published record, invoked from a process holding a fixture population — is
equally true of every `tools/couple_*.py --write-ledger` main and of every ledger added
tomorrow. They escape today only because no test happens to import them.

So the refusal was built at the **write**, and the two-lanes-one-file blocker dissolved: the
repair never needs to touch `run_phase2b.py` at all.

## Built

`background/live_ledger_guard.py` (new) — `guard_live_ledger_write(path, writer=...)` raises
`LiveLedgerWriteUnderTest` when a test process's write resolves inside
`<PROJECT_DIR>/docs/observability/`. Outside a test process it is a no-op, so real runs, real
daemons and real `--write-ledger` invocations are untouched.

Wired at the three live measurement-ledger writers, top-level import, no `try`:

| writer | ledger |
|---|---|
| `background/gap_metric.py::write_gap_entry` | `coupled_gap_ledger.json` (the Proof door's supplier) |
| `background/dd_h_solvency_gap.py::record_gap` | `dd_h_solvency_gap_ledger.json` |
| `background/conversation_gap_ledger.py::record_gap` | `conversation_gap_ledger.json` |

**Two design choices that are the control, not decoration:**

* **The subject is DERIVED, twice over.** A live record is *any path resolving inside the
  record directory* — not a filename list — so a ledger invented tomorrow is covered the day it
  exists (`test_a_new_ledger_nobody_enumerated_is_covered_on_the_day_it_is_created`). The class
  census's population is *every `background/*.py` speaking the `GAP_LEDGER_PATH` house
  convention*, binding **or importing** it.
* **There is deliberately no env-var override.** An escape hatch is a FAIL-OPEN door that the
  offending process is precisely the one able to set. `test_there_is_no_env_var_override` reads
  the guard's own AST and fails if the refusal path ever learns to read the environment.

## R15 — five source mutations, every one proven to fire

| mutation | pattern | red test |
|---|---|---|
| `in_test_process` → `PYTEST_CURRENT_TEST` only | FAIL-OPEN (collection/import-time writes) | `test_detection_survives_the_env_var_being_absent` |
| `is_live_record_path` → `str().startswith()` | FAIL-OPEN (a `..` spelling names the same inode) | `test_a_relative_and_dot_dot_spelling_of_the_same_file_is_the_same_subject` |
| unresolvable path → `return False` | FAIL-OPEN (unresolvable ≠ innocent) | `test_an_unresolvable_path_fails_closed` |
| drop the `not in_test_process()` early exit | refuse-everything (silently kills the real measurement) | `test_outside_a_test_process_the_live_write_is_permitted` |
| delete the guard call from `write_gap_entry` | the incident itself | 2 red, incl. the class census |

`15 passed` restored. The census has its own vacuity guard
(`test_the_writer_population_is_not_empty`) so a broken AST predicate reds *before* the class
test can pass over an empty set.

## The mutation battery reproduced the incident on the live artefact — disclosed, and repaired

Running mutation 5 (guard deleted from `write_gap_entry`) let the end-to-end test do exactly
what the finding describes: it wrote `W2_TEST_probe` into the real
`docs/observability/coupled_gap_ledger.json`, taking it from 14 entries to 15. **This is the
defect demonstrating itself, from my own process, one commit away from the door.**

Repaired in the same tick: the probe key was removed and the file rewritten in
`write_gap_entry`'s own format (`indent=2, sort_keys=True`); `git diff` on that path now
contains **zero** `W2_TEST_probe` lines and 14 entries remain. The residual diff against `HEAD`
is pre-existing drift written by earlier test processes — i.e. the finding's own evidence, left
in place rather than laundered.

**Standing lesson:** this mutation battery must be run with the live ledger backed up, because
the mutation under test is precisely "the thing that protects the live ledger is gone."

## What is still OWED (unchanged from the parent finding, not re-derived)

1. **The SITE-lane live tripwire is still not shipped**, for the reason the parent gave: it
   would be born RED, because the committed door (`0.0833907649896623`) and the committed
   ledger (`0.0859375`) have disagreed for five days. Repairing that divergence is the publish
   lane's territory
   (`WORKER_FINDING_THE_PUBLISH_PATH_COMMITS_THE_DOOR_AND_NOT_THE_RECORD_IT_RENDERED_2026-08-17.md`).
   A control that must wedge a shared gate to be honest is a sequencing problem, not a reason
   to weaken it.
2. **The narrowing to measurement ledgers is measured, not assumed.** `docs/observability/`
   also receives **75** persisting functions across 40 other `background/` modules — daemon
   STATE writers (`supervisor.py`'s stuck/interleave/stall savers, `trust_ledger.py`,
   `fidelity_evidence_ledger.py`, `process_run_complete.py`). Same shape, same directory, same
   test processes. Guarding them wholesale would red the many existing tests that deliberately
   write live state paths, so it is **owed, not covered** — and the count is pinned in
   `test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed` so it cannot grow
   unnoticed. If it moves, widen the guard; do not bump the bound.
3. **The store's oversized-`note` roll path** (parent finding's own "Owed, not taken") is
   untouched by this tick.

## R9 — not established, flagged rather than asserted

* This closes the *write*. It does **not** repair the door/ledger divergence at `HEAD`, and no
  published figure was changed by this tick.
* The guard's test-process detection is two heuristics OR'd. A process that imports `pytest`
  for an unrelated reason would be refused. That direction is chosen deliberately: a refused
  write costs one loud error in a caller that already catches it; a permitted one costs a
  published figure.
