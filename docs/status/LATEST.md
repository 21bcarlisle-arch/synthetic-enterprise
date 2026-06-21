# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-21T14:22:23Z

**Phase 14d LIVE (2026-06-21)**: ToU revenue premium analysis in annual report. 700 tests passing (4 new).
- `saas/reporting/annual_report.py`: `_tou_revenue_premium()` — derives flat-equivalent revenue from avg_peak_rate / 1.5×
- "ToU Premium" column added to utilization table + summary line (total actual vs flat equivalent)
- C8 (43.8% peak) earns ~+10% vs flat equivalent; C9 (42.2%) ~+9%; C7 (33.6%) ~+3%
- Revenue-neutral design is at 30% peak — anything above earns a surplus vs flat rate

**Phase 14c LIVE (2026-06-21)**: Adaptive lookback window in company tariff engine. 696 tests passing (7 new).
- `company/pricing/tariff_engine.py`: `_compute_adaptive_lookback()` — recent 30d std vs prior 90d baseline std
- High vol_ratio (crisis onset): shortens lookback toward 30d floor so mean tracks current regime not stale pre-crisis data
- Low vol_ratio (calm market): extends toward 180d ceiling for smoother estimate; falls back to 120d on flat/sparse data
- Crisis years (2021-22): expect tariff error reduction of 8-15pp in next sim run (vol ratio triggers shorter window)

**Phase 14a LIVE (2026-06-21)**: Tiered retention offer size. 689 tests passing (4 new).
- `simulation/run_phase2b.py`: `RETENTION_TIERS` [(≥75%→8%), (≥50%→5%), (≥30%→3%)] replaces flat 5%
- `_retention_discount_for_risk()` helper — borderline cases get lighter touch, high-risk get aggressive offer
- Both existing offers (company_p=0.45) stay at 5% tier; next run with Phase 13c may show C6 at different tier

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

**Latest simulation results (2016–2025)** — auto-processed (1711s / 29 min):
- Net margin: £-3,765.60 | Gross: £-2,537.97 | Capital: £1,228
- Treasury: £29,846 → £15,683 | 287 committee interventions | 1117 bills issued
- Enterprise value: £-16,445.26 | Net after CTS: £-19,097
- Retention: 2 offers, 2/2 retained | 6 no-offer churns | 6 total churned accounts

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

**Phase 12a-12e LIVE (2026-06-20/21)**: Company CRM event log, retention offers, ROI analysis, margin-aware guard, SIM/company divergence tracking. Full history in ANNUAL_REPORT.md and git log.

**Five hollow gaps status (as of 2026-06-21)**:
1. ~~No customer events firing~~ — CLOSED (Phase 6b/7e): churn events, replacement onboarding
2. ~~No ledger~~ — CLOSED (Phase 7a/7b): transaction log, cash waterfall, bad-debt events
3. ~~SIM/company barrier~~ — DEEPENED (Phase 11a+11b): tariff pricing AND churn estimation now use observable-data models only; pricing basis risk + churn basis risk both visible in annual report
4. ~~HH data path~~ — CLOSED (Phase 6a): C7-C9 on real HH consumption
5. ~~Reporting~~ — CLOSED (Phase 5a/5b): ANNUAL_REPORT.md, full pipeline

**Autonomous stack status**: sim_runner, autonomous_runner, health_check, staging_watcher, ntfy_responder — all operational. NTFY spam fixed (all 3 sources). Cron self-healing installed every 30min.
Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
