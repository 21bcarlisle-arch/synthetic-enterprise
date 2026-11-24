**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# The collections desk can ask a household that has left to take a prepayment meter (23 Nov 2026)

Filed by the delivery seat under `verify-gas-only-win-landing-from-the-6c-resume-chain`, from the probe
that named the live Consent red
(`SEAT_FINDING_ORIGIN_IS_RED_ON_THE_LIVE_CONSENT_OFFER_SINCE_7527A2E36_..._2026-11-23.md`).

## What happened

On origin with 7527a2e36's `closing` forced off (the world before 7527), the answered 2016 run's only
live Consent offer went to **ACC-SYN-2016-005**, which closed in June 2016 (on
`churned_billing_accounts`). Its journey opened 2016-07-29, after it left. The desk offered an
arrangement on 2016-08-25, and on 2016-10-26 `_offer_prepayment` (`company/billing/collections_journey.py`)
asked the world to fit a prepayment meter by Consent (SLC 28.22). The company no longer supplied
that premise.

7527 removed this instance by collecting the level debit on the final bill. It did not remove the class:
any leaver whose final bill fails still has a journey, and nothing on the Consent path asks whether
the account is still supplied.

## Why it is an absurdity a real supplier would not commit

A supplier knows its account closed. It issued the final bill, and the loss of registration is its own
observable (the desk already reads `dunning_at_leaving`). A prepayment meter is fitted at a supplied
premise. A closed account's debt goes to final-account recovery: the write-off a year after the final
bill, then agency placement (`debt_and_collections.md` s.7.3). It does not go to the 90-day rung.

## Done means

1. The Consent gate (`_gate.may_take(CONSENT_PPM_OFFER, ...)`) refuses for an account the company knows
   has closed, with a named reason, and the journey records `prepayment_withheld` with that reason. Fixed
   as a class in `company/compliance/domain_invariants.py` if a recovery step on a closed account
   generalises.
2. A test names the defect (a leaver with an unpaid final bill reaches the 90-day rung) and is
   mutation-proven (removing the closed-account column reds it).
3. The epistemic question is answered in the commit: the closure the gate reads is the company's own
   record, not world truth.

## Resolution (23 Nov 2026, claim `a-closed-account-is-never-offered-a-prepayment-meter`)

- **The gate.** `winter_moratorium` has a new column, `account_still_supplied`
  (`EnforcementCase.supply_ended_on`, refusal `SUPPLY_ENDED`). It covers every action taken AT THE
  PREMISE: disconnection, warrant, remote switch, Consent offer. Agency hand-off is n/a, because it
  is the final-account route. The commons s.5 table carries the column, and the table control
  engages it.
- **The desk.** `CollectionsJourneyDesk.note_supply_ended(account, last_supplied)` holds the
  company's own closure date. `_offer_prepayment` passes it to the gate, so a refused offer records
  `prepayment_withheld` with the reason. The debt stays on the journey until `_write_off_if_closed`
  takes it a year after the final bill.
- **The class.** `domain_invariants.NO_PREMISE_STEP_AFTER_SUPPLY_ENDED` is in `ALL_INVARIANTS`. The
  desk raises it in `_refuse_issued` over every stage it issues, so a later premise route that
  skips the gate is caught by a read it does not share.
- **The epistemic answer.** The closure the gate reads is the company's own record. The run tells
  the desk the last day supplied at the two moments it closes an account: a registration loss is
  filed, or a move does not follow (`LivePaymentTriad.close_account(..., last_supplied=)`). The
  company issues that account's final bill and loses its registration on those same facts. The
  world's `churned_billing_accounts` is never read.
- **Tests.** `tests/company/billing/test_a_closed_account_is_never_offered_a_prepayment_meter.py`
  rebuilds the ACC-SYN-2016-005 shape (left 30 Jun, opened 29 Jul, declined 25 Aug, Consent
  26 Oct). The permit leg is that a supplied account in the same state is offered and fitted. A
  closure dated on the step day does not reach back. Mutation: removing `supply_ended_on=` from the
  desk's gate call reds only the refusal test.
- **On the live run.** `test_every_live_consent_offer_goes_to_an_account_still_supplied`, held
  open by a strict xfail, XPASSed. Its xfail is dropped, and it now also asserts that a leaver
  reached the rung, so the check is not vacuous. The answered window to 2017-12-31 held three
  offers, all to leavers, and all are now withheld. So the window holds NO Consent offer. The two
  answered controls, `test_an_answered_live_run_decides_the_consent_offer_both_ways` (split from
  the 90-day-rung test, whose shipped leg stays live) and
  `test_the_world_counts_every_consent_offer_the_company_made`, are vacuous there. They are held
  open by a strict xfail that names the re-key.
- **Not done here, handed on.** The measurement that finds a window with an offer to a SUPPLIED
  account (`docs/staging/records/SEAT_PREREG_THE_ANSWERED_WINDOW_AFTER_CLOSED_ACCOUNTS_ARE_REFUSED_2026-11-23.md`)
  could not be admitted in this turn: the box queue held both in-process probes asleep for 30 min.
  It runs as a long job, and the re-key waits on its result file.
