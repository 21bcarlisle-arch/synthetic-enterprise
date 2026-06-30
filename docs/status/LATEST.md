# Simulation Status -- LATEST

Last updated: 2026-06-30T09:02:22Z

## Current state

- **Phase:** FO complete -- 6,702 tests. **6,700 milestone crossed.** Session (FK-FO): Customer Profitability Scorecard, Porting Loss Register, Power Auction Monitor, Customer Lifetime Revenue, Debt Age Analysis. 358 company/ modules. All green.
- **Tests passing:** 6,702 (all green, verified)
- **Python modules:** 358 company/ modules + simulation + saas
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

## Build summary (2026-06-30, this session FK-FO)

- FK: Customer Profitability Scorecard (14 tests) -- 4-component 0-100 score, PLATINUM tier
- FL: Porting Loss Register (14 tests) -- switch reasons, winback eligibility gates
- FM: Wholesale Power Auction Monitor (16 tests) -- N2EX DA, crisis/negative price detection
- FN: Customer Lifetime Revenue Register (13 tests) -- backward-looking actuals vs CLV
- FO: Debt Age Analysis Register (13 tests) -- IFRS 9 ECL, 5 age buckets, 6,700 crossed

## CTO Architecture Guidance

Rich staged CTO_architecture_guidance.md. This is the long-term vision document.
Key directive: Horizon 1 (compliance core, epistemic air gap, event ledger) must be
bulletproof before Horizon 2 (behavioral depth, 3-horizon CLV). 6,700 tests confirms foundation.

## Links

- [Annual Report](../reports/ANNUAL_REPORT.md)
- [Phase History](../claude/phase-history.md)
- [Project Overview](../PROJECT_OVERVIEW.md)

**Latest simulation results (2016-2025)** -- auto-processed:
- Net margin: £6,239,245.03 | Gross: £6,475,913.39 | Capital: £236,668
- Treasury: £2,466,636 -> £3,709,973 | 38 committee interventions | 1531 bills issued
- Enterprise value: £6,037,509.08 | Net after CTS: £6,370,846
