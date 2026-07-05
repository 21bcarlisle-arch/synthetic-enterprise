## Phase QM COMPLETE -- Retention as Deferral, H1 vs H2
Last updated: 2026-07-05T01:13:43Z

**Status:** COMPLETE. 15,555 tests collected (fast suite). Epistemic: PASS.

**Phase QM -- Retention as Deferral (docs/staging/QL_WIRE_AND_DEFERRAL.md):**
- simulation/run_phase2b.py: ASSUMED_DEFERRAL_MONTHS=12 (H1), named on every retention offer
- company/analytics/retention_deferral_economics.py (new): H2 realized deferral + serial-saver EV flag
- Evidence on all 3 surfaces: Sim (H1 vs H2 by year), Customers (C_IC1 4-offer timeline), Supplier (serial-saver table)
- saas/reporting/annual_report.py: _section_retention_deferral_economics() board section

**KEY FINDING:**
- 0/10 resolved offers underperformed their assumed 12-month window
- C1/C5/C6 (Phase QK's defer-then-churn names) churned at 12-24 months post-offer, matching or exceeding H1
- The offer worked exactly as priced -- it was never priced to buy more than one term

**Prior milestone:** Phase PZ (Scenario Stress Testing) closed PRIORITIES.md P1 (Correlated Simulation Endgame).


**Latest simulation results (2016–2025)** — auto-processed (516s / 9 min):
- Net margin: £1,445,257.67 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 14 offers, 14/14 retained | 6 no-offer churns | 6 total churned accounts