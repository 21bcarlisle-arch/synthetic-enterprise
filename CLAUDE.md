# CLAUDE.md — Synthetic Enterprise

## What this project is

A high-fidelity simulation of a fully autonomous UK energy supply business, operating against
real Elexon/NESO half-hourly settlement data. The business layer cannot see future data
(Point-in-Time Blindfold, strictly enforced). Goal: detailed enough to say "that is how a
real UK energy supplier works."

→ Architecture, module inventory, build history: `docs/PROJECT_OVERVIEW.md`

---

## Who does what

- **Rich** — MD/board. Stages instructions in `docs/staging/`. Staging = approval. Does not write code.
- **Claude Code** — lead orchestrator. Designs, delegates, reviews, manages build.
- **qwen3:14b (Ollama)** — all code generation and mechanical execution. Frontier tokens for reasoning only.
- **Risk committee** — local Ollama only. No frontier API spend in simulation runs.

---

## How to operate autonomously

**NTFY is the primary communication channel.** Rich uses it for steering and quick direction changes.
- `background/ntfy_responder.py` writes inbound messages (>25 chars) to `docs/staging/from_rich_TIMESTAMP.md`
- After acting on a `from_rich_*.md` message, reply via `background.ntfy_utils.send_ntfy`.
- Move actioned files to `docs/staging/done/` after processing.

**At startup and after every completed task:** poll `docs/staging/` and action unread files immediately.
- `run_complete_*.md` — publish results (regenerate report, LATEST.md, dashboard.json), commit, push,
  archive. **Do NOT send NTFY for routine sim run completions.** Only NTFY for notable exceptions
  (admin event, all-time high/low margin). Batch silently if multiple queued.
- `run_pending_*.md` — check if finished and act accordingly.
- `from_rich_*.md` — action it, reply via NTFY, archive.

**At every REVIEW_GATE:**
1. Complete phase and commit all outputs.
2. NTFY Rich with results.
3. Write proposed next step as `docs/staging/drafts/NEXT_PHASE.md`.
4. NTFY: "Proposed next step in docs/staging/drafts/ — will proceed in 4 hours unless redirected."
5. Action the draft after 4 hours if no redirect arrives.

**Always update and commit LATEST.md before sending NTFY.** If stale, fix the root cause.

**When budget is available between tasks:** check backlog, fix known issues, improve coverage. Don't sit idle.

---

## Phase-close checklist (in order)

1. Update test count + latest run figures in PROJECT_OVERVIEW.md Section 10.
2. Add build history entry in PROJECT_OVERVIEW.md Section 4.
3. **Run epistemic verifier:** `python3 -m tools.epistemic_verifier` — must PASS before committing.
   If FAIL: fix violations before committing any phase-close output.
4. **`wc -c CLAUDE.md` — hard limit 35,000 chars / 200 lines.** If over: move phase details to
   `docs/claude/phase-history.md`. Never accumulate phase details in CLAUDE.md.
5. Add one-line phase completion entry to CLAUDE.md "Current state".
6. Commit and push.

PROJECT_OVERVIEW.md is updated at phase close. Run-complete pipeline does NOT update it.

---

## Current state

**Phase 46a COMPLETE (2026-06-23):** Gas risk premium further reduced 10%→5% — 0 new tests (1,250+ passing).
`company/pricing/tariff_engine.py`: `GAS_RISK_PREMIUM_FRACTION` 10%→5%. UK resi gas margins near-zero in stable
markets (competitive market dynamics; pass-through already at spot). Elec (8%) now higher than gas (5%).

**Phase 45c COMPLETE (2026-06-23):** Forward curve risk premium recalibration — 8 new tests (1,250+ passing).
`company/pricing/tariff_engine.py`: `COMPANY_RISK_PREMIUM_FRACTION` 15%→8%, `GAS_RISK_PREMIUM_FRACTION` 20%→10%.
UK I&C market benchmarks: 5-8% above NAP for electricity; original 15%/20% drove C_IC1/C_IC2 to 33% net vs 3-8%
industry benchmark. Reduces systematic forward overpricing without affecting gas pass-through (already fixed 45b).

