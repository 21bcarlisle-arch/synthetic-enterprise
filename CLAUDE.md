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

**At startup and after every completed task:** check `docs/staging/` for
unactioned files and action them immediately. Do not wait to be told.

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

**252 tests passing.**

**Key financial position (latest run):**
- Treasury: £21,829.17 → £48,003.06
- Net margin: £26,173.89
- Gross margin: £44,682.49
- Capital cost ratio: 41.4%
- Risk committee interventions: 122
- Enterprise value: £17,569.06

**In progress:**
- Phase 5b: persist run output to JSON, integrate 4b outputs, hedge
  effectiveness analysis, GitHub Gist publishing for report access

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
