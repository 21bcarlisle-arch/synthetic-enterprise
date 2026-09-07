**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_20_household_weights_per_cell_from_the_census

**Knowledge:** none -- the weather-cells knowledge page is deliverable 1 of the weather ruling and is
not yet written. These are the rows it will be built from; the declaration is replaced when the page
lands.

# Half of Britain's land has nobody on it, and weighting for that halves the variation the cells must span

**Measured 2026-09-06**, delivery seat, `W1_20`. Reproduce with
`python3 tools/weather_cell_weights.py --weighted`.

The weather ruling's decision 9, verbatim: *"Household weights come from the censuses (England &
Wales 2021, Scotland 2022) via postcode, NOT from the SIM's drawn population."* Weighting the cells
by the population we drew would make the coverage curve a statement about our own draw. The curve
would look identical and nothing downstream could tell.

---

## The join

| source | what it gives | size |
|---|---|---:|
| ONS Postcode Directory (live) | OSGB easting/northing and output area per postcode | 1,675,166 live residential GB postcodes |
| Census 2021 **TS041** (nomis `NM_2059_1`) | households per 2021 output area, England & Wales | 188,880 areas |
| Scotland's Census 2022 **UV402** | households per 2022 output area | 46,363 areas, 2,508,542 households |

**27,283,137 households placed.** England, Wales and Scotland's published totals sum to 27.29
million, so the join loses nothing material. What it *does* lose is named rather than absorbed: 128
census output areas have no live residential postcode, 1,434 postcode cells fall in squares the
HadUK grid classifies as sea (coast and estuary), and those hold **160,886 households — 0.6%**.
Final figure: **27,122,251 households on 121,668 land cells.**

**The Choice.** A census output area holds several postcodes and does not say how its households
divide between them, so they are split **equally across the area's live residential postcodes**. The
alternative — the whole area at one population-weighted centroid — was rejected because a rural
output area can span tens of kilometres. That is not a free choice and it was measured rather than
waved through: **17.6% of households (4.8 million) land in a different 1 km cell** under the two
methods. It is load-bearing, and the reason the split wins is that the error it makes is
sub-kilometre while the error the centroid makes is tens of kilometres.

## The first finding: half the land is empty

**121,668 of 245,077 land cells hold at least one household — 49.6%.** An area-weighted derivation
spends half of its effort on cells nobody lives in.

> **CORRECTED 2026-09-06 — THE DENOMINATOR WAS THE UNITED KINGDOM, NOT GREAT BRITAIN.** HadUK-Grid's
> land mask covers the whole UK, and **14,911 of its 245,077 land cells are outside Great Britain**.
> ONSPD carries no British grid reference for Northern Irish postcodes and this company's market is
> GB, so every one of those cells arrived with zero households and was counted as *empty British
> land*. Over GB alone the mask is **230,166 km²** — within 0.5% of the published GB land area of
> 228,991 km² — and **121,668 of them hold a household, 52.9%**, not 49.6%.
>
> "Nearly half of Britain's land holds nobody" survives as prose; the number moves. Found when the
> director asked why Scotland had visible gaps on the published map: the answer for Scotland was
> genuine terrain, and the same question applied to the rest of the blank found this. The
> discriminator is distance to the nearest live GB postcode, which is sharply bimodal — 108,533
> empty cells within 10 km, 965 between 10 and 20, and 13,207 beyond 50.

> **CORRECTED AGAIN 2026-09-06 — AND THIS TIME THE METHOD, NOT THE DENOMINATOR.** The director
> asked whether it was really true that 47% of GB square kilometres hold no address. It is not.
> Households were placed at **postcode centroids**, and a centroid is a point: a kilometre of
> scattered dwellings whose postcode centroid fell in the next cell read as empty.
>
> **OS Open UPRN** — a published grid reference for all 41,629,393 addressable properties in GB —
> settles it directly. **195,045 of 230,166 GB land cells (84.7%) hold at least one address.** What
> the centroid method was measuring, to within half a percent, was *"ten or more addressable
> properties"*: 120,464 cells, 52.3%, against its own 121,668. Of its occupied cells, exactly **two**
> hold no UPRN — the placement was right where it put things; the absence overstated.
>
> Households now follow address density within each output area, with the census still fixing the
> totals. **Occupied GB land: 175,188 cells, 76.1%.**
>
> **And every answer resting on the weights is unchanged.** Re-placing all 27,283,137 households
> moves the household-weighted driver means by **1.2%, 1.0% and 0.1% of a standard deviation**, and
> the cell counts are identical — 34, 89 and 987 for the shared partition, about 21 per driver. The
> addresses the old method missed are 1.2% of Britain's: a long thin tail of isolated properties,
> too few to move a weighted mean and more than enough to ruin a map. Measured, not hoped:
> `python3 tools/weather_cell_weights.py --choice-cost`.

