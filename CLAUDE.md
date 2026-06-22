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

**At every phase close, update PROJECT_OVERVIEW.md:**
- Update test count, latest run figures in Section 10
- Add a build history entry in Section 4 (Phase N)
- PROJECT_OVERVIEW.md is a project state document — it must be updated at phase close, not at run complete. The run-complete pipeline (which updates ANNUAL_REPORT.md and LATEST.md) does NOT update PROJECT_OVERVIEW.md.

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

**1,097+ tests passing (non-integration, SIM_FAST_MODE=1). Phase 37a adds 7, Phase 36a adds 9, Phase 35b adds 9, Phase 35a adds 16, Phase 34a adds 9.**

**Key financial position (latest 10-year run, 61e5b3f, Phase 13a-13e active):**
- Treasury: £29,846 → £15,683 (£-14,163 net change)
- Gross margin: £-2,538 | Net margin: £-3,766 (ledger)
- Enterprise value: £-16,445
- Retention ROI: +£0.75 (2 offers made, both retained; 6 no-offer churns)
- 2021 churn divergence: 2.79× mean (down from 4.09× in c7aa449)
- C6 2024 company_est: 0.14 (Phase 13c: up from 0.00; below 0.30 threshold → no offer)
- *Pre-Phase-11a baseline (d7d3185): net margin +£13,958 with SIM-internal pricing*

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

**Phase 29b COMPLETE (2026-06-22)**: Network charge table calibration from Ofgem Annex 9 v1.10. 0 new tests (test values updated).
- `simulation/policy_costs.py`: `_NETWORK_COST_RESI_SME_BY_YEAR` updated from Phase 29a mid-range estimates to Ofgem Annex 9 authoritative figures
- Key change: 2022 £43→£66/MWh (+35%) — BSUoS moved 100% to demand side from April 2022 (previously 50/50 demand/generator)
- 2023: £75/MWh (RIIO-ED2 commenced); 2024: £69/MWh; earlier years also corrected upward (2016: £35→£43/MWh)
- Source: Ofgem Annex 9 v1.10 June 2026, `docs/market_research/network_charges_uk_2016_2024.md`
- I&C DUoS table unchanged; 907 non-integration tests passing

**Phase 29a COMPLETE (2026-06-22)**: Network charges (DUoS + TNUoS) in settlement P&L and tariff stack. 15 new tests.
- `simulation/policy_costs.py`: `_NETWORK_COST_RESI_SME_BY_YEAR` (£35-46/MWh, 2016-2024) + `_DUOS_IC_BY_YEAR` (£11-14/MWh); `get_electricity_network_cost_per_mwh(date_str, segment="resi")`
- `simulation/hedged_settlement.py`: `network_cost_gbp` field per settlement period; `net_margin_gbp = margin_gbp - policy_cost_gbp - network_cost_gbp - capital_cost_gbp`
- `saas/tariff_pricing.py`: `network_cost_per_mwh` param on `price_fixed_tariff()` — pass-through in unit rate
- `simulation/renewals.py`: `segment` param on `build_renewal_schedule()`; I&C uses DUoS-only rate (Triad TNUoS tracked separately in triad.py to avoid double-count)
- `simulation/run_phase2b.py`: passes `segment=c.get("segment", "resi")` at both build_renewal_schedule call sites
- `saas/reporting/annual_report.py`: `network_cost_gbp` in yearly aggregation; `_section_network_costs()` backward-compatible section
- Network cost is now the largest single non-commodity cost component in the P&L stack
- 907 non-integration tests passing in 7.87s

**Phase 28a COMPLETE (2026-06-22)**: I&C portfolio summary section in annual report. 6 new tests.
- `saas/reporting/annual_report.py`: `_section_ic_portfolio()` — lifetime P&L, CCL/MWh, TNUoS Triad exposure, volume tolerance summary, and year-by-year segment comparison (I&C vs SME vs Resi)
- Identifies I&C customers from CUSTOMERS module (`segment == "I&C"`); not CCL proxy (fixed: CCL proxy also matched C5 SME)
- Pulls from `triad_log`, `volume_tolerance_log`, `segment_split` per year — no new run keys required
- Backward compatible: silent if no I&C settlement records (pre-Phase-24a runs)

**Phase 27e COMPLETE (2026-06-22)**: I&C churn model — broker-driven, price-sensitive. 6 new tests.
- `company/crm/churn_model.py`: `IC_BASE_CHURN_RATE=0.20` (vs 0.10 resi), `IC_RATE_SENSITIVITY=1.5` (vs 0.8), `IC_TENURE_DISCOUNT_PER_YEAR=0.005`, `IC_BILL_STRESS_THRESHOLD_GBP=50,000` (vs £3k)
- `estimate_churn_probability()` gains `segment="I&C"` param — I&C uses broker-driven constants
- `simulation/run_phase2b.py`: passes `segment=segment_for_churn` at electricity renewal — I&C customers now get correct churn estimates
- I&C base churn 20% (vs 10% resi) reflects broker-driven market — company must be proactive on I&C retention

