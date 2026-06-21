# Project Status

Last updated: 2026-06-21T12:00:00Z
Current phase: **Phase 12d COMPLETE** (2026-06-21). Margin-aware retention guard. 637 tests passing.

## Current state

**Build summary (Phase 12d, 21 June 2026):**
Phase 12d added a margin-aware guard to the retention offer engine: offers are only made when
`expected_margin > retention_cost` (gross margin rate > 5% discount). Crisis-year offers (2021–22)
are automatically blocked when commodity margins collapse below the discount floor.

Full 2016–2025 simulation results (Phase 12d run, 1870s):
- Ledger net margin: £-8,317.21 | Gross margin: £-7,089.58 | Capital: £1,228
- Treasury: £29,846 → £11,131 | Enterprise value: £-20,661.90 | Net after CTS: £-23,569
- Retention: 2 offers (down from 21 in Phase 12c), 100% retained, Net ROI **+£2.85** (was £-1,263)
- Crisis years 2021–22: 0 offers — guard blocked 3 uneconomical; 3 below 30% threshold
- Risk committee: 323 interventions | Bills issued: 1,117 | Churned customers: 6

**Five hollow gaps status:**
1. Customer events — DEEPENED (Phase 12b–12d): dated churn/acquisition/retention artefacts; retention decision affects SIM outcome; ROI now positive
2. Ledger — CLOSED (Phase 7a/7b): 2.2M ledger events; P&L from transaction sum
3. SIM/company barrier — DEEPENED (Phase 11a+11b+12b): company pricing + churn estimation from observable data only; basis risk visible
4. HH data path — CLOSED (Phase 6a): C7-C9 on real HH consumption
5. Reporting — CLOSED (Phase 5a/5b): ANNUAL_REPORT.md, full pipeline, GitHub Pages

637 tests passing (SIM_FAST_MODE=1 suite, 16s).

Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
Status: https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md
