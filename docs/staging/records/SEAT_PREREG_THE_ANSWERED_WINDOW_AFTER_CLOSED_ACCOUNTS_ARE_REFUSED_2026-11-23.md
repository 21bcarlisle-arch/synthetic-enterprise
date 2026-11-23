# Pre-registration: where the answered run still makes a Consent offer once closed accounts are refused (23 Nov 2026)

Written before the measurement, under claim `a-closed-account-is-never-offered-a-prepayment-meter`.

**What I already know.** With the `account_still_supplied` column live, the answered run to
2017-12-31 makes no Consent offer. All three of its offers (ACC-SYN-2016-055, -099 and -390) went to
accounts that had left, and they are now withheld. The strict-xfail control
`test_every_live_consent_offer_goes_to_an_account_still_supplied` XPASSes, and two controls go red
as their own text predicted: `test_a_live_run_withholds_the_prepayment_offer_at_the_ninety_day_rung`
and `test_the_world_counts_every_consent_offer_the_company_made`.

**The question.** Does the answered run (plan answers at the register's `high` row) to 2018-12-31
make at least one Consent offer to a still-supplied account, and so give the two controls a
non-vacuous window?

**Prediction.** About 45% yes. The arrangement-first column needs an answered offer, and the S&RP
finding and the 27A watch must both be held. 2016-2017 produced only offers to leavers, which
suggests the supplied population rarely reaches day 90 with all of those met. If 2018 is empty, the
next step is the same probe at 2019-12-31. If that is still empty, the controls need a different
instrument (a seeded supplied household), not a longer window.

**Instrument.** `simulation.run_phase2b.main(report_end="2018-12-31")` with
`plan_offer_response.BASIS = basis_at("high")`, as the `answered_live_run` fixture does. It counts
`prepayment_offered` and `prepayment_withheld` stages, with their reasons, and every offer's
account against `final_month_nets`.
