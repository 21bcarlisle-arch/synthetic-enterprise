# G14: GB grid carbon, from the published series and a weather fit for futures

**Knowledge:** none -- no knowledge page covers grid carbon intensity yet; carbon-price is the allowance price, a different quantity

*Written 2026-10-05. Director, 2026-10-05: take NESO's published series and align it to
settlement; fill any gap before it from Elexon's fuel mix and standard factors, not from a dispatch
model; fit futures on wind, solar and demand "so future carbon is consistent with future weather".
Code: `sim/grid_carbon_history.py` (`09e2bf07f`), `sim/grid_carbon_future.py` (`4059a392b`). What
the parked plant-by-plant rebuild found is in `what_ep13_established_about_gb_grid_carbon.md`.*

Claims are marked **[measured]** (a run on real published data), **[sourced]** (a published
document or service, cited), **[fitted]** (a parameter chosen against data, with its window) or
**[open]**.

## What the quantity is

National GB grid carbon intensity, gCO2 per kWh **consumed**, per half hour, keyed by the
settlement period's start time. Clock-change days carry 46 and 50 periods. It is NESO's
definition: generation-weighted emissions over a denominator that includes NESO's estimate of
embedded (distribution-connected) wind and solar. It is not regional, and it is the *actual*, not
NESO's forecast; what a household could have acted on at the time is the forecast, graded in the
EP13 write-up.

## History, 2016-2025

- **[sourced] Coverage.** NESO's carbon intensity API (`api.carbonintensity.org.uk`, key-free,
  openly licensed) holds national half-hourly actuals from **2018-05-11**; a request before that
  returns an empty set (`sim/neso_carbon_intensity.FIRST_PUBLISHED_DATE`).
- **Before 2018-05-11** the value is Elexon FUELHH outturn by fuel times NESO's own published
  generation and import factors (`sim/elexon_fuel_outturn`), with NESO's embedded wind and solar in
  the denominator. No dispatch model is involved.
- **[measured]** On the 2018-2025 overlap the fuel-mix estimate tracks NESO at correlation 0.976
  (0.965-0.996 by year). Adding embedded generation to the denominator took the post-2020 bias from
  +12.6 g to +2.4 g.
- **[fitted]** NESO's level sits 10-13% above the fuel-mix arithmetic until a step at 2020-04-27
  period 34. That step is a change in how the API calculates its figure (below), not a change in the
  fleet. The pre-2018 estimate is scaled by 1.1287, fitted on 2018-05-11 to 2020-04-27 (the level
  at the join). That takes the window's bias from -25.3 g to -0.6 g. It puts 2016 to 2020-04 on the
  API's pre-step basis, about 11% above everything after it.
- **Inside NESO's coverage** a NESO outage or null is filled from the fuel mix and tagged
  `fuelmix_fill`. A half hour with neither source is a gap with its reason, never a zero. Every value
  carries `neso_published`, `fuelmix_estimate` or `fuelmix_fill`.
- **[measured] A publication defect found on the way.** Through 2022 Elexon's FUELHH row labelled
  (D, 48) starts at D-1 23:30Z. All FUELHH readers now key by start time; about 1.3% of half hours
  moved.

### The 2020-04-27 step is a change in NESO's calculation, not in the fleet

*Established 2026-10-05; the pre-registration and the runs are in
`docs/staging/SEAT_FINDING_G14_NESOS_2020_04_28_LEVEL_STEP_2026-10-05.md`.*

- **[measured] It happens at one half hour.** At 2020-04-27 period 33 the API's actual is 210 g. At
  period 34 it is 195 g. Over the same two half hours CCGT rose 860 MW and the fuel-mix arithmetic
  rose from 191 g to 198 g. Embedded generation, every FUELHH fuel and the import mix are smooth
  across the boundary, so none of our inputs moved: the cause is on NESO's side.
- **[measured] It is not one factor revised.** The implied per-fuel factors were fitted on a year
  either side of the step. Before it, CCGT is 430 g/kWh, coal 1,066 and biomass 165. After it they
  are 400, 984 and 122, against NESO's table of 394, 937 and 120. Every well-identified factor is
  9-14% high before the step and back near the table after it. That is a uniform multiplier, not a
  revision to one fuel.
