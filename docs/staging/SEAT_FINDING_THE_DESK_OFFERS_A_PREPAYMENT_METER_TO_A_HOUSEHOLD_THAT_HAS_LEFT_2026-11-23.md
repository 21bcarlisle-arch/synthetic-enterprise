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
