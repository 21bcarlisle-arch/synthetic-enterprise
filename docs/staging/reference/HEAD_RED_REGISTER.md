# [REGISTER] Tests red at HEAD

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

**THIS IS A REGISTER, NOT A QUEUE ITEM. Do not archive it.** It is re-rendered in place by `background/head_red_register` on every HEAD-green census run. You action it by MAKING A TEST GREEN, or by adding that test BY NAME to `docs/observability/head_red_baseline.json` with a reason. There is no third exit and no blanket disposition: one paragraph must not be able to retire 830 subjects, which is the wallpaper this register exists to replace.

## The count, with each number's population named

| | |
|---|---:|
| red at HEAD, last run | **41** |
| accepted by a person, with a reason | 0 |
| **owed — neither fixed nor accepted** | **41** |
| passed, same run | 35055 |

Last run **2026-09-22T04:23:51+00:00** at HEAD `f705248ae`.

Causes that run: AssertionError x29, KeyError x6, IndexError x1, ValueError x1

## The 41 owed, longest-standing first

`runs` is consecutive census runs this test has been red — the recurrence signal, the same argument `class_debt` makes for instance count. The longest-standing red here has survived **19 run(s)**.

| test | runs red | first seen |
|---|---:|---|
| `tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py::test_no_tree_scanning_test_passes_on_an_empty_population` | 19 | 2026-09-02 |
| `tests/simulation/test_home_move_undeliverable_win.py::test_a_won_home_mover_WITH_a_successor_activates_it_and_does_not_go_to_market` | 19 | 2026-09-02 |
| `tests/simulation/test_home_move_undeliverable_win.py::test_a_won_home_mover_with_no_successor_still_goes_to_market` | 19 | 2026-09-02 |
| `tests/simulation/test_price_response_curve_position_split.py::test_within_a_price_side_the_response_moves_monotonically_with_perceived_pounds` | 19 | 2026-09-02 |
| `tests/tools/test_bill_correctness_addendum_defect4.py::test_billed_total_never_less_than_gross_margin_for_any_real_customer_year` | 19 | 2026-09-02 |
| `tests/tools/test_billing_tab_fix.py::test_closed_account_notice_date_tracks_the_record_not_a_constant` | 19 | 2026-09-02 |
| `tests/tools/test_billing_tab_fix.py::test_closed_account_notice_real_churned_customer_c1` | 19 | 2026-09-02 |
| `tests/tools/test_evidence_pages.py::test_page_is_reproducible_from_the_sources` | 19 | 2026-09-02 |
| `tests/tools/test_year_spotlight.py::test_crisis_year_2022_worse_than_2020` | 19 | 2026-09-02 |
| `tests/tools/test_internal_seam_verifier.py::test_current_tree_passes` | 17 | 2026-09-03 |
| `tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py::test_no_committed_store_credits_a_falsifier_the_repository_does_not_have` | 12 | 2026-09-05 |
| `tests/simulation/test_phase30b_gas_policy_costs.py::test_gas_ccl_clamps_post_2024` | 12 | 2026-09-08 |
| `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py::test_no_committed_discharge_cites_a_falsifier_the_repository_does_not_have` | 11 | 2026-09-09 |
| `tests/harness/test_premise_two_level.py::test_MEASURED_population_values` | 11 | 2026-09-09 |
| `tests/harness/test_premise_two_level.py::test_the_L1_1_BREACH_WAS_the_WATER_HEATER_and_the_LOAD_SET_CLOSED_IT` | 11 | 2026-09-09 |
| `tests/harness/test_premise_two_level.py::test_the_REPAIR_ITSELF_fires_its_own_named_defect` | 11 | 2026-09-09 |
| `tests/harness/test_premise_two_level.py::test_the_WATER_HEATER_netting_is_a_LOAD_SET_repair_and_not_a_LOOSENING` | 11 | 2026-09-09 |
| `tests/harness/test_premise_two_level.py::test_the_worst_L1_1_cell_is_the_worst_MARGIN_not_the_lowest_RAW_value` | 11 | 2026-09-09 |
| `tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py::test_no_claim_about_the_drawn_population_arrives_silent` | 9 | 2026-09-11 |
| `tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py::test_every_issued_bill_agrees_with_the_sum_of_its_own_printed_components` | 9 | 2026-09-04 |
| `tests/architecture/test_a_commons_artefact_can_tell_when_its_source_was_revised.py::test_every_verdict_can_be_recorded[cannot_tell]` | 8 | 2026-09-15 |
| `tests/architecture/test_a_commons_artefact_can_tell_when_its_source_was_revised.py::test_every_verdict_can_be_recorded[superseded]` | 8 | 2026-09-15 |
| `tests/tools/test_every_promote_target_producer_declares_its_run_identity.py::test_the_producer_declares_which_of_its_fields_are_its_run_identity[tools/run_value_cycle_ab.py-producing_commit]` | 7 | 2026-09-16 |
| `tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py::test_the_vat_charged_on_every_catchup_bill_matches_the_NET_base_across_the_real_book` | 6 | 2026-09-17 |
| `tests/tools/test_a_published_surface_is_reproducible_from_its_committed_input.py::test_the_published_customer_book_is_reproducible_from_the_run_output_committed_beside_it` | 6 | 2026-09-17 |
| `tests/background/test_suppression_lint.py::test_live_tree_passes` | 5 | 2026-09-18 |
| `tests/saas/test_w2_13_property_people_count.py::test_ons_shares_agree_across_the_wall` | 5 | 2026-09-18 |
| `tests/tools/test_abolished_block_classes.py::test_guard_a_on_the_real_map_is_clean` | 4 | 2026-09-19 |
| `tests/tools/test_abolished_block_classes.py::test_the_LIVE_map_carries_no_stale_block_claim` | 4 | 2026-09-19 |
| `tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py::test_a_unanimous_family_that_reads_against_the_company_says_so` | 4 | 2026-09-19 |
| `tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py::test_both_verdicts_are_reachable_over_real_floors_on_this_disk` | 4 | 2026-09-19 |
| `tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py::test_each_leg_is_graded_at_its_own_familys_bar_and_over_its_own_rows` | 4 | 2026-09-19 |
| `tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py::test_every_bounded_contrast_reaches_a_reading_of_its_own` | 4 | 2026-09-19 |
| `tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py::test_the_level_leg_states_its_sign_because_its_own_family_determines_one` | 4 | 2026-09-19 |
| `tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py::test_the_selection_leg_reads_the_same_on_both_routes` | 4 | 2026-09-19 |
| `tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py::test_the_split_verdict_says_the_level_is_what_can_be_called` | 4 | 2026-09-19 |
| `tests/simulation/test_the_gas_leg_rolls_onto_the_cap_like_the_electricity_one.py::test_the_opening_term_is_fixed_on_both_fuels` | 3 | 2026-09-20 |
| `tests/tools/test_a_published_feed_matches_what_its_generator_would_produce.py::test_a_candidate_standpoint_is_observed_from_the_feed_not_asserted` | 3 | 2026-09-20 |
| `tests/tools/test_a_published_feed_matches_what_its_generator_would_produce.py::test_a_feed_checkable_at_its_own_commit_is_promoted` | 3 | 2026-09-20 |
| `tests/tools/test_a_published_feed_matches_what_its_generator_would_produce.py::test_every_covered_feed_is_what_its_generator_produces` | 3 | 2026-09-20 |
| `tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py::test_THE_TWO_GUARDS_ARE_GRADED_AT_THE_FUNCTION_BECAUSE_THE_READER_CANNOT_REACH_THEM` | 1 | 2026-09-22 |

