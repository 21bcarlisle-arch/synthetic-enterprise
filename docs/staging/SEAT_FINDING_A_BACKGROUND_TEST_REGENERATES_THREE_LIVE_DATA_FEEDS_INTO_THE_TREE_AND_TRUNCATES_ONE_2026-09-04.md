**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# A background test regenerates three live data feeds into the tree, and truncates one by 87%

*Delivery seat, 2026-09-04, found while landing
`decide-the-proposal-side-of-a-low-water-episode-field-2026-09-04`. Not that claim's subject —
it is what refused that claim's promotion.*

---

## What happens

Running `tests/background/test_process_run_complete.py` writes three **tracked, committed** files
in the working tree:

```
 M docs/market_data/grid_intensity_feed.json     2314 lines -> 293   (2027 deleted)
 M site/data/explore_carbon.json
 M site/data/weather.json
```

Reproduction, from a clean tree, ~40 seconds:

```bash
git status --short docs/market_data/grid_intensity_feed.json   # clean
python3 -B -m pytest -q -p no:randomly tests/background/test_process_run_complete.py
git status --short docs/market_data/grid_intensity_feed.json   # ' M'
```

Bisected against five sibling publish-path suites (`test_publish_scope`, `test_publish_gate_scope`,
`test_publish_freshness`, `test_published_provenance_is_real`, `test_publish_decoupling_exit`) —
none of them touches the files. Only `test_process_run_complete.py` does. The route is
`background/process_run_complete.py`, which names all three feeds and drives
`tools/generate_grid_intensity_feed.py` and `tools/generate_explore_carbon.py`; the test reaches a
real publish path whose generators are not redirected, so they regenerate from whatever local data
the test environment has and write the result over the committed artefact.

## Why this is BLOCKING and not housekeeping

**It refuses landings.** `promote_worktree_landing` correctly reads a tracked change outside the
machine-churn directories as "this landing is not the whole of what was done" and refuses. That is
exactly what happened to this turn: a full `tests/background/` run at 16:34:56 BST dirtied the
three files, and the promotion of an already-gated commit was refused until they were restored by
hand. Any turn that runs the background suite before landing hits this.

**The truncation is the dangerous half.** `grid_intensity_feed.json` does not merely get rewritten
— it loses 2027 of 2314 lines, because the regeneration runs against whatever the test environment
could reach rather than against the record the committed file holds. A shorter feed is not an
obviously-broken feed; it is a plausible one.

**And there is a route for it to land.** The publish daemon commits generated site output it finds
in the tree. `site/data/explore_carbon.json` and `site/data/weather.json` are exactly that shape.
A truncated feed written by a test, sitting in the tree when the daemon sweeps, is committed as
data — with no source change beside it to make anyone look.

**It is also a test manufacturing the evidence a control reports on** — the same class the episode
guard's own suite has a fixture docstring about, caught in the act on 2026-08-10:

> the moment the recorder gained a second state path, running this suite wrote
> `docs/observability/.wedge_suspect_hit_rate.json` into the live tree — a test manufacturing the
> very evidence a control reports on.

That fix isolated the paths the recorder was *known* to use. This is the same defect one publish
stage further out, and the same remedy applies: isolate the paths the path under test is known to
write, not the ones a test happened to need.

## What I did and did not do

Restored all three from `HEAD` (via `git show HEAD:<path> > <path>`, not `git checkout`) so the
landing could promote. **I did not fix the test** — the claim in hand was the episode guard's
proposal side, and silently widening a landing to cover an unrelated suite is how a commit stops
being reviewable. It is written down here instead, at the severity it earns.

## The narrowing that is still owed

Which test *within* `test_process_run_complete.py`, and which generator call escapes redirection.
The bisect above stopped at file granularity because the claim in hand was elsewhere; the next step
is a `-k` bisect over that file with the three mtimes watched, which is the same shape as the loop
that found it and costs about a minute.

---

## DISPOSITION — repaired 2026-09-04, worker lane

**The bisect, run per-node over all 88 collected tests with the three paths watched.** Five tests
write, and they are exactly the five that drive `main()`/`_process()` end to end:
`test_main_success_flow`, `test_force_republish_flag_bypasses_identical_fingerprint`,
`test_force_republish_flag_consumed_exactly_once`, `test_a_failed_publish_does_not_write_the_
fingerprint`, `test_a_successful_publish_still_writes_the_fingerprint`. The fixture docstring
already named "test_main_success_flow and the force-republish trio" as the four end-to-end tests;
the fingerprint pair joined them later and nothing noticed.

### THE TRUNCATION WAS NOT THE TEST. It is what the live publisher has written for nine days.

**This refutes the heading of this document and the sharpest paragraph in it, and the refutation
is kept here rather than folded away.** *"The regeneration runs against whatever the test
environment could reach rather than the record the committed file holds"* — measured, and false.

`docs/observability/sim-runner-log.md`, every real `[process_run]` cycle:

```
2026-08-25 07:34 .. 2026-08-26 16:48 UTC   1247 record(s) over 2016-06-01..2025-06-07
2026-08-26 18:09 .. 2026-09-04 16:16 UTC    959 record(s) over 2016-07-24..2025-06-07
```

The step is at **2026-08-26 18:09 UTC** and it has held for ~250 consecutive publish cycles over
nine days. The committed artefact is `generated: 2026-08-26T13:14Z` — the last cycle *before* the
step. So the "2314 → 293 lines" this document opens with is not damage a test did; it is the
current, reproducible output of the production publish path, which the test wrote because it ran
the same generator against the same tree. **A shorter feed is not an obviously-broken feed** was
the right instinct and it was pointed at the wrong writer.

