# Simulation Status -- LATEST

Last updated: 2026-06-30T03:14:01Z

## Current state

- **Phase:** AU complete (Commodity Split: Electricity vs Gas P&L) -- phases P through AU shipped
- **Tests passing:** 5,414 (all green)
- **Python modules:** 330+
- **Company modules:** 267+
- **Net position (latest sim run):** £1,243,337

## Latest run figures (git 5e2a5dc, 2026-06-30)

| Metric | Value |
|--------|-------|
| Total Revenue | 14,137,721 |
| Gross Margin | 6,462,146 |
| Net Margin | 1,243,337 |
| Enterprise Value | 6,142,209 |
| Administration Event | None |

## Session (AH--AU): 15 phases, 178 tests added

Board intelligence synthesis: annual report now comprehensive.
- **AU:** Commodity Split (12 tests; gas loss-making 2021-2025, 5 consecutive years)
- **AT:** Management Accounts P&L (12 tests; 2016-2025 income statement + balance sheet)
- **AS:** Gas Exit Analysis Report Section (10 tests; REPRICE +£134k vs SQ)
- **AR:** Gas Exit Decision Book (14 tests; board-level scenario model)
- **AQ:** Board Risk Summary (12 tests; 6 RAG indicators: 4 RED, 1 AMBER, 1 GREEN)
- **AP:** Segment Capital Efficiency (12 tests; I&C gas ROC=-0.7x CAPITAL DESTROYER)
- **AO:** Demand Estimation Error Trend (12 tests; 0.07% -> 3.3%/15.6% by 2024)
- **AN:** Portfolio Concentration Risk (12 tests; HHI=2249 MODERATE, I&C=98.7%)
- **AM:** Pricing Basis Risk (12 tests; 2025 +32.8% over-estimate)
- **AL:** Counterfactual Retention (12 tests; £3,621 recoverable from 4 missed)
- **AK:** Churn Root Cause Attribution (14 tests; 6 churns, 4 blind misses)
- **AJ:** CRM Risk Triage (14 tests; CRITICAL/HIGH/MEDIUM/LOW + blind spots)
- **AI:** EAC Drift Snapshot (10 tests; demand drift per customer)
- **AH:** Board Intelligence Pack (12 tests; retention/flex/churn synthesis)
- **Board finding:** Gas cross-subsidy confirmed 5 years; REPRICE_GAS recommended; I&C concentration existential; churn blind miss 67%.

-> Full build history: docs/PROJECT_OVERVIEW.md Section 4

**Latest simulation results (2016--2025)** -- auto-processed:
- Net margin: £6,239,245.03 | Gross: £6,475,913.39 | Capital: £236,668
- Treasury: £2,466,636 -> £3,709,973 | 38 committee interventions | 1531 bills issued
- Enterprise value: £6,037,509.08 | Net after CTS: £6,370,846
- Retention: 18 offers, 17/18 retained | 5 no-offer churns | 6 total churned accounts