## By module

Where a whole module is red, the cause is usually one thing — a conftest, an import, a fixture — and not N separate defects.

| module | red |
|---|---:|
| `tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py` | 7 |
| `tests/harness/test_premise_two_level.py` | 5 |
| `tests/tools/test_a_published_feed_matches_what_its_generator_would_produce.py` | 3 |
| `tests/architecture/test_a_commons_artefact_can_tell_when_its_source_was_revised.py` | 2 |
| `tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py` | 2 |
| `tests/simulation/test_home_move_undeliverable_win.py` | 2 |
| `tests/tools/test_abolished_block_classes.py` | 2 |
| `tests/tools/test_billing_tab_fix.py` | 2 |
| `tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py` | 1 |
| `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py` | 1 |
| `tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py` | 1 |
| `tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py` | 1 |
| `tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py` | 1 |
| `tests/background/test_suppression_lint.py` | 1 |
| `tests/saas/test_w2_13_property_people_count.py` | 1 |
| `tests/simulation/test_phase30b_gas_policy_costs.py` | 1 |
| `tests/simulation/test_price_response_curve_position_split.py` | 1 |
| `tests/simulation/test_the_gas_leg_rolls_onto_the_cap_like_the_electricity_one.py` | 1 |
| `tests/tools/test_a_published_surface_is_reproducible_from_its_committed_input.py` | 1 |
| `tests/tools/test_bill_correctness_addendum_defect4.py` | 1 |
| `tests/tools/test_every_promote_target_producer_declares_its_run_identity.py` | 1 |
| `tests/tools/test_evidence_pages.py` | 1 |
| `tests/tools/test_internal_seam_verifier.py` | 1 |
| `tests/tools/test_year_spotlight.py` | 1 |

## Run history

| run | red | passed |
|---|---:|---:|
| 2026-09-06T03:42:16+00:00 | 29 | 32311 |
| 2026-09-07T03:35:32+00:00 | 28 | 32691 |
| 2026-09-08T03:40:01+00:00 | 25 | 33110 |
| 2026-09-09T03:44:39+00:00 | 35 | 33504 |
| 2026-09-10T03:46:53+00:00 | 43 | 33697 |
| 2026-09-11T03:46:20+00:00 | 37 | 33826 |
| 2026-09-15T08:47:41+00:00 | 40 | 33825 |
| 2026-09-16T04:02:53+00:00 | 37 | 34078 |
| 2026-09-17T04:01:52+00:00 | 67 | 34292 |
| 2026-09-18T04:20:55+00:00 | 41 | 34588 |
| 2026-09-19T04:26:36+00:00 | 41 | 34757 |
| 2026-09-20T04:27:40+00:00 | 48 | 34887 |
| 2026-09-21T08:59:33+00:00 | 48 | 34887 |
| 2026-09-22T04:23:51+00:00 | 41 | 35055 |