Two consequences, both of which change what to do:

1. **The three hand-restorations of this file — mine and the two before it — were reverts of live
   publisher output**, each made by a seat that read a dirty tracked file as test damage. That is
   the mechanism that has held the committed copy nine days behind for nine days.
2. **The isolation repair below is still right, and its reason is stronger, not weaker.** What the
   test wrote was byte-identical to what the daemon writes. There is no `abc1234` and no epoch-0
   stamp in it — nothing whatsoever marks it as fixture output. A defect that leaves no trace in
   the artefact is exactly the one a guard has to catch at the sink.

**What I am NOT claiming**: that 959 is wrong. `extra_days_carried_for_meter_reads` went from 11
days to 5 and the window start moved forward, which is `dates_with_reads()` returning fewer days —
book churn and a regression look the same from here, and more than one thing changed. **I cannot
yet say.** Filed as its own finding with the evidence, not decided in a bounded tick:
`SEAT_FINDING_THE_COMMITTED_GRID_FEED_IS_NINE_DAYS_BEHIND_THE_ONE_ITS_OWN_DERIVED_PAGE_IS_BUILT_FROM_2026-09-04.md`.

### The rest of the disposition, which stands

**It was FOUR files, not three.** `tools/couple_value_based_pricing.py` writes
`docs/observability/value_based_pricing_arms.json` by the same route. It escaped the original
bisect because `docs/observability/` is a machine-churn directory the landing gate tolerates — so
the one that could not refuse a landing was also the one nobody would have found this way.

**Why the two registries already in the file did not reach them.** All four take their destination
as an *optional* keyword that defaults to `None` and fall back to a module constant:
`dest = OUT_PATH if out_path is None else out_path`. `_PIPELINE_OUTPUT_PATHS` re-roots a module
*attribute* prc owns; `_PIPELINE_OUTPUT_WRITERS` rebinds a keyword whose *def-time default* is the
real path. This is a third shape, and its def-time default is `None` — so the sibling registry's
own "am I still isolating this?" assertion would not have fired either.

**A clean `git archive HEAD` extract UNDERSTATES this defect.** In an extract, the grid-intensity
generator raises `FileNotFoundError` on `sim/cache/elexon_demand_full.json` (untracked) and
`_process` swallows it as "Grid intensity feed publication skipped" — so only two of the four are
visible there. The truncating one only truncates where the caches exist, which is every real tree.

### What landed

`_PIPELINE_OUTPUT_FALLBACK_WRITERS` in `tests/background/test_process_run_complete.py`, wired into
`_isolate_project_dir`, carrying all four with the same rename-detecting assertions as its
siblings *plus* one the siblings cannot make: that the keyword still defaults to `None`.

Verified both ways: a full run of the file against the real tree now leaves
`grid_intensity_feed.json`, `explore_carbon.json`, `weather.json` and
`value_based_pricing_arms.json` byte-identical (the arms file checked by md5, since the shared
tree's own copy was already dirty from another lane); and a full run inside a clean HEAD extract
leaves that tree carrying nothing but `test_execution_log.jsonl`, which every suite writes.

**And a sink, because a registry only covers the generators somebody enumerated.**
`docs/market_data/grid_intensity_feed.json` is added to `_PROTECTED_WRITE_PATHS` in
`tests/production_surface_guard.py`. Blast radius measured before adding, to the standard that
module demands and for the reason it demands it — the `site/data/` file-scoping is a *measured*
decision, not an oversight, and this is not a re-litigation of it: six test files name this feed,
five only READ it or assert on generator source, and
`tests/tools/test_grid_intensity_feed_and_explore_carbon.py` passes its own `out_path`. Exactly one
wrote the real path and it is now redirected. What puts this file on the protected side of the
`site/data/` line is not that it is unregenerable — it is that it sits OUTSIDE the publisher's
`site/data/*.json` commit glob, so nothing overwrites a test's write on the way past.

### The fifth generator, which is the part worth keeping

Per-registry wiring is opt-in and invisible when omitted — the same objection
`_isolate_project_dir`'s own docstring makes about the incident before it, and the reason this
recurred. So `_PUBLISH_BLOCK_COLLABORATORS` declares every module `_process`/`_run_weather_data`
imports and what makes it safe, and `test_every_module_the_publish_block_imports_is_declared_here`
compares that set for **equality** against the live source. Wiring a new generator into the publish
block reds this file until someone says which it is — at the one moment isolating it is cheap.

`test_a_collaborator_declared_isolated_is_actually_in_the_registry_it_names` binds the declaration
and the registries to each other in both directions, because deleting a registry entry would
otherwise silently delete its own parametrised case: a control that stops testing exactly what it
stopped covering.

Mutation-proved, three ways, in an isolated extract:

| mutation | result |
|---|---|
| drop `generate_explore_carbon` from the fallback registry | cross-check RED, **and** the real `site/data/explore_carbon.json` is rewritten again |
| wire an undeclared `tools.brand_new_generator` into `_process` | declaration control RED |
| delete the `tools.revenue_sanity_check` declaration | declaration control RED |

The first row is the one that matters: it shows the redirection is load-bearing and that removing
it costs something, rather than the control merely agreeing with the list it was built from.
