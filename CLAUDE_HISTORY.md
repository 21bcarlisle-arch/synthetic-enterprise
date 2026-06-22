# CLAUDE_HISTORY.md — Archived Build Context

Historical context archived from CLAUDE.md to keep it under the 35k character limit.
Reference material — not loaded every session. See CLAUDE.md for current state.

---

## Original Phase Plan vs What Was Built


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

## Phase Completion History — Phases 12–29

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
