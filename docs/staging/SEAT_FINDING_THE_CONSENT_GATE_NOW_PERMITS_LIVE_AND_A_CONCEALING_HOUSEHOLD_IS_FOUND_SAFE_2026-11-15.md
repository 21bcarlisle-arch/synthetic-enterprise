**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 3 · **Atom:** `C32_one_obligation_one_vulnerability_scorer`

# The Consent gate now permits live, and a household that conceals is found safe (2026-11-15)

Found building W2_43, the two world doors C32 ninth pass item 1 waited on. Knowledge pages: commons
s.5, "The S&RP conversation" and "The PPM's supply events, and the 27A watch on them".

## What changed live

- **Door 1, the S&RP conversation** (`SimInterface.ask_prepayment_suitability`). At the Consent
  rung the desk now asks the household. The household answers from its hidden state.
- **Door 2, the meter's reports** (`SimInterface.get_meter_supply_events`). The desk's own 27A
  watch reads this door at every advance. The watch's record lapses the day after its last read.
- **Before:** every live Consent offer was withheld, on two grounds: no S&RP finding and no watch.
- **After:** no live withhold names either ground. A household found S&RP is offered
  (`test_a_live_run_withholds_the_prepayment_offer_at_the_ninety_day_rung`, re-keyed to that
  property).
- *Superseded later on 15 Nov (C32 tenth pass, item 5):* on the shipped world every live Consent
  offer is withheld again, on one ground: no arrangement offer was answered (27.8). The S&RP and
  watch grounds stay clear. With the world's plan answers on in-process, households found S&RP are
  offered, and the concealing count is checked on that run. On a shipped run it reads 0.
- **No meter moves yet.** `method_prepayment_offer_take_up_share` is still 0, so the world refuses
  every offer.

## What the world can now do to the company

- **A PSR-type household that does not disclose answers every question "no".** It is the same
  `discloses_psr` draw that decides PSR registration. The company finds it S&RP and offers it a
  meter. That is the world pressing back, and the company cannot see it.
- **What that means once take-up is on.** Some of the meters moved will be harms that no control
  in `company/` can detect. That is correct. It is also unmeasured: nothing counts, behind the
  wall, the offers made to concealing households.
- **What is owed: a world-side count.** The count is of offers made to PSR-type households that
  concealed, and it is truth. It belongs in the run's result, beside `psr_registrations`, and must
  never cross the wall.

## Still not built (GAP, in order)

1. **The 27A.5 response.** *(Built 2026-11-15, C36: commons s.5 "The 27A.5 response". Each
   interruption seen on a meter the desk fitted gets ASC (amount None, GAP E6), one contact attempt per
   residential channel, and a §9.1(b) referral from the second; the world-side count
   `consent_offers_to_concealing_households` sits beside `psr_registrations`. The world-side count
   item under "What is owed" is met by the same commit. Not built: what the household does with the
   contact or the credit; no world door answers either. `ppm_emergency_credit_register.py`'s £5/£10/
   28-day constants are unsourced and are not reached by this path.)* The watch keeps every interruption it sees
   (`CollectionsJourneyDesk.self_disconnections`). Nothing acts on them. Not built: emergency or
   friendly credit, Additional Support Credit, multi-channel contact, and the §9.1(b) S&RP
   re-assessment after frequent or prolonged self-disconnection.
2. **Recovery through the meter while the household is self-disconnecting.** That table cell is
   still GAP. The world takes the weekly deduction regardless (simplification 5).
3. **The interruption rate.** It is derived from the whole smart-PPM stock, using a denominator
   from other dates (`ppm_debt_self_disconnection_weekly_share`). No per-household or debt-PPM
   rate is published. Top-ups and interruption durations are not drawn.
4. **Disclosers' answers.** A discloser answers every question "unanswered", because no needs code
   is drawn. Meter location (3.7 "cannot access") is not drawn. That errs FOR the company.

NEXT: C36_a_self_disconnection_the_watch_sees_is_answered_with_support
