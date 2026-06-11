# Project Status

Last updated: 2026-06-11T15:45:00Z
Current phase: Phase 3b (price engine calibration) begun — [REVIEW_GATE] OPEN, does not clear. sim/price_engine.py implements the spec'd merit-order formula; calibrated against real 2019/2022 SSP, demand, and renewable-generation data and overestimates SSP by ~10x at gamma=1.5 (the spec's floor), worsening at higher gamma. Escalation to Rich: the demand/renewable margin term needs redesign before re-calibration — see `docs/calibration/price-engine.md`. Phase 2b (gas dual fuel) also remains open as [REVIEW_GATE] pending Rich review (ANTHROPIC_API_KEY escalation).
Last commit: pending — Phase 3b price engine + calibration report

## Committed files (all phases)

**Root / config**
- `CLAUDE.md` — project charter: laws, principles, phase structure, simulation window, scope discipline
- `.claude/agents/{interface-steward,saas-engineer,sim-engineer}.md` — the three subagent role definitions for the sim/saas/interface seam
- `.claude/settings.json`, `.claude/settings.local.json` — permissions and tool allowlists

**`sim/` — historical data, point-in-time market state, synthetic forward curves**
- `sim/README.md` — module purpose and seam boundary
- `sim/system_prices.py`, `sim/system_prices_history.py` — Elexon BMRS System Sell Price ingestion (point-in-time and ranged history)
- `sim/profile_class_1.py` + `sim/data/profile_class_1_gad.csv` — domestic Profile Class 1 consumption shape (48 half-hourly periods/day)
- `sim/forward_curve.py` — `generate_forward_price()`: Law 3 synthetic forward curve (90-day base + sigma volatility premium + seasonal blend)
- `sim/weather_ingestor.py` — Open-Meteo historical daily weather pull, by customer location
- `sim/hedging.py` — `settle_hedged_period()`: pure per-period hedge economics (hedged share at forward price, unhedged at spot)
- `sim/hedging_strategy.py` — the agent's hedging decision/evolution logic (`decide_initial_hedge_fraction`, `evolve_hedge_fraction`)
- `sim/risk_engine.py` — Phase 1e: dual-window VaR (sigma_recent coefficient-of-variation + sigma_stressed regulatory floor), active collateral, monthly cost of capital (WACC=10%)
- `sim/price_engine.py` — Phase 3b: merit-order wholesale price model (gas floor, system margin shape, wind cubic power curve) — calibration in progress, gate not yet cleared
- `sim/generation_demand_history.py` — Phase 3b: Elexon demand/outturn + AGWS wind-and-solar generation ingestion, the price engine's demand/renewable inputs

**`saas/` — business layer**
- `saas/README.md` — module purpose and seam boundary
- `saas/customers.py` — the 6-customer cohort (C1-C4 resi, C5-C6 SME with profile_class=3)
- `saas/tariff_pricing.py` — `price_fixed_tariff()`: applies business margin to a pre-generated forward price (pure margin step, curve-generation lives in `sim/`)
- `saas/customer_reaction.py` — `score_dissatisfaction()`: Experience-observability seed (counts periods where wholesale cost > 120% of bill)
- `saas/clv_seed.py` — `build_clv_seed()`: per-customer running (billed − cost) total, the first CLV building block

