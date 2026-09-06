**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_25_the_cells_per_driver_and_what_each_driver_is_actually_for

**Knowledge:** none -- the weather-cells knowledge page is deliverable 1 of the weather ruling and is
not yet written. These rows replace `W1_21`'s single joint curve as what it will publish; the
declaration is replaced when the page lands.

# One grid, three jobs — and wind is not the awkward one

**Measured 2026-09-06**, delivery seat, `W1_25`, on the director's challenge to `W1_21`'s framing.
Reproduce with `tools/weather_cell_derivation.py` and the per-driver sweep it now carries.

The director's diagnosis was right and his mechanism was wrong, and the difference matters, so both
are set out here against the measurements.

---

## 1. All three drivers need the SAME number of cells

Household-weighted, one driver at a time, over the 121,668 occupied land cells:

| cells | winter temperature | annual wind | annual sunshine |
|---:|---:|---:|---:|
| 5 | 91.1% | **92.5%** | 92.3% |
| 8 | 96.2% | **96.6%** | 96.6% |
| 13 | 98.4% | **98.6%** | 98.7% |
| 21 | 99.3% | **99.4%** | 99.4% |
| 34 | 99.7% | 99.8% | 99.8% |

**Wind is not the fine-grained one. It is marginally the smoothest of the three.**

The premise — that wind varies over kilometres in a way temperature does not — is true of *Britain*
and false of *inhabited Britain*. Wind's fine structure comes from terrain, coast and exposure, and
`W1_20` established that half of GB's land cells hold nobody: the ridges, the exposed headlands and
the uplands that make the wind map look nuanced are the empty half. Weight by households and the
wind field is as smooth as the temperature field.

**So `W1_21`'s 987 is not an artefact of resolving wind at the wrong level.** It is an artefact of
demanding that **one** partition resolve all three drivers **simultaneously**. Each alone needs about
21 cells for 99%; one grid serving all three needs 987. That is dimensionality, not roughness — and
it is exactly the director's diagnosis, reached from the opposite direction. The framing was wrong;
the conclusion drawn from it was right.

## 2. Wind reaches a household through infiltration, and it is not second-order

**The mechanism is published and it is linear.** SAP 10.2 / BREDEM adjust a dwelling's infiltration
rate by a wind factor:

> adjusted infiltration ACH = raw ACH × shelter factor × (**wind speed ÷ 4 m/s**)

Not a wind-chill correction on the outside surface: a direct linear multiplier on the air change
rate, normalised at 4 m/s. Ventilation loss is `0.33 × ACH × volume`, so it flows straight into the
heat loss coefficient.

Applied to this project's own stock model (`simulation/fabric_physics.py`, 288 era × type ×
insulation × size combinations):

| | min | median | max |
|---|---:|---:|---:|
| ventilation share of heat loss coefficient (at median wind) | 15.0% | **27.5%** | 50.6% |
| HLC change, 5th → 95th percentile household wind (2.98 → 5.61 m/s) | +2.7% | **+14.9%** | +29.7% |

**The comparator, over the same percentile span of the same population:** winter temperature moves
from 3.95 °C to 6.13 °C, which changes heating degree days by **−18.9%** (base 15.5 °C).

**So wind is roughly 0.8× the size of the temperature effect on household heat demand. It is not
second-order and the hypothesis is refuted.** A pre-1919 flat at the windy end of the distribution
loses 30% more heat than the same dwelling at the calm end, from wind alone. That is larger than
most of the retrofit measures a supplier would ever recommend.

**Importance and resolution are separate questions**, and conflating them is what produced both the
987 and the challenge to it. Wind matters as much as temperature *and* needs no more cells than
temperature. Neither fact implies the other.

## 3. The finding underneath all of this: our own world has no wind term

`simulation/fabric_physics.py` computes infiltration from build era and insulation level, and
**nothing else**. There is no wind factor. `wind_speed_mean_ms` is listed in the module's own
docstring as an available field of the weather archive and is consumed by no demand path anywhere in
`simulation/`.

Meanwhile `company/pricing/weather_normalisation_belief.py` carries an optional wind-chill
regressor — `HDD × excess wind above a calm threshold` — that a caller can switch on and fit.

