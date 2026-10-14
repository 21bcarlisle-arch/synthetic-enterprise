**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** unbilled-energy-and-revenue-assurance

# D48's title ends "and the accrual", but the module says unbilled energy is not computed (2026-10-14)

**Fate (2026-10-14):** DONE -- remedy taken in this commit: the row title now says the accrual is a GAP, not yet computed.

*From D48 Expert Hour, 2026-10-14. Adjudication: `SEAT_FINDING_D48_THE_EXPERT_HOUR_FAILS_ON_THE_CLAIM_NOT_THE_MEASURE_2026-10-14.md`. Not fixed in the turn that found it.*

The row title is "...true-ups, back-billing limits, and the accrual". The brief's blind restatement repeated it, as "the energy used but not yet billed at the month's end (the accrual)". The module docstring says: "True unbilled revenue (used and not yet billed) is still not computed."

K1, on the page as "Open on estimate" (£25k-£90k at year ends), is estimated energy already **billed** and not yet trued up. That is not the accrual. The reviewer read it as the accrual's stand-in and refused it.

The row lists E3 (unbilled accrual, `saas/ledger`) as reused. Whether E3's figure could be graded the way K1 is graded has not been asked.

**Remedy:** either drop "and the accrual" from the title, or grade E3's month-end accrual against the bills that later covered the same days.
