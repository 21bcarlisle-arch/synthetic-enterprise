**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_14_weather_cells_for_household_heat_load`

# The demand-shape and forward-price legs read the world's own weather now — and the leg I did not touch is a third resolver

Drawn 2026-09-21 as LANE 1 BUILD, `W1_14_weather_cells_for_household_heat_load`, level 1→3,
`loop_stage=build`. The atom's `block_reason` (corrected 2026-09-20) names three pieces of remaining
work; this tick did **step 1**, the only one of the three that is code:

> *"migrate `weather_inputs` onto `sim.weather_world` — the seam must resolve to a CELL, not to a
> customer_id with a CSV; this is what makes L2 true."*

Pre-registration, written before any measurement:
`docs/staging/records/WORKER_PREREG_W1_14_WHAT_THE_SEAM_MIGRATION_CHANGES_ON_THE_BOOK_2026-09-21.md`.

## 1. The predictions, and what they returned

| # | prediction | measured | verdict |
|---|---|---|---|
| 1 | 14/18 premises hold a mean-temperature series under the four archives | **14/18** | confirmed |
| 2 | 16/18 after the migration; the two misses Birmingham; net gain Teesside's pair | **16/18**, misses C_IC1/C_IC2, gained C_IC3/C_IC3g | confirmed |
| 3 | not an equivalence: ≥0.5 C mean-absolute at C1, store WARMER | **+1.19 C mean, 1.31 C mean-abs** at C1; +1.19 (C2), +1.27 (C3), +0.25 (C4) | confirmed |
| 4 | mutatable on the live book, unlike the 2026-09-20 `_has_archive` repair | **6 of 9 controls die** under the revert-to-archive mutation | confirmed |

An unpredicted gain: the store spans **3,653 days (to 2025-12-31)** against the archives' 3,446 (to
2025-06-07), so the shape leg gets 207 days it previously fell back to an unadjusted base shape for.

Prediction 3 is the one worth reading twice. **This migration changes settled numbers.** The store's
temperature is HadUK-Grid 1 km plus the cell's own `level_c`; the archives are ERA5 at ~9 km. The
1 km observational analysis resolves the urban heat island a reanalysis cannot, so it is the more
faithful reading — an R13 fidelity decision taken blind to company results, which it will move.
Cloud cover is ERA5 on both sides and differs only by sampling point (cell centre vs property
coordinate): +0.015 pp mean, 1.62 pp mean-absolute at C1.

## 2. What landed

`simulation/weather_inputs.py` — `cell_weather_for_customer` resolves a premise's coordinate to a
cell with **`WeatherWorld.cell_id_for`, the same call the physics leg makes**, so which sky a
household had is decided in exactly one place. `weather_means_for_customer` and
`cloud_cover_for_customer` read that; `weather_refusals_for_book` carries the reasons out.

Three deliberate shapes:

- **The refusal travels with the series** (`CellWeather`). `_weather_adjusted_shape_fn` falls back to
  the UNADJUSTED base shape on any date it has no weather for, so an empty series is invisible
  downstream — a premise 7.4 km outside the store and a premise with a complete sky produce the same
  kind of number. A declared `None` and a silent `None` were collapsing into the flattering branch.
- **Completeness is asked PER FIELD**, not over the five trace fields the physics leg needs. 8 of the
  store's 221 cells hold temperature and no wind/cloud/precipitation (counted here; `available()`
  cites 18 from the store validator — a different count, left beside this one, and the rule is
  unaffected). Refusing those a real 1 km temperature for a wind column nobody asked for would throw
  away a reading the world has.
- **One world per process.** `shared_world` caches, and `run_phase2b` now loads
  `WeatherWorldSource` ONCE at the 4c inputs and hands the same world to all three legs. Two copies
  of the world in one process can drift, which is the exact thing the per-cell architecture exists
  to make impossible.

`simulation/run_phase2b.py` — the two comprehensions take that world, and
`weather_refusal_by_customer` is in the run's returned record. Empty is the good answer; a missing
key would not be an answer at all.

### The controls, and the three that stayed green

`tests/simulation/test_weather_inputs.py`, 9 legs. Mutation: point the resolver back at
`sim/weather_data/{id}.csv`, in-process, no shared-tree write.

| control | under the mutation |
|---|---|
| `the_shape_leg_reads_the_world_and_not_the_per_property_archive` | **RED** |
| `the_physics_leg_and_the_shape_leg_send_a_premise_to_the_same_cell` | **RED** |
| `a_premise_the_store_cannot_reach_gets_a_named_refusal_not_a_silent_empty_series` | **RED** |
| `a_premise_with_no_coordinate_says_so_in_its_own_sentence` | **RED** |
| `a_cell_holding_temperature_and_no_cloud_still_answers_the_temperature_question` | **RED** |
| `the_store_refusing_entirely_is_a_reason_and_not_a_crash` | **RED** |
| `..._gives_two_premises_in_one_place_one_sky` | GREEN — **equivalence** |
| `..._gives_the_gas_leg_its_electricity_twin_s_sky` | GREEN — **equivalence** |
| `the_world_is_loaded_once_per_process...` | GREEN — **different subject** |

The three silent legs are equivalences and not missing tests, and establishing which way round that
falls is the point: under the archive design C5 and C1 shared a *location*, so they shared a CSV;
under the store they share a *cell*, so they share a series. One-place-one-sky is true of both
designs — **which is exactly why no control caught the four days between 2026-09-17 and 2026-09-21
when the physics leg read the cell and the shape leg read the CSV.** The leg that catches that is
the new cross-leg agreement control, and it is on the live book because the defect was a whole-book
property.

Two pre-existing controls asserted the OLD source and were rewritten, with the old claim kept beside
the new one: `test_weather_means_for_customer_resolves_shared_location_to_c1` pinned
`== 4.6` (ERA5's reading at C1's coordinate) and `test_cloud_cover_for_customer_resolves_shared_locations`
asserted `cloud_cover_for_customer(c5) == load_weather_cloud_cover("C1")` — file identity, which was
never the property. Both now assert one-place-one-sky and nothing about which file.

## 3. What the migration found: a THIRD resolver, and it is filed BLOCKING

`docs/staging/WORKER_FINDING_THE_HDD_LEG_IS_A_THIRD_RESOLVER_AND_TEN_OF_EIGHTEEN_PREMISES_GET_A_CLIMATE_NORMAL_INSTEAD_OF_WEATHER_2026-09-21.md`.

`sim/weather_hdd._resolve_source_cid` strips a trailing `g` from the customer_id and otherwise
passes it through. It asks no coordinate, matches no location, and when the resulting id has no CSV
`get_hdd` returns `REFERENCE_MONTHLY_HDD[month]/30` — the 1991-2020 England & Wales monthly normal.

**8 of 18 premises read a real daily temperature; 10 get the normal.** C7 (London, in C1's cell):
annual HDD 1560.1 from its own cell vs 2086.1 from `get_hdd` — **+33.7% in 2018 and +52.6% in 2022**,
the same 2086.1 in both years because a normal cannot see a winter. C1 and C7 share a cell and are
12–20% apart. That is the attribution failure the per-cell store exists to end, in a third place,
arithmetically.

Not folded into this commit on purpose: `get_hdd` has 11 test files against it and takes an id rather
than a coordinate, so the remedy is a seam change that will move settled gas numbers for ten
premises. Two source changes in one commit would make neither attributable.

## 4. The level: STAYS AT 1, and now for a measured reason

The map row has asked its next reader, twice, to say whether L2 means "the mechanism works" or "the
world uses it" and then move it. The answer this tick produces is neither: **the mechanism works and
the world uses it on two of three legs, and the third substitutes climatology for a tenth of the
book.** L2 is "mechanically real"; a level move over §3 would be the reachable-but-not-chosen error
the row keeps warning about, and this time the refusal is arithmetic rather than judgement. The move
is also refused *mechanically* — `record_level_up_self_certified` raises `LaneBlockedError` while
this lane carries a live BLOCKING finding, and as of this commit it carries mine. That is the OPS11
machinery doing exactly what it is for.

`block_reason` is updated with all four pieces and the version it replaces is in git history.

## 5. Owed elsewhere

- **§3 is the next item in this lane**, ahead of steps 2 and 3: it is the only one of the four still
  changing settled numbers.
- **Step 2 (Birmingham's cell) needs a network pull** for the ERA5 half at one cell centre, which is
  a store build (`tools/build_weather_world --build`), not a per-property archive. Two premises.
- `simulation/run_phase1b_weather_pull.py` is still the refused design, still executable, still
  saying nothing about having been refused — carried forward from the 2026-09-20 result's §5, and it
  belongs with step 3's judgement rather than with either of these commits.
- `_weather_source_customer_id` and `cell_matched_site` now reach **no settlement leg**. They resolve
  the archives for `load_weather_means`'s remaining readers and carry W1_14's L1 evidence; their
  deletion is step 3.
