**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The world reacts in full to one pain point in seven, and its renewal-shock reaction is the supplier's own churn curve (2026-10-30)

This answers the director's 07:30 question, "Is the SIM making customers react and behave to pain
points?". The audit asked for is in
`docs/staging/advisor/DIRECTOR_STEER_PAIN_POINTS_DRIVE_THE_LOOP_KNOWLEDGE_THEN_SIM_REACTION_THEN_SUPPLIER_TESTS_2026-10-30.md`.
It is a code reading of origin/main at 0637dace32, made by a census agent, with the two load-bearing
claims re-checked by the seat. Nothing was run. "Off" means off at its shipped default.

| Pain point | Does a world household react? | How, and where | Conditioned on | Evidence for the size |
|---|---|---|---|---|
| DD step-up | **Partly.** Departure is on. Mandate cancellation, extra collection failures and a complaint are built but **ship at 0** | Shock = reviewed DD > 15% above the one in force (`simulation/experienced_bill_shock.py`). This feeds the renewal hazard (`customer_events.py:749-774`). The other three legs are in `simulation/dd_shock_response.py` (`dd4b_*` toggles) | Payment-stress tier, for cancellation and failure | Complaint 2-6% (Ofgem/Citizens Advice survey). Cancellation and failure: "no source publishes" |
| Catch-up or shock bill | **Partly.** Calls only | Contact propensity rises with `bill_shock_pct` and bill clarity, times engagement (`simulation/contact_propensity.py`) | Engagement | "A modelling CHOICE, not sourced" |
| Run of estimates | **No** | Estimates are produced (`meter_reads.py`). Nothing reads the run's length | n/a | n/a |
| Refused refund or large credit | **No** | `credit_refund_events.py` logs the event for the supplier's compliance mechanic only | n/a | n/a |
| Billing error or complaint | **Partly.** A complaint roll and an Ombudsman escalation. No billing-error trigger | `feedback_survey.py` rolls a complaint per renewal term: 3%, plus 35pp on a rise over 20%, times occupancy. Escalation is 8%. `FrictionEventType.BILLING_ERROR` is never recorded. `complaint_generation.py`, the sourced generator, has **no caller** | Occupancy only | 3% / 35pp / 8%: none cited |
| Debt letter | **Partly.** Pays on time a little more often | Tone match +3 to +10% on the on-time probability (`nudge_physics.py`, via `arrears_engine`) | Hidden tone susceptibility | Cabinet Office / BIT, +3 to +10pp |
| Price rise or renewal | **Yes** | Renewal departure hazard (shock, market position, income stress, tenure), SVT inertia exit, SERL price elasticity of demand from 2022, and the complaint roll above | Payment stress, engagement, tenure, occupancy | Departure level fitted to published switching bands; SERL elasticity; shock weight 0.50 "declared" |

## What this means for the loop

- **The supplier has nothing to optimise against in three areas: estimate runs, credit balances and
  billing errors.** In two more it has only a call or a small payment effect: catch-up bills and debt
  letters.
- **The reactions the steer names first are built and switched off:** DD cancellation, DD failure and a
  complaint about the DD. They are the cheapest SIM enhancement to test, because the mechanism exists
  and only the strength is open. Their strengths are mostly unsourced, which is what the two evidence
  packs are for.
- **Resentment drives nothing.** Friction events are logged, and `churn_journey` is logged only
  (`customer_events.py:1623`: "nothing in the run loop reads a journey").
  - Satisfaction lowers churn only above 0.80. That is deliberate and sourced: Ofgem CIM wave 6 Table 56
    shows dissatisfied households switch less.
- **Vulnerability conditions no reaction.**

## The wall-shaped item (raised here, not fixed)

The world's renewal-shock hazard is the **supplier's** function.

- `simulation/customer_events.py:32` imports `churn_probability` from `saas.churn_model`, and line 770
  uses it in the world's departure dice.
- `CHURN_UPLIFT_PER_BILL_SHOCK` is therefore the supplier's belief and the world's truth at once. A
  supplier graded on predicting churn after a shock is graded against its own curve, so the world
  cannot defeat it on that leg.
- This breaks W7's "truth stays an instrument" and the coupled-triad principle ("the world must be able
  to defeat the company").
- **The fix belongs to the world:**
  - Give the shock uplift its own world-side draw, sourced from the evidence packs' reaction evidence.
  - Leave the supplier's constant as its belief, graded against that draw.
- This is a SIM enhancement under the steer's order of work. It is drawn after the correctness exit
  test, unless that test needs it.

## Filing

The steer asks for the SIM enhancement and the supplier experiments to be filed "on the
customer-outcomes roadmap". **No such file exists** (searched `docs/`). Until one is made, this finding
is that file's first entry. It carries three candidates:
- (a) switch on and source the DD4b legs;
- (b) the world's own shock uplift (the wall item above);
- (c) a household reaction to estimate runs and to held credit.

These come in that order, because (a) needs no new mechanism.
