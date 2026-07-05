# PRIORITIES.md -- Synthetic Enterprise
# Last refreshed: 2026-07-05 (PROCESS_NOT_EVENTS.md's acquisition funnel -- second in its
# declared sequence -- DELIVERED: wired into the live sim + all three evidence surfaces.
# New P1: PROCESS_NOT_EVENTS.md's debt-branch, third and last in the sequence -- generalize
# QD's stress->timing drift->miss->arrears->plan->write-off shape with the engagement/
# avoidance behavioural branch (overwhelmed-not-delinquent distinction).)

## COMPLETED
- P1 (process model, acquisition funnel): PROCESS_NOT_EVENTS.md's quote->application->
  credit_check->onboarding->cooling_off funnel (simulation/acquisition_funnel.py,
  tools/credit_bureau_port.py + synthetic_bureau adapter -- all pre-existing from an
  interrupted session, completed and wired this phase) replaces the flat coin-flip roll
  in run_phase2b.py's home-move replacement acquisition. Evidence on all 3 surfaces: Sim
  tab per-year stage leakage + win rate + population-anchoring RAG check; Customers tab
  one named won attempt, preferring a real credit-bureau-vs-ground-truth divergence case;
  Supplier tab portfolio stage leakage + real blended CAC. 11 new tests, full slow
  integration suite re-run clean. Epistemic: PASS.
- P1 (billing depth): Arrears states + dunning cycles + emergent bad debt -- DONE (Phase QD).
  simulation/arrears_engine.py: arrears_stages()/ic_arrears_stages() model the full missed-payment
  -> FIRST_NOTICE -> SECOND_NOTICE -> RESOLVED|WRITTEN_OFF cascade per customer (resi + I&C dispute
  variant); compute_emergent_bad_debt()/apply_emergent_bad_debt() replace the flat get_bad_debt_rate()
  formula with real written-off arrears. KEY FINDING: flat-rate bad debt was £92,550.88; real emergent
  figure is £3,051.07 -- confirms the PP/PW/NU infrastructure PRIORITY 1's note flagged was already
  most of the way there; QD closed the remaining "bad debt emerges from arrears, not a formula" gap.
