# [WORKER-REPORT] The wedge alarm's evidence file was written by the gate's own test suite, every cycle

**Drawn:** 2026-08-10 19:55–20:10Z as PUBLISH-GATE WEDGE RUNG 1 (priority zero).
**Wedge age at draw:** ~1765 min, 150 consecutive gate failures, no pass at HEAD `22b097a1b`.
**Disposition:** two defects FIXED with R15 mutation evidence; one filed, NOT fixed (blast radius).
**Rank:** proposed top-of-backlog for the filed item.

## Part 1 — the named blocking test is already green, and the record proves the order

`docs/observability/.publish_gate_state.json` cited one blocking test:

```
FAILED tests/background/test_publish_gate_subject_is_head.py::
       test_the_timeout_clears_the_floor_the_measurement_implies
```

Run at HEAD (working tree byte-identical to HEAD for both of this control's inputs —
`git diff HEAD -- docs/observability/publish_gate_subject_cost.json` is empty, and
`GATE_SUITE_TIMEOUT_SECONDS` is committed source):

```
tests/background/test_publish_gate_subject_is_head.py    30 passed in 1.37s
```

`measured_gate_timeout_floor` answers `int(max(1291.9, 1167.5) × 2.0) = 2583`, and
`GATE_SUITE_TIMEOUT_SECONDS = 2600` clears it.

**The cause was the untracked evidence file, and it was already fixed one minute before the
last recorded failure.** All five in-window failures predate the repair:

| failure ts (UTC) | git hash |
|---|---|
| 19:20:16, 19:28:05, 19:35:58, 19:43:12 | 1fd85cb27 / ad67e713b |
| **19:51:01** | ab8d19b37 |
| — `c228b48f5` lands the cost record — | **19:52:06** |

The alarm's "5 failures in-window" was true and its implied conclusion ("still red now") was
not. That is a lagging-state read, already a filed class
(`feedback_lagging_monitor_state_redraws_priority_zero`); it is not re-filed here.

## Part 2 — OBSERVED (R9): the gate's own tests write the machine's live diagnostic state

**Evidence, caught in the act.** `docs/observability/.last_gate_blocking_tests.json` at 20:00Z:

```json
{"git_hash": "1c0414e9fb49f13a46043b3402d1fa581d172786", "node_ids": [], "ts": 1786391795.27}
```

```
$ git cat-file -t 1c0414e9fb49f13a46043b3402d1fa581d172786
fatal: bad object 1c0414e9fb49f13a46043b3402d1fa581d172786
```

That SHA is not a commit in this repo. It is a **sandbox** commit, from the throwaway git repo
`test_publish_gate_subject_is_head.py::sandbox` builds — written into the live file at
20:56:35 BST, which is when this seat ran that test file.

**Why it escaped.** The `sandbox` fixture redirected `PROJECT_DIR`, `HEAD_CHECKOUT_ROOT`,
`LAST_TESTED_HASH_FILE` and `LOG_FILE`. `GATE_BLOCKING_TESTS_FILE` is declared
`PROJECT_DIR / "docs" / "observability" / ...` and resolved at **import** time, so re-pointing
`prc.PROJECT_DIR` afterwards moves nothing. The fixture isolated the paths its author thought
of; the constant added later by a different atom escaped in silence
(`feedback_a_test_isolates_the_paths_it_thought_of`).

**Why it matters, and it is not cosmetic.** That file exists precisely so the alarm stops
guessing — its own comment records the mtime-ranked finding list scoring 0/8, 0/8, 0/8 across
four episodes. A fresh-but-empty record does **not** read as absent: `last_blocking_tests`
returns `([], hash)` inside its staleness window, so the alarm reports "the gate was red and
printed no FAILED line" and falls back to the guess. And
`tests/background/test_publish_gate_subject_is_head.py` is in the gate's own **scoped blocking
list** (observed in the live argv at 19:55Z), so this fired on every publish cycle.

**Fixed, two layers, both mutation-proven.**

1. *Caller.* The fixture now **derives** its redirect set from prc's source —
   `_project_dir_paths_this_module_writes()` walks the module AST for `PROJECT_DIR`-derived
   constants that the module mutates (`write_text`/`unlink`/`mkdir`/…, including via
   `.parent`). A constant added tomorrow is isolated tomorrow, not at the next incident.
2. *Class.* `docs/observability/.last_gate_blocking_tests.json` added to conftest's
   `_PROTECTED_WRITE_PATHS`, following that tuple's own stated doctrine: "a guard list only
   protects the paths somebody thought of, so the answer to finding a hole in it is to fill
   the hole, not to isolate the caller."

**R15, the mutation actually run** — the derivation altered to skip that one name:

```
FAILED ...::test_the_sandbox_moves_every_writable_path_off_the_real_tree
  AssertionError: ['GATE_BLOCKING_TESTS_FILE'] still point inside /home/rich/synthetic-enterprise
FAILED ...::test_mutation_pointing_the_gate_back_at_the_tree_reds      (G-T2 guard fired)
FAILED ...::test_a_red_suite_does_not_stamp_the_tested_hash            (G-T2 guard fired)
3 failed, 30 passed
```

