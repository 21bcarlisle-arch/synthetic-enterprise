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

**At every phase close — checklist (in order):**
1. Update test count, latest run figures in PROJECT_OVERVIEW.md Section 10
2. Add a build history entry in PROJECT_OVERVIEW.md Section 4 (Phase N)
3. **Check `wc -c CLAUDE.md` — hard limit is 35,000 chars.** If over, trim before committing: move completed phase details to `CLAUDE_HISTORY.md` and replace with a one-line reference. Never let phase details accumulate in CLAUDE.md.
4. Add the new phase completion block to CLAUDE.md (newest phase at the top of the "Current state" phase list).
5. Commit and push.

PROJECT_OVERVIEW.md is a project state document — it must be updated at phase close, not at run complete. The run-complete pipeline (which updates ANNUAL_REPORT.md and LATEST.md) does NOT update PROJECT_OVERVIEW.md.

---

## Current state (as of 22 June 2026 — 10:00 UTC)

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

**1,195+ tests passing (non-integration, SIM_FAST_MODE=1). Phase 40c adds 8 (excl. fast_run), Phase 40b adds 7, Phase 40a adds 9, fixes 2 stale CCL/CM tests. Phase 39a adds 18, Phase 38a adds 12, Phase 37a adds 7, Phase 36a adds 9, Phase 35b adds 9, Phase 35a adds 16, Phase 34a adds 9.**

**Key financial position (latest 10-year run, 61e5b3f, Phase 13a-13e active):**
- Treasury: £29,846 → £15,683 (£-14,163 net change)
- Gross margin: £-2,538 | Net margin: £-3,766 (ledger)
- Enterprise value: £-16,445
- Retention ROI: +£0.75 (2 offers made, both retained; 6 no-offer churns)
- 2021 churn divergence: 2.79× mean (down from 4.09× in c7aa449)
- C6 2024 company_est: 0.14 (Phase 13c: up from 0.00; below 0.30 threshold → no offer)
- *Pre-Phase-11a baseline (d7d3185): net margin +£13,958 with SIM-internal pricing*

**Phase 40c COMPLETE (2026-06-22)**: Deemed rate for out-of-contract I&C customers. 8 new tests.
- `saas/customers.py`: `C_IC1` and `C_IC2` get `deemed_gap_days: 30` — 30-day out-of-contract window on each renewal.
- `simulation/renewals.py`: `build_renewal_schedule()` gets `deemed_gap_days` param. Inserts `tariff_type: "deemed"` gap terms between fixed terms. Gap terms carry `deemed_premium: 0.20`, no locked unit_rate. Added `DEEMED_PREMIUM = 0.20` constant.
- `simulation/hedged_settlement.py`: `run_deemed_term()` — settles out-of-contract periods at spot × (1 + premium). No hedge fraction, no capital cost.
- `simulation/run_phase2b.py`: dispatches to `run_deemed_term()` for deemed terms. Skips risk assessment and churn estimation for deemed periods.

**Phase 40b COMPLETE (2026-06-22)**: Gas pass-through leg + tariff type in annual report. 7 new tests.
- `saas/customers.py`: `C_IC3g` — 5 GWh industrial gas, Teesside, `tariff_type: "pass_through"`.
- `simulation/run_phase2b.py`: `_build_gas_renewal_schedule()` gets `tariff_type` param. Pass-through: locked unit_rate = wholesale+margin only. Term dict stores `tariff_type`.
- `simulation/gas_settlement.py`: `run_gas_term()` gets `pass_through=False` param. When True: `revenue_gbp` includes actual gas_policy + gas_network costs passed through. Net margin = wholesale spread only.
- `saas/reporting/annual_report.py`: `_section_customer_pnl_ranking()` now shows a Tariff column, looking up `tariff_type` from customer definitions.

**Phase 40a COMPLETE (2026-06-22)**: I&C pass-through tariff. 9 new tests + 2 stale test fixes.
- `saas/customers.py`: `C_IC3` — 4 GWh chemical plant, Teesside, `tariff_type: "pass_through"`.
- `sim/hh_data/C_IC3.csv`: continuous-process HH profile (flat 24/7, 4.005 GWh/year, 3,446 rows).
- `simulation/renewals.py`: `build_renewal_schedule()` gets `tariff_type` param. Pass-through: `unit_rate = wholesale + margin` only (no locked policy/network). Term dict stores `tariff_type`.
- `simulation/hedged_settlement.py`: `run_hedged_term()` gets `pass_through=False` param. When True: `revenue_gbp` includes actual policy + network costs passed through. `net_margin_gbp` unchanged by cancellation — company bears only wholesale spread risk.
- `simulation/run_phase2b.py`: reads `tariff_type` from customer, passes to `build_renewal_schedule()` and `run_hedged_term()`.
- Fixed stale `test_ccl_included_in_policy_cost` and `test_cm_levy_included_in_policy_cost` — both missed FiT levy added in Phase 31a.

