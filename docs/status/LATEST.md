# Simulation Status -- LATEST

Last updated: 2026-06-30T08:55:16Z

## Current state

- **Phase:** FK complete -- 6,646 tests. Session (FA-FK): VCR, Ombudsman, Billing Disputes, Carbon Intensity, Onboarding Journey, Gas Market Monitor, Triad Exposure, ROC Ledger, BSC Credit, CfD Levy, Customer Profitability Scorecard. Earlier: EX-EZ + FA (6,500 milestone). 354 company/ modules. All green.
- **Tests passing:** 6,646 (all green)
- **Python modules:** 354 company/ modules + simulation + saas
- **Net position (latest sim run):** £1,243,337 (git 5d0e280)

## Latest run figures (git 5d0e280 + ongoing builds)

| Metric | Value |
|--------|-------|
| Total Revenue | £14,135,305 |
| Gross Margin | £6,462,146 |
| Net Margin | £1,243,337 |
| Enterprise Value | £6,037,509 |
| Final Treasury | £3,709,973 |
| Administration Event | None |

## Build summary (2026-06-30, this session FA-FK)

- FA: Vulnerable Customer Register (17 tests) -- Consumer Duty 2023, PPM ban, 6 vuln types
- FB: Ombudsman Register (15 tests) -- SLC 18.9, 6m referral window, binding decisions
- FC: Billing Dispute Resolution Book (17 tests) -- SLC 23, no disconnect while open
- FD: Carbon Intensity Register (13 tests) -- FMD, REGO, 53% decarbonisation 2016-25
- FE: Customer Onboarding Journey Tracker (15 tests) -- SLC 14.2/22.1/7.5
- FF: Wholesale Gas Market Monitor (13 tests) -- NBP pricing, WAPP, crisis detection
- FG: Triad Exposure Register (12 tests) -- TNUoS, 3 peak HH Nov-Feb, I&C management
- FH: ROC Ledger (13 tests) -- Renewables Obligation, buy-out prices 2016-25
- FI: BSC Credit Assurance Register (13 tests) -- CDN, 5WD cure, suspension risk
- FJ: CfD Levy Register (14 tests) -- LCCC quarterly levy, credit when market>strike
- FK: Customer Profitability Scorecard (14 tests) -- 4-component score, PLATINUM/GOLD/SILVER

## CTO Architecture Guidance

Rich staged CTO_architecture_guidance.md. This is the long-term vision document.
Key directive: Horizon 1 (compliance core, epistemic air gap, event ledger) must be
bulletproof before Horizon 2 (behavioral depth, 3-horizon CLV). Currently at high velocity.

## Links

- [Annual Report](../reports/ANNUAL_REPORT.md)
- [Phase History](../claude/phase-history.md)
- [Project Overview](../PROJECT_OVERVIEW.md)

**Latest simulation results (2016-2025)** -- auto-processed:
- Net margin: £6,239,245.03 | Gross: £6,475,913.39 | Capital: £236,668
- Treasury: £2,466,636 -> £3,709,973 | 38 committee interventions | 1531 bills issued
- Enterprise value: £6,037,509.08 | Net after CTS: £6,370,846
