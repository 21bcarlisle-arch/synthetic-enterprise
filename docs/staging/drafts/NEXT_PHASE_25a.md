# Phase 25a: EFFECTIVE_EAC_KWH Calibration — Fix Declared EAC vs Actual Consumption

## Status: PROPOSED

## Motivation

Phase 23a demand estimation analysis revealed a systematic mismatch between
`EFFECTIVE_EAC_KWH` (the declared pricing EAC) and actual settlement consumption
for PC1 residential customers. This is documented in REPORTING_BACKLOG.md items
18 and 19.

**The problem:**
- PC1 shape produces ~3,900 kWh/year regardless of declared EAC
- EV charging adds 8 kWh/night × 365 = 2,920 kWh/year for C2/C4
- C2 declared EAC = 3,500 kWh; actual consumption ≈ 6,820 kWh
- C4 declared EAC = 5,500 kWh; actual consumption ≈ 6,820 kWh (same — EV but no effective solar)
- Pricing is based on wrong EAC → tariff rates are wrong for these customers
- Hedging is based on wrong EAC → unhedged exposure is ~2× what the supplier thinks

**The consequence:**
- Supplier prices C2 assuming 3,500 kWh cost basis, but bills C2 for 6,820 kWh
- Revenue is ~2× the expected at that rate (possibly unintentional overcharge)
- Wholesale cost: hedge covers 3,500 × hf kWh but actual exposure is 6,820 kWh
- Effective hedge fraction for C2 = (3,500 × 0.85) / 6,820 = 43.5% (not 85%)
- During 2021-22 crisis: massive additional unhedged exposure = large unexpected losses

Also documented (item 19): solar generation is implemented in demand_model.py
but the irradiance parameter is never wired through from run_phase2b.py, so
C4's solar asset has zero effect on consumption.

## What Phase 25a builds

### Part A: Calibrate EFFECTIVE_EAC_KWH from actual settlement data

1. After the first full run, derive each customer's mean annual kWh from
   settlement records rather than customer declarations
2. Update `EFFECTIVE_EAC_KWH` to use settled kWh as the source of truth:
   ```python
   def _derive_eac_from_settlement(cid, all_records):
       # Mean annual kWh from settlement records
       annual_totals = {}
       for r in all_records:
           if r["customer_id"] == cid:
               year = r["settlement_date"][:4]
               annual_totals.setdefault(year, 0.0)
               annual_totals[year] += r["consumption_kwh"]
       if not annual_totals:
           return None
       return sum(annual_totals.values()) / len(annual_totals)
   ```
3. Use derived EAC for pricing and hedging in subsequent terms
4. First term still uses declared EAC (no settlement history yet)

This is the correct epistemic approach: the company measures actual consumption
from billing records and uses that for future pricing, not a static declaration.

### Part B: Wire solar irradiance into shape function

1. Load per-customer half-hourly irradiance from `sim/weather_engine`
2. Pass `irradiance_w_m2_periods` to `build_demand_shape()` for dates when
   irradiance data is available
3. C4 (solar: True) should see ~1,500-2,500 kWh/year reduction in consumption
4. This changes C4's company estimate from ~6,820 to ~4,800-5,300 kWh/year

## Expected impact

- C2/C4 EAC recalibrated to ~6,820 kWh → pricing rates recalculated on higher cost basis
- Higher tariff rates for C2/C4 → better margin, lower overcharge risk
- Better hedge sizing (hedging 6,820 × hf instead of 3,500 × hf)
- Solar wiring: C4 actual consumption drops from 6,820 to ~4,800-5,300 kWh
- demand_estimation_log `error_pct` drops from ~100% to near 0% for C2/C4

## Dependencies

- Phase 24a: C_IC1 added (DONE) ✅ — no conflict
- Run output: need a full run to derive calibrated EACs from settlement records
- REPORTING_BACKLOG items 18 and 19

## Token estimate

~0.5 frontier sessions (Part A is a targeted change to 2 functions; Part B is 
a wiring exercise through 1 module)

## Note: this changes run output

Part A changes pricing and hedging for C2/C4. A full re-run is required after
this phase. The financial results will change (higher tariff rates for C2/C4
→ slightly better margins, but this is a correction not a business improvement).
C_IC1 is unaffected (HH customer with accurate EAC from actual data).
