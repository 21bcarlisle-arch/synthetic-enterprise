# Design Note: Processes, Not Events

Staged: docs/staging/PROCESS_NOT_EVENTS.md (2026-07-04), pre-approved sight-unseen by
docs/staging/PREAPPROVE_PROCESS_MODEL.md. Companion to docs/staging/DECISION_LOOP_AND_EVENT_LEDGER.md
(company-side moments-of-truth) -- this note is the SIM-side twin: the hidden-state journey the
company's decisions react to.

## 0. The one finding that reframes the whole build

Before designing anything new: most of the physics this directive asks for already exists in this
repo, built and unit-tested, and was never wired into the live simulation loop or a business
surface. From an earlier "CTO Architecture Guidance" round (Phases DZ/EA/EB/ED, dates predate the
current build log):

- company/core/event_ledger.py (Phase DZ) -- typed, immutable, timestamped event bus
  (EventDomain, EventType incl. CUSTOMER_CHURNED, RENEWAL_NOTICE_SENT,
  RETENTION_OFFER_MADE, COMPLAINT_RAISED). This IS the event ledger
  DECISION_LOOP_AND_EVENT_LEDGER Part 5 asks for.
- company/core/resentment_ledger.py (Phase EA) -- a decaying stock accumulator
  (FrictionEventType -> score, -1pt/month decay) that triggers irreversible churn when cumulative
  resentment crosses a personal threshold. This IS the content-to-irritated transition mechanic.
- company/core/reputation_index.py (Phase EB) -- Global Reputation Index (GRI), banded
  STRONG/ADEQUATE/WEAK/CRISIS, driven by ReputationEventType (complaint handling, Ofgem
  enforcement, ombudsman upholds). This IS most of FEEDBACK_AND_REPUTATION Layer 2's "regulator-style
  rating."
