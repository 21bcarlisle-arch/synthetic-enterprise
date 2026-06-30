# Simulation Status -- LATEST

Last updated: 2026-06-30T02:30:42Z

## Current state

- **Phase:** AK complete (Churn Root Cause Attribution) -- phases P through AK shipped
- **Tests passing:** 5,294 (all green)
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

## Recent build phases (AH--AK)

- **Phase AK:** Churn Root Cause Attribution (14 tests). _section_churn_root_cause():
  cross-references customer_events/dynamic_pricing_log/churn_basis_risk/per_customer_lifetime.
  6 churns: £39,706 lifetime margin lost; 3 blind misses (C3/C1/C4, sim 32%, company 0%).
- **Phase AJ:** CRM Risk Triage (14 tests). _section_crm_intelligence(): CRITICAL/HIGH/MEDIUM/LOW
  churn bands, rate-vs-SVT, company blind spot count.
- **Phase AI:** EAC Drift Snapshot (10 tests). Per-customer demand drift from billing history.
- **Phase AH:** Board Intelligence Pack (12 tests). Retention/flex/churn board synthesis.

-> Full build history: docs/PROJECT_OVERVIEW.md Section 4
