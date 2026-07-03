# LATEST -- Synthetic Enterprise Simulation
Last updated: 2026-07-03T15:58:50Z

## Current Status
Phase OB COMPLETE (2026-07-03) -- Elexon Settlement Reconciliation Exposure: settlement_reconciliation.py; R1/R2/R3/RF timeline (1, 3, 5, 28 months); HH 0.5% / non-HH 4% variance; 90% HH portfolio -> GREEN RAG; crisis years (2021-22) flagged for net credit bias. 25 tests, 14,966 total.

Phase OA COMPLETE (2026-07-03) -- I&C Broker/TPI Commission Model: tpi_book.py wired; Standard Energy Broker GBP 1.5/MWh (0.15 p/kWh); actual settled consumption per year per customer; tpi_summary in results; board section. 21 tests, 14,941 total.

Phase NZ COMPLETE (2026-07-03) -- Ofgem FRA Regulatory Capital Ratio: fra_capital_ratio.py; 16-32x all GREEN; 2022 weakest. 24 tests, 14,908 total.

## Last Run
Net position: £1,445,258 (git 3fe6e96b, 2026-07-03)

## Test Suite
- **14,966 tests passing**
- Epistemic verifier: PASS
- PRIORITIES.md refreshed: OB DONE, OC (Licence Health Observatory) next

**Latest simulation results (2016–2025)** — auto-processed (540s / 9 min):
- Net margin: £1,445,257.67 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts