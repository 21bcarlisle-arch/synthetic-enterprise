**Severity:** BLOCKING · **Lane:** H_harness (`tools/pre_commit_test_gate.py` selection) · **Epoch:** 3 · **Atom:** `unminted`
**Evidence:** `docs/staging/reference/HEAD_RED_REGISTER.md` (the 2026-10-02 run at `3b7a2ae19`, 47 owed)

# The head reds' turning commits, and why the gate did not select them

**2026-10-04, autonomous worker, Lane 0 claim `the-head-red-register-names-the-commit-and-the-selection-miss`.**

## What was measured, and what was not

The register's 47 owed reds come from the census of 2026-10-02 at `3b7a2ae19`. Every reading below
was taken in a locked, detached worktree of `origin/main` (`4196e40c8`). Nothing was read from the
shared tree.

1. **All 47 at origin.** 10 are still red and 37 are green. The 10 were run twice, once inside a
   `launch_long_job` unit and once directly, and they are red both ways.
2. **The 37 at `3b7a2ae19`.** 33 reproduce red at that commit. **4 are green there on a direct
   run**, so no commit turned them red; they went red only inside the census unit. Those 4 are
   `test_net_new_acquisition::test_the_ceiling_still_fits_the_peak_systemds_own_journal_reports_today`,
   `test_phase_c_household_demand::...::test_c4_solar_reduces_multiplier` and both nodes of
   `test_the_registry_eac_rewrite_reaches_the_dd_opening`. The census counted
   `LaunchRefused x4` that night. That the 4 are those 4 is **likely, not shown**, because the store
   does not keep a cause per test.
3. **Bisect.** Every red first seen on or after 2026-09-17 was bisected, grouped by test file and
   first-seen window: 25 groups, 40 nodes. Each search runs from the census run before the red to
   the run that first saw it, along `--first-parent`. Where the turning commit was a merge, the
   search went down its second parent. Where that landed on a merge too, both of that merge's parents
   were tested.
4. **The selection.** For each turning commit, `tools/pre_commit_test_gate.select_targets` was
   called **as it stood at that commit**, on that commit's diff against its first parent. That is
   the gate's own answer to which tests to run, not a reconstruction of it.
5. **Gate receipts.** Every turning commit carries a `[surgical-land receipt]` with `gate-rc: 0`.
   **The gate ran on all 17 and passed every one.** In no case was it bypassed. The tests that went
   red simply were not in what it ran, except in one case (row M2).

**Not bisected:** the 3 reds first seen before 2026-09-17 (`test_evidence_pages::test_page_is_reproducible_from_the_sources`,
`test_self_clearing_alarm_census::test_every_live_hit_is_dispositioned`,
`test_maturity_map_store::test_the_split_predicate_agrees_with_where_every_atom_actually_SITS`).
They fall outside this item's window, and all three are **green at origin**.

## The table: 40 nodes, 17 turning commits, a cause on every row

"Sel" is whether the gate's own selection at the turning commit contained the red test file. "Now"
is the test's state at `origin/main` `4196e40c8`.

