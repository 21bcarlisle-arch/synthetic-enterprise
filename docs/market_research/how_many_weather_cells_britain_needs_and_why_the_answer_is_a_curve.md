**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_21_the_cells_and_the_level_coverage_curve

**Knowledge:** none -- the weather-cells knowledge page is deliverable 1 of the weather ruling and is
not yet written. This document is the curve it will publish; the declaration is replaced when the
page lands.

# How many weather cells Britain needs — 34, 89 or 987, and the reason it is a curve

**Measured 2026-09-06**, delivery seat, `W1_21`. Reproduce with
`python3 tools/weather_cell_derivation.py --curve` and `--choice-sensitivity`.

The director's question, verbatim: *"how much granularity is needed to capture, say 99%, versus 95 or
90% of the variation for households across these primary heat load variables"*.

---

## What was measured, said before the answer

A percentage of variation means nothing until three things are fixed, and inferring them from the
answer afterwards is this project's most expensive recurring failure.

1. **Whose variation — households, not land.** `W1_20` established that half of GB's land cells hold
   nobody, and that the empty half is the climatic extreme. Every headline figure here is
   household-weighted over 27,122,251 households on 121,668 occupied 1 km cells.
2. **Variation in what — three drivers.** Winter mean temperature (heat demand), annual mean wind
   speed (infiltration), annual sunshine duration (solar gain). Annual mean temperature is *not* a
   fourth: it correlates 0.936 with winter temperature. Annual and winter wind correlate 0.996, so
   there is only one wind measure to have.
3. **Measured how.** Household-weighted k-means on the standardised drivers; captured share is
   1 − within/total weighted sum of squares. Cells are derived, **blind to LDZ, GSP and SAP
   boundaries** as the ruling requires.

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




## The answer

| cells | households covered | winter temp RMS error | wind RMS | sunshine RMS |
|---:|---:|---:|---:|---:|
| 1 | 0.0% | 0.689 °C | 0.798 m/s | 127 h |
| 5 | 65.9% | 0.404 | 0.494 | 69 |
| 13 | 82.3% | 0.283 | 0.358 | 51 |
| 21 | 87.0% | 0.257 | 0.293 | 43 |
| **34** | **90.5%** | 0.216 | 0.256 | 37 |
| 55 | 93.2% | 0.182 | 0.217 | 32 |
| **89** | **95.2%** | 0.151 | 0.182 | 27 |
| 233 | 97.6% | 0.108 | 0.127 | 19 |
| **987** | **99.2%** | 0.061 | 0.072 | 11 |
| 2584 | 99.7% | 0.040 | 0.047 | 7 |

**90% takes 34 cells. 95% takes 89. 99% takes 987.**

**The last four points cost eleven times the cells the first ninety did.** That is the answer to
"why a curve and not a number": there is no natural cell count, only a price list. Between 34 and 89
cells a supplier buys 4.7 points of coverage; between 89 and 987 it buys 4.0 points for eleven times
the granularity. Anyone choosing 99% because it sounds rigorous is paying 29× the cells of 90% for a
winter-temperature error that falls from 0.22 °C to 0.06 °C — and 0.22 °C on a winter mean is far
below the error in any household heat model we will build.

## Weighting for where people live is worth about 40% of the cells

The same clustering over the same cells, unweighted:

| target | household-weighted | area-weighted | 
|---|---:|---:|
| 90% | **34** | 55 |
| 95% | **89** | 144 |
| 99% | **987** | 1597 |

The comparison holds the cell population fixed and varies only the weighting, so the difference is
attributable. An area-weighted derivation asks for **60% more cells at every target** and spends the
extra resolving places with no customers in them.

## The Choice, and the number that prices it

Standardising each driver by its own spread gives the three equal say — a statement that a one-sigma
move in sunshine matters as much to a heat bill as a one-sigma move in winter temperature. That is
almost certainly false; temperature dominates. The honest alternative weights each driver by its
coefficient in a fitted heat-load model, and **this company has no such model yet** (`W2_21`).

So the Choice was made conservatively and then *checked*, because "conservative" was a falsifiable
claim about this data rather than a reassurance:

| metric | 90% | 95% | 99% |
|---|---:|---:|---:|
| equal weighting (published above) | 34 | 89 | 987 |
| temperature-dominant 4 : 1 : 1 | 13 | 34 | 377 |
| temperature only | **5** | **8** | **21** |

The claim holds at every target and in the right direction: **the published counts are an upper
bound.** And the bottom row is the most useful line in this document —

> **Twenty-one cells capture 99.3% of the household-weighted variation in winter temperature.**
> Five capture 91%. If heat load turns out to be as temperature-dominated as the physics suggests,
> Britain needs about twenty weather cells, not a thousand.

That is a result about the *shape of the problem*, not about our method: temperature varies smoothly
across a small island, and the places people live occupy a narrow part of its range. What forces the
count into the hundreds is insisting that wind and sunshine be resolved to the same relative
precision, and nothing yet establishes that they should be.

## What this says about the industry's own geography

The clustering never sees LDZ, GSP or SAP boundaries. But it can be read at their counts, and that
is a stronger statement than a boundary overlay would be:

| industry partition | count | best possible coverage at that count |
|---|---:|---:|
| gas Local Distribution Zones | 13 | 82.3% |
| GSP groups | 14 | 83.1% |
| SAP climate regions | 21 | 87.0% |

These are **upper bounds on what those partitions can achieve**, because the derived cells at that
count are optimal for weather and the real boundaries are not — LDZs follow gas networks and GSP
groups follow electricity supply areas. So the settlement geography the company receives its data on
resolves at most 82–87% of the weather variation its customers actually experience, and the true
figure is lower. **That gap is the case for deriving cells at all.**

Read the same table under a temperature-only metric and it inverts: at those three counts the best
possible temperature coverage is 98.4%, 98.6% and 99.3%. The industry's geography is not obviously too coarse *for
temperature*; it is too coarse for wind and sun. Which of those readings matters is a question for
`W2_21`'s fitted model, and it is now a decidable question rather than an argued one.

## Limits

- **Level only.** This is annual heat load. Shape is `W1_18`; persistence and cross-cell synchrony
  are `W1_22`, and a hedger cares more about those than about level.
- **The comparators are inferred from counts, not from boundaries.** Actual LDZ/GSP/SAP polygons are
  not in this tree and would need a pull. The counts give upper bounds, which is enough to make the
  argument and not enough to publish a per-boundary figure. Registered as the open half of this atom.
- **k-means on standardised drivers** assumes clusters are roughly spherical in that space. A
  method that allowed elongated cells along the north–south axis would likely do better at low k.
  Not tested.
- **`n_init=1`** with a fixed seed. Repeated runs move the captured share in the third decimal, well
  below anything the argument rests on, but the counts at the 90/95/99 boundaries could shift by one
  sweep step.
- **No elevation correction.** Grid-to-house-height adjustment is registered as the open half of
  `W1_20` and would sharpen the temperature axis.
