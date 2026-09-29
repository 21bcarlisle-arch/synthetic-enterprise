**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_19_who_lives_where_money_and_composition`

# FINDING — the committed siting frame predates its own placement, and a life event erases four NEED fields

Found 2026-09-27 while wiring W2_19 layer one (the sited cell carries its output area;
`docs/staging/records/PREREG_W2_19_LAYER_ONE_THE_SITED_CELL_CARRIES_ITS_OUTPUT_AREA_2026-09-27.md`).
Neither is fixed by the commit that files this. Each would change the world for a reason other than
the one that commit is about, and the result would be unattributable.

## 1. `--build` at HEAD would move every household

`sim/household_siting/region_household_frame.csv` was committed at `d331c255c` (2026-09-07 03:49).
`weather_cell_weights.census_weights` moved from the second placement (addresses in the 3×3 window
around each postcode centroid) to the ONSUD address placement at `1a352d2aa`, four hours later. The
frame was never rebuilt. So `python3 -m tools.household_siting_frame --build` today writes a
different frame. Its manifest still says "OS Open UPRN", and the cell sets differ: Scotland has
35,389 cells committed against 51,864 rebuilt, and the first East row is `51.4451, 0.3674` committed
against `51.4538, 0.3823` rebuilt.

**What it costs today:** 0.16% of committed households (43,028 of 27.1M) sit in cells where no
address of their region exists, because the window put them there. W2_19's output-area frame handles
those cells from the smallest square around them that holds an address of the region (2,942 cells
at ring 1, 2 at ring 2, none further). That keeps the committed frame as the single source of
coordinates, but it is a patch over the gap, not a close.

**Remedy, as its own one-variable change:** rebuild the household frame (`--build`), then the
output-area frame (`--build-output-areas`, whose ring census should fall to all-zero), in one commit.
Print the household-weighted driver means before and after, the way `census_weights`' docstring did
for the placement change (1.28% / 1.07% / 0.11% of an SD). Every home's weather cell may move.

## 2. `life_events.apply_events` drops every `Household` field added after `income_stress`

`apply_events` rebuilds the household from an explicit field list. The list stops at
`income_stress`, so `floor_area_band`, `has_loft_insulation`, `has_cavity_wall_insulation` and
`has_mains_gas_supply` (NEED, added 2026-09-10) go back to `None` on **any** life event, including
events that have nothing to do with them (a job loss). W2_19 added `output_area` to the list. The
other four were left alone deliberately, because restoring them changes demand for every home with
an event.

**Remedy:** build `state` from `dataclasses.fields(Household)` so a new field cannot be dropped
again, with a control that applies one event of each type and asserts every field it does not name
survives. Measure first how many live homes have an event before their fabric start, because that
is the population whose demand moves.

## Status 2026-09-27

**2 is FIXED.** `apply_events` builds its state from `fields(Household)`; the control is
`tests/simulation/test_life_event_keeps_every_field_it_does_not_name.py`. The claim above that
restoring the fields "changes demand for every home with an event" was measured and is WRONG: 0 of
9.6M half-hours moved across 273 homes with events, because no demand code reads the four fields.
Pre-registration and result: `docs/staging/records/PREREG_LIFE_EVENTS_KEEP_EVERY_HOUSEHOLD_FIELD_2026-09-27.md`.

**1 is FIXED.** Both frames were rebuilt on the address placement: every cell is ring 0, the weather
join is total, and the driver means moved less than the placement change moved them. Result:
`docs/staging/records/PREREG_REBUILD_THE_SITING_FRAME_ON_THE_ADDRESS_PLACEMENT_2026-09-27.md`. The
ring fallback stays as the refusal a future drift will hit. Both remedies are landed and this
finding is closed.
