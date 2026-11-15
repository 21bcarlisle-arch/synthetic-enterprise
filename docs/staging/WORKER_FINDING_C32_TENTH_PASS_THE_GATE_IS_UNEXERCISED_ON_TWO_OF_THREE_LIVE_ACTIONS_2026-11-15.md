**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 3 · **Atom:** `C32_one_obligation_one_vulnerability_scorer`

# The enforcement gate is unexercised on two of its three live actions, and its own-hold column is wired off (2026-11-15)

Found by C32's tenth blind pass, on a 2016 live run. The full record is
`docs/staging/records/WORKER_RESULT_C32_TENTH_EXPERT_HOUR_THE_GATE_IS_TESTED_IN_OPERATION_ON_ONE_ACTION_OF_THREE_2026-11-15.md`.

## What was measured

On `main(report_end="2016-12-31")`, `may_take` was asked 6 times, all on the Consent offer
(5 permitted, 1 refused). The debt objection never reached the gate: its one request stopped on
the 28-day filter. Meter recovery was never asked, because no meter moves while
`method_prepayment_offer_take_up_share` is 0.

## The classes, in order of what they block

1. **Unexercised in operation** (owner C32). The DEBT_OBJECTION and METER_RECOVERY legs have only
   unit evidence.
   - *Done means:* a probe that sets take-up on in-process, over a window that includes 2021-05-04
     onwards, logs both legs of both actions.
   - *Constraint:* the curriculum value is not changed.
2. **The own-hold column is wired off** (owner C32).
   - The live desk's `own_holds` is None, so `collections_journey.py:864` and `:946` always pass
     False.
   - `company/interfaces/transfer_objection.request_debt_objection` never passes `own_hold` to
     `decide_debt_objection`, which defaults it to False.
   - So a COVERED cell on all three routed rows can never refuse live.
   - *Either:* wire the register.
   - *Or:* mark the column unrouted, with the reason, as `UNROUTED_ACTIONS` does for actions.
3. **One debt meter per billing account** (owner W2 meter book, with C32's check (e)).
   - `simulation/plan_offer_response.py:238` recovers a dual-fuel account's debt at the electricity
     rate on one meter.
   - The knowledge page does not state this.
   - Owed: name it in commons §5 as a simplification, or key the meter book by supply point.
4. **Plan re-offers 2-5 days apart** (owner: the collections desk, D lane).
   - ACC-SYN-2016-012 had 12 plan offers in 2016, including 07-15/07-17 and 09-16/09-18.
   - The trigger reads "a further bill missed".
   - Hypothesis, not yet tested: per-fuel bills on one account each count as a miss.
   - Contact frequency is a conduct question (SLC 0, the treating-customers-fairly standard).
5. **An offer of nothing satisfies 27.8** (owner C32).
   - The CONSENT_PPM_OFFER check reads `arrangement_offered` as a boolean.
   - All 69 live offers carry `instalment_gbp: null` while the world's take-up is off.
6. **No payment method on `EnforcementCase`** (owner C32). A Consent PPM offer cannot be refused
   because the account is already on prepayment.
7. **"Negative" printed over unanswered evidence** (owner C32). In `_suitability_check`, the refusal
   is correct but the reason misdescribes it.

Fixed in the same tick: the world's concealing count was taken before the journeys' end-of-run
advance (4 counted, 5 made). It now comes after the journeys, under a control.

NEXT: C32_one_obligation_one_vulnerability_scorer