- **[measured] It is not embedded generation leaving the denominator.** Dropping embedded wind and
  solar fits the pre-step API worse: the ratio's SD goes from 0.076 to 0.083, and its slope on
  embedded share from +0.35 to -0.84.
- **[measured] NESO's other published series has no step.** NESO's Open Data Portal "Historic GB
  Generation Mix" (`df_fuel_ckan.csv`) is half-hourly from 2009-01-01 and carries its own
  `CARBON_INTENSITY`. Across the 28 days either side of the step, historic-mix/arithmetic goes 0.961
  → 0.959, while API/historic-mix goes 1.151 → 1.048. A placebo cut on 2019-04-27 moves neither
  (0.978 → 0.970 and 1.130 → 1.125). After the step the two NESO series agree half hour by half
  hour within 1-3%. Before it, the API runs 13-18% above NESO's own historic mix.
- **[sourced] The likely mechanism.** NESO's methodology says the API's figure is "corrected to
  account for transmission losses to give the intensity of consumption". A loss correction is the
  one uniform, fuel-independent multiplier of about this size. NESO's FOI response FOI/25/152 says
  NESO "does not hold recorded information on an historical time series of the net percentage or
  multiplier used to convert generated electricity to delivered/final-use electricity". **[open]**
  So which term changed cannot be established from NESO. The classification can: **a methodology
  change in the API's live calculation**, not a factor revision and not a fleet change.
- **[measured] What it does to G14 as shipped.** The series takes the API from 2018-05-11. So
  2018-05-11 to 2020-04-27, and the pre-2018 estimate scaled to join it, sit on the old basis, about
  11% above 2020-04-27 onwards. Part of the published decline from 2019 to 2021 is therefore the
  calculation change and not the fleet. The same part sits inside the 2018-2020 rows of the weather
  fit's per-year table below. For 2019 that is roughly 24 of its +45.6 g (214 g × the ~11% step).
  The futures fit is unaffected, because its window is 2024-25.

The company reads this series through `docs/market_data/grid_intensity_feed.json`
(`tools/generate_grid_intensity_feed.py`), the same route as the price and consumption feeds; the
household footprint (`company/carbon/half_hourly_footprint.py`) and `site/explore` read it there.
That is the switch from EP13's reconstruction. The reconstruction is still buildable, and nothing
publishes it.

## Futures: a weather fit on today's fleet

The world does not generate future grid wind, solar or demand. It replays whole historical weather
years (`sim/weather_world.extended_by_analogue_years`). So a forward half hour takes its analogue
record year's real half-hourly wind, solar and demand, rescaled to 2025:

- wind and solar by DUKES year-average installed capacity (`sim/renewable_capacity_trend`);
- demand held at the 2025 level, a named simplification.

**Model:** log intensity on renewable share and demand (`share_log`), with Duan's smearing so the
back-transformed level is unbiased. **[fitted]** Fit window 2024-01-01 to 2025-12-31, 35,039 half
hours; coefficients (5.00987, -2.39279, 0.01954), smearing 1.02632. Fitted share range 0.054-0.795,
demand 19.6-45.2 GW. Wind is FUELHH metered plus NESO's embedded estimate, and solar is NESO's
embedded estimate, matching NESO's own denominator.

### How the form and window were chosen (held out: all of 2025)

| Fitted on 2023-24, graded on 2025 | corr | bias g | RMSE g | daily p95/p5 (actual 2.25) |
|---|---|---|---|---|
| constant | -- | -9.4 | 58.4 | 1.00 |
| linear in wind, solar, demand | 0.922 | -4.3 | 23.6 | 3.66 (p5 floors at 0 on 23 days) |
| **share_log (shipped)** | 0.930 | -6.1 | 22.2 | 2.16 |
| fossil_fraction_log | 0.928 | -5.8 | 22.4 | 2.13 |

**[measured]** Every window ending 2024 has about the same correlation (0.927-0.931). What
separates them is the level: all NESO years since 2018-05 -26.2 g, 2021-24 -19.1 g, 2023-24
-6.1 g, 2024 only +5.7 g. The fleet sets the level and the weather does not.

### Residuals by year

