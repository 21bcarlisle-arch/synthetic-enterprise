# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-21T13:30:00Z

**Phase 13e LIVE (2026-06-21)**: Gas seasonal adjustment in company tariff engine. 685 tests passing (2 net new).
- `company/pricing/tariff_engine.py`: `GAS_WINTER_SEASONAL_UPLIFT=0.15`, `GAS_SUMMER_SEASONAL_DISCOUNT=0.08`
- Gas pricing now fuel-aware in seasonal logic: winter +15%, summer -8% (electricity: +8%/-4%)
- UK NBP heating-demand seasonality is more pronounced than electricity — this is standard in real supplier pricing
- `test_seasonal_does_not_apply_to_gas` replaced with 3 quantified gas seasonal tests

**Phase 13d LIVE (2026-06-21)**: Seasonal forward price awareness in company tariff engine. 683 tests passing (9 new).
- `company/pricing/tariff_engine.py`: `seasonal: bool = True` param + winter/summer adjustment for electricity
- Winter delivery (Oct-Mar): +8% uplift; summer delivery (Apr-Sep): -4% discount.
- Fixes structural basis risk: 120-day lookback for Oct-renewal captured summer prices, underestimating winter costs
- Effect in next sim run: company forward estimates better-calibrated for autumn/winter contracts

**Phase 13c LIVE (2026-06-21)**: Bill burden signal in company churn model. 674 tests passing (8 new).
- `company/crm/churn_model.py`: `annual_consumption_kwh` param + `BILL_STRESS_SENSITIVITY=0.25`, `BILL_STRESS_THRESHOLD_GBP=£3,000`
- Bill stress term = 0.25 × max(0, prev_annual_bill/£3,000 − 1); activates for high-spend SME customers
- C6 2024 failure mode fixed: falling rate (−40%) + 45,000 kWh/year at £250/MWh → company now estimates 42% churn (was 0%)
- Rate-only model had 3 "below threshold" misses all at company_p=0.0; bill burden makes the large-SME case detectable
- Small resi (2,800 kWh at £60/MWh → £168 bill) unaffected — signal only fires above £3,000 annual bill

**Phase 13b LIVE (2026-06-21)**: ToU utilization section in annual report. 666 tests passing.
- `saas/reporting/annual_report.py`: `_section_tou_utilization()` — per-customer (C7/C8/C9) peak/off-peak kWh split, revenue contribution, avg rates; populates from next full sim run
- Report now shows C7-C9 peak utilization % and revenue breakdown after each sim run

**Phase 13a LIVE (2026-06-21)**: 666 tests passing. ToU tariffs for C7-C9 HH smart meter customers.
- `simulation/tou_periods.py`: is_peak_period() — morning (07:00-11:00) + evening (16:00-20:00) weekday peaks (SP 15-22, 33-40)
- `saas/tariff_pricing.py`: price_tou_tariff() — peak rate 1.5× flat, off-peak 0.786× flat, revenue-neutral at 30/70 split
- `simulation/hedged_settlement.py`: per-period unit_rate now reflects actual ToU tier; flat rate retained for churn/retention calculations
- `simulation/run_phase2b.py`: is_hh_customer() check wires ToU rates for C7-C9
- Next sim run (currently in progress): ToU stats will appear in report

**Latest simulation results (2016–2025)** — run at 70646db (Phase 12d guard active):
- Net margin: £-8,317 | Gross: £-7,090 | Capital: £1,228
- Treasury: £29,846 → £11,131 | 323 committee interventions | 1117 bills issued
- Enterprise value: £-20,662 | Net after CTS: £-14,399
- Retention ROI: +£2.85 (2 offers made, both retained; 3 blocked — uneconomical by Phase 12d guard)
- 6 total churned accounts | 6 no-offer churns (3 below threshold, 3 uneconomical)

**Phase 12e LIVE (2026-06-21)**: SIM/company divergence tracking. 649 tests passing (7 new).
- `simulation/run_phase2b.py`: `company_divergence` key in run output — year-by-year mean/max abs error for tariff pricing and churn estimation
- `saas/reporting/annual_report.py`: "Company Model Divergence" section with year-by-year error tables for both models
- Hollow gap #3 (SIM/company barrier): divergence from SIM ground truth now formally measured, not assumed
- Next full sim run will populate tariff error by year + churn estimate error by year

**Run-complete mechanization LIVE (2026-06-21)**: sim results auto-processed after each background run.
- `background/process_run_complete.py`: regenerates ANNUAL_REPORT.md, updates LATEST.md key figures, runs fast tests, commits + pushes
- Saves ~1 frontier turn per sim run; falls back to Claude processing if anything fails
- Only NTFYs Rich for administration events; routine runs fully silent

**Token proxy LIVE (2026-06-21)**: localhost:8801 intercepts all Anthropic API calls, tracks per-session usage.
- Handles gzip-compressed responses (decompresses before parsing SSE/JSON)
- Logs to docs/observability/token-usage-log.jsonl (one JSONL line per call)
- autonomous_runner.py sets ANTHROPIC_BASE_URL=http://localhost:8801 so all autonomous turns tracked
- Query: `python3 -m background.token_proxy --query` | Pricing: Sonnet 4.6 input $3/MTok, output $15/MTok