| # | red test file (nodes) | turning commit | sel | cause | now |
|---|---|---|---|---|---|
| S1 | `background/test_a_relaunch_cannot_erase_the_death_it_follows` (3) | `b50a03519` launch refuses without `--peak-mb` | no | **stem mismatch**: changed `launch_long_job.py`; tests named for the aspect, not `test_launch_long_job*` | **RED** |
| S2 | `background/test_an_unreadable_launch_register_is_never_an_empty_board` (1) | `b50a03519` | no | **stem mismatch**: same commit, same module | **RED** |
| S3 | `background/test_the_census_lost_five_hits_to_the_parameter_seam` (1) | `2d3b87a6b` lock the claim stores | no | **stem mismatch**: `seat_work_in_hand.py` now leaves `claims.json.lock`; the test that lists the store directory is named for another subject | **RED** |
| S4 | `simulation/test_policy_cost_coverage` (1) | `6f5bb8b68` 2025 standing charge | no | **stem mismatch**: changed `policy_costs.py`; the gate globs `test_policy_costs*`, the test is `test_policy_cost_coverage` (singular) | **RED** |
| S5 | `company/finance/test_bad_debt_reconciliation` (1) | `2bb03a094` P&L write-off over issued bills | no | **stem mismatch**: changed `bill_assembly.py` / `generate_billing_ledger.py`; consumer test named for another module (`KeyError: 'period_start'`) | green |
| S6 | `simulation/test_net_new_acquisition` (2) | `3bf64c4e7` registry EAC from own reads | no | **stem mismatch**: changed `fabric_demand_path.py`, `run_phase2b.py` | green |
| S7 | `test_nh_payment_behaviour_wiring` (2) | `fc390b918` churn belief hears household size | no | **stem mismatch**: changed `company/crm/churn_model.py` | green |
| S8 | `tools/test_evidence_pages` (1: `..._publish_cycle_refreshes_...`) | `7e9c2c935` publisher clean-tree checkout | no | **stem mismatch**: changed `process_run_complete.py` | green |
| W1 | `architecture/test_switching_rate_commons` (8) | `c3939e7b1` PB4 swap, arms retaken in world `cf823b18` | no | **world digest**: the commit moved the world and its committed artefacts (`site/data/value_arms.json`, `docs/observability/value_cycle_*`); the readers keyed to the old world's capture were not selected | green |
| W2 | `tools/test_the_incidences_denominator_is_measured_against_a_survey_base` (5) | `c3939e7b1` | no | **world digest** | green |
| W3 | `tools/test_settlement_evidence_is_graded_only_against_the_world_it_was_measured_in` (1) | `c3939e7b1` | no | **world digest** | green |
| W4 | `tools/test_the_concordance_curve_says_what_it_could_have_seen` (1) | `c3939e7b1` | no | **world digest** | green |
| W5 | `tools/test_the_front_doors_selection_verdict_cannot_rot` (1) | `c3939e7b1` | no | **world digest** | green |
| W6 | `tools/test_the_worlds_internal_return_is_stated_in_the_kind_the_record_bounds` (1) | `c3939e7b1` | no | **world digest** | green |
| W7 | `tools/test_website_integrity_fix` (1) | `c3939e7b1` | no | **world digest** | green |
| C1 | `architecture/test_a_published_count_gates_on_its_denominators_grade` (1) | `f9c1bf956` draw regrade | no | **whole-tree census**: a source ratchet over every module; changed `tools/fold_noise_floor_family.py` | green |
| C2 | `background/test_env_constant_sync_guard` (1) | `b6136796b` seats move to Opus 5.5 | no | **whole-tree census**: `seat_executor.MODEL` is visible to grep and not to the AST scan | green |
| C3 | `tools/test_closed_atom_delivery` (1) | `7be8cec09` (side of merge `528b18b4e`) | no | **whole-tree census**: changed `tools/next_step_gate.py`; the call-site scan's hand answer for `write_time_gate.py` drifted | green |
| D1 | `tools/test_a_published_feed_matches_..._produce` (1: `..._uncommitted_working_copy_edit_...`) | `92d75a690` one RNG substream | no | **data-file subject**: `maturity_map.yaml` is a curated level surface, so `data_surface_tests` returns early, and `LEVEL_SENSITIVE_TESTS` does not list the feed check that regenerates `simplified.json` from it | **RED** |
| D2 | `tools/test_the_within_year_remedy_is_indexed_on_decisions` (1) | `08c696269` (side of merge `bf1761043`) | no | **data-file subject**: `site/data/value_arms.json` lies under `PUBLISHED_OUTPUT_ROOTS`, which the data-surface sweep skips by design | green |
| D3 | `tools/test_generate_proof_data_expert_hour_findings` (1) | `d029477c7` H47 L2->L3 | no | **data-file subject**: changed `blind_review_ledger.jsonl` and the map; the published finding count read off them moved (`AssertionError: 67`) | green |
| G1 | `company/billing/test_the_statement_shows_how_each_bill_reached_its_number` (1) | `05add41ab` auto-process run complete (357 paths) | no (10 files selected) | **generated artefact**: the run-complete commit regenerates `docs/state/billing_ledger.json` and the published book | green |
| G2 | `tools/test_a_published_surface_is_reproducible_from_its_committed_input` (1) | `05add41ab` | no | **generated artefact** | **RED** |
| M1 | `background/test_an_empty_git_dir_made_scratch_immortal` (1) | `c5e9a1b5c`, a reconciler merge (side of `69b3c8d57`) | no | **merge interaction**: both parents (`9a5dc872e`, `9073a256c`) are green and the merge is red | **RED** |
| M2 | `tools/test_a_published_feed_matches_..._produce` (1: `test_every_covered_feed_...`) | `178259c6b`, a reconciler merge (side of `92fe2cb48`) | **yes** | **merge interaction, plus the gate grading a different tree**: both parents (`085a23c73`, `83d514da4`) are green. The gate selected the test and it passed: `1077 passed, 3 skipped`, run in a history-less extract where `head_resolves()` is false and the disk is the baseline. A checkout of the same commit that does have history reds | **RED** |