**`simulation/` — orchestration / phase-runner scripts**
- `simulation/README.md` — module purpose and seam boundary
- `simulation/settlement.py` — `run_settlement()`/`build_portfolio_pnl` core: per-customer, per-period spot-only settlement loop (the structure every later settlement variant mirrors)
- `simulation/portfolio_pnl.py` — `build_portfolio_pnl()`: aggregates settlement records into portfolio + per-customer P&L
- `simulation/renewals.py` — `build_renewal_schedule()`: chains a customer's contract terms contiguously, re-pricing each at the forward curve (100% renewal, no churn)
- `simulation/hedged_settlement.py` — `run_hedged_term()`: settles exactly one contract term, hedge-aware, structurally enforcing "no foresight"
- `simulation/run_phase0b.py` — Phase 0b: first 4-customer Q4-2016 spot-only settlement + P&L
- `simulation/run_phase0c.py` — Phase 0c: full-year 2016 run + dissatisfaction scoring + CLV seed wiring
- `simulation/run_phase1b_weather_pull.py` — Phase 1b: pulls and stores 9.5 years of daily weather for all 4 customer locations
- `simulation/run_phase1c.py` — Phase 1c: re-runs the 2016 settlement with forward-curve pricing (margin flips −£78.28 → +£498.68)
- `simulation/run_phase1c_full_window.py` — Phase 1c: full 2016-2025 run that surfaced the empty-book gap (no renewal mechanic)
- `simulation/run_phase1c_renewals.py` — re-runs the full-window settlement with renewals active (book stays full, 4 customers every year 2016-2025)
- `simulation/run_phase1d.py` — Phase 1d: full agent-discovered hedging run across all customers and the full window
- `simulation/run_phase1e.py` — Phase 1e: nine-year portfolio run with enterprise risk physics (dual-window VaR, shared £3,250 treasury, administration-event halting, chronological interleaving)
- `simulation/run_phase2a.py` — Phase 2a: 6-customer run with SME segment (PC3 shape), Context Handshake (RiskCommitteeMonitor + risk_committee_agent), scaled treasury £18,416.67, chronological term interleaving
- `simulation/run_phase1e_repriced.py` — Phase 1e re-run with activity-based pricing (comparison baseline)
- `simulation/run_phase2a_repriced.py` — Phase 2a re-run with activity-based pricing + recalibrated risk committee (VAR_BREACH_MULTIPLIER=2.50, treasury health gate)
- `simulation/run_phase2b.py` — Phase 2b: gas dual-fuel run (C1-C4 + C1g-C4g + C5-C6, shared treasury)
- `simulation/run_phase3a.py` — Phase 3a: experience observability report (bill shock / cumulative exposure / expectation gap)
- `simulation/run_phase3b_calibration.py` — Phase 3b: price engine calibration run (2019/2022 sample years vs real SSP)

**`interface/` — sim/saas seam**
- `interface/README.md`, `interface/contracts/.gitkeep` — seam scaffold (contracts not yet populated)

**`tools/`**
- `tools/delegate_ollama.py` — local-model delegation harness, routes to `qwen2.5-coder:14b` (code) or `qwen2.5:7b` (analysis/drafting) by task type

**`sim/`** (continued)
- `sim/profile_class_3.py` + `sim/data/profile_class_3_gad.csv` — PC3 (non-domestic unrestricted) GAD shape (fetched from UKERC/CEDA)
- `sim/risk_committee.py` — RiskCommitteeMonitor: treasury drawdown + VaR breach threshold checks, context packager
- `sim/risk_committee_agent.py` — frontier LLM risk committee agent (one lever: hedge_fraction, fired on threshold breach)
- `sim/cache_store.py` — lightweight JSON cache layer; background tasks pre-fetch, simulation checks before live API

**`background/`**
- `background/background_worker.py` — autonomous off-peak worker (Qwen only, no frontier tokens, pauses 16:00-19:00 GMT)
- `background/run_queued_tasks.py` — task dispatcher: reads background-tasks.md queue, runs via Ollama, logs performance + sends NTFY
- `background/start_worker.sh` — launches worker in detached tmux session

**`docs/`**
- `docs/simulation-period.md` — derivation of the 2016-01-01 → 2025-06-07 simulation window (P305 boundary)
- `docs/simulation-strategy.md` — companion to Phase 1d: hedging-strategy mechanics, what signal drove each evolution step, whether it improved
- `docs/phase0c-findings.md` — Phase 0c delegation-approach findings ("delegate everything" verdict)
- `docs/instructions/MASTER_BACKLOG.md` — the standing phase roadmap + NTFY/Phase-Summary/Delegation protocols (read at the start of every session)
- `docs/data-sources/{elexon,profile-class-1,profile-class-3,customers,weather,gas-nbp}.md` — data-source design records
- `docs/instructions/background-tasks.md` — background worker task queue (QUEUED/RUNNING/DONE)
- `docs/observability/PHASE_{1a,1b,1c,1d}_SUMMARY.md` — per-phase summaries (What was built / Key findings / Key decisions / Open questions / Token efficiency)
- `docs/observability/token-log.md` — running process-observability log (frontier vs local token spend, per session)
- `docs/observability/pricing-fix-comparison.md` — flat-margin vs activity-based pricing comparison (C6 flip, all-customer net margins, year-by-year)

