**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# PRE-REGISTRATION — what the weather-cell re-cut does to the accept branch

**Filed** 2026-09-16, before the measurement, by the delivery seat (lane 0, claim
`weather-coverage-is-the-cap-on-the-half-hourly-shape`). RECORDED because a pre-registration is not
a defect. The finding it corrects is
`SEAT_FINDING_THE_HALF_HOURLY_SHAPE_REACHES_FOUR_CUSTOMERS_AND_AN_UNCOMMITTED_ARTEFACT_KILLS_THE_ONE_MECHANISM_THAT_WIDENS_IT_2026-09-16.md`;
the outcomes are in
`SEAT_RESULT_THE_WEATHER_CELL_ARTEFACT_WAS_THE_STALE_ONE_AND_THE_ACCEPT_BRANCH_WAS_NEVER_DEAD_2026-09-16.md`.

## Why this is filed before anything is run

The drawn item says the shared tree's uncommitted `sim/weather_cells/` regeneration is a
**regression** that "makes `cell_matched_site` accept nothing", and that the committed artefact is
the good one. Re-measuring the premise in an isolated worktree inverts that, and the inversion is
established before this file is written, so it is not what is being pre-registered:

* `simulation.weather_cell_siting._derived()` run **today, in a worktree checked out at
  `a7faea4ff`, with none of the shared tree's uncommitted bytes**, produces
  `occupied_land_cells = 194,865` and coverage
  `{winter_temp 0.2113, annual_wind 0.2062, annual_sun 0.2493, all_three 0.0191}` — byte-identical
  to the shared tree's "regression", and cell-label-identical on all four archive sites.
* The committed artefact says `175,188` and
  `{0.2036, 0.2782, 0.1725, 0.02}`.
* `tests/simulation/test_weather_cell_siting.py::test_derive_reproduces_the_committed_artefact` is
  **RED at HEAD in a clean worktree**. It is not catching the shared tree; it is catching the
  commit.
* Cause, from cache mtimes: the artefact landed in `f27695607` at **2026-09-07 02:06**. The ONSUD
  address placement it is cut over was written **after** that —
  `~/.cache/synthetic-enterprise/onsud/oa_cell_addresses.pkl` at 07:33 and `oa_region.pkl` at 09:56,
  both 2026-09-07. The HadUK normals have not moved since 2026-09-05 and the land mask still asserts
  245,077. **So the committed artefact is the one cut from a partial input, and it has been
  unreproducible for nine days.**

That much is measurement, not prediction. What follows is prediction.

## The predictions

**Q1. Under the re-cut partition, how many of a 210-household draw (seed 7, `draw_region=True`)
does `cell_matched_site` accept?**

At HEAD's artefact the answer is 2 (both London's cells). I predict **a small perturbation, not a
wipe-out: 0–6, and most likely still around 2.** Reasoning: the drivers are unchanged, the
partition is the same k-means at the same `random_state` over 11% more occupied cells, and London's
joint cell held 28 of 175,188 cells before. A re-cut moves *which* cells, not the order of
magnitude. If the answer is exactly **0 for every one of the 210**, the item's phrase "accepts
nothing" is right about the effect while being wrong about the cause, and I will say so in those
words.

**Q2. Is the committed `REACHABILITY_WITNESS` (50.4689, -4.1492) still inside all three of London's
cells under the re-cut?**

I predict **NO.** That constant has already expired once for exactly this reason (it was moved on
2026-09-07 when the placement went from postcode centroids to the UPRN record), and a witness is a
measurement of a partition, not of a place. If it has expired, the accept branch is again
unreachable from the committed answer with no `~/.cache` — the R15 failure the constant exists to
prevent — and re-measuring it is part of landing the re-cut, not a follow-up.

**Q3. Does landing the re-cut move any published figure?**

I predict **yes, and downward**: the `all_three` coverage the module publishes falls from 2.0% to
1.91%, and the per-driver table moves on all three. These are not a recalculation of the same
thing — they are the same quantity measured against a placement the first cut could not see — so
both go in the module beside each other, superseded figure named as superseded.

## What would refute me

Q1 answering 0 refutes "small perturbation". Q2 answering yes refutes "a witness expires with its
partition" for this re-cut. Q3 is close to arithmetic and is registered for completeness, not
because it is in doubt.

## What this pre-registration does NOT cover

The archive **widening** — new Open-Meteo pulls beyond C1–C4. The re-cut is a lookup fix and
changes the archive's breadth by nothing; the module already says so. Whether the widening lands in
this turn is a scope call, and the shared tree holds a week-stranded `tools/pull_book_weather.py`,
`tools/build_weather_world.py` and a 7.9 MB `sim/weather_world/` (all mtime 2026-09-08/09) that a
widening has to reckon with rather than duplicate.