- company/core/activation_energy.py (Phase ED) -- per-customer Status Quo Bias barrier; an action
  (switch/complain/escalate) only fires when Perceived Utility of Action exceeds it, modulated by
  GRI, tenure, resolution history. This IS the "in-market" entry-probability gate PROCESS_NOT_EVENTS
  Part 1 describes ("entry probability shaped by satisfaction, elasticity, inertia/activation
  energy").
- company/crm/retention_risk.py -- company-observable risk scorer (overdue invoices, recent
  complaint, renewal window, rate exposure, no smart meter) -> LOW/MEDIUM/HIGH tier. This IS most of
  DECISION_LOOP_AND_EVENT_LEDGER Part 1's "moments of truth" trigger logic.
- company/crm/contact_journey.py -- multi-channel contact/preference tracking, wired into
  company/portal/app.py (the only one of these five already live, but only in the portal, not the
  simulation loop).

Every one of these has a real, passing unit test and zero non-test importers except
contact_journey.py. A grep for "company.core.event_ledger" across the repo (excluding __pycache__)
returns only its own test file, and the same is true for resentment_ledger, reputation_index, and
activation_energy. They were built to spec and then never connected to simulation/run_phase2b.py,
never fed by real settlement data, never read by any dashboard/shadow-site generator.

This changes the implementation plan from "build new behavioral physics" to "wire existing
physics into the live run, replace the ad-hoc bits it was meant to replace, and fill the two real
gaps (state-machine orchestration, observable-exhaust split) that don't exist yet." Section 3 below
is a wiring plan more than a from-scratch design.

## 1. What's wrong with the current model (the "events" critique, concretely)

simulation/customer_events.py::roll_lifecycle_event() is called exactly once per renewal
(annually, sometimes less for I&C multi-year deals) from simulation/run_phase2b.py. Between
renewals, a customer's churn risk is invisible -- nothing accumulates, nothing decays, nothing is
observable. The company-side satisfaction proxy (company/crm/satisfaction_accumulator.py) already
has a monthly decay (_MONTHLY_DECAY_RATE = 0.01, reverting to baseline 0.70), and Phase QK (this
session, 2026-07-04) just demonstrated the consequence empirically: three passive renewers
(C1/C5/C6) crossed the risk threshold at one renewal, got a retention offer, were retained -- and
then churned 1-2 renewal cycles later once the signal had fully decayed back to baseline. The
company-vs-SIM churn classifier (company/analytics/churn_accuracy_report.py) scores only the
terminal renewal before departure, so a correctly-caught-then-decayed risk still reads as a false
negative. QK's own phase-close entry (PRIORITIES.md, PROJECT_OVERVIEW.md Section 4) names this
exact mechanism as the reason recall stayed at 0% even after fixing the passive-renewal signal gap.
This design note is the structural fix QK's finding calls for: model the customer as a
continuously-evolving process, not a once-a-year dice roll.

The same critique applies to acquisition (currently a single win/lose roll,
company/crm/customer_profitability.py / acquisition cost tables -- no funnel, no stage leakage)
and debt (already partially a process -- see Section 4 -- but not generalized).

## 2. Churn journey state machine (SIM-side, hidden state)

CONTENT -- friction accumulates --> IRRITATED -- in-market trigger --> IN_MARKET
-> COMPARING -> (STAY_SVT | SWITCH) -> POST_DECISION_WINDOW

Plus a parallel HOME_MOVE forced-churn subtype that can fire from any state (existing
household.py life-event machinery already models this; it bypasses the funnel entirely -- a mover
churns regardless of satisfaction).

State definitions and transition triggers:

- CONTENT: baseline. Entry: initial / post-decision reset. Building block: satisfaction_accumulator
  baseline (0.70).
- IRRITATED: friction accumulating, not yet shopping. Entry: resentment stock crosses a low
  threshold (not yet the churn threshold). Building block: resentment_ledger.py -- reuse the
  stock/decay mechanic, add an intermediate threshold below the existing "irreversible churn" one.
- IN_MARKET: actively receptive to switching. Entry: renewal letter sent, price-vs-market drift
  exceeds a calibrated gap, referral, crisis media event; entry probability gated by Activation
  Energy. Building block: activation_energy.py -- Perceived Utility of Action (bill saving vs
  friction/switching cost) must exceed AE; AE itself modulated by reputation_index.py GRI and tenure.
- COMPARING: evaluating market offers. Entry: entered IN_MARKET + observes a competitor offer
  (existing market_conditions.py switching-multiplier data informs the base rate here). Building
  block: new -- thin layer combining GRI (reputation-mediated conversion) and the existing
  rate-comparison math in company/crm/churn_model.py.
- SWITCH / STAY_SVT: terminal decision. Entry: dice roll gated by AE threshold + retention offer
  (existing roll_lifecycle_event). Building block: roll_lifecycle_event() becomes the
  COMPARING-to-decision transition, not the whole model.
- POST_DECISION_WINDOW: win-back eligibility. Entry: N months after SWITCH. Building block: new --
  thin, feeds the acquisition funnel's "win-back" channel later.

Life events modulate the whole chain, not just entry: IncomeStress (existing
simulation/switching_propensity.py) suppresses the CONTENT-to-IRRITATED-to-IN_MARKET progression for
HIGH-stress households (the vulnerability trap already modelled) and sim_satisfaction.py's
tenure bonus slows accumulation for loyal customers. No new stress/satisfaction model needed -- the
state machine is the orchestration layer these already-correct signals were missing.

HOME_MOVE short-circuits the whole machine: existing home-move life-event handling in
simulation/household.py fires a forced churn regardless of state. Keep as-is; just make sure the
event ledger records it distinctly from a satisfaction-driven churn (they must not be counted
together in any recall/precision metric -- a home-mover was never "catchable").

## 3. Epistemic split -- what the company actually observes

SIM holds the true state (CONTENT/IRRITATED/IN_MARKET/COMPARING and the underlying resentment
stock, AE, income stress). The company must NEVER read state directly. Observable exhaust, mapped
to real company-side modules:

- Resentment stock rising (entering IRRITATED) -> Complaint raised, billing dispute, contact-centre
  call volume/sentiment. Existing module: company/crm/complaint_register.py,
  company/crm/contact_log.py, company/crm/contact_centre_metrics.py.
- IN_MARKET entry -> Renewal-window opening (company already knows term-end dates), portal
  quote-tool usage if realistic, price-vs-market gap (company computes this from its own tariff vs
  market_conditions.py). Existing module: company/crm/retention_risk.py renewal-window flag already
  covers this.
- COMPARING -> No direct signal -- this is the epistemically honest gap. Company infers via
  retention_risk.py's composite score, nothing more. Existing module: none, by design.
- Activation Energy / GRI -> Not observable at all -- internal behavioral parameter. Company's only
  proxy is its OWN complaint-resolution timeliness and Ofgem/ombudsman outcomes, which is exactly
  what reputation_index.py's ReputationEventType table already tracks from the company's own
  actions. Existing module: reputation_index.py.

The company's churn model (company/crm/churn_model.py + enriched_churn_estimate.py, including
this session's QK enrichment) should be re-expressed as: estimate P(IN_MARKET or beyond) from
observable precursors -- retention_risk.py's composite score is the natural feature vector. This
is the concrete mechanism by which "recall improves because precursors now exist, not because the
math was tortured" (PROCESS_NOT_EVENTS.md's own acceptance bar).

## 4. Debt as a process (generalize, don't rebuild)

QD (Phase QD, 2026-07-04) already built the shape: simulation/arrears_engine.py's
stress -> timing-drift -> miss -> arrears -> plan -> write-off pipeline. What's missing per
PROCESS_NOT_EVENTS.md and SAAS_COVERAGE_MAP.md:
1. Engagement/avoidance behavioural branch -- same arrears state, two customer archetypes
   (engages with payment plans vs avoids contact entirely; "overwhelmed, not delinquent" per the
   pitch's Stockport case). Slot into arrears_engine.py's existing per-customer state, gated by
   income_stress trajectory shape (a HIGH-stress customer who was previously LOW is more likely
   "overwhelmed"; a customer with a long HIGH-stress history is more likely "avoidant").
2. DCA-placement / debt-sale stage (SAAS_COVERAGE_MAP.md item 3) -- extend past WRITTEN_OFF with
   placement windows, recovery-rate economics, sale-price-vs-book haircut. New terminal states after
   WRITTEN_OFF, not a redesign of the existing engine.

Sequenced third, after churn journey and acquisition funnel, per PROCESS_NOT_EVENTS.md's own
ordering.

## 5. Acquisition funnel (sequenced second)

awareness -> consideration -> quote -> application -> credit_check -> onboarding -> cooling_off.
No existing dormant module covers this one -- it's a genuine gap, unlike churn and debt. Keep it
thin at first pass: stage-level conversion rates calibrated to published UK switching-site/broker
conversion benchmarks (population-anchoring discipline applies here too -- same pattern as
tools/population_anchor.py's existing switching/complaint/arrears checks), with the acquisition
cost tables already in company/crm/customer_profitability.py attaching per-stage instead of as a
single lump sum. SAAS_COVERAGE_MAP.md's credit-bureau boundary feed (item 4) attaches at the
credit_check stage specifically -- a purchased, imperfect external signal, modelled as an
epistemic-boundary adapter (same pattern as the market-feed swappable adapter, Phase PV).

## 6. Calibration anchors (population-anchoring discipline, per stage)

Every stage-transition rate must aggregate to the same published benchmarks
tools/population_anchor.py already checks in aggregate:
- CONTENT-to-IRRITATED-to-IN_MARKET cumulative annual rate must reproduce Ofgem's published annual
  switching rate by year (_churn_by_year benchmark table already in population_anchor.py).
- Resentment-stock friction event frequency must reproduce Ofgem/Citizens Advice complaint-volume
  benchmarks (_complaints_check).
- Debt-branch stage rates must still satisfy _arrears_check_by_year's DESNZ bands.
This is a gate, not a one-off check: any stage-rate change must re-run population_anchor.py
before shipping, same as today.

## 7. Interface to DECISION_LOOP_AND_EVENT_LEDGER (company-side twin)

The decision loop's "moments of truth" triggers ARE this state machine's transitions, observed
through the exhaust mapping in Section 3:
- Renewal window opening -> triggers regardless of state (existing behaviour, unchanged).
- Price-competitiveness drift -> company-computed, independent of SIM state (existing).
- Service-recovery event -> complaint/billing-error exhaust from an IRRITATED-state customer.
- Payment-stress signal -> already modelled (Phase MW/NG/NH + this session's QK).
Each trigger firing logs a decision (EV of each option, chosen action, H1 EV) to
company/core/event_ledger.py -- finally wiring it into a live data path -- which becomes the
Decision Event Ledger surfaced on the business tabs.

## 8. Implementation sequencing (per PROCESS_NOT_EVENTS.md + PREAPPROVE_PROCESS_MODEL.md)

1. Churn journey first (next phase, QL candidate): wire resentment_ledger.py +
   activation_energy.py + reputation_index.py into a new orchestration module
   (simulation/churn_journey.py) called at every settlement period, not just renewal; re-express
   retention_risk.py as the company's observable-precursor feature vector; evidence on all three
   surfaces (a named customer's state trajectory, both sides of the wall).
2. Decision-loop triggers on journey stages -- wire event_ledger.py for real, attach EV logging.
3. Event ledger surfaces (customer timeline + portfolio event stream).
4. Acquisition funnel (Section 5) -- genuine new build.
5. Debt-branch generalization (Section 4) -- extend arrears_engine.py.
6. Design system (Part B) / per-fuel portal depth (Q5) fill in parallel per
   PREAPPROVE_PROCESS_MODEL.md.

Each of 1-5 is its own phase with its own tests, epistemic-verifier pass, and evidence-surface
retrofit -- this note does not authorize skipping the phase-close checklist for any of them.
