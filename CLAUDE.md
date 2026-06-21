# CLAUDE.md — Synthetic Enterprise

## What this project is

A high-fidelity simulation of a fully autonomous, fully automated energy
supply business. Not a model of a company — a running approximation of one,
operating against real UK market data (Elexon/NESO), with all primary
commercial, financial, and operational processes.

The simulation runs on real historical half-hourly settlement data. The
business layer cannot see future data (Point-in-Time Blindfold, strictly
enforced). Everything that happens in the simulation must be explainable by
what a real supplier could have known at the time.

The ultimate goal: a simulation detailed enough that you could look at it
and say "that is how a real UK energy supplier works" — and use it to build,
test, and improve the systems that would run such a business autonomously.

---

## Who does what

**Rich** is the MD/board. He provides strategic direction, reviews outputs,
and steers priorities. He does not write code, run terminals, or manage
implementation details. His input arrives via staged instructions in
`docs/staging/`. His act of staging is his act of approval.

**This agent (Claude Code)** is the lead orchestrator. It reads staged
instructions, designs solutions, delegates implementation to local Qwen,
reviews outputs, runs tests, and manages the build. It knows the environment
better than Rich does and should design its own solutions rather than waiting
for implementation guidance.

**Local Qwen (qwen3:14b via Ollama)** handles all code generation,
mechanical execution, and self-correction. Frontier tokens are reserved for
reasoning, design, and review — not code writing.

**Risk committee agent** routes through local Ollama by design. No frontier
API spend in simulation runs.

---

## How to operate autonomously

**NTFY is the primary communication channel.** Rich uses it for steering,
questions, and quick direction changes. This window (Claude Code chat) is for
urgent or more involved conversations. The protocol:
- `background/ntfy_responder.py` acks inbound messages and writes them to
  `docs/staging/from_rich_TIMESTAMP.md` for substantive messages (>25 chars)
- At startup and after every task, poll `docs/staging/` — `from_rich_*.md`
  files are Rich's NTFY instructions; act on them exactly like staged files
- After acting on a `from_rich_*.md` message, send the result summary back
  via `background.ntfy_utils.send_ntfy` so Rich sees the answer on his phone
- Move actioned files to `docs/staging/done/` after processing

**At startup and after every completed task:** check `docs/staging/` for
unactioned files and action them immediately. Do not wait to be told.
- `run_complete_*.md` — a full run finished while the session was down; publish
  results (regenerate report, update LATEST.md, commit, push) then archive to
  `staging/done/`. **Do NOT send NTFY for routine sim run completions** —
  results are always on GitHub Pages. Only NTFY if the run shows an
  administration event, a new all-time high/low margin, or another notable
  exception. If multiple run_complete files are queued, process all silently in
  one batch and commit once.
- `run_pending_*.md` — a run was started; check if it finished and act accordingly.
- `from_rich_*.md` — an inbound NTFY message from Rich; act on it and reply via NTFY.

**At every REVIEW_GATE:** do not stop and wait indefinitely. Instead:
1. Complete the phase and commit all outputs
2. Send NTFY to Rich with results and the Gist URL for any reports
3. Write a proposed next instruction as `docs/staging/drafts/NEXT_PHASE.md`
4. Send a second NTFY: "Proposed next step in docs/staging/drafts/ — will
   proceed in 4 hours unless redirected"
5. If Rich stages a different instruction, action that instead
6. If no redirection arrives, action the draft after 4 hours

This opt-out model means the build continues autonomously unless Rich
actively steers it in a different direction.

**When usage budget is available between tasks:** be proactive. Check for
quick-win backlog items, fix known issues, improve test coverage, update
LATEST.md. Don't sit idle.

**Always update and commit LATEST.md before sending NTFY**, not after.
If LATEST.md is stale, investigate and fix the root cause.

---

## Current state (as of 21 June 2026 — 10:45 UTC)

