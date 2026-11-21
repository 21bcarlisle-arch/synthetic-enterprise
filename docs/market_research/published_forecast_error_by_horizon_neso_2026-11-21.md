# What GB's system operator publishes about its own forecast error, by horizon

**Knowledge:** none -- no knowledge page covers the published forecast layer yet; this anchors B3's frame (`docs/design/B3_PUBLISHED_FORECAST_ERROR_HORIZONS_FRAME.md` §7), which is where it is read

**date**: 2026-11-21
**domain**: weather / system forecasts
**atom**: `B3_published_forecast_error_horizons` (DISCOVER; `loop_stage: idle`, no build code)

The B3 frame (2026-07-29) recorded week-ahead and season-ahead error as UNSOURCED. The only
anchor then was a two-week Elexon pull for day-ahead demand. That pull is
`WEATHER_FORECAST_ERROR_BY_HORIZON.md`, and its own note says it is too short for a smooth curve.
This page reads what the system operator itself publishes about its forecast error.
Three documents were fetched by the harness and read as text (`pdftotext -layout`). Every figure
below is quoted from one of them. Nothing is interpolated.

## Sources

- **S1**: National Grid, *Demand Forecasting, Reporting Period 19 Jun 2017 – 10 Sep 2017*. This is
  the licence report covering forecasts "from within day to 52 weeks ahead"
  (<https://www.neso.energy/document/93921/download>, 21 pp).
- **S2**: NESO, *RIIO-2 Business Plan 3 (2025-26) Incentives, BP3 End-Scheme Report, Reported
  Metrics Annex*, May 2026 (<https://www.neso.energy/document/381541/download>, 83 pp). It covers
  §2 Demand Forecasting, §3 Wind, and §15 EMR Demand Forecasting.
- **S3**: NESO, *Energy Forecasting Strategy & Delivery Plan*, March 2026
  (<https://www.neso.energy/document/373066/download>). This one is context only and carries no
  figures used here.

## What is established

### Day-ahead, the current record (S2, pp. 29–34)

**National demand.** The figure is the mean absolute MW error, per half hour, between two
published series. The forecast is BMRS's National Demand Forecast published 09:00–10:00 the day
before. The outturn is Initial National Demand Outturn.

| 2025-26 | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | Jan | Feb | Mar |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| absolute error (MW) | 671 | 692 | 616 | 584 | 579 | 702 | 711 | 641 | 626 | 662 | 717 | 985 |
| previous 5-year avg (MW) | 727 | 620 | 541 | 532 | 538 | 545 | 588 | 596 | 662 | 707 | 684 | 793 |

- The full year is **682 MW**, against a 5-year average of **628 MW**.
- The error has a seasonal shape. Summer is lowest in the 5-year average, at about 530–545 MW in
  Jul–Sep. Spring and winter are highest.
- NESO names day-ahead **solar** error as "the largest contribution to the metric performance".
- The largest single half-hour error in March 2026 was 5.5 GW. Demand that month ran from 18.1 GW
  to 38.2 GW.
- Ofgem "no longer use a benchmark" for this metric.

**Wind.** The figure is the mean absolute error between the day-ahead forecast and settlement
metering. It is expressed as a **percentage of capacity**, for BM wind units only. It excludes
half hours with a BOA and sites that withdrew availability.

| 2025-26 | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | Jan | Feb | Mar |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APE (% of capacity) | 3.85 | 4.09 | 5.61 | 3.80 | 4.06 | 5.74 | 4.38 | 5.27 | 4.43 | 4.86 | 4.72 | 4.20 |
| previous 5-year avg (%) | 4.26 | 3.87 | 4.53 | 4.39 | 4.30 | 5.27 | 5.23 | 4.55 | 4.84 | 5.36 | 4.78 | 5.18 |

- The full year is **4.58%**, against a 5-year average of **4.71%**.
- The largest single half-hour error in March 2026 was 4.3 GW.
- This is a *controlled* metric. Curtailment and withdrawal are removed. A supplier exposed to
  the whole fleet's real outturn faces a larger error than this, by an amount the page does not
  publish.

### The shape across horizons (S1, pp. 2–12; summer 2017)

- "With forecast lead-time increasing ... the errors grow." Daytime errors are larger than
  overnight and "increase more with increasing forecast lead time".
- **The weather skill horizon is a stated fact of the method.** Forecasts from within-day to 13
  days ahead use the latest weather forecasts. Beyond 14 days they are "based on seasonal average
  weather". S1 also notes that "accuracy of weather forecasts declines significantly from 7 to 13
  days ahead".
- **Wind speed MAE by lead time (m/s):**

  | in-day | DA | 2DA | 3DA | 4DA | 5DA | 6DA | 7DA | 8DA | 9DA | 10DA | 11DA | 12DA | 13DA |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
  | 0.55 | 0.83 | 1.01 | 1.24 | 1.54 | 1.81 | 1.93 | 1.92 | 1.94 | 1.94 | 2.01 | 1.99 | 1.94 | 1.96 |

  S1 converts speed error to power error as follows: in the mid power curve (5–15 m/s), "a 1 m/s
  error in wind speed forecast equates to around a 10% error in wind power forecast for the
  generator".
- **Solar PV MAE by lead time (MW, daylight hours):**

  | DA | 2DA | 3DA | 4DA | 5DA | 6DA | 7DA | 8DA | 9DA | 10DA | 11DA | 12DA | 13DA |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|
  | 376 | 471 | 557 | 638 | 673 | 750 | 848 | 843 | 857 | 851 | 859 | 851 | 859 |

  This was against 12.0–12.4 GW of installed PV.
- **2–52 weeks ahead, peak national demand.** These forecasts are built on seasonal-average
  weather. Their MAE was **1.1 GW** for the period, against 1.3 GW the previous quarter. The
  maximum error was 3.7 GW against actual demand, and 3.7 GW on a weather-corrected basis.
- **Wind bias** is incentivised separately. The aim is an equal count of over- and
  under-forecasts, with a break-even target of 60:40 and a floor of 70:30. The months ran 57%, 47%
  and 51%.

### Years ahead (S2, p. 77)

The metric is ACS peak national demand, which is weather-corrected. It compares forecast with
outturn, as a percentage of outturn. Delivery year 2025-26:

| Auction | Forecast made | Forecast GW | Outturn GW | Error |
|---|---|---|---|---|
| T-1 | 2024-25 | 46.0 | 46.4 | **0.9%** |
| T-4 | 2021-22 | 44.7 | 46.4 | **3.7%** |

That is one delivery year, and NESO calls it "provisional". Because the outturn is
weather-corrected, this error is **structural** (load growth, embedded generation). It contains
no weather error.

## What it means for B3's definition of done

The DoD (`docs/design/simplifications/B3_...yaml`) asks for an error that "monotonically shrinks
toward delivery by a calibrated schedule". **The published record has a different shape.** It
has three regimes:

1. **About 0–6 days.** Error grows with lead time. Wind speed error rises 0.55 → 1.93 m/s and
   solar error rises 376 → 750 MW.
2. **About 7–13 days.** There is a **plateau** at the weather-skill limit. The values are flat to
   within noise: wind 1.92–2.01 m/s, solar 843–859 MW. The 10DA wind figure is *above* 13DA.
   **Corrected the same day, by measurement:** this plateau holds for wind and solar. It does
   **not** hold for national demand, which keeps rising to about day 11 (see *Measured* below).
3. **Beyond about 14 days.** The forecast is climatology, built on seasonal-average weather. Its
   error is the weather's own spread around its seasonal mean plus structural error, which is
   0.9% at one year and 3.7% at four for the peak. Lead time stops mattering until the structural
   term grows.

A control keyed to strict monotonicity is keyed to the wrong property. A world that is faithful
to the record would fail it. The test should be keyed to this: error is **non-increasing toward
delivery within the sampling noise**, and **flat from the skill horizon outward**. The frame's
§7 now names this.

## Measured: demand error by lead day (BMRS, FY2021-22 to FY2025-26)

A harness pull, made 2026-11-21. It covers BMRS's own published forecasts against Initial
National Demand Outturn, with target days from 1 Apr 2021 to 31 Mar 2026. The aggregates are in
`published_demand_forecast_error_by_lead_day_bmrs_2021_2026.csv` (cuts: all, by FY, by season,
and the day-ahead series by month). The CSV header states the endpoints and the method. The
row-level pull (about 2 MB) is not committed; it can be reproduced from those endpoints.

**What is measured.** Two different products, and they are not interchangeable:

- **Day-ahead, half-hourly** (`NDF`). For each half-hour of day D, the forecast is the latest
  `NDF` publish at or before 10:00 UK on D-1. This is NESO's BP3 metric shape. One trap: `NDF`
  arrives in *fragments*, and no single publish covers all 48 periods of the next day. A first
  pass that read one publish, in a 09:00–10:00 window, measured 413 MW and then 644 MW.
  Neither figure is a measurement; both are recorded here so nobody repeats them.
- **2–14 days, daily peak** (`NDFD`). There is one publish a day, at about 14:45 UK, of each
  target day's peak national demand. Lead is the forecast date minus the publish date. It is
  scored against the day's maximum half-hourly INDO. Lead 1 on this basis is the day's maximum
  of the day-ahead `NDF`, so the step from lead 1 to lead 2 also contains a change of product
  and of publish time (10:00 vs 14:45).

**Pre-registered** (written before any number was read):
P1, day-ahead half-hourly MAE for 2025-26 within 10% of NESO's 682 MW (614–750).
P2, error rising to about 6 days and flat from 7 to 13 days, as S1's wind and solar tables show.

**P1 holds.** The 2025-26 figure is **695 MW**, 1.9% above 682. By month, Apr–Mar:
689, 750, 653, 593, 585, 715, 720, 620, 629, 677, 738, 977. Each is within 60 MW of S2's table.
That agreement is the evidence that the series and the vintage are the ones NESO scores. The
other years read 598, 617, 601 and 660 for FY2021-22 to FY2024-25 (FY2021-22 lacks May 2021).
Their mean is 619, against S2's 5-year average of 628.

**P2 is refuted for demand.** Peak MAE by lead (MW), all five FYs together, with n ≈ 1,720 per
lead:

| lead (days) | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MAE | 591 | 725 | 762 | 824 | 928 | 1,002 | 1,054 | 1,166 | 1,234 | 1,290 | 1,335 | 1,360 | 1,379 | 1,372 |
| bias (fc − out) | +26 | −168 | −147 | −138 | −69 | −16 | +72 | +377 | +441 | +473 | +223 | +244 | +256 | +193 |
| FY range of MAE | 581–615 | 693–783 | 700–817 | 804–858 | 905–959 | 974–1,061 | 999–1,099 | 1,092–1,240 | 1,154–1,291 | 1,207–1,356 | 1,295–1,405 | 1,318–1,449 | 1,325–1,509 | 1,227–1,583 |

- The error keeps rising well past day 7, from 1,054 to 1,290 MW by day 10. It flattens only from
  about day 11 to day 14 (1,335–1,379). The FY ranges at 11–14 overlap, and those at 7 and 10 do
  not. Demand does not show the 7-day plateau that S1's wind speed and solar tables show. The
  probable reason, not tested here, is that demand error is dominated by **temperature**, which
  keeps forecast skill longer than wind or cloud.
- **The season decides the shape.** In winter (DJF) the error rises steadily, from 816 MW at lead
  2 to 1,340 at lead 7 and 1,876 at lead 13. In summer (JJA) it is **flat from day 6 to day 10**
  (882–901), with a step to about 1,045 at day 11. The 7-day plateau prediction was a summer
  shape, applied to the whole year.
- **The bias changes sign and jumps between day 7 and day 8**, from +72 to +377 MW, while MAE
  steps by +112. That is a method boundary, not a smooth decay: past a week, BMRS's peak
  forecast leans high. The method change was not identified on the pages read (GAP).
- Tails are about twice the MAE. The p90 absolute error is 1.2 GW at lead 1, 2.2 GW at lead 7
  and 2.9 GW at lead 14.

**For B3.** A calibrated day-ahead-to-fortnight schedule for demand now exists, by season. The
DoD's control should be keyed to "non-increasing toward delivery, within the FY range". It should
not be keyed to strict monotonicity (lead 14 is below lead 13 in the pooled figure), nor to a
plateau from day 7, which demand does not have.

## GAP (not published in what was read)

- ~~Demand MAE at 2-day and 7-day ahead.~~ **Measured 2026-11-21**: see *Measured: demand error
  by lead day* below. 2DA peak MAE is 725 MW and 7DA is 1,054 MW. It is published nowhere as a
  number, but it is now measured from the published series. What stays open: the 2DA/7DA figure
  on NESO's *own* incentive basis (its exact forecast vintage and peak definition), which we
  match only for day-ahead.
- **Wind *power* MAE beyond day-ahead.** Only wind *speed* by horizon is published here. The
  1 m/s ≈ 10% conversion is NESO's mid-curve rule of thumb, not a measurement.
- **Any price forecast.** The system operator publishes no price forecast at any horizon. What a
  supplier sees ahead of time is the forward curve, which is a traded price, not a forecast. The
  same distinction is already drawn in `company/trading/forward_curve_confidence.py:8`. B3's "price"
  leg therefore has no published-forecast twin to calibrate against.
- **2016–2024 history.** S1 covers one 2017 quarter and S2 covers 2025-26, plus 5-year averages by
  month. Year-by-year error for the 2016–2025 run window is not on these pages. The monthly
  5-year averages are the nearest available.