**Phase 45b COMPLETE (2026-06-23):** Gas pass-through bills at spot, not forward — 6 new tests (1,242+ passing).
`simulation/gas_settlement.py`: pass-through customers billed at daily spot + `GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH`
(£2/MWh); eliminates artificial 19.9% I&C/gas net margin from 20% risk premium on non-risk-bearing billing.

**Phase 45a COMPLETE (2026-06-23):** Revenue & margin sanity check — 0 new tests (1,236+ passing).
`tools/revenue_sanity_check.py`: P&L waterfall + per-segment net% vs Ofgem/CMA benchmarks. Runs
post-run and in annual report. Snapshot JSON companion for strategy advisor (no-JS fetch). Anomalies
detected: I&C/gas 19.9% (gas forward bias), resi 12.2%/11.8% (CCL-exempt + forward bias).

**Phase 43a COMPLETE (2026-06-23):** Company trading book — 14 new tests (1,242+ passing).
`company/trading/forward_book.py`: `ForwardContract` + `TradingBook`. On each fixed/pass-through
term signing, company opens a forward contract (agreed_price = company_fwd, notional = EAC × hf).
`settle_period()` decomposes hedge P&L from supply margin each half-hour. `trading_book.summary()`
in run output (contract_count, total_hedged_mwh, hedge_pnl_gbp). Net margin unchanged.

**Phase 44b COMPLETE (2026-06-23):** VaR-constrained hedging extended to gas fixed terms — no new tests needed.
`simulation/run_phase2b.py`: gas else-branch now calls `decide_hedge_fraction()` for fixed gas terms.
Same VaR model (EWMA vol, 95% VaR ≤ 15% term revenue) using gas price records. Pass-through skipped.
Committee overrides still take precedence.

**Phase 44a COMPLETE (2026-06-23):** Customer profitability feedback into renewal pricing — 13 new tests (1,290+ passing).
`company/crm/customer_profitability.py`: `estimate_prior_term_net_margin()` + `compute_profitability_uplift()`.
Net-negative electricity customers receive £3/MWh uplift at renewal. Churn model handles consequence.
`saas/tariff_pricing.py`: `profitability_uplift_per_mwh` param. Run output: `profitability_uplift_log`.
Closes "Pricing actions not implemented" Known Gap.

**Phase 43b COMPLETE (2026-06-23):** VaR-constrained trading desk — 15 new tests (1,275+ passing).
`company/trading/hedge_decision.py`: `estimate_price_volatility()` (EWMA, 90-day lookback),
`decide_hedge_fraction()` (95% VaR ≤ 15% of term revenue), `compute_bid_ask_cost()` (0.5-1.5%).
`simulation/run_phase2b.py`: per-term VaR hedge decision replaces static RESET_HEDGE_FRACTION.
`saas/reporting/annual_report.py`: `_section_trading_pnl()` — hedge P&L year-by-year with bid-ask.

**Architecture Stages 2-4 COMPLETE (2026-06-23):** All four stages done.
- Stage 2: `.claude/agents/discovery-agent.md` — scoped to market_research/, structured findings.
- Stage 3: `.claude/agents/epistemic-verifier.md` + `tools/epistemic_verifier.py` — in phase-close checklist.
- Stage 4: `background/agent_protocol.py` — `AgentMessage` + `IntentType`, 18 tests, live in sim_runner.

**Tests:** 1,250+ passing (1,242 non-integration `SIM_FAST_MODE=1`, 8 integration).

**Latest run (2026-06-23, commit 467debd):** Net £678,588 | Gross £5,468,296 |
Treasury £3,145,224 | SURVIVED.