Both controls fire independently on the same named defect. Restored: **136 passed** across the
four affected files plus `test_process_run_complete.py`. The live file was byte-unchanged by
the re-run, verified by diff.

Three further guards were written against the derivation itself, because a derived population
that silently returns `set()` would make the redirect loop theatre: a **vacuity** guard (the
population is non-empty and names `GATE_BLOCKING_TESTS_FILE` explicitly), and a
**discrimination** mutation proving the walker separates a path that is only *read* from one
that is *written* — otherwise its agreement with reality would be a coincidence.

## Part 3 — the annotation pass could only ever report ONE red

`remainder_pytest_argv` returned `list(base_argv)` — the blocking gate's argv **unchanged**,
`-x` and all. The pass whose entire contract is "the reds that no longer block still have to
be SEEN" was running under fail-fast, so it stopped at the first red. Its caller's `reds[:32]`
cap was dead code; so was `GATE_MAX_CITED_BLOCKING_TESTS = 5`.

Observed in the live log at 19:59Z, from a real publisher cycle:

```
- [2026-08-10 19:59 UTC] [process_run] Remainder annotation: rc=1, 1 non-blocking red(s), ...
```

"1 red" is what that pass printed whether there was one or thirty. This is the same flag that
made the **eleventh** wedge read as four flapping tests across six cycles when it was a STACK
of three simultaneous reds, each tick paying one layer and reporting it as *the* cause
(`WORKER_FINDING_THE_ELEVENTH_WEDGE_WAS_A_STACK_NOT_A_BUG_2026-08-10.md`, recommendation 1).

**Fixed at the seam, not at the gate.** `remainder_pytest_argv` now strips `FAIL_FAST_FLAG`;
`-x` stays on the blocking gate, where the verdict is `rc != 0` either way and stopping early
returns latency to the lanes. The R15 arm is an **outcome** test, run as a real subprocess
against three genuinely failing tests, because an in-process assertion about a flag list would
pass just as happily on an argv that does not do what we think `-x` does: the gate's argv
reports 1, the remainder's reports 3, and the fail-fast red is a member of the enumerated set.

The pre-existing `test_the_remainder_pass_is_independent_of_the_scope` asserted
`remainder_pytest_argv(base) == base`, which is what pinned the flag. Its **property** (same
subject, same deselections, never "full minus scoped") is right and is now asserted directly —
subject, marker expression, heavy ignores, and `set(remainder) <= set(base)` so the pass may
drop flags but never acquire a new subject.

## FILED, NOT FIXED — the write guard is keyed to one syntactic form

`prc.log()` appends via the **builtin** `open()`:

```python
with open(LOG_FILE, "a") as f:      # background/process_run_complete.py:682
```

G-T2 patches `pathlib.Path.write_text` / `write_bytes` / `open`. A builtin-`open` write to a
protected path passes the guard completely — so adding the log to `_PROTECTED_WRITE_PATHS`
would protect nothing. Demonstrated (R9, observed, one test, no monkeypatching of `prc.log`):

```
$ pytest tests/background/test_publish_decoupling_exit.py::test_the_annotation_pass_cannot_block_a_publish
1 passed in 0.05s
- [2026-08-10 20:03 UTC] [process_run] Remainder annotation skipped (non-fatal): suite exploded
- [2026-08-10 20:03 UTC] [process_run] Remainder annotation: rc=1, 1 non-blocking red(s), 56 open finding(s)
```

Two fabricated `[process_run]` lines in the live `sim-runner-log.md`, indistinguishable from
publisher events, in the exact log the wedge draw and every human diagnosis reads —
`feedback_publish_gate_red_find_the_test_in_sim_runner_log` names it as *the* place to look.
That test isolated `PROVENANCE_FILE` and `REMAINDER_ANNOTATION_STATE_FILE`, the two it thought
of, and left `log`. Same class as Part 2, one path further out.

**Not fixed here, deliberately.** Closing it means guarding `builtins.open` and then adding
the log to the protected list — and the moment the log is protected, every test that drives
any logging prc function reds unless it isolates `LOG_FILE`. That blast radius has to be
measured against the whole suite before it lands (`feedback_measure_blast_radius_before_
choosing_a_dirt_predicate`), and a blanket stdlib patch is itself a filed hazard
(`feedback_blanket_stdlib_patch_escapes_test_mocks`). Rushing it beside a live publisher would
risk wedging the thing this draw exists to unwedge. Queued per SELF-INTERRUPT DISCIPLINE.

**Suggested shape:** guard `builtins.open` in write modes only, reusing `_is_protected`
unchanged; measure the red set on a full run; then add `docs/observability/*-log.md` to the
protected tuple in the same commit as the `LOG_FILE` isolations the measurement names.

## Changed

- `background/publish_scope.py` — `FAIL_FAST_FLAG`; `remainder_pytest_argv` strips it.
- `tests/background/test_publish_scope.py` — property-form independence test; flag-removal
  test with a vacuity precondition; R15 subprocess enumeration differential (1 vs 3).
- `tests/background/test_publish_gate_subject_is_head.py` — derived isolation population;
  fixture redirect loop; vacuity, discrimination and live-escape controls.
- `tests/conftest.py` — `.last_gate_blocking_tests.json` protected.
