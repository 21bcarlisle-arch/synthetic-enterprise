# [CLASS] The publish gate and the wedge: the control that stops publishing, and what it stops on

**Severity:** LATENT · **Lane:** H_harness

**Instances:** 30 · **Class:** `publish_gate_and_wedge` · **Ruling's own count:** ~18 (`DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12`, clause 1, "publish-gate/wedge")

This document supersedes the individual findings listed below, which are **archived, not deleted**, in `docs/staging/done/`. Membership is DERIVED, never hand-kept: `python3 -m background.finding_classes --check` re-derives it from the filesystem and fails if a live finding belongs to this class and is not listed here, if a listed instance is missing from the archive or has come back to the root, or if the count above stops equalling the length of the list below.

## The 30 instances

- `WORKER_FINDING_AN_OOM_KILL_IS_RECORDED_AS_A_TEST_REGRESSION_2026-08-10.md` — LATENT
- `WORKER_FINDING_A_BRANCHS_GATE_AUDITED_THE_NEIGHBOURING_BRANCHS_PROMISE_2026-08-12.md` — RECORDED
- `WORKER_FINDING_A_DUPLICATE_MARKER_DISARMS_THE_WEDGE_ALARM_2026-08-10.md` — RECORDED
- `WORKER_FINDING_A_FINDING_RECORDED_ITS_OWN_INSTANCE_AS_FIXED_AND_THE_FIX_HAD_NEVER_BEEN_COMMITTED_2026-08-14.md` — RECORDED
- `WORKER_FINDING_A_MUTATION_TEST_RAN_THE_OPERATIONAL_SUITE_INSIDE_THE_PUBLISH_GATE_2026-08-12.md` — LATENT
- `WORKER_FINDING_A_NEW_REFUSAL_MADE_A_SIBLING_FIXTURE_UNREACHABLE_BY_DESIGN_2026-08-12.md` — LATENT
- `WORKER_FINDING_A_RED_AT_HEAD_IS_INVISIBLE_TO_EVERY_COMMIT_THAT_DOES_NOT_SELECT_ITS_FILE_2026-08-15.md` — LATENT
- `WORKER_FINDING_A_REPAIR_DOWNSTREAM_OF_ITS_OWN_GATE_CANNOT_LAND_2026-08-10.md` — RECORDED
- `WORKER_FINDING_DERIVED_ARTEFACT_STALENESS_IS_A_WEDGE_CLASS_2026-08-09.md` — LATENT
- `WORKER_FINDING_EPISODE_MEMORY_WIPED_MID_EPISODE_2026-08-09.md` — LATENT
- `WORKER_FINDING_SECOND_WEDGE_CAUSE_LANDED_AFTER_THE_FIRST_2026-08-09.md` — LATENT
- `WORKER_FINDING_SEVEN_REDS_LIVE_AT_HEAD_BENEATH_A_SCOPED_GATE_2026-08-12.md` — RECORDED
- `WORKER_FINDING_THE_DURATION_SERIES_RECORDS_ABORTED_RUNS_2026-08-10.md` — LATENT
- `WORKER_FINDING_THE_ELEVENTH_WEDGE_WAS_A_STACK_NOT_A_BUG_2026-08-10.md` — LATENT
- `WORKER_FINDING_THE_EPISODE_CLOSES_ON_AN_EMPTY_QUEUE_THAT_CANNOT_EMPTY_2026-08-12.md` — LATENT
- `WORKER_FINDING_THE_GATES_SCRATCH_SPACE_IS_RAM_AND_NOTHING_DRAINS_IT_2026-08-12.md` — LATENT
- `WORKER_FINDING_THE_GATE_SELECTS_BY_FILENAME_STEM_SO_A_RENAMED_KEYS_CONSUMERS_NEVER_RUN_2026-08-17.md` — LATENT
- `WORKER_FINDING_THE_GATE_WAS_THE_BRANCHS_OWN_ADMISSION_TICKET_2026-08-12.md` — RECORDED
- `WORKER_FINDING_THE_GHOST_PUSHER_GUARD_FIRES_ON_A_CONCURRENT_WRITER_2026-08-09.md` — LATENT
- `WORKER_FINDING_THE_LANDING_TOOL_EXTRACTS_INTO_THE_TMPFS_THE_GATE_WAS_MOVED_OFF_2026-08-14.md` — RECORDED
- `WORKER_FINDING_THE_NAMED_BLOCKING_TEST_PASSES_WHEN_YOU_RUN_IT_2026-08-10.md` — LATENT
- `WORKER_FINDING_THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE_2026-08-09.md` — RECORDED
- `WORKER_FINDING_THE_TMPFS_DRAIN_WAS_POINTED_AT_THE_WRONG_FILESYSTEM_2026-08-12.md` — LATENT
- `WORKER_FINDING_THE_WEDGE_ALARM_NAMED_TESTS_THE_GATE_NEVER_RAN_2026-08-12.md` — LATENT
- `WORKER_FINDING_THE_WEDGE_CLEARS_ON_PROCESS_EXIT_NOT_ON_THE_RECORDED_PASS_2026-08-12.md` — LATENT
- `WORKER_FINDING_THE_WEDGE_DETECTOR_FED_ITSELF_2026-08-12.md` — RECORDED
- `WORKER_FINDING_THE_WEDGE_DRAW_NEVER_READS_THE_COMMIT_ITS_OWN_FAILURE_RECORDS_NAME_2026-08-17.md` — RECORDED
- `WORKER_FINDING_THE_WEDGE_RECORD_CITED_A_TEST_THAT_NO_LONGER_EXISTS_2026-08-12.md` — LATENT
- `WORKER_FINDING_THE_WEDGE_WAS_FIVE_INSTANCES_OF_ONE_CLASS_AND_pytest_x_SERVED_THEM_ONE_AT_A_TIME_2026-08-14.md` — RECORDED
- `WORKER_REPORT_THE_GATES_OWN_TESTS_WERE_WRITING_THE_ALARMS_EVIDENCE_2026-08-10.md` — LATENT

