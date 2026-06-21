# Project Status

Last updated: 2026-06-21T12:05:46Z
Current phase: **Phase 12d COMPLETE + quick wins** (2026-06-21). 637 tests passing (now runs in 16s by default).

## Current state

**Session 2026-06-21 quick wins (between Phase 12d and 12e):**
- Run-complete mechanization: `background/process_run_complete.py` auto-handles run_complete_*.md markers — regenerates report, updates LATEST.md, runs fast tests, commits+pushes. Saves ~1 frontier turn per sim run.
- Fix: removed duplicate `notify_retention_attempt` from `StubSimInterface` (Phase 12b copy-paste artifact)
- LiveSimInterface observability audit docstring (Phase 12e prep): every value classified as OBSERVABLE, STUB, or SIM INTERNAL (audit-only)
- Fix: session-scoped `SIM_FAST_MODE=1` in conftest.py — tests now run in 16s by default without CLI env var; module-scoped simulation fixtures no longer block on Ollama
- Retention threshold analysis: 30% threshold is correctly set; the 3 "below_threshold" churns had 0% company estimates (price decrease → model predicts stable, SIM has hidden factors). Root cause is company model divergence, not threshold level.
- Phase 12e proposed (SIM/company divergence tracking — hollow gap 3)

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

642 tests passing (SIM_FAST_MODE=1 suite, 16s).

Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
Status: https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md
