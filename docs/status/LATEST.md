# Simulation Status -- LATEST

Last updated: 2026-06-30T03:01:41Z

## Current state

- **Phase:** AQ complete (Board Risk Summary) -- phases P through AQ shipped
- **Tests passing:** 5,366 (all green)
- **Python modules:** 330+
- **Company modules:** 232+
- **Net position (latest sim run):** 1,243,337

## Latest run figures (git 5e2a5dc, 2026-06-30)

| Metric | Value |
|--------|-------|
| Total Revenue | 14,137,721 |
| Gross Margin | 6,462,146 |
| Net Margin | 1,243,337 |
| Enterprise Value | 6,142,209 |
| Administration Event | None |

## Session (AH--AQ): 11 phases, 132 tests added

Board intelligence synthesis: all annual report sections now synthesised in _section_board_risk_summary():
- **AQ:** Board Risk Summary (6 RAG indicators: 4 RED, 1 AMBER, 1 GREEN)
- **AP:** Segment Capital Efficiency (gas ROC=-0.7x CAPITAL DESTROYER)
- **AO:** Demand Estimation Error Trend (0.07% to 3.3%/15.6% by 2024)
- **AN:** Portfolio Concentration (HHI=2249 MODERATE, I&C=98.7%)
- **AM:** Pricing Basis Risk (company_fwd vs sim_fwd; 2025 +32.8%)
- **AL:** Counterfactual Retention (3,621 net recoverable from 4 missed)
- **AK:** Churn Root Cause Attribution (6 churns, 4 blind misses, 39,706 lost)
- **AJ:** CRM Risk Triage (CRITICAL/HIGH/MEDIUM/LOW bands + blind spots)
- **AI:** EAC Drift Snapshot (per-customer demand drift from billing)
- **AH:** Board Intelligence Pack (retention/flex/churn synthesis + recs)
- **Board finding:** Gas is a capital destroyer; electricity cross-subsidises; I&C concentration at existential risk level; churn blind miss rate 67%.

-> Full build history: docs/PROJECT_OVERVIEW.md Section 4

**Latest simulation results (2016–2025)** — auto-processed (454s / 8 min):
- Net margin: £6,239,245.03 | Gross: £6,475,913.39 | Capital: £236,668
- Treasury: £2,466,636 → £3,709,973 | 38 committee interventions | 1531 bills issued
- Enterprise value: £6,037,509.08 | Net after CTS: £6,370,846
- Retention: 18 offers, 17/18 retained | 5 no-offer churns | 6 total churned accounts