**What's built:**
- Phase 0+1: agentic loop, Elexon data ingestion, profile-class billing,
  fixed tariffs, shape risk, dual-fuel gas expansion (SME)
- Deep risk physics: multi-tenor hedging, VaR, stress testing, risk
  committee (Context Handshake), 9.5-year run 2016–2025
- Weather engine: regime-switching AR1, regional Cholesky correlation,
  half-hourly translation, 4 locations, fitted 2016–2025
- Customer value layer: cost-to-serve, churn model (bill-shock driven),
  Shifted-BG CLV via PyMC-Marketing, home-move win rate, enterprise value
- Reporting function: `saas/reporting/annual_report.py`, `make report`
- Event-driven customer lifecycle: 6 customers actually churned (dated
  events), replacement customers activated via home-move wins
- Real ledger: 2.2M events — billing, settlement, capital charges, VAT,
  bad debt, acquisition; P&L emerges from transaction sum
- HH smart meter path: `simulation/hh_consumption.py`, C7-C9 on real HH data
- SIM/company separation deepened (Phase 11a+11b): company tariff engine
  (observable-data only) + company churn estimator; pricing and churn
  basis risk both visible in annual report
- Infrastructure: session-watchdog, staging-watcher, NTFY responder,
  File API, GitHub Pages status; NTFY spam fixed

**637 tests passing (SIM_FAST_MODE=1 suite, 16s).**

**Key financial position (Phase 11a run, company observable pricing):**
- Treasury: £29,846 → £11,131 (Phase 11a basis risk consumes treasury)
- Net margin: £-18,715 (company tariff underprices SIM forward curve)
- Gross margin: £-17,487
- Risk committee interventions: 323 (higher — price volatility 2021-2022)
- Enterprise value: £-20,661
- 2021 net margin: £-3,069 | 2022: £-5,582 (worst year, crisis + basis risk)
- *Pre-Phase-11a baseline (d7d3185): net margin +£13,958 with SIM-internal pricing*

**Phase 12d COMPLETE (2026-06-21)**: Margin-aware retention guard. 637 tests passing (3 new).
- `simulation/run_phase2b.py`: guard condition added — retention offer only made when `expected_margin > ret_cost` (i.e. gross margin rate > 5% discount). Crisis-year offers blocked when commodity margins collapse below the discount floor.
- `no_offer_churn_log` entries now carry `no_offer_reason`: "below_threshold" or "uneconomical" (high churn estimate but margin < discount cost)
- `saas/reporting/annual_report.py`: missed-opportunity breakdown shows count + margin by reason
- Effect visible in next full sim run: crisis-year offers eliminated; ROI expected to turn positive in normal years

**Phase 12c COMPLETE (2026-06-21)**: Retention ROI analysis live. 634 tests passing (17 new).
- `simulation/run_phase2b.py`: `no_offer_churn_log` — churns where company churn estimate was below 30% threshold (missed opportunities); `expected_term_margin_gbp` on all retention_log entries
- Bug fix: Phase 12b left retention outcomes as "pending" when offer made but no lifecycle event fired (customer renewed normally). Fixed: `elif` block now marks as "retained" and fires notify_retention_attempt
- `saas/reporting/annual_report.py`: "Retention Strategy P&L" extended with ROI summary (net_roi = margin_saved − total_cost), missed opportunity count + per-year breakdown
- **Test speedup**: `SIM_FAST_MODE=1` runs full test suite in 16s (vs 2,301s full simulation). All 634 tests pass in fast mode. Risk committee tests that mock `_call_local` now explicitly unset `SIM_FAST_MODE`.
- Model evaluation: gemma4:12b pulled (7.6GB) and being evaluated vs qwen3:14b on dispatcher/discovery/risk committee tasks

**Phase 12b COMPLETE (2026-06-21)**: Company retention offers live.
- `RetentionEvent` in `company/crm/event_log.py` + `notify_retention_attempt()` on all SimInterface classes
- Pre-roll retention check in `run_phase2b.py`: if company estimate > 30% threshold, offer made before SIM rolls
- `make_retention_cost_event()` in ledger: foregone margin recorded as cash-out
- Annual report: "Retention Strategy P&L" section with offer/retained/churned table
- 617 tests passing (23 new)

