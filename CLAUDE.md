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

## Current state (as of 21 June 2026 — 14:00 UTC)

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
- ToU tariffs (Phase 13a): C7-C9 HH customers on time-of-use pricing;
  peak 1.5× / off-peak ~0.786×, revenue-neutral at 30/70 split; ToU
  utilization section in annual report (Phase 13b)
- Infrastructure: session-watchdog, staging-watcher, NTFY responder,
  File API, GitHub Pages status; NTFY spam fixed; token usage proxy

**696 tests passing (SIM_FAST_MODE=1 suite, ~17s).**

**Key financial position (latest 10-year run, 61e5b3f, Phase 13a-13e active):**
- Treasury: £29,846 → £15,683 (£-14,163 net change)
- Gross margin: £-2,538 | Net margin: £-3,766 (ledger)
- Enterprise value: £-16,445
- Retention ROI: +£0.75 (2 offers made, both retained; 6 no-offer churns)
- 2021 churn divergence: 2.79× mean (down from 4.09× in c7aa449)
- C6 2024 company_est: 0.14 (Phase 13c: up from 0.00; below 0.30 threshold → no offer)
- *Pre-Phase-11a baseline (d7d3185): net margin +£13,958 with SIM-internal pricing*

**Phase 17d COMPLETE (2026-06-21)**: Dual-fuel account combined P&L in annual report. 760 tests passing (4 new).
- `saas/reporting/annual_report.py`: `_section_dual_fuel_pnl()` — pairs electricity+gas legs (C1+C1g, C2+C2g, etc.) and shows combined lifetime margin
- Flags whether gas leg was accretive (positive net margin) or dilutive to each dual-fuel account
- Summary: how many dual-fuel accounts had gas net positive? Total gas net margin.
- Answers: "Did our gas offering add value to the dual-fuel customer relationship?"
- 4 new tests; fully backward-compatible

**Phase 17c COMPLETE (2026-06-21)**: Per-customer lifetime P&L ranking in annual report. 756 tests passing (4 new).
- `saas/reporting/annual_report.py`: `_section_customer_pnl_ranking()` — aggregates all_records by customer, sorts by net margin
- Shows: revenue, gross margin, capital cost, net margin, net margin % for each billing account
- Surfaces which customers created vs destroyed value over their lifetime — actionable for pricing and renewal strategy
- 4 new tests; fully backward-compatible (returns "" if no all_records)

**Phase 17b COMPLETE (2026-06-21)**: Churn avoidability analysis in annual report. 752 tests passing (5 new).
- `saas/reporting/annual_report.py`: `_section_churn_avoidability()` — joins `no_offer_churn_log` with `company_event_log` (SIM ground truth)
- Classifies each no-offer churn as: blind miss (company_est < 30%) or deliberate pass (uneconomical offer)
- Of blind misses, flags how many were "detectable" by a better model (SIM p ≥ 30% while company said < 30%)
- Shows total margin at stake per category; patient-zero question: "how much did our churn model's blind spots cost us?"
- 5 new tests; fully backward-compatible (returns "" if no no_offer_churn_log)

**Phase 17a COMPLETE (2026-06-21)**: Portfolio learning premium — company adjusts tariffs from recent portfolio-wide margin rates. 747 tests passing (9 new).
- `company/pricing/tariff_engine.py`: `compute_portfolio_premium()` — if mean recent electricity margin rates below 8% target, apply uplift at renewal (capped at +15%); over-earning triggers up to -5% discount
- `simulation/run_phase2b.py`: tracks `portfolio_elec_margin_rates` list; applies premium BEFORE Phase 16c surcharge at each electricity renewal
- `saas/reporting/annual_report.py`: `_section_dynamic_pricing()` — shows all premium/discount events
- Slower-acting than Phase 16c (portfolio-wide, 4-term lookback vs per-customer 1-term); together they form two-speed feedback system
- Expected: sustained 2021-22 crisis losses accumulate in rolling window → 2022-23 premiums of 10-15% on all renewals

