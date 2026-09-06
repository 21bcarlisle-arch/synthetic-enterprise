**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `W2_18-coordinate-at-the-draw` · **Class:** no_caller_and_never_runs

# RESULT: a drawn household now has a coordinate, and it was sourced rather than invented — and the pull that built it dropped Wales in silence until the count check refused

**Measured 2026-09-06 BST in the shared tree.** Sources: Census 2021 TS041 (households per output
area), OS Open UPRN (addresses per 1 km cell), the ONS `OA21_PARNCP25_LAD_CTYUA_RGN_CTRY_EW_LU`
lookup (output area to region), and the HadUK-Grid 1 km normals (each land cell's true latitude and
longitude). Build `python3 -m tools.household_siting_frame --pull --build`; artefact
`sim/household_siting/region_household_frame.csv` with its manifest beside it. Pull log at
/tmp/oa_region_pull.log.

## What the drawn item asked, and what the answer turned out to be

> *Give a drawn household a COORDINATE in `simulation/population_draw.py`, or establish and record
> that it cannot be sourced.* … *the region marginal gives a REGION and the cells are keyed to a
> POINT, so a coordinate must be sourced, never invented.*

**It can be sourced, and every link was already pulled and cached in this repository for the
weather-cell derivation.** Only one column was new. The chain:

| link | source | what it answers |
|---|---|---|
| households per 2021 output area | Census 2021 TS041 (nomis) | how many households there are |
| addresses per 1 km cell | OS Open UPRN | where inside an output area they sit |
| output area → ONS region | ONS `OA21_..._RGN_CTRY_EW_LU` (**new**) | which region an output area is in |
| 1 km cell → lat/lon | HadUK-Grid normals' own auxiliary coordinates | the coordinate itself |

Composed, that is the household-weighted distribution over the 1 km cells each of the curriculum's
ten regions actually occupies. A drawn household's coordinate is a **draw from its own region's
household distribution** — a cell with twice the households is twice as likely — carrying the very
coordinates the weather derivation is cut over.

`to_customer_dict` renders it. **The coordinate follows the region and has no dial of its own**:
there is no household distribution for a region that is not a real region, so with the default
placeholder region it stays honestly `None`, and with the director's region curriculum on
(`draw_population(draw_region=True)`, which is what `simulation/live_population.py` uses) every
household is sited.

## FIGURES

**The frame.** 144,542 occupied 1 km cells across the ten regions, carrying **24,664,503
households** — against a published England-and-Wales 2021 census total of ~24.8 million, which is
the independent check that the join did not lose a slice. 46,270 Scottish output areas are dropped
and counted (no slot in the region marginal); 115,364 households (0.47%) sit in cells the HadUK
land mask calls sea and are counted rather than absorbed. Artefact 5.07 MB.

**The draw, seed 7, `acquisitions_per_year_lambda=40`, and this is the exact inversion of what the
W1_14 finding measured this morning:**

| | before (2026-09-06 AM) | now |
|---|---|---|
| `lat is None`, `draw_region=True` | 210 / 210 (**100%**) | **0 / 210** |
| sited households | 0 | **210** |
| distinct coordinates | 0 | **209** |
| latitude range | — | 50.226 … 55.082 |
| latitude sd | — | 1.146° |
| `lat is None`, default draw | 210 / 210 | 210 / 210 — **unchanged, and correct** |

**What a centroid would have thrown away.** Household-weighted within-region spread of the three
heat-load drivers, from `--measure`:

| region | cells | households | winter temp sd | winter temp range |
|---|---|---|---|---|
| London | 1,895 | 3,415,930 | 0.292 | 4.03 … 6.32 |
| East | 19,057 | 2,614,129 | 0.282 | 3.93 … 5.93 |
| West Midlands | 13,749 | 2,429,177 | 0.297 | 2.18 … 5.73 |
| East Midlands | 15,704 | 2,036,392 | 0.309 | 1.94 … 5.34 |
| Yorkshire and The Humber | 14,384 | 2,327,732 | 0.385 | 1.38 … 5.45 |
| North East | 7,075 | 1,170,011 | 0.457 | 0.63 … 5.64 |
| North West | 12,372 | 3,143,477 | 0.508 | 0.86 … 6.02 |
| South East | 19,417 | 3,773,519 | 0.514 | 3.66 … 6.97 |
| Wales | 17,726 | 1,331,257 | 0.672 | 1.96 … 7.30 |
| South West | 23,163 | 2,422,878 | **0.687** | 3.24 … 8.81 |
| **England and Wales** | 144,542 | 24,664,503 | **0.640** | 0.63 … 8.81 |