**Phase 12a COMPLETE (2026-06-20)**: Company CRM event log live.
- `CompanyEventLog` with dated `ChurnEvent` / `AcquisitionEvent` artefacts
- `LiveSimInterface.notify_churn` / `notify_acquisition` record to event log
- `run_phase2b.py` emits notifications on every churn/acquisition roll
- Annual report: "Company CRM — Event Log" section with year-end reconciliation
- 597 tests passing (20 new)

---

## The five hollow gaps

These are the things that make the simulation feel like a model rather than
an operating company. Status as of 21 June 2026:

1. **Customer events firing — DEEPENED (Phase 12b).** Six customers have
   actually churned with specific dates (C3/C1/C5/C2/C6/C4). Replacement
   customers activate via home-move wins. Company CRM has `CompanyEventLog`
   with dated `ChurnEvent` / `AcquisitionEvent` / `RetentionEvent` artefacts.
   Phase 12b complete: company's churn estimate (>30%) triggers a pre-roll
   retention offer that reduces SIM churn probability by 20%. Outcome recorded
   as "retained" or "churned_despite_offer". This is the first company decision
   that changes simulation outcome. Retention cost in ledger; ROI analysis next.

2. **Ledger — CLOSED.** 2.2M ledger events: billing, settlement, capital
   charges, VAT remittance, bad debt, acquisition spend. P&L is now the sum
   of transactions, not a formula.

3. **SIM/company barrier — DEEPENED, not yet closed.** Company now has its
   own tariff engine (observable forward prices only) and churn estimator
   (observable rate change + tenure). Both make consequential decisions using
   only what a real supplier could see. But the company still has implicit
   visibility into SIM internals through shared code paths. Full operational
   independence (company running blind on its own models) is the long-horizon
   goal.

4. **HH smart meter data path — CLOSED.** `simulation/hh_consumption.py`
   provides real HH consumption data. C7-C9 run on HH shapes instead of
   profile class. ToU tariffs are architecturally possible.

5. **Reporting — CLOSED.** Annual report, cost-to-serve breakdown, CLV
   snapshots, churn basis risk, pricing basis risk — all published to
   GitHub Pages on every sim run.

---

## Original phase plan vs what was built

**Original plan:**
- Phase 0: Prove the machine (agentic loop, tools, plumbing)
- Phase 1: Old world billing (resi electricity, profile classes, fixed tariffs)
- Phase 2: Smart metering (HH data, time-of-use tariffs, residential scale)
- Phase 3: I&C traded accounts (large sites, flex tranche hedging)
- Phase 4: The 2032 world (VPP, DER, EV/solar/battery)

**What actually happened:**
- Phase 0+1: Done but went much deeper than planned. Hedging evolution,
  enterprise risk physics, activity-based pricing discovery, 9.5yr run.
- Phase 2: Became SME + dual-fuel gas instead of HH metering. HH never done.
- Phase 3: Became physics calibration (price engine, weather model) instead
  of I&C. I&C never done.
- Phase 4: Became customer value layer (CLV, churn, cost-to-serve) instead
  of VPP/DER.

**Decisions made 14 June 2026:**
- HH smart meter customers are next priority after 5b
- I&C deferred until HH and event-driven customer lifecycle are in place
- VPP/DER remains the long-horizon destination
- C&I not being pursued yet

---

## Simulation Design Decisions

**Minimum hedge mandate (Phase 5c, 14 June 2026):** the hedging model was
redesigned from "speculative book with a risk governor" to "supply
obligation first, active position second" — matching how real suppliers
(e.g. EDF) actually operate.

