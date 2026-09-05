# [WORKER-FINDING] The publish gate grades a tree other lanes are writing, so each wedge cycle reds on a different test and the episode can never converge (2026-08-30)

**Severity:** BLOCKING (this is the live wedge) · **Lane:** H_harness

**Found:** 2026-08-30, RUNG-1 scheduled tick drawn to "FIX the red test" of a 489-minute
publish-gate wedge. There was no red test. Found by refusing the draw's premise and reading the
seven failures side by side instead of the last one alone.
**Disposition:** DIAGNOSED AND ACTIONED — born archived, existing class `publish_gate_and_wedge`.
**Class:** `publish_gate_and_wedge` (18th ruling). Not a new class.

## The draw's premise was false

The doorbell said the gate "has been FAILING for ~489 min (3 failures in-window, no pass at HEAD
3e90ae5e1)" and instructed: *diagnose the failing test, fix the red test*. It also warned the
depth was unknown and the named test "may be one red of several".

It was none of several. Read as a series rather than an instance, the seven failures of this
episode accuse a **different** subject almost every cycle:

| Cycle (UTC) | What was blamed |
|---|---|
| 04:31 | `site/test_expert_doors_mobile.py::test_tables_scroll_inside_their_own_container[capabilities]` |
| 06:03 | the same site test again |
| 07:37 | `site/test_the_site_lane_runs_no_untracked_control.py::test_no_control_the_site_lane_executes_is_missing_from_the_repository` |
| 09:09 | refused with **no FAILED/ERROR summary at all** |
| 10:43 | refused with **no summary at all** |
| 12:08 | `test_regression`, rc=1 |
| 12:30 | `test_regression`, rc=1 — three lines under *"Tests skipped — already passed for git=09b90343d"* |
| 12:57 | **4** reds in `tests/background/test_process_run_complete.py` |

Six different accusations across seven failures is not a regression. A regression is stable: it
names the same test until someone fixes it. This names whatever happened to be half-written when
the suite walked past.

Note the 12:30 row against the standing lesson *"any publish path that fails without running the
suite is filed as `test_regression` by default"*: `blocking_tests: []`, `total_red: 0`, and
"Tests skipped" directly above the failure. That is the fourth clock of that class, and it is
already repaired in the working tree (below) — by a lane that could not land the repair, because
of this finding.

## Pinned to the second

The 12:57 cycle is the one that leaves proof rather than inference.

- The gate's selected suite ran **12:51 → 12:57** (`4 failed, 456 passed, 1 skipped in 393.07s`).
- `background/process_run_complete.py` mtime: **2026-08-30 12:54:21.980852838 +0000**.

The file was rewritten by another lane **dead centre of the window that was grading it**.

The failure text is not merely consistent with that — it is *only* possible under it:

```
E       assert 'GIT_COMMIT_HOOK_TIMEOUT_SECONDS' in '\n\nCOMMIT_HOOK_DURATION_PATH = (\n    PROJECT_DIR / "docs" / "observability" / "commit_hook_duration.jsonl")\n'
```

```
E        +    where <built-in method count of str object ...> = '            "from the commit that would follow, is the cause. Refusing this cycle so the "\n'.count
```

```
E         File "<unknown>", line 1
E           _prov.read(prov_path), repo_root=PROJECT_DIR)
E                                                       ^
E       SyntaxError: unmatched ')'
```

`inspect.getsource(f)` returned, for one function, the *constant block above it*; for another, a
**single fragment of a string literal belonging to a different function**; and `ast.parse` was
handed a slice with an unbalanced paren. **No self-consistent Python file can produce any of
those.** `getsource` binds `co_firstlineno` from the code object at import and reads the file text
at call time. The test module does `import background.process_run_complete as prc` at **line 17 —
module level**, so the binding happens at *collection*, t≈0 of a 393-second run, while the
assertions fire ~6 minutes later. Rewrite the file in between and every source-introspection
assertion in the file reads new text at old line numbers.

## The counter-check

All four "red" tests pass in the tree, and so does everything around them:

```
$ python3 -m pytest tests/background/test_process_run_complete.py -q -p no:randomly
82 passed in 63.57s
```

Nothing was fixed between the failure and that run. The tests were never red.

## The mechanism, stated as a property

**A gate whose suite takes longer than the shared tree's inter-write interval cannot converge**,
because the artefact it grades does not exist as a single version for the duration of the grading.
The gate is not measuring the tree; it is measuring a smear of it.

Two things make it worse here and both are specific:

1. **Source-introspection tests re-read their subject mid-run.** A test asserting on
   `inspect.getsource(...)` has a *second*, later read of the file that ordinary tests do not.
   It is the most sensitive detector of tree churn in the repo, which is why this class surfaces
   there first and why the resulting message is incoherent rather than a clean assertion.
2. **The incoherence is misfiled as a regression.** `rc=1` reaches `_classify_gate_failure` as
   `test_regression`, which is the label that sends the RUNG-1 draw hunting a test at HEAD. Two
   of this episode's seven failures were that, and this draw was the third — sent, with the
   authority of a PRIORITY-ZERO wedge, after a test that did not exist.

## Prediction, filed before the confirming run

