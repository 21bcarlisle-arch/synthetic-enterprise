**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: how much of the data-file selection route is citation, not reading (2026-11-17)

*Filed before any pair was counted. Drawn on `gate-selection-data-file-citation-census`, the sequel to
34656a6f2, which cut the markdown route after finding 562 of 814 (page, test) pairs (69%) were
citation, against a predicted <15%.*

## What is counted

`tools/pre_commit_test_gate.data_surface_tests` on every tracked file with a non-markdown
`DATA_SURFACE_SUFFIXES` suffix (`.yaml .yml .json .jsonl .toml .ini .cfg .csv .txt .sh`), outside
`PUBLISHED_OUTPUT_ROOTS` and `CURATED_SURFACE_PATHS`. Only the **direct test route** is classified (a
`test_*.py` that names the file); the module route already ignores docstrings for every suffix.

Each (file, test) pair is put in exactly one class, by the strongest string in the test that names the file:

- **PATH** — an evaluated string with no whitespace holds the name (`ROOT / "x.json"`, `open("x.yaml")`).
- **SENTENCE** — only evaluated strings with whitespace hold it: shell lines (`git show HEAD:x.json`),
  error messages, fixture text. Ambiguous by construction: some read, some cite.
- **PROSE** — only docstrings or bare string statements hold it. Such a string cannot read anything.

A PROSE pair can still be a real guard if the test imports a module whose code names the file
(the test_simplifications_store shape). So PROSE is split again:

- **PROSE-READER-IMPORTED** — the test imports a non-test module whose evaluated strings name the file.
- **PROSE-ONLY** — it does not.

## What "done" means for this item

The census is measured and recorded here, and one of two things lands: a cut of the PROSE-ONLY class
(if it is material in seconds, and a spot-check finds none reading the file), or a recorded decision
not to cut, with the number that makes it not worth it.

## Predictions, written before measuring

1. PROSE (both sub-classes) is **under 25%** of direct-route pairs. Data files are loaded far more than
   they are cited, unlike K8 pages.
2. SENTENCE is **under 10%** of direct-route pairs.
3. PROSE-READER-IMPORTED is **at least a third** of PROSE: a test that names a data file in its
   docstring usually tests the module that loads it.
4. The summed seconds of PROSE-ONLY test files, over the files that select them, are **not material**:
   no single data file selects more than 60 s of PROSE-ONLY tests.
5. A spot-check of five PROSE-ONLY pairs finds none whose verdict depends on the file's content.

## Results

Measured at 0fadd2b9b (this worktree's base) by a probe that calls the gate's own functions
(`_py_files_naming`, `_basename_identifies_one_file`, `_names_it_outside_comments`, `tests_for`). Each
PROSE-ONLY test file was then timed alone (`pytest -q`, serial, 900 s cap).

879 data files qualify. 175 of them select at least one test directly, giving **529 (file, test) pairs**.

| Class | Pairs | Share | Also selected through a module |
|---|---|---|---|
| PATH | 408 | 77% | — |
| SENTENCE | 21 | 4% | 2 |
| PROSE-READER-IMPORTED | 52 | 10% | 9 |
| PROSE-ONLY | 48 | 9% | 1 |

The 48 PROSE-ONLY pairs are 45 test files, **1,913 s** in total. Five exited non-zero in this worktree.
`test_phase24a_ic_customer` hit the 900 s cap, so its true cost is higher.

| Data file | PROSE-ONLY seconds | Does the test reach the file? |
|---|---|---|
| `docs/design/curriculum/served_segments.json` | ≥900 (`test_phase24a_ic_customer`, capped) | **Transitively.** It imports `run_phase2b`, whose book is built by `live_population()` → `served_segments()`. One test was rewritten so that it does not depend on the file. |
| `docs/design/simplifications/DD_seasonal_cashflow_physics.yaml` | 507 (`test_a_published_feed_matches_what_its_generator_would_produce`) | **Yes.** `generate_simplified_data` copies every store yaml through `simplifications_store`'s `f"{atom_id}.yaml"`. |
| `docs/market_research/assumption_toggles.yaml` | 215 (`test_registration_loss_feed`) | **Yes.** It asserts a register row's default through `arrears_engine._toggle_row`, two imports away. |
| the other 32 files | 291 in total, none over 50 | mostly citation (see spot-check) |

1. **Held.** PROSE is 19%, against a ceiling of 25%. Markdown was 69%.
2. **Held.** SENTENCE is 4%.
3. **Held.** 52 of the 100 PROSE pairs import a module whose code names the file.
4. **Refuted.** Three data files each select more than 60 s of PROSE-ONLY tests.
5. **Refuted.** The spot-check covered the five chosen first plus the three large ones above. Real readers: `test_scenario_spine`, which reads `history_replay.yaml` through `spine`'s `f"{world_id}.yaml"`; `test_registration_loss_feed`; and the feed test. `test_phase24a_ic_customer` reaches its file transitively. Only citers: `test_phase27b_ccl` (`policy_costs` cites the CCL table only in comments), `test_domain_invariants` (VAT), `test_executor_daemon` (`start_worker.sh`) and `test_weather_inputs` (C1.csv, which no longer reads it since the seam migration).

## Decision: the data-file route is not cut

The markdown cut was safe because K8 pages are cited, not loaded. Data files are loaded, and often
through a path **assembled from parts** (`f"{world_id}.yaml"`, `f"{location_id}.csv"`, `f"{atom_id}.yaml"`).
Neither route can see such a path, so a test's docstring is sometimes the only trace of a real read.
The tests "PROSE-ONLY" would drop include at least 1,622 of the class's 1,913 s, and those are the
real readers. The most a cut could save is about 290 s, spread across small files, and it would
blind the gate to `history_replay.yaml`. The docstring of `_names_it_outside_comments` now records
this, so the next session does not repeat the measurement.

**Residue, stated (not filed as an atom):** this is a hole in **under-selection**, not over-selection.
A module that opens `f"{world_id}.yaml"` without naming any file has no route back to its tests at
all. Here it was covered by luck, through a docstring. A curated-surface entry for the curriculum
directory is the obvious repair, but it needs a census of assembled-path readers first, so it is
not attempted here.