**Phase 39a COMPLETE (2026-06-22)**: SVT comparative pricing for passive renewers. 18 new tests.
- `simulation/svt_rates.py`: Ofgem Default Tariff Cap electricity rates 2016–2029 (£/MWh). `get_svt_elec_rate_gbp_per_mwh(date_str)` looks up the applicable quarterly period.
- `simulation/run_phase2b.py`: `_build_churn_basis_risk()` helper; adds `unit_rate_gbp_per_mwh`, `svt_rate_gbp_per_mwh`, `rate_vs_svt_pct` to every `churn_basis_risk` record.
- `saas/reporting/annual_report.py`: `_section_svt_comparison()` — per-year table of passive renewers' fixed rate vs SVT; flags at-risk (above SVT) and protected (below SVT) cohorts.
- 1,127 non-integration tests passing

**Phase 38a COMPLETE (2026-06-22)**: Scenario comparison runner. 12 new tests.
- `simulation/scenario_comparison.py`: `run_scenario_comparison(scenarios, year_from, year_to, seed)` — runs all 5 (or selected) scenarios sequentially, returns sorted KPI list.
- `extract_scenario_kpis(result, scenario_name)`: extracts net margin, treasury, churn, retention from a run result (unit-testable).
- `format_comparison_table(comparison)`: markdown table showing all scenarios side-by-side — summary + year-by-year net margin.
- 1,109 non-integration tests passing

**Phase 37a COMPLETE (2026-06-22)**: Forward scenario metadata banner in annual report. 7 new tests.
- `saas/reporting/annual_report.py`: `_section_scenario_metadata(data)` — prominent banner when `scenario_name` is set. Shows scenario preset name, synthetic year range, FORWARD SCENARIO warning, and key price distribution parameters (upper/lower mode, negative day frequency, dunkelflaute). Silent for standard historical runs.
- Wired into `generate_annual_report()` before executive summary.
- 1,097 non-integration tests passing

**Phase 36a COMPLETE (2026-06-22)**: Scenario integration runner. 9 new tests.
- `simulation/run_scenario.py`: `run_forward_scenario(scenario, year_from, year_to, seed)` — runs full 2016-year_to sim using historical + synthetic scenario prices.
- `build_extended_price_feeds()`: appends scenario electricity (expanded to half-hourly) + gas records to historical feeds.
- Monkey-patches `get_cached_prices` and `load_nbp_history` so `main()` sees the extended records transparently.
- 1,090 non-integration tests passing

