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

**Phase 81 COMPLETE (2026-06-26):** Trading desk: live spot prices from M3 feed -- 8 new tests (1,683 passing). company/portal/app.py: _load_spot_prices() reads PriceFeed, returns elec/gas spot + forward estimates. Trading route passes spot to template. trading.html: Market Data Feed section with spot/forward prices; stale warning. M3 end-to-end loop complete: SIM writes → feed file → company reads → trading desk displays.
**Phase 80 COMPLETE (2026-06-26):** M3 price feed live: publish on every sim run -- 11 new tests (1,675 passing). simulation/publish_market_feed.py (new): build_feed_prices() (last 48 SSP HH periods + 10 NBP daily prices), publish() writes to docs/market_data/price_feed.json. process_run_complete.py: calls publish() after report gen. PriceFeed.is_available() now True; latest elec spot £100.58/MWh. Phase 76 M3 gap fully closed.
**Phase 79 COMPLETE (2026-06-26):** Portal consumption history page -- 11 new tests (1,664 passing). company/billing/consumption.py (new): consumption_history() reads kWh from invoice DB, monthly_totals() groups by year/month. Portal: GET /account/{id}/consumption, HH customers (metering=='HH') get smart meter banner. consumption.html template. Portal MVP now fully complete: all 5 Destinationvision customer views live (dashboard/bills/consumption/tariff-compare/switch).
**Phase 78 COMPLETE (2026-06-26):** Year-indexed non-commodity billing rates -- 14 new tests (1,653 passing). saas/non_commodity.py: _NON_COMMODITY_ELEC_RESI_BY_YEAR + _NON_COMMODITY_GAS_RESI_BY_YEAR (2016-2024), SME multipliers (0.77 elec / 0.80 gas), non_commodity_rate(commodity, segment, year=None) year-indexed with flat 2019 fallback. bill_generator.py: billing year extracted from dates[0], passed to non_commodity_rate. 2022 resi elec rises from £55 to £73/MWh; gas from £10 to £15/MWh. Closes Section 9 known gap.
**Phase 106 COMPLETE (2026-06-26):** CSAT admin reporting -- 7 new tests (1,946 passing). _load_admin_data() adds csat dict from _SERVICE_LOG.csat_summary(). Admin overview: 5th summary card (mean score / rated count). Closes CSAT feedback loop from portal capture to management view.
**Phase 105 COMPLETE (2026-06-26):** CSAT score tracking -- 9 new tests (1,939 passing). ServiceLog: csat_score INT column (with migration), csat_summary() (count/mean/promoter_pct), rate_contact(), latest_contact_id(). Contact portal: star rating widget on success page + POST /contact/rate. Admin: csat_summary() available for reporting.
**Phase 104 COMPLETE (2026-06-26):** Ombudsman referral tracking -- 10 new tests (1,930 passing). ServiceLog.ombudsman_eligible() + ombudsman_count(): complaints unresolved >8 weeks. admin/complaints: red alert box listing eligible cases + deadlock letter prompt. regulatory dashboard: Ombudsman section (0 = green / >0 = red alert + link).
**Phase 103 COMPLETE (2026-06-26):** Smart meter upgrade request flow -- 8 new tests (1,920 passing). GET/POST /account/{id}/smart-meter. HH customers see confirmation; non-HH get request form (contact pref + notes). POST records CRM ServiceEvent (contact_reason=smart_meter, outcome=upgrade_requested, agent_type=self_service). Dashboard: non-HH prompt with link.
**Phase 102 COMPLETE (2026-06-26):** Admin navigation hub -- 10 new tests (1,912 passing). admin.html: coloured quick-link buttons to Complaints/Collections/Renewals/Regulatory/Trading. All 22 portal routes reachable from admin in ≤2 clicks.
**Phase 101 COMPLETE (2026-06-26):** EPC energy efficiency advice -- 11 new tests (1,902 passing). company/billing/efficiency_advice.py (new): epc_advice() (7 bands A-G, tailored tips), available_schemes() (ECO4/GBIS/SEG/BUS/WHD by rating), efficiency_summary(). Dashboard: collapsible EPC advice panel with scheme list.
**Phase 100 COMPLETE (2026-06-26):** Switching recommendation engine -- 11 new tests (1,891 passing). company/pricing/switching_recommendation.py (new): synthesises contract type, renewal window, market rate delta, and price cap into action (switch/stay/consider/N/A) + urgency (high/medium/low/none) + plain-text reason. Dashboard tariff advice widget.
**Phase 99 COMPLETE (2026-06-26):** Market rate comparison widget -- 8 new tests (1,880 passing). company/market/rate_comparison.py (new): market_rate_comparison() compares PriceFeed forward estimate (£/MWh → p/kWh) vs effective contracted rate from last invoice; returns delta, protected flag, and human message. Consumption page: rate comparison widget.
**Phase 98 COMPLETE (2026-06-26):** Admin upcoming renewals -- 8 new tests (1,872 passing). GET /admin/renewals lists customers with contracts ending ≤90 days; colour-coded by urgency (≤14d red/≤30d amber/≤90d green). admin_renewals.html. Extends contract.py from Phase 95.
**Phase 97 COMPLETE (2026-06-26):** Annual cost forecast -- 8 new tests (1,864 passing). company/billing/consumption_forecast.py (new): forecast_annual_cost() uses calibrated EAC × unit_rate + SC × 365; UK seasonal quarterly split (Q1 30%/Q2 22%/Q3 18%/Q4 30%). Consumption page: estimated annual cost + quarterly breakdown.
**Phase 96 COMPLETE (2026-06-26):** Collections queue -- 10 new tests (1,856 passing). company/billing/collections.py (new): get_overdue_invoices() (unpaid/partially_paid past due), get_collections_queue() (per-customer aggregation, sorted by severity), _aging_tier() (0-30/30-60/60-90/90+ days). GET /admin/collections + admin_collections.html.
**Phase 95 COMPLETE (2026-06-26):** Contract renewal countdown -- 11 new tests (1,846 passing). company/billing/contract.py (new): contract_end_date() advances acquisition date by N-year steps (fixed_1yr/2yr), days_until_renewal(), is_in_notice_window(), renewal_summary(). Dashboard: renewal date + days countdown; notice window CTA → tariff compare.
**Phase 94 COMPLETE (2026-06-26):** Complaint deadline tracker -- 10 new tests (1,835 passing). _add_working_days() helper; ServiceLog.complaint_deadlines(): ack-by (2 working days) + resolve-by (8 weeks) per complaint, overdue flags. GET /admin/complaints + admin_complaints.html.
**Phase 93 COMPLETE (2026-06-26):** Warm Home Discount (WHD) -- 11 new tests (1,825 passing). company/regulatory/warm_home_discount.py (new): WHD_REBATE_BY_YEAR 2017-2025, whd_eligible_customers() from vulnerability_register(), compute_whd_liability(), whd_summary(). Regulatory page WHD section; dashboard vulnerability badge.
**Phase 92 COMPLETE (2026-06-26):** Peak/off-peak band overlay on HH consumption -- 10 new tests (1,814 passing). _tou_band(date, hour): weekends always off-peak; weekdays peak 07:00-19:00. consumption route enriches hh_data with band field + is_tou flag. consumption.html: Band column, colour-coded rows, Peak/Off-Peak legend. Destinationvision C7 test now met.
**Phase 91 COMPLETE (2026-06-26):** CSS filing wired to persistent ServiceLog -- 9 new tests (1,804 passing). _load_regulatory_data() calls generate_css_filing(_SERVICE_LOG.as_dicts(), current_year); regulatory.html: CSS Annual Filing table (contacts/complaints/resolution rate/target met/vulnerable). CSS year = datetime.now().year not simulation latest_year.
**Phase 90 COMPLETE (2026-06-26):** Contact Us portal form -- 11 new tests (1,795 passing). GET/POST /account/{id}/contact: reason dropdown (billing/payment/smart_meter/switch/complaint/general), notes textarea, formal complaint checkbox. ServiceEvent recorded in persistent _SERVICE_LOG on submit. contact.html (new). Dashboard Contact Us link.
**Phase 89 COMPLETE (2026-06-26):** ServiceLog SQLite persistence -- 8 new tests (1,784 passing). company/crm/service_log.py rewritten: ServiceLog(db_path=None) uses in-memory SQLite; ServiceLog(db_path=...) persists to file. All 12 existing CRM tests pass unchanged. Events, complaint stats, vulnerability register survive reconnect.
→ Phases 55–88 completion details: `docs/claude/phase-history.md`

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
