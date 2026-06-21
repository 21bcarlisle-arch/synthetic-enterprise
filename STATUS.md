# Project Status

Last updated: 2026-06-21T12:28:17Z
Current phase: **Phase 12e COMPLETE** (2026-06-21). 649 tests passing.

## Current state

**Phase 12e (2026-06-21): SIM/company divergence tracking**
- `simulation/run_phase2b.py`: `_compute_company_divergence()` aggregates basis risk by year; `company_divergence` key in run output (tariff + churn error by year)
- `saas/reporting/annual_report.py`: "Company Model Divergence" section renders year-by-year mean/max abs error tables
- Hollow gap #3 (SIM/company barrier): divergence from SIM ground truth formally measured
- 7 new tests (649 total, 17s)

**Session 2026-06-21 quick wins (between Phase 12d and 12e):**
- Run-complete mechanization: `background/process_run_complete.py` auto-handles run_complete_*.md markers
- Fix: session-scoped `SIM_FAST_MODE=1` in conftest.py — tests now run in 16s by default
- Fix: basis_risk_terms extraction bug in annual_report.py JSON extraction
- LiveSimInterface observability audit docstring (every value classified OBSERVABLE/STUB/SIM INTERNAL)
- 5 new tests, 0 lint errors

**Build summary (Phase 12d, 21 June 2026):**
Phase 12d added a margin-aware guard to the retention offer engine. Full 2016-2025 sim results:
- Ledger net margin: £-8,317.21 | Gross: £-7,089.58 | Capital: £1,228
- Treasury: £29,846 -> £11,131 | Enterprise value: £-20,661.90 | Net after CTS: £-23,569
- Retention: 2 offers (down from 21), 100% retained, Net ROI +£2.85

**Five hollow gaps status:**
1. Customer events — DEEPENED (Phase 12b-12d): dated churn/acquisition/retention artefacts; retention decision affects SIM outcome; ROI now positive
2. Ledger — CLOSED (Phase 7a/7b): 2.2M ledger events; P&L from transaction sum
3. SIM/company barrier — DIVERGENCE MEASURED (Phase 12e): company divergence from SIM ground truth tracked by year; tariff + churn error in run output and annual report
4. HH data path — CLOSED (Phase 6a): C7-C9 on real HH consumption
5. Reporting — CLOSED (Phase 5a/5b): ANNUAL_REPORT.md, full pipeline, GitHub Pages

649 tests passing (SIM_FAST_MODE=1 suite, 17s).

Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
Status: https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md