**Phase 16c COMPLETE (2026-06-21)**: Realized-margin feedback into renewal tariff. 748 tests passing (8 new).
- `company/pricing/margin_feedback.py`: `compute_margin_surcharge()` — if prior term lost >5% of revenue, apply recovery surcharge (capped at 20%) at next renewal
- `simulation/run_phase2b.py`: tracks `prev_term_margin` and `prev_term_revenue` per customer; applies surcharge before settlement
- `saas/reporting/annual_report.py`: `_section_margin_feedback()` — shows all recovery surcharge events in the run
- Closes the tariff feedback loop: company observes its own losses and corrects pricing at renewal
- `margin_feedback_log` in run output: customer, term, prior margin, surcharge %, before/after rates

**Phase 16b COMPLETE (2026-06-21)**: Retention durability analysis in annual report. 740 tests passing (5 new).
- `saas/reporting/annual_report.py`: `_section_retention_durability()` — post-retention survival per customer cohort
- First retention date per customer → months survived until churn or window end
- Real data: 4/7 retained customers eventually churned, avg 60 months post-retention; 3 still active
- 2017 cohort: C2 (60mo), C6 (84mo), C8 (105mo active); 2018 cohort: C3 (24mo), C9 (90mo active), C4 (72mo)
- Shows whether retention efforts produced durable outcomes or merely delayed inevitable churn

**Phase 16a COMPLETE (2026-06-21)**: Tariff repricing impact assessment in annual report. 735 tests passing (5 new).
- `saas/reporting/annual_report.py`: `_section_repricing_impact()` — for each NET_NEGATIVE customer, estimates churn risk if tariff raised to break-even
- Uses churn model rate sensitivity: uplift % = rate_increase_pct → churn_est = base + sensitivity × uplift - tenure_discount
- Active customers: repricing opportunity; churned customers: retrospective counterfactual
- Thresholds: <40% churn est → "Raise"; 40-65% → "Partial"; >65% → "Hold"
- Real data: all 6 active loss-making customers can be repriced to B/E with <25% churn risk

**Phase 15d COMPLETE (2026-06-21)**: Hedge fraction signal in company churn model. 730 tests passing (6 new).
- `company/crm/churn_model.py`: `hedge_fraction` param + `HEDGE_SENSITIVITY_REDUCTION=0.4` constant
- `effective_rate_sensitivity = rate_sensitivity × (1 - hf × 0.4)`: hf=1.0 → 40% sensitivity reduction
- `simulation/run_phase2b.py`: passes `prev_hf = current_hf.get(cid, 0.0)` at electricity renewal time
- Reduces structural over-estimation in 2021-22: hedged customers had stable bills despite headline rate spikes
- 6 new tests (31 total in test_churn_model.py): zero/full/partial hedge quantified; crisis scenario caps verified

**Phase 15c COMPLETE (2026-06-21)**: Full economic ROI in retention section. 724 tests passing (3 new).
- `saas/reporting/annual_report.py`: adds "Acquisition cost avoided" + "Full economic ROI" rows to retention table
- Full ROI = (margin saved - offer cost) + acq_cost_saved (only shown when Phase 15b acq_cost data present)
- Example: Phase 15b run with C1+C5 2021 retained → acq saved £550, full ROI includes that vs offers-only net

**Phase 15b COMPLETE (2026-06-21)**: Acquisition-aware retention offer guard. 721 tests passing (4 new).
- `simulation/run_phase2b.py`: retention guard now `expected_margin + acq_cost_saved > ret_cost` (Phase 15b)
- Previously blocked crisis-year offers where margin < discount cost even when acq_cost_saved made offer rational
- C5 2021 (SME, £122 margin, £160 ret_cost, £400 acq): now offered. C1 2021 (resi, £14 margin): also offered
- `retention_log` entries now include `acq_cost_saved_gbp` for traceability

**Phase 15a COMPLETE (2026-06-21)**: Gas renewal pressure section in annual report. 717 tests passing (5 new).
- `saas/reporting/annual_report.py`: `_section_gas_renewal_pressure()` — consumes company_gas_churn_log from Phase 14b
- Year-by-year table: renewal count, mean/max gas company estimate, elevated risk count (>20% threshold)
- Top-5 most elevated renewals with rate change direction and estimated churn %; flags crisis years with ⚠
- Section is silent when company_gas_churn_log is absent (pre-Phase-14b runs)

