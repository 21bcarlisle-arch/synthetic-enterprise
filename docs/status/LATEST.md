# Simulation Status -- LATEST

Last updated: 2026-06-30T02:27:17Z

## Current state

- **Phase:** AJ complete (CRM Risk Triage) -- all phases P through AJ shipped
- **Tests passing:** 5,280 (all green)
- **Python modules:** 330+
- **Company modules:** 232+
- **Net position (latest sim run):** £1,243,337

## Latest run figures (git 5e2a5dc, 2026-06-30)

| Metric | Value |
|--------|-------|
| Total Revenue | £14,137,721 |
| Gross Margin | £6,462,146 |
| Net Margin | £1,243,337 |
| Enterprise Value | £6,142,209 |
| Administration Event | None |

## Recent build phases (AH→AJ)

- **Phase AJ:** CRM Risk Triage (14 tests). _section_crm_intelligence() in annual_report.py:
  churn_basis_risk latest-renewal-per-customer classified CRITICAL/HIGH/MEDIUM/LOW bands;
  rate-vs-SVT flag; lifetime margin at risk (CRITICAL+HIGH); company blind-spot count
  (HIGH sim risk + <10% company estimate). Connects Phases AD, AC, 11b.
- **Phase AI:** EAC Drift Snapshot (10 tests). _section_eac_drift_snapshot():
  per-customer demand drift from billing EAC estimates. Classifies significant/moderate/stable.
- **Phase AH:** Board Intelligence Pack (12 tests). _section_portfolio_intelligence_pack():
  retention coverage, flex enrollment CAGR, churn peak year, board recommendations.

-> Full build history: docs/PROJECT_OVERVIEW.md Section 4

**Latest simulation results (2016–2025)** — auto-processed (720s / 12 min):
- Net margin: £6,239,245.03 | Gross: £6,475,913.39 | Capital: £236,668
- Treasury: £2,466,636 → £3,709,973 | 38 committee interventions | 1531 bills issued
- Enterprise value: £6,037,509.08 | Net after CTS: £6,370,846
- Retention: 18 offers, 17/18 retained | 5 no-offer churns | 6 total churned accounts
