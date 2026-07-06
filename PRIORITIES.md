# PRIORITIES.md -- Synthetic Enterprise
# Last refreshed: 2026-07-06 (PRIORITY RESET, docs/staging/PRIORITY_RESET_PUBLIC_SITE.md,
# [ADVISOR-STAGED] 5fa9a0cf -- Tier 2, pre-approved). Rich's direct verdict: the public site
# (poesys.net's four top-level tabs) is still structurally pre-overhaul despite backend depth
# (SIM tab QY-RC, Project generators RD/RG, portal design tokens QO) shipping. THE PUBLIC SITE
# IS NOW P1, ahead of further backend depth (CTS reconciliation, frozen-policy baseline,
# FEEDBACK_AND_REPUTATION, NUDGE_PHYSICS, SAAS_COVERAGE_MAP all demoted to P2, resume after P1
# lands + Rich confirms visually). "Overhaul" means structure/nav/tab-order/layout/per-fuel
# separation on the REAL site (site/{index,sim,customers,project} + the portal), not the shadow
# mirror, not a CSS palette flip.
#
# NEW ORDER (work top-down, single-writer, each Tier 2/pre-approved):
# P1a. CUSTOMER 360 v4 (docs/staging/CUSTOMER_360_REDESIGN.md) -- reference implementation.
#   Household w/ TWO first-class accounts (elec MPAN + gas MPRN, own tariff/meter/consumption/
#   bills/P&L each), combined roll-up OPTIONAL only; tabbed IA (Overview/Accounts/Consumption/
#   Billing/Timeline/Risk); usage viz (volume+shape+weather overlay); bill equation + why-different
#   waterfall; QP event ledger as timeline; progressive disclosure; UK lens (MPAN/MPRN/p-kWh/EAC/
#   PSR). GAS/ELEC SEPARATED AT EVERY STAGE is the specific repeated complaint -- highest priority
#   sub-item. (Phase RI closed v3's item 1 usage-chart rendering; Phase RJ closed the tabbed IA +
#   account-separation ask; Phase RK closed item 2 -- bill equation + why-different waterfall, real
#   billing_ledger.json data now wired into the customer JSON in place of the old fabricated
#   seasonal-weight invoices. Still open: item 3 (event downstream effects on Timeline), item 4
#   (reaction-loop rendering: bill shock -> complaint -> satisfaction -> offer -> outcome).)
# P1b. SUPPLIER TAB IA (docs/staging/SUPPLIER_TAB_OVERHAUL.md). Phase RH already closed the core
#   IA regroup (grouped nav + Query FAB) and RG closed Capabilities->Project + Regulatory RAG +
#   Worst-Shock-Month; remaining: portfolio event stream as spine, Recommended Actions elevated
#   to Overview, heatmap click-through to customer 360 + year.
# P1c. SIX-SECTION NAV + STORY (docs/staging/NAV_STORY_PLATFORM_METHOD.md) -- Home/Story landing,
#   new Platform + Method sections, tab reorder. Not yet started.
# P2 (resumes after P1a-c land + Rich's visual confirmation): CTS £0/£91,780 reconciliation
#   (docs/staging/drafts/NEXT_PHASE.md), frozen-policy baseline (FROZEN_POLICY_BASELINE_DESIGN.md),
#   FEEDBACK_AND_REPUTATION.md, NUDGE_PHYSICS.md, SAAS_COVERAGE_MAP.md.
# Acceptance for every P1 item: Rich's eyes on the live public page -- report "awaiting Rich's
# visual review", never "done" outright.
# Already-staged infra fixes (SERIALIZE_WORKERS.md, FLAG_ALL_LAUNCHERS.md, PAGES_CONCURRENCY_FIX.md)
# were actioned prior to this reset -- see docs/staging/done/.

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