Written before the in-flight gate (PID 2202633) returned: **it will not reproduce the four
`test_process_run_complete` reds.** If it reds at all it will red somewhere unrelated, on whatever
was being written during *its* window. A gate that reds on a stable subject would refute this
finding outright.

## What was done about it

The 92 uncommitted lines sitting in `background/process_run_complete.py` are a completed,
green repair for the `EXIT_TREE_LOCK_UNAVAILABLE` misclassification — the very defect that
mislabels contention as `test_regression`. It was stranded uncommitted, and while stranded it was
itself the churn reddening the gate. Landing it both removes a churn source and closes the
mislabelling. That is the action taken; see the commit that cites this document.

## What is NOT claimed

This does not claim the site-lane reds at 04:31/06:03/07:37 were also races — they named a stable
subject twice, so at least the first may be a genuine red that a later cycle stopped reaching once
fail-fast moved on. **I cannot yet say**, and the honest position is that the episode contains at
least one race and possibly one real red underneath it. The report-only census the doorbell asked
for is the way to settle that, and it must be run when the tree is quiet or it will measure the
same smear.

---

## Addendum, 2026-09-05: the stable variant, and why this document was invisible for six days

Added by the autonomous worker, closing the two surviving reds of a 725-minute wedge
(`b476a4de0`). I filed a fresh finding for what I had measured, then found this one and deleted
mine. **The class is the same; what follows is only what this document did not already contain.**

### 1. This document was untracked for six days and unlisted in its own register

It was "born archived" — written straight into `docs/staging/done/`, which skips the
root→`--render`→`mv` flow that puts a finding into `CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`.
So it is archived, uncommitted, and absent from the register that claims to supersede it, and
`finding_classes --check` passes: the check reads the staging ROOT, so a document in `done/` that
nothing lists is outside its subject **by construction**. Six days and one repeat diagnosis is
what that cost. It is committed with this addendum, which is the actual fix for that part.

### 2. The variant: a red that is stable, reproducible, and still not at the stamped hash

The 2026-08-30 measurement is a *race within one run* — the file rewritten mid-grade, producing
incoherent `getsource` output that could come from no self-consistent file. Today's is the
quiet twin, and it does not announce itself at all:

- Gate record: 4 blocking tests, census `complete`, `git_hash: 1cfc48c01` on all 3 failures.
- At HEAD `5c7b1d78f`, 16 commits later: **2 of the 4 had already been repaired** by intervening
  commits. Nobody had re-checked, so the draw sent me after two tests that were green.
- With the other 2 repaired, the shared tree was **still 5 red** — 3 in
  `test_a_standing_red_becomes_work_instead_of_a_retry.py`, 2 in `test_static_quality_ratchet.py`.
- Attribution, in a clean `HEAD` worktree: **13 passed / 213 passed**. At `HEAD` + my hunks only:
  green. In the shared tree: 5 failed.
- Cause: a lane live at that moment (`process_run_complete.py` mtime 10 minutes earlier, seat
  heartbeat current) had **uncommitted** edits deleting `_record_commit_hook_pass` and dropping
  the I001 census 1328 → 1327.

These reds are **stable** — they reproduce every run, they name the same tests, they read exactly
like a regression. Nothing about them looks like a race. They are simply not in any commit, and
the record stamps them with a hash at which they do not exist.

So the class has two members with opposite symptoms and one cause: **the gate runs pytest against
the working tree and stamps `git_hash`, and those are two different subjects.** A failure has
three renderings the record cannot tell apart — genuinely at the stamped commit; at it and since
repaired (2 of 4 today); or in no commit at all (5 of 5 today).

The second reading is the dangerous one, and it is new here. The draw's instruction is "fix the
red test". Under case 3 that means **reverting a live lane's uncommitted work**, which is the
worst move available, and this document is the only thing standing between the next tick and it.

### 3. The repair this argues for, which the 2026-08-30 entry did not propose

That entry landed the churn source and stopped there — correct, and it does not generalise,
because the next lane to hold a file dirty re-creates it. One leg, not a register: when the gate
records a failure, ask whether the tree it graded is the tree the hash names.

```
dirty = subprocess.run(["git", "status", "--porcelain"], …).stdout.strip()
```

Write the answer into `.publish_gate_state.json` as its own field — `graded_tree: "clean at
<hash>"` or `graded_tree: "DIRTY: <n> path(s) differ from <hash>"`, naming the paths that
intersect the failing tests' own modules. Keyed to the property (does the graded tree equal the
stamped tree), not to today's answer.

It must **not** become "refuse to run on a dirty tree". This tree is dirty by design — several
lanes and daemons write it at once — and a gate that only ran on a clean tree would never run.

**Not built in this tick, and the reason is this finding's own subject:**
`background/process_run_complete.py` is the file the live lane is rewriting right now. Building
into it would either be clobbered or would carry their half-finished rewrite into my commit. It
is the next tick's work, once that lane lands.

### 4. What this addendum does not claim

It does not claim the 5 remaining reds are the *whole* of what is left of the wedge. The scoped
gate was not run to green in this tick, because the tree it would grade is the smear this
document is about. **I cannot yet say** whether anything else is red underneath them, and the
honest reading is that publishing stays wedged until the live lane lands, at which point the
question can be asked of a tree that holds still.
