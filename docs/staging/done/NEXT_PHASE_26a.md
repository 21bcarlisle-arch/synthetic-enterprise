# Phase 26a: Industrial Demand Profile + Risk Committee EAC Calibration

## Status: PROPOSED

## Motivation

Phase 24a (C_IC1) used a scaled C7 residential HH shape (156× amplification) for
the 2 GWh industrial customer. While this is volume-correct (~2 GWh/year), the
shape is fundamentally wrong:
- Residential shape: peaks morning/evening, high winter, low summer, sensitive to
  temperature
- Industrial warehouse shape: relatively flat Mon-Fri, near-zero weekends, 
  low overnight (00:00-06:00), temperature-insensitive (climate-controlled warehouse),
  no heating-demand seasonality

This matters for:
1. **ToU tariff pricing accuracy**: C_IC1 pays peak rates on residential peak periods
   (07:00-11:00, 16:00-20:00), but an industrial customer's actual peak usage is
   during core operational hours (08:00-17:00 Mon-Fri)
2. **Churn model**: bill stress is computed from EAC × rate. With a flat industrial
   profile vs spiked residential, the actual bill per period is more predictable
3. **Risk committee context**: `sigma_recent` from VaR uses declared EAC (3,500 kWh
   for C2). After Phase 25a, hedging uses calibrated EAC. The risk committee
   should be consistent.

## What Phase 26a builds

### Part A: Industrial demand profile for C_IC1

1. Generate `sim/hh_data/C_IC1_industrial.csv` with a realistic warehouse HH profile:
   - Mon-Fri: 08:00-18:00 = base load × 1.2 (operations); 06:00-08:00 = ramp up; 
     18:00-22:00 = ramp down; 22:00-06:00 = minimal (security lighting + HVAC standby)
   - Saturday: 40% of weekday load (half-shift operations)
   - Sunday: 15% of weekday load (maintenance + security)
   - No temperature sensitivity (controlled warehouse environment)
   - Annual total: ~2 GWh (scale factor derived from target annual kWh)

2. Replace `sim/hh_data/C_IC1.csv` (scaled residential) with industrial profile

3. Update C_IC1 `home_type` from `warehouse_unit` to reflect industrial nature in
   property model (no solar, no EV charging, no heating_degree_days impact)

### Part B: Risk committee EAC calibration

Update lines 998-1009 of `simulation/run_phase2b.py` to use `_company_eac_estimate()`
for `total_eac_active` and per-customer EAC in VaR context handshake:

```python
# Phase 26a: risk committee uses calibrated EAC (billing-derived), not declared
total_eac_active = sum(
    _company_eac_estimate(c["customer_id"], period_date_str, all_records)
    for c in active_elec
)
```

This makes the risk committee's portfolio sizing consistent with the hedging
calibration (Phase 25a). Before Phase 25a, hedging used declared EAC so consistency
was less important. Now hedging uses billing-derived EAC, but VaR still uses declared
EAC — creating an inconsistency.

### Annual report

- Add `industrial_demand_profile_summary` to run output: peak-to-average ratio, 
  weekday vs weekend load ratio, confirmation of ~2 GWh annual total
- `_section_demand_estimation()` already covers EAC calibration accuracy

## Expected impact

- C_IC1 ToU billing: under industrial profile, C_IC1 uses more power during
  08:00-17:00 core hours. Current ToU peak periods (07:00-11:00, 16:00-20:00)
  partially overlap with industrial core hours, but afternoon peak (16:00-20:00)
  misses the industrial shutdown. Revenue impact uncertain.
- Bill shock events: industrial profile is smoother (no demand spikes from 
  heating/cooling). Fewer bill shock events for C_IC1 despite its large spend.
- Risk committee VaR: Part B should produce more accurate portfolio VaR figures,
  especially after EV customers (C2/C4) accumulated billing history.

## Dependencies

- Phase 24a: C_IC1 added ✅
- Phase 25a: EAC calibration from billing ✅ — Part B extends this to risk committee

## Token estimate

~0.5 frontier sessions (Part A: generate CSV, update HH loader; Part B: 3-line
change to risk committee VaR calculation)

## Note

Phase 26a does NOT change C_IC1's segment designation or contractual structure.
Industrial ToU pricing, tranche hedging, and demand response are Phase 27+ topics.
This phase is purely about fidelity of the underlying demand data and risk consistency.
