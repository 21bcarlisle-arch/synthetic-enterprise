# Project Status

Last updated: 2026-06-22T00:44:00Z
Current phase: **Phase 23a COMPLETE** (2026-06-22). 838 tests passing.

## Current state

**Phase 23a (2026-06-22): Company-owned demand estimation**
- `simulation/run_phase2b.py`: `_company_eac_estimate()` sums prior-year billing records for EAC estimate; falls back to SIM oracle only on first term
- Three `EFFECTIVE_EAC_KWH` oracle lookups replaced in company decisions: churn signal, retention economics, missed-opportunity analysis
- `demand_estimation_log` in run output: per-renewal company vs oracle EAC comparison (error_pct, source)
- `saas/reporting/annual_report.py`: Demand Estimation Accuracy section (year-by-year mean/max abs error)
- 12 new tests (838 total)

**Latest simulation results (2016-2025)** - auto-processed:
- Gross margin: £18,605 | Net margin: £-3,795 | Capital: £2,348
- Treasury: £29,846 → £26,051 | 214 committee interventions | 1117 bills issued
- Enterprise value: £9,889 | Net after CTS: £-10,476
- Retention: 19 offers, 16/19 retained | 3 churned despite | 3 no-offer churns

**Five hollow gaps status:**
1. Customer events - DEEPENED (Phases 12b-16b, 17b, 23a): dated CRM artefacts; retention with tiered offers; acquisition-aware guard; ROI, durability, repricing analysis; company demand estimation closed epistemic honesty violation
2. Ledger - CLOSED (Phase 7a/7b): 2.2M ledger events; P&L from transaction sum
3. SIM/company barrier - DIVERGENCE MEASURED + DEMAND FIXED (Phases 12e, 23a): company-owned EAC estimation from billing records; tariff + churn + demand error tracked by year in run output and annual report
4. HH data path - CLOSED (Phase 6a): C7-C9 on real HH consumption; ToU tariffs live (Phase 13a)
5. Reporting - CLOSED (Phase 5a/5b): ANNUAL_REPORT.md, full pipeline, GitHub Pages

838 tests passing (SIM_FAST_MODE=1 suite, ~16s).

Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
Status: https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md
