# Phase 46: Resi Gas Margin Calibration + Sanity Check Tuning

## Context

After Phase 45c (GAS_RISK_PREMIUM_FRACTION 20%→10%), resi/gas net margin is expected to
land at ~5% (down from 13%) vs the 2-4% Ofgem benchmark. This is marginal — within 2x of
the benchmark, but still flagged as an anomaly.

Root cause: resi gas customers are CCL-exempt (zero policy cost) so the only deductions
from the risk premium are: network cost (~£4/MWh) and capital. The 10% risk premium on a
typical resi gas unit_rate (~£40/MWh) leaves ~£4/MWh net, which on a £40 revenue base
is 10%. Reducing further to 5% would give ~£2/MWh net (~5%) — still above 2-4% benchmark.

True alignment requires either:
1. Gas risk premium of 3-5% (realistic for domestic fixed terms)
2. Or acknowledgment that 5% is within model tolerance for 9-year cumulative

## What Phase 46 would build

**Option A (Recommended): Lower gas fixed premium further**
- `GAS_RISK_PREMIUM_FRACTION`: 10% → 5%
- Only affects fixed gas tariffs (pass-through already bills at spot + £2/MWh)
- UK resi gas fixed tariffs: suppliers price at NBP + ~5% margin (including network)
- 2 new tests, minimal change

**Option B: Widen resi/gas benchmark**
- Change `SEGMENT_BENCHMARKS["resi/gas"]` from `(-2.0, 6.0)` to `(-2.0, 8.0)`
- Acknowledges that 9-year cumulative data naturally exceeds single-year benchmarks in
  years where churn removed crisis losses
- 0 code changes, just benchmark tolerance update

**Decision for Rich**: A is more realistic (reduces actual pricing error). B is defensible
(simulation is internally consistent, cumulative data differs from annual data).

## Expected outcome

With Option A (5%):
- resi/gas: ~5% → ~3% net (within benchmark)
- resi/elec: Already fixed by Phase 45c (~4.4%)
- All segments expected to be within benchmark range

Sanity check should show 0 anomalies after Phase 46A.

## Dependencies

- Phase 45c must complete and show resi/gas at ~5% (as predicted)
- No other blocking dependencies

## Test estimate

2 new tests (constant value + forward price test). No interface changes.
