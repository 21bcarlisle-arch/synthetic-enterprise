# LATEST -- Synthetic Enterprise Simulation
Last updated: 2026-07-03T15:50:41Z

## Current Status
Phase OA COMPLETE (2026-07-03) -- I&C Broker/TPI Commission Model: tpi_book.py wired into run_phase2b.py; Standard Energy Broker at £1.5/MWh (0.15 p/kWh); actual settled consumption per customer per year; tpi_summary in results; board section. I&C gross margin was previously overstated by this commission cost. 21 tests, 14,941 total.

Phase NZ COMPLETE (2026-07-03) -- Ofgem FRA Regulatory Capital Ratio: fra_capital_ratio.py; FRACapitalRatio(equity/monthly_rev/fra_ratio/rag/is_compliant); SIM supplier 16-32x all GREEN; 2022 weakest at 16.8x. 24 tests, 14,908 total.

Phase NY COMPLETE (2026-07-03) -- Flexibility Revenue Site/ Dashboard: extract_flexibility() + dashboard["flexibility"]; _section_flexibility_revenue extended (Phase AG/NX). Backlog item closed. 15 tests, 14,884 total.

Phase NX COMPLETE (2026-07-03) -- I&C Demand Response Enrollment: £21k CM/DFS 2016-2025 (was £0). 24 tests, 14,869 total.

## Last Run
Net position: £1,445,258 (git f432904b, 2026-07-03)

## Test Suite
- **14,941 tests passing**
- Epistemic verifier: PASS
- PRIORITIES.md refreshed: OA DONE, OB (settlement reconciliation) next

**Latest simulation results (2016–2025)** — auto-processed (508s / 8 min):
- Net margin: £1,445,257.67 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts
- I&C TPI commission (Phase OA): £1.5/MWh trail on actual consumption; total commission visible in board section
