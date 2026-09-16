**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_19_weather_cell_derivation · **Class:** figures_on_a_superseded_clock

# FINDING: five research documents publish the centroid method's 121,668 occupied cells as current fact, and the placement moved three weeks after they were written

**Measured 2026-09-07 while re-cutting `site_cells.json`. Filed rather than fixed, and the boundary
is stated below so the next reader can see what was deliberately left.**

## What is stale

The household placement moved from postcode centroids to the OS Open UPRN address record on
2026-09-06: **121,668 occupied 1 km cells → 175,188**. Five published documents still carry the old
count, in the present tense, as the size of the space their conclusions were drawn over:

| document | line | what it says |
|---|---|---|
| `how_many_weather_cells_britain_needs_and_why_the_answer_is_a_curve.md` | 24, 38, 54 | "27,122,251 households on 121,668 occupied 1 km cells"; "121,668 of them hold a household, 52.9%" |
| `half_the_land_is_empty_and_weighting_halves_the_variation.md` | 31, 43, 51 | "Final figure: 27,122,251 households on 121,668 land cells" |
| `one_grid_three_jobs_and_wind_is_not_the_awkward_one.md` | 19 | "over the 121,668 occupied land cells" |
| `pv_yield_cannot_be_keyed_on_latitude.md` | 21 | "Clustering the 121,668 occupied cells" |
| `cold_snaps_arrive_in_blocks_and_britain_has_no_second_weather.md` | 103 | "89 cells, not 121,668" |

`tools/generate_weather_cells_data.py:189` carries it in a comment too.

## Why this is a finding and not a typo

**121,668 is not a stale number, it is a stale METHOD, and the documents' conclusions rest on it.**
The curve in the first document is the one W1_27 read as the build decision "about 21 cells per
driver". That curve was computed household-weighted over the centroid placement. The placement now
occupies 44% more cells and the director's own challenge — that 47% of GB kilometres holding no
address was implausible — is what moved it.

So the open question is not the printed count. It is whether **the curve itself moves**, and with it
the 21-cells-per-driver decision that every derived cell in `site_cells.json` is cut on. Restating
the number without re-running the curve would be worse than leaving it: it would make five documents
look current while their conclusion was still the old placement's.

## What was fixed today and what was not

The blocking finding
(`SEAT_FINDING_THE_WEATHER_CELL_ARTEFACT_PUBLISHES_THE_CENTROID_METHODS_COVERAGE...`) asked for the
artefact regenerated and **"the four percentages moved wherever they are quoted"**. Both are done —
mostly by a concurrent lane in `f27695607`, which regenerated the artefact and moved the four
archive-coverage percentages (20.5 / 30.7 / 27.9 / 3.5 → 20.4 / 27.8 / 17.2 / 2.0) in the module
docstring, the refusal assertion and the W1_14 map row. This lane re-derived the same artefact
independently and every shared key matched byte-for-byte, then cut it over the drawable population.
That finding is archived by this commit.

**`121,668` is a different figure from those four**, and it is the derivation's, not the seam's. It
is left standing, deliberately, because closing it means re-running the per-driver coverage curve
over the UPRN placement and then deciding whether 21 still is the answer — which is W1_19/W1_27's
work and a bigger job than one turn.

## What to do

1. Re-run `weather_cell_derivation.per_driver_curve` over the UPRN placement.
2. Compare the elbow against 21. If it moved, `CELLS_PER_DRIVER` and every artefact cut on it are
   downstream of that, including the one re-cut today.
3. Only then restate the five documents — with the new curve beside the old, not over it.

**Until step 2 is done, nobody should read the five documents as describing the current world**, and
that is the whole reason this is filed rather than silently carried.