## Phase summary index
- Phase 0a/0b: no standalone summary doc — see `docs/instructions/MASTER_BACKLOG.md` "Where We Are" for the headline numbers (Q4 2016 P&L = −£77.67)
- Phase 0c: `docs/phase0c-findings.md` (full-year 2016 P&L = −£78.28; dissatisfaction counter; CLV seed)
- Phase 1a: `docs/observability/PHASE_1a_SUMMARY.md` (4-customer cohort + geography)
- Phase 1b: `docs/observability/PHASE_1b_SUMMARY.md` (9.5 years of real daily weather, 4 locations)
- Phase 1c: `docs/observability/PHASE_1c_SUMMARY.md` (forward-curve pricing fixes 2016 losses; surfaced the empty-book gap)
- Phase 1d: `docs/observability/PHASE_1d_SUMMARY.md` (agent-discovered hedging — converged to fully naked, "learned the wrong lesson from a calm period")
- Phase 1e: `docs/observability/PHASE_1e_SUMMARY.md` — capital physics run. Survived. Treasury £3,250→£9,114. Central hypothesis not confirmed: capital costs (37.6% of gross) didn't produce organic hedging. C1/C2 trapped at hf=0.00 (evolution rule blind at that boundary). C3/C4 held at 0.10. 2021 only net-loss year (-£154). 2023 σ_stressed regime shift tripled collateral — invisible to trapped agents.
- Phase 2b: `docs/observability/PHASE_2b_SUMMARY.md` — gas dual fuel (NBP SAP price feed, CV/CF conversion, C1g-C4g). Full 2016-2025 run survived: net margin £16,799.11 (electricity £13,678.68 + gas £3,120.43), treasury £21,829.17 → £38,628.27. 2021 only net-loss year (-£2,002.62). 0 Context Handshake wake-ups.
- Phase 3a: `docs/observability/PHASE_3a_SUMMARY.md` — experience observability depth (`score_experience_signals()`: bill_shock_score, cumulative_exposure, expectation_gap). Combined dual-fuel billing (C1-C4 + C1g-C4g as one bill) roughly halves crisis-year shock counts (C1-C4 2021-22 total: 102 → 44). 2016 shocks concentrated in London; 2021-22 shocks much higher across all legs, highest for smaller-consumption profiles.
- Phase 3b: `docs/calibration/price-engine.md` — price engine calibration. `sim/price_engine.py` implements the spec'd merit-order formula; calibrated against real 2019/2022 data, it overestimates SSP by ~10x at gamma=1.5 (spec floor), worsening at higher gamma — gate does not clear, margin-term redesign needed. Wind cubic physics implemented/tested but not yet validated against real wind data.

## Open gates
- **Phase 1e** (`[REVIEW_GATE]`, SUPERSEDED): Closed by Phase 2a.
- **Phase 2a** (`[REVIEW_GATE]`, SUPERSEDED): Pricing fix applied; C6 now net-positive. See pricing-fix-comparison.md.
- **Pricing fix + Context Handshake** (`[REVIEW_GATE]`, SUPERSEDED): Closed by Phase 2b. Activity-based pricing confirmed working (C6: -£1,176 → +£620, treasury +£4,977 improvement vs flat margin). Full comparison: `docs/observability/pricing-fix-comparison.md`.
- **Phase 3b — Price Engine Calibration** (`[REVIEW_GATE]`, OPEN — does not clear): `sim/price_engine.py` implements the spec'd merit-order formula (`gas_floor * (demand/renewable)^gamma`). Calibrated against real 2019 (calm) and 2022 (crisis) Elexon demand/AGWS/SSP + NBP gas data: overestimates SSP by ~10x at gamma=1.5 (the spec's floor), correlation weak (0.1-0.3), worsening monotonically as gamma→2.5. Even gamma=0 (gas floor alone) leaves ~40-45% MAE. **Escalation to Rich**: the demand/renewable margin term needs redesign (two candidates proposed in the report) before re-calibration. See `docs/calibration/price-engine.md`.
- **Phase 2b — Gas Dual Fuel** (`[REVIEW_GATE]`, LIVE): anthropic SDK confirmed installed (0.107.1) and importable from risk_committee_agent.py. Full 2016-2025 dual-fuel run survived (net margin £16,799.11, treasury £21,829.17 → £38,628.27). Risk committee still cannot fire — no `ANTHROPIC_API_KEY` in this environment, every wake-up (had any fired) would fail with an auth error, caught and logged. **Escalation to Rich**: an API key / billing decision is needed before the Context Handshake can ever activate. See `docs/observability/PHASE_2b_SUMMARY.md` for full findings and open questions.

## Background Worker Performance

| Task | Tokens (P/E) | Wall time | Output | Consumed by | Value |
|------|-------------|-----------|--------|-------------|-------|
| pre-fetch-elexon-full | 96/44 | 8s | background-task-pre-fetch-elexon-full.md (0.3KB) | pending | pending |
| pre-fetch-weather-full | 99/26 | 1s | background-task-pre-fetch-weather-full.md (0.3KB) | pending | pending |
| pre-fetch-pc3-profiles | 79/40 | 7s | background-task-pre-fetch-pc3-profiles.md (0.4KB) | pending | pending |
| pre-fetch-nbp-gas-full | -/- | - | pending | pending | pending |
| code-quality-audit | -/- | - | pending | pending | pending |
| simulation-sensitivity-experiments | -/- | - | pending | pending | pending |