**Phase 27d COMPLETE (2026-06-22)**: Triad risk for I&C electricity customers. 15 new tests.
- `simulation/triad.py`: `identify_triad_candidates()` — top-3 SSP periods (≥10 days apart, Nov-Feb Triad window) as demand proxy; `compute_triad_exposure()` — I&C demand_kw × TNUoS tariff
- `_TNUOS_TRIAD_TARIFF_BY_YEAR`: £46.23→£63.82/kW/year 2016-2024 (Zone 14 London HV connected)
- `simulation/run_phase2b.py`: after term loop, computes Triad for each winter × each I&C customer; `triad_log` in run output
- `saas/reporting/annual_report.py`: `_section_triad_exposure()` — per-winter table; cumulative exposure per I&C customer

**Phase 27c COMPLETE (2026-06-22)**: Volume tolerance tracking for I&C contracts. 12 new tests.
- `simulation/volume_tolerance.py`: `compute_term_volume_tolerance()` — actual vs contracted ±10%; excess at spot, deficit unwind P&L
- `simulation/run_phase2b.py`: I&C terms after settlement compute tolerance; `volume_tolerance_log` in run output
- `saas/reporting/annual_report.py`: `_section_volume_tolerance()` — per-term table with ⚠ flag on breach

**Phase 27b COMPLETE (2026-06-22)**: CCL (Climate Change Levy) for business electricity customers. 9 new tests.
- `simulation/policy_costs.py`: `get_ccl_per_mwh()` — 0 for resi (domestic exempt), main CCL rate for SME/I&C; CCL year Apr-Mar (same as RO obligation year)
- `_CCL_ELECTRICITY_RATE_BY_YEAR`: £5.44→£7.35/MWh 2016→2024; April 2020 step-change: electricity CCL raised as gas CCL frozen
- `simulation/hedged_settlement.py`: `segment` param on `run_hedged_term()`; `ccl_gbp` per settlement period; CCL in `policy_cost_gbp`
- `simulation/run_phase2b.py`: passes `segment=cust_segment` — I&C customers automatically pay CCL from first settlement
- `saas/reporting/annual_report.py`: `ccl_gbp` in yearly aggregation; `_section_policy_costs()` adds CCL column when non-zero (backward compatible with pre-27b runs)
- Policy cost stack now: RO levy + CfD levy + CCL = `policy_cost_gbp`; resi domestic exempt from CCL

**Phase 27a COMPLETE (2026-06-22)**: Second I&C customer C_IC2 — commercial office building, 1 GWh/year. 9 new tests.
- `saas/customers.py`: C_IC2 (office_building, Birmingham, acquisition 2018-01-01, segment "I&C", HH metered)
- `sim/hh_data/C_IC2.csv`: 3,446-day commercial office profile — Mon-Fri 08:00-18:00 peak at 135 kWh/period, +15% Jun-Aug summer cooling, 30% Saturday, 8% Sunday; ~1,004,285 kWh/year
- C_IC1 segment corrected from "SME" → "I&C" — both I&C customers now share correct segment
- EFFECTIVE_EAC_KWH auto-derived from CSV: C_IC2 ≈ 1,003,306 kWh; TOTAL_ELEC_EAC now ~3.1 GWh
- Starting treasury: £678k (up from £463k — scales with I&C portfolio growth)
- I&C portfolio now: 3 GWh (2 GWh warehouse + 1 GWh office), seasonal diversification (office summer peak vs warehouse temperature-insensitive)

**Phase 22b COMPLETE (2026-06-22)**: Company takes ownership of hedging decisions. 8 new tests.
- `company/risk/hedge_policy.py`: `company_evolve_hedge_fraction()` — same algorithm as sim.hedging_strategy, now in the company layer
- `COMPANY_MIN_HEDGE_FLOOR=0.85`, `COMPANY_EVOLUTION_STEP=0.1`, `COMPANY_MARGIN_TOLERANCE_GBP=5.0`
- `simulation/run_phase2b.py`: imports `company_evolve_hedge_fraction as evolve_hedge_fraction` + `COMPANY_MIN_HEDGE_FLOOR as MIN_HEDGE_FLOOR` from company layer
- `sim/hedging_strategy.py` preserved unchanged for historical runners (run_phase1d, 1e, 2a, run_segments)
- Closes Level 2 (decision boundary) separation for hedging — company now owns this decision