> **CORRECTED A THIRD TIME 2026-09-07 — the centroid is gone entirely.** The director asked why
> dwellings were not placed directly, and the version above was still centroid-anchored: households
> went to the 3×3 neighbourhood of each postcode, weighted by address counts there. Two errors
> survived that — **20,959 address-bearing cells lay outside every window**, and **94.5% of GB's
> addresses sat in cells claimed by five or more output areas**, each sizing its share by all the
> addresses present including its neighbours'.
>
> The **ONS UPRN Directory** carries every address's grid reference *and* its output area in one
> row, so each area's households now go to the cells its own addresses occupy and nowhere else.
> **Occupied GB land: 194,861 cells, 84.7%** — exactly the share that holds an address, because
> households now sit where addresses are.
>
> **And it cost 70 seconds once and half a second per run.** Reducing 41,386,453 addresses to
> 690,132 (output area, cell) pairs is the one-off; the placement is a dictionary join. Nothing here
> was ever expensive.
>
> **The cell counts did not move: 34, 89 and 987 for the shared partition, about 21 per driver.**
> The household-weighted driver means shifted by 1.28%, 1.07% and 0.11% of a standard deviation
> between the second placement and this one — which is what makes the analysis above sound rather
> than lucky, and is why it is stated as a measurement.




And the occupied half is itself extremely concentrated:

| share of GB households | cells | share of land cells |
|---:|---:|---:|
| 50% | 6,160 | 2.5% |
| 80% | 15,215 | 6.2% |
| 90% | 23,435 | 9.6% |
| 95% | 35,586 | 14.5% |
| 99% | 80,826 | 33.0% |

## The second finding: weighting halves the spread

| driver | area-weighted sd | household-weighted sd | ratio |
|---|---:|---:|---:|
| annual temperature | 1.459 °C | 0.794 °C | 0.54 |
| winter temperature | 1.296 °C | 0.689 °C | 0.53 |
| annual wind | 1.388 m/s | 0.798 m/s | 0.58 |
| annual sunshine | 203.0 h | 126.8 h | 0.62 |

And the household-weighted spread itself, which is the span every later sensitivity is quoted over:

| driver | 5th percentile | median | 95th percentile |
|---|---:|---:|---:|
| annual temperature | 9.00 °C | 10.45 | 11.69 |
| winter temperature | **3.95 °C** | 4.95 | **6.13** |
| annual wind | **2.98 m/s** | 3.85 | **5.61** |
| annual sunshine | 1320 h | 1544 | 1734 |

**The variation the cells have to span is roughly half what `W1_19`'s unweighted table implied**, on
every driver. Britain's climatic extremes are in the uplands and the far north-west, and almost
nobody lives there. Medians move the way that implies: the household median cell is 1.0 °C warmer,
0.57 m/s calmer and gets 116 more hours of sun a year than the land median.

**This is a direct input to `W1_21`.** For any given similarity radius, halving the spread reduces
the number of cells needed. `W1_19` predicted the coverage curve would rise faster than a
three-dimensional argument suggests, on the grounds that two drivers share one gradient; this is a
second, independent reason pointing the same way, and the two compound.

## The third finding: the winter correlation has a THIRD value, and it is zero

`W1_19` tested the ruling's prediction that *"winter temperature and wind are positively
correlated"* and reported it refuted at **−0.430** across land cells, while noting the repo's own
temporal measurement of **+0.507**. Weight the same land cells by households:

| reading | winter temp × winter wind |
|---|---:|
| in time, at a place (`W1_COUPLED_WEATHER_CASCADE_DISCOVER`) | **+0.507** |
| across land cells, area-weighted (`W1_19`) | **−0.430** |
| **across land cells, household-weighted (this) ** | **+0.060** |

**Among the places people actually live, the spatial relationship is essentially absent.** The
negative spatial correlation was a fact about empty uplands: they are cold and they are windy, and
they dominate an area-weighted fit while contributing almost no households.

The same collapse happens to annual temperature × wind, from −0.592 to **−0.173**. It does *not*
happen to the pair that carries `W1_19`'s clustering argument: annual temperature × sunshine falls
from +0.841 to **+0.678**, still high. The two-axis expectation for `W1_21` survives weighting.

> **This qualifies `W1_19`'s verdict and the qualification is recorded there too.** The ruling's
> prediction is not refuted for households; it is *undetectable* for them, at r = +0.06. What
> `W1_19` refuted was a claim about land, which is not the claim the ruling needed to make. The
> useful statement is that this pair has three values, one per question, and no one of them can be
> quoted without naming which.

## Limits

- **The weights are a snapshot, not a series.** Census 2021/2022 against 1991–2020 normals. Where
  Britain built houses over that window is not modelled; for cell derivation the effect is small,
  for anything longitudinal it would not be.
- **Household counts are disclosure-controlled.** NRS perturbs small counts and ONS applies its own
  protection. At output-area level that is noise; at 1 km aggregate it is invisible.
- **Northern Ireland is out.** HadUK covers the UK and the company's market is GB; NI postcodes
  carry no OSGB reference in ONSPD.
- **No elevation correction.** The ruling asks for grid-to-house-height adjustment (section 4). It
  is a postcode join like this one and belongs here, and it is not done: registered as the open half
  of this atom rather than implied by its absence.
- **A household is not a customer and not a meter.** These weights answer "where do people live",
  which is what the director's question asked. Meter counts per postcode are a different and also
  available series, and the difference between them is a question for stage 2, not this one.
