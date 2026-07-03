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
- `run_complete_*.md` — publish results (regenerate report, LATEST.md, dashboard.json), commit, push, archive. **Do NOT send NTFY for routine sim run completions.** Only NTFY for notable exceptions (admin event, all-time high/low margin). Batch silently if multiple queued.
- `run_pending_*.md` — check if finished and act accordingly.
- `from_rich_*.md` — action it, reply via NTFY, archive.
**At every REVIEW_GATE:**
1. Complete phase and commit all outputs.
2. NTFY Rich with what was done and what's next.
3. Proceed immediately to the next phase — do not hold for confirmation.
4. Rich redirects via NTFY if he wants a different direction.
**Always update and commit LATEST.md before sending NTFY.** If stale, fix the root cause.
**When budget is available between tasks:** check backlog, fix known issues, improve coverage. Don't sit idle.
**NEXT_PHASE.md proposals:** must name the gap or roadmap item served and what real-world fidelity is gained. Test-count increases alone are not a valid answer. No value answer = PRIORITIES.md outbids it.
---
## Phase-close checklist (in order)
0. **PRIORITIES.md freshness:** "Next" must have ≥1 real roadmap item outbidding self-generated work. If stale, refreshing it IS the next task — before all else.
1. Update test count + latest run figures in PROJECT_OVERVIEW.md Section 10.
2. Add build history entry in PROJECT_OVERVIEW.md Section 4.
3. **Run epistemic verifier:** `python3 -m tools.epistemic_verifier` — must PASS before committing. If FAIL: fix violations first.
4. **`wc -c CLAUDE.md` — hard limit 35,000 chars / 200 lines.** If over: move to `docs/claude/phase-history.md`. Never accumulate phase details in CLAUDE.md.
5. Add one-line phase completion entry to CLAUDE.md "Current state".
6. Commit and push.
PROJECT_OVERVIEW.md is updated at phase close. Run-complete pipeline does NOT update it.
## Current state
**Phase NR COMPLETE (2026-07-03):** Bad Debt -> Capital Stress Feedback -- 19 tests (14,805 total). company/risk/credit_risk_stress.py: CreditRiskStress(current_provision_gbp, stress_multiplier=2.5x, annual_revenue_gbp) -- stressed_provision/stress_incremental/is_material (>0.5% revenue). company/risk/capital_adequacy.py: credit_risk_stress_gbp field (default=0.0); stress_test_passes = equity > (price_VaR + credit_stress). saas/reporting/annual_report.py: _section_credit_risk_capital board section -- per-year bad debt table + crisis stress RAG. Ofgem FRA post-2022 requires combined market+credit stress; capital model now reflects full Ofgem FRA requirement. Epistemic: PASS.
**Phase NQ COMPLETE (2026-07-03):** Churn Model Recalibration -- 14 tests (14,786 total). INDUSTRY_BASE_CHURN_RATE=0.05 floor on enriched_churn_estimate (Ofgem passive switching baseline); estimate_passive_churn_probability floor at PASSIVE_BASE_CHURN_RATE; yoy_extended 24-month reference window in score_experience_signals (crisis-period shocks visible when reference year itself elevated); build_churn_risk comparison_mode param; run_phase2b: industry base rate when no prior rate; Phase NP pay_metrics bug fixed. Epistemic: PASS.
**Phase NO COMPLETE (2026-07-03):** Counterfactual Retention & Threshold Optimisation -- 15 tests (14,772 total). company/analytics/counterfactual_retention.py: compute_counterfactual_retention -- per-miss CounterfactualMiss (counterfactual_retained/value_recovered/net_value/was_worth_offering); company/analytics/threshold_sensitivity.py: compute_threshold_sensitivity -- recall/precision/F1 at 0-50% thresholds. saas/reporting/annual_report.py: _section_threshold_optimisation renders per-miss table + sensitivity curve + RAG. Key finding: model underestimates churn (all estimates < 25%; optimal threshold 0% = offer everyone). Board section exposes root cause. Epistemic: PASS.
**Phase NP COMPLETE (2026-07-03):** Behavioral Trajectory Emission -- 13 tests (14,757 total). simulation/household_demand.py: income_stress_trajectory(cid, years)->list[{year,stress}] (Dec-31 snapshot; None->low); life_event_history(cid)->list[{date,event_type}]. simulation/run_phase2b.py: _build_behavioral_trajectories emits per_customer_behavioral dict with income_stress_trajectory/life_event_history/payment_behaviour_score+metrics/company_satisfaction_score. tools/generate_customer_sample.py: behavioral lookup wired; data_status=complete|pending_sim_emission. Epistemic: PASS.
**Remote Staging Bridge (2026-07-03):** background/staging_watcher.py extended: git fetch origin every 3 min; new commits with [ADVISOR-STAGED] prefix trigger extraction of staging files via git show; files written to docs/staging/ then surface through normal check_once NTFY pipeline. _run() helper; _extract_advisor_staging_files(since_ref); check_remote(seen). 12 tests in tests/background/test_remote_staging_bridge.py. Epistemic: PASS.
**Harness Hardening (2026-07-03):** Three failure-mode rules encoded: (1) PRIORITIES.md freshness is phase-close gate; (2) Done = named artifact; (3) NEXT_PHASE.md must state fidelity value. Sim boundary audit closed (3 violations fixed: segment_report/annual_report/tou_periods; verifier extended to saas/). Observability: customer_sample.json + shadow HTML live in site/ pipeline. Phases LQ-MU archived to phase-history.md. Harness_hardening.md processed.
**Phase NL COMPLETE (2026-07-02):** Bill Shock YoY Recalibration -- 13 tests (14,744 total). saas/customer_reaction.py: score_experience_signals comparison_mode=rolling|yoy; yoy compares same calendar month prior year, eliminates seasonal false-positives (resi customers had 8-11 rolling-avg shocks/year -> 29-38% SIM churn). yoy_ref_gbp key added; rolling_avg_gbp=None in yoy mode. saas/churn_model.py: build_churn_risk -> comparison_mode=yoy; stable YoY prices -> 0 shocks -> 5% base; crisis-year doubles -> 11 shocks/12m window. Epistemic: PASS.
**Phase NK COMPLETE (2026-07-02):** Churn Model Performance Report -- 14 tests (14,731 total). saas/reporting/annual_report.py: extract_report_data now includes churn_model_performance key (fixes silent Phase NJ regression where recall/precision/F1 was discarded from JSON); _section_churn_model_performance renders TP/FP/FN/TN/recall/precision/F1/per-year/RAG. Structural limitation documented: passive SVT-rollers churn at ~10% effective rate; 30% RETENTION_THRESHOLD calibrated for active renewers; seasonal bill shocks inflate SIM base rate but passive cap holds effective churn to 10%. Epistemic: PASS.
**Phase NH COMPLETE (2026-07-02):** Payment Behaviour Score Wired -- 17 tests (14,701 total). simulation/run_phase2b.py: generate_payment_record + PaymentBehaviourAnalytics imported; _payment_analytics instantiated; monthly payment record generated per customer per settlement month; _nh_behaviour_score=_payment_analytics.get_score(cid) passed as behaviour_score to _enriched_churn_estimate at renewal. Three-signal churn model (bill_shock+behaviour+satisfaction) now fully operational. Epistemic: PASS.
**Phase NJ COMPLETE (2026-07-02):** Churn Model Calibration Report -- 16 tests (14,717 total). company/analytics/churn_accuracy_report.py: compute_churn_model_performance(customer_events, retention_log, no_offer_churn_log, threshold=0.30)->dict; TP=predicted>threshold+churned; FP=predicted+renewed; FN=no_offer_churn_log+not_predicted+churned; TN=not_predicted+renewed; recall/precision/f1/per_year. simulation/run_phase2b.py: churn_model_performance wired at results assembly. Board now has model calibration KPI. Epistemic: PASS.
**Fix (2026-07-02):** TOU Bill Shock Counter Bug -- resi HH TOU customers (C7/C8/C9) got 500-1500 spurious shocks from peak/offpeak transitions, capping company churn at 0.95 every renewal. Fix: _elec_rate_shock_counts tracks term-level rate transitions only (not HH period records). 14 tests (14,684 total). Epistemic: PASS.
**Fix (2026-07-02):** I&C Churn Model Calibration -- IC_BILL_STRESS_SENSITIVITY 0.10->0.0 -- 2 tests (14,670 total). Root: bill_stress dominated for 4 GWh I&C (£216k bill = 4.3x threshold, stress=0.33+base=0.20=0.53 minimum). Company was estimating 95% churn vs SIM 5% (1800% over). I&C churn is rate-driven not bill-size-driven; IC_RATE_SENSITIVITY=1.5x already handles sensitivity. 58% of retention offers were going to low-risk I&C. Fix restores rate-only churn for stable prices; crisis spikes (400%+) still hit MAX_CHURN. Epistemic: PASS.
**Phase NA COMPLETE (2026-07-02):** Dim 4 Emotional -- Customer Satisfaction Accumulator -- 20 tests (14,572 total). company/crm/satisfaction_accumulator.py: BASELINE=0.70; _BILL_SHOCK_DELTA=-0.05; _COMPLAINT_RAISED_DELTA=-0.10; _COMPLAINT_RESOLVED_DELTA=+0.05; _CSS_GOOD_DELTA=+0.05; _CSS_POOR_DELTA=-0.05; _MONTHLY_DECAY_RATE=0.01; record_bill_shock/record_css_score/record_complaint_raised/record_complaint_resolved/apply_monthly_decay/get_satisfaction/is_low_satisfaction/low_satisfaction_customers.
**Phase MZ COMPLETE (2026-07-02):** Dim 3 Behavioural -- Income Stress -> SIM Switching Propensity -- 21 tests (14,552 total). simulation/switching_propensity.py: STRESS_SWITCHING_MULTIPLIER LOW=1.10/MODERATE=0.85/HIGH=0.65; stress_switching_multiplier(income_stress|None)->float; adjust_churn_probability(base_prob, income_stress)->capped_at_0.95. simulation/customer_events.py: roll_lifecycle_event income_stress param; adjust_churn_probability applied before retention modifier. Vulnerability trap: HIGH stress customers 35% less likely to actually switch even with bill pain.
**Phase NG COMPLETE (2026-07-02):** Company Satisfaction Score -> Renewal Churn Estimate -- 16 tests (14,668 total). simulation/run_phase2b.py: CustomerSatisfactionAccumulator wired; 12-month decay + bill_shock(>20% rate rise) per electricity term; satisfaction_score=_company_sat_acc.get_satisfaction(cid) passed to _enriched_churn_estimate (was None). Company's 3-signal enriched estimate now fully populated. Epistemic: derived from company billing records only.
**Phase NF COMPLETE (2026-07-02):** Gap 3 Dim 4 SIM-side -- 16 tests (14,652 total). simulation/sim_satisfaction.py: sim_satisfaction_score(bill_shock_count, tenure_years, income_stress) -> [0,1]; BASELINE=0.70; BILL_SHOCK_DELTA=-0.10; INCOME_STRESS_DELTA LOW/MOD/HIGH 0/-0.05/-0.15; TENURE_BONUS_PER_YEAR=0.02 capped at 0.10. simulation/satisfaction_churn.py: satisfaction_churn_multiplier; adjust_churn_for_satisfaction (HIGH>=0.80->0.85x; LOW<0.50->1.30x). simulation/customer_events.py: satisfaction_score param; applies adjust_churn_for_satisfaction after income_stress. simulation/run_phase2b.py: _sim_satisfaction_score wired at roll_lifecycle_event call. Gap 3 Dim 4 CLOSED.
**Phase NE COMPLETE (2026-07-02):** Gas Pass-Through Capital Risk Correction -- 16 tests (14,636 total). Bug: assess_term_risk called with naked_kwh=aq_kwh for pass_through gas (hf=0 forced), generating spurious VaR capital on zero-risk position. Fix: naked_kwh=0.0 if term_tariff_type=="pass_through" in run_phase2b.py (also counterfactual_risk). C_IC3g: net -£134k -> +£95k. Gap 5 CLOSED.
**Phase ND COMPLETE (2026-07-02):** Gap 4 SIM-side Wiring -- 16 tests (14,620 total). simulation/bill_shock_tracker.py: count_rate_shocks(cid, commodity, all_records, shock_threshold=0.20) -> int; filters records by cid+commodity, sorts by term_start, counts rate transitions >20%. simulation/run_phase2b.py: imports enriched_churn_estimate + count_rate_shocks; active renewal path uses enriched_churn_estimate(old_rate, new_rate, tenure, eac, bill_shock_count=_count_rate_shocks(cid, elec, all_records), ...). Gap 4 company+SIM wiring now complete.
**Phase NC COMPLETE (2026-07-02):** Enriched Company Churn Estimate -- 16 tests (14,604 total). company/crm/enriched_churn_estimate.py: enriched_churn_estimate(old_rate, new_rate, tenure, kwh, *, bill_shock_count, behaviour_score, satisfaction_score, ...) = max(rate_model, combined_payment_model) capped at 0.95. company/interfaces/sim_interface.py: get_churn_estimate extended with bill_shock_count/behaviour_score/satisfaction_score params; StubSimInterface calls enriched_churn_estimate. Backward-compatible: no signals = pure rate model.
**Phase NB COMPLETE (2026-07-02):** Satisfaction Score -> Combined Churn Model -- 16 tests (14,588 total). company/crm/payment_churn_model.py: _HIGH_SATISFACTION_THRESHOLD=0.80; _LOW_SATISFACTION_THRESHOLD=0.50; _HIGH_SATISFACTION_UPLIFT=-0.02; _LOW_SATISFACTION_UPLIFT=+0.10; _satisfaction_uplift(score); combined_churn_probability(bill_shock_count, behaviour_score, satisfaction_score). Three-signal churn model: bill_shock+BehaviourScore+satisfaction capped at 0.95; backward-compatible (satisfaction_score=None).
**Phase MY COMPLETE (2026-07-02):** Payment Behaviour Score -> Company Churn Model -- 20 tests (14,531 total). company/crm/payment_churn_model.py: CHURN_UPLIFT_BY_SCORE EXCELLENT=-0.02/GOOD=0.00/FAIR=+0.03/POOR=+0.10/CRITICAL=+0.20; combined_churn_probability(bill_shock_count, behaviour_score) -> min(base+uplift, 0.95); imports churn_probability from saas.churn_model; BehaviourScore from Phase MX. Closes Gap 4 company-side: two observable signals (bill shock + payment behaviour) now feed churn estimate.
**Phase MX COMPLETE (2026-07-02):** Company Payment Behaviour Analytics -- 26 tests (14,511 total). company/crm/payment_behaviour_analytics.py: BehaviourScore EXCELLENT/GOOD/FAIR/POOR/CRITICAL; _SCORE_ORDER dict; score_payment_history(otr>=0.95+no_dd=EXCELLENT; otr>=0.80+ddf<0.05=GOOD; otr>=0.60+ddf<0.15=FAIR; otr>=0.40+ddf<0.35=POOR; else=CRITICAL); compute_payment_metrics(on_time_rate/late_rate/dd_fail_rate/avg_days_late); PaymentBehaviourAnalytics: record_payment/get_score/get_metrics/is_at_risk(POOR|CRITICAL)/at_risk_customers/score_trend(IMPROVING/STABLE/DETERIORATING).
**Phase MW COMPLETE (2026-07-02):** Income Stress to Observed Payment Behaviour -- 25 tests (14,485 total). simulation/payment_timing.py: _PAYMENT_DELAY_DAYS LOW(7-14)/MODERATE(14-45)/HIGH(30-90); _DD_FAILURE_PROBABILITY 0.03/0.12/0.35; _ON_TIME_PROBABILITY 0.92/0.50/0.10; _BAD_DEBT_MULTIPLIER 1.0/1.5/3.0; stress_bad_debt_multiplier; generate_payment_record. simulation/run_phase2b.py: income_stress_at_date lookup per term, multiply bad_debt_rate by stress_bad_debt_multiplier.
**Phase MV COMPLETE (2026-07-01):** Economic Life Events -- 20 tests (13,949 total). simulation/household: IncomeStress enum LOW/MODERATE/HIGH; income_stress field default=LOW. simulation/life_events: EventType +job_loss/income_recovery/new_baby/retirement_starts; _JOB_LOSS_ANNUAL_PROB=0.022; _INCOME_RECOVERY_ANNUAL_PROB=0.50; _NEW_BABY_ANNUAL_PROB=0.011; _RETIREMENT_PROB_BY_ERA ERA_1945_1964=0.035; econ_rng isolation; apply_events 4 new handlers. household_demand: income_stress_at_date().

