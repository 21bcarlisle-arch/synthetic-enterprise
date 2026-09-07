# PRE-REGISTRATION — what cutting `sim/weather_cells/site_cells.json` over the drawn population must show

**Severity:** RECORDED · **Lane:** W1_market_weather · **Atom:** W1_14

**Written:** 2026-09-07, BEFORE any of the numbers below were computed, by the delivery seat.
**Claim:** `W1_14-cut-the-artefact-over-the-drawn-population`

RECORDED and not BLOCKING: a pre-registration asserts nothing about the tree. It fixes the
predictions before the run so the result can refute them.

---

## The question

`simulation.weather_cell_siting.cells_for_location` is a lookup into a precomputed TABLE keyed to
~11 m. `derive()` is handed 7 locations (`KNOWN_LOCATIONS` + `REACHABILITY_WITNESS`), so the table
holds 7 keys. Since W2_18 landed (`ec8a18710`), every drawn household carries a real coordinate
drawn from `sim/household_siting/region_household_frame.csv`, and **0 of 210 resolve**: an arbitrary
coordinate cannot collide with a 7-key table.

The direction is to cut the artefact over the population that actually gets looked up in it, or to
establish that it cannot be.

## What I already know (not a prediction — read from the source before writing this)

`tools/household_siting_frame.py:295-314` builds each frame row's coordinate as
`round(float(d["latitude"][i]), 4)` and `round(lon_grid[searchsorted(ys, north), searchsorted(xs,
east)][i], 4)`. `simulation/weather_cell_siting._occupied_space()` builds the siting's coordinates
by the *identical* two expressions over the same `weather_cell_drivers.drivers()` array.

So the lookup population is **closed and enumerable**: it is exactly the distinct `(lat, lon)` pairs
in the frame, and they are the derivation's own grid cells at the derivation's own precision. The
join is an EQUALITY, not a nearest-neighbour, and nothing has to be fabricated to do it. That is
what makes a bounded re-cut possible at all.

## Predictions

Each is falsifiable and each is recorded here before the run.

1. **Join rate.** Of the distinct frame coordinates, **≥ 99.9 %** match an occupied land cell of
   `_occupied_space()` by exact 4-dp `(lat, lon)` equality. *If this comes back materially below
   100 %, the two constructions have diverged and the honest answer is a refusal, not a re-cut with
   a hole in it.*
2. **No key collisions.** The distinct 4-dp keys number the same as the distinct frame rows'
   coordinates: at 1 km spacing, 4 dp (~11 m) cannot merge two grid cells. *A collision means the
   key is lossy and the artefact would silently site one cell as another.*
3. **Resolution after the re-cut.** Of 210 drawn households (seed 7, `draw_region=True`),
   **210/210 resolve** — `cells_for_location` returns cells, not `None`. This is the number the
   whole atom turns on, and it is 0/210 today.
4. **Archive match after the re-cut.** Of those 210, the count for which `cell_matched_site` returns
   an archive site is **low, and I predict 0–8** (0–4 %). *The re-cut is a LOOKUP fix, not an
   archive-breadth fix.* If this comes back high, my reading of the coverage figure (`all_three` =
   2.0 % of GB households) is wrong and I must say so rather than bank the good news.
5. **The refusal changes its subject, and the count of refusal REASONS does not fall to zero.** A
   drawn household that resolves but shares no archive site's cells must still be refused, with the
   third refusal ("shares no archive site's cells on all three drivers"), not the second ("not in
   the derived artefact"). *A re-cut that made every refusal disappear would mean I had wired a
   nearest-anything fallback, which this seam exists to refuse.*
6. **Size.** The bulk table is **3–5 MB** on disk. `sim/household_siting/region_household_frame.csv`
   is 5.0 MB and committed, so this is the established order of magnitude for a committed frame in
   this repo and needs no new decision. *If it comes out above ~10 MB the shape is wrong and I
   should encode more tightly rather than commit it.*

## What "done" means for this turn

The direction says no exit test is written, so I am fixing it here, before the answer is known:

* `cells_for_location` resolves for a coordinate drawn by
  `simulation.household_siting.coordinate_for_customer` for every region in the frame — proved by a
  test that DRAWS rather than by a hand-picked coordinate.
* The small `site_cells.json` keeps its present role (archive sites, coverage, witness, the
  human-readable answer) and does not grow to megabytes: `load()` is on the lookup path.
* The bulk table cannot silently drift from the partition that cut it — a control refuses when the
  two artefacts disagree on `cells_per_driver`, `drivers`, `partition` or `occupied_land_cells`.
* The fail-closed property survives: a coordinate in NEITHER table is still refused with its named
  reason, and no nearest-cell fallback is added anywhere.
* The reachability witness still resolves and still matches C1 — i.e. the accept branch is still
  provably reachable *after* the re-cut. (This is exactly what the 2026-09-07 re-derivation broke
  once already; see `REACHABILITY_WITNESS`'s own note.)

## What would make me stop and record "it cannot be"

Prediction 1 failing, or the bulk table exceeding ~10 MB with no tighter encoding available. In
either case the finding is the deliverable and the artefact stays as it is.
