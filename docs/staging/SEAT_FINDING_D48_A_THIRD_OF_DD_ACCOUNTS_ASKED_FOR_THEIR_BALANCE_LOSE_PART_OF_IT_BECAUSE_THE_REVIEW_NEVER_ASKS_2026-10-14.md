**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** back-billing-and-liability

# A third of direct-debit accounts asked for their balance lose part of it to the 12-month limit, because only the final bill ever asks (2026-10-14)

**Fate (2026-10-14):** ATOM -- company, next week, with the DD engine: the review never asks for the balance (seek_balance_at_review false).

*From D48 Expert Hour, 2026-10-14. Adjudication: `SEAT_FINDING_D48_THE_EXPERT_HOUR_FAILS_ON_THE_CLAIM_NOT_THE_MEASURE_2026-10-14.md`. Not fixed in the turn that found it.*

**The figures:** 153 of 422 DD accounts (36.3%, 95% CI 31.8-40.9%) that met a charge recovery action had money barred, £33,770 gross of VAT in all. `seek_balance_at_review: false`.

**What the reviewer said:** its prior was a few percent, and it held that 21BA does not reach a DD shortfall. The rule half is refuted by the sourced position, "a direct debit statement is not a charge" (`back_billing_and_liability.md` §44). The magnitude half stands.

`back_billing_and_liability.md` already records that `dd_review` "does not seek the balance", and that the shortfall therefore ages out. So the 36% is an artefact of the review never asking. A real supplier's annual DD review normally sets the new amount to clear the shortfall.

**Question for the knowledge layer first (K4):** does published practice (Ofgem's DD guidance, Energy UK, Ombudsman decisions) say the review recovers the balance? If it does, `seek_balance_at_review` defaults to the wrong setting, and the 36% describes a supplier that does not exist.
