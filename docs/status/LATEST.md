# Simulation Status — LATEST

Last updated: 2026-06-30T02:06:56Z

## Current state

- **Phase:** AH complete (Board Intelligence Pack) -- all phases P→AH shipped
- **Tests passing:** 5,256 (all green)
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

## Recent build phases (AG→AH)

- **Phase AH:** Board Intelligence Pack (12 tests). _section_portfolio_intelligence_pack() in annual_report.py:
  retention coverage rate/acceptance rate, flexibility enrollment CAGR, churn peak year,
  net book movement, 4 board recommendations. Uses retention_log/no_offer_churn_log/company_event_log.
- **Phase AG:** Flexibility Revenue Annual Report Section (12 tests). _section_flexibility_revenue() renders
  CM vs DFS revenue table; pre-DFS years labelled; enrolled customer-years count; DFS launch note.
- **Phase AF:** DSR/Flexibility Revenue Integration (15 tests). FlexibilityRevenueBook computes
  CM (2016+) and DFS (2022+) revenue from dynamic_assets; wired into run_phase2b and annual_report.
- **Phase AE:** Customer Retention Offer Book (21 tests). CustomerRetentionBook generates tailored offers
  by driver: EV+RATE_SHOCK→TOU_REFERRAL; RATE_SHOCK→PRICE_MATCH 8%; BILL_STRESS→ACCOUNT_REVIEW.
- **Phase AD:** Portfolio Churn Risk Book (34 tests). PortfolioChurnRiskBook: CRITICAL/HIGH/MEDIUM/LOW
  bands; RATE_SHOCK/BILL_STRESS/TENURE_SHORT/BASELINE drivers; revenue-at-risk.
- **Phase AC:** Portfolio Repricing Action Book (24 tests). RepricingPriority CRITICAL→MONITOR; EAC-based
  recommended tariff; 70% retention; margin recovery estimates.

→ Full build history: docs/PROJECT_OVERVIEW.md Section 4
