# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-23T11:02:24Z

**Full Ollama run complete (2026-06-23, commit ffb7ecc, 445s — 20 consecutive runs stable):**
- **Net margin: £1,158,439 | Gross: £5,980,190 | Treasury: £3,625,075 | SURVIVED**
- All I&C tariff types active (fixed, pass-through, deemed, flex). Gas seasonal calibration. 38 committee calls (~monthly). Figures consistent across all post-bugfix runs.

**Architecture Stage 0 (2026-06-23)**: Observability + system health panel live.
- `background/agent_status.py`: all 8 daemons now emit structured status (last_heartbeat, last_action, anomaly)
- System tab added to poesys.net dashboard — green/amber/red per heartbeat age
- Best-practice audit at `docs/claude/best-practice-audit.md` — STOP gate reached, awaiting Rich's "proceed stage 1"

**Bugfixes (2026-06-23)**: 4 production bugs fixed after overnight crash.
- Committee cooldown: record-count → date-based (30-day calendar). Was firing 10× too often with I&C customers.
- Volume tolerance crash on deemed/flex (forward_price=None) — guard added.
- `cost_to_serve.py` missing I&C segment → KeyError — added.
- `C_IC3g` missing contract_type key — default fallback added.

**Phase 42 LIVE (2026-06-22)**: Gas-specific seasonal forward curve. 8 new tests (1,228+ passing).

**Phase 41a LIVE (2026-06-22)**: Flex/trading tariff for I&C customers. 8 new tests (1,220+ passing).
- `C_IC4`: Manchester supermarket, 3 GWh/year, `tariff_type: "flex"`. HH metered.
- `simulation/hedged_settlement.py`: `run_flex_term()` — revenue = (7-day rolling spot average + £2/MWh markup) × consumption. Gross margin = markup × consumption (predictable). Capital cost = 0, hedge fraction = 1.0.
- `simulation/renewals.py`: flex terms carry no locked unit rate; only markup agreed at signing.
- All 4 UK I&C tariff types now complete: Fixed (C_IC1/C_IC2), Pass-through (C_IC3/C_IC3g), Deemed (C_IC1/C_IC2 out-of-contract), Flex (C_IC4).

**Phase 41-prep LIVE (2026-06-22)**: Forward curve reform — EWMA + term structure model. 10 new tests.
- `sim/forward_curve.py` rewritten: `forward = spot_EWMA × seasonal_shape × (1 + term_premium)`.
- EWMA half-life 30 days (vs old 90-day SMA) — faster regime adaptation.
- Term premium: 6% for 1-year electricity (sqrt-tenor scaling); calibrated to UK N2EX historical data.
- Monthly seasonal multipliers: Q1/Q4 premium (1.12×), Q2/Q3 discount (0.88×).
- Research: `docs/market_research/uk_power_forward_curves_2016_2025.md` — ICE/N2EX structure, crisis backwardation analysis.

**Phase 40c LIVE (2026-06-22)**: Deemed rate for out-of-contract I&C customers. 8 new tests.
- `build_renewal_schedule()`: `deemed_gap_days` param inserts an out-of-contract period between terms.
- `run_deemed_term()` in `hedged_settlement.py`: billed at (7-day rolling spot + 20% premium). Capital cost = 0.
- Industry-standard UK out-of-contract pricing. Triggers when I&C customer doesn't renew on time.

**Phase 40b LIVE (2026-06-22)**: Gas pass-through leg + tariff type in annual report. 7 new tests.
- `C_IC3g`: Teesside industrial gas, 5 GWh/year, `tariff_type: "pass_through"`.
- `simulation/gas_settlement.py`: `pass_through=True` — actual gas network + CCL + GGL billed at settlement (not locked at pricing time). Company bears only wholesale spread risk.
- `saas/reporting/annual_report.py` `_section_customer_pnl_ranking()`: tariff type column added.