**Model evaluation COMPLETE (2026-06-21)**: gemma4:12b vs qwen3:14b — **keep qwen3:14b everywhere**.
- Accuracy: identical (dispatcher 10/10, discovery 5/5, risk committee valid — both models)
- Speed: qwen3:14b 4x faster (4.5s vs 20.9s/call dispatcher; 11s vs 34.6s risk committee)
- gemma4:12b would triple the SIM runtime (~3hrs vs 38min). Not worth switching.

**SIM bottleneck (2026-06-21)**: 95% of the 38-min runtime is 323 risk committee Ollama calls (~7s each).
- Pure Python (billing/settlement/hedging): ~40s
- SIM_FAST_MODE=1 (deterministic +0.10, no Ollama): ~2 min for full sim, 16s for full test suite
- Keep LLM mode for production runs (it's the agentic part); use SIM_FAST_MODE=1 for tests

**Phase 13a LIVE (2026-06-21)**: 666 tests passing. ToU tariffs for C7-C9 HH smart meter customers.
- `simulation/tou_periods.py`: is_peak_period() — morning (07:00-11:00) + evening (16:00-20:00) weekday peaks
- `saas/tariff_pricing.py`: price_tou_tariff() — peak rate 1.5× flat, off-peak 0.786× flat, revenue-neutral at 30/70 split
- `simulation/hedged_settlement.py`: per-period unit_rate now reflects actual ToU tier; flat rate retained for churn/retention calculations
- Effect in next run: C7-C9 settlement records show real peak/off-peak rate split; revenue impact from actual HH load profile

**Phase 12d LIVE (2026-06-21)**: 637 tests passing. Margin-aware retention guard.
- Guard: only make retention offer when `expected_margin > retention_cost` (gross margin rate > 5% discount)
- Crisis years (2021-22): forward prices spike, margins collapse below 5% → offers blocked automatically
- `no_offer_churn_log` entries carry `no_offer_reason`: "below_threshold" or "uneconomical"
- Annual report shows missed-opportunity breakdown by reason
- Effect visible in next full sim run: crisis-year offers gone, ROI expected positive in normal years

**Phase 12c LIVE (2026-06-21)**: 634 tests passing. Retention ROI analysis — no-offer churn tracking + expected margin in each offer.
- `no_offer_churn_log` tracks missed opportunities (company estimate <30%, no offer made, customer churned)
- `expected_term_margin_gbp` added to all retention_log entries
- Annual report: ROI = margin_saved − total_offer_cost visible; 21 offers, net ROI £-1,263.14 (19 retained, 2 churned despite)
- 17 new tests (634 total)


**Phase 12b LIVE (2026-06-21)**: 617 tests passing. Company retention offers — first company decision affecting SIM outcome.
- `company/crm/event_log.py`: `RetentionEvent` dataclass + `record_retention()` + `retention_events()` — dated retention artefacts
- `company/interfaces/sim_interface.py`: `notify_retention_attempt()` on all SimInterface classes — StubSimInterface stores notifications
- `simulation/customer_events.py`: `roll_lifecycle_event()` accepts `retention_modifier` param — reduces churn probability by 20% when offer is made
- `simulation/run_phase2b.py`: pre-roll retention check: if company estimate > 30%, offer made before SIM rolls churn dice; outcome recorded
- `saas/ledger.py`: `make_retention_cost_event()` — foregone margin recorded as cash-out event
- `saas/reporting/annual_report.py`: "Retention Strategy P&L" section (offers/retained/churned-despite/cost table)
- Hollow gap 1 (customer events): **DEEPER** — company now acts on its churn estimate before SIM rolls; retention outcome is first company decision affecting simulation outcome
- 20 new tests (617 total)

**Phase 12a LIVE (2026-06-20)**: 597 tests passing. Company CRM event log — customers actually leave as dated artefacts.
- `company/crm/event_log.py`: `CompanyEventLog` with `ChurnEvent` / `AcquisitionEvent` dataclasses
  - Append-only, dated artefacts — churn is no longer just a flag in a set
  - `active_accounts(as_of_date)`: replays event history to determine CRM view at any point in time
- `company/interfaces/sim_interface.py`: `LiveSimInterface.notify_churn` / `notify_acquisition` now record to event log
- `simulation/run_phase2b.py`: emits `notify_churn` on every churn roll, `notify_acquisition` on home-move wins and fresh acquisitions; returns `company_event_log` in output
- `saas/reporting/annual_report.py`: "Company CRM — Event Log" section: dated event table + year-end SIM vs CRM reconciliation
- Hollow gap 1 (customer events): **DEEPER** — company now has a CRM event log with dated churn/acquisition artefacts; reconciliation table shows CRM vs SIM ground truth match
- 20 new tests (597 total passing)

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

**Five hollow gaps status (as of 2026-06-21)**:
1. ~~No customer events firing~~ — CLOSED (Phase 6b/7e): churn events, replacement onboarding
2. ~~No ledger~~ — CLOSED (Phase 7a/7b): transaction log, cash waterfall, bad-debt events
3. ~~SIM/company barrier~~ — DEEPENED (Phase 11a+11b): tariff pricing AND churn estimation now use observable-data models only; pricing basis risk + churn basis risk both visible in annual report
4. ~~HH data path~~ — CLOSED (Phase 6a): C7-C9 on real HH consumption
5. ~~Reporting~~ — CLOSED (Phase 5a/5b): ANNUAL_REPORT.md, full pipeline

**Autonomous stack status**: sim_runner, autonomous_runner, health_check, staging_watcher, ntfy_responder — all operational. NTFY spam fixed (all 3 sources). Cron self-healing installed every 30min.
Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
