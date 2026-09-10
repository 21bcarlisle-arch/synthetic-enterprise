# [REGISTER] Tests red at HEAD

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

**THIS IS A REGISTER, NOT A QUEUE ITEM. Do not archive it.** It is re-rendered in place by `background/head_red_register` on every HEAD-green census run. You action it by MAKING A TEST GREEN, or by adding that test BY NAME to `docs/observability/head_red_baseline.json` with a reason. There is no third exit and no blanket disposition: one paragraph must not be able to retire 830 subjects, which is the wallpaper this register exists to replace.

## The count, with each number's population named

| | |
|---|---:|
| red at HEAD, last run | **43** |
| accepted by a person, with a reason | 0 |
| **owed — neither fixed nor accepted** | **43** |
| passed, same run | 33697 |

Last run **2026-09-10T03:46:53+00:00** at HEAD `dceedff0f`.

Causes that run: AssertionError x35, TypeError x2, ValueError x2, IndexError x1

## The 43 owed, longest-standing first

`runs` is consecutive census runs this test has been red — the recurrence signal, the same argument `class_debt` makes for instance count. The longest-standing red here has survived **10 run(s)**.

| test | runs red | first seen |
|---|---:|---|
| `tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py::test_no_tree_scanning_test_passes_on_an_empty_population` | 10 | 2026-09-02 |
| `tests/simulation/test_home_move_undeliverable_win.py::test_a_won_home_mover_WITH_a_successor_activates_it_and_does_not_go_to_market` | 10 | 2026-09-02 |
| `tests/simulation/test_home_move_undeliverable_win.py::test_a_won_home_mover_with_no_successor_still_goes_to_market` | 10 | 2026-09-02 |
| `tests/simulation/test_price_response_curve_position_split.py::test_within_a_price_side_the_response_moves_monotonically_with_perceived_pounds` | 10 | 2026-09-02 |
| `tests/tools/test_bill_correctness_addendum_defect4.py::test_billed_total_never_less_than_gross_margin_for_any_real_customer_year` | 10 | 2026-09-02 |
| `tests/tools/test_billing_tab_fix.py::test_closed_account_notice_date_tracks_the_record_not_a_constant` | 10 | 2026-09-02 |
| `tests/tools/test_billing_tab_fix.py::test_closed_account_notice_real_churned_customer_c1` | 10 | 2026-09-02 |
| `tests/tools/test_evidence_pages.py::test_page_is_reproducible_from_the_sources` | 10 | 2026-09-02 |
| `tests/tools/test_year_spotlight.py::test_crisis_year_2022_worse_than_2020` | 10 | 2026-09-02 |
| `tests/background/test_live_ledger_guard.py::test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed` | 9 | 2026-09-02 |
| `tests/background/test_seat_guard_daemons.py::TestStructuralLock::test_every_main_entrypoint_is_guarded` | 9 | 2026-09-02 |
| `tests/tools/test_internal_seam_verifier.py::test_current_tree_passes` | 8 | 2026-09-03 |
| `tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned` | 6 | 2026-09-04 |
| `tests/background/test_class_debt.py::test_an_accruing_class_outranks_a_finding_and_yields_to_a_persons_ask` | 4 | 2026-09-07 |
| `tests/background/test_class_debt.py::test_an_accruing_undecided_class_is_work` | 4 | 2026-09-07 |
| `tests/background/test_finding_severity.py::test_the_staging_root_has_no_false_discharges` | 4 | 2026-09-06 |
| `tests/tools/test_maturity_map_store.py::test_the_split_predicate_agrees_with_where_every_atom_actually_SITS` | 4 | 2026-09-04 |
| `tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py::test_no_committed_store_credits_a_falsifier_the_repository_does_not_have` | 3 | 2026-09-05 |
| `tests/simulation/test_phase30b_gas_policy_costs.py::test_gas_ccl_clamps_post_2024` | 3 | 2026-09-08 |
| `tests/simulation/test_weather_cell_siting.py::test_derive_reproduces_the_committed_artefact` | 3 | 2026-09-08 |
| `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py::test_no_committed_discharge_cites_a_falsifier_the_repository_does_not_have` | 2 | 2026-09-09 |
| `tests/background/test_staging_root_resurrection_watch.py::test_the_landing_tool_actually_brackets_its_gate` | 2 | 2026-09-09 |
| `tests/harness/test_premise_two_level.py::test_MEASURED_population_values` | 2 | 2026-09-09 |
| `tests/harness/test_premise_two_level.py::test_the_L1_1_BREACH_WAS_the_WATER_HEATER_and_the_LOAD_SET_CLOSED_IT` | 2 | 2026-09-09 |
| `tests/harness/test_premise_two_level.py::test_the_REPAIR_ITSELF_fires_its_own_named_defect` | 2 | 2026-09-09 |
| `tests/harness/test_premise_two_level.py::test_the_WATER_HEATER_netting_is_a_LOAD_SET_repair_and_not_a_LOOSENING` | 2 | 2026-09-09 |
| `tests/harness/test_premise_two_level.py::test_the_worst_L1_1_cell_is_the_worst_MARGIN_not_the_lowest_RAW_value` | 2 | 2026-09-09 |
| `tests/tools/test_console_capture_lapse.py::test_THE_CHECK_READS_THE_SAME_ROOM_THE_WRITER_WRITES_TO` | 2 | 2026-09-09 |
| `tests/tools/test_couple_fabric.py::test_the_OLD_WHOLE_METER_reading_was_FAIL_OPEN_on_a_BEHAVIOURALLY_FLAT_home` | 2 | 2026-09-09 |
| `tests/tools/test_couple_fabric.py::test_the_money_consequence_is_AFFINE_in_the_unit_rate_for_a_fixed_decision` | 2 | 2026-09-09 |
| `tests/tools/test_seat_reply_capture.py::test_THE_WINDOW_THE_DIRECTOR_NAMED_IS_A_FINDING` | 2 | 2026-09-09 |
| `tests/tools/test_the_value_arms_pages_undriven_pointers.py::test_every_untied_here_relative_literal_has_a_recipe_that_drives_its_branch` | 2 | 2026-09-09 |
| `tests/background/test_one_answer_standing_on_several_census_rows.py::test_a_declared_provenance_sentence_may_stand_on_many_rows` | 1 | 2026-09-10 |
| `tests/background/test_one_answer_standing_on_several_census_rows.py::test_a_null_field_does_not_fall_open` | 1 | 2026-09-10 |
| `tests/background/test_one_answer_standing_on_several_census_rows.py::test_a_short_repeated_phrase_is_not_a_finding` | 1 | 2026-09-10 |
| `tests/background/test_one_answer_standing_on_several_census_rows.py::test_an_unreadable_register_does_not_fabricate_a_refusal` | 1 | 2026-09-10 |
| `tests/background/test_one_answer_standing_on_several_census_rows.py::test_one_claim_on_two_rows_is_refused_and_the_refusal_names_both_rows` | 1 | 2026-09-10 |
| `tests/background/test_one_answer_standing_on_several_census_rows.py::test_one_row_keeping_its_own_claim_is_not_refused` | 1 | 2026-09-10 |
| `tests/background/test_one_answer_standing_on_several_census_rows.py::test_the_live_registers_allowlist_is_reachable_and_load_bearing` | 1 | 2026-09-10 |
| `tests/background/test_one_answer_standing_on_several_census_rows.py::test_the_same_claim_in_why_and_in_loader_is_caught_in_both_fields` | 1 | 2026-09-10 |
| `tests/tools/test_site_freshness_stamps.py::test_claim_review_is_allowed_to_be_newer_than_the_data` | 1 | 2026-09-10 |
| `tests/tools/test_the_value_arms_pages_undriven_pointers.py::test_a_sentence_no_door_renders_is_reported_rather_than_read_as_clean` | 1 | 2026-09-10 |
| `tests/tools/test_the_value_arms_pages_undriven_pointers.py::test_every_undriven_pointer_is_true_from_the_region_it_lands_in` | 1 | 2026-09-10 |

