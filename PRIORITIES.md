# PRIORITIES.md -- Synthetic Enterprise
# Last refreshed: 2026-07-04 (Phase PY: statistical equivalence gate PASS; endgame backlog gate UNLOCKED)

## COMPLETED
- P1a: PROJECT_STATE.txt auto-sync -- FIXED (Phase PT + HARD GATE verified 2026-07-03T21:36:23Z)
- P1b: customer_sample.json + customers.json + supplier.json at stable fetchable paths -- DONE (Phase PT)
- P1c: Shadow HTML site (4 sections) -- DONE (site/shadow/* auto-regenerating on every run)
- P2 (billing): Billing & Payment Infrastructure -- DONE (Phases PP/MW/MX/MY/NH)
- P2 (network): Network Charge Year-Indexed Actuals -- DONE (Phase 78; PROJECT_OVERVIEW.md Sec 9 gap closed)
- P3: Population Anchoring -- DONE (Phases NS/PQ/PR/PS: switching, churn, complaints, arrears)
- P4: Shadow Live Operation -- DONE (Phases PU/PV: live decisions + market adapter)

## PRIORITY 1 -- CORRELATED SYNTHETIC MARKET GENERATOR (Phase PX)
Gate condition: P4 done + P2 network charges done. GATE NOW LIFTED.
Bivariate OU process (calibrated from 2016-2025 NBP+SSP) plugs in as CorrelatedGeneratorAdapter
satisfying MarketDataPort (Phase PV guarantee: zero company-layer changes).
Enables scenario stress testing: base/bull/bear market decisions without touching company layer.
Addresses CLAUDE.md known failure: regime-change blindness.
NEXT_PHASE.md draft exists (written 2026-07-04T03:30 BST; 4h opt-out window expires ~07:30 BST).

## PRIORITY 2 -- COMPANY OPERATIONAL INDEPENDENCE (long horizon)
Company layer shares code-execution paths with SIM.
True independence = company runs end-to-end against observable market data only.
Precondition for fully clean P4 live operation architecture.

## Backlog (not queued)
- C2/C3/C4 resi EAC benchmarking vs Ofgem TDCV by dwelling type
- Smart meter customers on real HH shapes for segment model
- EPC-calibrated consumption distributions (requires GOV.UK data access)
- BSUoS year-indexed actuals
- CORRELATED SIMULATION ENDGAME (full, long horizon, gated): free-running weather+market generator
  with NO historical replay; statistical-equivalence gate required (distributional moments + tail
  frequencies + stylised facts). Phase PX (bivariate OU adapter) is the intermediate step; full
  endgame follows after statistical-equivalence validation.
