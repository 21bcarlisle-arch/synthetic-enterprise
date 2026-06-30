# Current Priorities

Last updated: 2026-06-30 by Claude Code (Phase AG complete)

## Now (active this session)
- Phase AG: Annual Report Flexibility Revenue Section -- COMPLETE (2026-06-30). 12 new tests (5,244 total).
  saas/reporting/annual_report.py: _section_flexibility_revenue() renders year-by-year CM vs DFS table.
  Pre-2022 rows labelled pre-DFS. Portfolio total with CM/DFS split. DFS launch note (NESO Oct 2022).

## Next (queued, unblocked)
- Phase AH: Network Charge Year-Indexed Costs -- DUoS/TNUoS currently flat pass-through in non_commodity.py.
  Year-indexed actuals would improve calibration (DUoS ~£15-20/MWh resi, rising with network investment).
  Closes Section 9 known gap. ~8-10 tests.

## Backlog
- Dashboard KPI coverage (company P&L trends, household asset mix over time)
- Integration tests: end-to-end workflow tests across module seams
- I&C Triad management model (active demand reduction in Triad windows for 1-4 GWh customers)

## Recently completed (last 12)
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
- Phase W (2026-06-29) -- Gas Boiler Daily HDD Shape (13 tests; 5,003 total)
- Phase V (2026-06-29) -- ToU Migration Impact Scenario (16 tests; 4,990 total)