**Active phases (30a–42):** Full policy cost stack (RO, CfD, CCL, CM, FiT, GGL), gas policy
costs, all 4 I&C tariff types (fixed / pass-through / deemed / flex), active/passive renewal
split, SVT comparison, forward scenario infrastructure (5 named presets), 42-day notice period,
forward curve reform (EWMA + term structure), gas seasonal calibration.

→ Phase completion details (30a–42): `docs/claude/phase-history.md`
→ Earlier phase history (Phases 1–29): `CLAUDE_HISTORY.md`
→ Roadmap and backlog: `MASTER_BACKLOG.md`
→ Calibration notes (hedge mandate, design decisions): `docs/claude/phase-history.md`

---

## Architectural Laws

### Epistemic Honesty — The Company Cannot See Inside the SIM

The company layer operates under the same information constraints as a real energy supplier.
It cannot see simulation internals — churn parameters, forward curve construction, weather
engine outputs, VaR internals. It discovers the world through observable interfaces: market
data feeds, meter reads, customer interactions, its own bills and payments, regulatory
publications.

The company's models are approximations built from observed outcomes — not reads from ground
truth. That imperfection is the point.

**Before writing any company-layer code:** ask "Could a real UK energy supplier know this?"
If the answer requires reading simulation internals, it is a violation.

The SIM/company seam (`company/interfaces/sim_interface.py`) enforces this boundary —
exposes observables and outcomes only, never parameters or internals.

---

## Sequencing principles

**Two-way-door filter:** don't build something that depends on an unresolved upstream question.

**Build efficiency:** tests passing + capabilities added per frontier session (hard metric).
Fidelity delta — one sentence per phase on what the sim can now do (soft metric, Rich assesses).
CLV is not a stable measuring stick — it evolves with business rules.

**Reversibility** governs data architecture and agent governance. Prefer designs that can be unwound.

**Regime-change blindness** is a known failure mode. The sim converged to near-naked hedging during
calm 2016–2020 data, directly before the crisis — mirroring what killed real suppliers. All
hedging/risk models must account for this.

**Activity-based pricing:** flat margin makes some customers net-negative. Any pricing model must
account for cost-to-serve at the customer level.

---

## Key learnings — do not repeat these mistakes

- **Local models confabulate endpoints.** Pre-load ground-truth API context before any local model touches external sources.
- **LATEST.md must be committed before NTFY**, not after. If stale, fix root cause.
- **REVIEW_GATE must only match on actual pane idleness** — not on prose mentioning the string "REVIEW_GATE".
- **Staging-watcher notifies Rich, not the agent.** Poll `docs/staging/` yourself.
- **The simulation is not the company.** Company makes decisions based on what it's allowed to see.
- **Non-blocking concurrency.** If blocked on a long run, move to the next staging item and return.
- **Session usage window is ~5 hours**, not 4. Don't under-estimate available budget.
- **CLAUDE.md hard limit: 35k chars / 200 lines.** Stop and trim before anything else if exceeded.
- **Committee cooldown must be date-based**, not record-count. With 18+ customers, 1440 records ≠ 30 days.
- **sim_runner TimeoutExpired must be caught.** Uncaught exception kills the `while True` loop.

---

## Technical environment

**Hardware (Skynet):** Intel i5-13400F, 32GB DDR4, RTX 3060 12GB VRAM. Windows 11 Pro + WSL2/Ubuntu.
**Networking:** Tailscale WSL2 `100.69.81.59` | File API `https://skynet-1.taila062fa.ts.net:8765`
**AI stack:** Claude Code (orchestrator) → qwen3:14b/Ollama (code gen) → risk committee (local Ollama)
**Key paths:** `docs/staging/` (instructions) | `docs/status/LATEST.md` | `docs/reports/ANNUAL_REPORT.md`
**Data:** Elexon `data.elexon.co.uk` (key-free) | NESO CKAN | Open-Meteo | synthetic forward curves
**Elexon note:** API migrated to Insights Solution. Legacy wrappers partly stale — verify before use.