The 10 nodes still red at origin are S1 (3), S2, S3, S4, D1, G2, M1 and M2.

## The causes, counted two ways

| cause | turning commits | red nodes |
|---|---:|---:|
| **stem mismatch**: a `.py` change whose consumer test is not named `test_<stem>[_*]` | **7** | 12 |
| **world digest**: one commit moved the world and its committed artefacts | 1 | **18** |
| **whole-tree census**: a ratchet whose subject is every module | 3 | 3 |
| **data-file subject**: a curated surface short-circuits the sweep, or the file sits under a published-output root | 3 | 3 |
| **generated artefact**: the run-complete auto-commit | 1 | 2 |
| **merge interaction**: two green parents give a red merge | 2 | 2 |
| **total** | **17** | **40** |

**The largest cause by independent events is the stem mismatch.** It accounts for 7 of 17 turning
commits, on seven different days and in five different lanes. The world digest has the largest
blast radius, 18 nodes, but it is **one** commit. That commit was the PB4 swap with its arms
retaken, which a full-suite run on a world move would have caught as a single event. The item asked
for the fix to follow the largest measured cause, not the latest instance. The cause that keeps
recurring is the stem mismatch, so that is the follow-on.

Four of the stem rows (S1–S4) are **still red at origin**, as is every merge-interaction row. The
stem mismatch is the commonest cause, and it is also where most of the standing reds come from.

## Follow-on (filed, not done here: the console's `se-om` worktree holds the selection gate)

**`select_targets` should add the test files that IMPORT a changed module, not only the ones
named for it.** The gate already has the shape: `data_surface_tests` derives readers by
`git grep`. The `.py` counterpart is `git grep -l -e "import <dotted.module>" -e "from <dotted.module> import" -- 'tests/*.py'`.
**Measured against each test file as it stood at its turning commit, a direct-import grep would
have selected 5 of the 8 stem rows: S1, S2, S3, S4 and S6.**

The other three, S5, S7 and S8, reach the changed module only transitively. Their test files import
none of `bill_assembly` / `arrears_engine` / `generate_billing_ledger`, `churn_model`, or
`process_run_complete` / `publish_from_a_clean_tree` / `published_feed_regeneration_check`.
Catching those needs reachability one level down: the tests that import a module which imports the
changed one. Price that depth before choosing it.

**Before shipping it, print what it adds** on the 7 stem turning commits above, and its cost on a typical
commit. The `CLAUDE.md` precedent shows the risk: an over-wide derived sweep put 150 files into one
commit.

What the follow-on does not cover:

- the **world digest** (W1–W7). A world-moving commit should run the world-reading tests as a
  family. That probably means `PUBLISHED_OUTPUT_ROOTS` stops excluding `site/data/value_arms.json`
  and its `docs/observability/value_cycle_*` inputs.
- **M2's** history-less extract. The gate's subject and a real checkout disagree about what the
  baseline is.

Each of these is its own item after the stem fix lands.

## How this was done, so it can be redone

The bisect driver and step script were run from `/tmp` against the locked worktree
`/home/rich/se-wt-headred`; the raw per-group JSON is `.bisect_results.json` in that worktree.

One correction, kept beside the result. The first sweep passed a multi-node group to pytest as a
single quoted argument. pytest read it as "not found", which the step script counted as **green**,
and 5 groups reported "environment red, not a commit". That was false. A test in the sweep also
writes `site/data/dd_opening_arms.json`, a tracked file, which blocked a non-forced checkout.
**Every row above comes from the second, clean sweep**: arguments fixed, every checkout forced.
