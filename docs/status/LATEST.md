# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-21T16:17:01Z

**Phase 19a LIVE (2026-06-21)**: Extend margin feedback (16c) and portfolio premium (17a) to gas. 775 tests passing (5 new).
- `simulation/run_phase2b.py`: gas CIDs (C1g, C2g, etc.) now get per-customer surcharge + portfolio premium at renewal
- Separate `portfolio_gas_margin_rates` tracking; `"commodity"` field added to both log dicts
- Backward-compatible: pre-19a log entries without commodity default to electricity
- Expected: 2023 gas losses (resi gas -£1,014 in last run) should improve as gas portfolio premium fires

**Phase 17c/17d/16c/17a/14b report fix (2026-06-21)**: Five keys missing from extract_report_data() → sections always empty in auto-processed reports. Fixed (faed334). 770 tests passing (2 new).
- `margin_feedback_log`, `dynamic_pricing_log`, `company_gas_churn_log` now pass through to saved JSON
- `per_cid_pnl` and `per_cid_comm_pnl` pre-aggregated from `all_records` before JSON save (can't persist ~1M rows)
- Phase 17c customer P&L ranking and 17d dual-fuel P&L now populate in all auto-processed reports

**Phase 18a LIVE (2026-06-21)**: Regime detection premium in company tariff engine. 768 tests passing (9 new).
- `company/pricing/tariff_engine.py`: `_compute_regime_premium()` — 60d vs 180d spot price mean ratio
- Upward trend (ratio > 1.10) → premium up to +15%; downward trend (ratio < 0.90) → discount to -5%
- Wired into `get_forward_price()` as `regime_detect` param (default True; backward compat via False)
- Complements Phase 14c: 14c reacts to volatility, 18a reacts to trend direction
- Expected: 2021-22 upward crisis trend → 5-10% premium → reduced tariff under-pricing error

**Phase 17d LIVE (2026-06-21)**: Dual-fuel account combined P&L in annual report. 760 tests passing (4 new).
- `saas/reporting/annual_report.py`: `_section_dual_fuel_pnl()` — pairs electricity+gas legs, shows combined lifetime margin
- Flags gas accretive/dilutive per dual-fuel account; total gas net margin summary
- Answers: "Did our gas offering add value, or was it a drag on each dual-fuel account?"

**Phase 17c LIVE (2026-06-21)**: Per-customer lifetime P&L ranking in annual report. 756 tests passing (4 new).
- `saas/reporting/annual_report.py`: `_section_customer_pnl_ranking()` — ranks all billing accounts by lifetime net margin
- Aggregates all_records per customer: revenue, gross margin, capital, net margin, net margin %
- Answers: "which customers created vs destroyed value over their lifetime?"

**Phase 17b LIVE (2026-06-21)**: Churn avoidability analysis in annual report. 752 tests passing (5 new).
- `saas/reporting/annual_report.py`: `_section_churn_avoidability()` — classifies no-offer churns as blind misses vs deliberate passes
- Flags "detectable" blind misses (SIM p ≥ 30% but company said < 30%) — shows churn model's blind-spot cost
- Shows margin at stake per category; answers "how much did our churn model's false negatives cost us?"

**Phase 17a LIVE (2026-06-21)**: Portfolio learning premium — company adjusts tariffs from recent portfolio-wide margin rates. 747 tests passing (9 new).
- `company/pricing/tariff_engine.py`: `compute_portfolio_premium()` — mean recent electricity margins below 8% target → surcharge up to +15%; over-earning → discount up to -5%
- `simulation/run_phase2b.py`: tracks `portfolio_elec_margin_rates`; applies before Phase 16c surcharge at each electricity renewal
- Two-speed feedback now live: Phase 17a (portfolio-wide, 4-term) + Phase 16c (per-customer, 1-term emergency)
- Expected: 2021-22 losses accumulate in rolling window → systematic 10-15% premium on 2022-23 renewals

**Phase 16c LIVE (2026-06-21)**: Realized-margin feedback into renewal tariff. 748 tests passing (8 new).
- `company/pricing/margin_feedback.py`: recovery surcharge when prior term loss >5% of revenue (capped 20%)
- `simulation/run_phase2b.py`: tracks prev_term_margin/revenue per customer; applies surcharge at each renewal
- Closes the tariff feedback loop: company reacts to its own observed losses at each contract renewal
- Annual report: `_section_margin_feedback()` shows all surcharge events; `margin_feedback_log` in run JSON
- Expected impact: reduced structural losses in 2022-23 renewals (crisis aftermath recovery pricing)

**Phase 16b LIVE (2026-06-21)**: Retention durability analysis in annual report. 740 tests passing (5 new).
- `saas/reporting/annual_report.py`: `_section_retention_durability()` — post-retention survival months per customer
- 4/7 retained customers eventually churned: avg 60 months post-retention; 2017 cohort survived 60-84mo before churning
- 3 still active at simulation end (C8, C9, C2_2) — retention in 2017 gave C8 105+ months of active tenure
- Shows whether retention efforts are durable or merely delay churn

**Phase 16a LIVE (2026-06-21)**: Tariff repricing impact assessment in annual report. 735 tests passing (5 new).
- `saas/reporting/annual_report.py`: `_section_repricing_impact()` — churn risk at break-even tariff for each NET_NEGATIVE customer
- Active customers: repricing opportunity; churned: counterfactual (could B/E pricing have changed outcomes?)
- All 6 active loss-making customers repriceable with <25% churn risk — uplift is viable
- C3/C4/C2 churned facing "Partial" territory (40-44% at B/E) — incremental uplift over full repricing

**Phase 15d LIVE (2026-06-21)**: Hedge fraction signal in company churn model. 730 tests passing (6 new).
- `company/crm/churn_model.py`: `hedge_fraction` param + `HEDGE_SENSITIVITY_REDUCTION=0.4`
- `effective_rate_sensitivity = rate_sensitivity × (1 - hf × 0.4)` — well-hedged customers less reactive at renewal
- `simulation/run_phase2b.py`: passes previous term's hedge fraction into company estimate at electricity renewal
- Reduces structural 2021-22 over-estimation: hedged customers had stable bills despite headline rate spikes
- Next run: company_est 2021-22 expected to be lower for high-hf customers (prev divergence 2.79× → ?×)

**Phase 15c LIVE (2026-06-21)**: Full economic ROI in retention section. 724 tests passing (3 new).
- `saas/reporting/annual_report.py`: "Acquisition cost avoided" + "Full economic ROI" rows in retention table
- Full ROI = (margin saved - offer cost) + acq_cost_avoided; backwards-compatible (hidden for old-format logs)
- Surfaces the true economic case for retention (acq cost is a sunk cost either way if you don't retain)

**Phase 15b LIVE (2026-06-21)**: Acquisition-aware retention offer guard. 721 tests passing (4 new).
- `simulation/run_phase2b.py`: retention guard now `expected_margin + acq_cost_saved > ret_cost`
- Unblocks crisis-year offers where margin < ret_cost but acq_cost makes retention economical
- C5/C1 2021 (previously "uneconomical"): now offered. Expected: more retained crisis-year accounts
- `retention_log` includes `acq_cost_saved_gbp`; report section shows updated offer economics

**Phase 15a LIVE (2026-06-21)**: Gas renewal pressure section in annual report. 717 tests passing (5 new).
- `saas/reporting/annual_report.py`: `_section_gas_renewal_pressure()` — consumes company_gas_churn_log
- Year-by-year gas est table; elevated risk flagged (>20%); top-5 worst renewals with rate change direction
- Silent on pre-Phase-14b runs; will populate in next sim run at HEAD a761cc1+

**Phase 14b LIVE (2026-06-21)**: Gas-specific churn sensitivity. 712 tests passing (7 new).
- `company/crm/churn_model.py`: `fuel` param → gas uses BASE_CHURN_RATE=0.08, RATE_SENSITIVITY=0.6
- Gas contracts stickier (fewer alternatives) than electricity; dual-fuel gas legs rarely churn independently
- `simulation/run_phase2b.py`: tracks gas renewal rates; `company_gas_churn_log` in run output
- Next sim: gas rate pressure visible per-renewal in run JSON; no change to electricity retention logic

**Phase 14e LIVE (2026-06-21)**: Bill shock portfolio summary in annual report. 705 tests passing (5 new).
- `saas/reporting/annual_report.py`: `_section_bill_shock_summary()` — aggregates all bill_shock_events across years
- Year-by-year table: count + worst spike; top-10 worst spikes with churn status
- 274 total events in 61e5b3f run; worst: C2_2 2022-04-30 +1717%

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
- C6 2024 failure mode fixed: falling rate (−40%) + 45,000 kWh/year at £250/MWh → company now estimates 14% churn (was 0%; below 0.30 offer threshold, but C6 churns anyway via high roll)
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

**Latest simulation results (2016–2025)** — auto-processed (1118s / 19 min):
- Net margin: £5,207.26 | Gross: £6,434.89 | Capital: £1,228
- Treasury: £29,846 → £24,656 | 181 committee interventions | 1117 bills issued
- Enterprise value: £-8,944.68 | Net after CTS: £-10,276
- Retention: 22 offers, 18/22 retained | 2 no-offer churns | 6 total churned accounts

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