## By module

Where a whole module is red, the cause is usually one thing — a conftest, an import, a fixture — and not N separate defects.

| module | red |
|---|---:|
| `tests/background/test_one_answer_standing_on_several_census_rows.py` | 8 |
| `tests/harness/test_premise_two_level.py` | 5 |
| `tests/tools/test_the_value_arms_pages_undriven_pointers.py` | 3 |
| `tests/background/test_class_debt.py` | 2 |
| `tests/simulation/test_home_move_undeliverable_win.py` | 2 |
| `tests/tools/test_billing_tab_fix.py` | 2 |
| `tests/tools/test_couple_fabric.py` | 2 |
| `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py` | 1 |
| `tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py` | 1 |
| `tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py` | 1 |
| `tests/background/test_finding_severity.py` | 1 |
| `tests/background/test_live_ledger_guard.py` | 1 |
| `tests/background/test_seat_guard_daemons.py` | 1 |
| `tests/background/test_self_clearing_alarm_census.py` | 1 |
| `tests/background/test_staging_root_resurrection_watch.py` | 1 |
| `tests/simulation/test_phase30b_gas_policy_costs.py` | 1 |
| `tests/simulation/test_price_response_curve_position_split.py` | 1 |
| `tests/simulation/test_weather_cell_siting.py` | 1 |
| `tests/tools/test_bill_correctness_addendum_defect4.py` | 1 |
| `tests/tools/test_console_capture_lapse.py` | 1 |
| `tests/tools/test_evidence_pages.py` | 1 |
| `tests/tools/test_internal_seam_verifier.py` | 1 |
| `tests/tools/test_maturity_map_store.py` | 1 |
| `tests/tools/test_seat_reply_capture.py` | 1 |
| `tests/tools/test_site_freshness_stamps.py` | 1 |
| `tests/tools/test_year_spotlight.py` | 1 |

## Run history

| run | red | passed |
|---|---:|---:|
| 2026-09-02T04:30:02+00:00 | 830 | not written by a completed census run |
| 2026-09-02T13:18:33+00:00 | 49 | 30479 |
| 2026-09-03T03:37:35+00:00 | 19 | 30780 |
| 2026-09-04T03:41:00+00:00 | 25 | 31012 |
| 2026-09-05T03:40:02+00:00 | 21 | 31673 |
| 2026-09-06T03:42:16+00:00 | 29 | 32311 |
| 2026-09-07T03:35:32+00:00 | 28 | 32691 |
| 2026-09-08T03:40:01+00:00 | 25 | 33110 |
| 2026-09-09T03:44:39+00:00 | 35 | 33504 |
| 2026-09-10T03:46:53+00:00 | 43 | 33697 |
