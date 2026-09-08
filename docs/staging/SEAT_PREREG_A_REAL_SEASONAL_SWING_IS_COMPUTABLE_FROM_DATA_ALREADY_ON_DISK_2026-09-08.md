**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`
· **Class:** measurements_that_mirror

**Knowledge:** `how-many-synthetic-households` — landed at `3745b9c0d`. This pre-registers the
fix to the second of the three limits that page publishes, and its result replaces that paragraph.

# A real seasonal swing needs no new data, and the cell alone will not make it an axis

**Pre-registration, written 2026-09-08 at `8151fa592` before the build**, so the prediction below
can be refuted rather than confirmed after the fact.

---

## The problem this addresses

`seasonal_swing` is `0.5 * (1 + 0.15 * z(hlc))` — two invented numbers, and an exact affine
transform of `weather_sensitivity`. Measured today: three of the vector's seven axes are one
direction, the correlation matrix has two zero eigenvalues, and dropping one duplicate cut the
sample size by 31%. Full account:
`SEAT_FINDING_TWO_AXES_OF_THE_DEMAND_VECTOR_ARE_THE_SAME_AXIS_2026-09-08`.

The module's own docstring calls the axis *"the share of the year's demand falling in the coldest
half"*, which the model could not compute because `demand_case_coverage.DOYS` stops on 31 March.

## What I expected to find, and what is actually there

I expected this to be blocked behind the `simulate_premise` build — full-year half-hourly gas,
costed at 16.7 hours for a 120,000-household reference. **It is not.**

`weather_cell_drivers._monthly()` already returns a **(12, 1450, 900)** array of 30-year monthly
normals for temperature, wind and sunshine, for all 245,077 land cells. `drivers()` reduces it to an
annual mean and a winter mean and **throws the other ten months away**. The data for a real
cold-half share has been on disk since the fetch.

## Measured, before writing any formula

Monthly mean temperature over GB land, January to December:

    3.9  4.1  5.7  7.9  10.6  13.3  15.3  15.1  12.9  9.7  6.5  4.2

The coldest six months are November to April, chosen by the data rather than by naming months.

| heating base | annual degree-days (median) | cold-half share (p10 / median / p90) | Jun–Aug share of degree-days |
|---:|---:|---:|---:|
| 15.5 °C | 2,211 | 0.703 / **0.796** / 0.862 | **3.2%** |
| 18.0 °C | 3,113 | 0.655 / 0.708 / 0.774 | 9.6% |
| 20.0 °C | 3,843 | 0.629 / 0.668 / 0.715 | 12.6% |

**15.5 °C is the right base and the table is why**, not because it is the convention: at the model's
current 20 °C set-point, an eighth of all degree-days fall in June, July and August, which is
heating that does not happen. This also settles a question the naive fix would have got wrong —
extending `DOYS` to 365 days at the existing 20 °C set-point would have manufactured a summer
heating season.

The real swing is **0.796**, not the 0.5 that was typed.

## THE PREDICTION, AND THE REASON IT MIGHT FAIL

**Cell geography alone will NOT produce an independent axis.** Measured: the cold-half share
correlates **−0.9217** with annual degree-days across all land cells. A colder cell has both more
demand and a more concentrated winter, so a swing computed from the cell is largely a third copy of
the level — better than an exact duplicate, and not by much.

**So the independence must come from the household, and I predict it comes almost entirely from the
flat hot-water base.** Space heat is seasonal; hot water is not. A household's gas swing is

    (cold-half space heat + cold-half hot water) / (annual space heat + annual hot water)

and the hot-water term is roughly flat across the year, so a household with more people has
proportionally more flat gas and a **lower** swing than a single-person household in the same
dwelling in the same cell. That is real physics, it varies with occupancy rather than with fabric or
weather, and it is the first thing in this vector that would.

**Falsifiable, filed before the measurement:**

1. The household-level swing will correlate with `weather_sensitivity` at **|r| < 0.85**, against
   0.9999+ today and −0.92 for the cell-only version. If it comes out above 0.95, the household
   terms add nothing and the axis should be DROPPED rather than rebuilt.
2. The household-level swing will correlate with **headcount at |r| > 0.20**. Today every axis
   correlates with headcount below 0.14. If this fails, the hot-water base is too small a share of
   the annual total to register and the mechanism above is wrong.
3. **N will rise.** This is the first genuinely new direction added since the payment-method
   stratum, so unlike hot water — which moved the count by two households in 8,822 because it was
   a DRIVER — this should move it. I am not predicting a size: today's evidence says I do not
   understand the magnitudes well enough, and a range invented to look rigorous is the thing this
   project keeps paying for. Direction only, and it is falsifiable on its own.

**Prediction 3 is the one I most expect to be wrong**, because the same reasoning produced the
2–4× estimate for occupancy that today's measurement refuted by a factor of a thousand.

## What this does NOT claim

It does not claim the `simulate_premise` build is unnecessary. That build serves the use case the
director named — *"a customer who wants to budget needs to see the daily cost effect of changing
their thermostat or their timer"* — which a closed form cannot answer at any resolution, and it is
the only route to intermittency. **What this claims is narrower: the invented axis can be replaced
with a measured one first, cheaply, and the two are not the same piece of work.**

**And a constraint on that build, found while scoping this and worth its own line.** `simulate_premise`
needs `daily_weather`, and only **four** locations have a real daily archive
(`sim/weather_data/C1-C4.csv`), covering 2.0% of GB households on all three drivers at once. Per-cell
weather is monthly normals. The synthetic weather engine models those same four locations. So
retiring the closed form is executable for the book's actual households — all of which sit at
archived locations — and **is not executable across the coverage instrument's 194,865-cell space
without synthesising daily weather that does not exist.** That is a fidelity decision about the
world, which the baseline/curriculum split makes the director's, and it is named here rather than
discovered mid-build.
