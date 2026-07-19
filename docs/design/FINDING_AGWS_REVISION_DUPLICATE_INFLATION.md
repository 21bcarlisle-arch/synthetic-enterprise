# FINDING (queued atom) — AGWS revision-duplicate records inflate renewable_mw

**Surfaced by:** the SSP price-engine recalibration fork (2026-07-19), while joining real
renewables data for calibration. **Disposition:** QUEUED as a candidate atom (SELF_INTERRUPT_DISCIPLINE
— a shared-code data-quality bug is not fixed on sight mid-build; the recal worked around it *locally*
in `simulation/run_phase3b_recalibration.py` and left the shared aggregator untouched). `provenance:
proposal` — DISCOVER/FRAME-workable now, BUILD when opened.

## The bug (observed-with-evidence, R9)
`sim/cache/elexon_agws_full.json` contains **revision-duplicate records**: the same
`(settlementDate, settlementPeriod, fuelType)` appears multiple times because Elexon republishes
settlement runs (II → SF → R1 → R2 → R3 …) each with a later `publishTime`. The existing aggregator
in `sim/generation_demand_history.py` (`aggregate_wind_generation` / `aggregate_renewable_generation`)
**naively sums all rows** for a period rather than taking the latest-published revision per
`(period, fuelType)`. For a handful of heavily-republished periods this inflates
`renewable_generation_mw` to **millions of MW** (physically impossible — GB renewable capacity is
tens of GW), which then corrupts any downstream residual-demand / margin computation for those periods.

## Blast radius
- **Confirmed consumer:** the price-engine recalibration (worked around locally — deduped to latest
  `publishTime` before aggregating; this is why the recal's stats are clean).
- **Potentially affected (unaudited):** the existing `simulation/run_phase3b_regression.py` OLS fit and
  `run_phase3b_calibration.py` both call the same aggregator on the same cache — their published
  coefficients/MAE **may carry the same inflation** for the affected periods (the effect is small in
  aggregate — few periods — but real; the OLS wind coefficient is the most exposed).
- Any future coupled-cascade physics (Epoch-2 weather→gen→residual→price) that reads this aggregator
  would inherit the bug — so it gates cascade fidelity, matching the price-engine's role.

## Fix direction (for BUILD, when opened)
Dedup at the aggregator: group by `(settlementDate, settlementPeriod, fuelType)`, keep the row with the
**max `publishTime`** (latest settlement revision), then sum across fuel types. This is the correct
"latest-published-revision" semantics real settlement systems use. Make it **R15-failable**: a mutation
test that injects a duplicate `(period, fuelType)` with an inflated quantity and an earlier `publishTime`
must show the aggregator IGNORES it (takes the latest, not the sum) — the control fails if the naive-sum
form is restored. Re-run `run_phase3b_regression.py` after the fix and diff the coefficients to quantify
the inflation the published OLS carried (honest re-statement, not silent).

## Why queued, not fixed now
Fixing a shared aggregator mid-recal-build would (a) widen the recal fork's file_scope and risk the
merge, (b) change the OLS baseline the recal was measured against under its feet. The recal's local
dedup is the correct isolation. This finding homes the real fix as its own atom against the
`sim/generation_demand_history.py` aggregator, with the OLS re-statement as its acceptance evidence.
