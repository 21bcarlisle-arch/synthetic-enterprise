# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-20T19:18:34Z

**Phase 11b LIVE (2026-06-20)**: 577 tests passing. Company churn model implemented.
- `company/crm/churn_model.py`: `estimate_churn_probability()` — observable-data churn estimator
  - Inputs: rate change %, customer tenure (observable). No SIM bill-shock parameters.
  - Formula: base_rate(10%) + rate_sensitivity(0.8) × rate_increase_pct − tenure_discount × min(tenure, 5yr)
  - Systematically under-estimates churn when prices spike (company sees % change, not household bill shock)
- `company/interfaces/sim_interface.py`: `get_churn_estimate()` on all SimInterface classes
- `simulation/customer_events.py`: lifecycle events now carry `company_churn_estimate` + `churn_estimate_error_pct`
- `simulation/run_phase2b.py`: `churn_basis_risk` in output — per-renewal company vs SIM error
- `saas/reporting/annual_report.py`: "Churn Prediction Basis Risk" section with year-by-year error table
- Hollow gap 3 (SIM/company barrier): now **DEEPER** — two consequential decisions (tariff + churn) use observable-only data
- 21 new tests (577 total passing)

**Phase 11a LIVE (2026-06-20)**: 559 tests passing. Company pricing autonomy implemented.
- `company/pricing/tariff_engine.py`: `CompanyTariffEngine` — observable-data forward price model
  - 120-day rolling mean of daily spot prices + 15% risk premium
  - No seasonal adjustment (company hasn't built that model yet)
  - Systematically differs from SIM's model — difference is basis risk, now visible in P&L
- `company/interfaces/sim_interface.py`: `LiveSimInterface` implemented — `build_sim_interface(live=True)` now works
- `simulation/renewals.py` / `run_phase2b.py`: unit rates now derived from company's estimate, not SIM internals
  - `forward_price_gbp_per_mwh` = SIM's sophisticated estimate (used for hedging, risk)
  - `company_forward_price_gbp_per_mwh` = company's observable estimate (drives tariff)
  - `basis_risk_terms` now returned from `main()` — per-term company vs sim error %
- Hollow gap 3 (SIM/company barrier structural not functional): now **CLOSED** — company makes consequential tariff decisions using only observable information
- 16 new tests: `tests/company/pricing/` (tariff engine + LiveSimInterface)

**Phase 10b (2026-06-20)**: Segment portfolio report committed.
- `saas/reporting/segment_report.py`: standalone segment P&L report generator
  - Per-segment unit economics: headcount trajectory, net/customer, smart-meter migration
  - `make segment-report` regenerates from saved JSON; `make run-segments` runs full simulation
- 26 new tests covering extract_segment_data(), generate_segment_report(), table helpers
- Full 2016-2025 segment simulation still in progress (background, at 2017-09, treasury £531k)

**Phase 10a (2026-06-20)**: Segment customer model live.
- `simulation/segments.py`: 5 customer segments (resi_standard 150 customers, resi_smart 20, sme_standard 40, sme_smart 5, gas_resi 80)
- `simulation/run_segments.py`: simulation loop with annual headcount evolution (churn, smart upgrades, acquisition)
- Non→Smart flow: UK smart meter rollout modelled — Standard customers upgrade to Smart at 3-10%/yr
- Speed: O(segments×periods) same as before, economically credible at realistic headcounts

**Latest simulation results (2016–2025)** — run git 0e49860 (Phase 11a+11b: company pricing + churn basis risk):
- Net margin: £-8,317.21 | Gross: £-7,089.58 | Capital: £1,228 (ledger-based, includes standing charges)
- Treasury: £29,846 → £11,131 | 323 committee interventions | 1117 bills issued
- Enterprise value: £-20,661.90 | Net after CTS: £-14,399 | Bad debt: £2,821
- 2021 (crisis): net margin £-3,069.53 | 2022 (crisis): net margin £-5,582.79 (worst year)
- 6 churned customers (C3/C1/C5/C2/C6/C4), 1 home-move win (C2→1 successor)
- *Phase 11a basis risk: company’s 120-day-rolling+15% tariff underprices SIM forward curve — commodity-only gross £-17,487*

**Five hollow gaps status (as of 2026-06-20)**:
1. ~~No customer events firing~~ — CLOSED (Phase 6b/7e): churn events, replacement onboarding
2. ~~No ledger~~ — CLOSED (Phase 7a/7b): transaction log, cash waterfall, bad-debt events
3. ~~SIM/company barrier~~ — DEEPENED (Phase 11a+11b): tariff pricing AND churn estimation now use observable-data models only; pricing basis risk + churn basis risk both visible in annual report
4. ~~HH data path~~ — CLOSED (Phase 6a): C7-C9 on real HH consumption
5. ~~Reporting~~ — CLOSED (Phase 5a/5b): ANNUAL_REPORT.md, full pipeline

**Autonomous stack status**: sim_runner, autonomous_runner, health_check, staging_watcher, ntfy_responder — all operational. NTFY spam fixed (all 3 sources). Cron self-healing installed every 30min.
Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