**Phase 14b COMPLETE (2026-06-21)**: Gas-specific churn sensitivity. 712 tests passing (7 new).
- `company/crm/churn_model.py`: `fuel: str = "electricity"` param to `estimate_churn_probability()`
- `GAS_BASE_CHURN_RATE = 0.08`, `GAS_RATE_SENSITIVITY = 0.6` — stickier dual-fuel gas legs, fewer alternatives
- `simulation/run_phase2b.py`: tracks prev_gas_unit_rates; computes gas company churn estimate per renewal
- `company_gas_churn_log` in run output: informational gas rate pressure monitoring for dual-fuel portfolio

**Phase 14e COMPLETE (2026-06-21)**: Bill shock summary section in annual report. 705 tests passing (5 new).
- `saas/reporting/annual_report.py`: `_section_bill_shock_summary()` — aggregates per-year bill_shock_events into portfolio view
- Year-by-year table: event count + worst spike per year; total across all years
- Top-10 worst single-period spikes with date, customer, severity %, and whether they eventually churned
- 274 total bill shock events across 10 years in 61e5b3f run; worst: C2_2 2022-04-30 +1717%

**Phase 14d COMPLETE (2026-06-21)**: ToU revenue premium analysis in annual report. 700 tests passing (4 new).
- `saas/reporting/annual_report.py`: `_tou_revenue_premium()` helper computes flat-equivalent revenue from avg_peak_rate / 1.5×
- Adds "ToU Premium" column to utilization table; summary line showing total HH revenue vs flat equivalent
- C8 (43.8% peak) earns ~+10% vs flat; C9 (42.2%) ~+9%; C7 (33.6%) ~+3% (design split is 30% breakeven)
- Test: confirms premium > 0 for above-design utilization; ≈ 0% at exactly 30/70 split

**Phase 14c COMPLETE (2026-06-21)**: Adaptive lookback window in company tariff engine. 696 tests passing (7 new).
- `company/pricing/tariff_engine.py`: `_compute_adaptive_lookback()` — compares recent 30d price std vs prior 90d baseline
- High vol_ratio (crisis onset): shorten lookback (30d floor) so mean tracks current-regime prices, not stale pre-crisis data
- Low vol_ratio (calm period): extend lookback up to 180d ceiling for smoother estimates
- Falls back to base 120d when baseline std < 0.5 £/MWh (stable/sparse data)
- Crisis years (2021-22): ~40d adaptive lookback expected to reduce tariff error by 8-15 percentage points
- `adaptive_lookback: bool = True` param to `get_forward_price()` for deterministic test overrides

**Phase 14a COMPLETE (2026-06-21)**: Tiered retention offer size. 689 tests passing (4 new).
- `simulation/run_phase2b.py`: `RETENTION_TIERS` replaces flat `RETENTION_DISCOUNT_PCT=0.05`
- Tiers: ≥75% churn risk → 8% discount; 50-75% → 5%; 30-50% → 3%
- `_retention_discount_for_risk(company_est)` helper; all retention log/notify calls use variable discount
- Effect: borderline cases get lighter touch (3%), genuinely high-risk get aggressive offer (8%)
- Both c7aa449 offers (company_p=0.45) remain at 5% — no change for current run; next run (61e5b3f) may show differentiation if Phase 13c brings C6 above threshold

**Phase 13e COMPLETE (2026-06-21)**: Gas seasonal adjustment in company tariff engine. 685 tests passing (2 net new).
- `company/pricing/tariff_engine.py`: `GAS_WINTER_SEASONAL_UPLIFT=0.15`, `GAS_SUMMER_SEASONAL_DISCOUNT=0.08`
- Gas pricing now fuel-aware: winter +15%, summer -8% (vs electricity +8%/-4%)
- UK NBP spot has more pronounced heating-demand seasonality than electricity — real pricing teams would apply this shape
- `test_seasonal_does_not_apply_to_gas` replaced with 3 quantified gas seasonal tests

