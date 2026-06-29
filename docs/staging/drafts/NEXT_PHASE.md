# Phase I: ASHP Seasonal Electricity Shape (HDD-Weighted)

Status: IN PROGRESS (2026-06-29)

## The gap

Phase G added ASHP electricity as a flat additive load:

    ashp_hh_kwh = ashp_annual_kwh() / 365.25 / 48  # uniform across all HH periods

The Phase G comment explicitly marks this as "a first approximation." A real ASHP
follows a strongly seasonal demand pattern: ~70% of consumption is space-heating
(scales with Heating Degree Days, same basis as gas), ~30% is DHW (flat year-round).

UK reference annual HDD sum (base 15.5C, E&W normals): ~2,066 HDD/yr.

January daily HDD ~11.3 -> ASHP daily kWh ~30 kWh (flat: 15.1 kWh) -- 2x flat
July daily HDD ~0.16 -> ASHP daily kWh ~0.42 kWh (flat: 15.1 kWh) -- 0.03x flat

This affects:
1. Imbalance costs (higher winter, near-zero summer)
2. Shape risk (settlement profile mismatches hedge)
3. BSUoS (time-of-use winter peaks)
4. Network charges (DUoS seasonal/triad exposure)

## What Phase I does

In _weather_adjusted_shape_fn (run_phase2b.py line 252-261), replace the flat adder
with an HDD-weighted additive. Split annual kWh: 70% heating (HDD-driven), 30% DHW (flat).
Uses get_hdd() and REFERENCE_MONTHLY_HDD from sim/weather_hdd.py (already exist).

Annual total ASHP electricity unchanged (5,500 kWh/yr by construction).

## Scope

Files to change:
- simulation/run_phase2b.py: replace flat ashp_hh_kwh adder (~5 lines)

Tests to add (~10):
- Winter day ASHP load > flat
- Summer day ASHP load < flat
- Annual integral over reference year ~= ashp_annual_kwh (conservation check)
- Non-ASHP customer unchanged
- DHW component always present (floor > 0 even in summer)
