**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# RESULT: the weather-cell artefact is cut over the whole occupied grid, 210/210 drawn households resolve, and 2 of them reach the accept branch

**Measured 2026-09-07 in an isolated worktree.** Claim
`W1_14-cut-the-artefact-over-the-drawn-population`. Pre-registered before any number below was
computed:
`docs/staging/SEAT_PREREGISTRATION_WHAT_CUTTING_THE_WEATHER_CELL_ARTEFACT_OVER_THE_DRAWN_POPULATION_MUST_SHOW_2026-09-07.md`.

## The result against the predictions

Every prediction held. They are listed with their outcomes rather than summarised, because a
pre-registration that is only ever reported as "confirmed" is not evidence of anything.

| # | Prediction | Outcome |
|---|---|---|
| 1 | ≥ 99.9 % of frame coordinates join a land cell by exact 4 dp equality | **139,938 / 139,938 = 100 %**, 0 missed households of 24,664,502 |
| 2 | no 4 dp key collisions | **175,188 grid cells → 175,188 distinct keys** |
| 3 | 210/210 drawn households resolve (0/210 before) | **210 / 210** |
| 4 | 0–8 of them match an archive site | **2** (both London's cells) |
| 5 | the refusal changes subject; refusals do not fall to zero | **208 receive the archive refusal**, not the artefact one |
| 6 | bulk table 3–5 MB | **4.27 MB** |

## What was built

`simulation/weather_cell_siting.cells_for_location` now asks two tables in order: the JSON's named
`locations` (archive sites, supply book, reachability witness — they keep their names and their
measured `km_to_cell_centre`), then `sim/weather_cells/occupied_land_cells.csv`, which holds **all
175,188 occupied 1 km land cells** with their per-driver cell label.

**`site_cells.json` came out byte-identical.** The re-cut is purely additive: no named location
moved, no coverage figure moved, and the 2.0 % `all_three` is untouched. That is the check that the
re-cut is a LOOKUP fix and not a quiet widening of the archive claim.

## The decision that was actually open, and why it went the other way

The direction said to cut over the drawn population. The artefact is cut over the **whole grid**
instead. That decision is the deliverable, so here is its reasoning rather than its conclusion:

* The drawn population is 139,938 distinct cells; the grid is 175,188. The difference is **25 %,
  0.9 MB**, against a `region_household_frame.csv` of 5.0 MB already committed beside it. The size
  argument that made "which population" a real question does not survive contact with the numbers.
* **The frame is a subset that moves.** It covers England and Wales and has no Scottish region
  today. An artefact cut to it goes silently stale the moment the frame gains one — and stale in
  the worst way, because the symptom would be a refusal that reads as a fidelity finding.
* Cut to the grid there is no "which population" question for any future reader to re-ask, and the
  drift control is an integer that was already in the JSON: the CSV's row count IS
  `occupied_land_cells`.

This is CLAUDE.md's *key a control to the property, not to today's answer*, applied to an artefact
rather than to a control.

## Why the join needed nothing fabricated

`tools/household_siting_frame.py:295-314` builds each frame coordinate from
`round(d["latitude"][i], 4)` and the normals' own longitude auxiliary coordinate.
`weather_cell_siting._occupied_space()` builds the siting's coordinates from the identical two
expressions over the same array. So a drawn coordinate IS a land cell's own coordinate at the same
precision, and the join is an EQUALITY. **No nearest-anything was added, and the fail-closed
property is unchanged**: a coordinate 22 m off a cell centre is still refused.

## What the controls now prove, and that they can fail

Four poison mutations, each reverted and the tree checksummed back to identical:

| Mutation | Killed by |
|---|---|
| a nearest-cell fallback in `cells_for_location` | `..._never_placed_by_nearest_anything`, `..._not_told_to_re_derive` |
| one land cell's label moved by 1 | `..._cut_by_the_same_partition`, `test_derive_reproduces_the_committed_artefact` |
| the land table never consulted (the pre-re-cut world) | `..._the_artefact_resolves_it`, `..._reachable_from_the_population_that_uses_it`, `..._never_placed_by_nearest_anything` |
| the all-three AND loosened to any-driver | four pre-existing controls |

Two controls are new and one is a replacement:

* `test_the_two_artefacts_were_cut_by_the_same_partition` **re-sites all seven named locations from
  the CSV alone** and checks cells and distance against the JSON. Written first as a key-equality
  check, which was wrong and said so on its first run: a named location is keyed on the PREMISE's
  coordinate (London's `km_to_cell_centre` is 0.42 km, so it is deliberately not a CSV row).
  Reproducing the nearest-cell siting is what actually binds the two artefacts.
* `test_both_legs_of_the_substitution_are_reachable_from_the_population_that_uses_it` asserts the
  accept and refuse legs over the DRAWN population, one control over the whole partition. The
  existing reachability test fires the accept branch with `REACHABILITY_WITNESS` — a coordinate
  this module plants in its own artefact — so it is a control over the mechanism and would stay
  green in a world where no real household ever matched. This one would not.
* Leg 3 of the W2_18 tripwire was written as its own opposite ("and none of them resolves"),
  shaped to go red when the world got better, with the instruction to replace and not weaken it. It
  went red on schedule and is replaced by the same property read the other way round.

## What this does NOT close

**The archive gap is untouched and is now the only thing left.** 208 of 210 drawn households
resolve and match nothing: four archive CSVs against a 21-cell-per-driver partition covers 2.0 % of
GB households on all three drivers at once. The refusal they receive is the honest one and it names
the drivers that disagreed. W1_14's *mechanism* is now reachable by the world's own population;
what it buys is bounded by archive breadth, which is a pull, not a lookup.

## Observation for W2_18's lane, not acted on here

The household siting frame carries ten regions and **none of them is Scottish**. Every Scottish
household the region curriculum can draw is therefore unsited at the draw, before this seam is ever
consulted. That is not this atom's to fix and it is not a defect in anything landed here — but the
GB-wide coverage figures this artefact publishes are computed over a grid that includes Scotland,
and the population that gets looked up in it currently cannot be Scottish. Two populations, one
number, which is the shape CLAUDE.md names as this project's most expensive recurring failure.
Filed here so it is on the record rather than rediscovered.

## Discharged by this work

`SEAT_FINDING_THE_WEATHER_CELL_ARTEFACT_PUBLISHES_THE_CENTROID_METHODS_COVERAGE_AND_ITS_OWN_DERIVATION_NO_LONGER_REPRODUCES_IT_2026-09-06.md`
(BLOCKING, same lane, same atom). Its three actions are complete and each is measured, not
asserted: the artefact reproduces (`test_derive_reproduces_the_committed_artefact` passes, and now
covers the 4.3 MB bulk table too, which would otherwise be the largest unfalsifiable claim in the
tree); the four percentages are corrected in the module docstring with the superseded figures kept
beside them, and no live surface hardcodes them — `tools/generate_weather_cells_data.py` computes
coverage from the grid and the refusal text reads it from the artefact; and the control it asked to
be kept exactly as it is was kept and extended.
