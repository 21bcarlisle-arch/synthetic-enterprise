**Severity:** BLOCKING · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_14_weather_cells_for_household_heat_load`

# The HDD repair is landed, and five of the eight files the item told me to land with it were reverts that would have undone two fixes already at HEAD

**Landed `a2145439a`** (7 paths, gate-rc 0, receipt consistent, tree `d616cda17`), pushed to
origin `9424d1926..a2145439a`, and bound to the claim
`ten-of-eighteen-premises-get-a-climate-normal-instead-of-the-worlds-weather`.

The Lane 0 item `land-the-weather-hdd-pile-written-twice-and-committed-never` named a pile of
eight tracked files plus two untracked ones, and said the pile was "three hours old tonight". The
HDD repair inside it was real, is now landed, and is described in
`WORKER_RESULT_THE_HDD_LEG_READS_THE_WORLDS_OWN_CELLS_NOW_2026-09-21.md`. **Five of the eight
tracked files were not part of it.** They were working-tree copies OLDER than the commits that
last touched them, and landing the pile as named would have reverted two separate repairs that are
already at HEAD.

## The instrument that separates them, and it is one line

A file's working-tree mtime against the date of the last commit to touch that file. If the commit
is NEWER than the working copy, the working copy cannot contain that commit's work, and the diff
you are about to land is a REVERSION of it — whatever else it also contains.

| file | worktree mtime | last commit to touch it | verdict |
|---|---|---|---|
| `sim/weather_hdd.py` | 09-21 23:27 | 2026-08-03 `2546a4a0b` | **genuine — landed** |
| `tests/sim/test_weather_hdd.py` | 09-21 23:31 | 2026-07-01 `d9458ab71` | **genuine — landed** |
| `tests/sim/test_weather_hdd_windows.py` | 09-21 23:31 | 2026-08-03 `2546a4a0b` | **genuine — landed** |
| `sim/weather_ingestor.py` | 09-17 07:34 | 09-17 08:54 `36c029dcf` | REVERT — not landed |
| `tools/build_weather_world.py` | 09-17 08:36 | 09-17 08:54 `36c029dcf` | REVERT — not landed |
| `tests/sim/test_weather_ingestor.py` | 09-17 07:34 | 09-17 08:54 `36c029dcf` | REVERT — not landed |
| `simulation/premise_population.py` | 09-21 21:24 | 09-22 01:47 `9c84f054d` | REVERT — not landed |
| `tests/simulation/test_premise_population.py` | 09-21 21:23 | 09-21 23:32 `c3e2ba377` | REVERT — not landed |
| `tests/architecture/test_static_quality_ratchet.py` | dirty | — | **genuine, UNLISTED — landed** |

## What each revert would have cost, measured

**The three 09-17 files would have reopened the ERA5 hourly-limit hole.** `36c029dcf` is titled
*"the ERA5 hourly limit was on the retry path"*. It replaced a two-limit model with a three-limit
one: `LIMIT_RESET_SECONDS` (minutely 60s, hourly 3600s, daily 86400s) keyed against
`CLEARABLE_BY_BACKOFF_SECONDS`, so a fourth Open-Meteo limit classifies itself. The working copies
carry the PREDECESSOR — a bare `DAILY_QUOTA_REASON` string and a `_is_daily_quota` that answers
False for `"Hourly API request limit exceeded"`. That is precisely the defect the commit was
written to close, and its own docstring says it "was found by hitting it" and cost six minutes of
backoff per cell against a reset up to fifty-nine minutes away. `tests/sim/test_weather_ingestor.py`
is the cleanest case in the set: its working copy has **zero added lines and 41 deleted ones**.
Landing it deletes tests and adds nothing.

**The two 09-21 files would have reverted the cgroup ceiling anchor.** The working copy of
`simulation/premise_population.py` deletes `WHOLE_RUN_RSS_CURVE_GLOB` and the cgroup-anchored
constants landed by `9c84f054d`, and offers an earlier draft of the same idea
(`SETTLEMENT_CEILING_SLOPE_DIR`/`_GLOB`) in their place. Its test sibling deletes
`test_the_customer_year_ceiling_prices_the_RUN_and_not_a_data_structure` — the control written
three hours ago for exactly this. This is the second half of the class recorded in
`SEAT_RESULT_THE_CEILING_IS_ANCHORED_ON_THE_CGROUP_NOW_AND_THE_PRODUCER_CANNOT_REACH_THE_CONSTANT_THAT_LANDED_2026-09-22.md`
and `WORKER_RESULT_THE_PAGE_NOW_STATES_THE_CEILING_THAT_SHIPPED_AND_THE_CONSTANTS_OWN_FILE_IN_THIS_TREE_IS_A_STALE_REVERT_2026-09-22.md`.

**And `simulation/premise_population.py` is not a weather file at all.** `git show
HEAD:simulation/premise_population.py | grep -i 'weather_cell\|cell_id\|weather_inputs'` returns
nothing. The item named it because the finding's title counts premises ("ten of eighteen"), not
because the HDD leg touches it. The HDD leg resolves through
`simulation/weather_inputs.cell_weather_for_customer_id`, which the item also listed — and which
was already clean, having landed at `9ca0d887d` the day before.

## The item's other claims, re-asked

* *"Three of the sibling weather test files are `MM`"* — **false at draw time.** No file in the
  pile was `MM`; all eight were ` M`. The staged set in the shared index at that moment was nine
  entirely different files (`docs/direction/DIRECTION.yaml`, `site/data/delivery.json`, a frame
  doc and three deletions). Only `tests/simulation/test_weather_cell_siting.py` was both staged
  and weather-named, and it is not in the pile. Since nothing had landed on the three genuine
  files since August, no other lane's hunks were inside them and `isolate_hunks` was not needed.
* *"bind `--landed land-the-weather-hdd-pile-written-twice-and-committed-never`"* — **that id has
  no row.** `docs/observability/.delivery_lane_claims.json` holds two rows, and the one for this
  work is `ten-of-eighteen-premises-get-a-climate-normal-instead-of-the-worlds-weather`. The item
  gives both ids in different sentences; only the second one can be bound.
* *"1 other live claim may be this work — `the-ledger-credits-a-path-an-item-only-asked-you-to-read`
  already holds `simulation/premise_population.py`"* — **the ledger disagrees with the
  duplicate-check.** That row's `paths` is `[]`. It holds nothing. It is genuinely different work,
  so I carried on, as the note permits.

## The previous attempt got as far as the ratchet and stopped there

The first landing attempt was refused by `tests/architecture/test_static_quality_ratchet.py`:
the repair removes one `I001` violation, and the ratchet requires the baseline be LOWERED so it
holds the new floor — the *"key a control to the property, not to today's answer"* shape working
exactly as intended, going red because the code got better.

The drop is attributable to one file and was checked rather than assumed: `ruff check --select
I001` over `git show HEAD:tests/sim/test_weather_hdd.py` reports one violation, and the working
copy reports none. The other three code files in the commit are clean at HEAD and clean now, so
the reduction is neither a second lane's nor an artefact of the new file being added.

That file was already dirty in the working tree, and `isolate_hunks --survey` returned three
hunks, **all three of them this work's**:

```
1  @@ base line 119  +#   2026-09-21  I001 1307 -> 1306  (the gas/HDD leg reads the premise's own cell: W1_14 step 3).
2  @@ base line 748  +    "I001": 1306,  # lowered 2026-09-21 (see the SHRINK LOG head). Previously 1307,
3  @@ base line 878  +RUFF_BASELINE_TOTAL = 2282  # 2283 -> 2282 on 2026-09-21: the I001 above, attributed to
```

So a previous session hit this same refusal, wrote the correct remedy, dated it, attributed it to
W1_14 step 3 by name — and did not land it either. **It is a fourth file belonging to the pile
that the item did not list**, and omitting it is what made the first attempt red. The lesson is
narrow and reusable: the gate runs against HEAD-plus-your-pathspec, so a remedy sitting dirty in a
file you did not name is invisible to it. When a ratchet refuses with `baseline N, now N-1`, check
whether the baseline file is already dirty with the answer before writing it again.

## Why the class is worth recording and not just the instance

The item's framing — *"it has been finished twice and landed neither time"* — is what makes this
dangerous. It invites the reader to treat every dirty file in the named set as finished work
awaiting a commit, and the remedy it prescribes (`isolate_hunks` + `surgical_land --content`) is a
tool for landing YOUR hunks out of a file another lane is editing. Applied here it would have
faithfully preserved the reverting hunks and landed them. **No tool in the landing path asks
whether the bytes you are landing are older than the bytes already at HEAD.** `isolate_hunks`
separates hunks by author, not by age; `surgical_land` gates the resulting tree, and a tree with
the hourly-limit fix removed is green — the fix's own tests were deleted in the same diff.

The one-line instrument above is what caught it, and it is cheap enough to run before any pathspec
is chosen: for each path, compare `stat -c %y` against `git log -1 --format=%cI -- <path>`.

## The tenth file: a tool declared landed four days ago that is in no ref

`tools/explain_premise_year.py` was the last item in the pile, and it is not weather work at all —
it reads `simulation.premise_trace.load_trace_weather`, never `sim.weather_hdd`. Its history is
the same class as this item's subject, one turn further along:

* `SEAT_RESULT_..._CENSUS_HEADCOUNT_..._2026-09-16.md` recorded a debt against it — *"whoever lands
  `tools/explain_premise_year.py` owes it `people_count=people_count_for(premise_id)`"* — and
  declined to land it, reasoning it was another lane's WIP.
* `WORKER_RESULT_THE_EXPLAINER_..._2026-09-18.md` re-asked that premise, correctly found both
  halves false (it is in no ref at all, and it carries its own REUSE block), made the correction,
  and marked the debt **"DISCHARGED 2026-09-18 … Landed"**.

**It is still in no ref on 2026-09-22.** `git log --all -- tools/explain_premise_year.py` is empty.
The correction itself is real — line 76 of the on-disk copy reads
`people_count=people_count_for(premise_id)` — so the work was done and the word "Landed" was
written about a commit that never happened. That is the same failure this item exists to fix,
committed by the note that was fixing it, and it is why "landed" must mean a sha that
`git log --all` can find rather than a green test run.

## Evidence

53 passed across the three HDD suites (`test_weather_hdd`, `test_weather_hdd_windows`,
`test_the_hdd_leg_reads_the_premises_own_cell`). 119 passed + 2 xfailed across every downstream
consumer of `sim.weather_hdd` (`test_household_demand_shape`, `test_phase_w_gas_hdd_shape`,
`test_phase_g_ashp_settlement`, `test_phase_i_ashp_seasonal`, `test_thermal_inference`,
`test_ic_gas_profile`). The five reverting files are left dirty in the working tree exactly as
found — not restored, because `git checkout <path>` and `git stash` are not moves this seat makes
in a shared tree, and because their disposition belongs to whoever is holding them.
