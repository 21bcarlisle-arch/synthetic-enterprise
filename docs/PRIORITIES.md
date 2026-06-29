# Current Priorities

Last updated: 2026-06-29 by Claude Code (Phase V complete)

## Now (active this session)
- Phase W: Gas Boiler Demand HDD Shape -- replace flat gas AQ distribution with HDD-seasonal
  shape (mirrors Phase I for electricity ASHP). Last major settlement accuracy gap: gas boilers
  peak sharply in winter but settlement currently distributes AQ evenly across all half-hours.

## Next (queued, unblocked)
- Phase X: ToU Product Launch Decision Engine -- company-layer model for deciding whether to
  launch a ToU product given EV penetration, cross-subsidy exposure (Phase U), and migration
  risk (Phase V). Completes T-V analytics to decision loop.
- Phase Y: Annual Run Integration -- wire Phase A-V household physics into run output summary.
  HDD-shaped gas + EV overnight + battery dispatch should shift the annual P&L numbers.

## Backlog
- Dashboard KPI coverage (company P&L trends, household asset mix over time)
- Integration tests: end-to-end workflow tests across module seams

## Recently completed (last 12)
- Phase V (2026-06-29) -- ToU Migration Impact Scenario (16 tests; 4,990 total)
- Phase U (2026-06-29) -- EV Cross-Subsidy Register (16 tests; 4,974 total)
- Phase T (2026-06-29) -- ToU Tariff Profitability Assessor (16 tests; 4,958 total)
- Phase S (2026-06-29) -- Unified Dual-Fuel Billing Engine + Payment Ledger (44 tests; 4,930 total)
- Phase R (2026-06-29) -- SEG Export Estimator (21 tests; 4,886 total)
- Phase Q (2026-06-29) -- Battery Home Energy Storage Settlement Wiring (14 tests; 4,865 total)
- Phase P (2026-06-29) -- EV Smart Charging Shape (12 tests; 4,942 total)
- Phase O (2026-06-29) -- Solar Dynamic Settlement Wiring (12 tests; 4,851 total)
- Phase N (2026-06-29) -- EV Settlement Wiring + Physical Suitability Constraints (26 tests; 4,861 total)
- Phase M (2026-06-29) -- Renewal Conversion Rate Book (21 tests; 4,835 total)
- Phase L (2026-06-29) -- Tariff Segment Profitability Book (21 tests; 4,814 total)
- Phase K (2026-06-29) -- Break-Even Tariff Assessor (21 tests; 4,782 total)
