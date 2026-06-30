# Simulation Status -- LATEST

Last updated: 2026-06-30T03:59:38Z

## Current state

- **Phase:** BJ complete (Churn Prediction Calibration section)
- **Tests passing:** 5,621 (all green)
- **Python modules:** 340+
- **Company modules:** 272+
- **Net position (latest sim run):** £1,243,337

## Latest run figures (git 11d76e4, 2026-06-30)

| Metric | Value |
|--------|-------|
| Total Revenue | 14,137,721 |
| Gross Margin | 6,462,146 |
| Net Margin | 1,243,337 |
| Enterprise Value | 6,142,209 |
| Administration Event | None |

## This session: phases AY-BJ (18 phases this continuation)

- **Annual report dedup fix:** Removed duplicate _section_management_accounts call
- **Dashboard refresh:** run_insights.json regenerated from latest run data (was stale)
- **Report sections added (BG-BJ):** CLV Evolution / Dynamic Pricing Activity / Tariff Accuracy / Churn Calibration
- **Report sections added (AY-BF):** Strategic Value Matrix / Bill Shock / Policy Cost / Commodity Split / Committee Activity
- **New company modules:** Triad Notification / Price Elasticity / Committee Ledger / Renewal Pricing Engine / Acquisition Strategy

-> Full build history: docs/PROJECT_OVERVIEW.md Section 4

**Latest simulation results (2016-2025)** — auto-processed (457s / 8 min):
- Net margin: £6,239,245.03 | Gross: £6,475,913.39 | Capital: £236,668
- Treasury: £2,466,636 -> £3,709,973 | 38 committee interventions | 1531 bills issued
- Enterprise value: £6,037,509.08 | Net after CTS: £6,370,846
- Retention: 18 offers, 17/18 retained | 5 no-offer churns | 6 total churned accounts