## Cumulative cost, measured from the instances' own recorded evidence

**152.0 recorded episode-hours** across 9 of the 30 instances; largest single recorded episode **60h**; 2 instance(s) name a published figure in scope.

**The definition, because a bare sum here would be the very defect this class catalogues.** Each instance contributes the LARGEST duration it records with evidence — one figure per document, so a finding that states the same episode twice is not billed twice. The sum is then over DOCUMENTS, not over distinct outages: two findings describing the same wedge from different angles each contribute, so this is *recorded episode-hours*, not a claim that this many distinct hours were lost. An instance that never measured its own damage contributes zero, which makes the figure a floor on attention spent and never an estimate. Every line below is traceable to the document and the sentence it came from — a cost that cannot be traced is the mirror class this consolidation itself lists.

- **60 hours** — `WORKER_FINDING_A_NEW_REFUSAL_MADE_A_SIBLING_FIXTURE_UNREACHABLE_BY_DESIGN_2026-08-12.md`: …ixture unreachable-by-design, and that fixture wedged publishing for ~60h **Severity:** LATENT · **Lane:** H_harness **Date:** 2026-08-12 **S…
- **31 hours** — `WORKER_FINDING_A_DUPLICATE_MARKER_DISARMS_THE_WEDGE_ALARM_2026-08-10.md`: …alarm was disarmed 188 times today while publishing stayed wedged for 31 hours (2026-08-10) **Severity:** BLOCKING · **Lane:** H_harness **Dischar…
- **23 hours** — `WORKER_FINDING_THE_NAMED_BLOCKING_TEST_PASSES_WHEN_YOU_RUN_IT_2026-08-10.md`: …What happened `.publish_gate_state.json` had wedged publishing for ~23h with one entry: The obvious first move — run the named test — repo…
- **13 hours** — `WORKER_FINDING_THE_ELEVENTH_WEDGE_WAS_A_STACK_NOT_A_BUG_2026-08-10.md`: …data.py` carried uncommitted hydration. So the gate had been red for 13h on work that was **finished and sitting on the disk it was failing ag…
- **10 hours** — `WORKER_FINDING_THE_GHOST_PUSHER_GUARD_FIRES_ON_A_CONCURRENT_WRITER_2026-08-09.md`: …) **Severity:** LATENT · **Lane:** H_harness **Found during:** the ~10h publish-wedge unwedge, while running the gate's own argv without `-x`…
- **7 hours** — `WORKER_FINDING_SECOND_WEDGE_CAUSE_LANDED_AFTER_THE_FIRST_2026-08-09.md`: …he episode* (23:17 UTC). So: * it is **not** a cause of the observed 7-hour episode (inferred-free: the timestamps do not overlap), and * it **…
- **3 hours** — `WORKER_FINDING_THE_GATES_SCRATCH_SPACE_IS_RAM_AND_NOTHING_DRAINS_IT_2026-08-12.md`: …separately and is why the exhaustion loop still > closes: the drain's 3h age bound is longer than the ~80-minute fill, so restored reach > rec…
- **3 hours** — `WORKER_FINDING_THE_TMPFS_DRAIN_WAS_POINTED_AT_THE_WRONG_FILESYSTEM_2026-08-12.md`: …**0** were older than the sweep's `STALE_HEAD_CHECKOUT_AGE_SECONDS` = 3h bound, so a live sweep still frees nothing. Measured fill rate over…
- **2 hours** — `WORKER_FINDING_A_MUTATION_TEST_RAN_THE_OPERATIONAL_SUITE_INSIDE_THE_PUBLISH_GATE_2026-08-12.md`: …ere quiet only by accident of arithmetic — they need `since_commit >= 2h` and the stall tests pin their gap at ~46 min. Latent, not isolated.…

---

Generated by `background/finding_classes.py` (atom `OPS10_finding_class_consolidation`). Regenerate with `python3 -m background.finding_classes --render`; verify with `--check`.
