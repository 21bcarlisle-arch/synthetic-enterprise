**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `OPS6_scoped_publish_path_suite`

# OPS6 exit (4): the scoped publish gate graded against every wedge episode on record

**Question.** Of the wedge episodes on record, which would today's blocking scope
(`background/publish_scope.resolve_scope()`) have **blocked**, and which would it have **annotated**?

**Not pre-registered.** The atom's exit asks for a census, not a test of a prediction, and I made no
prediction before running it. Read this as a measurement and nothing more.

## Instrument, and what it can and cannot see

- **Population:** every `docs/staging/done/*WEDGE*.md`, 100 documents. Each document stands for one episode.
  They are not independent: several describe the same Aug 9-10 wedge from different angles.
- **The red:** a test file path (`tests/…test_*.py` or `site/…test_*.py`) that appears **on a line saying
  FAILED / ERROR / red / failing**. This is a proxy. It can catch the test that *fixed* the episode when
  that test sits on a "red" line, and it misses a red the document names only in prose.
- **The scope:** today's live scope, 348 files, `full_suite=False`. The scope at the time of each episode
  was smaller, because it is derived from imports.
- **kind:** the document title names a commit-chain wedge (`EVERY_COMMIT`, `EVERY_LANE`, …) or a
  publish-gate one. OPS6 governs only the publish gate.
- **Reproduce:** run the script at the foot of this file from the repo root.

## Result

| kind | BLOCK | mixed | annotate | no test red |
|---|---|---|---|---|
| publish | 11 | 3 | 11 | 60 |
| commit-chain | 2 | 0 | 2 | 11 |

1. **60 of the 85 publish-gate episodes had no test red at all.** Their causes were a full disk or /tmp,
   races, merge-to-push forks, stale checkouts and uncommitted edits. No test scope blocks or annotates
   those. Narrowing the scope helps only with the other 25.
2. **Of those 25, 11 would be annotated today** (plus the outside half of 3 mixed). That is the shape
   the ruling meant: the map ratchet, the static-quality ratchet, the atom-notes store, the ledger
   and the alarm census.
3. **11 would still block.** Some of these are rightly in scope because they guard content:
   `test_partial_year_clv_headline_guard.py`, `test_phase_ob_settlement_reconciliation.py` and
   `test_website_integrity_fix.py`. Most are not. `test_process_run_complete.py`,
   `test_staging_archive_policy.py`, `test_control_mutation.py`, `test_publish_gate_red_census.py`,
   `test_a_duplicate_marker_is_not_a_publish.py`, `test_publish_gate_alert.py` and
   `test_head_green_census.py` are the **publisher's own bookkeeping**.
4. **Why that happens:** `background/process_run_complete.py` is a declared `PUBLISH_PATH_SOURCES` entry.
   The publisher is about 9,000 lines, and every test that imports it is selected, which accounts for
   **166 of the 348** blocking files (`tests/background/`). So an alarm or census red in the publisher
   still freezes the site. That is the failure the 10 Aug ruling exists to end.
   Filed: `docs/staging/SEAT_FINDING_THE_PUBLISHERS_OWN_HARNESS_TESTS_ARE_HALF_THE_BLOCKING_PUBLISH_SCOPE_2026-11-09.md`.

## Per episode

