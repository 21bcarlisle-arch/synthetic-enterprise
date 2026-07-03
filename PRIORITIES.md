# PRIORITIES.md -- Synthetic Enterprise
# Last refreshed: 2026-07-03 (all P1-P3 complete; P4 is next)

## COMPLETED
- P1a: PROJECT_STATE.txt auto-sync -- FIXED (Phase PT + HARD GATE verified 2026-07-03T21:36:23Z)
- P1b: customer_sample.json + customers.json + supplier.json at stable fetchable paths -- DONE (Phase PT)
- P1c: Shadow HTML site (4 sections) -- DONE (site/shadow/* auto-regenerating on every run)
- P2: Billing & Payment Infrastructure -- DONE (Phases PP/MW/MX/MY/NH)
- P3: Population Anchoring -- DONE (Phases NS/PQ/PR/PS: switching, churn, complaints, arrears)

## PRIORITY 1 -- SHADOW LIVE OPERATION (P4)
Design + implement paper-trading mode against current real market data.
- Daily pricing, hedging, and retention decisions logged and timestamped.
- Zero capital at risk: decisions are recorded but not executed.
- Elexon BMRS API for live market prices.
- Converts sim from retrodiction to falsifiable live prediction.
- One-way-door architecture: DESIGN PROPOSAL to docs/staging/drafts/ first; Rich reviews.

## PRIORITY 2 -- NETWORK CHARGE YEAR-INDEXED ACTUALS
DUoS (~15-20/MWh) and TNUoS (~5-8/MWh) currently flat pass-through.
Real UK suppliers see annual band resets (Project Helix 2019; 2022 uplift).
Replacing flat model with year-indexed actuals closes named gap in PROJECT_OVERVIEW.md Sec 9.
Real fidelity: margins correct in reform years rather than systematically offset.

## PRIORITY 3 -- COMPANY OPERATIONAL INDEPENDENCE (long horizon)
Company layer shares code-execution paths with SIM.
True independence = company runs end-to-end against observable market data only.
Precondition for P4 live operation to be architecturally clean.

## Backlog (not queued)
- C2/C3/C4 resi EAC benchmarking vs Ofgem TDCV by dwelling type
- Smart meter customers on real HH shapes for segment model
- EPC-calibrated consumption distributions (requires GOV.UK data access)
- BSUoS year-indexed actuals
