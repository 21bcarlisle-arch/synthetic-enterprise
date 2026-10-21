**Severity:** LATENT · **Lane:** D_billing_metering · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# Pre-registration: a held estimate on a closed account goes out on the final bill (2026-10-21)

*Worker, claim `d48-a-held-estimate-on-a-closed-account-is-never-worked`. Written before any
before/after figure was computed. Design: `docs/market_research/unbilled_energy_and_revenue_assurance.md`,
K6, "A held bill on an account that closes".*

Instrument: the 44a21e3e8 run's bills, with `final_bill` stamped the way the changed assembly
stamps it (last bill of each account in the run's churned set), through `bill_assembly.held_bills` /
`billing_accuracy`. Not a re-run.

1. Held bills fall by exactly 5, all PROS-2017-0117's (2017-12 .. 2018-04-11), and no other bill
   changes state. Gas is unchanged at zero.
2. K1_unbilled_accrual, electricity: unchanged at 2016-12 and 2017-12 (the interims are not
   billed until the final bill's month). From 2018-12 to the run end, kWh falls by 12,825 and
   GBP net by about 1,635 at every year end, and `closed_account_kwh` reads 0 at every month end.
3. No interim is barred: the closing run spans under 5 months, so 21BA bars nothing on it.
