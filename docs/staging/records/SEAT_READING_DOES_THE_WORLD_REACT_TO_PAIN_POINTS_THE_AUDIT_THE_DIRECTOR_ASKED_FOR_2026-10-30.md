**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# Does the world make customers react to pain points? The audit asked for on 30 Oct (2026-10-30)

Answers the "Ask now" in `docs/staging/advisor/done/DIRECTOR_STEER_PAIN_POINTS_DRIVE_THE_LOOP_KNOWLEDGE_THEN_SIM_REACTION_THEN_SUPPLIER_TESTS_2026-10-30.md`.
It is read-only, at origin/main 38960f39cc, over `simulation/` and `sim/`. A Sonnet census did the
sweep. The seat re-checked two of its claims by hand: `simulation/complaint_generation.py` is
imported by nothing but its own test, and the DD4b responses in
`docs/market_research/assumption_toggles.yaml` default to 0.0. Both held.

## The answer

**Mostly no.** Price is the only pain point a world household reacts to fully, with its evidence
cited. Three pain points have no reaction at all. On those, the supplier has nothing to optimise
against.

| Pain point | Reacts? | How, today | Conditioned on | Evidence behind it |
|---|---|---|---|---|
| Price rise or renewal | **Yes** | departure hazard from price position and elasticity; a roll to shop at renewal; inertia on the default stock; supplier contact wakes a share | engagement, elasticity, stress, tenure | anchored to the GB switching record; Ofgem EFTC trials; Ofgem 2018-19 and CMA 2016 |
| DD step-up | **Partly** | a rise over 15% raises the departure hazard (live). Mandate cancellation, DD failure uplift and complaint are coded but **ship at 0** | payment stress (scales unsourced) | the 15% cut is "INHERITED, NOT SOURCED"; the page says no cancellation rate is published |
| Catch-up or shock bill | **Partly** | raises the odds of a call; the complaint uplift is keyed to a unit-rate rise, not to the bill | engagement, household size | contact constants a modelling choice; complaint rates unsourced |
| Billing error or complaint | **Partly** | a complaint goes to the desk; an Ombudsman escalation (8%) feeds reputation. The resentment ledger is kept but **does not feed the churn roll**, and `BILLING_ERROR` is never raised | household size | Ombudsman figures unsourced; the 56-day window is the licence's |
| Debt letter | **Partly** | tone moves on-time payment (live). Plan take-up and early contact **ship at 0** | hidden tone susceptibility, stress | Cabinet Office/BIT; PFRC/StepChange |
| Run of estimates | **No** | nothing reads the run. Estimates and catch-ups are produced and nobody reacts to the estimates | none | none |
| Refused refund or large credit balance | **No** | the refund log grades reg 6D only; a falling DD is excluded as "not a shock" | none | none |

The household sees the DD amount, its bills (with `bill_shock_pct`, catch-ups folded in), a letter's
tone and supplier contacts, each through the seam. It never sees an estimate's flag as a
behavioural input.

## The gaps, ranked by what they cost the loop

1. **A run of estimates, and a large credit balance, have no reaction.** Both sit in the
   second area, unbilled energy, so that area's supplier experiments would grade against a world that
   cannot press back.
2. **Built and switched off.** The DD4b responses, plan take-up and early contact all ship at 0, and
   `complaint_generation.py` (cause-driven complaints, Ofgem/GfK 2014 and Ombudsman 2024 shares) is
   wired to nothing. The cheapest way to move any of these is to source the strength. Switching one
   on without a source would be inventing it.
3. **Resentment is kept and goes nowhere.** Friction is tracked per household, but
   `churn_journey.py` says it "does not decide switch-vs-stay". A billing error therefore costs the
   supplier nothing it can see.
4. **Most reaction strengths are unsourced.** The two pages that tried to find a source say none is
   published: `communications_sentiment_and_nps.md` §6.1 and
   `does_a_bill_shock_event_raise_the_odds_a_household_shops.md` ("NOT ESTABLISHED"). The advisor's
   evidence packs are the place to close this.

## What this means for graded outcomes now

The correctness stretch grades **records**: bills, reads, pages. None of these gaps moves an
invariant row. Outcome metrics are different: complaints, churn after shock, and arrears in year one
read only the reactions in the table. Until rows 1 to 3 have a sourced reaction, a supplier variant
that cuts estimates or refunds a credit balance would show **no** outcome change. That would be
an absent mechanism, not a finding.

## Filed

The SIM enhancement (one sourced reaction per pain point, hidden from the supplier) and the supplier
experiments go on the customer-outcomes list in `docs/direction/priority_order.yaml`, drawn after
the correctness exit test, as the steer orders.
