# FINDING — seven tests are red at HEAD and no routine gate is shaped to see them

**Severity:** BLOCKING · **Lane:** H_harness

**Date:** 2026-08-12 · **Atom:** `OPS4_surgical_landing` / gate scope · **Class:** control blind spot
**Status:** ALL SEVEN REPAIRED 2026-08-12. **One claim below was wrong** — see the correction.
The gate blind spot itself is now covered by `tools/head_green_census.py` + a nightly timer.

## Observed, with evidence

A full unscoped run of the publish-gate marker expression (24,204 passed, 1,472s) reported
**8 failed**. Re-run at HEAD, seven still fail; all seven also fail at `82dd451c1`, i.e. they
**predate** this morning's churn cut (`048bc10f8`) and seat-guard fix (`9f82ce897`). Verified in
a detached worktree at that commit, not inferred from ordering:

```
7 failed, 147 passed in 8.46s     (worktree at 82dd451c1)
```

The seven:

1. `test_aged_staging_digest.py::test_the_four_documents_that_motivated_clause_5_are_flagged_aged`
   — filed separately as `WORKER_FINDING_A_BULK_PASS_BLINDS_THE_AGED_STAGING_DIGEST_2026-08-12`.
2. `test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned`
   — `undispositioned self-clearing-alarm hits: .lock`.
3. `test_simplifications_store.py::test_counts_match_file_contents`
   — `D36_bill_render_footing_and_pence` and `SITE2_two_sided_wall_exhibit` both have
   `map simplifications_count=None != store file count=1`. Record/code divergence: two atoms
   landed (`7a199defe`, `09f65f694`) without their map counts moving.
4. `test_measure_publish_gate_subject_cost.py::test_the_kernel_applied_both_limits_not_just_this_repo_writing_them_down`
5. `test_measure_publish_gate_subject_cost.py::test_the_sampler_reads_this_scopes_own_high_water_mark_from_the_kernel`
6. `test_measure_publish_gate_subject_cost.py::test_a_killed_phases_peak_is_its_ceiling_and_is_labelled_a_lower_bound`
   — (4–6) `peak_mb` is `None`; the scope peak sampler reads nothing back from the kernel.
7. `test_pre_commit_test_gate.py::test_every_hook_gate_that_spawns_pytest_scrubs_GIT_star__class_guard`

## Number 7 is not merely red, it is a live hazard

Its own message states the mechanism:

> `orphan_ratchet.py` spawns a pytest subprocess but does NOT scrub `GIT_*` from its env — this
> is the exact H24 corruption class (a git-touching test inherits the commit's
> `GIT_INDEX_FILE`/`GIT_DIR` and writes the SHARED `.git`).

That matters more than a normal red because `tools/surgical_land` is now the ONLY sanctioned
landing path, and it runs the gate with a constructed index. A gate-spawned pytest that inherits
`GIT_INDEX_FILE` and writes the shared `.git` is a corruption route through the one mechanism
every lane is required to use. Not observed firing; the guard that would catch it firing is
itself the test that is red.

## Why no routine gate sees any of this

Three controls run routinely and none has the shape to catch these:

- **`pre_commit_test_gate` / `surgical_land`** select tests by NAME STEM from the changed paths.
  A change to `background/finding_severity.py` selects `tests/**/test_finding_severity*`; it
  cannot reach a census in `tests/design/` or a guard in `tests/tools/`. This is the same
  reach-by-reference gap already filed in
  `WORKER_FINDING_A_FINISHED_CUT_SAT_UNCOMMITTED_WITH_EVERY_CONTROL_GREEN_2026-08-12`.
- **The operational-layer check** runs `-m "operational or join_report_only or scale_report_only"`
  — the complement of the set these live in.
- **`process_run_complete`'s publish gate** carries `-x`, so it stops at the first failure and
  reports one name. Observed today: a run that stopped at an unrelated seat-guard failure left
  1,121 tests unrun and said nothing about the other six.

So "HEAD is green" has never been measured. What is measured is "the tests name-adjacent to the
last diff are green", which is a much weaker claim wearing the same words.

## Recommended remedy — NOT applied

Two separable pieces, in priority order:

1. **Run the full unscoped marker expression on a cadence** (nightly is enough at ~25 min) and
   alarm on the DELTA, not the absolute count — a standing red set that nobody has dispositioned
   becomes wallpaper otherwise. Carry the failure names in the alert per R5.
2. **Drop `-x` from that cadence run.** Fail-fast is right for a commit gate and wrong for a
   health measurement; today it turned six findings into one.

Do not remedy by widening the per-commit gate to the full suite — a 25-minute commit gate will
be bypassed, and hook-bypass is a wall. The commit gate being scoped is a legitimate design; the
defect is that nothing else is unscoped.

Queued per self-interrupt discipline. Item 7 arguably deserves promotion out of this list on its
own, since it names a corruption route through the sanctioned landing path.


---

## CORRECTION (2026-08-12, same day) — item 7 was NOT a live hazard

The section above calls item 7 *"a live hazard"* and *"a corruption route through the one
mechanism every lane is required to use"*. **That is wrong, and it was wrong when written.** I
took the assertion message at face value instead of reading the file it accused.

`tools/orphan_ratchet.py` does not spawn pytest. Its only occurrence of the token is
`_RUNNERS = frozenset({"uvicorn", ..., "pytest"})` at line 90 — a data literal of runner names
it looks for when deciding whether a module has a caller. The one subprocess it spawns is a
read-only `git ls-files`, which the guard's own docstring says is correctly out of scope.

The defect was in the **guard**: its detector was `'"pytest"' in src`, a substring match over
the whole file, which cannot tell a data literal from an argv. **There was no corruption route.**
Replaced with a structural AST detector (`bbe45c1ac`), R15-proven both ways with this false
positive pinned as a named case.

**Why this correction matters more than the fix:** a control that fires on mentions rather than
uses had been telling everyone to repair a file that was never broken, and I amplified it into a
security-shaped claim about the landing path. A red test's message is a hypothesis, not evidence.

## Disposition of all seven

| # | Test | Outcome |
|---|---|---|
| 1 | `test_the_four_documents_that_motivated_clause_5_are_flagged_aged` | fixed `2318b4b84` — clock now `--diff-filter=A` |
| 2 | `test_every_live_hit_is_dispositioned` | fixed `54b8579dd` — `.lock` dispositioned benign (a mutex, no episode field) |
| 3 | `test_counts_match_file_contents` | fixed `3ea01a213` — two atoms' `simplifications_count` added |
| 4–6 | `test_measure_publish_gate_subject_cost` (×3) | fixed `ae8cf2807` — user D-Bus located; no product defect existed |
| 7 | `test_every_hook_gate_that_spawns_pytest_scrubs_GIT_star__class_guard` | fixed `bbe45c1ac` — detector read mentions, not uses |

An **eighth** red appeared mid-repair (`test_the_live_store_has_roll_headroom`, another lane's
commit at 10:48 pushed a store file past the watermark). Instance cleared in `3ea01a213`; the
class remains open under `WORKER_FINDING_A_ROLL_INSIDE_THE_SOLE_WRITE_PATH_DID_NOT_FIRE`, now on
its **second manual drain in twelve hours**.

## The blind spot itself is now covered

`tools/head_green_census.py` runs the publish gate's own marker expression **unscoped and
without `-x`**, nightly via `head-green-census.timer`, and alarms on the **delta** against a
committed baseline rather than the absolute count. It cannot pass on a run that selected
nothing, and it cannot write its own baseline — both pinned by mutation tests.