| kind | today's scope would | episode | red(s) named |
|---|---|---|---|
| publish | **no-test-red** | ADVISOR_POINTER_PUBLISH_WEDGE_2026-08-08 | - |
| publish | **no-test-red** | DIRECTOR_PRIORITY_UNWEDGE_AND_ALARM_TEETH_2026-08-08 | - |
| publish | **no-test-red** | DIRECTOR_RULING_UNWEDGE_AND_AXIS3_2026-07-23 | - |
| publish | **no-test-red** | DIRECTOR_RULING_UNWEDGE_PUBLISH_PRIORITY_ZERO_2026-07-23 | - |
| publish | **no-test-red** | DIRECTOR_RULING_WEDGE3_AND_RUNG1_MECHANISE_2026-07-24 | - |
| publish | **no-test-red** | DIRECTOR_STEER_SECOND_PUBLISH_WEDGE_2026-08-09 | - |
| commit-chain | **no-test-red** | SEAT_FINDING_A_CONTENT_LANDED_RENAME_LEFT_THE_PRE_RENAME_DRAFT_IN_THE_TREE_AND_IT_WEDGED_EVERY_LANE_FOR_22_HOURS_2026-09-07 | - |
| commit-chain | **no-test-red** | SEAT_FINDING_ELEVEN_BYTE_IDENTICAL_DUPLICATES_WEDGED_EVERY_LANES_COMMIT_AND_THE_DOOR_I_LANDED_THROUGH_HAS_THE_OBSERVER_WHERE_THE_OTHER_HAS_THE_REPAIR_2026-09-08 | - |
| publish | **no-test-red** | SEAT_FINDING_THE_CHECKOUT_ADVANCE_IS_JUDGED_BY_THE_CHECKOUTS_OWN_CODE_SO_EVERY_RULE_THAT_WOULD_UNWEDGE_IT_IS_INSIDE_THE_PAYLOAD_2026-09-24 | - |
| commit-chain | **no-test-red** | SEAT_FINDING_THE_DIRECTORS_OWN_STAGED_DOCUMENT_WEDGED_EVERY_MERGE_BECAUSE_A_MERGE_MAKES_ANOTHER_AUTHORS_FILE_THIS_COMMITS_OWN_2026-09-05 | - |
| publish | **no-test-red** | SEAT_FINDING_THE_LAST_PUBLISH_WEDGE_WAS_ONE_UNSTAGED_FILE_2026-09-02 | - |
| commit-chain | **no-test-red** | SEAT_FINDING_THE_MAP_IS_185_BYTES_FROM_ITS_RATCHET_CEILING_SO_THE_NEXT_LEVEL_MOVE_WEDGES_EVERY_COMMIT_2026-09-17 | - |
| publish | **no-test-red** | SEAT_FINDING_THE_PATH_THAT_WEDGED_THE_PUBLISHER_WAS_THE_FILE_THE_LANE_REPAIRING_THE_PUBLISHER_WAS_HOLDING_2026-09-04 | - |
| publish | **BLOCK** | SEAT_FINDING_THE_PUBLISH_GATE_JUDGED_A_HEAD_31_COMMITS_BEHIND_ORIGIN_AND_NOTHING_IN_THE_WEDGE_MACHINERY_READS_ORIGIN_2026-09-02 | `test_head_green_census.py` (in scope) |
| publish | **no-test-red** | SEAT_FINDING_THE_PUBLISH_WEDGE_WAS_TWO_UNCOMMITTED_EDITS_AND_NEITHER_IS_A_RED_TEST_2026-09-06 | - |
| publish | **BLOCK** | SEAT_FINDING_THE_REPAIR_FOR_THE_WEDGE_WAS_SITTING_UNLANDED_INSIDE_THE_WEDGE_2026-09-04 | `test_process_run_complete.py` (in scope) |
| publish | **no-test-red** | SEAT_FINDING_THE_REPAIR_THAT_CLEARS_THE_PUBLISH_WEDGE_RUNS_45_MINUTES_BEFORE_THE_GATE_THAT_READS_IT_2026-09-04 | - |
| publish | **no-test-red** | SEAT_FINDING_THE_RUNG_ONE_WEDGE_DRAW_COULD_NOT_BE_CLEARED_BY_THE_PIPELINE_BEING_HEALTHY_2026-09-06 | - |
| publish | **no-test-red** | SEAT_FINDING_THE_SITE_WEDGES_NAMED_CAUSE_WAS_THE_PAGE_AND_ONE_VARIABLE_RUNS_PUT_IT_IN_THE_TEST_FILE_2026-09-08 | - |
| publish | **no-test-red** | SEAT_FINDING_THE_SITE_WEDGES_STATED_REMEDY_NAMED_A_COMMAND_THAT_REPRODUCES_ITS_INPUT_BYTE_FOR_BYTE_2026-09-08 | - |
| publish | **no-test-red** | SEAT_FINDING_THE_SITE_WEDGE_IS_CLEARED_AND_THE_CONTROL_THAT_HELD_IT_WAS_PINNED_TO_A_LOG_COUNT_THAT_ROTATES_2026-09-08 | - |
| publish | **no-test-red** | SEAT_FINDING_THE_WEDGE_DETECTORS_MIN_ADMITTED_ANY_NUMBER_SO_ONE_UNRECORDED_STAMP_COULD_DATE_AN_OUTAGE_TO_1970_2026-09-04 | - |
| publish | **no-test-red** | SEAT_NOTE_THE_PUBLISH_WEDGE_IS_ONE_STAGED_TEST_REWRITE_FROM_CLEARING_2026-10-13 | - |
| commit-chain | **no-test-red** | SEAT_RESULT_A_FIXTURE_CATCH_ALL_ANSWERED_THE_NEW_ANCESTRY_PREDICATE_AND_WEDGED_EVERY_COMMIT_2026-09-17 | - |
| publish | **no-test-red** | SEAT_RESULT_THE_CHURN_BELIEF_PREMISE_WAS_SPENT_AND_THE_WEDGE_MOVED_TO_A_REMEDY_THAT_REVERTS_CORRECTIONS_2026-09-24 | - |
| commit-chain | **no-test-red** | SEAT_RESULT_THE_HEAD_RED_OBSERVATION_IS_MACHINE_STATE_AND_UNTRACKING_IT_IN_PLACE_WOULD_HAVE_WEDGED_EVERY_LANE_2026-09-10 | - |
| publish | **no-test-red** | SEAT_RESULT_THE_HOOK_CHAIN_IS_GROWING_AT_6_PERCENT_A_DAY_AND_THE_INSTRUMENT_GOES_BLIND_EXACTLY_WHEN_THE_PUBLISH_PATH_WEDGES_2026-09-18 | - |
| publish | **no-test-red** | SEAT_RESULT_THE_PUBLISHERS_LIVE_WEDGE_WAS_NOT_THE_UNTRACKED_CONTROL_AND_THE_CONTROL_COULD_NOT_LAND_ALONE_2026-09-08 | - |
| publish | **no-test-red** | SEAT_RESULT_THE_PUBLISH_GATE_WAS_WEDGED_ON_TWO_REDS_THAT_DO_NOT_EXIST_AT_HEAD_2026-09-08 | - |
| publish | **no-test-red** | SEAT_RESULT_THE_PUBLISH_WEDGE_IS_ONE_UNCOMMITTED_SENTENCE_OF_SEAT_PROSE_AND_THE_GUARD_REFUSES_THE_WHOLE_TREE_INSTEAD_OF_ITS_AUTHOR_2026-09-16 | - |
| publish | **no-test-red** | SEAT_RESULT_THE_STRETCH_ALARM_WAS_HOSTED_INSIDE_THE_PUBLISHER_THAT_WAS_WEDGED_AND_THE_PRODUCT_FLOOR_WAS_A_SENTENCE_2026-09-16 | - |
| publish | **no-test-red** | SEAT_RESULT_THE_THREE_FACTS_REACH_THE_READER_AND_THE_WEDGE_THAT_HELD_THEM_BACK_WAS_ONE_ARGUMENT_SHIFTED_ONE_PLACE_LEFT_2026-09-10 | - |
| publish | **BLOCK** | WORKER_FINDING_A_DUPLICATE_MARKER_DISARMS_THE_WEDGE_ALARM_2026-08-10 | `test_a_duplicate_marker_is_not_a_publish.py` (in scope) |
| publish | **no-test-red** | WORKER_FINDING_A_GREEN_PUBLISH_CANNOT_CLEAR_THE_WEDGE_UNTIL_A_SECOND_SUITE_THE_DEADLINE_DOES_NOT_KNOW_ABOUT_FINISHES_2026-08-20 | - |
| commit-chain | **BLOCK** | WORKER_FINDING_A_HALF_FINISHED_ARCHIVE_MOVE_WEDGED_EVERY_LANES_COMMIT_AND_THE_DRAWN_CAUSE_WAS_ALREADY_SPENT_2026-09-08 | `test_process_run_complete.py` (in scope) |
| commit-chain | **no-test-red** | WORKER_FINDING_A_LEVEL_STAGED_IN_THE_SHARED_MAP_WEDGES_EVERY_LANES_PUBLISH_INDEFINITELY_2026-08-31 | - |
| publish | **BLOCK** | WORKER_FINDING_A_REFUTATION_SCORES_AS_EVIDENCE_IN_THE_WEDGE_CITATION_2026-08-12 | `test_publish_gate_alert.py` (in scope); `test_staging_archive_policy.py` (in scope) |
| commit-chain | **no-test-red** | WORKER_FINDING_A_SEAM_CUT_HOLLOWED_OUT_82_ORPHAN_RULINGS_AND_WEDGED_THE_REGISTER_2026-08-19 | - |
| publish | **no-test-red** | WORKER_FINDING_A_TOP_LEVEL_IMPORT_WEDGED_EVERY_PUBLISH_AND_THE_SMOKE_CHECK_COULD_NOT_SEE_IT_2026-08-17 | - |
| publish | **no-test-red** | WORKER_FINDING_DERIVED_ARTEFACT_STALENESS_IS_A_WEDGE_CLASS_2026-08-09 | - |
| publish | **annotate** | WORKER_FINDING_PUBLISH_WEDGE_ROOT_CAUSE_2026-08-08 | `test_static_quality_ratchet.py` |
| publish | **no-test-red** | WORKER_FINDING_REPEATING_ALARM_UNDECLARED_WORKTREE_S_ACCRETION_REPORT_ONLY_AGENT_ORPHAN_WEDGE_CHECK_2026-08-24 | - |
| publish | **annotate** | WORKER_FINDING_SECOND_WEDGE_CAUSE_LANDED_AFTER_THE_FIRST_2026-08-09 | `test_seat_guard_daemons.py` |
| commit-chain | **no-test-red** | WORKER_FINDING_THE_CONTROL_ON_THE_REPAIRERS_ROOM_SET_FROZE_THE_ANSWER_AND_A_NEW_ROOM_WEDGED_EVERY_COMMIT_2026-09-04 | - |
| publish | **annotate** | WORKER_FINDING_THE_ELEVENTH_WEDGE_WAS_A_STACK_NOT_A_BUG_2026-08-10 | `test_predictions_ledger_can_fail.py` |
| publish | **no-test-red** | WORKER_FINDING_THE_GATES_SKIP_PATH_NEVER_RESTAMPS_THE_GREEN_CLOCK_SO_THE_WEDGE_CROSS_CHECK_DECAYS_2026-08-27 | - |
| publish | **no-test-red** | WORKER_FINDING_THE_GENERATED_PATH_ORACLE_MISSES_A_TERMINAL_OUTPUT_NOBODY_RE_SPELLS_AND_THE_WEDGE_REMEDY_THEN_SAYS_TO_LAND_IT_2026-09-10 | - |
| commit-chain | **no-test-red** | WORKER_FINDING_THE_LIVENESS_REACHABILITY_LEG_PASSES_ALONE_AND_FAILS_IN_THE_SUITE_SO_EVERY_LANES_COMMIT_IS_WEDGED_2026-09-16 | - |
| publish | **no-test-red** | WORKER_FINDING_THE_PRESERVATION_SAYS_NOTHING_HAS_BEEN_WRITTEN_AFTER_IT_HAS_WRITTEN_THE_REF_AND_THE_ALL_OR_NOTHING_RULE_TURNS_THAT_INTO_A_BOX_WIDE_WEDGE_2026-09-21 | - |
| publish | **no-test-red** | WORKER_FINDING_THE_PUBLISH_GATE_WEDGE_COULD_NOT_CLEAR_BECAUSE_A_SUCCESSFUL_PUBLISH_ARCHIVES_ITS_OWN_EVIDENCE_2026-08-17 | - |
| publish | **no-test-red** | WORKER_FINDING_THE_PUBLISH_GATE_WEDGE_TWO_DOCSTRINGS_CITE_HAS_NEVER_EXISTED_2026-08-18 | - |
| publish | **no-test-red** | WORKER_FINDING_THE_PUBLISH_WEDGES_BEHIND_ORIGIN_CAUSE_HAD_ALREADY_CLEARED_AND_HEAD_GRADES_GREEN_UNDER_THE_REAL_OVERLAY_2026-10-12 | - |
| publish | **no-test-red** | WORKER_FINDING_THE_PUBLISH_WEDGES_RECORDED_CAUSE_WAS_STALE_AND_SPLITS_INTO_A_LOSSLESS_HALF_AND_A_FALSE_RACE_2026-10-12 | - |
| publish | **annotate** | WORKER_FINDING_THE_PUBLISH_WEDGES_TALLY_IS_SEVENTEEN_UNTRACKED_DONE_MARKERS_AND_THE_QUEUE_IT_DRAINS_READS_EMPTY_2026-09-23 | `test_atom_notes_store.py` |
| publish | **no-test-red** | WORKER_FINDING_THE_PUBLISH_WEDGE_CLEARED_BY_THE_SHARED_HEAD_ADVANCE_AND_BOTH_RECORDED_REDS_WERE_THE_STALE_HEAD_2026-10-13 | - |
| publish | **no-test-red** | WORKER_FINDING_THE_PUBLISH_WEDGE_IS_SEVEN_DAYS_OF_ONE_UNRESOLVED_MERGE_CONFLICT_AND_THE_NARROWING_THAT_DEEPENS_IT_HAS_NO_CEILING_2026-09-17 | - |
| publish | **no-test-red** | WORKER_FINDING_THE_PUBLISH_WEDGE_RED_WAS_A_FULL_TMP_HELD_BY_SCRATCH_NO_REAPER_PATTERN_NAMES_2026-11-02 | - |
| commit-chain | **no-test-red** | WORKER_FINDING_THE_SITE_LANE_IS_WEDGED_FOR_EVERY_LANE_BY_A_PAGE_WHOSE_PRODUCER_NEVER_LANDED_2026-09-01 | - |
| commit-chain | **annotate** | WORKER_FINDING_THE_SPLIT_INVARIANT_WEDGES_THE_TREE_ON_THE_NEXT_SUCCESSFUL_BUILD_2026-08-26 | `test_maturity_map_store.py` |
| publish | **no-test-red** | WORKER_FINDING_THE_WEDGES_ORDERING_INSTRUMENT_RUNS_BACKWARDS_SINCE_THE_QUEUE_BECAME_A_STACK_2026-08-20 | - |
| publish | **annotate** | WORKER_FINDING_THE_WEDGE_ALARM_IS_DISARMED_BY_RUNS_THAT_PUBLISH_NOTHING_2026-08-10 | `test_atom_notes_store.py` |
| publish | **mixed** | WORKER_FINDING_THE_WEDGE_ALARM_NAMED_TESTS_THE_GATE_NEVER_RAN_2026-08-12 | `test_supervisor.py`; `test_daemon_loop_mutation.py` (in scope) |
| publish | **no-test-red** | WORKER_FINDING_THE_WEDGE_CLEARS_ON_PROCESS_EXIT_NOT_ON_THE_RECORDED_PASS_2026-08-12 | - |
| publish | **annotate** | WORKER_FINDING_THE_WEDGE_DETECTOR_FED_ITSELF_2026-08-12 | `test_self_clearing_alarm_census.py` |
| publish | **no-test-red** | WORKER_FINDING_THE_WEDGE_DETECTOR_HAS_BEEN_RUNNING_PRE_REPAIR_CODE_FROM_MEMORY_FOR_TWO_DAYS_2026-09-01 | - |
| publish | **no-test-red** | WORKER_FINDING_THE_WEDGE_DRAW_NEVER_READS_THE_COMMIT_ITS_OWN_FAILURE_RECORDS_NAME_2026-08-17 | - |
| publish | **no-test-red** | WORKER_FINDING_THE_WEDGE_FIX_LANDED_AND_EVERY_DAEMON_THAT_PUBLISHES_WAS_STILL_RUNNING_THE_CODE_IT_REPLACED_2026-08-17 | - |
| publish | **no-test-red** | WORKER_FINDING_THE_WEDGE_MESSAGE_CALLS_A_CONTENT_VIOLATION_STALENESS_AND_MISDIRECTS_THE_DIAGNOSIS_2026-08-28 | - |
| publish | **BLOCK** | WORKER_FINDING_THE_WEDGE_RECORD_CITED_A_TEST_THAT_NO_LONGER_EXISTS_2026-08-12 | `test_phase_ob_settlement_reconciliation.py` (in scope) |
| publish | **BLOCK** | WORKER_FINDING_THE_WEDGE_STATE_LAUNDERS_THE_ALARMS_OWN_I_DONT_KNOW_INTO_A_CONFIDENT_STALE_ANSWER_2026-08-20 | `test_partial_year_clv_headline_guard.py` (in scope) |
| publish | **BLOCK** | WORKER_FINDING_THE_WEDGE_SUSPECTS_ARE_THE_TEST_FILES_IMPORTS_SO_A_REGISTER_FILE_ACCUSES_EVERYONE_2026-08-20 | `test_control_mutation.py` (in scope) |
| publish | **BLOCK** | WORKER_FINDING_THE_WEDGE_WAS_A_TREE_LOCK_TIMEOUT_FILED_AS_A_TEST_REGRESSION_2026-08-30 | `test_process_run_complete.py` (in scope) |
| publish | **BLOCK** | WORKER_FINDING_THE_WEDGE_WAS_FIVE_INSTANCES_OF_ONE_CLASS_AND_pytest_x_SERVED_THEM_ONE_AT_A_TIME_2026-08-14 | `test_publish_gate_red_census.py` (in scope) |
| publish | **BLOCK** | WORKER_FINDING_WEDGE_REMAINDER_IS_FULL_SUITE_ONLY_2026-08-09 | `test_website_integrity_fix.py` (in scope) |
| publish | **no-test-red** | WORKER_REPORT_FIFTH_WEDGE_SUSPECT_DISPOSITION_2026-08-10 | - |
| publish | **annotate** | WORKER_REPORT_FOURTH_WEDGE_CLOSED_THE_DERIVED_ARTEFACT_CLASS_2026-08-10 | `test_blocked_atom_visibility.py` |
| publish | **no-test-red** | WORKER_REPORT_OPS3_THE_WEDGE_WAS_REPAIRED_FOURTEEN_HOURS_BEFORE_THE_SITE_SAID_SO_2026-08-13 | - |
| publish | **no-test-red** | WORKER_REPORT_PUBLISH_WEDGE_SUSPECT_DISPOSITION_2026-08-09 | - |
| publish | **no-test-red** | WORKER_REPORT_SIXTH_WEDGE_SUSPECT_DISPOSITION_2026-08-10 | - |
| publish | **no-test-red** | WORKER_REPORT_THE_FIFTEENTH_WEDGE_WAS_THE_DEBRIS_OF_THE_OTHER_FOURTEEN_2026-08-10 | - |
| publish | **annotate** | WORKER_REPORT_THE_FOURTEENTH_WEDGE_WAS_A_RUNG_READING_LIVE_DISK_2026-08-10 | `test_forward_discovery_draw.py` |
| publish | **no-test-red** | WORKER_REPORT_THE_TENTH_WEDGE_WAS_THE_GATE_MATERIALISING_ITSELF_TWICE_2026-08-10 | - |
| publish | **mixed** | WORKER_REPORT_THE_TWELFTH_WEDGE_WAS_A_MISSING_CALLEE_2026-08-10 | `test_forward_discovery_draw.py`; `test_publish_gate_blocking_payload.py` (in scope) |
| publish | **BLOCK** | WORKER_REPORT_THE_WEDGES_RED_WAS_A_SIBLING_TESTS_STALE_PIN_2026-08-12 | `test_staging_archive_policy.py` (in scope) |
| publish | **annotate** | WORKER_REPORT_THIRD_WEDGE_WAS_A_FULL_DISK_2026-08-09 | `test_epistemic_wall_ratchet.py` |
| publish | **no-test-red** | WORKER_REPORT_THIRTEENTH_WEDGE_SUSPECT_DISPOSITION_2026-08-10 | - |
| publish | **no-test-red** | WORKER_RESULT_A_STAGING_DOCUMENT_IN_THE_ROOT_ALONE_WEDGED_ORIGIN_AND_ONLY_A_WORKTREE_AT_ORIGIN_COULD_UNWEDGE_IT_2026-09-16 | - |
| publish | **no-test-red** | WORKER_RESULT_THE_ELEVEN_THOUSAND_MINUTE_WEDGE_IS_TWO_LAYERS_AND_NEITHER_IS_A_BROKEN_TEST_2026-09-18 | - |
| publish | **annotate** | WORKER_RESULT_THE_FIFTY_EIGHT_FAILURE_PUBLISH_EPISODE_HAS_NO_RED_TEST_AND_THE_WEDGE_IS_A_MERGE_TO_PUSH_RACE_2026-09-17 | `test_static_quality_ratchet.py` |
| publish | **no-test-red** | WORKER_RESULT_THE_FLOOR_THAT_WEDGED_THIRTY_ONE_PUBLISHES_WAS_UNCOMMITTED_AND_A_LANDING_ALONE_COULD_NOT_CLEAR_IT_2026-09-16 | - |
| publish | **no-test-red** | WORKER_RESULT_THE_FORK_WAS_THE_WHOLE_WEDGE_AND_THE_ORPHAN_FLOOR_HAD_ALREADY_BEEN_DISCHARGED_2026-09-16 | - |
| publish | **no-test-red** | WORKER_RESULT_THE_PUBLISH_WEDGE_IS_A_FIXTURE_THAT_PINNED_TWO_OF_THE_THREE_WINDOWS_ITS_GUARD_READS_2026-09-18 | - |
| publish | **annotate** | WORKER_RESULT_THE_PUBLISH_WEDGE_WAS_NEITHER_NAMED_CAUSE_BUT_A_PATHSPEC_SPLITTING_AN_AUTHORED_PAIR_2026-09-16 | `test_index_reflects_the_record.py` |
| publish | **no-test-red** | WORKER_RESULT_THE_SITE_WEDGE_WAS_A_WEEK_OLD_WORKING_COPY_AND_LANDING_IT_ALONE_WOULD_NOT_HAVE_CLEARED_IT_2026-09-16 | - |
| commit-chain | **annotate** | WORKER_RESULT_THE_TREE_IS_LEVEL_AND_THE_CONTROL_THAT_WEDGED_IT_WAS_GRADING_AN_UPPER_BOUND_AS_A_MEASUREMENT_2026-09-21 | `test_static_quality_ratchet.py` |
| publish | **no-test-red** | WORKER_RESULT_THE_WEDGES_RED_WAS_REAL_ON_A_FORK_THAT_DIED_THREE_MINUTES_LATER_AND_THE_RECORD_COULD_NOT_SAY_SO_2026-09-18 | - |
| publish | **no-test-red** | WORKER_RESULT_THE_WEDGE_BROKE_ON_THE_FIRST_POST_FIX_RUN_AND_THE_EXIT_CRITERION_ASKED_FOR_THE_WORSE_OUTCOME_2026-09-21 | - |
| commit-chain | **BLOCK** | WORKER_RESULT_THE_WEDGE_CLEARED_ON_A_MERGE_THE_TREE_HAD_NEVER_TAKEN_AND_THE_ESCALATION_STRIPS_THE_FIELD_THAT_SAYS_IT_MAY_BE_MISDIRECTED_2026-09-18 | `test_a_multi_chain_landing_is_not_recorded_as_one_chain.py` (in scope) |
| publish | **no-test-red** | WORKER_RESULT_THE_WEDGE_IS_THE_CLASS_LANDING_A_STAGING_DOCUMENT_MINTS_AND_NO_CLASS_COULD_TAKE_IT_2026-09-17 | - |
| publish | **mixed** | WORKER_RESULT_THE_WEDGE_WAS_A_LANDING_THAT_NEVER_HAPPENED_AND_THE_SITE_HALF_WAS_SPENT_BY_ROTATION_2026-09-21 | `test_static_quality_ratchet.py`; `test_episode_prior_partition.py` (in scope) |

