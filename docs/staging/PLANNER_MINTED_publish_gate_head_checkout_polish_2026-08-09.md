# [PLANNER-MINTED] Polish the publish gate's HEAD-checkout subject (2026-08-09)

**Mint source:** `DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09` — *"Implement minimally tonight,
file the proper atom for the polished version."* This is that atom. The minimal version is LANDED
and deployed; this doc scopes only what the minimal version deliberately did not do.

**Proposed atom:** `OPS_publish_gate_head_worktree`
**Lane:** `H_harness` · **level 0→2** · **loop_stage:** build
**file_scope:** `background/process_run_complete.py`, `tests/background/test_publish_gate_subject_is_head.py`
**depends_on:** none (the minimal version is already live)

---

## What landed tonight (the minimal version — do not redo)

`run_fast_tests()` materialises HEAD with `git archive HEAD | tar -x` into a throwaway
`tempfile.mkdtemp()` and runs the existing gate argv there. Measured: **0.46s, 130MB, 8,444
files** — cheap enough per cycle that no caching was needed to make it viable.

Fail-closed both ways, per R15: a checkout that cannot be materialised returns
`(False, False)` and logs why, because if committed truth cannot be produced there is nothing
legitimate to test.

Deliberately unchanged: tests that assert about the LIVE box (systemd units, daemon liveness)
still observe the real machine. Only the CODE under test moved to HEAD.

## What this atom is for

**1. A REUSED checkout, not a fresh tmpdir per cycle — and the reason is measured, not stylistic.**
A fresh extraction has no `__pycache__`, so every module compiles cold on every publish cycle. The
in-tree suite ran **10m33s**; the first clean-checkout run was still at 41% at 11 minutes, i.e.
roughly **2.5× slower**, and that is a permanent per-cycle tax, not a one-off. The fix is a
persistent checkout directory refreshed in place (`git --work-tree=… checkout -f` + `git clean
-xdf` with `__pycache__` preserved, or a real `git worktree`), so bytecode survives between cycles.
**Exit criterion: the clean-subject gate runs within 1.3× the in-tree baseline.**

**2. Right-size `GATE_SUITE_TIMEOUT_SECONDS` against the NEW baseline.** It is currently 1800s,
justified as ~3× the *in-tree* 613s. If the cold-checkout runtime is ~27 min, 1800s is a
coin-flip, and this gate now fail-CLOSES on timeout — so an undersized bound wedges publishing,
which is exactly the defect closed this morning in the other direction. Re-measure after (1), then
set the bound to ≥2× the measured runtime and update
`test_the_gate_timeout_exceeds_the_suites_own_runtime`'s constant with it.

**3. Lifecycle under crash.** `mkdtemp` + `shutil.rmtree` in a `finally` leaks a 130MB directory
if the process is SIGKILLed (the OOM path is real here — `rc=-9` is a known gate outcome). Add a
startup sweep of stale `publish-gate-head-*` dirs, or move to `git worktree` with `prune`.

**4. R15 both ways, as its own test module** (`test_publish_gate_subject_is_head.py`):
   * the gate runs with `cwd` == the checkout, never `PROJECT_DIR` — *mutation: point it back at
     the tree and the test reds* (partially covered today in `test_publish_gate_scope.py`);
   * a **dirty working tree does not change the verdict** — write a syntax error into a tracked
     source file, assert the gate still passes. This is THE property the ruling bought and nothing
     asserts it yet;
   * an unavailable checkout **blocks** — *mutation: return `(True, …)` and it reds*;
   * the checkout dir is **removed** after a run, including on a raising run.

**5. Decide the `LAST_TESTED_HASH_FILE` contract explicitly.** It is keyed on `git_hash`, which
was only loosely meaningful when the subject was the tree. Now it is exactly right — but the
supervisor's RUNG-1 wedge draw uses it as its INDEPENDENCE cross-check, so the semantics should be
stated in one place rather than inferred from two call sites.

## Why it is worth an atom rather than a follow-up commit

The minimal version changes what the machine *means* by "the code passed": from "the tree happened
to pass while N lanes were mid-edit" to "committed truth passes". That is a governance-grade
change to the publish path, and its remaining risks are all in the LIFECYCLE (cost, timeout,
cleanup) rather than the semantics. Those are exactly the accretion-shaped risks
`OPERATIONAL_LAYER_DESIGN` says to design once rather than patch on symptom.

## Related

* `DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09.md` — the ruling.
* `background/tree_divergence.py` — the paired measure ("squatting gets named daily"), landed with
  the minimal version.
* `WORKER_FINDING_KNIFE2_IS_ORPHANED_19_FILES_IN_NO_COMMIT_2026-08-09.md` — the episode that
  forced the ruling.

— Planner mint, 2026-08-09, from the director's own ruling text.