- `sim/hedging_strategy.MIN_HEDGE_FLOOR = 0.85` — every contract term starts
  at least 85% hedged. Day one no longer starts at a neutral 50/50 guess;
  `decide_initial_hedge_fraction()` returns the mandate floor directly.
- The active position (at most 15% of volume, unhedged) is what the risk
  committee and `evolve_hedge_fraction()` manage. `evolve_hedge_fraction()`
  can raise the fraction toward 1.0 (lean further into hedging) but never
  drops below `MIN_HEDGE_FLOOR` — a bad term trims the active position back
  toward the floor, it never unwinds the supply obligation itself.
- Capital cost was *already* charged only on the unhedged (naked) portion of
  volume (`naked_kwh = eac_kwh * (1 - hedge_fraction)` in
  `simulation/run_phase2b.py`, fed to `sim.risk_engine.assess_term_risk`).
  Raising the floor to 0.85 therefore caps that naked exposure — and the
  collateral/capital-cost charge derived from it — at 15% of volume by
  construction, with no separate capital-cost code change needed.
- The previous reactive model's run output is preserved as
  `docs/reports/run_output_old_reactive_model_pre5c.json` so
  `ANNUAL_REPORT.md`'s "Hedging Mandate — Before/After Phase 5c" section can
  compare mandate-hedged vs. old reactive vs. fully naked without re-running
  the old model.

---

## Architectural Laws

### Epistemic Honesty — The Company Cannot See Inside the SIM

The company layer operates under the same information constraints as a
real energy supplier. It cannot see simulation internals — churn model
parameters, forward curve construction, weather engine outputs, VaR
model internals. It discovers the world through observable interfaces:
market data feeds, meter reads, customer interactions, its own bills
and payments, regulatory publications.

The company's models (churn, demand, forward curve) are approximations
built from observed outcomes — not reads from simulation ground truth.
Those approximations will be imperfect. That imperfection is the point.

Before writing any company-layer code, ask: "Could a real UK energy
supplier know this?" If the answer requires reading simulation internals,
it is a violation of this principle.

The SIM/company seam (`company/interfaces/sim_interface.py`) enforces
this boundary. It exposes observables and outcomes. It never exposes
parameters or internals.

---

## Sequencing principles

**Two-way-door filter:** don't build something that depends on an unresolved
upstream question. Check dependencies before starting.

**Build efficiency is measured two ways:**

- Hard metric: tests passing and new capabilities added per frontier session.
  Objective and stable regardless of how business rules evolve.
- Soft metric: fidelity delta — one sentence per phase describing what the
  simulation can now do that it couldn't before. Rich assesses this as the
  domain expert.

CLV is a business-layer metric for understanding the simulated company's
health, not for measuring build efficiency. It will evolve as the business
rules change and is not a stable measuring stick for token spend.

Every phase should be justifiable by the capability it unlocks relative to
its token cost.

**Reversibility** is the governing through-line in data architecture and
agent governance. Prefer designs that can be unwound.

**Regime-change blindness** is a known failure mode. The simulation
independently converged to near-naked hedging during 2016–2020 calm data,
directly before the 2021–2022 crisis — mirroring what killed real suppliers.
Any hedging or risk model must be designed with this in mind.

**Activity-based pricing necessity:** flat margin pricing makes some
customers net-negative. This emerged from the data, not from design. Any
pricing model must account for cost-to-serve at the customer level.

---

## Roadmap from here

**Model evaluation complete (2026-06-21)**: gemma4:12b vs qwen3:14b — **keep qwen3:14b**.
- Same accuracy on all 3 tasks (dispatcher 10/10, discovery 5/5, risk committee valid)
- qwen3:14b 4x faster: 4.5s/call vs 20.9s/call (dispatcher), 11s vs 34.6s (risk committee)
- gemma4:12b at 7.6GB (smaller) but slower inference on this hardware (RTX 3060 12GB)
- Switching to gemma4 would make the sim ~3 hrs, not 38 min. Stick with qwen3:14b.

