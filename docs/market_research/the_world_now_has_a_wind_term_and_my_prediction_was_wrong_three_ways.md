**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_26_the_world_has_no_wind_term_and_the_belief_does

**Knowledge:** none -- this is a SIM fidelity repair, not a knowledge-layer anchor. The published
mechanism it implements is SAP 10.2 / BREDEM and is cited in `simulation/fabric_physics.py` beside
the constant.

# The world now has a wind term, and the prediction filed before measuring it was wrong three ways

**Landed 2026-09-06**, delivery seat, `W1_26`. Reproduce with `tools/weather_driver_sensitivity.py`
and the archive replay in the commit.

`W1_25` found that `simulation/fabric_physics.py` computed infiltration from build era and
insulation and nothing else, while `company/pricing/weather_normalisation_belief.py` carried an
optional `HDD x excess wind` regressor. **The company could fit a household wind-chill coefficient
against a world in which household wind chill did not exist.** This closes it.

---

## What changed

SAP 10.2 / BREDEM: `adjusted infiltration ACH = raw ACH x shelter factor x (wind speed / 4 m/s)`.
Linear, normalised at 4 m/s, straight into `0.33 x ACH x volume`.

- `DailyWeather` gains a **required** `wind_speed_mean_ms`. No default, deliberately: the column has
  been the sixth in every `sim/weather_data/*.csv` since the archive was fetched, sitting next to
  `cloud_cover_pct` in the reader, and was skipped. A default would restore exactly that state and
  make it invisible again. Same reasoning that made `latitude_deg` required in August.
- `FabricParameters` carries its fabric and ventilation halves separately and gains `with_wind()`.
  It **refuses** on a vector built without them rather than returning `self` — a silent no-op there
  is indistinguishable from a calm day, which is how a wind term stays absent while looking present.
- `simulate_premise` applies the day's wind. `premise_trace` reads the column.

**At 4 m/s this is the identity.** `with_wind(4.0)` reproduces the pre-repair parameter vector
exactly, and the whole 60-test fabric suite passes unchanged with the fixtures pinned there. That is
what makes this an extension rather than a re-calibration, and it is what lets the movement below be
attributed to the wind series rather than to the change itself.

## The prediction, and how it did

Filed before `simulate_premise` had ever seen a wind speed, on the archive's all-year site means
(C1 4.03, C2 3.74, C3 3.84, C4 4.61 m/s against the 4.0 reference).

| # | prediction | outcome |
|---|---|---|
| 1 | annual heating demand moves **less than 3%** at every site | **REFUTED** — C1 +3.7%, C4 +8.3% |
| 2 | C4 rises most, **C2 falls** | **HALF** — C4 does rise most; C2 rises too, +1.3% |
| 3 | **day-to-day variance rises materially** | **REFUTED** — it *falls* at three sites of four |
| 4 | largest effects on cold windy days, **cold tail widens** | **REFUTED** — the largest single day is **mild** |

2023 replay, one 1965–80 semi, same household and same temperatures, wind held at the reference
against wind read from the archive:

| site | mean wind | fuel at reference | fuel with wind | level | daily sd change |
|---|---:|---:|---:|---:|---:|
| C1 London | 4.27 | 5,887 kWh | 6,107 | **+3.7%** | −0.8% |
| C2 Manchester | 3.81 | 6,660 | 6,745 | +1.3% | −1.1% |
| C3 Glasgow | 3.78 | 8,009 | 8,020 | +0.1% | −1.8% |
| C4 Cotswolds | 4.74 | 7,038 | 7,624 | **+8.3%** | +4.5% |

## Why I was wrong, and it is one reason for all three

**Heating-season wind is above the annual mean at every site** — DJF means are 4.41, 4.11, 4.28 and
5.19 m/s against annual 4.03, 3.74, 3.84, 4.61. I sized the prediction on annual means and the model
only runs the heating season. Every site therefore sits above the 4 m/s reference when it matters,
and every site rose.

**And the Part F floor makes the effect one-sided.** A calm day cannot ventilate below
`_MINIMUM_VENTILATION_ACH`, so the downside is clamped while the upside is not. The wind term can
only add, on average, which is why no site fell and why the level moved more than a symmetric
argument allows.

**The third and fourth failures share a cause I had the evidence for and read backwards.** The
archive's own winter temperature × wind correlation is **+0.465 to +0.541** across the four sites —
independently corroborating the repo's published +0.507 from a different dataset. A *positive*
correlation between temperature and wind means **cold days are CALM**. That is the cold-and-still
tail this project already documented, and I wrote in the prediction that the two "coincide… so the
cold tail widens more", which inverts it.

The consequence is the useful part:

> **The wind term matters most in mild windy weather, not in cold snaps.** The largest single-day
> effect in the whole 2023 replay is day 362 at C4 — **8.3 °C and 9.9 m/s, fuel 32.7 → 47.7 kWh,
> +45.8%.** A mild, gusty December day, not a freeze.

Because the coldest days are the calmest, the wind factor sits *below* 1.0 exactly when demand peaks,
and the Part F floor clamps it there. So the peak barely moves and the shoulder rises — which is why
daily variance **fell** at three sites: the term compresses the seasonal swing rather than widening
it. For anyone sizing a peak-demand hedge that is the opposite of the intuitive answer.

## What this costs, and why it is allowed

**Historical demand figures move by up to +8.3%.** That is a baseline-world change, and the wall
permits it on exactly one ground: a fidelity reason, decided blind to company results. This is that —
a published SAP/BREDEM term the model omitted, implemented at its published form, with the reference
point chosen so the omission's size is measurable rather than absorbed. No company figure was
consulted in deciding to make it, and the size of the movement was not known until after the code
was written.

## Limits

- **The shelter factor is not applied.** SAP's `1 - 0.075 x sides_sheltered` is a property attribute
  this model has no field for. Omitting it treats every dwelling as maximally exposed, which
  **overstates** the wind effect uniformly. Registered, not invented.
- **Four sites.** The decision in `W1_27` is 21 cells for wind; the world now has a wind term at the
  four sites the archive covers. Having the term is the precondition for the cells mattering at all.
- **Daily mean wind.** Infiltration responds to gusts and the archive is a daily mean, so within-day
  structure is absent in the same way it is for temperature.
- **One dwelling, one year.** The replay above is a single 1965–80 semi over 2023. The stock sweep in
  `W1_25` gives the spread across era and insulation; this gives the movement in the live archive.