**Phase 40a LIVE (2026-06-22)**: I&C pass-through tariff. 9 new tests + 2 stale fixes.
- `C_IC3`: Teesside chemical plant, 4 GWh/year, `tariff_type: "pass_through"`.
- `simulation/hedged_settlement.py` `run_hedged_term()`: `pass_through=True` — actual policy + network passed through to revenue; company bears only wholesale spread risk.

**Phase 39a LIVE (2026-06-22)**: SVT comparative pricing for passive renewers. 18 new tests (1,127 passing).
- `simulation/svt_rates.py`: Ofgem Default Tariff Cap electricity rates 2016–2029 (£/MWh).
- SVT comparison table in annual report: flags at-risk (above SVT) and protected (below SVT) cohorts.

**Phase 38a LIVE (2026-06-22)**: Scenario comparison runner. 12 new tests.
- `simulation/scenario_comparison.py`: runs all 5 scenarios, returns sorted KPI comparison.
- `format_comparison_table()`: markdown table — all scenarios side-by-side.

**Phase 35a-37a LIVE (2026-06-22)**: Forward scenario infrastructure.
- Bimodal electricity price generator (5 named scenarios), gas scenario generator, scenario integration runner, scenario metadata banner in annual report.
- Scenarios: `baseline_2025`, `central_2027`, `stress_dunkelflaute_2027`, `low_renewables_2027`, `battery_saturation_2029`.

**Phase 34a LIVE (2026-06-22)**: 42-day renewal notice period. 9 new tests.
- Company prices tariff using data from 42 days before term start (statutory notice). Amplifies basis risk in crisis: company priced pre-spike, SIM hedged at term_start.

**Phase 33a/33b LIVE (2026-06-22)**: Active/passive renewal split. 16 new tests.
- 65% passive (SVT rollers): 5% base churn, 10% cap, low rate sensitivity.
- 35% active (fixed-term choosers): standard churn model.
- 2022 crisis: all renewals forced passive (no fixed deals available in UK market).

**Phase 30a-32a LIVE (2026-06-22)**: Full policy cost stack + gas P&L.
- RO, CfD, CCL, CM (Capacity Market), FiT (Feed-in Tariff) all in settlement P&L.
- Gas book P&L section: gas CCL, GGL, network charges; year-by-year gas gross/net margin.
- Full electricity policy cost stack: £15–45/MWh (RO+CfD+CCL+CM+FiT).

**Phase 27a-29b LIVE (2026-06-22)**: I&C expansion + full cost stack.
- C_IC1 (2 GWh warehouse), C_IC2 (1 GWh office), C_IC3 (4 GWh chemical pass-through), C_IC4 (3 GWh supermarket flex).
- Triad risk (TNUoS), volume tolerance, CCL for I&C.
- Network charges (DUoS + TNUoS) calibrated to Ofgem Annex 9 v1.10.

**Dashboard LIVE (2026-06-22)**: poesys.net — 5-tab intranet dashboard (auto-deploys from main).
- Tabs: Overview, Financial, Trading, Customers, Market.
- Trading: spot vs forward price chart, extreme events, risk committee interventions, crisis visible.
- Market: spot vs 1-year forward contango/backwardation chart (2021 crisis backwardation visible).
- Customers: book size, net margin heatmap by customer/year, retention offers, lifecycle events.

**Latest simulation results (2016–2025)** — auto-processed (462s / 8 min):
- Net margin: £5,898,358.97 | Gross: £5,994,248.78 | Capital: £95,890
- Treasury: £2,466,636 → £3,625,075 | 38 committee interventions | 1569 bills issued
- Enterprise value: £6,535,890.41 | Net after CTS: £5,890,084
- Retention: 19 offers, 18/19 retained | 4 no-offer churns | 5 total churned accounts

Previous run figures (Phases 13a-13e, commit 61e5b3f — pre-I&C expansion):
- Net margin: £225,920 | Gross: £235,160 | Capital: £9,240
- Treasury: £463,166 → £465,105 | Enterprise value: £309,282
- 23 retention offers, 19/23 retained | 3 no-offer churns

**Autonomous stack**: sim_runner, autonomous_runner, health_check, staging_watcher, ntfy_responder — all operational.
Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
Dashboard: https://poesys.net