**Phase 13d COMPLETE (2026-06-21)**: Seasonal forward price awareness in company tariff engine. 683 tests passing (9 new).
- `company/pricing/tariff_engine.py`: `seasonal: bool = True` + `WINTER_SEASONAL_UPLIFT=0.08`, `SUMMER_SEASONAL_DISCOUNT=0.04`
- Winter delivery (Oct-Mar): +8%; summer (Apr-Sep): -4%. Gas unchanged (separate seasonality).
- Structural fix: 120-day lookback for Oct renewal captured June-Sep spot prices (low season), underestimating winter costs. Now corrected.

**Phase 13c COMPLETE (2026-06-21)**: Bill burden signal in company churn model. 674 tests passing (8 new).
- Root cause analysis: 3 "below threshold" false negatives all had company_p=0.0 because rate-% signal collapses when rates fall from crisis peaks — even for large SME customers who are financially stressed
- `company/crm/churn_model.py`: `annual_consumption_kwh` param + bill stress term. Formula: `p += 0.25 × max(0, old_rate × kwh/1000 / £3,000 − 1)`
- C6 2024: falling rate (−40%) + 45,000 kWh/year at £250/MWh → company now estimates 42% churn vs 0% before. Margin was £216.87 — economical offer now possible
- Small resi (2,800 kWh) unaffected; signal only fires for high-spend SME/HH customers

**Phase 13b COMPLETE (2026-06-21)**: ToU utilization section in annual report. 666 tests passing.

**Phase 13a COMPLETE (2026-06-21)**: Time-of-Use tariffs for C7-C9 HH customers. 666 tests passing (17 new).
- `simulation/tou_periods.py`: `is_peak_period()` and `period_start_time()` — peak = 07:00-11:00 and 16:00-20:00 weekdays (SP 15-22, 33-40)
- `saas/tariff_pricing.py`: `TOU_PEAK_MULTIPLIER=1.50`, `TOU_OFFPEAK_MULTIPLIER≈0.786`, `price_tou_tariff()`
- `simulation/hedged_settlement.py`: `tou_rates` param on `run_hedged_term()` — per-period rate in settlement records
- `simulation/run_phase2b.py`: `is_hh_customer()` check wires ToU rates for C7-C9

**Phase 12e COMPLETE (2026-06-21)**: SIM/company divergence tracking. 649 tests passing (7 new).
- `simulation/run_phase2b.py`: `_compute_company_divergence()` aggregates `basis_risk_terms` and `churn_basis_risk` by year; `company_divergence` key in run output with `tariff_error_by_year` and `churn_error_by_year`
- `saas/reporting/annual_report.py`: `_section_company_divergence()` renders year-by-year mean/max abs error tables for both models; added to report sections
- Hollow gap #3 (SIM/company barrier): company-model divergence from SIM ground truth now formally measured — not just described
- Next full sim run will show tariff pricing error by year (company 120-day rolling mean vs SIM forward curve) and churn estimate error by year

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

3. **SIM/company barrier — DIVERGENCE NOW MEASURED (Phase 12e).** Company now has its
   own tariff engine (observable forward prices only) and churn estimator
   (observable rate change + tenure). Both make consequential decisions using
   only what a real supplier could see. Phase 12e adds formal divergence tracking:
   `company_divergence` key in run output, year-by-year tariff and churn error tables
   in annual report. The company still shares code paths with SIM (not yet fully
   independent), but divergence from SIM ground truth is now measured, not assumed.
   Full operational independence is the long-horizon goal.

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

**Immediate (Phase 13e candidates):**
- SIM/company full operational independence: company runs end-to-end on its own models with no shared code paths to SIM internals; divergence accumulates and is measured by the existing `company_divergence` machinery
- Gas seasonal adjustment in company tariff engine: electricity done (Phase 13d), gas also highly seasonal but parameters differ (higher winter/summer amplitude for gas)
- I&C accounts: HH data path solid, event lifecycle solid — now feasible

**DONE (Phase 13a–13d):**
- ~~ToU tariffs for HH customers (C7-C9)~~ — COMPLETE (13a/13b).
- ~~Retention threshold analysis~~ — Resolved by Phase 13c (model accuracy was the issue, not threshold).
- ~~Seasonal tariff engine~~ — COMPLETE (13d). Winter +8%, Summer -4% for electricity.

**Then:**
- SIM/company full operational independence: company runs on its own models
  end-to-end; divergence from SIM ground truth accumulates and is measured
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
