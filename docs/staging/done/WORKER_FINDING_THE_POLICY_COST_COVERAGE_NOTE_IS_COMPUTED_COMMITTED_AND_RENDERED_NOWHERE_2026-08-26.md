**Severity:** LATENT · **Lane:** H_harness · **Disposition:** QUEUED (not fixed on sight)

# WORKER FINDING — the policy-cost coverage note is computed, committed, and rendered nowhere; the test that would say so is untracked and red

**Rank: backlog** (P-1: declare the intended rank on arrival). Not blocking any lane today.
**Found:** 2026-08-26, incidentally, while landing the value-cycle segment fix (`fef45d833`).
**Not fixed on sight** — SELF-INTERRUPT DISCIPLINE: the supply of harness findings is infinite,
so this is queued as an atom rather than repaired mid-draw.

## Observed, with evidence

`simulation/run_phase4c_on_phase2b.py:480-486` computes `policy_cost_coverage` and puts it in
the run output. Both that file and `saas/reporting/annual_report.py` are committed and clean
(`git status --porcelain` on both: empty).

Nothing reads it. `grep -rn "policy_cost_coverage"` over the tree returns the producer, a
docstring cross-reference in `tests/simulation/test_policy_cost_values_vs_source.py:14`, and
the untracked test file below. There is no `run_output.get("policy_cost_coverage")` anywhere in
the renderer.

`tests/simulation/test_policy_cost_coverage.py` is **untracked** and **red — 6 of its tests
fail**, including `test_the_note_reaches_the_published_report`, whose assertion message is
exactly the defect: *"the coverage block is no longer carried through from the run output, so
the report has nothing to render and the disclosure silently disappears."*

```
FAILED test_the_2025_clamp_the_finding_measured
FAILED test_coverage_is_derived_from_the_tables_not_declared_beside_them
FAILED test_the_note_reaches_the_published_report
FAILED test_the_note_is_derived_from_the_tables_not_narrated
FAILED test_the_note_is_silent_when_there_is_nothing_to_say
FAILED test_the_renderer_cannot_reach_across_the_wall_to_compute_this
```

## Why it matters

Two separate defects, and the second is the worse one.

**R11, a release whose effect is nothing.** The producer half of
`WORKER_FINDING_THE_COST_STACK_CLAMPS_SILENTLY_INSIDE_ITS_OWN_RUN_WINDOW` (2026-08-14) landed;
the rendering half did not. All 13 year-keyed policy/network tables end at 2024, the run bills
to 2025-06-07, and per that finding £391,531.72 — 8.09% of the published stack — is priced on
at least one clamped table. The disclosure that would say so is computed every run and reaches
no reader. Clamping is a defensible modelling choice; clamping silently is the fail-open shape
R15 names, and the instrument built to stop it is currently inert.

**A red test file loose in a shared tree is a trap for the next lane.** It is untracked, so it
does not red the gate today — but this tree has concurrent writers, and a broad `git add`
lands it and wedges publishing for everyone. That is the same class as the five
`..._LEFT_UNCOMMITTED_BY_A_...` alarms already in staging. It should be either finished or
deliberately parked, not left as an unexploded pathspec.

## What done looks like

Render the coverage note in `saas/reporting/annual_report.py` from `run_output`, **derived not
narrated** — two of the red tests exist specifically to refuse a hand-written note and a
renderer that recomputes coverage across the wall instead of reading what the run reported.
Then commit the test file with it, so the control and its subject land together.

Cheaper interim if that is not drawn soon: commit the test file `@pytest.mark.xfail(strict=True)`
with this finding cited, which removes the trap and keeps the defect visible and self-clearing.
Do not simply delete it — it is a correct control whose subject is missing.

## Not verified

Whether the renderer *ever* carried this block (the assertion says "no longer", implying a
regression, but I did not walk the history to confirm that). Labelled `inferred` per R9.
