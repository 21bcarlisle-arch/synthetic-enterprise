**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_27_the_cell_decision_and_the_solar_gain_check

**Knowledge:** none -- the weather-cells knowledge page is deliverable 1 of the weather ruling and is
not yet written. This is the decision it will publish; the declaration is replaced when the page
lands.

# The cell decision, and what the world actually uses today

**Decided 2026-09-06**, delivery seat, on the director's instruction to state the cell answer as a
build decision rather than a curve. Solar-gain check reproduced with
`tools/weather_driver_sensitivity.py --solar-gain`, which runs the 2R2C integration twice rather
than reading the source — the wind term was *named* in a docstring and consumed by nothing, so a
check that greps for a word would have reported both drivers present.

---

## The decision

> **Roughly twenty cells per driver, held SEPARATELY. Not one shared partition, and not 987.**

`W1_21` measured that one partition resolving all three drivers simultaneously to 99% needs 987
cells. `W1_25` measured that each driver alone needs about 21 — winter temperature 99.3%, wind 99.4%,
sunshine 99.4%. The 987 is the cost of a shared grid, and nothing in this company needs a shared
grid: a heat-loss calculation reads temperature and wind, a PV estimate reads irradiance, and each
can carry its own lookup.

| job | driver | decision |
|---|---|---|
| household heat load | winter temperature | **21 cells** |
| household heat load | wind speed | **21 cells** |
| household PV yield | irradiance | **5 cells** (3 for 1.5%) |
| household solar gain | irradiance | **shares the PV cells** |
| wholesale price | national wind | **1 — national** |

Three grids, not one. The heat-load pair are separate lookups even though both feed one calculation:
a 21-cell temperature grid and a 21-cell wind grid are **not the same 21 cells**, and forcing them to
be is exactly the shared-partition cost the decision refuses.

**Why 21 and not 34 or 13.** The curve is a price list, not a threshold. 13 cells reach ~98.5% on
every driver and 21 reach ~99.4%; the step from 21 to 34 buys 0.4 points. **21 is where the marginal
cell stops paying**, and that is the whole argument for it — not a threshold anyone should defend.

It is worth noting, without leaning on it, that 21 is also the count the weather ruling gives for
SAP's climate regions. SAP 10.2 does publish monthly regional wind speed and solar radiation tables,
so the published methodology partitions GB at roughly this order for the same drivers. **That is a
coincidence of magnitude, not corroboration**: nothing here has read SAP's region list or checked
that all three of its tables use the same partition, and a count agreeing with a count says nothing
about the boundaries agreeing.

## What the world actually uses today

This is the gap the decision is against, and it is not the same gap for each driver.

| driver | in the world? | geographic resolution today | reachable? |
|---|---|---|---|
| temperature | **yes** | **4 sites** — London, Manchester, Glasgow, Cotswolds | yes |
| **wind** | **NO** | none — absent from the data contract | n/a |
| solar gain | **yes** | **4 sites**, via latitude + daily cloud cover | **yes, measured** |
| PV yield | yes | **1** — a single national kWh/kWp | yes |

**Temperature.** `simulation/fabric_physics.py` resolves latitude per site through
`latitude_for_weather_site`, which fails closed on anything outside the four the archive covers.
Honest at the resolution the archive supports, and 4 against a decision of 21.

**Wind is absent at the data-contract level, not merely unused.** `DailyWeather` — the record the
whole demand path runs on — carries `day_of_year`, `temperature_min_c`, `temperature_max_c`,
`temperature_mean_c` and `cloud_cover_pct`. **There is no wind field.** `W1_25` found no wind term in
`fabric_parameters`; this is one layer deeper and stronger: there is nowhere to put one without
changing the contract. That is `W1_26`.

**PV yield.** `company/regulatory/seg_export_estimator.py` applies 850 kWh/kWp to every household in
the book. One cell, against a decision of five.

## Solar gain: checked, not assumed — and it is NOT the same gap as wind

The director's instruction was to check rather than assume, given the wind term's history. The wind
term was listed in a module docstring as an available archive field and consumed by nothing, so the
question here is not "is it mentioned" but "does it reach the heat balance and change the answer".

