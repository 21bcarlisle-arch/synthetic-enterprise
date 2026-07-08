# Current Priorities

Last director review: 2026-07-06. Updated (queue-tracking only, no re-rank): 2026-07-08 --
S1 (shadow-live proof-first track record) CLOSED by Phase RX (Options A rolling live Elexon
fetch AND B two decoupled clocks; see CLAUDE.md Current state). Its fast-follows (hedge-outcome
grading once live entries accumulate; a live NBP gas source) are unranked backlog and both
currently un-actionable autonomously (grading premature; gas is network/endpoint-verification
blocked). VERIFIED THIS SESSION and corrected below: CUSTOMER_360_REDESIGN.md items 2-4 (bill
equation + why-different waterfall, events-perturb chain, reaction-closes-loop) are ALL BUILT on
site/customers/index.html (billWaterfall/billEquationHtml/renderReactionChain/downstream-effect
annotations) -- the "Tab 4 ... items 2-4 not started" note in the ACTIVE WAVE section below is
STALE and superseded by this line. With the ranked queue exhausted at its front, the next-phase
proposal is Tier 3: docs/staging/drafts/NEXT_PHASE.md -- Phase RY, FEEDBACK_AND_REPUTATION Layer 2
(reputation feedback loop), 4h opt-out filed 2026-07-08. This is queue-TRACKING only; a director
re-rank (P-5) of the post-S1 backlog is still owed.
Previous tracking (2026-07-07): P2 CLOSED IN FULL (Phase RW, item 5 SAAS_COVERAGE_MAP.md landed);
front of queue was S1 (docs/staging/S1_SHADOW_LIVE_TRACK_RECORD_DESIGN.md), since closed per above.
Last updated: 2026-07-06 -- PRIORITY RESET (docs/staging/PRIORITY_RESET_PUBLIC_SITE.md,
[ADVISOR-STAGED] 5fa9a0cf, Tier 2 pre-approved). Rich's direct verdict after reviewing the live
site: still far below target -- tab order unchanged, gas/electricity still bundled everywhere he
looks -- despite backend depth (SIM tab QY-RC, Project generators RD/RG, portal tokens QO)
shipping. THE PUBLIC SITE (poesys.net's four top-level tabs + portal) IS NOW P1, ahead of further
backend depth. New order, top-down, each Tier 2:
  P1a. CUSTOMER 360 v4 (CUSTOMER_360_REDESIGN.md) -- CLOSED IN FULL (Phase RL). Reopened once
    (BILLING_AND_PAYMENTS_LEDGER.md, Rich's directive after live review) for the account
    ledger/bill-equation/cashflow scope -- CLOSED IN FULL (Phase RP, 2026-07-06): per-account
    chronological ledger (tools/generate_payment_ledger_data.py) + Billing & Payments tab
    Bills/Statement/Cashflow sub-views + household reconciliation line on site/customers/index.html.
  P1b. SUPPLIER TAB IA (SUPPLIER_TAB_OVERHAUL.md) -- CLOSED IN FULL (Phase RH IA regroup, Phase RM
    portfolio event stream + Recommended Actions->Overview + heatmap click-through).
  P1c. SIX-SECTION NAV + STORY (NAV_STORY_PLATFORM_METHOD.md) -- CLOSED IN FULL (Phase RO: Home/Story
    landing + Platform skeleton; Phase RQ, 2026-07-06: Method section + Project tab slim-down).
  P1a-c ALL CLOSED (2026-07-06, Phase RQ). P2 (Rich's visual confirmation received, queue running):
    item 1 CTS reconciliation CLOSED (Phase RS), item 2 frozen-policy baseline CLOSED (Phase RT),
    item 3 FEEDBACK_AND_REPUTATION.md Layer 1 CLOSED (Phase RU, Layer 2 still open). Item 4
    NUDGE_PHYSICS.md Layer 1 (loss-aversion offer framing) CLOSED (Phase RV, 2026-07-07) -- see
    Section 4 Phase RV. Item 5 SAAS_COVERAGE_MAP.md CLOSED (Phase RW, 2026-07-07) -- P2 QUEUE
    FULLY CLOSED. Front of queue next: S1 (shadow-live proof-first track record), design note
    filed docs/staging/S1_SHADOW_LIVE_TRACK_RECORD_DESIGN.md, Tier 3 own 4h opt-out (filed
    2026-07-07 12:24 UTC) -- not yet implemented, awaiting opt-out window.
Acceptance for every P1 item: Rich's eyes on the live public page -- report "awaiting Rich's visual
review", never "done" outright. PROJECT_TAB_OVERHAUL.md now CLOSED IN FULL (Phase RG).
PROCESS_NOT_EVENTS.md and DECISION_LOOP_AND_EVENT_LEDGER.md remain CLOSED IN FULL (no change).

**ACTIVE WAVE (director-critique site overhaul, 8 documents, staged 2026-07-04/05):**
WEBSITE_AS_SHOWCASE.md is the master directive. Progress per tab:
- Tab 1 (SIM): CLOSED -- SIM_TAB_OVERHAUL.md items 1-5 all done (Phases QY, QZ, RA, RB/RC).
- Tab 4 (Customer 360): CUSTOMER_360_REDESIGN.md item 1 (Usage Viz -- monthly/daily/HH
  consumption, load shape, weather overlay, period comparison) data layer + frontend rendering
  both done and both committed (Phases RE data layer, RI frontend commit -- RI found the frontend
  diff already written but never staged, a git-add gap not incomplete work) on
  site/customers/index.html. Items 2-4 (bill equation waterfall, events-perturb-chain,
  reaction-closes-loop) not started. WEBSITE_AS_SHOWCASE.md's case-study recommender
  (auto-curated "interesting customers" list) also not started.
- Tab 3 (Project): PROJECT_TAB_OVERHAUL.md CLOSED IN FULL (Phase RG, 2026-07-06): Timeline
  auto-append (item 2), real Capabilities register (item 6), and System-tab elevation (item 3) --
  all three found already implemented in site/project/index.html from an interrupted prior session,
  verified against live data and committed. Company dedup, Regulatory inline-expand, chart axis fix,
  capability-card stat generation, CONSISTENCY BREACH and phases.json hand-curation done earlier
  (RF, QW, RD).
- Tab 2 (Supplier): SUPPLIER_TAB_OVERHAUL.md's "Worst Shock Month" bug is already fixed (commit
  57fb0025) and its Regulatory RAG-per-obligation item is DONE (Phase RG) via
  company/regulatory/compliance_scorecard.py::latest_check() +
  tools/generate_dashboard_data.py::extract_regulatory(). The min-HF chart clipping bug and the
  IA regroup ("the big fix": 9 flat tabs -> 5 grouped nav -- Performance/Commercial/Trading &
  Market/Operations/Governance -- Query converted to a persistent FAB+panel affordance) are DONE
  (Phase RH, 2026-07-06), plus the Monthly-chart-axis FIX item and two THE IN-WORLD RULE
  violations found en route (header git-hash link, Insights tab git-hash Run History table --
  both removed as build metadata; see PROJECT_OVERVIEW.md Section 4 Phase RH). Judgment call:
  proceeded with the IA regroup once the frozen-policy design note itself had landed (satisfying
  the specific stated dependency -- "the design note must land before the IA regroup proceeds"),
  without waiting for that note's own option-B implementation or the separate CTS reconciliation
  note, since nav regrouping is orthogonal to both open ledger/policy questions and does not
  preclude the future delta-EV headline (Overview tab untouched). Flagging this reading for Rich
  in case a stricter sequencing was intended.
  Still open: the Accounts waterfall "CTS £0 vs Insights £91,780" breach (real gap, not a display
  bug -- ledger account 6100 has no posting event type; saas/cost_to_serve.py still bakes in the
  old flat BAD_DEBT_RATE Phase QD's emergent-arrears engine superseded). Write-up + options in
  docs/staging/drafts/NEXT_PHASE.md, Tier 3, own 4h opt-out (filed ~06:40, 2026-07-06). Also open:
  frozen-policy-baseline's actual option-B implementation (design written, docs/staging/drafts/
  FROZEN_POLICY_BASELINE_DESIGN.md) -- Tier 3, own 4h opt-out (filed ~06:49, 2026-07-06). Accounts
  waterfall CTS reconciliation itself still not actioned pending that opt-out.
- FEEDBACK_AND_REPUTATION.md Layer 1 CLOSED (Phase RU); Layer 2 (public reviews, regulator rating, reputation->funnel loops) still open. NUDGE_PHYSICS.md Layer 1 (loss-aversion offer framing) CLOSED (Phase RV, 2026-07-07); remaining mechanisms from docs/market_research/NUDGE_PHYSICS_BENCHMARKS.md (defaults/status-quo, anchoring, social norms, friction costs, present bias, collections-letter tone, commitment devices) not yet built -- own follow-on phase.

**SUPERSEDED (2026-07-06, Phase RQ):** the two Tier 3 design-note opt-outs below and the
"queued behind" ordering are now moot -- P1a-c (see top of file) are ALL CLOSED as of Phase RQ.
Front of queue next is P2 (CTS reconciliation is one of its five items, see top), gated on Rich's
visual confirmation of the live site, not a 4h opt-out. Retained below for history only.

## CRITICAL: NO MORE COVERAGE SPRINTS
Coverage sprints (phases LQ through MU, 95+ sprints) are complete.
All future phases must close a real capability gap from the list below.
Do NOT propose another coverage sprint. Do NOT read the old sprint pattern and repeat it.

## Now (active this session)
Last updated: 2026-07-05 -- see "NEW ACTIVE WAVE" above. The WEBSITE_AS_SHOWCASE.md wave outbids
everything in this section below (all dated 2026-07-04 or earlier); retained for history only.

Phase PY COMPLETE (2026-07-04): Synthetic Generator Statistical Equivalence Gate -- 15,402 tests.
Phase PZ COMPLETE (2026-07-04): Scenario Stress Testing via Synthetic Market -- 15,424 tests.
Phase QA/QB COMPLETE (2026-07-04): Churn estimate error-metric fix + observable market-conditions signal -- 15,319 tests.
Phase QC COMPLETE (2026-07-04): Website Data Integrity (Part A) -- 15,341 tests.
Phase QD COMPLETE (2026-07-04): Emergent Bad Debt (WEEKEND_ACCELERATION Q1) -- 15,393 tests. Real bad debt
GBP3,051 vs old flat-formula GBP92,551.
Phase QE COMPLETE (2026-07-04): Shadow-Live Decision Log Persistence (WEEKEND_ACCELERATION Q6) -- 15,329 tests.
Phase QF COMPLETE (2026-07-04): Permanent Consistency-Gate Wiring, 8 headline metrics -- 15,342 tests.
Phase QG COMPLETE (2026-07-04): GitHub Pages Advisor-Verification Mirror (WEEKEND_ACCELERATION Q3) -- 15,349 tests.
Phase QH COMPLETE (2026-07-04): Dead-code regression fix (dashboard generation early-return bug) -- 15,349 tests.
Phase QI/QJ COMPLETE (2026-07-04): EVIDENCE_IN_BUSINESS_SURFACES.md retrofit (bad debt + churn-model
evidence onto Sim/Customers/Supplier tabs) -- 15,367 tests.
Phase QK COMPLETE (2026-07-04): Enriched passive-renewal churn estimate -- 15,377 tests.

KEY OPEN FINDING (exposed by QJ, RECLASSIFIED not closed by QK): live churn classifier
(company/analytics/churn_accuracy_report.py) still shows recall=0%/precision=0% on the full live re-run
AFTER the QK fix. QK correctly closed the "passive renewals never receive the payment/satisfaction
signal" bug -- verified live: 3 passive renewers now cross the old 0.10 SVT-inertia cap under genuine
stress and trigger retention offers that were structurally impossible before (C1 2018-12-31 est 0.359,
C5 2021-12-30 est 0.492, C6 2023-03-31 est 0.387, all "retained"). But all three later churned anyway at
a SUBSEQUENT renewal once the satisfaction/behaviour signal had decayed back down (C1 2020-12-30 est
0.073; C5 2022-12-30 est 0.048; C6 2024-03-30 est 0.246) -- the classifier only scores the terminal
renewal before departure, so a correctly-detected-then-decayed risk still counts as a false negative.
Real root cause: signal-decay-timing, not a missing signal. Next candidates (neither started): slow the
satisfaction/behaviour decay rate, or redefine the accuracy metric to credit a prevented-churn
intervention instead of only the terminal event.

Observability URLs (all confirmed live at poesys.net and github.io mirror):
- /state/PROJECT_STATE.txt, /state/billing_ledger.json, /state/population_anchoring.json
- /data/customers.json + /data/supplier.json -- live portfolio
- /shadow/ /shadow/customers/ /shadow/project/ /shadow/sim/ -- all sections
- /state/live_decisions_latest.json -- shadow live decisions + persisted daily log


## Next (roadmap items outbid self-generated work)
Last refreshed: 2026-07-04 -- Phase QK complete (see KEY OPEN FINDING). Next: WEEKEND_ACCELERATION.md
Q2 (professional design system across all four shadow sections + customer portal) or Q5 (verify/complete
C4/C4g fully separate per-fuel legs: consumption/tariff/invoices/P&L, combined as roll-up only), or a
QL-style decay-timing/metric-redesign phase closing the reclassified churn-recall finding above.

**RULE (permanent, added to phase-close checklist):** A new board/report/Observatory section is NOT a phase. Board sections are byproducts of building capability. Any "add an X Observatory / X dashboard" proposal is automatically outbid by the priorities below.

### PRIORITY 1: OBSERVABILITY THE ADVISOR CAN ACTUALLY USE
**Acceptance: advisor confirms successful fetch of all three -- not a statement it was built.**

(a) **PROJECT_STATE.txt auto-sync BROKEN** -- shows Phase NS / 14,823 tests from Jun 30. Fix the
    regeneration pipeline so it updates on every push. Verify by fetching the file and confirming
    current phase + test count.

(b) **customer_sample.json**: 15-20 real segment-model customers, full behavioural trajectories
    (income_stress, life_events, payment_score, satisfaction, churn_estimate, basis_risk),
    at a STABLE fetchable URL listed in PROJECT_STATE.txt.

(c) **Shadow HTML site**: ALL FOUR sections (Supplier/Customers/Project/SIM) as plain no-JS HTML
    pre-rendered static content. No client-side rendering. The advisor's fetch tool must be able
    to read the full content. Ugly is fine; complete and current is mandatory.

### PRIORITY 2: REAL BILLING & PAYMENT INFRASTRUCTURE
Per-customer money movement -- NOT an Observatory section:
- Invoices issued per customer per billing cycle with due dates
- Payment methods (DD / cash / prepay) and payment events posting to ledger
- Missed payment -> arrears state -> dunning cycle (emergent from non-payment)
- Bad debt (stage 5) emerges naturally -- do NOT build separately first
**Acceptance:** named customer's ledger shows invoices raised, payments received, arrears accruing.

**Bad debt CLOSED (Phase QD, 2026-07-04):** board-reported bad_debt_gbp was a flat rate*revenue
formula, disconnected from the emergent per-customer arrears ledger (Phases PP/PW). Now the same
engine (simulation/arrears_engine.py) drives both -- proven equal by a dedicated acceptance test.
Real figure is £3,051.07 vs the old formula's £92,550.88 across the full run (net margin +£89.5k
on next production run). Remaining P2 scope: cash/prepay payment methods (DD only modelled).

### PRIORITY 3: POPULATION ANCHORING AS STANDING CONSTRAINT
SIM aggregates validated against published UK statistics every run:
- Ofgem annual switching rates by year (CRITICAL: 2021-22 crisis = switching COLLAPSE, not rise;
  SIM must NOT show churn rising during crisis -- if it does, the SIM is wrong)
- Complaints/ombudsman volumes, arrears rates vs published ranges
Build as a validation gate that flags SIM divergence from published reality.

### Completed / No longer current
~~Phase OM (Fuel Mix Disclosure board section)~~ -- SUPERSEDED BY HARD REDIRECT. Board sections
are not phases. Fuel mix capability already built; a board section is a byproduct, not a phase.

## Real capability gaps

### Gap 1 -- Real Forward Curve [CLOSED -- Phase MS]
NBP/EPEX term structure using real published seasonal forward strips (2016-2025).
seasonal_calibration.json now data-derived from Elexon SSP + TTF proxy. Gas Dec 1.294 (was 1.20).

### Gap 2 -- I&C Triad Demand Curtailment [CLOSED -- Phase MT]
Triad notification book wired to 25% load reduction in settlement for I&C HH customers.
build_triad_alert_set (SSP>80 + Triad season + SP 33-39) + make_triad_aware_shape_fn live.

### Gap 3 -- Human Simulation Layer [OPEN -- LARGE / MULTI-PHASE]
4-dimension customer modelling: physical (property/EPC/appliances), economic (income/credit),
behavioural (payment/switching propensity), emotional (satisfaction/trust).
Dim 1 (physical): CLOSED -- simulation/household.py + household_demand.py fully wired (EPC
  multipliers, seasonal_flatness_factor, life events for solar/EV/boiler/insulation).
Dim 2 (economic): CLOSED SIM-side (MV/MW); company-side closes with Phase MX.
Dim 3 (behavioural): CLOSED -- simulation/switching_propensity.py (Phase MZ) wires income_stress
  into roll_lifecycle_event. HIGH 0.65x / MODERATE 0.85x / LOW 1.10x multiplier on churn probability.
Dim 4 (emotional/satisfaction): CLOSED -- company side: satisfaction_accumulator.py (NA/NB/NC). SIM side:
  sim_satisfaction.py + satisfaction_churn.py + roll_lifecycle_event (NF). Full four-dimension model complete.

### Gap 4 -- Churn Blind Miss Rate [OPEN -- in progress]
Board risk shows 4/6 departures (67%) not forecast. Company churn model (saas/churn_model.py)
uses only bill shocks. Phase MX gives company payment behaviour scores (proxy signal).
Phase MY wired BehaviourScore (payment_churn_model.py). Phase NB added satisfaction_score.
Phase NC enriched_churn_estimate = max(rate, payment) wired into sim_interface.get_churn_estimate.
CLOSED. run_phase2b uses enriched_churn_estimate with bill_shock_count from all_records (Phase ND).

### Gap 5 -- Gas Segment ROC [CLOSED -- Phase NE]
Root cause was a bug: assess_term_risk called with naked_kwh=aq_kwh for pass_through gas
(hf=0 forced), generating spurious full-VaR capital on a zero-risk position. C_IC3g bills at
spot+service_fee; company holds no commodity price risk. Fix: naked_kwh=0.0 for pass_through
in run_phase2b.py. C_IC3g: net -GBP 134k -> +GBP 95k (service_fee x volume over 9.5 years).

## Backlog (lower priority)
- ~~Dashboard: Flexibility revenue tab~~ -- CLOSED (Phase NY, 2026-07-03): extract_flexibility() + dashboard["flexibility"] key + _section_flexibility_revenue extended
- ToU tariff depth: time-of-use pricing for HH smart meter customers
- Bad debt stress test: does bad_debt_provision feed back into capital model?

## Recently completed real capability
- **Phase PX** (2026-07-04): Correlated Synthetic Market Generator -- CorrelatedGeneratorAdapter; bivariate OU gas+elec; regime switching 8% crisis prob; 0.70 corr; seed reproducibility. Addresses regime-change blindness failure mode.
- **I&C churn calibration fix** (2026-07-02): IC_BILL_STRESS_SENSITIVITY 0.10->0.0. I&C was estimating 95% churn vs SIM 5% (1800% error) at stable rates. 58% of retention offers were wasted. Rate-sensitivity (IC_RATE_SENSITIVITY=1.5x) now drives I&C churn exclusively. Crisis spikes still correctly reach 95%.
- Phase MW (2026-07-02): Income Stress -> Observed Payment Behaviour (14,485 tests)
- Phase MV (2026-07-01): Economic Life Events -- income_stress enum, job_loss/income_recovery/new_baby/retirement
- Phase MT (2026-07-01): I&C Triad Demand Curtailment -- wired to settlement
- Phase MS (2026-07-01): Real NBP Forward Curve -- seasonal multipliers data-derived
- Net margin GBP 1.22M | EV GBP 5.99M | Treasury GBP 3.69M on live 2016-2025 data
