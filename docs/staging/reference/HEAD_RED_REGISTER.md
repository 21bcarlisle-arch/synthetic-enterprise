# [REGISTER] Tests red at HEAD

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

**THIS IS A REGISTER, NOT A QUEUE ITEM. Do not archive it.** It is re-rendered in place by `background/head_red_register` on every HEAD-green census run. You action it by MAKING A TEST GREEN, or by adding that test BY NAME to `docs/observability/head_red_baseline.json` with a reason. There is no third exit and no blanket disposition: one paragraph must not be able to retire 830 subjects, which is the wallpaper this register exists to replace.

## The count, with each number's population named

| | |
|---|---:|
| red at HEAD, last run | **830** |
| accepted by a person, with a reason | 0 |
| **owed — neither fixed nor accepted** | **830** |
| passed, same run | unreadable |

Last run **2026-09-02T04:30:02+00:00** at HEAD `ec2e0b1a4`.

Causes that run: OSError x760, AssertionError x33, CalledProcessError x24, JSONDecodeError x12, FileNotFoundError x2, IndexError x2, KeyError x2

## The 830 owed, longest-standing first

`runs` is consecutive census runs this test has been red — the recurrence signal, the same argument `class_debt` makes for instance count. The longest-standing red here has survived **1 run(s)**.