**Phase 35b COMPLETE (2026-06-22)**: Gas forward scenario generator. 9 new tests.
- `sim/scenario/gas_scenario_generator.py`: `generate_gas_scenario_prices(year_from, year_to, scenario, seed)` — regime-conditioned gas NBP prices, correlated with electricity scenario.
- 5 matching scenario presets: `baseline_2025`, `central_2027`, `stress_dunkelflaute_2027`, `low_renewables_2027`, `battery_saturation_2029`.
- Upper regime (gas-marginal): £28-38/MWh. Lower regime (renewable-rich): £18-26/MWh. Dunkelflaute: 1.3-2.0× gas price premium. Floor: £5/MWh (gas doesn't go negative).
- 1,081 non-integration tests passing

**Phase 35a COMPLETE (2026-06-22)**: Bimodal electricity forward scenario price generator. 16 new tests.
- `sim/scenario/bimodal_generator.py`: `generate_scenario_prices(year_from, year_to, scenario, seed)` — drop-in replacement for historical price feed, produces synthetic 2026-2030 records.
- 5 named scenario presets: `baseline_2025`, `central_2027`, `stress_dunkelflaute_2027`, `low_renewables_2027`, `battery_saturation_2029`.
- Two-regime Markov model: lower mode £38-60/MWh (renewable-rich) ↔ upper mode £100-130/MWh (gas-marginal). Negative price injection (7-28 days/year, floor −£75). Dunkelflaute overlays (2-10 events/year, 1-3+ days, 1.6-2.5× price premium). Calibrated to R&D findings.

**Phase 34a COMPLETE (2026-06-22)**: 42-day renewal notice period. 9 new tests.
- `simulation/renewals.py`: `NOTICE_DAYS = 42`. `company_fwd` now uses `notice_date = term_start - 42 days` as delivery_date for `get_forward_price`. `notice_date` stored in term dict.
- `simulation/run_phase2b.py`: Gas schedules apply same notice period. `gas_notice_date` stored in schedule dict.
- Effect in crisis: company priced tariff using pre-spike data → amplified basis risk. SIM sim_fwd unchanged (knows real market at term_start).

**Phase 33b COMPLETE (2026-06-22)**: Active/passive split in annual report. 6 new tests.
- `saas/reporting/annual_report.py`: `_section_active_passive_renewal(data)` — shows total active/passive counts, mean company estimates and abs errors for each type, year-by-year table. Silent when `churn_basis_risk` lacks `is_active_renewal` (pre-Phase-33a runs). Backward compatible.
- 1,047 non-integration tests passing

**Phase 33a COMPLETE (2026-06-22)**: Active/passive renewal split — company's churn model now distinguishes SVT-rollers (65%, passive) from active fixed-term choosers (35%). 10 new tests.
- `company/crm/churn_model.py`: `PASSIVE_BASE_CHURN_RATE=0.05`, `PASSIVE_RATE_SENSITIVITY=0.1`, `PASSIVE_CHURN_CAP=0.10`. `estimate_passive_churn_probability()` — very low sensitivity to rate changes; capped at 10%. `is_active_renewal(term_start_str, seed)` — 35% active, 65% passive; 2022 forced passive (no fixed deals available in UK crisis). `CRISIS_PASSIVE_YEARS={"2022"}`.
- `simulation/customer_events.py`: `passive_churn_cap` param on `roll_lifecycle_event()` — caps SIM ground-truth churn probability for passive renewers before retention modifier.
- `simulation/run_phase2b.py`: draws `is_active_renewal` at each electricity renewal; passive renewers use `estimate_passive_churn_probability`; I&C always active (brokers shop every renewal). `passive_churn_cap=PASSIVE_CHURN_CAP` passed to lifecycle roll. `is_active_renewal` field in `churn_basis_risk` output.
- Effect: passive renewers (65%) estimated at ~5% churn rather than 10-40% → fewer spurious retention offers; SIM ground-truth churn capped at 10% for passive renewers. Crisis 2022: all renewals forced passive.
- 1,041 non-integration tests passing

**Phase 32a COMPLETE (2026-06-22)**: Gas book year-by-year P&L section in annual report. 11 new tests.
- `saas/reporting/annual_report.py`: `_section_gas_pl(data)` — 8-column markdown table: Year | Revenue | Wholesale | Gross | Policy | Network | Capital | Net | Net%. Silent when no gas records. Shows totals row + net-sign summary line.
- `commodity_split` loop now includes `revenue_gbp` and `wholesale_cost_gbp` per commodity (electricity + gas) in addition to existing gross/capital/net fields.
- Research: `docs/market_research/svt_rates_active_passive_2016_2025.md` — SVT unit rates 2016–2025, active/passive renewal split (~35/65), crisis period dynamics. Phase 33 candidate identified.
- 1,031 non-integration tests passing

**Phase 30b COMPLETE (2026-06-22)**: Gas-side policy costs — gas CCL, gas network charges, Green Gas Levy (GGL). 33 new tests.
- `simulation/policy_costs.py`: `_GAS_CCL_RATE_BY_YEAR` (£1.95–7.75/MWh, 2016–2024); resi exempt; 2019 jump from Budget 2016 rebalancing. `_GAS_NETWORK_COST_BY_YEAR` (£9.0–17.6/MWh, all segments). `_GGL_RATE_GBP_PER_METER_YEAR` (per-MPRN, normalised to £/MWh via AQ; 0 before Nov 2021)
- `simulation/gas_settlement.py`: `gas_ccl_gbp`, `ggl_gbp`, `gas_policy_cost_gbp`, `gas_network_cost_gbp` per settlement record; `net_margin_gbp` deducts policy + network from gross margin
- `simulation/run_phase2b.py`: gas renewal tariff now includes CCL + GGL (policy) + gas network pass-through
- `saas/reporting/annual_report.py`: `_section_gas_policy_costs()` — year-by-year gas policy cost breakdown (backward compatible)
- Research: `docs/market_research/gas_policy_costs_2016_2024.md`
- All current gas customers (C1g–C4g) are resi → gas CCL = 0; gas network (£9-18/MWh) and GGL (tiny, £0.03-0.18/MWh) apply
- 981 non-integration tests passing

**Phase 31a COMPLETE (2026-06-22)**: Feed-in Tariff (FiT) levy in policy cost stack. 20 new tests.
- `simulation/policy_costs.py`: `_FIT_LEVY_BY_YEAR` (£4.10–8.47/MWh, 2016–2024) + `get_fit_levy_per_mwh()` — Apr-Mar OY, same as RO/CM
- Source: npower reconciled rates 2021-2024 (high confidence); Ofgem FiT Annual Reports 2019-2020 (medium); triangulated 2016-2018 (low-medium)
- `simulation/hedged_settlement.py`: `fit_levy_gbp` per period; `policy_cost_gbp = RO + CfD + CCL + CM + FiT`
- `simulation/renewals.py`: FiT included in tariff unit rate pass-through — no double-count risk
- `saas/reporting/annual_report.py`: 6-column policy costs table when FiT present; `elif has_cm` for 5-col backward compat
- FiT applies to ALL demand (no domestic exemption) — unlike CCL; key 2021 dip: £6.01/MWh (lower tariffs on newer post-2016 installs)
- Research: `docs/market_research/fit_levy_2016_2024.md`
- 943 non-integration tests passing

**Phase 30a COMPLETE (2026-06-22)**: Capacity Market (CM) levy in policy cost stack. 16 new tests.
- `simulation/policy_costs.py`: `_CM_LEVY_BY_YEAR` (£0.5–7.27/MWh, 2016–2024) + `get_cm_levy_per_mwh()` — Ofgem Annex 9 v1.8 authoritative for 2017-2024
- `simulation/hedged_settlement.py`: `cm_levy_gbp` per period; `policy_cost_gbp = RO + CfD + CCL + CM` (Phase 30a adds CM)
- `simulation/renewals.py`: CM levy included in tariff unit rate pass-through — no double-count risk
- `saas/reporting/annual_report.py`: `_section_policy_costs()` shows 5-column table when CM data present (backward compatible)
- CM applies to ALL demand (no domestic exemption); key data: 2021 £4.67/MWh (cheap 2017 T-4 auction), 2024 £7.27/MWh
- Research: `docs/market_research/capacity_market_levy_2016_2024.md`
- 923 non-integration tests passing

For phase completion history (Phases 12–29), see [CLAUDE_HISTORY.md](CLAUDE_HISTORY.md).

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

For original phase plan and build history, see [CLAUDE_HISTORY.md](CLAUDE_HISTORY.md).

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

**DONE (Phase 40c):**
- ~~Deemed rate~~ — COMPLETE (40c). C_IC1/C_IC2 have 30-day deemed gaps on renewal.

**Immediate (Phase 41a):**
- Flex/trading tariff: reference price mechanism (day-ahead index); customer calls volumes in tranches. Requires a trading desk lifecycle.

**DONE (Phase 40b):**
- ~~Gas pass-through leg~~ — COMPLETE (40b). C_IC3g added; tariff type in annual report.

**DONE (Phase 40a):**
- ~~I&C pass-through tariff~~ — COMPLETE (40a). C_IC3 added; mechanics in renewals + settlement.

**DONE (Phase 13a–13d):**
- ~~ToU tariffs for HH customers (C7-C9)~~ — COMPLETE (13a/13b).
- ~~Retention threshold analysis~~ — Resolved by Phase 13c.
- ~~Seasonal tariff engine~~ — COMPLETE (13d). Winter +8%, Summer -4% for electricity.

**Then:**
- SIM/company full operational independence: company runs on its own models
  end-to-end; divergence from SIM ground truth accumulates and is measured
- Fresh full sim run to get updated 10-year figures with all Phase 34a–40a changes active

**Later:**
- VPP/DER
- Complaint, debt, disconnection as events
- Real forward hedging (company decides hedge fraction, not SIM agent)

Investor thesis and long-horizon vision: see [CLAUDE_HISTORY.md](CLAUDE_HISTORY.md).

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
- **CLAUDE.md has a 35k char hard limit.** Completed phase details must be
  moved to `CLAUDE_HISTORY.md` at phase close — never accumulated in CLAUDE.md.
  If CLAUDE.md exceeds 35k, stop and trim before doing anything else.
  Run `wc -c CLAUDE.md` to check. Phase close checklist enforces this.
