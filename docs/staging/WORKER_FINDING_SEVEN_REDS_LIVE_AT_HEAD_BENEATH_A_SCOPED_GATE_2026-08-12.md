# FINDING — seven tests are red at HEAD and no routine gate is shaped to see them

**Severity:** BLOCKING · **Lane:** H_harness

**Date:** 2026-08-12 · **Atom:** `OPS4_surgical_landing` / gate scope · **Class:** control blind spot
**Status:** NOT repaired. Filed for disposition. The seven are enumerated so the next tick starts from a list, not a sweep.

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
