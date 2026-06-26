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

**Phase 247 COMPLETE (2026-06-26):** Power Purchase Agreement (PPA) book -- 11 new tests (3,275 passing). company/market/ppa_book.py (new): PPATechnology (5: ONSHORE_WIND/OFFSHORE_WIND/SOLAR/HYDRO/BIOMASS), PPAPricingType (FIXED/INDEXED/FLOOR), PPAContract (frozen: capacity_mw/annual_generation_mwh/price_gbp_per_mwh; term_years/annual_cost_gbp/is_active/effective_price/vs_market_gbp), PPABook (add_contract/active_contracts/total_contracted_mwh/total_annual_cost_gbp/total_vs_market_gbp/ppa_summary). FLOOR pricing tracks market when above floor; fixed-price PPAs at £45/MWh were enormously valuable in 2022 (spot £200+/MWh).
**Phase 246 COMPLETE (2026-06-26):** Gas seasonal storage book -- 9 new tests (3,264 passing). company/market/gas_storage.py (new): StorageFacility (5: ROUGH 3,300 mcm mothballed May 2017 / STUBLACH / HOLFORD / HUMBLY_GROVE / HORNSEA), StorageOperation (INJECT/WITHDRAW), StorageTransaction (frozen: volume_mcm/price_gbp_per_therm/cost_gbp/is_winter_operation), GasStorageBook (inject/withdraw/inventory_mcm/total_injected_mcm/net_storage_cost_gbp/spread_gbp_per_therm/storage_summary). Rough closure cut UK seasonal capacity 70%; key cause of 2021-22 crisis exposure.
**Phase 245 COMPLETE (2026-06-26):** Capacity Market (CM) participation book -- 9 new tests (3,255 passing). company/market/capacity_market.py (new): CMUnitType (6: CCGT/OCGT/BATTERY/DSR/INTERCONNECTOR/PUMP), AuctionType (T4/T1), _CM_CLEARING_PRICE 2016-2025 (£18-£75 crisis peak), CMUnit (frozen: derated_capacity_kw), CMObligation (mutable: annual_revenue/apply_penalty/net_revenue), CapacityMarketBook (register/add_obligation/total_revenue/total_derated_kw/cm_summary). 2022 crisis: clearing price £75/kW vs £6.44 in 2020.
**Phase 244 COMPLETE (2026-06-26):** Customer contact preferences and channel management -- 9 new tests (3,246 passing). company/crm/contact_journey.py (new): ContactChannel (6: EMAIL/SMS/POST/PHONE/IN_APP/WEB), ContactPurpose (7: BILL/TARIFF_CHANGE/MARKETING/DEBT_CHASE/RENEWAL/SERVICE_UPDATE/COMPLAINT_UPDATE), ContactOutcome (7), _CHANNEL_COST_PENCE (email 0.2p / SMS 4p / post 80p / phone 350p), CustomerContactPrefs (frozen: paper_free_discount_eligible), ContactAttempt (frozen: was_successful), ContactJourney (log_attempt/delivery_rate_pct/total_contact_cost/opted_out_customers).
**Phase 243 COMPLETE (2026-06-26):** Fuel poverty vulnerability index -- 9 new tests (3,237 passing). company/crm/vulnerability_index.py (new): VulnerabilityBand (LOW/MEDIUM/HIGH/CRITICAL at 0/15/35/60), FuelPovertyIndicator (6: BENEFITS/DISABILITY/CHILD/ELDERLY_75/CANCER/HOME_OXYGEN; scores 10-60), VulnerabilityAssessment (frozen: indicator_score + arrears_score + fuel_poverty_score + ppm_score = total; band/is_priority_services/disconnection_protected), assess_vulnerability() factory. HOME_OXYGEN=60 → always CRITICAL. Connects to PPMBook (Ph145) and credit_scoring (Ph135).
**Phase 242 COMPLETE (2026-06-26):** Metering services contracts (MOP/DC) -- 8 new tests (3,228 passing). company/market/metering_contracts.py (new): MeteringServiceType (MOP/DC/DA/MAM), MeterType (CREDIT/PPM/SMART/HH), ServiceCallType (6), _MOP_RATE (£18-£45/meter/yr by type), _DC_RATE (£12-£30/meter/yr), MeteringContract (frozen: annual_cost/is_active/cost_for_period), ServiceCall (frozen), MeteringContractManager (register/log_service_call/active_contracts/annual_contract_cost/service_call_cost/metering_summary). HH meters cost 3× credit for MOP services.

→ Phases 1–245: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`
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