**The South West's households vary more in winter temperature among themselves than England and
Wales do as a whole** (0.687 against 0.640), and Wales does the same on wind (1.019 against 0.764).
A single point for those regions does not lose a refinement; it loses more than the region label
was ever carrying. That is the measured answer to "why not a centroid", and it is the reason the
frame is a distribution rather than a lookup of ten points.

## The defect this build hit, and the wrong diagnosis kept beside it

The pull refused itself: **178,605 of 188,880 output areas**, caught by a count check written for a
different failure (nomis silently capping a request at 25,000 rows).

The obvious culprit was offset paging over a large ordered set, so the pager was rewritten to seek
on the sort key instead. **It returned 178,605 — exactly the same number, by a method that cannot
skip a row.** The pager had never been the problem.

The real cause: **all 10,275 of Wales's output areas carry a NULL region column**, because Wales is
a country and that table's region column is England's. `if not rgn: continue` was dropping every
Welsh household — 5.7% of the curriculum's book and one of its ten regions — while the other nine
looked complete. Asked of the server afterwards: 10,275 Welsh rows, 10,275 null regions,
178,605 + 10,275 = 188,880.

Three things worth keeping from that:

1. **The count check found a failure it was not written for.** It exists because a paged service
   once returned 13% of England with no error. It caught a null column instead. That is the
   argument for asserting the total rather than trusting the loop.
2. **A wrong cause survived one confirming change.** Rewriting the pager was a plausible fix that
   changed nothing, and only the identical number refuted it. One variable, one rerun.
3. `test_WALES_SURVIVES_A_NULL_REGION_COLUMN` holds it, **proven by poison round** — reverting the
   country fallback kills it.

## Why a centroid was not the answer

`simulation/adoption_geography` already holds one lat/lon per region, on the fourteen GSP groups.
One point per region puts every household in a region into a single derived weather cell and
collapses the 21-cell partition the derivation priced — the exact direction
`weather_cell_weights` says an unweighted fit fails in. `household_siting_frame.measurement()`
prices this rather than asserting it: the within-region household-weighted spread of each driver
is what a centroid throws away, and it is reported beside the national spread.

## What this does NOT close, stated plainly

**A sited household is still not sited in the derived cells.** `weather_cell_siting.
cells_for_location` looks a coordinate up in the committed artefact's `locations` map, which holds
only the locations `derive()` was run over — the four archive sites, the supply book and one
reachability witness. A drawn household's coordinate is not among them, so the lookup still returns
None, for a **different and correctly-named reason**. The seam's no-coordinate refusal — issued for
100% of drawn households until today — no longer fires, and
`test_the_weather_seam_no_longer_refuses_a_drawn_household_for_want_of_a_coordinate` is pinned to
that and nothing more.

Closing the rest is W1_14's: either site the frame's cells in `derive()`, or carry each frame row's
three cell labels in the frame itself (they are computed over these same land cells, deterministic
at `random_state=0`). Neither is a coordinate problem any more.

**W1_14's own control is unaffected and correctly so.**
`test_no_household_in_this_world_can_reach_the_cell_substitution_branch` asserts over
`draw_population(7, ...)` — the DEFAULT draw, placeholder region, no coordinate — so it stays green
and stays true. It is worth noting that it is therefore blind to the curriculum-on world, which is
the one `live_population` runs; that is a narrowing to record, not a fault to fix here.

**One world-fidelity consequence, named because it is a baseline change (R13).**
`simulation/run_phase2b.py` reads `location.lat or DEFAULT_LATITUDE_DEG` — 53.0 for every drawn
household until now. Under `draw_region=True` those households now carry their own latitudes.
Decided blind to company results, for a fidelity reason, and it makes the book harder rather than
easier: a spread of real latitudes replaces a single convenient one.

## What was unblocked on the way

`docs/staging/SEAT_PREREG_WEATHER_CELL_BRANCH_REACHABILITY_2026-09-06.md` was half-moved to
`records/` — the deletion staged, the addition not — which failed `finding_classes --check` for
every lane in this tree. The two copies were byte-identical; the move is completed in this commit.
