**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_19_the_three_drivers_per_land_cell_from_the_normals

**Knowledge:** none -- the weather-cells knowledge page is deliverable 1 of the weather ruling and is
not yet written. These are the rows it will be built from; the declaration is replaced when the page
lands.

# The three heat-load drivers per land cell — and one prediction confirmed, one refuted by a sign

**Measured 2026-09-07**, delivery seat, `W1_19`. Source: Met Office HadUK-Grid 1 km, 1991–2020
30-year monthly normals for `tas`, `sfcWind` and `sun`, pulled 2026-09-05 (318 files, 19.8 GB, zero
failures). Raw grids stay out of the repo as the ruling requires.

---

## The grid, and what is actually in it

The array is 1450 × 900 = 1,305,000 cells. **245,077 are land** — 18.8%. The rest is sea and
carries NaN. That number matches the figure already recorded in `ASSUMPTIONS.md` from the pull, so
the read is independently corroborated. **A mean taken over the full array is a mean over the
Atlantic**, which is why the land mask is stated here rather than treated as an implementation
detail.

| driver | min | median | max | unit |
|---|---:|---:|---:|---|
| annual mean temperature | 1.33 | 9.45 | 12.19 | °C |
| winter mean temperature (DJF) | −2.96 | 4.43 | 8.81 | °C |
| annual mean wind speed | 1.16 | 4.42 | 16.36 | m/s |
| annual sunshine duration | 783.5 | 1427.7 | 1991.5 | hours |

Sunshine is a **duration**, not irradiance — HadUK publishes no irradiance product. The ruling
anticipated this and requires the conversion to be registered as a Choice with its alternative
named. It is not made here: these are the source quantities.

## The ruling's two falsifiable predictions

Its expected-shape block predicts *"N cells capture ≥95% of household-weighted variation… the
north–south gradient dominates solar; winter temperature and wind are positively correlated."*
Across the 245,077 land cells:

| pair | correlation |
|---|---:|
| latitude × sunshine | **−0.806** |
| latitude × annual temperature | −0.754 |
| annual temperature × sunshine | **+0.841** |
| annual temperature × annual wind | −0.592 |
| **winter temperature × winter wind** | **−0.430** |
| winter wind × sunshine | −0.381 |

**The north–south gradient does dominate solar. Confirmed**, at −0.806.

**Winter temperature and wind are NEGATIVELY correlated. The prediction is refuted as written —
and both signs are right.**

## The sign flips because the question does

The ruling's claim is true *in time* and false *in space*, and this project has already measured the
temporal half: `W1_COUPLED_WEATHER_CASCADE_DISCOVER.md` records **winter temp/wind corr +0.507**,
the cold-and-still joint tail with a 2.34× decile lift. In a given winter, at a given place, cold
snaps arrive with still air.

Across *places*, the opposite holds: the windiest GB cells are northern, upland and exposed, and
those are the cold ones. −0.430.

Both are real. They answer different questions and they must not be pooled:

- **For deriving cells** — partitioning space — the SPATIAL correlation is the relevant one. It says
  wind carries information about a location that temperature does not, in the opposite direction to
  what the ruling assumed.
- **For persistence, synchrony and hedging** (`W1_22`, and use case 3.1 later) the TEMPORAL
  correlation is the relevant one, and it is positive.

Quoting one where the other belongs would be this project's recurring definitional failure: two
correct figures whose ratio, or whose sign, is not the quantity anybody wanted. The ruling's
expected-shape line should be read as a claim about time and is **left standing for that reading**;
what is refuted is the spatial reading, which is the one cell derivation needs.

## The finding that matters most for the cells

**Annual temperature and sunshine correlate at +0.841 across space.** Two of the three phase-1
drivers carry substantially the same spatial signal, because both are dominated by the same
north–south gradient (−0.754 and −0.806 against latitude).

That is a direct input to `W1_21`: a clustering on three drivers is not clustering on three
independent axes. It should be expected to behave closer to a two-axis problem — a north–south
temperature-and-light axis, and a wind-exposure axis largely orthogonal to it — which will make the
coverage curve rise faster than a naive three-dimensional argument predicts. It also means a cell
set derived on temperature alone may approximate one derived on temperature-and-sunshine closely,
and that is a comparison `W1_21` should make rather than assume.

## Limits

Normals are 1991–2020 averages, so nothing here says anything about year-to-year variability,
persistence, or synchrony — those need the daily series, which is `W1_22`'s subject and is already
on disk. Correlations are unweighted over land cells: **household weighting (`W1_20`) will change
them**, because the population is not spread evenly over the uplands that supply the wind tail.
Elevation correction to house height is not applied here.
