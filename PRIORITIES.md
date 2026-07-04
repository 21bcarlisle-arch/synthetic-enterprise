# PRIORITIES.md -- Synthetic Enterprise
# Last refreshed: 2026-07-04 (Phase PZ: regime-change blindness CLOSED; P1 endgame complete)

## COMPLETED
- P1a: PROJECT_STATE.txt auto-sync -- FIXED (Phase PT; GH Pages fix 2026-07-04)
- P1b: customer_sample.json + customers.json + supplier.json at stable fetchable paths -- DONE (Phase PT)
- P1c: Shadow HTML site (4 sections) -- DONE (site/shadow/* auto-regenerating on every run)
- P2 (billing): Billing & Payment Infrastructure -- DONE (Phases PP/MW/MX/MY/NH)
- P2 (network): Network Charge Year-Indexed Actuals -- DONE (Phase 78; PROJECT_OVERVIEW.md Sec 9 gap closed)
- P3: Population Anchoring -- DONE (Phases NS/PQ/PR/PS: switching, churn, complaints, arrears)
- P4: Shadow Live Operation -- DONE (Phases PU/PV: live decisions + market adapter)
- P1 (correlated market): Correlated Synthetic Market Generator -- DONE (Phase PX: bivariate OU adapter; Phase PY: equivalence gate PASS)
- P1 (endgame): Scenario Stress Testing -- DONE (Phase PZ: 4 scenarios; regime-change blindness CLOSED 2026-07-04)

## PRIORITY 1 -- COMPANY OPERATIONAL INDEPENDENCE (next focus)
Company layer shares code-execution paths with SIM.
True independence = company runs end-to-end against observable market data only.
Precondition for fully clean P4 live operation architecture.
Foundation: Phase PV (market adapter) + Phase PZ (scenario analysis). Next: decouple company
decision loop from needing sim/ imports.

## Backlog (not queued)
- C2/C3/C4 resi EAC benchmarking vs Ofgem TDCV by dwelling type
- Smart meter customers on real HH shapes for segment model
- EPC-calibrated consumption distributions (requires GOV.UK data access)
- BSUoS year-indexed actuals
