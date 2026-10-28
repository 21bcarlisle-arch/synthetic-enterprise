**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The second cold read's rows find a late direct debit, an unshown price guarantee and estimates too close to the month (2026-10-28)

**Source.** The six rows for the second cold read's classes (N2, N3, N5, N6, N7, and estimate
against the meter) were written blind into `docs/design/DOMAIN_INVARIANTS.yaml` and graded on the
1a02c46116 book. The predictions came first, in
`docs/staging/records/SEAT_PREREGISTRATION_THE_SECOND_COLD_READS_CLASSES_GRADED_ON_THE_1A02C46116_BOOK_2026-10-28.md`.

BLOCKING because the correctness stretch's exit test needs zero unexplained breaches. Each residual
below is excepted at its measured count in `DOMAIN_INVARIANT_EXCEPTIONS.yaml`, and each exception
names how much of the count it explains. Only R1 and R2 are fully explained.

## Fixed in the same commit

| row | before | after | the fix |
|---|---|---|---|
| `INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE` (N3) | 631 of 1,125 | 181 (R1 below) | `tools/generate_explore_cast.payment_record` counts bills, not ledger rows and arrears cases. The page bill now carries its due date, number and document type. Test: `tests/tools/test_the_payment_record_counts_bills_not_ledger_rows.py` |
| `INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER` | 11 of 4,311 | run-side: 10 of the 11 are this cause, and only a run can show them go | `estimate_unread_kwh` treats a zero-kWh window as no measurement, and the bill falls back to the registry figure. Test: `tests/company/billing/test_a_zero_advance_establishes_no_estimate.py` |
| N6 copy | "read frequency is the customer's consent to give" | monthly reads need no consent, daily reads are taken unless the customer opts out, and half-hourly reads wait for an opt-in | `tools/generate_explore_hh_day._coverage_statement` and the Explore panel. Test: `tests/tools/test_the_smart_meter_copy_says_what_the_licence_lets_a_supplier_read.py` |

## The residuals, worst first

**R1. A direct debit succeeds weeks late with no return (181 accounts, world side).** On
PROS-2016-0020, 12 bills were collected by DD 31 to 45 days after their due date with no returned
attempt (for example, invoice 9291 was due 2016-03-20 and collected 2016-04-28). A DD is collected
on its date or returned through Bacs, so this cannot happen. The run's payment timing gives a DD
payer a pay-on-receipt payer's delay. Every collections figure that reads DD timing inherits it.
Next step: read `simulation/world_payment_truth.py`'s timing for the DD channel, and write a test
that a DD succeeds on its date or fails.

*World fix landed 2026-10-28; the grade is owed on the next fresh run.* The delay was not in
`world_payment_truth`, which copies the triad's `days_late`. It was in `arrears_engine.payment_outcome`,
whose late leg (3 to 90 days by stress tier) every domestic credit method took, DD included. At real
inputs (400 bills a tier) a DD was late on 25 bills at LOW, 190 at MODERATE (14 to 45 days) and 337
at HIGH. Now a DD that is not returned is collected on its due date. The late draw is still made,
so no stream moves, and it is kept for pay-on-receipt. `generate_payment_event` now sends a non-DD
method as pay-on-receipt, not as "direct_debit". Whether a bill is paid does not change on either
channel. Test: `tests/simulation/test_a_direct_debit_is_collected_on_its_date_or_returned.py`.
Knowledge: `payments_and_direct_debit_2026-10-25.md`, "A DD is never late".
**Prediction, written before any run carries it:** on the first fresh run launched after this commit,
the row reads at most 10 breached, from 181. Anything left is a mover's final bill paid late on a DD
leg (`final_bill_outcome.PAID_LATE`, deliberately unchanged). Collections journeys and dunning opened
on DD accounts fall. Bad debt moves little, because a late DD was paid anyway. Not run here:
fresh-run-129e7de698 was already waiting, and it predates this fix.

