**Severity:** LATENT · **Lane:** D_billing_metering · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# Pre-registration: the K1 billed-on-estimate grade dates a closing-run interim at the final bill (2026-10-21)

*Worker tick. Written before any before/after figure was computed. The open item is the second
"Left open, named" bullet of the closed-account follow-on in
`docs/staging/SEAT_FINDING_D48_THE_UNBILLED_ACCRUAL_IS_THE_ENERGY_THE_PRE_BILL_GATE_HELD_2026-10-20.md`.*

**Definition.** A bill is billed on estimate at a month end only once it has been ISSUED by that
month end. A held interim released at the closing read goes out with the final bill
(`pre_bill_validation.issued_with_final_bill`). Before the final bill's month it is unbilled, which
is the accrual's half. So the K1 grade must not count it as billed on estimate. Today it does, so
for those month ends the two halves of unread revenue count the same bill twice.

**Fix.** `estimated_billing_outstanding_grade` dates each bill by its issue month: the final bill's
month for a bill in `issued_with_final_bill`, else its own period end. The summary computes the
late-issue map once and passes it to both the grade and the accrual.

**Instrument.** The 44a21e3e8 run's 38,005 bills (`docs/reports/run_output_44a21e3e8_20261020T085542Z.json`).
`final_bill` is stamped on the last bill of each account in its `churned_billing_accounts`, as the
changed assembly would. The held set is `bill_assembly.held_bills`. The grade is read through
`billing_accuracy_summary`. This is not a re-run.

**Predictions.**
1. Electricity K1 year-end grades: only 2017-12 moves. Its `open_bills` falls by 1 and its
   `open_kwh` and `never_read_kwh` by the same amount, about 3,120 kWh (PROS-2017-0117's 2017-12
   interim). Its `outstanding_gbp` falls by that bill's total. Every other year end is identical.
2. No `graded_*` figure moves at any year end. A closing run ends on an estimated final bill, so
   no later read grades it.
3. Gas is identical at every year end. No gas bill is released at closure on this run.
4. K1_unbilled_accrual is identical, because the accrual already used the late-issue map.

**Refuted if** any year end other than 2017-12 moves, or a graded figure moves.