| test | runs red | first seen |
|---|---:|---|
| `tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py::test_no_tree_scanning_test_passes_on_an_empty_population` | 1 | 2026-09-02 |
| `tests/background/test_finding_classes.py::test_a_class_id_named_outside_the_registration_section_is_a_mention_not_a_claim` | 1 | 2026-09-02 |
| `tests/background/test_finding_classes.py::test_a_self_clearing_alarm_is_never_consolidated_into_a_class` | 1 | 2026-09-02 |
| `tests/background/test_finding_classes.py::test_mutation_dropping_the_alarm_exclusion_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_classes.py::test_mutation_j_dropping_the_unknown_class_rule_kills_that_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_classes.py::test_mutation_k_reading_the_declaration_from_the_whole_body_kills_that_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_classes.py::test_the_alarm_exclusion_does_not_swallow_an_authored_finding` | 1 | 2026-09-02 |
| `tests/background/test_finding_classes.py::test_the_alarms_title_really_does_route_it_into_a_class` | 1 | 2026-09-02 |
| `tests/background/test_finding_classes.py::test_the_excluded_alarm_stays_live_drawable_and_check_clean` | 1 | 2026-09-02 |
| `tests/background/test_finding_classes.py::test_the_registration_loses_to_nothing_but_is_recorded_as_contested` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_bad_artefact_on_a_continuation_line_voids_the_whole_discharge` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_discharge_below_the_header_block_DOES_release` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_discharge_naming_an_artefact_that_does_not_exist_does_not_release` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_discharge_naming_no_test_node_does_not_release` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_discharge_spread_over_several_lines_claims_every_artefact_on_them` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_discharge_the_filesystem_refuses_does_not_stand_the_namer_down` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_discharge_whose_file_does_not_define_the_node_does_not_release` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_discharge_written_mid_SENTENCE_is_prose_and_still_does_not_release` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_document_saying_an_instrument_is_wrong_is_named_when_not_blocking` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_falsifier_in_neither_landed_tree_is_still_refused` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_falsifier_in_no_tree_and_never_deleted_is_still_refused` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_machine_doorbell_is_out_of_the_population_and_only_by_exact_prefix` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_named_test_exonerates_the_document_for_that_red` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_node_only_head_still_defines_releases_when_the_index_copy_has_lost_it` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_node_that_exists_only_in_the_working_tree_does_not_release` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_retired_falsifier_releases_and_records_that_its_evidence_is_HISTORICAL` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_retired_file_is_not_an_AMNESTY_for_a_node_it_never_defined` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_a_valid_discharge_reads_a_blocking_document_down_to_recorded` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_artefact_on_disk_but_not_in_the_index_does_not_release` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_exoneration_covers_nothing_when_the_red_names_no_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_exoneration_must_name_a_test_file_not_a_module` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_invalid_discharge_is_surfaced_not_silent` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_invalid_discharge_leaves_the_severity_where_it_was` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_ordinary_word_in_the_header_does_not_stand_the_namer_down[CLEARED]` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_ordinary_word_in_the_header_does_not_stand_the_namer_down[CLOSED]` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_ordinary_word_in_the_header_does_not_stand_the_namer_down[DISCHARGED]` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_ordinary_word_in_the_header_does_not_stand_the_namer_down[FIXED]` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_ordinary_word_in_the_header_does_not_stand_the_namer_down[REPAIRED]` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_ordinary_word_in_the_header_does_not_stand_the_namer_down[accepted]` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_ordinary_word_in_the_header_does_not_stand_the_namer_down[cleared]` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_ordinary_word_in_the_header_does_not_stand_the_namer_down[discharged]` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_ordinary_word_in_the_header_does_not_stand_the_namer_down[landed]` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_ordinary_word_in_the_header_does_not_stand_the_namer_down[relieved]` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_ordinary_word_in_the_header_does_not_stand_the_namer_down[repaired]` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_unclassified_document_saying_an_instrument_is_wrong_is_named` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_an_unreadable_index_refuses_rather_than_releasing` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_another_lanes_staged_deletion_does_not_void_a_committed_falsifier` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_blocking_findings_group_by_lane` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_exonerating_for_one_test_does_not_exonerate_for_another` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_a_defaulting_the_missing_header_to_latent_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_b_dropping_the_lane_from_the_parse_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_c_releasing_without_a_falsifier_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_d_dropping_the_existence_check_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_e_letting_an_invalid_discharge_release_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_f_covering_the_empty_trail_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_f_restoring_the_free_text_escape_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_g_dropping_the_denial_guard_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_g_subset_becomes_intersection_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_h_dropping_the_existence_check_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_h_reading_the_node_from_the_working_tree_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_i_accepting_a_module_path_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_i_dropping_the_pre_retirement_node_check_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_i_reading_only_the_first_line_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_j_reading_the_landed_set_from_the_index_alone_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_j_the_null_control_is_LOAD_BEARING_not_decorative` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_mutation_k_dropping_the_head_blob_fallback_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_only_a_valid_discharge_stands_the_namer_down` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_the_authors_reason_line_is_not_read_as_artefacts` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_the_body_of_a_document_never_releases_it` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_the_claim_must_sit_in_the_header_block_not_in_prose` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_the_monthly_maintenance_marker_is_out_of_the_population` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_the_population_is_counted_from_the_filesystem` | 1 | 2026-09-02 |
| `tests/background/test_finding_severity.py::test_the_same_document_classified_blocking_is_not_named` | 1 | 2026-09-02 |
| `tests/background/test_fork_salvage.py::test_ANY_writer_can_declare_its_worktree_in_use_not_just_the_executor` | 1 | 2026-09-02 |
| `tests/background/test_fork_salvage.py::test_a_DEAD_executors_worktree_is_still_salvaged` | 1 | 2026-09-02 |
| `tests/background/test_fork_salvage.py::test_a_live_executors_worktree_is_not_salvaged` | 1 | 2026-09-02 |
| `tests/background/test_fork_salvage.py::test_a_marker_left_by_a_DEAD_writer_does_not_spare_the_worktree` | 1 | 2026-09-02 |
| `tests/background/test_fork_salvage.py::test_the_SCAN_applies_the_live_writer_filter_not_just_the_predicate` | 1 | 2026-09-02 |
| `tests/background/test_forward_attachment_register.py::test_absent_map_makes_every_id_unknown_rather_than_accepted` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_act_surfaces_only_the_still_awaiting_track` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_all_complete_register_permits_rest` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_authorized_set_enumeration_all_empty_is_rest_legitimate` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_authorized_set_enumeration_names_every_level` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_complete_tracks_leave_the_drawable_set` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_completion_filter_is_load_bearing_mutation` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_dispositioned_tracks_stay_non_drawable_but_drop_from_the_act` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_graduation_emit_fires_once_per_complete_set` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_graduation_proposal_batches_complete_tracks` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_malformed_status_table_fails_safe_toward_work` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_may_rest_with_genuinely_empty_authorized_set` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_must_not_rest_with_nonempty_register` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_no_graduation_proposal_when_nothing_complete` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_partial_complete_still_forbids_rest` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_propose_half_drains_when_proposal_written_permits_rest` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_propose_half_forbids_rest_the_overnight_breach` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_propose_half_marker_absent_does_not_forbid_rest` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_propose_half_parses_only_the_frame_plus_proposal_track` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_propose_half_rung_is_load_bearing_mutation` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_rung_is_load_bearing_mutation` | 1 | 2026-09-02 |
| `tests/background/test_forward_discovery_draw.py::test_tracks_parse_highest_rank_first` | 1 | 2026-09-02 |
| `tests/background/test_gap_ledger_reconciler.py::test_a_module_that_only_READS_the_ledger_is_not_discovered_as_a_producer` | 1 | 2026-09-02 |
| `tests/background/test_gap_register_scan.py::test_neuter_all_registers_reads_closed_then_restore_reads_open` | 1 | 2026-09-02 |
| `tests/background/test_gap_register_scan.py::test_register1_text_heuristic_beats_old_measured_bound_key` | 1 | 2026-09-02 |
| `tests/background/test_gap_register_scan.py::test_register2_below_naive_cell_is_open` | 1 | 2026-09-02 |
| `tests/background/test_gap_register_scan.py::test_register2_nonfinite_at_weight_fails_safe_open` | 1 | 2026-09-02 |
| `tests/background/test_gap_register_scan.py::test_register6_state_key_beats_old_audit_prefix_key` | 1 | 2026-09-02 |
| `tests/background/test_gap_register_scan.py::test_single_open_row_flips_level_to_yes` | 1 | 2026-09-02 |
| `tests/background/test_gap_register_scan.py::test_supervisor_level_present_and_killable` | 1 | 2026-09-02 |
| `tests/background/test_gap_register_scan.py::test_unreadable_register_reads_drawable` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_a_blocker_in_another_lane_does_not_refuse` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_a_discharge_naming_a_nonexistent_test_releases_nothing` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_a_level_correction_can_never_satisfy_a_promotion` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_a_live_in_lane_blocker_refuses_the_level_record` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_an_absent_staging_root_refuses_and_is_still_dischargeable` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_an_acceptance_releases_only_the_finding_it_names` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_an_acceptance_survives_the_finding_being_archived` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_an_atom_with_no_lane_in_the_map_is_refused_under_unknown_lane` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_an_unclassified_document_refuses_every_lane` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_mutation_a_dropping_the_blocking_check_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_mutation_b_dropping_the_lane_scope_kills_a_named_test` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_record_level_correction_writes_an_honest_envelope_and_requires_evidence` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_record_level_up_self_certified_writes_honest_envelope_and_requires_evidence` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_recording_and_accepting_the_limitation_lets_the_next_raise_through` | 1 | 2026-09-02 |
| `tests/background/test_gate_authorization.py::test_repairing_the_finding_lets_the_next_raise_through` | 1 | 2026-09-02 |
| `tests/background/test_ghost_pusher_attribution.py::test_the_sentinel_is_inherited_by_a_real_git_subprocess` | 1 | 2026-09-02 |
| `tests/background/test_governance_refusal.py::test_build_draw_of_only_gated_atoms_is_empty` | 1 | 2026-09-02 |
| `tests/background/test_governance_refusal.py::test_build_draw_refuses_gated_atom_even_at_max_dial` | 1 | 2026-09-02 |
| `tests/background/test_governance_refusal.py::test_gated_atom_surfaces_as_discover_with_explicit_no_build_instruction` | 1 | 2026-09-02 |
| `tests/background/test_governance_refusal.py::test_held_in_progress_staging_doc_is_not_surfaced` | 1 | 2026-09-02 |
| `tests/background/test_governance_refusal.py::test_held_manifest_daemon_running_is_flagged_not_accepted` | 1 | 2026-09-02 |
| `tests/background/test_governance_refusal.py::test_single_build_draw_never_returns_the_gated_atom` | 1 | 2026-09-02 |
| `tests/background/test_harden_rung_pass_ceiling.py::test_MUTATION_FAIL_OPEN_a_broken_ceiling_does_not_narrow_the_core_draw` | 1 | 2026-09-02 |
| `tests/background/test_harden_rung_pass_ceiling.py::test_MUTATION_RULE_0_the_gate_never_zeroes_the_feasible_set` | 1 | 2026-09-02 |
| `tests/background/test_harden_rung_pass_ceiling.py::test_MUTATION_without_the_gate_the_same_draw_hands_out_the_saturated_atom` | 1 | 2026-09-02 |
| `tests/background/test_harden_rung_pass_ceiling.py::test_a_BUILD_atom_over_its_own_ceiling_is_excluded_too` | 1 | 2026-09-02 |
| `tests/background/test_harden_rung_pass_ceiling.py::test_a_saturated_HARDEN_atom_is_excluded_from_the_core_draw` | 1 | 2026-09-02 |
| `tests/background/test_harden_rung_pass_ceiling.py::test_the_gate_is_WIRED_into_the_production_core_draw` | 1 | 2026-09-02 |
| `tests/background/test_harden_rung_pass_ceiling.py::test_the_live_map_and_live_ceiling_agree_that_no_atom_over_its_ceiling_is_drawable` | 1 | 2026-09-02 |
| `tests/background/test_inbound_secret_redaction.py::test_no_raw_file_is_written_for_an_ordinary_message` | 1 | 2026-09-02 |
| `tests/background/test_inbound_secret_redaction.py::test_preserve_raw_NEVER_raises_when_the_location_is_unwritable` | 1 | 2026-09-02 |
| `tests/background/test_inbound_secret_redaction.py::test_preserve_raw_writes_the_unredacted_message_with_owner_only_permissions` | 1 | 2026-09-02 |
| `tests/background/test_inbound_secret_redaction.py::test_route_1_an_ordinary_message_gets_NO_redaction_banner` | 1 | 2026-09-02 |
| `tests/background/test_inbound_secret_redaction.py::test_route_1_the_staged_file_SAYS_that_something_was_removed` | 1 | 2026-09-02 |
| `tests/background/test_inbound_secret_redaction.py::test_route_1_the_staged_file_does_not_contain_the_credential` | 1 | 2026-09-02 |
| `tests/background/test_inbound_secret_redaction.py::test_route_2_the_QUARANTINE_file_is_guarded_too` | 1 | 2026-09-02 |
| `tests/background/test_inbound_secret_redaction.py::test_route_3_is_guarded_at_the_FUNCTION_not_at_its_call_sites` | 1 | 2026-09-02 |
| `tests/background/test_inbound_secret_redaction.py::test_route_3_the_responder_LOG_is_guarded` | 1 | 2026-09-02 |
| `tests/background/test_inbound_secret_redaction.py::test_the_raw_message_is_preserved_out_of_tree_when_something_was_removed` | 1 | 2026-09-02 |
| `tests/background/test_last_tested_green_clock.py::test_a_green_stamps_the_sha_and_the_clock_together` | 1 | 2026-09-02 |
| `tests/background/test_last_tested_green_clock.py::test_an_unwritable_clock_never_reds_a_publish_the_suite_passed` | 1 | 2026-09-02 |
| `tests/background/test_last_tested_green_clock.py::test_mutation_the_sidecar_written_at_the_module_default_lands_in_the_live_record` | 1 | 2026-09-02 |
| `tests/background/test_last_tested_green_clock.py::test_the_stamp_reports_whether_it_landed` | 1 | 2026-09-02 |
| `tests/background/test_last_tested_green_clock.py::test_the_writer_and_the_reader_agree_on_the_shape` | 1 | 2026-09-02 |
| `tests/background/test_live_ledger_guard.py::test_write_gap_entry_still_writes_when_given_a_scratch_path` | 1 | 2026-09-02 |
| `tests/background/test_live_payment_triad.py::test_d8_attribution_is_published_as_structure_and_as_a_sentence` | 1 | 2026-09-02 |
| `tests/background/test_live_payment_triad.py::test_measure_and_write_renders_its_published_note_with_both_directions` | 1 | 2026-09-02 |
| `tests/background/test_live_payment_triad.py::test_the_belief_caveats_reach_the_written_ledger_not_only_the_result` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_a_bare_director_reserved_adjective_does_NOT_unblock[director-reserved` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_a_bare_director_reserved_adjective_does_NOT_unblock[self` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_a_bare_director_reserved_adjective_does_NOT_unblock[the` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_an_explicit_self_drawable_marker_still_wins` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_genuine_upstream_blocker_still_blocks[depends_on` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_genuine_upstream_blocker_still_blocks[the` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_permission_blocked_mint_is_self_drawable[a` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_permission_blocked_mint_is_self_drawable[director` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_permission_blocked_mint_is_self_drawable[director_build_open` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_permission_blocked_mint_is_self_drawable[director_level_up` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_permission_blocked_mint_is_self_drawable[main-session/director` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_reserved_real_world_consequence_still_blocks_even_with_a_permission_token` | 1 | 2026-09-02 |
| `tests/background/test_mint_permission_block_abolished.py::test_unreadable_or_unstated_mint_fails_closed_to_blocked` | 1 | 2026-09-02 |
| `tests/background/test_misparked_campaign_draw.py::test_closed_register_entry_does_not_suppress` | 1 | 2026-09-02 |
| `tests/background/test_misparked_campaign_draw.py::test_fully_blocked_campaign_not_surfaced` | 1 | 2026-09-02 |
| `tests/background/test_misparked_campaign_draw.py::test_marker_past_the_head_still_caught` | 1 | 2026-09-02 |
| `tests/background/test_misparked_campaign_draw.py::test_non_campaign_doc_not_surfaced` | 1 | 2026-09-02 |
| `tests/background/test_misparked_campaign_draw.py::test_parked_campaign_with_proceedable_item_is_surfaced` | 1 | 2026-09-02 |
| `tests/background/test_misparked_campaign_draw.py::test_reconciled_into_open_register_not_double_surfaced` | 1 | 2026-09-02 |
| `tests/background/test_misparked_campaign_draw.py::test_supervisor_draw_surfaces_parked_campaign` | 1 | 2026-09-02 |
| `tests/background/test_model_tier.py::test_a_broken_pilot_config_is_opus[-` | 1 | 2026-09-02 |
| `tests/background/test_model_tier.py::test_a_broken_pilot_config_is_opus[not:` | 1 | 2026-09-02 |
| `tests/background/test_model_tier.py::test_a_broken_pilot_config_is_opus[version:` | 1 | 2026-09-02 |
| `tests/background/test_model_tier.py::test_disabling_one_class_reverts_only_that_class` | 1 | 2026-09-02 |
| `tests/background/test_model_tier.py::test_log_decision_writes_an_attributable_line` | 1 | 2026-09-02 |
| `tests/background/test_model_tier.py::test_the_window_closes_the_pilot_with_no_edit` | 1 | 2026-09-02 |
| `tests/background/test_naive_organ.py::test_answer_rejects_empty_evidence_and_accepts_with_evidence` | 1 | 2026-09-02 |
| `tests/background/test_naive_organ.py::test_anti_capture_payload_contains_no_prior_qa` | 1 | 2026-09-02 |
| `tests/background/test_naive_organ.py::test_debounce_does_not_reask_an_open_question` | 1 | 2026-09-02 |
| `tests/background/test_naive_organ.py::test_falsify_advisor_doc_runs_a_falsify_pass` | 1 | 2026-09-02 |
| `tests/background/test_naive_organ.py::test_falsify_staged_doc_reads_from_disk` | 1 | 2026-09-02 |
| `tests/background/test_naive_organ.py::test_hit_rate_is_a_diagnostic` | 1 | 2026-09-02 |
| `tests/background/test_naive_organ.py::test_pa1_map_simplifications_prose_never_leaks_into_the_payload` | 1 | 2026-09-02 |
| `tests/background/test_naive_organ.py::test_run_daemon_fires_the_organ_off_its_own_clock_not_a_publish` | 1 | 2026-09-02 |
| `tests/background/test_naive_organ.py::test_run_organ_cycle_and_digest_section_are_wired` | 1 | 2026-09-02 |
| `tests/background/test_naive_organ.py::test_seed_replay_from_frozen_fixture_rediscovers_at_least_three_catches` | 1 | 2026-09-02 |
| `tests/background/test_naive_organ.py::test_the_line_declines_purpose_claims_without_invoking` | 1 | 2026-09-02 |
| `tests/background/test_named_but_unminted.py::test_a_lying_free_prose_number_does_not_over_cover` | 1 | 2026-09-02 |
| `tests/background/test_named_but_unminted.py::test_coverage_signal_2_banner_landed_covers_a_deliverable_with_no_mint_doc` | 1 | 2026-09-02 |
| `tests/background/test_named_but_unminted.py::test_done_rulings_are_not_sources_but_are_coverage` | 1 | 2026-09-02 |
| `tests/background/test_named_but_unminted.py::test_law_c_output_derives_from_primary_state_mutation` | 1 | 2026-09-02 |
| `tests/background/test_named_but_unminted.py::test_ruling_without_work_block_yields_no_residue_here` | 1 | 2026-09-02 |
| `tests/background/test_named_but_unminted.py::test_unminted_deliverable_appears_then_disappears_when_minted` | 1 | 2026-09-02 |
| `tests/background/test_notification_digest.py::test_a_deferred_item_is_on_disk_before_the_call_returns` | 1 | 2026-09-02 |
| `tests/background/test_notification_digest.py::test_a_deferred_item_still_obeys_transition_only` | 1 | 2026-09-02 |
| `tests/background/test_notification_digest.py::test_a_digested_item_is_still_findable_afterwards` | 1 | 2026-09-02 |
| `tests/background/test_notification_digest.py::test_a_rate_limited_digest_leaves_every_item_pending` | 1 | 2026-09-02 |
| `tests/background/test_notification_digest.py::test_a_suppressed_digest_does_not_advance_the_mark` | 1 | 2026-09-02 |
| `tests/background/test_notification_digest.py::test_a_torn_queue_line_does_not_lose_the_rest` | 1 | 2026-09-02 |
| `tests/background/test_notification_digest.py::test_an_elided_digest_says_so_rather_than_reading_complete` | 1 | 2026-09-02 |
| `tests/background/test_notification_digest.py::test_defer_returns_a_sentinel_and_never_an_id` | 1 | 2026-09-02 |
| `tests/background/test_notification_digest.py::test_maybe_flush_is_throttled_but_never_drops` | 1 | 2026-09-02 |
| `tests/background/test_notification_digest.py::test_notify_defers_a_deferrable_class_instead_of_sending` | 1 | 2026-09-02 |
| `tests/background/test_notification_digest.py::test_the_digest_names_the_file_that_holds_every_line` | 1 | 2026-09-02 |
| `tests/background/test_oom_watch.py::test_a_raising_clause_never_reaches_the_draw_ladder` | 1 | 2026-09-02 |
| `tests/background/test_oom_watch.py::test_rung_1d_carries_the_clause_and_drops_the_false_assertion` | 1 | 2026-09-02 |
| `tests/background/test_oom_watch.py::test_rung_1d_is_unharmed_when_the_door_is_clean` | 1 | 2026-09-02 |
| `tests/background/test_open_campaign_draw.py::test_closed_campaign_leaves_the_drawable_set` | 1 | 2026-09-02 |
| `tests/background/test_open_campaign_draw.py::test_empty_or_absent_register_permits_rest` | 1 | 2026-09-02 |
| `tests/background/test_open_campaign_draw.py::test_independence_not_a_constant` | 1 | 2026-09-02 |
| `tests/background/test_open_campaign_draw.py::test_may_rest_when_all_items_landed` | 1 | 2026-09-02 |
| `tests/background/test_open_campaign_draw.py::test_must_not_rest_with_open_campaign` | 1 | 2026-09-02 |
| `tests/background/test_open_campaign_draw.py::test_one_landed_rest_open_must_not_rest` | 1 | 2026-09-02 |
| `tests/background/test_open_question_register.py::test_corrupt_register_fails_closed_all_open` | 1 | 2026-09-02 |
| `tests/background/test_open_question_register.py::test_missing_register_fails_closed` | 1 | 2026-09-02 |
| `tests/background/test_open_question_register.py::test_open_when_absent_blocks__answered_unblocks__carried_still_blocks` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_a_collection_error_is_not_paged_as_a_daemon_lifecycle_regression` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_a_genuine_operational_failure_is_still_reported_as_a_regression` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_a_timed_out_signal_is_never_a_green` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_a_timed_out_signal_stamps_its_run_so_the_throttle_engages` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_a_timeout_is_not_filed_as_a_daemon_red_or_a_collection_block` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_absent_output_fails_LOUD_not_silent` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_force_bypasses_throttle` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_green_page_carries_no_failure_payload` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_persistent_red_does_not_block_a_simulated_content_publish` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_persistent_red_never_touches_publish_gate_state_or_scope` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_persistent_red_pages_exactly_once` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_persistent_red_reescalates_after_window_elapses` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_recovery_after_persistent_red_pages_once` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_red_page_names_the_failing_tests_not_just_the_return_code` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_red_then_green_flake_never_pages` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_runner_exception_is_swallowed_not_raised` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_single_green_result_is_clean_no_page` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_single_red_result_logs_but_does_not_page` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_the_blocked_signal_is_still_red_never_silently_green` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_the_real_runner_actually_captures_output` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_throttle_runs_again_after_interval_elapses` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_throttle_skips_before_interval_elapses` | 1 | 2026-09-02 |
| `tests/background/test_operational_layer_signal.py::test_unreadable_state_file_is_treated_as_due_not_silently_skipped` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_a_below_threshold_timeout_stays_silent` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_a_blocked_draw_does_not_send_the_worker_to_the_daemons` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_a_blocked_draw_with_no_named_files_says_so_rather_than_going_blank` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_a_blocked_signal_still_draws` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_a_genuine_red_still_gets_the_daemon_draw` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_a_record_written_after_head_gets_the_base_draw` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_a_record_written_at_the_same_second_as_head_gets_the_base_draw` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_a_record_written_before_head_leads_with_re_run_first` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_a_timed_out_signal_is_drawable_not_silent` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_an_unreadable_record_stamp_never_softens_the_draw[state0]` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_an_unreadable_record_stamp_never_softens_the_draw[state1]` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_an_unreadable_record_stamp_never_softens_the_draw[state2]` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_fires_just_above_threshold` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_fires_on_the_exact_overnight_state` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_git_unavailable_never_softens_the_draw` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_is_drained_and_gated_refuses_rest_while_persistent_red` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_self_refill_returns_it_above_product_lanes` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_silent_at_and_below_threshold` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_silent_on_green` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_silent_on_malformed_file` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_silent_on_missing_consecutive_red_key` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_silent_on_non_dict_json` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_silent_on_non_numeric_counter` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_still_silent_on_a_below_threshold_blocked_record` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_the_clause_cannot_resurrect_a_green_or_below_threshold_record` | 1 | 2026-09-02 |
| `tests/background/test_operational_red_persistent_draw.py::test_the_timeout_draw_names_a_duration_not_a_daemon_defect` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_axes_present_false_on_empty_and_absent` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_axes_present_true_on_ratified_axes` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_blocked_mints_level_forbids_rest_and_is_named` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_enumeration_shows_planner_drawable_when_axes_populated` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_in_progress_slug_partition_fail_closed_on_unmarked` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_is_drained_refuses_rest_when_planner_can_mint` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_pending_mints_detector_true_when_batch_in_staging` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_pending_mints_ignores_consumed_subdirs` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_planner_draw_fires_on_populated_axes` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_planner_rests_while_minted_batch_pending` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_rest_proof_ages_out_on_blocked_batch_past_max_age` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_rest_proof_max_age_does_not_apply_without_blocked_mints` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_rest_with_proof_MINTS_on_malformed_marker` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_rest_with_proof_MINTS_when_no_marker` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_rest_with_proof_REPLANS_when_a_mint_is_unblocked` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_rest_with_proof_REPLANS_when_axes_change` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_rest_with_proof_REPLANS_when_day_rolls` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_rest_with_proof_rests_when_marker_fresh_and_state_unchanged` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_self_refill_mints_when_lanes_empty_and_axes_populated` | 1 | 2026-09-02 |
| `tests/background/test_planner_rung.py::test_shadow_rail_flag_disables_planner` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::TestFrozenBaselineOutOfBandTrigger::test_spawns_detached_when_stale_and_never_runs_inline` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::TestLivenessPublishRefusesForeignSoil::test_foreign_seat_leaves_one_stderr_line_naming_the_refusal` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::TestLivenessPublishRefusesForeignSoil::test_foreign_seat_makes_no_git_calls_and_returns_false` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::TestLivenessPublishRefusesForeignSoil::test_the_import_call_bypass_is_closed_end_to_end` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::TestLivenessPublishRefusesForeignSoil::test_the_seat_is_checked_before_anything_else` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::TestRefreshPublishedLivenessOnSkip::test_due_but_phantom_push_does_not_record` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::TestRefreshPublishedLivenessOnSkip::test_due_commits_only_liveness_paths_and_records_push` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::TestRefreshPublishedLivenessOnSkip::test_nothing_to_commit_skips_push` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::TestRefreshPublishedLivenessOnSkip::test_throttled_is_a_noop` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_a_commit_timeout_is_not_recorded_as_nothing_to_commit` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_a_failed_publish_does_not_write_the_fingerprint` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_a_redirected_sim_runner_log_still_writes` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_a_repaired_projection_is_LANDED_and_it_lands_BEFORE_the_gate` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_a_successful_publish_still_writes_the_fingerprint` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_a_timed_out_publish_gate_blocks_the_commit` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_change_detection_gate_skips_identical_run_when_not_forced` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_commit_timeout_is_caught_and_does_not_crash_the_publish` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_fingerprint_roundtrip` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_force_republish_flag_bypasses_identical_fingerprint` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_force_republish_flag_consumed_exactly_once` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_gate_failure_log_tail_is_bounded` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_gate_never_skips_admin_event` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_gate_never_skips_when_git_hash_differs` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_gate_skips_identical_run` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_gate_skips_when_git_hash_matches_too` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_git_commit_push_commits_whole_generated_site_data_surface` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_git_commit_push_defers_push_within_throttle_window` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_git_commit_push_does_not_record_on_phantom_push` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_git_commit_push_no_push_recorded_if_commit_fails` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_git_commit_push_pushes_when_throttle_window_elapsed` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_green_publish_gate_logs_no_failure_payload` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_main_returns_1_for_missing_marker` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_main_returns_1_when_tests_fail` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_main_skips_when_lock_already_held` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_main_success_flow` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_parse_marker_extracts_git_hash_elapsed_json_path` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_push_due_false_within_throttle_window` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_push_due_true_after_throttle_window_elapses` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_push_due_true_on_malformed_file` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_red_publish_gate_captures_output_rather_than_discarding_it` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_red_publish_gate_logs_a_tail_even_with_no_summary_line` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_red_publish_gate_logs_the_blocking_test_node_ids` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_the_commit_runs_its_hook_chain_unbuffered` | 1 | 2026-09-02 |
| `tests/background/test_process_run_complete.py::test_update_latest_md_replaces_block` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestItFiresOnTheRealOutage::test_a_dead_runner_that_wrote_no_counter_still_draws` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestItFiresOnTheRealOutage::test_rest_is_refused_while_the_producer_is_down` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestItFiresOnTheRealOutage::test_self_refill_returns_it_above_the_product_lanes` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestItFiresOnTheRealOutage::test_the_draw_carries_the_diagnostic_not_just_the_count` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestItFiresOnTheRealOutage::test_the_recorded_2026_08_17_state_draws` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestItStaysSilentWhenItShould::test_a_director_hold_is_not_starvation` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestItStaysSilentWhenItShould::test_a_healthy_producer_draws_nothing` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestItStaysSilentWhenItShould::test_a_lone_flake_is_not_an_outage` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestItStaysSilentWhenItShould::test_a_malformed_state_file_does_not_raise_into_the_draw_ladder` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestItStaysSilentWhenItShould::test_a_single_failure_with_no_output_for_hours_is_still_starvation` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestItStaysSilentWhenItShould::test_a_young_streak_is_not_yet_drawable` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestItStaysSilentWhenItShould::test_an_absent_state_file_with_fresh_artefacts_draws_nothing` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestTheBlindnessesThisRungExistsToCover::test_rung_1_is_silent_on_an_empty_failure_list` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestTheBlindnessesThisRungExistsToCover::test_rung_1b_is_silent_while_the_daemon_is_merely_ALIVE` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestTheEpisodeGuardOnTheProducerState::test_only_a_terminal_SUCCESS_closes_the_episode` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestTheIndependenceLimb::test_a_later_successful_run_supersedes_a_stale_counter` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestTheIndependenceLimb::test_an_artefact_older_than_the_failures_does_not_supersede_them` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestTheIndependenceLimb::test_the_artefact_age_helper_reads_the_newest_not_the_first` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestTheRunnerSideBookkeeping::test_a_failure_starts_and_grows_the_streak` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestTheRunnerSideBookkeeping::test_a_success_clears_the_streak_so_the_rung_drains_itself` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestTheRunnerSideBookkeeping::test_the_streak_start_is_not_restamped_by_later_failures` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestTheUndiagnosedLimbIsSizedAgainstRealCADENCE::test_a_genuine_multi_hour_silence_still_draws` | 1 | 2026-09-02 |
| `tests/background/test_producer_starvation_draw.py::TestTheUndiagnosedLimbIsSizedAgainstRealCADENCE::test_a_normal_slow_publish_cycle_does_not_draw` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_a_clause_2_blocker_takes_the_product_side_slot_and_is_named` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_a_harness_lane_blocker_is_not_a_clause_2_product_substitution` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_a_product_only_grant_is_not_a_violation_and_owes_nothing` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_an_undebted_harness_grant_is_not_displaced_it_accrues_the_debt` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_an_unreadable_owed_ledger_is_named_in_the_line_not_silently_reset` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_r15_the_arm_does_not_move_with_staging_depth` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_r15_the_digest_line_can_never_be_suppressed` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_the_arm_adds_rather_than_displaces_when_the_fork_budget_has_room` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_the_arm_takes_the_slot_rather_than_widening_the_grant` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_the_digest_line_is_never_empty_on_any_path` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_the_digest_names_the_pair_actually_drawn` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_the_owed_harness_atom_forces_the_next_grants_product_side` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_the_owed_ledger_is_bounded` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_the_stale_record_of_a_previous_grant_cannot_be_reported_as_this_cycles_pair` | 1 | 2026-09-02 |
| `tests/background/test_product_interleave.py::test_two_harness_atoms_and_no_product_atom_is_named_a_violation` | 1 | 2026-09-02 |
| `tests/background/test_publish_decoupling_exit.py::test_a_green_remainder_run_still_publishes_no_reds` | 1 | 2026-09-02 |
| `tests/background/test_publish_decoupling_exit.py::test_a_red_gate_publishes_the_banner_and_never_the_content` | 1 | 2026-09-02 |
| `tests/background/test_publish_decoupling_exit.py::test_an_unreadable_remainder_transcript_is_a_red_not_an_all_clear` | 1 | 2026-09-02 |
| `tests/background/test_publish_decoupling_exit.py::test_the_annotation_pass_cannot_block_a_publish` | 1 | 2026-09-02 |
| `tests/background/test_publish_decoupling_exit.py::test_the_banner_publisher_refuses_on_foreign_soil` | 1 | 2026-09-02 |
| `tests/background/test_publish_freshness.py::test_a_fresh_publish_reads_as_publishing` | 1 | 2026-09-02 |
| `tests/background/test_publish_freshness.py::test_a_healthy_tick_does_not_make_a_frozen_publish_look_fresh` | 1 | 2026-09-02 |
| `tests/background/test_publish_freshness.py::test_an_unmeasurable_age_is_UNKNOWN_and_never_fresh` | 1 | 2026-09-02 |
| `tests/background/test_publish_freshness.py::test_content_moving_by_luck_is_not_a_publishing_pipeline` | 1 | 2026-09-02 |
| `tests/background/test_publish_freshness.py::test_the_eighteen_hour_freeze_reads_as_stale` | 1 | 2026-09-02 |
| `tests/background/test_publish_freshness.py::test_the_heartbeat_carries_the_freshness_block` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_alarm_carries_the_episode_not_just_the_window` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_alarm_cites_linked_findings_and_persists_them_for_the_draw` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_an_exonerated_finding_is_dropped_from_the_citation_for_that_red` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_an_exoneration_for_another_red_still_leaves_the_finding_cited` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_an_exoneration_naming_a_path_that_does_not_exist_does_not_suppress` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_an_unexonerated_finding_is_cited_exactly_as_before` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_archived_findings_are_not_cited` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_citation_is_bounded` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_cooldown_suppresses_repeat_alerts_then_re_arms` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_does_not_fire_after_recovery` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_episode_counter_survives_the_window_trim_but_clears_on_recovery` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_failures_outside_the_window_do_not_count` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_fires_on_n_consecutive_failures` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_markers_pending_is_measured_independently_of_the_gate_state` | 1 | 2026-09-02 |
| `tests/background/test_publish_gate_alert.py::test_mutation_a_broken_threshold_would_be_caught` | 1 | 2026-09-02 |

… 430 more not listed here. **Every one is in `docs/observability/head_red_observed.json`**, which is the store this table is rendered from.

## By module

Where a whole module is red, the cause is usually one thing — a conftest, an import, a fixture — and not N separate defects.

| module | red |
|---|---:|
| `tests/background/test_finding_severity.py` | 63 |
| `tests/background/test_publish_gate_wedge_draw.py` | 58 |
| `tests/background/test_process_run_complete.py` | 44 |
| `tests/background/test_shared_primitive_census.py` | 38 |
| `tests/background/test_operational_red_persistent_draw.py` | 26 |
| `tests/background/test_sanity_daemon.py` | 26 |
| `tests/background/test_operational_layer_signal.py` | 23 |
| `tests/background/test_producer_starvation_draw.py` | 23 |
| `tests/background/test_publish_gate_alert.py` | 22 |
| `tests/background/test_forward_discovery_draw.py` | 21 |
| `tests/background/test_planner_rung.py` | 20 |
| `tests/background/test_seat_continuity.py` | 18 |
| `tests/background/test_publish_step_ledger.py` | 16 |
| `tests/background/test_resource_headroom.py` | 16 |
| `tests/background/test_staging_two_rooms_repair.py` | 16 |
| `tests/background/test_gate_authorization.py` | 15 |
| `tests/background/test_product_interleave.py` | 15 |
| `tests/background/test_pw4_episode_guards.py` | 15 |
| `tests/background/test_seat_work_in_hand.py` | 15 |
| `tests/background/test_staging_disposition.py` | 14 |
| `tests/background/test_mint_permission_block_abolished.py` | 13 |
| `tests/background/test_publish_gate_red_census.py` | 13 |
| `tests/background/test_publish_provenance.py` | 12 |
| `tests/background/test_run_rotation.py` | 12 |
| `tests/background/test_staging_rooms.py` | 12 |
| `tests/background/test_naive_organ.py` | 11 |
| `tests/background/test_notification_digest.py` | 11 |
| `tests/background/test_publish_gate_blocking_payload.py` | 11 |
| `tests/background/test_sim_runner_publish_gate_outcome.py` | 11 |
| `tests/background/test_inbound_secret_redaction.py` | 10 |
| `tests/background/test_publisher_deadline_exceeds_its_gate.py` | 10 |
| `tests/background/test_finding_classes.py` | 9 |
| `tests/background/test_rolling_ssp_refresh.py` | 9 |
| `tests/background/test_seat_continuation.py` | 9 |
| `tests/background/test_gap_register_scan.py` | 8 |
| `tests/background/test_publish_gate_subject_is_head.py` | 8 |
| `tests/background/test_rotation_curriculum_binding.py` | 8 |
| `tests/background/test_harden_rung_pass_ceiling.py` | 7 |
| `tests/background/test_misparked_campaign_draw.py` | 7 |
| `tests/background/test_sim_runner_stderr_capture.py` | 7 |

## Run history

| run | red | passed |
|---|---:|---:|
| 2026-09-02T04:30:02+00:00 | 830 | unreadable |
