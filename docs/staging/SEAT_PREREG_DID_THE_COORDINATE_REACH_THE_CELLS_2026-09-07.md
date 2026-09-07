**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_14_weather_cells_for_household_heat_load

# SEAT PRE-REGISTRATION — did W2_18's coordinate actually reach the derived weather cells?

**Date:** 2026-09-07
**Claim:** `W2_18-coordinate-at-the-draw` (Lane 0 delivery)
**Written BEFORE the measurement below was run.**

## Why this is being asked

`ec8a18710` landed a coordinate at the draw: `simulation/household_siting.coordinate_for_customer`
draws a 1 km cell from the region's own census household distribution, and
`population_draw.to_customer_dict` renders it. That is the thing W1_14 was blocked on.

W1_14's tripwire for exactly this event is
`test_weather_cell_siting.py::test_no_household_in_this_world_can_reach_the_cell_substitution_branch`,
whose docstring says: *"a coordinate at the draw breaks it. That is the point … Do not weaken it;
delete it and move W1_14's level."*

**It did not break.** The whole suite is green at HEAD. So either the coordinate does not reach the
cells, or the tripwire cannot see it. Reading the control, line 155 draws with
`draw_population(7, acquisitions_per_year_lambda=40.0)` — no `draw_region=True` — so it measures the
DEFAULT placeholder-region path, which is the one branch `household_siting` correctly refuses to
site. The capability landed on the non-default branch and the control is blind to it.

## Predictions

- **P1** — with `draw_region=True`, **100%** of drawn households carry a non-None `lat`/`lon`. All
  ten curriculum regions are present in the committed frame (verified above; that part is not a
  prediction).
- **P2** — with `draw_region=True`, the share of drawn households that `weather_cell_siting.
  cells_for_location` actually RESOLVES is **low, well under 10%**, and near the committed
  artefact's `all_three` coverage figure (~2–3.5%). A coordinate existing is not a coordinate the
  cells cover. If this comes back near 100% I have misread what the artefact's coverage counts.
- **P3** — flipping only `draw_region=True` in that control turns it **red** on the drawn-household
  leg (line 157 and/or 160), with the resi-premise leg unchanged. That is the poison round proving
  the control CAN see the event it was built for.
- **P4** — `test_derive_reproduces_the_committed_artefact` (red in my first run) is **pre-existing at
  HEAD and unrelated to W2_18** — it compares a fresh derivation against the committed artefact and
  the fresh one covers LESS, which is the signature of a degraded local pull, not of anything the
  coordinate work touched.

## What each answer means

- P1 true + P2 true → the household gap is **partly** closed: a coordinate exists for every drawn
  household, and the cells cover a small measured share of them. W1_14's blocker changes from "no
  coordinate exists" to "the archive covers N% of sited households", which is a **different and
  smaller** blocker, and it must be restated rather than declared closed.
- P1 true + P2 false (near 100%) → my reading of the coverage figure is wrong and I say so here.
- P3 false → the control is blind for some second reason as well, and finding it is the deliverable.

## What I will NOT do

Move W1_14's `level_current`. Level moves are recorded, never authorised, and a coverage share is
not a wired heat load. The deliverable here is that the tripwire can see the truth and that the
blocker names the real remaining gap.
