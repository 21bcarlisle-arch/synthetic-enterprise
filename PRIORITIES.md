# PRIORITIES.md -- Synthetic Enterprise
# Last refreshed: 2026-07-04 (Infra: PROJECT_STATE.txt GH Pages fix + watchdog exit-reason; endgame pending advisor confirmation)

## COMPLETED
- P1a: PROJECT_STATE.txt auto-sync -- FIXED (Phase PT; GH Pages fix 2026-07-04)
- P1b: customer_sample.json + customers.json + supplier.json at stable fetchable paths -- DONE (Phase PT)
- P1c: Shadow HTML site (4 sections) -- DONE (site/shadow/* auto-regenerating on every run)
- P2 (billing): Billing & Payment Infrastructure -- DONE (Phases PP/MW/MX/MY/NH)
- P2 (network): Network Charge Year-Indexed Actuals -- DONE (Phase 78; PROJECT_OVERVIEW.md Sec 9 gap closed)
- P3: Population Anchoring -- DONE (Phases NS/PQ/PR/PS: switching, churn, complaints, arrears)
- P4: Shadow Live Operation -- DONE (Phases PU/PV: live decisions + market adapter)
- P1 (correlated market): Correlated Synthetic Market Generator -- DONE (Phase PX: bivariate OU adapter; Phase PY: equivalence gate PASS)

## PRIORITY 1 -- CORRELATED SIMULATION ENDGAME (on hold: awaiting PROJECT_STATE.txt advisor confirmation)
Gate: PY statistical-equivalence gate PASS (done). Advisor must confirm PROJECT_STATE.txt fresh at
21bcarlisle-arch.github.io/synthetic-enterprise/status/PROJECT_STATE.txt before starting.
Goal: scenario stress testing -- run live renewal/hedging decisions against base/bull/bear/crisis
market scenarios using CorrelatedGeneratorAdapter. Demonstrates regime-change blindness is now
addressable: board can see hedge recommendations under 2021-22 style volatility without historical replay.

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