- P1a: PROJECT_STATE.txt auto-sync -- FIXED (Phase PT; GH Pages fix 2026-07-04)
- P1b: customer_sample.json + customers.json + supplier.json at stable fetchable paths -- DONE (Phase PT)
- P1c: Shadow HTML site (4 sections) -- DONE (site/shadow/* auto-regenerating on every run)
- P2 (billing): Billing & Payment Infrastructure -- DONE (Phases PP/MW/MX/MY/NH)
- P2 (network): Network Charge Year-Indexed Actuals -- DONE (Phase 78; PROJECT_OVERVIEW.md Sec 9 gap closed)
- P3: Population Anchoring -- DONE (Phases NS/PQ/PR/PS: switching, churn, complaints, arrears)
- P4: Shadow Live Operation -- DONE (Phases PU/PV: live decisions + market adapter)
- Correlated market generator: Correlated Synthetic Market Generator -- DONE (Phase PX: bivariate OU adapter; Phase PY: equivalence gate PASS)
- Scenario stress testing: Phase PZ -- 4 scenarios; QUANTIFIES residual regime-change exposure for the board
  (correction 2026-07-04: PZ does NOT close regime-change blindness -- the 85% hedge floor closed it
  historically; PZ adds board-facing visibility into residual exposure. Claims must match artifacts.)
- P1 (churn recalibration): DONE (Phase QA fixed the churn_estimate_error_pct ground-truth comparison bug;
  Phase QB added market_conditions_multiplier so passive estimates vary 3-22% by year instead of pinning
  at a flat 5-10% floor). Residual: I&C estimates still hit the 0.95 ceiling -- noted as a follow-on, not
  blocking.
- Churn model validation loop rerun (2026-07-04, WEEKEND_ACCELERATION.md Q4): reran recall/precision/F1
  on the live production run (docs/reports/run_output_latest.json) with QA+QB in place. Result: TP=0,
  FP=6, FN=6, recall=precision=F1=0.0 at the 0.30 threshold -- UNCHANGED from the structural limitation
  Phase NK already documented (passive SVT-rollers capped at PASSIVE_CHURN_CAP=0.10 pre-multiplier in
  company/crm/churn_model.py:estimate_passive_churn_probability). ROOT CAUSE CONFIRMED: the market
  multiplier is applied AFTER that cap, and its max value (2.17x, year 2016) can only lift the passive
  estimate to ~0.217 -- structurally below the 0.30 classification/RETENTION_THRESHOLD regardless of
  market conditions, so the multiplier fix cannot move recall for this segment without either raising
  the cap or lowering the threshold. company/analytics/threshold_sensitivity.py (already wired, Phase NO)
  independently confirms this: optimal_threshold=0.00 (flag everyone) with F1=0.176 vs current threshold
  0.30 with F1=0.000 -- no positive threshold currently separates churners from renewers at all.
  NOT auto-fixed: lowering RETENTION_THRESHOLD to chase recall means offering paid discounts to the
  ~34 false-positive renewals the 0.05 threshold would also flag (precision 0.081 there) -- a real
  spending-policy tradeoff, not a mechanical bug. Flagged for Rich, not actioned autonomously. NOT a
  regression -- Phase NK predicted exactly this ("passive churns are below detection threshold by
  design"); QB improved estimate accuracy (mean error 1.25->1.00 per Phase QB) without ever being able
  to move TP/FP/FN counts for this segment. Q4 in WEEKEND_ACCELERATION.md CLOSED on this measurement;
  no code changed.
- Website data integrity Part A: DONE (Phase QC, staged WEBSITE_INTEGRITY_AND_DESIGN.md) -- fixed the
  step-ordering bug that put a stale Executive Summary next to correct 10-Year Totals on the same page, and
  replaced the hardcoded phase/test-count site header with docs/observability/build_info.json.
- Shadow-live decision log persistence: DONE (Phase QE) -- append_decision_log() writes
  site/state/live_decisions_log.jsonl, one immutable entry per UTC calendar day, closing the gap where
  run_decisions() silently overwrote the same dated snapshot every cycle and no track record accumulated.
- Website data integrity Part C (permanent per-run wiring): DONE (Phase QF) -- widened the Part A
  consistency gate from a single net-margin check to 8 headline metrics (net/gross margin, enterprise
  value, bills, committee interventions, retention offers/retained, churn count) compared across the
  dashboard totals vs run_insights.json exec-summary source; a mismatch now NTFYs Rich immediately instead
  of only printing to a log nobody watches in real time (generate() propagates the gate result instead of
  discarding it). Freshness stamps (git commit + phase, not just a timestamp) added to every shadow page
  footer. KEY FINDING: the widened gate immediately caught a real, pre-existing gross-margin discrepancy
  (dashboard £6,452,603 vs exec-summary £6,467,309, ~£14.7k / 0.2%) caused by tools/generate_insights.py
  preferring the _ledger_headline subtotal over total_gross_gbp -- the same class of bug Part A fixed for
  net margin, just never applied to gross. Fixed at root (precedence flipped to match net margin's and
  extract_portfolio's convention). Part B (design system + customer portal per-fuel legs) is the only
  remaining scope from the staged instruction.
- GitHub Pages advisor-verification mirror: DONE (Phase QG, docs/staging/ADVISOR_GITHUBIO_MIRROR.md) --
  poesys.net (Cloudflare Pages) proven persistently stale on the advisor's own fetch path specifically
  (cache-busted fetch still returned an 08:35Z generation while CC's direct fetch of the same URL at
  17:58 returned the current one), independent of any CD incident. tools/mirror_github_pages.py copies
  site/shadow/ -> docs/shadow/ and the 4 named state JSONs (customer_sample, billing_ledger,
  population_anchoring, sim_data) -> docs/state/ every run (same generator pass, no regeneration);
  wired into process_run_complete.py's site-generation + git_commit_push staging list. docs/status/
  PROJECT_STATE.txt Key Files section now lists the github.io URLs as the advisor-verification channel,
  poesys.net kept as the visitor-only surface. Also fixed a related bug found while touching this file:
  generate_project_state.py::_parse_phase_and_tests() picked the phase with the HIGHEST reported test
  count rather than the most recent one -- since the fast-suite total isn't monotonic across phases,
  this had silently regressed PROJECT_STATE.txt's "Current Phase" label to an older phase (PZ instead
  of the actual QF) whenever a later phase reported a smaller count.

## ORDERING NOTE (2026-07-04, advisor steer)
Phase PZ (scenario stress testing) jumped the queue: ADVISOR_CONFIRM_STATE_FRESH.md released the
correlated-generator hold WITH explicit conditions -- it stays BACKLOG behind P1 below until it's
DELIVERED, not just listed. No further generator/scenario phases until P1 below is complete.

## COMPLETED (cont.)
- Website Integrity Part B (Professional Design System): DONE (Phase QN + Phase QO, 2026-07-05).
  QN closed the per-fuel-legs data-completeness half -- Customers tab no longer drops gas legs
  (`if cid.endswith("g"): continue` removed), both fuel legs shown as separate accounts, a
  "Combined Roll-Up" table added as an explicit optional secondary view, and a per-fuel case study
  (C_IC3/C_IC3g) shows real invoice/arrears/failed-payment history per leg from billing_ledger.json
  -- live run shows the gas leg carrying a real -GBP89,641 arrears balance the electricity leg (0
  failed payments, 0 arrears) has none of, proving why the legs must stay separate.
  QO closed the design-system half -- company/portal/templates/base.html centralizes design tokens
  (palette/spacing/typography) and shared components (kpi-card, rag-chip, banner, btn, consistent
  nav with active-page highlighting) across all 19 customer portal templates, replacing 19
  independent inline <style> blocks; matching kpi-card/rag-chip CSS added to the shadow mirror
  (dark advisor-verification theme, kept intentionally distinct from the portal's light customer
  theme); population_anchoring.json (computed since Phase PQ, never rendered anywhere) now surfaces
  as real rag-chips on the Sim tab. See docs/staging/done/WEBSITE_INTEGRITY_AND_DESIGN_PARTA_DONE.md
  for the full original staged instruction.

## COMPLETED (cont. 2)
- Decision Event Ledger Part 5: DONE (Phase QP, 2026-07-05, docs/staging/DECISION_LOOP_AND_EVENT_LEDGER.md).
  company/analytics/decision_event_ledger.py unifies the per-topic case studies built independently
  across QI/QJ/QL/QM (behavioral signal, renewal decision, churn journey, retention deferral) into
  one real chronological timeline per customer (Customers tab: C_IC1, the flagship divergence case --
  2018-01-31 retention decision, company believed 95% churn risk / EV GBP139,477, immediately followed
  by the real outcome, SIM truth 4%, in one ordered feed) plus a portfolio-wide feed (Supplier tab:
  most recent 150 decisions/outcomes, filterable by event type, plain JS). FOUND AND FIXED EN ROUTE:
  Phase QL's churn_journey_log was computed by run_phase2b but never forwarded through
  saas/reporting/annual_report.py::extract_report_data() -- had been silently empty in every
  production run since QL shipped. 17 new tests.

## COMPLETED (cont. 3)
- Decision Event Ledger Part 4 + 0.95-ceiling calibration fix: DONE (Phase QQ, 2026-07-05,
  docs/staging/DECISION_LOOP_AND_EVENT_LEDGER.md, remaining scope). company/crm/churn_model.py:
  hard clamp at MAX_CHURN_PROBABILITY replaced with an asymptotic saturating curve above
  CHURN_SATURATION_ELBOW=0.90 (identity below it -- every previously-unclamped estimate
  unchanged); genuinely different elevated risk levels (60% vs 150% I&C rate rise) now read
  as distinguishable values instead of both collapsing to the same 95% ceiling -- the exact
  C_IC1-class bug. company/analytics/counterfactual_retention.py: compute_counterfactual_lift_by_class()
  classifies every no-offer churn as detection_gate (model problem) or uneconomical_{high,medium,low}
  (economics problem), each scored under H3 (effectiveness scales 0.04 per discount point,
  anchored so the medium tier reproduces the old flat 0.20 assumption); produces real
  lift-per-pound per class, wired into the board's Counterfactual Retention & Threshold
  Optimisation section. 26 new tests, 15,498 collected.

## PRIORITY 1 -- PROCESS_NOT_EVENTS.md: ACQUISITION FUNNEL (second in declared sequence)
Staged, Tier 2 (design note docs/design/PROCESS_MODEL.md already reviewed and pre-approved via
docs/staging/done/PREAPPROVE_PROCESS_MODEL.md). Churn journey (first) shipped via Phase QL.
Next: awareness -> consideration -> quote -> application -> credit check -> onboarding ->
cooling-off, with stage-level leakage observable to the company and supplier levers per stage
(price position, acquisition cost, onboarding friction) -- makes CAC real and gives the
acquisition-aware retention guard a genuine funnel to price against. Debt-branch extension
(engagement/avoidance behavioural split, generalizing QD's arrears pattern) is third; DCA-placement
/ debt-sale stage (SAAS_COVERAGE_MAP.md item 3) can fold into the same debt-branch phase.

## Backlog
- Further correlated-generator scenarios, extended stress suites, shadow-live index page
- C2/C3/C4 resi EAC benchmarking vs Ofgem TDCV by dwelling type
- Smart meter customers on real HH shapes for segment model
- EPC-calibrated consumption distributions (requires GOV.UK data access)
- BSUoS year-indexed actuals