**Phase 21c COMPLETE (2026-06-22)**: Consumption recalibration — C1 and C5 EAC corrected. 4 new tests.
- `saas/customers.py`: C1 resi eac_kwh 2800→2500 (Ofgem TDCV domestic medium); C5 SME small_office 25000→15000 (midrange 8,500–25,000 kWh/yr)
- Both successors (C1_2, C5_2) updated to match
- Impact: first-term tariff pricing and hedging more accurate; subsequent terms auto-correct via settlement-derived EAC (Phase 25a)
- Starting treasury barely changes (~0.5% total EAC shift — dominated by C_IC1 at 2 GWh)

**Phase 21b COMPLETE (2026-06-22)**: Per-customer net assets solvency signal. 7 new tests.
- `saas/reporting/annual_report.py`: `_section_solvency_signal()` — treasury ÷ active billing accounts each year-end
- Ofgem licence floor: £0/account (positive net assets required); capital adequacy target: £130/dual-fuel account
- `_billing_account_id` dedup: C1g + C1 = one billing account; I&C C_IC1 counted separately
- Table shows per-year signal with BREACH flag when treasury negative; "below (gap: £N)" when below £130
- End-state summary: final year net-assets-per-account vs both thresholds

**Phase 24a COMPLETE (2026-06-22)**: I&C customer C_IC1 — first industrial account. 8 new tests.
- `saas/customers.py`: C_IC1 added — 2 GWh/year, HH metered, Birmingham, acquisition 2017-01-01, segment SME
- `sim/hh_data/C_IC1.csv`: C7 shape scaled by 156× to give ~2 GWh/year; 3446 days of data
- `EFFECTIVE_EAC_KWH["C_IC1"]` auto-derived from HH data (1,999,935 kWh/year ≈ 2 GWh)
- Bill-stress churn model: C_IC1 saturates at MAX_CHURN_PROBABILITY=0.95 from 2nd term onwards
- Retention offer: 5% discount on 2 GWh at £150/MWh = £15,000 cost per offer (guard condition scale-invariant)
- Starting treasury scales with EFFECTIVE_EAC: £29,846 → £463,166 (adds working capital for I&C volume)
- Demand estimation log includes C_IC1 from 2nd term (2018-01-01) with ~2-4% error (HH accuracy)
- All existing report sections (P&L ranking, retention durability, churn avoidability) data-driven; include C_IC1 automatically
- Expected 2021-22: C_IC1 shows large crisis losses (2 GWh × £400/MWh spot vs £150/MWh tariff)

**Phase 23a COMPLETE (2026-06-22)**: Company-owned demand estimation — closes epistemic honesty violation. 12 new tests.
- `simulation/run_phase2b.py`: `_company_eac_estimate()` sums prior-year billing records (12 months before term start) for EAC estimate; falls back to SIM oracle only on first term (no prior billing)
- Three `EFFECTIVE_EAC_KWH` oracle lookups in company-layer decisions replaced: bill-burden churn signal, retention economics, missed-opportunity analysis
- `demand_estimation_log` key in run output: per-renewal comparison of company estimate vs SIM oracle (customer_id, term_start, company_eac_kwh, true_eac_kwh, error_pct, source)
- `_compute_company_divergence()` extended with `demand_error_by_year` alongside existing tariff and churn error tracking
- `saas/reporting/annual_report.py`: `_section_demand_estimation()` — year-by-year mean/max abs error table; prior-billing vs fallback count; silent when log absent (backward compatible)

**Phase 22a COMPLETE (2026-06-21)**: Post-crisis churn hangover + trailing-margin CLV. 22 new tests.
- `company/crm/churn_model.py`: `CRISIS_HANGOVER_BASE_UPLIFT=0.12` — +12pp churn when company observes prior term net loss >20% of revenue; persists for 2 renewal periods. Fixes 2024 failure mode: falling rates collapse the rate-change signal to near-zero, but customers remain financially scarred.
- `simulation/run_phase2b.py`: `hangover_remaining` dict tracks remaining hangover periods per customer; triggers at term close, decrements at renewal; passed as `hangover_periods_remaining` to `estimate_churn_probability`.
- `saas/clv_model.py`: `override_avg_margin_by_account` param bypasses cost_to_serve lookup; enables trailing-margin CLV variants without rerunning settlement.
- `saas/reporting/annual_report.py`: `_section_enterprise_value_analysis()` — Full-history EV vs 3yr-trailing EV; year-by-year net margin table; per-account CLV comparison. Answers: "is negative EV a history problem or a current problem?"

