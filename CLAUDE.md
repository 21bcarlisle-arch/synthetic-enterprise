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
**Phase 83 COMPLETE (2026-06-26):** Portal payment submission -- 12 new tests (1,708 passing). `POST /account/{id}/pay`: accepts invoice_number+amount from bills page, calls reconcile_payment(), returns payment_confirm.html (paid/partially_paid/no_match). `bills.html`: Pay button on unpaid rows. Customer journey complete: login→dashboard→bills→pay→confirmation.
**Phase 82 COMPLETE (2026-06-26):** HH consumption feed + portal half-hourly view -- 13 new tests (1,696 passing). `simulation/publish_consumption_data.py` (new): reads sim/hh_data/{C7,C8,C9}.csv, writes 288-record JSON feed (2 days × 48 periods × 3 customers). `company/billing/hh_consumption.py` (new): get_hh_consumption() + recent_hh_periods() reads feed. Portal consumption route: HH customers see live half-hourly table (last 24h). process_run_complete.py: calls publish_consumption() after each sim run.
**Phase 77 COMPLETE (2026-06-26):** Portal Phase 2: Tariff Comparison -- 17 new tests (1,639 passing). company/pricing/tariff_comparison.py (new): unit_rate_from_forward(), annual_cost_gbp(), compare_tariffs() (3 options: Fixed 1yr/2yr/Variable SVT, sorted by est. annual cost, segment-aware VAT+SC). Portal: GET /account/{id}/tariff-compare + POST /account/{id}/switch-tariff (generates reference, renders confirm page). templates: tariff_compare.html + tariff_switch_confirm.html.
**Phase 76 COMPLETE (2026-06-26):** M3 Market Data Feed -- 10 new tests (1,622 passing). company/market/price_feed.py (new): PriceFeed class reads published JSON feed file (no SIM module imports), SpotPrice dataclass, get_latest_spot(), get_forward_price_estimate() (mean + risk premium), is_stale() (configurable max age), summary(); publish_feed() for SIM pipeline to write feed. M3 closed -- all Destinationvision gaps now closed.
**Phase 75 COMPLETE (2026-06-26):** M1 Elexon Settlement Interface -- 10 new tests (1,612 passing). company/market/settlement_reconciler.py (new): SettlementStatement dataclass, receive_settlement(), reconcile_against_bill() (imbalance = billed - settled, flagged if >5% or >£10), reconcile_period_batch() (batch reconciliation with counts), imbalance_summary() (favourable/unfavourable/flagged/net_position). M1 closed.
**Phase 74 COMPLETE (2026-06-26):** M2 Regulatory Reporting -- 13 new tests (1,602 passing). company/regulatory/compliance.py (new): smart_meter_target(year, segment), smart_meter_compliance_status() COMPLIANT/AT_RISK/BREACH (Ofgem SMETS2 mandate), check_price_cap_compliance() (SLC breach detection), generate_css_filing(service_log, year) (annual CSS return: complaints, resolution rate, vulnerable contacts), annual_turnover_fee(). M2 closed.
**Phase 73 COMPLETE (2026-06-26):** T1 Trading Desk Interface -- 7 new tests (1,589 passing). company/portal/app.py: GET /trading route + _load_trading_data() reads hedge_effectiveness from run_output_latest.json; templates/trading.html: hedge portfolio summary, best/worst decisions, P&L by year table. T1 closed -- trading desk view live on portal.
**Phase 72 COMPLETE (2026-06-25):** T2 Position Management -- 10 new tests (1,582 passing). company/trading/forward_book.py: HedgeAmendment + PositionClosure dataclasses; amend_hedge() records old->new fraction with dated audit trail; close_position() records realised P&L (close_price-agreed)*notional; closed_contracts(), amendments(), closures() accessors. open_contracts() now excludes closed; portfolio_mtm() likewise. T2 closed.
**Phase 71 COMPLETE (2026-06-25):** T3 Mark-to-Market Valuation -- 10 new tests (1,572 passing). company/trading/forward_book.py: mark_to_market(contract, current_price) -> {mtm_pnl_gbp, in_the_money, ...}, portfolio_mtm(current_prices_by_customer) -> {total_mtm_pnl_gbp, positions_priced, in/out counts, positions[]}. MTM = (market - agreed) x notional_mwh. Skips positions with no current price. T3 closed.
**Phase 70 COMPLETE (2026-06-25):** FI3 Treasury Management -- 12 new tests (1,562 passing). company/finance/treasury.py (new): working_capital(balance_sheet), cash_flow_by_year(pack), annual_cash_changes(pack), project_treasury(pack, base_year, horizon=3) -- 3-yr trend extrapolation, treasury_health(pack, year, customer_count) -- MCR headroom + OK/WATCH/CRITICAL status. Uses management accounts balance sheets only. FI3 closed.
**Phase 69 COMPLETE (2026-06-25):** C4 CRM Service Interaction Log -- 12 new tests (1,550 passing). company/crm/service_log.py (new): ServiceEvent dataclass (channel/reason/outcome/agent_type/complaint_flag/vulnerability_flag), ServiceLog with record_contact(), contacts_for_customer(), complaints(), complaint_rate(), complaint_stats(year), vulnerability_register(), resolve_vulnerability(), as_dicts(). CRM moves from lifecycle-only to full service history. C4 closed.
**Phase 68 COMPLETE (2026-06-25):** C2 Customer Portal MVP -- 14 new tests (1,538 passing). company/portal/app.py (new): FastAPI app with routes GET /, POST /login (account number auth), GET /account/{id} (dashboard), GET /account/{id}/bills (invoice list). Jinja2 HTML templates (login/dashboard/bills). Reads company layer only: saas/customers.py + invoice DB. Rich can now log in as C1 and see account profile, billing summary, and invoice history. C2 closed.
**Phase 67 COMPLETE (2026-06-25):** C3 Payment Processing + Debt Aging -- 10 new tests (1,524 passing). company/billing/payments.py (new): reconcile_payment() by customer_id+billing_period_end (paid/partially_paid/no_match), reconcile_payments() batch counts, age_debt() bad_debt after 90 days, debt_aging_summary() four aging buckets. Billing lifecycle complete: bill->invoice->payment->reconciliation->bad_debt. C3 closed.
**Phase 66 COMPLETE (2026-06-25):** C1 Invoice Line Items + Text Format -- 9 new tests (1,514 passing). company/billing/invoice.py: schema extended with commodity_amount_gbp/non_commodity_amount_gbp columns; create_invoice() uses bill line items (standing charge, non-commodity, VAT) directly; format_invoice_text() renders structured text invoice with energy/levies/standing/VAT/total. C1 line-item invoice documents now working.
**Phase 65 COMPLETE (2026-06-25):** FI2 Budget vs Actual -- 12 new tests (1,505 passing). company/finance/budget.py (new): _BUDGET_BY_YEAR (2016-2025, prior-year-actuals * 1.10 revenue / * 1.05 opex), variance_report(), monthly_variance(), traffic_light() (GREEN/AMBER/RED). Annual report: _section_budget_vs_actual() 10-year RAG table. 2021 AMBER (-13.7%), 2022 RED (+18.3%), 2023 RED (-21.1%). FI2 closed.
**Phase 64 COMPLETE (2026-06-25):** FI1 Management Accounts -- 13 new tests (1,493 passing). company/finance/management_accounts.py (new): build_monthly_accounts(), annual_management_pack(), cross_check(). Annual report _section_management_accounts(): 10-year P&L table (Revenue/COGS/Gross/OpEx/Net/Cash/Equity all from account codes 4xxx/5xxx/6xxx), cross-check vs simulation net (<=5% variance), final-year balance sheet with A=L+E. FI1 closed.
**Phase 63 COMPLETE (2026-06-25):** F1 Double-entry ledger — 24 new tests (1,480 passing). `company/finance/double_entry.py` (new): chart of accounts (13 codes, 1xxx–6xxx), `to_journal_entry()` for all 9 ledger event types, `trial_balance()`, `income_statement()`, `balance_sheet()`. P&L and balance sheet now emerge from accounts; Assets = Liabilities + Equity verified. Foundation for FI1 management accounts and C1 invoices. (Destinationvision.md F1)
**Phase 62 COMPLETE (2026-06-25):** Standing charges (electricity + gas, resi/SME) -- 12 new tests (1,456 passing). simulation/policy_costs.py: get_electricity_standing_charge_per_day() and get_gas_standing_charge_per_day(), year-indexed Ofgem tariff tracker data 2016-2024. Resi elec 24p/day->61p/day, gas 22p->31p; SME 1.5x multiplier; I&C=0. hedged_settlement.py: SC prorated per half-hour period, added to revenue+margin, standing_charge_gbp field. gas_settlement.py: daily SC in gas_standing_charge_gbp field.
**Phase 61 COMPLETE (2026-06-25):** Flex tariff policy pass-through fix — 8 new tests (1,444 passing). `run_flex_term()` in `hedged_settlement.py`: revenue now includes policy+network recovery (pass-through to customer). Prior: supplier absorbed all policy costs, creating £175k/yr artificial losses for C_IC4. Net = markup x volume only; C_IC4 total net swings from -£1.06M to +£33k.
**Phase 60 COMPLETE (2026-06-25):** I&C gas flat seasonal profile — 8 new tests (1,436 passing). `GAS_IC_CONSUMPTION_MONTHLY_PROFILE` in `gas_settlement.py`: Jan=1.075, Jul=0.913, 1.18× ratio. `run_gas_term()` selects resi vs I&C profile by `segment`. Prior: resi 5.3× swing on 5M kWh I&C = £1k/day distortion.
**Phase 59 COMPLETE (2026-06-25):** Monthly gas consumption seasonality — 10 new tests (1,428 passing).. `simulation/gas_settlement.py`: `GAS_CONSUMPTION_MONTHLY_PROFILE` (Jan=1.884, Jul=0.353, 5.3× ratio). Per-day `daily_kwh = AQ/365 × seasonal × weather`. Prior model: flat AQ/365 every day.
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