→ Phases 1–HK, HO, HS–HT, IA–IE, IF–IM, FT–HZ, IJ, II, IV, IW, IN–IU, IX–IZ, JA–JE, JH–JM, JN–MU: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`
---
## Architectural Laws — Epistemic Honesty: The Company Cannot See Inside the SIM
The company layer operates under the same information constraints as a real energy supplier.
It cannot see simulation internals — churn parameters, forward curve construction, weather
engine outputs, VaR internals. It discovers the world through observable interfaces: market data feeds, meter reads, customer interactions, its own bills and payments, regulatory publications.
The company's models are approximations built from observed outcomes — not reads from ground
truth. That imperfection is the point.
**Before writing any company-layer code:** ask "Could a real UK energy supplier know this?"
If the answer requires reading simulation internals, it is a violation.
The SIM/company seam (`company/interfaces/sim_interface.py`) exposes observables only, never internals.
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
- **"Done" = named artifact.** Every completion (NTFY/report) must cite evidence: PROJECT_OVERVIEW.md entry, passing test count, or fetchable file. No artifact -> say "in progress".
---
## Technical environment
**Hardware (Skynet):** Intel i5-13400F, 32GB DDR4, RTX 3060 12GB VRAM. Windows 11 Pro + WSL2/Ubuntu.
**Network/AI:** Tailscale WSL2 `100.69.81.59` | File API `https://skynet-1.taila062fa.ts.net:8765` | Claude Code → qwen3:14b/Ollama → risk committee (Ollama)
**Key paths:** `docs/staging/` (instructions) | `docs/status/LATEST.md` | `docs/reports/ANNUAL_REPORT.md`
**Data:** Elexon `data.elexon.co.uk` (key-free; API migrated to Insights Solution — legacy wrappers partly stale) | NESO CKAN | Open-Meteo | synthetic forward curves
