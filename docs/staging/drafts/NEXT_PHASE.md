# NEXT_PHASE.md -- Proposed Phase RU (Tier 3 design note)

**Source:** docs/staging/FEEDBACK_AND_REPUTATION.md (front of PRIORITIES.md P2 queue, staged
2026-07-05, [ADVISOR-STAGED] d017b4bd). Its own text: "Tier 3 for the design (novel scope, 4h
window unless Rich pre-approves); implementation Tier 2 after." This is that design note.
Classification: **Tier 3 (novel) -- proceeding 4h unless redirected**, per CLAUDE.md's tiered
approval model (nothing here touches the epistemic law, a one-way door, or a safety control --
it's new company-side modelling, reversible, no scale/architecture jump).

## What already exists (audited this session, Explore agent, so this isn't built blind)

- company/crm/nps_tracker.py -- pure NPS aggregation math. **Orphaned**: no code feeds it real
  responses; a survey/response-bias generator does not exist yet.
- company/core/reputation_index.py (GlobalReputationIndex, Phase EB) -- portfolio score
  0-100 (STRONG/ADEQUATE/WEAK/CRISIS), activation_energy_multiplier() read by
  simulation/churn_journey.py per customer. **Half-wired**: nothing ever calls gri.record(...),
  so it's permanently pinned at the default (50, ADEQUATE, 1.0x) in every live run -- the
  multiplier machinery runs on dead data. Not surfaced on any site page.
- company/core/resentment_ledger.py + activation_energy.py -- per-customer friction
  accumulator + status-quo-bias barrier. **Live and wired** via churn_journey.py into
  run_phase2b.py, surfaced on Customers tab labeled "visible to us but never to the company."
  Nothing to build here -- reuse as-is, per the DZ-ED "wire don't rebuild" precedent
  (docs/staging/done/QL_WIRE_AND_DEFERRAL.md).
- company/portal CSAT widget (ServiceLog.rate_contact) -- a manual 0-5 rating on every
  contact, no response-rate modelling, no bias. Seed to extend, not a duplicate.
- Satisfaction ground truth (simulation/sim_satisfaction.py) and the company-side proxy
  (company/crm/satisfaction_accumulator.py) are already correctly separated -- checked all
  company/saas imports of simulation.* for a direct read, found none. **No existing
  epistemic-wall violation to fix** (the doc flagged this as a risk to verify; it's clean).
- Complaints exist only company-side (company/crm/complaints.py, Ombudsman 56-day SLC timer);
  SIM only supplies avg_complaint_probability (a propensity, phase-4c contact model), not a
  volume distribution.
- No Trustpilot-class review generation or regulator star-rating exists anywhere.

## Proposed scope for Phase RU (this phase -- the achievable next slice)

Full FEEDBACK_AND_REPUTATION.md scope is two layers + two loops + decision levers + evidence
surfaces -- too large for one phase (same pattern as SIM_TAB_OVERHAUL/WEBSITE_AS_SHOWCASE, which
took 6+ phases). Sequencing by the two-way-door filter: Layer 1 (measurement) doesn't depend on
Layer 2 (public reputation); the loops depend on both existing first. Phase RU takes the
foundation slice:

1. **Solicited-feedback engine (Layer 1 core).** New simulation/feedback_survey.py: post-event
   CSAT dispatch (after contact/complaint/home-move/onboarding events already in the event log)
   and a quarterly NPS campaign, both with realistic response propensity -- single-digit-to-low-tens
   % base rate, U-shaped (very satisfied + very dissatisfied respond, the silent middle doesn't),
   modulated down by IncomeStress/emotional state (the overwhelmed don't answer surveys). Response
   value itself derives from sim_satisfaction_score plus response-report noise (a real respondent
   reports a noisy/rounded version of their true state, not a clean read) -- this is what makes it a
   measurement instrument rather than an oracle.
2. **Wire it as nps_tracker's real data source.** Company-side: survey responses feed
   NPSTracker for real (closing the orphaned-code gap) and extend satisfaction_accumulator.py
   to also ingest CSAT responses as an observable, alongside its existing bill-shock/complaint
   inputs. Epistemic check applies here specifically: the company must only ever see the response,
   never the underlying sim_satisfaction_score used to generate it.
3. **Basis-risk display.** Sim tab correlation panel: measured CSAT/NPS (company's biased
   instrument) vs SIM-true satisfaction, both lines, same chart -- the gap is the product insight.
   Customers tab: at least one named account whose true satisfaction dropped but who never
   responded to any survey (the "silent-middle churn" case the doc calls out).
4. **Feed the GRI for real.** Cheapest, highest-leverage fix in this audit: wire actual
   ReputationEventType events (complaint outcomes, SLC breaches already tracked in
   company/crm/complaints.py) into gri.record(...) inside run_phase2b.py's per-customer loop.
   This alone turns activation_energy_multiplier() from permanently-inert to live, and is
   pure wiring of an existing Phase EB module -- no new modelling required.

**Deferred to a follow-on phase (RU cont. or RV), not started this phase:** Layer 2 public
reviews (Trustpilot-class) + population-anchored regulator star rating; the two loops (reputation
-> acquisition funnel conversion, reputation -> in-market entry probability); company decision-loop
levers (service recovery spend as an EV decision). These need Layer 1 + a live GRI in place first
(the two-way-door filter), and each is substantial enough to be its own phase given past pacing on
staged docs this size.

## Evidence rule (per CLAUDE.md 0b, for this phase's slice)

- Sim tab: CSAT/NPS-vs-true-satisfaction correlation panel, live.
- Customers tab: one named account with a real post-event survey response (or a real
  no-response/silent-middle case), dates and values from the actual run.
- Supplier tab: company CSAT/NPS dashboard reading only survey data, GRI score now moving
  (not pinned at 50) with at least one real event shown driving it.
- Project tab: spec archive only, per standing rule (0a) -- not primary evidence.

## Risk / reversibility

Fully additive (new simulation module + wiring calls), no schema migration, no scale change,
no touch to the epistemic law itself (this phase's own audit confirms current company/saas
code is already clean -- it extends the observable-only pattern, doesn't loosen it). Reversible:
new module can be unwired without touching existing resentment_ledger/activation_energy/churn_journey
mechanics. Classified Tier 3 only because the shape of the feedback-bias model is novel design,
not because it's risky.

**Proceeding in 4h unless redirected**, per the doc's own stated process and CLAUDE.md's Tier 3
opt-out window.