**It does, and by a lot.** Solar gain enters `simulate_day` as `phi_s = ghi × solar_aperture_m2` and
is split between the air and mass nodes by `_SOLAR_SPLIT_TO_AIR`. Zeroing the aperture on a
representative 1965–80 semi over an October–March half-year raises heating fuel from **7,274 kWh to
9,138 kWh**:

> **Solar gain offsets 20.4% of heating fuel.** Larger than the wind effect `W1_25` measured, and it
> is wired.

Two things vary it geographically, and both are live:

| | fuel change |
|---|---:|
| latitude 51.51 °N (London) → 55.86 °N (Glasgow), cloud held at 60% | **+5.7%** |
| cloud cover 35% → 85%, latitude held at 53 °N | **+12.7%** |

**Across the household solar spread**, quoted the same way as `W1_25`'s wind and temperature figures
— 5th to 95th percentile of the same household-weighted population, an irradiation spread of +11.8%
by Ångström–Prescott:

| stock | fuel at p05 solar | at p95 solar | change |
|---|---:|---:|---:|
| pre-1919, poor insulation | 16,687 kWh | 16,494 | **−1.2%** |
| pre-1919, full insulation | 9,447 | 9,234 | −2.3% |
| 1965–80, poor | 8,832 | 8,613 | −2.5% |
| 1965–80, full | 5,193 | 4,971 | −4.3% |
| post-2000, poor | 2,224 | 2,062 | −7.3% |
| post-2000, full | 1,965 | 1,811 | **−7.9%** |

**Solar gain matters MORE the better the house is** — it is a fixed quantity of free heat against a
shrinking demand. Set beside the same sweep for wind:

| stock | wind: HLC change p05 → p95 |
|---|---:|
| pre-1919, poor | +12.6% |
| pre-1919, full | **+18.6%** |
| 1965–80, full | +16.8% |
| post-2000, poor | +9.8% |
| post-2000, full | **+2.9%** |

Wind's effect peaks in the middle of the stock and collapses in the tightest modern homes, because
the Part F minimum air change rate binds there and the calm end is clamped — a sealed house cannot
ventilate less. **So the two drivers are complementary across the stock**: wind is the older,
insulated home's exposure and solar is the modern airtight one's. Neither is an old-versus-new story,
and a targeting model that used one as a proxy for the other would be wrong at both ends.

## Two residuals on solar gain, both already recorded in the module

Neither is the wind gap, and neither should be read as one:

1. **Orientation-blind.** `solar_aperture_m2` is glazing area × transmittance × frame factor, applied
   to *global horizontal* irradiance. A north-facing and a south-facing home receive identical solar
   gain. The module's own docstring records that a per-orientation transposition was documented and
   never written, with the citations withdrawn. The PV *generation* path does transpose by
   orientation; the *gain* path does not.
2. **Four sites, and cloud rather than irradiance.** The driver is `cloud_cover_pct` from the
   Open-Meteo daily archive at four points, put through Kasten-Czeplak attenuation of a Haurwitz
   clear-sky curve. The decision above asks for five cells of *irradiance*; the world has four sites
   of *cloud*. Those are different quantities and the conversion is the same Choice `W1_19`
   registered and did not make.

## What this means for sequencing

- **`W1_26` first.** Wind is the only driver with no home in the world at all, it is the largest
  unmodelled effect measured so far, and the company already has a belief term for it.
- **Then PV.** Five cells against one is the largest ratio in the table, and `seg_export_estimator`
  is a self-contained change with no effect on historical demand.
- **Solar gain needs no repair, only resolution.** It is correct in structure and material in size;
  what it lacks is cells and orientation, and both are additive rather than corrective.

## Limits

- **The solar-gain figures are one representative dwelling** (82 m² semi, 1965–80, partial
  insulation, gas combi) swept across era and insulation, on a synthetic smooth seasonal temperature
  so that only the sun varies. They are sensitivities, not a demand forecast.
- **Aperture scaling is used as a proxy for irradiance scaling.** `phi_s = ghi × aperture`, so the
  two are exactly equivalent in the heat balance — but only because the model is linear in both.
- **21 is a reading of a curve, not an optimum.** Nothing here establishes that 21 cells of
  temperature and 21 of wind cannot be served by one grid of 30-odd; that overlay is unmeasured and
  is the open question `W1_25` left.
