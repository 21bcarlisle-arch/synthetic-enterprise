# [REGISTER] Tests red at HEAD

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

**THIS IS A REGISTER, NOT A QUEUE ITEM. Do not archive it.** It is re-rendered in place by `background/head_red_register` on every HEAD-green census run. You action it by MAKING A TEST GREEN, or by adding that test BY NAME to `docs/observability/head_red_baseline.json` with a reason. There is no third exit and no blanket disposition: one paragraph must not be able to retire 830 subjects, which is the wallpaper this register exists to replace.

## The count, with each number's population named

| | |
|---|---:|
| red at HEAD, last run | **21** |
| accepted by a person, with a reason | 0 |
| **owed — neither fixed nor accepted** | **21** |
| passed, same run | 31673 |

Last run **2026-09-05T03:40:02+00:00** at HEAD `2d44c42f5`.

Causes that run: AssertionError x13, KeyError x5, IndexError x1

## The 21 owed, longest-standing first

`runs` is consecutive census runs this test has been red — the recurrence signal, the same argument `class_debt` makes for instance count. The longest-standing red here has survived **5 run(s)**.

| test | runs red | first seen |
|---|---:|---|
| `tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py::test_no_tree_scanning_test_passes_on_an_empty_population` | 5 | 2026-09-02 |
| `tests/simulation/test_home_move_undeliverable_win.py::test_a_won_home_mover_WITH_a_successor_activates_it_and_does_not_go_to_market` | 5 | 2026-09-02 |
| `tests/simulation/test_home_move_undeliverable_win.py::test_a_won_home_mover_with_no_successor_still_goes_to_market` | 5 | 2026-09-02 |
| `tests/simulation/test_price_response_curve_position_split.py::test_within_a_price_side_the_response_moves_monotonically_with_perceived_pounds` | 5 | 2026-09-02 |
| `tests/tools/test_bill_correctness_addendum_defect4.py::test_billed_total_never_less_than_gross_margin_for_any_real_customer_year` | 5 | 2026-09-02 |
| `tests/tools/test_billing_tab_fix.py::test_closed_account_notice_date_tracks_the_record_not_a_constant` | 5 | 2026-09-02 |
| `tests/tools/test_billing_tab_fix.py::test_closed_account_notice_real_churned_customer_c1` | 5 | 2026-09-02 |
| `tests/tools/test_capability_index.py::test_the_live_register_rules_on_every_live_orphan` | 5 | 2026-09-02 |
| `tests/tools/test_evidence_pages.py::test_page_is_reproducible_from_the_sources` | 5 | 2026-09-02 |
| `tests/tools/test_year_spotlight.py::test_crisis_year_2022_worse_than_2020` | 5 | 2026-09-02 |
| `tests/background/test_live_ledger_guard.py::test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed` | 4 | 2026-09-02 |
| `tests/background/test_seat_guard_daemons.py::TestStructuralLock::test_every_main_entrypoint_is_guarded` | 4 | 2026-09-02 |
| `tests/simulation/test_dd_level_collection_book.py::test_amount_equals_dd2_collected_by_construction` | 3 | 2026-09-03 |
| `tests/simulation/test_dd_level_collection_book.py::test_collection_is_fixed_within_year_though_bills_vary` | 3 | 2026-09-03 |
| `tests/simulation/test_dd_level_collection_book.py::test_collection_lands_on_staggered_payment_day` | 3 | 2026-09-03 |
| `tests/simulation/test_dd_level_collection_book.py::test_re_estimation_moves_the_fixed_amount_between_years` | 3 | 2026-09-03 |
| `tests/simulation/test_dd_level_collection_book.py::test_sample_schedules_bounded` | 3 | 2026-09-03 |
| `tests/simulation/test_dd_level_collection_book.py::test_summary_totals_and_count` | 3 | 2026-09-03 |
| `tests/tools/test_internal_seam_verifier.py::test_current_tree_passes` | 3 | 2026-09-03 |
| `tests/tools/test_maturity_map_store.py::test_the_split_predicate_agrees_with_where_every_atom_actually_SITS` | 2 | 2026-09-04 |
| `tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py::test_no_committed_store_credits_a_falsifier_the_repository_does_not_have` | 1 | 2026-09-05 |

## By module

Where a whole module is red, the cause is usually one thing — a conftest, an import, a fixture — and not N separate defects.

| module | red |
|---|---:|
| `tests/simulation/test_dd_level_collection_book.py` | 6 |
| `tests/simulation/test_home_move_undeliverable_win.py` | 2 |
| `tests/tools/test_billing_tab_fix.py` | 2 |
| `tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py` | 1 |
| `tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py` | 1 |
| `tests/background/test_live_ledger_guard.py` | 1 |
| `tests/background/test_seat_guard_daemons.py` | 1 |
| `tests/simulation/test_price_response_curve_position_split.py` | 1 |
| `tests/tools/test_bill_correctness_addendum_defect4.py` | 1 |
| `tests/tools/test_capability_index.py` | 1 |
| `tests/tools/test_evidence_pages.py` | 1 |
| `tests/tools/test_internal_seam_verifier.py` | 1 |
| `tests/tools/test_maturity_map_store.py` | 1 |
| `tests/tools/test_year_spotlight.py` | 1 |

## Run history

| run | red | passed |
|---|---:|---:|
| 2026-09-02T04:30:02+00:00 | 830 | not written by a completed census run |
| 2026-09-02T13:18:33+00:00 | 49 | 30479 |
| 2026-09-03T03:37:35+00:00 | 19 | 30780 |
| 2026-09-04T03:41:00+00:00 | 25 | 31012 |
| 2026-09-05T03:40:02+00:00 | 21 | 31673 |
