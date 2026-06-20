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

## Current state (as of 14 June 2026)

**What's built:**
- Phase 0+1: agentic loop, Elexon data ingestion, profile-class billing,
  fixed tariffs, shape risk, dual-fuel gas expansion (SME)
- Deep risk physics: multi-tenor hedging, VaR, stress testing, risk
  committee (Context Handshake), 9.5-year run 2016–2025
- Weather engine: regime-switching AR1, regional Cholesky correlation,
  half-hourly translation, 4 locations, fitted 2016–2025
- Customer value layer: cost-to-serve, churn model (bill-shock driven),
  Shifted-BG CLV via PyMC-Marketing, home-move win rate, enterprise value
- Reporting function: `saas/reporting/annual_report.py`, `make report`,
  REPORTING_BACKLOG.md
- Infrastructure: session-watchdog (usage-limit auto-resume), staging-watcher,
  File API (systemd user unit), GitHub Pages status

**273 tests passing.**

**Key financial position (latest run, mandate-hedged per Phase 5c):**
- Treasury: £21,829.17 → £37,953.15
- Net margin: £16,123.98
- Gross margin: £18,970.93
- Capital cost ratio: 15.0% (was 41.4% under the old reactive model)
- Risk committee interventions: 99
- Enterprise value: £10,496.28
- 2021 net margin: £632.78 (was £-1,096.43 under the old reactive model)

**In progress:**
- Phase 6a: next phase TBD — see `docs/staging/`

---

## The five hollow gaps

These are the things that make the simulation feel like a model rather than
an operating company. They are the primary design challenge going forward:

1. **No customer events actually firing.** Home move, renewal, complaint,
   debt — these are probability scores and win rates, not events. No customer
   has ever actually left, arrived, complained, or moved house in the
   simulation. The customer roster has been static since 2016.

2. **No ledger.** There is no record of money moving. Bills are computed but
   not issued as artefacts. Wholesale costs are settled but not posted to an
   account. The P&L is a formula, not the sum of transactions.

3. **SIM/company barrier is architectural, not functional.** The seam exists
   in code structure but the company layer has no operational independence.
   It doesn't make decisions based only on what it's allowed to see.

4. **HH smart meter data path never built.** All customers are on profile
   class shapes. No half-hourly consumption data exists for any customer.
   This blocks ToU tariffs, demand flexibility, EV charging, solar export —
   the entire smart energy value chain.

5. **Reporting only recently added.** The operator had no visibility into
   what was happening to the business. Being fixed in Phase 5a/5b.

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

**Immediate (in progress):**
- Phase 5b: data pipeline, 4b integration, hedge effectiveness, Gist URL

**Next:**
- Add 2-3 HH smart meter residential customers with real half-hourly
  consumption data (source: public Ofgem/UKPN smart meter trial datasets
  or Open-Meteo correlated synthetic HH profiles)
- Prove the data architecture handles profile-class and HH customers
  simultaneously

**Then:**
- Event-driven customer lifecycle: acquisition, renewal, home move,
  complaint, debt, disconnection as actual events with timestamps and
  consequences
- A real ledger: money moves when a bill is raised, when wholesale is
  settled, when a hedge is marked. P&L emerges from transactions.

**Later:**
- ToU tariffs enabled by HH data
- SIM/company functional separation
- I&C accounts
- VPP/DER

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
