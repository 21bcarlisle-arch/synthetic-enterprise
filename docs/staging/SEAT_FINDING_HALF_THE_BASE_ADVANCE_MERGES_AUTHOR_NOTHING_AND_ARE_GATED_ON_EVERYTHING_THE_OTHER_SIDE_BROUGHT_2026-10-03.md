# Half the base-advance merges author nothing, and are gated on everything the other side brought

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `base-advance-merges-select-by-their-combined-diff` (Lane 0 delivery)

Prices the gate time spent on `surgical_land --merge origin/main` commits whose combined diff is
empty, and records the selection change that stops spending it.

## 1. Pre-registration (written 2026-10-03 20:50Z, BEFORE the census below was run)

**What the thing is.** A merge on `origin/main`'s first-parent line. Its *combined diff* is
`git diff-tree -c --name-only <merge>`: the paths whose merged content differs from EVERY parent --
the only bytes no parent already carried (same definition `commit_narrative._carries_work` adopted
in `ea39d8063`). "Empty" means that list is empty. A re-derived path (`surgical_land.rederive_in`)
or a resolved conflict is in the combined diff, so such a merge is NOT empty.

**What the gate selected for it.** `tools/pre_commit_test_gate.py` reads `git diff --cached` against
the extract's HEAD, which is the FIRST parent -- so for a base advance it selects on everything
origin brought in since the merge-base, i.e. code already gated when it landed on origin.

**Windows.** Two consecutive 24-hour windows of committer time ending 2026-10-03 20:45Z
("this stretch" = the later). The brief's 15/31 and 23/38 used a window it did not name; these are
mine and are named so the next brief can be read against them.

**Prediction.** Empty share 40-65% in each window. The receipt's `tests:` seconds (the LAST pytest
summary in the hook chain -- a floor on the chain's wall time, not its total) has a median over
100 s for the empty merges.

## 2. Result (census run 2026-10-03 ~20:55Z over every merge on `origin/main`, both windows)

Every merge in both windows came through `surgical_land --merge` and carries a receipt.

| window (24 h, ending) | merges | combined diff EMPTY | receipt pytest seconds on the empty ones | median | old selection on them | new |
|---|---|---|---|---|---|---|
| last (2026-10-02 20:45Z) | 25 | **24 (96%)** | **7,336 s (2.0 h)** | 282 s | 58.9 test files each | 0 |
| this (2026-10-03 20:45Z) | 90 | **77 (86%)** | **29,634 s (8.2 h)**, 76 of 77 parsed | 274 s | 48.4 test files each | 0 |

The 14 non-empty merges (re-derived renders, resolved conflicts) selected 996 test files between
them on the old rule and 391 on the new one -- they still select, mostly through `CONTROL_TESTS`.

**The prediction is REFUTED on the high side, and kept here as written.** I predicted 40-65%
empty; it is 86-96%. The brief's 15/31 and 23/38 were not my windows and I cannot reconcile them
to these without knowing theirs. The median prediction (>100 s) held. The window also moved: the
later 24 h has 3.6x the merges, which is the race the brief describes -- several receipts are the
same base advance gated three times by three lanes (`07ed31f3d`, `6f0d871ba`, `ec4b247bb` each ran
the same 1,454 tests for ~16 min).

**What the seconds are.** The receipt's `tests:` is the LAST pytest summary in the hook chain. On
these commits the test counts match the test gate's selection size, so it is the test gate's
pytest, and it is a floor on the chain's wall time, not the chain. The site-lane gate (~150 s when
it fires, `commit_hook_step_timings.jsonl`) selects by the same first-parent diff and is NOT changed
here -- it is the next-largest cost on the same shape.

## 3. What changed

`tools/pre_commit_test_gate.selection_paths`: for a merge, test selection keys on the staged paths
that also differ from the OTHER parent -- the combined diff. The merge parent is read from
`PRE_COMMIT_GATE_MERGE_PARENT` (set by `surgical_land.run_gate`, whose extract has no `MERGE_HEAD`)
or from `MERGE_HEAD`. A token that is not a commit, or is already in HEAD's history, is ignored and
the full staged set is selected; a failed diff also selects everything. Every structural check in
`main` and in the hook chain still reads the full staged set. The token is stripped from the
suite's environment so tests that call `main()` cannot be narrowed by a merge they are not part of.

**What this gives up.** Two green sides can union to red (one side renames a function, the other
adds a caller of the old name) and no path in such a merge is in its combined diff. That risk was
already present for every path the gate did not select; it is now present for base advances too.
The publish gate's full run is what still catches it.

Control: `tests/tools/test_a_merge_is_selected_by_its_combined_diff.py`. Mutations, each red:
selecting the full staged set (the old rule) reds the EMPTY leg; selecting nothing reds the
NON-EMPTY leg; dropping the ancestor refusal, the `run_gate` hand-off, the `main` wiring, or the
token strip (`test_pre_commit_test_gate.py`) each red their own leg. `--no-renames` on the diff was
an EQUIVALENCE (`--name-only` prints a rename's destination), so it was removed. Run green from
this worktree, from the shared tree's cwd, and with a merge token in the environment.

**Read the next brief's no-work share against this table.** The expected effect is that an empty
base advance's gate drops from ~280 s of pytest to the fixed structural steps.
