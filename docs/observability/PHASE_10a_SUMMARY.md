# Phase 10a Summary — Segment Customer Model

**Completed: 2026-06-20**
**Commit: 05372e9**

## What was built

- **`simulation/segments.py`**: `CustomerSegment` dataclass + 5 segment definitions:
  - `resi_standard` (150 customers, PC1, 3,100 kWh avg)
  - `resi_smart` (20 customers, PC1 shape, 2,800 kWh avg — lower consumption from smart visibility)
  - `sme_standard` (40 customers, PC3, 35,000 kWh avg)
  - `sme_smart` (5 customers, PC3, 32,000 kWh avg)
  - `gas_resi` (80 customers, gas, 13,250 kWh avg)
  - `apply_annual_headcount_changes()`: deterministic annual churn, smart-upgrade transfer, and acquisition

- **`simulation/run_segments.py`**: Full 2016-2025 simulation loop using segments:
  - Volume = `headcount × avg_kwh × PC-shape-scale` per period
  - Unit rate re-priced each annual term at current headcount EAC
  - Headcount evolves at year boundaries: churn (e.g. 15% resi), smart upgrades (3-10%/yr, per UK rollout), acquisition
  - Same hedging physics, risk committee, and hedge evolution as run_phase2b
  - Non→Smart flow: `resi_standard → resi_smart`, `sme_standard → sme_smart`

- **`tests/simulation/test_segments.py`**: 21 new tests — segment definitions, shape scaling, headcount dynamics, volume arithmetic. All passing.

## Key findings

- **Speed unchanged**: O(segments × periods) — same as 9-customer model, just with credible unit economics. A segment with headcount=150 is trivially fast (one shape lookup per date, scaled by 150).
- **Unit economics credible immediately**: fixed overhead of £50/month ÷ 295 initial customers = £0.17/customer/month (vs £5.56/customer in the 9-customer model). The segment model makes overhead analysis meaningful.
- **PC1 integrates to ~3,933 kWh/yr**, PC3 to ~13,610 kWh/yr (2020 calibration year). Scale factors (`shape_scale = avg_kwh / calibration_kwh`) applied to match actual segment avg_kwh_per_customer.
- **Starting treasury £508,300** (vs £3,250 in old model) — correctly sized to 295 customers × comparable EAC per the same £3,250/15,000 kWh formula.
- **Risk committee fires monthly** at this scale (VaR exceeds threshold regularly due to large absolute EAC). This is correct behavior — a £500k treasury book should have active risk management.

## Key decisions

- **Additive, not replacing**: run_segments.py runs in parallel to run_phase2b.py. Named-customer model preserved for backward compatibility and benchmarking.
- **Profile class shapes for all segments**: including "smart" segments use PC1/PC3 shapes (not real HH data). Smart vs Standard distinction is in churn rate and avg_kwh, not metering type. True HH shape for smart segments deferred to Phase 10b.
- **Deterministic headcount evolution**: no stochastic acquisition — `acquired = round(attempts × win_rate)`. Keeps simulation fast and deterministic for testing. Stochastic acquisition can be added in Phase 10c.
- **FORWARD_CURVE fix already applied**: `sim/forward_curve.py` already computes pstdev from daily means (not half-hourly), giving ~45% average premium vs ~116% before. FORWARD_CURVE_FIX_PROPOSAL.md archived.

## Open questions

1. **Annual report integration**: run_segments.py currently runs standalone. Phase 10b should wire it into `annual_report.py` as an optional engine (controlled by a CLI flag), with a segment-level P&L section in the report.
2. **Benchmark Phase 9a vs Phase 10a economics**: once the full 9.5yr segment run completes, compare gross/net margin, capital cost ratio, and headcount trajectory to understand what scale does to unit economics.
