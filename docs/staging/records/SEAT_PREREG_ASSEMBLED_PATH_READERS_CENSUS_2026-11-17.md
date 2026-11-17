# Pre-registration: which modules read a data file through an assembled path, and what the commit gate misses because of it

**Severity:** LATENT · under-selection in the commit test gate. A missed reader lets a red test land.
**Filed:** 2026-11-17, delivery seat, claim `gate-selection-assembled-path-readers`.
**Follows:** `SEAT_PREREG_DATA_FILE_CITATION_CENSUS_2026-11-17.md` (017c6a467). That census found
`test_scenario_spine` selected for `history_replay.yaml` only because its docstring names the file.

## The question

`tools/pre_commit_test_gate.data_surface_tests(path)` selects tests for a staged data file through
modules whose source names the file, by repo path or by a unique basename. A module that opens
`base / f"{world_id}.yaml"` names no file, so for every file in `base` it has no route back to its
tests. Which modules do this, which tracked directories do they read, and for how many tracked
data files does the gate select none of the tests of the module that actually reads them?

## Definitions

- **Assembled data path**: in a non-test module under CODE_PREFIXES, an f-string whose last constant
  part ends in a DATA_SURFACE suffix, a `+` concatenation ending in one, `.with_suffix(<suffix>)`, or
  a `glob`/`rglob` pattern ending in one. Found by AST, over git's index.
- **Assembled reader of D**: such a module whose assembled path is joined to tracked directory D
  (decided per module by reading it, for the census).
- **Missed file**: a tracked data file in D where `data_surface_tests(file)` contains none of
  `tests_for(reader)`.

## Predictions, written before measuring

1. Fewer than 40 non-test modules contain an assembled data path.
2. At least half of them read a tracked directory (the rest write output, or read a temp/runtime dir).
3. For at least half the tracked data files in assembled-read directories, the gate today selects
   none of the reader's tests (the hole is general, not one file).
4. A static rule, "the module names D (a path-shaped constant or a `/` chain of constants that
   resolves to D, relative to the repo or to the module's own directory) and assembles a path with
   the file's suffix", finds at least 80% of the hand-identified (reader, D) pairs.

## Results

Measured at 632dd85db1 (this worktree's base). The probes call the gate's own `tests_for`,
`importing_tests` and `data_surface_tests`.

1. **Refuted.** 101 non-test modules contain an assembled data path, at 197 sites: 94 `glob`, 80
   f-strings, 9 `rglob`, 7 `with_suffix`, 7 concatenations. They are 55 in `tools/`, 38 in
   `background/`, 5 in `simulation/`, 2 in `sim/` and 1 in `.claude/`. My ceiling of 40 was set
   without looking at `glob`.
2. **Not graded as written.** The first rule I tried, "names D anywhere and assembles a path anywhere",
   resolved a directory for 93 of the 101 modules and reached 11,902 files. 11,244 of those are
   markdown, mostly `docs/staging/**`. Almost all of that is coincidence: `work_cost_estimate` names
   20 directories. So the per-module hand classification that prediction 2 assumed was replaced by a
   tighter rule (below), checked against the readers already known.
3. **Held, and stronger than predicted.** Under the broad rule, 653 of 658 non-markdown files in
   assembled-read directories had a reader none of whose named tests the gate selected. Under the
   tight rule, the directories with a real reader and no route were `sim/scenario/curriculum/*.yaml`
   (spine; 0 tests selected for `crisis_2021_22.yaml`), `sim/weather_data/*.csv`, `sim/hh_data/*.csv`
   and `tests/fixtures/judge_gold_set/*.json` (0 selected).
4. **Held for the final rule. The first tight version found 3 of 5.** The rule is that the assembled
   path is JOINED onto an expression resolving to D, through `/`, `os.path.join`, an f-string's leading
   parts, names, `IfExp`/`or`, and the module's own function returns. It is anchored at the repo root
   or at an ancestor of the module's directory. It finds all five hand-known readers: spine,
   simplifications_store, weather_inputs, premise_trace and hh_consumption. The first version found
   three, missing the f-string prefix and `os.path.join` spellings and stopping too shallow for
   `STORE_DIR`.

Final rule over the 879 non-markdown data files outside the published roots (71 directories). Seven
directories have an assembled reader:

| Directory | Files | Readers | Named tests | More importers (capped run) |
|---|---|---|---|---|
| `docs/design/simplifications/*.yaml` | 356 | simplifications_store, map_assertion_provenance | 2 | 12 |
| `docs/design/simplifications/archive/*.yaml` | 123 | simplifications_store | 1 | 11 |
| `docs/observability/*.json` | 162 | published_feed_regeneration_check | 0 | 6, **excluded** (see below) |
| `sim/hh_data/*.csv` | 7 | hh_consumption, publish_consumption_data, generate_customer_consumption, generate_explore_hh_day | 4 | 5 |
| `sim/scenario/curriculum/*.yaml` | 4 | spine | 0 | 3, including test_scenario_spine |
| `sim/weather_data/*.csv` | 4 | weather_tail_demonstration, premise_trace, run_phase3c_calibration, weather_inputs | 3 | 32 |
| `tests/fixtures/judge_gold_set/*.json` | 4 | judge_validation | 1 | 0 |

## What was built

`tools/assembled_path_readers.py` implements the rule. `data_surface_tests` adds the readers' NAMED
tests to the main selection, and `import_derived_extras` adds their importers to the existing capped
run (30 s per file, 180 s in all). So `test_scenario_spine` now reaches `history_replay.yaml` through
spine's importers, whatever any docstring says. The cost is about 0.6 s per distinct data directory
staged, cached per process.

**One exclusion, stated.** `docs/observability/` is kept off the route. Its reader's importers include
`test_evidence_pages`, which is red at origin for an unrelated reason, and that directory takes about
17 daemon commits a week. The red is filed:
`docs/staging/SEAT_FINDING_THE_EVIDENCE_PAGE_TEST_IS_RED_ON_FIVE_ARCHIVED_CITATIONS_2026-11-17.md`.

**Residue, still invisible.** The rule cannot see these:
- a directory passed in by a caller (`load_world(curriculum_dir=...)` from another module);
- a path assembled in one module and opened in another;
- markdown readers (the `docs/staging` scanners), which are out of scope because markdown selection
  was deliberately narrowed to path-shaped strings for cost;
- `arrears_engine._toggle_row`, which is not assembled at all. It names its file, two imports away
  from the test, and is the import-depth problem `importing_tests` declares out of scope.

Mutation-checked in `tests/tools/test_assembled_path_readers.py`: removing either gate hook, or making
the resolver answer "yes" for every join, turns a named test red.
