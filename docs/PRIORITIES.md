# Current Priorities

Last updated: 2026-06-30 by Claude Code (Phase AI complete)

## Now (active this session)
- Phase AI: EAC Drift Snapshot -- COMPLETE (2026-06-30). 10 new tests (5,266 total).
  saas/reporting/annual_report.py: _section_eac_drift_snapshot() per-customer demand drift from billing history.

## Next (queued, unblocked)
- Phase AJ: CRM Intelligence Books wired into run snapshot (PortfolioChurnRiskBook/PortfolioRepricingBook
  summary populated in run JSON; annual report shows final-year churn risk bands and repricing priorities).
  ~12-15 tests. Requires care in run_phase2b.py (large loop — add at term-end, not mid-loop).

## Backlog
- Dashboard: Flexibility revenue tab (per-year CM/DFS data from flexibility_revenue_by_year)
- Integration tests: end-to-end workflow tests across module seams
- I&C Triad management model (active demand reduction in Triad windows for 1-4 GWh customers)
- Real forward curve (NBP/EPEX term structure) — HIGH fidelity, substantial work

## Recently completed (last 12)
- Phase AI (2026-06-30) -- EAC Drift Snapshot (10 tests; 5,266 total)
- Phase AH (2026-06-30) -- Board Intelligence Pack (12 tests; 5,256 total)
- Phase AG (2026-06-30) -- Annual Report Flex Revenue Section (12 tests; 5,244 total)
- Phase AF (2026-06-30) -- DSR/Flexibility Revenue Integration (15 tests; 5,232 total)
- Phase AE (2026-06-29) -- Customer Retention Offer Book (21 tests; 5,217 total)
- Phase AD (2026-06-29) -- Portfolio Churn Risk Book (34 tests; 5,196 total)
- Phase AC (2026-06-29) -- Portfolio Repricing Action Book (24 tests; 5,162 total)
- Phase AB (2026-06-29) -- EAC Drift Assessor (35 tests; 5,138 total)
- Phase AA (2026-06-29) -- Demand Flexibility Potential Assessor (23 tests; 5,103 total)
- Phase Z (2026-06-29) -- Smart Meter Consumption Reconciliation (23 tests; 5,080 total)
- Phase Y (2026-06-29) -- ToU Rate Card Optimiser (29 tests; 5,057 total)
- Phase X (2026-06-29) -- ToU Product Launch Decision Engine (25 tests; 5,028 total)