**R2. The Energy Price Guarantee is in revenue and on no page (266 of 316 accounts outside the N2
band).** "Revenue, before VAT" values Oct 2022 to Jun 2023 at the supplier's tariff. The customer
was billed at the guarantee's rate, and the government paid the difference. Taking each account's
EPG-window revenue less its EPG-window bills off R puts all 266 inside the band. That is a
supplier-side page fix: print the EPG support as its own line, then give the row an EPG term.
50 residuals are open: 34 accounts never supplied in the EPG window (short occupier accounts 1% to
5% apart, possibly part-month standing charges against the row's 1% belief) and 16 supplied in it.
The cold reader's 2016-to-2019 example (OCC-423594fbfa6b, on the 1691ec0ecd book) is among the
pre-EPG kind and is not explained yet.

**R3. Estimates that track the month too closely (N7, 292 bills on 50 accounts).** The estimator's
reference windows (three actual reads, or an advance of 182 to 731 days) differ from the row's,
which explains part of the count. On OCC-01e79fcf2d4fg, the estimates after a read sit within
1% to 6% of the month's settlement kWh (Dec 2021: 2,138.6 billed against 2,151.1 settled).

*Traced 2026-10-28. The example is refuted as a crossing; the cause is the printed read.* The Dec
2021 estimate is `annualised_advance_kwh` exactly (2,138.62). The register advanced 6,514.85 kWh from
the 20 Mar opening read to the 30 Nov actual read, and that advance is annualised at the 182-day
floor. That is what the meter told the supplier, and the household's use was steady, so the estimate
was simply good. The breach comes from the ledger. `tools/generate_billing_ledger.py` prints an
actual bill's closing read as the previous printed register (seven 0 kWh estimates) plus the month's
own kWh: 1,618.9 where the meter read 6,514.85. The row's references are printed actual reads, so it
graded the estimate against a quarter of the real advance. **A bill prints an "actual" read the meter
never showed** wherever an estimated run before it billed a different kWh from the meter's. That
is a customer-facing defect on its own.

Measured on a scratch copy of the ledger with each actual bill given the meter's register
(`docs/staging/records/SEAT_PREREGISTRATION_R3_THE_PRINTED_ACTUAL_REGISTER_AND_THE_ESTIMATE_WINDOW_2026-10-28.md`):
292 falls to **151 on 30 accounts**, so 141 are the printed register. On the same register,
`INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER` rises from 11 to 20 runs: the printed register was hiding
runs billed 3 to 5.5 times what the meter advanced.

*The crossing the item suspected is real, and it lives elsewhere.* After an estimated run,
`trailing_actual_periods` took the month's settlement kWh over the month alone, which no read gives a
supplier. It set the estimate wherever no actual read lay 182 or more days back: **2,754 of 31,588
estimated bills (8.7%) on 493 accounts**, with 55 of the 292 among them and 38 of the 151. **Fixed**:
the entry now spans the last actual read to this one and holds the register's advance
(`company/billing/monthly_bill_assembly.py`). Test, red on origin:
`tests/company/billing/test_the_estimate_window_holds_only_what_the_meter_told_the_supplier.py`. The
prepayment branch's window append is never read, because a prepayment account is never estimated
and its channel is fixed for the account's run. The epistemic verifier passed the diff.

Two follow-ups from that review, both open:
- The prepayment branch's `read_advance_kwh` is the month's kWh alone, even after unread months. So
  its register runs low, and the theft screen's `registered_kwh` reads it on every prepayment actual
  read.
- `_resolve_catchup` prices the run's correction from each unread month's own true charge. No read
  gives how an advance splits across months. A supplier shares it out by the profile.

Open, and handed on: the ledger prints the meter's register on an actual bill. That needs a K8
reading of how a bill after an estimated run shows its reads, because the printed usage then includes
the run's correction. Then re-grade on a fresh book carrying both fixes. The prediction for that
grade is filed in the pre-registration above.

**R4. A held bill counts on the usage panel (N5, 10 account-years).** These are the same four
accounts and nine held months as `INV_OVERDUE_WITHIN_BALANCE`'s exception, with the same cause and
the same retirement.

**R5. One Smart household is billed on estimates (N6, 4 fuel-years).** C2 and C2g, 21 and 13 of 24
bills estimated. Nothing yet says why its meter in smart mode delivers no reads. The book has only
nine Smart accounts, so the share bound is mostly this one household.

## N4 (world, no build)

Measured and recorded in the second cold read's finding, which is now done: no price-level demand
response (electricity −0.3%, gas −2.2%, 2021 to 2022, same accounts, against a published −10.3%
and −19.2% unadjusted). That is a world item for the seat to sequence. The ruling holds feature
work, and it is a fidelity fix, not a feature.

## Not done here

- R1, R2's page line, R3's printed actual read and R5. Each is named in its exception's `retired_by`.
- The commons still lacks the licence text for smart data access (SLC 47 and its gas counterpart).
  That GAP is on `INV_SMART_METER_BILLED_ON_ITS_OWN_READS`.
- No fresh run was launched for the zero-advance fix. Item 1's run (`the-desk-fix-is-graded-on-a-fresh-run`)
  will carry it if it launches after this lands, and its grade should read the run row at 1 or less.