**The company can therefore fit a household wind-chill coefficient against a world in which
household wind chill does not exist.** Whatever it fits is noise or a proxy for something else, and
the fit will look entirely healthy: the regressor is real, the data is real, and the r² will be
reported. This is a coupled-triad defect — the belief carries a term the truth does not — and it is
the reason this document exists rather than a cell count.

The repair is on the SIM side and it is small: the published factor is one multiplication. It is not
done here, because changing the world changes every historical demand figure in the tree and that is
a fidelity decision with its own evidence bar. **Registered as `W1_26`.**

## 4. Wind → price is national, and that part of the premise holds

`company/pricing/weather_price_belief.py` already fits `price ~ gas + temperature + wind` on a
single national wind series. Wind's largest business effect is on wholesale price, that quantity is
national, and it is already wired. **No household resolution is needed for it** — and none is used.

## 5. PV: three to five cells, against the one the company has today

`company/regulatory/seg_export_estimator.py` uses **one number for the whole country**: 850 kWh/kWp,
with a comment noting ~950 in the south and ~750 in the north.

Sunshine duration converts to irradiation by the Ångström–Prescott relation, `H/H₀ = a + b·(n/N)`,
which is the method used to build the UK's own gridded solar resource from gridded sunshine duration.
Because `a > 0`, **relative variation in irradiation is strictly smaller than in sunshine duration**:
at the GB household mean (1,535 h, n/N = 0.350) the elasticity is **0.41** at Prescott's a = 0.25,
b = 0.50, and 0.43–0.49 across the published coefficient range. So the sunshine spread overstates the
yield spread by about a factor of two.

| cells | sunshine RMS error | **annual PV yield RMS error** |
|---:|---:|---:|
| **1 (today)** | 126.8 h | **3.4%** |
| 2 | 77.9 h | 2.1% |
| 3 | 56.9 h | 1.5% |
| **5** | 35.1 h | **0.95%** |
| 13 | 14.7 h | 0.40% |
| 21 | 9.5 h | 0.25% |

**Three cells gets a household's annual generation to 1.5%; five gets it under 1%.** The company's
single national figure carries 3.4%, which is the same order as the SEG rate spread it is used to
value. The cells wanted are not a different *shape* so much as a small number of latitude bands —
sunshine correlates −0.806 with latitude (`W1_19`), so the partition is close to one-dimensional.

## 6. What replaces the single answer

| job | driver(s) | resolution | where it stands |
|---|---|---|---|
| household heat load | winter temperature **and** wind | **~21 cells** for 99% of each | wind is unmodelled in the SIM (§3) |
| household PV yield | sunshine → irradiation | **3–5 cells** for ~1% | one national figure today |
| wholesale price | national wind | **1** — national | already wired |

**`W1_21`'s 987 stands as arithmetic and falls as a recommendation.** It is the correct answer to
"how many cells resolve all three drivers jointly to 99%", and that is a question nothing in this
company asks. The jobs are separable, and separating them costs about 21 cells instead of a thousand.

## Limits

- **Ångström–Prescott is applied at the annual mean**, not month by month, and its coefficients are
  not UK-calibrated here. The elasticity is stable at 0.41–0.49 across the published range, so the
  conclusion does not turn on the choice, but the yield percentages would move slightly.
- **The wind sensitivity is our own stock model's**, driven by the published SAP factor. It inherits
  whatever is wrong with `_INFILTRATION_ACH_BY_ERA`, and the SAP shelter factor is deliberately
  omitted because it is a property attribute, not a cell attribute, and cancels in a ratio.
- **HLC is not annual demand.** Both figures in §2 are heat-loss-coefficient and degree-day changes;
  gains, controls and occupancy sit between them and a bill. They are comparable to each other,
  which is what the comparison needs, and neither is a demand forecast.
- **Per-driver curves are one-dimensional partitions.** Nothing here says a 21-cell temperature grid
  and a 21-cell wind grid can be the same 21 cells — §1 says the opposite. Two jobs may want two
  overlays, and whether one 34-cell grid serves both to 99% is not measured.
- **Nothing here touches shape.** These are annual and winter-mean levels; `W1_22`'s persistence and
  synchrony findings are unaffected by any of it.