## COMPLETED (cont. 4)
- PROCESS_NOT_EVENTS.md: FULLY DELIVERED, all three items in its declared sequence (2026-07-05).
  Churn journey (Phase QL) -> acquisition funnel (Phase QR) -> debt-branch (Phase QS: DCA
  placement/recovery/sale past WRITTEN_OFF, with debt_archetype() OVERWHELMED/AVOIDANT/NEUTRAL
  behavioural split generalizing QD's arrears pattern). SAAS_COVERAGE_MAP.md item 3
  (DCA-placement/debt-sale) folded into QS as designed. Staged instruction archived
  (docs/staging/done/, "Archive PROCESS_NOT_EVENTS.md" commit 56df5f86). SAAS_COVERAGE_MAP.md
  item 4 (credit bureau as boundary feed) partially done -- QR wired credit bureau into
  acquisition credit checks; the collections-strategy half is not yet fed by the same feed
  (minor backlog item, not blocking).

## PRIORITY 1 -- WEBSITE_AS_SHOWCASE.md design wave (six staged Tier-2 directives)
Staged 2026-07-05: NAV_STORY_PLATFORM_METHOD.md, WEBSITE_AS_SHOWCASE.md, SIM_TAB_OVERHAUL.md,
SUPPLIER_TAB_OVERHAUL.md, PROJECT_TAB_OVERHAUL.md, CUSTOMER_360_REDESIGN.md -- all Tier 2,
structure pre-approved by the directives themselves; Rich's eyes are the acceptance test for
each visual landing, not a code review.
Front of queue per WEBSITE_AS_SHOWCASE.md's own sequencing note: **Part 0** -- Phase QO
(design-system unification) styled company/portal/templates/ (the internal Flask portal)
instead of site/ (poesys.net, the four public tabs Rich actually looks at) -- a verification
failure, redo on the correct surface. Paired with **tab 1** (SIM tab living-world: event
frequency panels, journey-stage flows, correlation panels) since the underlying data already
exists (QL journey states, population anchoring, income-stress/satisfaction trajectories) --
no new SIM capability needed, only surfacing what is already computed.
STARTED 2026-07-05 (Phase QT, in progress): while auditing the SIM tab against
SIM_TAB_OVERHAUL.md's critique ("header cards say 0 moderate-stress while the table shows
C7/C8 moderate; Tenure and Satisfaction columns are dead -- every row a dash"), found the
root causes go deeper than styling -- three separate JS bugs on site/sim/index.html's
Customers sub-tab: (1) case-sensitivity (SIM emits lowercase 'low'/'moderate'/'high', JS
compared against uppercase literals -- silently broke the KPI header count, the stress
distribution chart, AND the per-row colour coding, not just the header/table contradiction
Rich saw), (2) `payment_behaviour_analytics.current_score` read a field that has never
existed (real key: `.score`) -- broke the Payment Behaviour Score Distribution chart, every
customer defaulting to GOOD, (3) `tenure_years` and `satisfaction_score` read fields that
don't exist on the customer record at all -- Tenure/Satisfaction columns were structurally
incapable of showing data. Root-caused (3): satisfaction had never been retained as a
per-year history, only a rolling current scalar (company/crm/satisfaction_accumulator.py) --
tools/generate_customer_sample.py hardcoded satisfaction_score_trajectory to None with a
"pending_sim_emission" status. Fixed at root: accumulator gains record_year_snapshot()/
get_trajectory(); simulation/run_phase2b.py snapshots at each renewal's term_start_str year;
generate_customer_sample.py wires the real trajectory through; site/sim/index.html computes
tenure from acquisition_date (fixed SIM_END_DATE=2025-12-31 reference, matching the 10-year
sim window) and reads the last trajectory point for satisfaction. 6 new/updated tests
(satisfaction accumulator trajectory + generate_customer_sample field passthrough), fast
suite re-run clean. NOT YET DONE: needs a fresh production sim run to emit real trajectory
data end-to-end (verified via unit tests only so far -- the live site/data/customer_sample.json
still shows the old null until the next natural sim_runner cycle regenerates it), and the
rest of WEBSITE_AS_SHOWCASE Part 0 + tab 1 (event frequency panel, journey-stage flows,
correlation panels, light-theme completion started by a prior ADVISOR-STAGED commit but not
finished) remains open.
CONTINUED 2026-07-05 (Phase QT, same session resumed after a restart): verified the trajectory
fix end-to-end against a fresh production run that completed mid-session (git 03fa5747) --
site/data/customer_sample.json now carries real per-year satisfaction history (e.g. C1: 2016
0.7, 2017 0.7, 2018 0.65) instead of null, closing the "NOT YET DONE" item above. Also shipped
JOURNEY STAGES LIVE (first slice of the "journey-stage flows" item): new "Customer Journey
Stages -- the Behavioural Pulse" section on the Customers sub-tab reads QL's journey_log
(already computed, dashboard.json, 92 entries/15 customers/4 states -- content/irritated/
in_market/comparing) and shows (a) current stage distribution as KPI cards (live run: 12
content, 1 irritated, 0 in-market, 2 comparing) and (b) a stacked bar chart of stage counts
per year 2016-2025, visibly showing in_market appearing in the 2022 crisis year. Verified with
a node harness executing the real data-transform functions against the live dashboard.json
(no browser tool available in this session) plus `node --check` for syntax -- both clean.
CONTINUED 2026-07-05 (Phase QU, same wave): shipped the remaining two of the four
"distributions" dimension -- Satisfaction Score Distribution (5 bands, critical/poor/fair/
good/excellent, stacked per year 2016-2025 from satisfaction_score_trajectory, already
computed by the Phase QT accumulator fix) and Switching Propensity Distribution ("the
Vulnerability Trap": each customer's income-stress trajectory point mapped through
simulation/switching_propensity.py's fixed multiplier -- LOW x1.10, MODERATE x0.85, HIGH
x0.65 -- no new SIM field, purely derived client-side from data the Income Stress chart
already displays). All four distribution dimensions (income stress, payment score,
satisfaction, switching propensity) are now live on the Customers sub-tab. Verified by
reimplementing both binning functions in Python against the live site/data/customer_sample.json
and confirming sane, crisis-consistent output (e.g. satisfaction "fair" band rises and "good"
drops in 2021-2022; switching-propensity "high" count dips exactly in the 2022-2024 stress
years) -- no node available in this session, `python3 -m tools.epistemic_verifier` PASS
(no company/saas files touched, site/ is presentation-only). Epistemic verifier PASS.
CONTINUED 2026-07-05 (Phase QX, same wave): event frequency panel was already shipped in QV.
This phase closes the remaining three tab-1 bullets: correlation panels (income stress vs
payment delay rate, and wholesale price vs journey-log in-market entries -- both from data
already computed; satisfaction vs complaints left as an explicit honest gap, complaints still
not wired into the live sim), per-customer click-to-expand trajectory sparklines (Customer 360
link honestly noted as pending CUSTOMER_360_REDESIGN.md -- that page doesn't exist yet, no dead
link fabricated), and a portfolio-scale Both-Sides-of-the-Wall strip (churn_accuracy_by_renewal's
sim vs company-estimated churn probability, aggregated per year -- shows the divergence narrowing
after Phase QQ's calibration fix). Tab 1 (SIM tab living-world) is now DONE except items 1-3
(Prices/Weather/BM sub-tab rebuilds, not part of item 4) and item 5 (site-wide consistency gate +
light theme). Rich's eyes are the acceptance test -- awaiting visual review.
Tab 2 (Supplier: frozen-policy-baseline delta-EV) needs its own Tier 3 design note first
(policy snapshot/replay is one-way-door-adjacent) -- do not start implementation before that
review lands. Tab 3 (Project: learning ledger) assembles as 1/2 land.
CONTINUED 2026-07-05 (Phase QY): SIM_TAB_OVERHAUL.md item 1 (PRICES -> MARKET) DONE -- selectable
price-chart overlay (HDD/Short%/Gas NBP), negative-price-hours/year chart, and a real year->month->
day progressive-disclosure drill-down on the annual table (daily rows built lazily, not pre-baked).
8 new tests, 15,595 collected, epistemic PASS. Tab 1 (SIM tab) now has only items 2 (Weather physics
chain), 3 (BM axis legibility), and 5 (consistency gate + light theme) remaining.
CONTINUED 2026-07-05 (Phase QZ): item 2 (Weather -> Physics Chain) DONE -- band chart replaces
spaghetti temp chart, new episode panel chains HDD -> price -> Short% for two named crisis
episodes. 4 new tests, 15,591 collected, epistemic PASS. Tab 1 now has only items 3 (BM axis
legibility) and 5 (consistency gate + light theme) remaining.
CONTINUED 2026-07-05 (Phase RA): item 3 (BM axis legibility) DONE -- both BM charts' x-axis fixed
to match the Prices/Weather convention, plain-language Short%/NIV explainer added, Crisis Zone
band added to the SSP-vs-Short% chart matching the Prices tab's same window, real cross-tab link
added. Presentation-only, no new tests, epistemic PASS. Tab 1 (SIM tab) now has only item 5
(site-wide consistency gate + light theme) remaining -- the last item before Tab 1 is fully DONE.
CONTINUED 2026-07-05 (Phase RB): freshness stamp (git_hash/phase) threaded into sim_data.json
metadata + an orphaned Customers sub-tab consistency-gate test committed. Item 5 partial --
freshness stamp still missing on Weather/BM/Customers sub-tabs, light theme unconfirmed.
CONTINUED 2026-07-05 (Phase RC): item 5 CLOSED -- freshness stamp extended to the three remaining
sub-tabs (shared freshnessSpan() helper reusing sim_data.json's metadata for Weather/Customers,
new buildBmMeta() for BM); weather.json's own generator now carries git_hash/phase too. Light
theme confirmed already shipped site-wide on site/sim/index.html, no work needed. SIM_TAB_OVERHAUL.md
now CLOSED IN FULL. Tab 1 (SIM tab) DONE. Found, not actioned: site/shadow/{index,customers,
supplier,project}/index.html still on the pre-v4 dark terminal-monospace theme -- WEBSITE_AS_SHOWCASE.md
Part 0 / PROJECT_TAB_OVERHAUL.md / SUPPLIER_TAB_OVERHAUL.md scope, front of queue next.

## COMPLETED (cont. 5)
- PROJECT_TAB_OVERHAUL.md R-A/consistency partial + WEBSITE_INTEGRITY_AND_DESIGN QW Part 2:
  DONE (Phase RD, 2026-07-05). site/data/phases.json regenerated from docs/PROJECT_OVERVIEW.md
  Section 4 via new tools/generate_phases_json.py (was hand-curated, frozen since 2026-07-03 at
  latest_phase OL) -- wired into process_run_complete.py so it self-updates every run. Fixes
  the stale Timeline, frozen Capabilities cards, and the corrupted Test Progression/
  Phases-per-day charts (duplicate x-axis labels). Also fixed the Project tab's "Sim runs"
  dead counter (always showed 10, the truncated run_history list length) via new
  count_run_history_total(). 9 new tests, 14,470 fast suite passed, epistemic PASS. Remaining
  PROJECT_TAB_OVERHAUL.md scope (R-D light-theme/visual polish, Company/Overview dedup, per-tab
  direction items 3-7) folds into the WEBSITE_AS_SHOWCASE.md Part 0 design wave below.

## COMPLETED (cont. 6)
- WEBSITE_AS_SHOWCASE.md Part 0: CLOSED (Phase RE, 2026-07-06). The shadow-mirror light-theme
  rewrite of tools/generate_shadow_html.py (flagged as remaining work at the end of Phase RC)
  had already been written by an interrupted prior session and its output already regenerated
  and committed by a live sim run -- but the generator source itself was never committed, a
  silent output-ahead-of-source gap. Verified complete (no dark-palette colors remain) and
  correct (new guard test `test_shadow_page_uses_v4_light_design_system` passes), then
  committed. Confirmed live in both site/shadow/ and docs/shadow/ committed HTML, all 4 pages.
  Also recovered tools/generate_customer_consumption.py (CUSTOMER_360_REDESIGN.md item 1 data
  layer: real per-fuel monthly/daily/load-shape kWh into site/data/customers/{cid}.json --
  frontend rendering still open). 1 new test, 15,739 collected, fast suite 14,477, epistemic
  PASS.

## Backlog
- SAAS_COVERAGE_MAP.md item 4 remainder: credit bureau feed into collections strategy
  (currently only feeds acquisition credit checks)
- FEEDBACK_AND_REPUTATION.md, NUDGE_PHYSICS.md: explicitly queued behind the current design
  wave per their own staged text -- do not jump ahead of PRIORITY 1 above
- Further correlated-generator scenarios, extended stress suites, shadow-live index page
- C2/C3/C4 resi EAC benchmarking vs Ofgem TDCV by dwelling type
- Smart meter customers on real HH shapes for segment model
- EPC-calibrated consumption distributions (requires GOV.UK data access)
- BSUoS year-indexed actuals