## The script

```python
import re, sys, json, glob, os, collections
sys.path.insert(0, os.getcwd())
from background import publish_scope
scope = publish_scope.resolve_scope(); blocking = set(scope["tests"])
pat = re.compile(r"((?:tests|site)/[\w/\.\-]+?test_[\w\-]+\.py)")
redline = re.compile(r"FAILED|ERROR|\bred\b|\breds\b|failing|fails", re.I)
out = collections.Counter(); rows = []
for d in sorted(glob.glob("docs/staging/done/*WEDGE*.md")):
    name = os.path.basename(d); txt = open(d).read()
    kind = "commit-chain" if re.search(r"EVERY_(LANES_)?COMMIT|EVERY_MERGE|EVERY_LANE|THE_TREE|THE_REGISTER", name) else "publish"
    reds = sorted({m for ln in txt.splitlines() if redline.search(ln) for m in pat.findall(ln)})
    if not reds: v = "no-test-red"
    elif any(r in blocking for r in reds) and all(r in blocking for r in reds): v = "BLOCK"
    elif any(r in blocking for r in reds): v = "mixed"
    else: v = "annotate"
    out[(kind, v)] += 1; rows.append({"doc": name, "kind": kind, "verdict": v, "reds": [[r, r in blocking] for r in reds]})
print("scope files", len(blocking))
for k in sorted(out): print(k, out[k])
json.dump({"scope_files": len(blocking), "rows": rows}, open("/tmp/ops6probe/out2.json","w"), indent=1)
for r in rows:
    if r["kind"]=="publish" and r["verdict"]!="no-test-red": print(r["verdict"], r["doc"][:90], [x[0].split('/')[-1][:60] for x in r["reds"]][:3])
```
