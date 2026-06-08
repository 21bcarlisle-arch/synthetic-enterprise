# Project Status

Last updated: 2026-06-08T23:15:00Z
Current phase: Phase 1e complete — parked at `[REVIEW_GATE]`. Rich reviews whether risk physics produced organic hedging before Phase 2.
Last commit: bc8f569 — Phase 1e results: PHASE_1e_SUMMARY.md + simulation-strategy.md Phase 1e section

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

**`saas/` — business layer**
- `saas/README.md` — module purpose and seam boundary
- `saas/customers.py` — the 4-customer cohort (`CUSTOMERS`, `customer_to_settlement_input`) — C1 London/C2 Manchester/C3 Glasgow/C4 Cotswolds
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

**`interface/` — sim/saas seam**
- `interface/README.md`, `interface/contracts/.gitkeep` — seam scaffold (contracts not yet populated)

**`tools/`**
- `tools/delegate_ollama.py` — local-model delegation harness, routes to `qwen2.5-coder:14b` (code) or `qwen2.5:7b` (analysis/drafting) by task type

**`docs/`**
- `docs/simulation-period.md` — derivation of the 2016-01-01 → 2025-06-07 simulation window (P305 boundary)
- `docs/simulation-strategy.md` — companion to Phase 1d: hedging-strategy mechanics, what signal drove each evolution step, whether it improved
- `docs/phase0c-findings.md` — Phase 0c delegation-approach findings ("delegate everything" verdict)
- `docs/instructions/MASTER_BACKLOG.md` — the standing phase roadmap + NTFY/Phase-Summary/Delegation protocols (read at the start of every session)
- `docs/data-sources/{elexon,profile-class-1,customers,weather,gas-nbp}.md` — data-source design records (one per external/internal data source brought into the sim)
- `docs/observability/PHASE_{1a,1b,1c,1d}_SUMMARY.md` — per-phase summaries (What was built / Key findings / Key decisions / Open questions / Token efficiency)
- `docs/observability/token-log.md` — running process-observability log (frontier vs local token spend, per session)

## Phase summary index
- Phase 0a/0b: no standalone summary doc — see `docs/instructions/MASTER_BACKLOG.md` "Where We Are" for the headline numbers (Q4 2016 P&L = −£77.67)
- Phase 0c: `docs/phase0c-findings.md` (full-year 2016 P&L = −£78.28; dissatisfaction counter; CLV seed)
- Phase 1a: `docs/observability/PHASE_1a_SUMMARY.md` (4-customer cohort + geography)
- Phase 1b: `docs/observability/PHASE_1b_SUMMARY.md` (9.5 years of real daily weather, 4 locations)
- Phase 1c: `docs/observability/PHASE_1c_SUMMARY.md` (forward-curve pricing fixes 2016 losses; surfaced the empty-book gap)
- Phase 1d: `docs/observability/PHASE_1d_SUMMARY.md` (agent-discovered hedging — converged to fully naked, "learned the wrong lesson from a calm period")
- Phase 1e: `docs/observability/PHASE_1e_SUMMARY.md` — capital physics run. Survived. Treasury £3,250→£9,114. Central hypothesis not confirmed: capital costs (37.6% of gross) didn't produce organic hedging. C1/C2 trapped at hf=0.00 (evolution rule blind at that boundary). C3/C4 held at 0.10. 2021 only net-loss year (-£154). 2023 σ_stressed regime shift tripled collateral — invisible to trapped agents.

## Open gates
- **Phase 1e** (`[REVIEW_GATE]`, LIVE): Rich reviews whether risk physics produced organic hedging behaviour, and what the hf=0.00 trap finding implies for Phase 2 (Context Handshake threshold triggers vs. modified evolution rule). Full write-up: `docs/observability/PHASE_1e_SUMMARY.md` + `docs/simulation-strategy.md` Phase 1e section. This is the key Phase 1 milestone.
