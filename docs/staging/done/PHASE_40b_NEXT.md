# Proposed Phase 40b: Deemed rate + gas pass-through

## What
- **Deemed rate**: out-of-contract I&C customers moved to day-ahead spot + 20% premium (industry standard for "rolled" contracts in the UK)
- **C_IC3 gas leg**: add C_IC3g (5 GWh industrial gas, Teesside, pass-through). Gas pass-through: NBP spot + margin locked, actual gas network + CCL + GGL billed at settlement
- **Annual report**: tariff type column in customer P&L ranking section

## Why now
C_IC3 electricity pass-through is working. Gas pass-through uses the same pattern — marginal change. Deemed rate requires a small architectural addition (contract gap detection) but unlocks realistic out-of-contract modelling.

## Sequencing
1. Gas pass-through (C_IC3g) — follow same pattern as electricity, verify gas settlement path
2. Deemed rate — add gap detection to renewal schedule; out-of-contract periods get spot+20%
3. Report update — tariff_type column

## Dependencies
- Gas renewal schedule (`_build_gas_renewal_schedule` in run_phase2b.py) — needs `tariff_type` param, same pattern as electricity
- Deemed rate needs a "spot price lookup" for the out-of-contract period (Elexon SSP cache already available)
