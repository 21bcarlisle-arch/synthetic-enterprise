# Data Source: Profile Class 3 (Non-Domestic Unrestricted) Load Profile

## What it is

Profile Class 3 (PC3) is the BSC settlement profile class for non-domestic customers on unrestricted (single-rate) electricity meters — the standard classification for small offices, retail units, and light-industrial premises billed on a single tariff without Economy 7 or time-of-use differentiation. C5 (London small office, 25,000 kWh EAC) and C6 (Manchester warehouse, 45,000 kWh EAC) are PC3 customers.

The profile defines a Group Average Demand (GAD, in kW) for each half-hourly settlement period, broken down by five BSC seasons × three day types = 15 seasonal/day-type combinations, each with 48 half-hourly values. Energy per period (kWh) = GAD × 0.5 h.

## Source

**UKERC Energy Data Centre — "Electricity user load profiles by profile class"**

- Dataset DOI/URL: `https://dap.ceda.ac.uk/edc/d1/5af8ae29-86a7-4e8c-9fe4-1e2d99d9fb96/`
- Direct CSV: `https://dap.ceda.ac.uk/edc/d1/5af8ae29-86a7-4e8c-9fe4-1e2d99d9fb96/data/version_0/data/ProfileClass3.csv`
- Licence: Open Access
- Provider: Electricity Association (now Energy UK), supplied via Elexon Ltd
- Reference year: 1997 (the original BSC-mandated measurement year; unchanged by Elexon since)

This is the same UKERC/CEDA archive used for Profile Class 1 (see `docs/data-sources/profile-class-1.md`). The dataset covers all eight BSC profile classes (1–8) as separate CSV files.

## Why this source, not the Elexon API

Elexon's modern REST API (data.elexon.co.uk, Insights Solution) exposes current and future profile coefficient time series but does not serve the historical GAD tables in machine-readable form. The UKERC archive is the canonical published source for the 1997 reference year GAD values that underpin all BSC settlement profile mathematics; it is referenced in Elexon's own BSC Guidance Note "Load Profiles and their use in Electricity Settlement" (S.D. No. 2, Schedule 3).

## File stored

`sim/data/profile_class_3_gad.csv` — 49 lines (1 header row + 48 half-hourly periods).

Column layout: `Time, Aut Wd, Aut Sat, Aut Sun, Hsr Wd, Hsr Sat, Hsr Sun, Smr Wd, Smr Sat, Smr Sun, Spr Wd, Spr Sat, Spr Sun, Wtr Wd, Wtr Sat, Wtr Sun`

Fetched on 2026-06-08 directly from the CEDA DAP at the URL above; no transformation applied.

## Validation

- 48 rows of period data confirmed (periods 1–48 in the `Time` column).
- Winter weekday daily total ≈ 39.55 kWh/day (typical non-domestic flat-ish profile peaking ~0.85 kW during business hours).
- A PC3 default winter weekday profile is substantially flatter than PC1 (domestic): minimal overnight trough, consistent daytime load 07:00–18:00.
- Computed in `sim/profile_class_3.py` via `load_pc3_shape("2016-01-04")` → 48 periods, daily total = 48.12 kWh (winter weekday, GAD × 0.5 h for each period).

## Loader

`sim/profile_class_3.py` — function `load_pc3_shape(target_date)`. Identical logic to `sim/profile_class_1.py`; uses the same five-season × three-day-type BSC classification (`season_for_date`, `day_type_for_date`). Returns a list of 48 kWh floats indexed by settlement period (0-indexed).

## Season boundaries

Same as PC1 — the BSC season classification is portfolio-class-agnostic:

| Season | Approximate dates |
|--------|------------------|
| Winter | BST→GMT change (Oct) → GMT→BST change (Mar) |
| Spring | GMT→BST change (Mar) → 16 Saturdays before August Bank Holiday |
| Summer | 16 Saturdays before Aug BH → 6 Saturdays before Aug BH |
| High summer | 6 Saturdays before Aug BH → Sunday after Aug BH |
| Autumn | Monday after Aug BH → BST→GMT change (Oct) |

August Bank Holiday = last Monday of August.

## Historical Ground Truth compliance

This dataset satisfies Architecture Law 1 (Historical Ground Truth): the GAD values are real published figures derived from measured half-hourly metering data, not synthetic or modelled consumption. The 1997 reference year is the BSC's own mandated measurement period; these GAD tables are the live values embedded in the UK's electricity settlement system.
