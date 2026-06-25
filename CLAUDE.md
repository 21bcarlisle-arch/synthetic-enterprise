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
2. NTFY Rich with what was done and what's next.
3. Proceed immediately to the next phase — do not hold for confirmation.
4. Rich redirects via NTFY if he wants a different direction.

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

**Phase 58 COMPLETE (2026-06-25):** Weather-adjusted gas consumption (HDD model) — 15 new tests (1,418 passing). `sim/weather_hdd.py` (new): `get_weather_factor(year, month, cid)` — actual/reference HDD ratio [0.3, 2.0]; UK 1991–2020 climate normals. `gas_settlement.py`: `weather_factor` param scales `daily_kwh`; field in every record. `run_phase2b.py`: resi/SME gas gets term-averaged factor; I&C process gas unchanged.
**Phase 57 COMPLETE (2026-06-25):** Year-varying bad debt (crisis surge) — 9 new tests (1,403 passing). `saas/cost_to_serve.py`: `get_bad_debt_rate(year, segment)` — 2021 resi 4%, 2022 8% (Ofgem 2.4M arrears), 2023 5%. `run_phase2b.py`: bad_debt_gbp deducted from net_margin_gbp + treasury each settlement period.
**Phase 56 COMPLETE (2026-06-25):** Gas pass-through hedge zero-locked — 5 new tests (1,394 passing). `simulation/run_phase2b.py`: pass-through gas `hf` forced to 0.0 (was 0.85). Wrong-way risk eliminated: C_IC3g had +42% gas margin 2021 (hedge windfall) and -86% 2023 (hedge loss on reversion). Cost now = spot × vol; margin = service_fee + network + policy only.

**Phase 55 COMPLETE (2026-06-25):** Ofgem MCR solvency signal — 12 new tests (1,389 passing). `saas/capital/solvency.py` (new): `compute_solvency_signal(treasury, customers)` → status OK/Watch/STRESS. MCR floor £130/dual-fuel account; Watch < 2×, STRESS < 1×. `_section_solvency_signal()` updated; formal ratio column in annual report.

**Phase 54 COMPLETE (2026-06-25):** Supplier mutualization levy — 8 new tests (1,377 passing). `simulation/policy_costs.py`: `_MUTUALIZATION_LEVY_BY_YEAR` + `get_mutualization_levy_per_mwh()`. 2021 £4.14/MWh, 2022 £10.00/MWh (Bulb SAR + BSC shortfall recovery). Applied in all 3 electricity settlement paths; policy costs table extended in annual report.

**Phase 53 COMPLETE (2026-06-25):** BSC credit cover — 14 new tests (1,369 passing). `saas/capital/bsc_credit.py` (new): `compute_daily_wholesale_exposure()`, `compute_bsc_credit_requirement()`, `compute_bsc_credit_by_year()`. Peak daily electricity wholesale cost × 1.2 buffer over 28-day window = credit cover required. Annual report section: per-year peak/cover/treasury/ratio table (2022 crisis shows £10k cover vs £28 in 2016). `extract_report_data()` pre-computes per year from all_records.

**Phase 52 COMPLETE (2026-06-25):** ToU demand response — 20 new tests (1,355 passing). `saas/demand_response.py`: peak→off-peak load shift (base 15% + EV +12% + heat_pump +8%); `make_shifted_shape_fn()` wraps shape for ToU-eligible customers; `demand_response_log` per term in run output. Watchdog: API exponential backoff (1m/2m/5m/10m), NTFY on failure. SSH auto-attach via `~/.bashrc`.

**Phase 51 COMPLETE (2026-06-24):** ToU eligibility gate broadened to smart-meter customers — 9 new tests (1,330 passing).
`saas/smart_meter_rollout.py`: `is_tou_eligible(customer)` — True if `metering=="HH"` OR `smart_meter==True`. `simulation/run_phase2b.py`: ToU gate upgraded from `is_hh_customer()` to `is_tou_eligible()`. Acquired customers with smart meters now receive peak/off-peak ToU pricing (profile-class consumption shape). Phase 5 smart tariff stack: pricing infrastructure complete.

**Phase 50 COMPLETE (2026-06-24):** Smart meter rollout model — 30 new tests (1,321 passing).
`saas/smart_meter_rollout.py` (new): `get_penetration(year, segment)`, `get_new_install_probability()`, `should_upgrade_to_hh()`. Resi 10%→75% (2016-2025), SME 5%→57%, I&C 100% (BSC P272 mandate). `saas/property_model.py`: `get_smart_meter_status(customer_id, year, segment)` — time-aware flag (static for known customers, rollout-probabilistic for acquired). `saas/customers.py`: `make_acquired_customer()` stamps `smart_meter` at acquisition year. Gates Phase 51 ToU tariff eligibility.

**Phases 48a/49 COMPLETE (2026-06-24):** Forward curve reform — 22 new tests. `tariff_engine.py`: EWMA (30-day half-life) base, dynamic term structure slope (contango/backwardation ±[8%,15%]/yr), term-length premium (2%/yr above 12 months). Rising-market I&C crisis pricing now higher for long-dated contracts.

**Active phases (43a–47b):** Company trading book (43a), customer profitability/renewal pricing (44a), VaR gas hedging (44b), revenue & margin sanity benchmarks (45a), gas spot billing (45b), risk premium recalibration elec 8%/gas 5% (45c/46a), Ofgem domestic price cap (47a), cap-aware acquisition gate (47b). Architecture Stages 2-4: discovery agent, epistemic verifier, agent protocol.
**Active phases (30a–42):** Full policy cost stack (RO/CfD/CCL/CM/FiT/GGL), gas costs, all 4 I&C types, active/passive renewal, SVT comparison, forward presets, 42-day notice, forward curve reform, gas seasonal calibration.
→ Phase completion details (30a–47b): `docs/claude/phase-history.md`
→ Earlier phase history (Phases 1–29): `CLAUDE_HISTORY.md`

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
