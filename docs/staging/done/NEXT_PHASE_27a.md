# Phase 27a: Second I&C Customer — Commercial Office (C_IC2)

## Status: PROPOSED

## Motivation

Phase 24a–26a established the I&C customer foundation: HH metering, EAC calibration,
realistic industrial demand shape, risk committee consistency. C_IC1 is a warehouse
(temperature-insensitive, Mon-Fri core hours, 2 GWh/year).

A single I&C customer limits what we can learn about I&C portfolio dynamics:
- No diversity test: retention/churn behaviour, tariff pricing, VaR all reflect one
  customer archetype
- No office-building shape: temperature-sensitive cooling load, M-F business hours,
  occupancy-driven profile (very different from warehouse)
- No I&C portfolio scaling test: risk committee VaR and hedging fraction across 3+ GWh
  industrial load

The natural next I&C customer is a commercial office building:
- 1 GWh/year (~500× smaller than C_IC1 per period)
- Temperature-sensitive (A/C summer peak, moderate heating winter)
- Monday-Friday occupancy driven (08:00-18:00), some Saturday half-load
- Birmingham or Leeds (similar UK grid region as C_IC1 for correlation purposes)

## What Phase 27a builds

### Part A: C_IC2 customer definition

`saas/customers.py`: add C_IC2
```python
{
    "customer_id": "C_IC2",
    "name": "Midlands Office Park",
    "segment": "I&C",
    "postcode": "B1 1AA",
    "eac_kwh": None,                # HH-metered, EAC from settlement
    "fuel": "electricity",
    "metering": "HH",
    "acquisition_date": "2018-01-01",
    "home_type": "office_building",
    "assets": {"solar": False, "ev": False},
}
```

### Part B: Office building HH demand profile

Generate `sim/hh_data/C_IC2.csv` with commercial office pattern:
- Weekday: 08:00-18:00 = 100% load; 06:00-08:00 = ramp-up; 18:00-22:00 = ramp-down;
  22:00-06:00 = 5% standby
- Saturday: 30% of weekday (weekend occupancy for some tenants)
- Sunday: 8% (security + minimal HVAC)
- Summer peak (Jun-Aug): +15% on peak hours (A/C load)
- Winter trough (Dec-Feb): -5% (less cooling load)
- Annual total: ~1 GWh/year

### Part C: EFFECTIVE_EAC_KWH and starting treasury

`simulation/run_phase2b.py`:
- Add `C_IC2` to `EFFECTIVE_EAC_KWH` (~1,000,000 kWh)
- Starting treasury scales up slightly (now 3 GWh total I&C)
- `is_hh_customer()` already handles any HH customer via segment/metering check

### Part D: Annual report section

`saas/reporting/annual_report.py`: extend `_section_ic_demand()` (or add new
`_section_ic_portfolio()`) showing:
- Per-I&C-customer annual EAC vs calibrated estimate
- I&C portfolio share of total revenue and gross margin
- C_IC1 vs C_IC2 profile comparison (seasonal pattern difference)

## Expected impact

- Total portfolio: ~3.2 GWh electricity (up from ~2.2 GWh), I&C now ~62% of volume
- Revenue: additional ~£200k/year gross billing
- Risk committee: VaR scales with portfolio size; C_IC2 provides diversification
  (office cooling load inversely correlated with warehouse load seasonally)
- Annual report: I&C portfolio section shows diversity of I&C demand shapes

## Dependencies

- Phase 24a: C_IC1 added ✓
- Phase 25a: HH EAC calibration from billing ✓
- Phase 26a: industrial demand profile (fidelity baseline) ✓

## Token estimate

~0.5 frontier sessions (Part A: 10-line customer definition; Part B: CSV generation
script ~100 lines; Part C: 2 constant additions; Part D: 20-line report section)

## Notes

- C_IC2 starts 2018-01-01 (one year after C_IC1) — this creates a natural first-term
  fallback (no prior billing) for _company_eac_estimate(), testing the fallback path
- I&C segment designation for both C_IC1 (retroactively corrected from "SME") and
  C_IC2 makes the segment breakdown in reports accurate
- Office profile with summer cooling distinguishes from warehouse — tests seasonal
  divergence section in annual report