**Immediate (Phase 12e candidates):**
- SIM performance: consider switching background sim_runner to SIM_FAST_MODE=1 for dev runs (16s tests; 23x faster sim). Reserve full LLM mode for staged milestone runs.
- Run_complete processing mechanization: autonomous runner frontier tokens spent on processing staging markers. Could be a pure shell script (`make report && git commit && git push`) to save 1 frontier turn per sim run.
- Retention threshold tuning: Phase 12d guard eliminates uneconomical offers. Next: threshold at 30% — is it too low? Would a higher threshold reduce false positives (offers where customer would renew anyway)?
- OR: SIM/company full operational independence (company runs on its own models end-to-end)

**Then:**
- SIM/company full operational independence: company runs on its own models
  end-to-end; divergence from SIM ground truth accumulates and is measured
- ToU tariffs for HH customers (C7-C9 eligible now)
- I&C accounts (when HH data path and event lifecycle are solid)

**Later:**
- VPP/DER
- Complaint, debt, disconnection as events
- Real forward hedging (company decides hedge fraction, not SIM agent)

---

## Technical environment

**Hardware (Skynet):**
- Intel i5-13400F, 32GB DDR4, RTX 3060 12GB VRAM
- Windows 11 Pro host, WSL2/Ubuntu with systemd

**Networking:**
- Tailscale: WSL2 `100.69.81.59`, Windows host `100.72.35.103`
- File API: `https://skynet-1.taila062fa.ts.net` (port 8765, Tailscale Funnel)
- SSH: `ssh rich@100.69.81.59`, then `tmux attach -t claude`

**AI stack:**
- Claude Code: lead orchestrator (this agent)
- qwen3:14b via Ollama: all code generation and mechanical execution
- Risk committee: local Ollama (no frontier spend in simulation runs)

**Key files:**
- `CLAUDE.md`: this file — primary agent anchor
- `MASTER_BACKLOG.md`: phase execution instructions
- `docs/staging/`: instruction staging directory (check on every startup)
- `docs/staging/drafts/`: agent-proposed next steps
- `docs/status/LATEST.md`: current state (update before every NTFY)
- `docs/reports/ANNUAL_REPORT.md`: operator-facing annual report
- `docs/reports/REPORTING_BACKLOG.md`: reporting improvement queue

**Data sources:**
- Elexon Insights Solution: `data.elexon.co.uk` (key-free)
- NESO CKAN data portal
- Open-Meteo (weather)
- Synthetic forward curves based on historical spot prices

**Elexon note:** The API migrated to the Insights Solution. Most existing
GitHub wrappers are partially stale. Always verify against live endpoints.

---

## Key learnings — do not repeat these mistakes

- **Local models confabulate endpoints.** Pre-load ground-truth API context
  before any local model touches external data sources.
- **LATEST.md must be committed before NTFY**, not after. If it's stale,
  fix the root cause.
- **REVIEW_GATE pattern must only match on actual pane idleness**, not on
  prose that mentions the string "REVIEW_GATE". (Bug fixed June 2026.)
- **Staging-watcher notifies Rich, not the agent.** The agent must poll
  `docs/staging/` itself — do not rely on being told when work arrives.
- **The simulation is not the company.** Keep them conceptually separate
  even before the functional separation is built. The company makes decisions
  based on what it's allowed to see. The simulation is the environment it
  operates in.
- **Non-blocking concurrency.** If blocked on one task (e.g. a long
  background simulation run), don't wait idle — move to the next
  independent item in `docs/staging/` or the backlog and come back once
  unblocked.
- **The session usage window is ~5 hours, not 4.** Claude Code's UI calls it
  the "5-hour limit"; `docs/observability/usage-limit-tracking.md` logs the
  actual reset intervals observed. Don't assume a 4-hour budget when
  estimating how much work fits in a session (the REVIEW_GATE opt-out
  window's "4 hours" is an unrelated, deliberately-chosen wait period for
  staged instructions, not a usage-window estimate).