**[measured] Out of sample (rolling origin).** Each year is predicted from a fit on earlier years
only. Figures are RMSE (bias) in g/kWh; bias is actual minus model.

| year | previous year | two previous | all previous |
|---|---|---|---|
| 2020 | 28.3 (-7.8) | 30.4 (-12.8) | 30.4 (-12.8) |
| 2021 | 21.4 (-9.4) | 24.4 (-14.6) | 27.7 (-19.2) |
| 2022 | 39.6 (+23.2) | 35.9 (+17.3) | 34.3 (+10.3) |
| 2023 | 39.1 (-27.2) | 29.8 (-15.2) | 31.2 (-17.6) |
| 2024 | 40.9 (-25.9) | 51.3 (-39.0) | 49.3 (-39.9) |
| 2025 | 22.4 (+5.7) | 22.2 (-6.1) | 34.9 (-26.2) |

**[measured] The shipped fit applied to each record year's own wind, solar and demand.** This
is what the future does: a past year's weather, on the 2024-25 fleet.

| year | half hours | actual mean g | corr | bias g | RMSE g | daily p95/p5 model / actual |
|---|---|---|---|---|---|---|
| 2018 (from 05-11) | 11,220 | 236.3 | 0.874 | +60.7 | 67.4 | 1.78 / 1.58 |
| 2019 | 17,183 | 214.1 | 0.929 | +45.6 | 51.0 | 1.88 / 1.64 |
| 2020 | 17,467 | 180.3 | 0.899 | +35.5 | 44.4 | 2.05 / 1.75 |
| 2021 | 17,312 | 187.7 | 0.941 | +26.5 | 33.2 | 1.95 / 1.74 |
| 2022 | 17,439 | 182.6 | 0.865 | +47.9 | 57.9 | 2.16 / 1.81 |
| 2023 | 17,404 | 152.2 | 0.906 | +22.6 | 35.0 | 2.18 / 1.92 |
| 2024 | 17,524 | 125.1 | 0.895 | -3.5 | 27.0 | 2.19 / 2.24 |
| 2025 | 17,515 | 129.2 | 0.930 | +3.0 | 21.4 | 2.20 / 2.25 |

2024 and 2025 are inside the fit window. Every earlier year sits 23-61 g dirtier than today's fleet
would have made its weather, and its within-day swing is narrower. That is the fleet change (coal's
exit, more wind), and it is what a future on today's fleet should show, not an error in the future.
Correlation stays at 0.87-0.94 across the decade, so the weather's *shape* carries across fleets.
The fit's own monthly mean residuals have an SD of 11.3 g: the level error weather cannot explain.
Every future value names it in its provenance.

Regenerate both tables with `python3 -m sim.grid_carbon_future`, which also prints a sample forward
week beside the record week it replays.

## What is simplified, and what is open

- **Fleet frozen at 2025.** Futures carry no fleet trajectory beyond DUKES installed capacity. A
  2030 half hour is 2030's weather on 2025's thermal fleet and demand.
- **Demand held at the 2025 level.** No electrification trend.
- **[open] Not yet read by anything.** Forward runs publish no carbon, and the company's feed
  carries history only. The smallest honest wiring is forward-year blocks in the grid-intensity
  feed. Before that, the feed's per-year typical-day blocks must be shown readable at earlier
  simulated dates (point in time).
- **[measured] Since the step the API is not loss-corrected, whatever its methodology text says.**
  From 2020-04-27 P34 NESO's actual is 0.97× the generation-only fuel-mix arithmetic (2021-25). A
  loss correction would be about 1.08×. The ×1.10-1.14 before the step was that correction, and the
  step is where it stopped. Any label calling the post-step series "per kWh consumed" or
  "loss-corrected" is wrong (Expert Hour MAJOR-1, 2026-10-05). The quantity defined at the top of
  this page is what NESO's methodology describes, not what the series has measured since 2020-04-27.
- **[open] One basis across the step.** The cause is classified (above), but the shipped series
  still changes basis at 2020-04-27 P34. NESO's Historic GB Generation Mix publishes one basis from
  2009. It is the candidate source for the whole history and would replace the fitted 1.1287 scale.
  The exact term NESO changed is not recorded anywhere NESO holds (FOI/25/152).
