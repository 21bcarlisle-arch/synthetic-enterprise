# Simulation period — confirmed window

Decision record for the historical window the simulation runs over, so the
choice doesn't need re-deriving each time a new data source is onboarded.
Confirmed by direct probing of the Elexon system-prices endpoint on
2026-06-07 (see [`elexon.md`](data-sources/elexon.md) for the endpoint shape).

## Window

**2016-01-01 → 2025-06-07** — 1 build year (accumulate priced portfolio) +
~9.5 test years.

## Why this window, not the originally-proposed 11 years

- Elexon's `DISEBSP` system-prices dataset begins abruptly on **2015-11-07**
  (first complete day; 2015-11-06 has a single trailing record, 2015-11-05
  and earlier return empty). This is a real-world discontinuity, not an API
  limitation: **BSC Modification P305** replaced the old SSP/SBP imbalance
  pricing methodology in November 2015, so there is no earlier data under the
  current methodology to splice onto.
- An 11-year window anchored on "today" (2026-06-07) would either overshoot
  into the future (violating the Point-in-Time Blindfold law) or reach back
  before the dataset starts. Trimming to ~10.5 years, ending today, is the
  window that fits cleanly inside both constraints.
- Legacy pre-2015 imbalance pricing was deliberately **not** investigated —
  even if retrievable, it reflects a different pricing methodology and would
  introduce a methodological discontinuity not worth the complexity at this
  stage. The simulation works entirely within the post-P305 regime.
- 2016-01-01 (rather than 2015-11-07) was chosen as the start so the window
  begins on a clean calendar-year boundary, comfortably clear of the dataset's
  ragged opening days.

## Completeness evidence

Sampled 227 days (1st & 15th of every month, 2016-01 → 2025-06) plus all 19
UK clock-change days in range:

- **226/227** sampled days returned a clean 48 settlement periods, HTTP 200,
  no gaps
- **1/227** — 2019-01-01 — returned 47 records, missing settlement period 23.
  An isolated single-period gap, not part of a pattern (~0.4% of sample)
- All 9 spring-forward days → 46 periods, all 10 autumn-back days → 50
  periods — DST transitions are represented correctly and consistently

## Implication for ingestion

Build the sim/ ingestion path to **tolerate occasional missing settlement
periods** (don't assert a fixed 48-per-day count) and to **expect 46/50-period
days around the UK's DST transitions** (don't treat them as anomalies).