**Phase 21a COMPLETE (2026-06-21)**: Explicit RO + CfD electricity policy costs. 787 tests passing (23 new).
- `simulation/policy_costs.py`: year-indexed lookup tables for RO (£15.6→£31.8/MWh 2016→2024) and CfD levy (negative in 2022 = crisis rebate)
- `saas/tariff_pricing.py`: `price_fixed_tariff()` gains `policy_cost_per_mwh` param — passes through levy in unit rate
- `simulation/renewals.py`: calls `get_electricity_policy_cost_per_mwh(term_start_str)` at schedule build; electricity unit rates now realistic
- `simulation/hedged_settlement.py`: records `ro_levy_gbp`, `cfd_levy_gbp`, `policy_cost_gbp` per period; `net_margin_gbp = margin_gbp - policy_cost_gbp - capital_cost_gbp`
- Settlement uses SETTLEMENT DATE year for the levy; tariff uses TERM START year → creates authentic basis risk when cross-year terms meet 2022 CfD rebate
- Annual report: `_section_policy_costs()` shows year-by-year RO + CfD breakdown; flags 2022 negative CfD
- R&D: 2 scenario research agents completed; findings in `docs/market_research/energy_market_complexity_june2026.md` + `energy_stress_scenarios_june2026.md`
- Knowledge map updated with full Novel/Unseen Scenario domain

**Phase 18a COMPLETE (2026-06-21)**: Regime detection premium in company tariff engine. 768 tests passing (9 new).
- `company/pricing/tariff_engine.py`: `_compute_regime_premium()` — compares 60d mean vs 180d baseline mean of spot prices
- If short/long ratio > 1.10 (upward trend): apply premium = (ratio - 1.10) × 0.50, capped at +15%
- If short/long ratio < 0.90 (downward trend): apply discount, capped at -5%
- Wired into `get_forward_price()` as a new `regime_detect: bool` param (default True, backward-compat off)
- Complementary to Phase 14c (adaptive lookback reacts to volatility; regime detector reacts to trend direction)
- Expected: 2021-22 crisis upward price trend → 5-10% premium applied at pricing → reduced tariff error

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
## Investor Thesis — Long-Horizon Vision

The following goals are not immediate build targets. They are the
destination the simulation is working toward. Every phase decision
should be evaluated against whether it moves toward or away from
these goals.

### Digital Darwinism at Machine Speed

The simulation currently runs one continuous timeline (2016–2025).
The long-horizon goal is to run the same company through multiple
alternative timelines simultaneously — deliberately inducing extinction
events (the 2021 crisis, regulatory interventions, competitor shocks,
demand collapses) and evolving the operational blueprint through them.

Each run produces a blueprint stronger than the last — not by small
iterative margin, but fundamentally stronger because each run discovers
failure modes invisible in the previous one. The 2021 crisis revealed
regime-change blindness. The next stress test will reveal something else.

The build should move toward: configurable extinction events, parallel
scenario runs, blueprint comparison across runs. The current single-
timeline run is the foundation. Scenario branching is the destination.

### Bot-to-Bot Protocol Discovery

As AI deployment matures, a new category of interaction emerges: two
AI agents negotiating directly with no human in the loop on either
side. When the company's procurement agent negotiates with a supplier's
sales agent, the failure modes — commitment boundaries, hallucination
risks, adversarial dynamics, contractual implications — are qualitatively
different from anything in human-to-human or human-to-AI interaction.

The simulation is the only safe environment to discover and test these
protocols before they result in real contractual commitments or legal
exposure. This is not a future problem — it is an immediate one for any
company deploying AI agents in commercial roles.

The build should move toward: agent-to-agent interaction scenarios,
commitment boundary testing, adversarial negotiation discovery. The
company layer agents (tariff engine, churn model, retention offers)
are the starting point. Inter-agent negotiation is the destination.

### The Translation Thesis — Geography and Industry as Parameters

Every failure mode discovered in UK energy has a structural analogue
in other complex regulated industries:

- Regime-change blindness → insurance reserving models trained on
  benign history; credit scoring trained on expansion
- Activity-based pricing gap → corporate insurance policies profitable
  until claims capital is loaded; large bank clients subsidised by retail
- Forward curve overpricing → specialty lines premia wrong vs loss
  emergence; bid-offer calibrated to recent vol, blind to tail risk

The simulation should eventually be re-parameterisable: change the
regulatory framework, market structure, currency, and cultural behaviour
parameters — and the same core physics runs in German energy, UK
insurance, or retail banking. The blueprint compounds across sectors
and geographies without a full rebuild.

The build should move toward: clean separation of market-specific
parameters from core physics, documented parameter interfaces for
each layer, proof-of-concept re-parameterisation for one new market.
UK energy is the first blueprint. It is not the last.

### The Real Company Transition

The simulation becomes a real company when it starts transacting.
That transition requires:
- The SIM/company barrier fully enforced — the company operating
  entirely on its own models with no shared code paths to SIM internals
- Real customer-facing interfaces — a portal where simulated customers
  interact, and eventually real ones
- Real market interfaces — the company submitting to Elexon, not just
  reading from it
- Capital — at the point when the blueprint is proven, not before

The simulation is not there yet. But every phase should be evaluated
against: does this move us closer to a company that could actually
transact? If not, why are we building it?

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
