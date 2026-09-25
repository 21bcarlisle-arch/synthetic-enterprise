**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# `NAMES_ONLY_A_SCOPE` is two shapes, and the repair the census prints is unanswerable for half of them — a controls-only repoint tells four rows "no named file exists" while a named file is on disk and passing

Answers `docs/staging/records/SEAT_PREREG_HOW_MANY_OF_THE_EIGHT_NAMES_ONLY_A_SCOPE_ROWS_A_REPOINT_CAN_ACTUALLY_MAKE_GRADABLE_2026-09-25.md`.
Successor to `f0470836e`, which split `CONTROL_NEVER_WRITTEN` and reached `NAMES_ONLY_A_SCOPE`
through a second branch. This is the same defect one level down, in the branch that commit added.

**DISCHARGED 2026-09-25.** The guard was narrowed to ask whether ANY named file is on disk
(`61fc300a7`), together with the adjacent `NOTHING_IN_THE_ROW` claim this file said had to be fixed
in the same pass -- an eighth cause, `SUBJECT_NEVER_WRITTEN`, now stands where the false sentence
was reachable. Measured over the live map in one process against `HEAD`: **zero rows change**, so
the latency claim below held exactly. Two of the four rows were then repointed at artefacts their
own design docs declare and delisted from `LEGACY_UNGRADABLE_BUILD_ROWS` (`0fe3d492b`); `H40` and
`H48` were REFUSED a repoint in writing, because their deliverable is a record and no filename
exists to name without inventing one. That refusal is its own finding, filed the same day.

## The finding

`ungradable_causes` reaches `NAMES_ONLY_A_SCOPE` through two branches, and they describe two
genuinely different rows that get ONE cause name and ONE repair instruction:

* **`elif not controls:` with a control-scope directory** — the row names subject modules AND a
  directory where controls live. It is one level short of the file, and *"name the FILES this atom
  writes, not the directory they live in"* is exactly the right instruction. Four rows:
  `W2_non_dd_miss_vocabulary`, `OPS6_scoped_publish_path_suite`, `W2_18`, `W2_19`.
* **`if not files:` — EVERY entry a directory** — the row names no subject module either. There is
  nothing to repoint *at*, and the repair instruction cannot be followed without inventing a
  filename. Four rows: `G4_unified_failure_register`, `SP2_2_rng_substream_primitive`,
  `H40_full_suite_pollution_bisect`, `H48_the_parked_document_audit_is_the_idle_hole_at_scale`.

Measured, not reasoned: of the eight, exactly the four in the first shape have a subject module in
`file_scope`, and every one of those modules already has a `test_<stem>.py` on disk. The other four
have no `.py` entry at all, so no control can be derived from what the row says.

## And following the printed repair on the second shape makes the verdict WORSE, on a false claim

Run against the real `G4` row with one control appended:

```
as it stands                   : NAMES_ONLY_A_SCOPE
+ a control that does NOT exist: HONESTLY_UNBUILT -- "no named file exists, so the row is RIGHT to read zero"
+ a control that DOES exist    : HONESTLY_UNBUILT -- "no named file exists, so the row is RIGHT to read zero"
```

**The second line is the defect.** `subject_on_disk` is computed as `files not in controls`, so a
row whose only non-directory entries are controls has an empty subject list however many of those
controls are sitting on disk and passing. The row is then told it is honestly unbuilt and *right* to
read zero — the one verdict in the partition that means "this was never a defect" — on the strength
of a sentence the tree contradicts. A row silenced that way leaves the 26-owe-a-repair count by
getting vaguer, not by getting better.

This is why four of the eight were NOT repointed on 2026-09-25 when the other four were. The item's instruction was
followed where it is answerable and refused where following it would have manufactured that
silence.

## It is LATENT, not live, and that is measured

Both live `HONESTLY_UNBUILT` rows are legitimate: `G14_half_hourly_grid_carbon_intensity_aligned_to_settlement`
names `tools/fetch_grid_carbon_intensity.py` and `G15_forward_curve_series_to_backtest_hedging_by_physics`
names `simulation/forward_curve.py`, and neither file is on disk. Nothing in the live map reaches the
false branch today. **The only route into it is the repoint this very work item prescribes**, which
is the reason to write it down now rather than after a future turn takes the instruction at its word.

## The fix, for whoever takes it

The guard must ask whether ANY named file is on disk, not whether any named *subject* is:
`HONESTLY_UNBUILT` may only be claimed when nothing the row names exists. A row naming an existing
control is not unbuilt — it has a runnable control, and belongs in the legs below. Note before
starting that the adjacent claim has the same shape: `NOTHING_IN_THE_ROW` says *"every named path is
on disk"* and is reachable with an absent subject, so the two want fixing together or the false
sentence moves rather than goes.

A control for it must fail on the row-with-an-existing-control case specifically — the mutation that
matters is not "does `HONESTLY_UNBUILT` still fire for `G14`" (it will, and that is the flattering
reading) but "does it refuse to fire when a named control is on disk".

## What else this turn established, recorded here because it is a separate subject

`OPS6_scoped_publish_path_suite` sits at `level_current: 0` / `loop_stage: build` and its own
program — `background/publish_scope.py`, 22KB, landed 2026-09-01 — was in NO atom's `file_scope`,
nor was its R15 suite `tests/background/test_publish_scope.py`. The `file_scope` floor
(`check_file_scope_names_the_atoms_own_program`) could not see it: that leg only catches program text
whose NAME carries the atom id, and this module is named after its subject. The row has been
repointed at both. Whether OPS6's level is now wrong is a level question and is not decided here.

Running OPS6's named set surfaces one red at HEAD that the register does not know about:
`tests/background/test_publish_scope.py::test_a_root_unavailable_scope_stops_the_gate_instead_of_running_it`
fails with *"gate ran on a dead root"* (131 passed, 1 failed, 107s). The node is absent from
`docs/observability/.head_red_observed.json` entirely — the store holds five `test_publish_scope`
nodes, all `currently_red: false`, from a run stamped 2026-09-23. So the register reports OPS6's set
as clean and the set is not. That is another instance of
`SEAT_FINDING_A_GENUINELY_RED_ARCHITECTURE_TEST_IS_ABSENT_FROM_THE_REGISTER_THAT_NOW_GRADES_THE_MAP_2026-09-25.md`
and belongs to that class, not to a new one. It does not change OPS6's verdict: with or without the
register the row is graded and consistent, because CONTRADICTED needs the whole set to pass.
