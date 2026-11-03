**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The seventh cold read finds pay-on-receipt customers back-billed beyond 12 months, because billing reads the direct debit they started on, not the method they pay by now (2026-11-03)

**Source.** Class N14, from named check (a) of the seventh cold read (the reader did not raise it: "no catch-up
exceeds 12 months"), on the 0a6391d186 book
(`docs/staging/records/SEAT_READING_THE_SEVENTH_COLD_READ_ON_THE_0A6391D186_BOOK_2026-11-03.md`).
It is BLOCKING because it is a new class, and the correctness stretch cannot exit while it stands.

**What the published pages hold** (`site/data/customers/*.json` at 1eaf19d78d, domestic bills issued from
1 May 2018):
- 169 catch-up bills recover an undercharge whose window starts more than 12 months before the bill. The
  back-billing cap is applied on 23. On the other 146 (132 accounts) `catchup_back_billing_cap_applied` is
  false and nothing is written off.
- 132 of the 146 sit on accounts paying by direct debit at the time. For those the code defers the bar to the
  recovery action (`BASIS_DD_AT_RECOVERY_ACTION`, `company/billing/monthly_bill_assembly.py:507`), which the
  Ombudsman's Scenario B can make lawful. Those are not graded here.
- **8 sit on accounts paying on receipt (standard credit) at the time**, £111.11 ex-VAT in all. Every one paid it.
  Example, PROS-2018-0016, bill of 31 May 2024: 27 estimated bills from 1 Feb 2022, then an actual read;
  "catch-up" 99.4 kWh, £25.40 ex-VAT, cap not applied, £0 written off, paid 27 Jun 2024. For a customer who
  pays each bill on receipt, every estimated bill was a demand, so the energy before 31 May 2023 is barred under
  SLC 21BA. No customer fault is recorded.
- Six more catch-ups sit on accounts with no payment method stamped within 90 days. Not graded.

**Why, as far as the code shows.** 7 of the 8 accounts paid by direct debit first and moved to standard credit
later (e.g. SYN-2016-045: DD 2016-03 to 2021-06, standard credit from 2021-10). The billing organ learns how an
account pays from `payment_channel_feed`, which `simulation/run_phase4c_on_phase2b.py:224`
(`simulated_payment_channel`) answers once per account and fuel, undated. An account whose direct debit is
cancelled mid-tenure is still billed as a DD account, so its back-billing takes the deferred DD basis and the
cap never runs. The eighth (PROS-2018-0016) has no DD payment on its record at all. **I cannot yet say** whether
its feed answer is DD or something else; that is the first measurement.

**Why no row caught it.** `INV_BACK_BILLING_12M` names back-billing but only FLAGS (144 on this book). Its
`uncheckable_part` says "a definitive breach needs the bill issue (demand) date and the link between a catch-up
charge and the consumption window it recovers; the export has neither". The published page carries both
(`date`, `catchup_period_start`, `catchup_period_end`, `catchup_back_billing_cap_applied`). The payer's method
at the bill is in the ledger (`method` on each payment), so the breach is checkable where a pay-on-receipt
payer is billed.

**What a fix needs (knowledge first, K8).** `docs/market_research/back_billing_and_liability.md` already covers
Scenario B. The open question for the page is the dated payment method: the feed should answer "how does this
account pay on this date", since the ledger shows the method changing. The row should grade a pay-on-receipt
catch-up as a breach, not a flag.

## Done (2026-11-03)

**The trace** (published 0a6391d186 bills and `per_customer_behavioral`, replayed through
`supplier_dd_spells` over the issued bills). The finding's filter gave 8. Mine, which keeps the OCC-
legs and the 2018 bills, gives 11 uncapped catch-ups on accounts paying by standard credit only, within
90 days of the bill. For every one: `payment_channel_feed` answered `direct_debit`. The basis taken was
`direct_debit_barred_at_the_charge_recovery_action`, nothing written off. The supplier's own spells had
the DD stopped, so the dated answer is `standard_credit`:

| account | catch-up bill | DD stopped after the bill of |
|---|---|---|
| PROS-2018-0016 | 2024-05-31 | 2018-02-28 |
| PROS-2018-0016g | 2021-10-31 | 2018-02-28 |
| SYN-2016-045 | 2022-12-31 | 2021-07-31 |
| SYN-2016-269 | 2024-10-31 | 2024-02-29 |
| SYN-2016-299 (gas-only) | 2018-07-08 | 2016-12-31 |
| SYN-2016-380 | 2024-10-31 | 2022-06-30 |
| SYN-2016-487 | 2018-11-30 | 2017-08-31 |
| PROS-2017-0393g | 2019-09-30 | 2018-12-31 |
| PROS-2021-0217 | 2025-06-07 | 2022-03-31 |
| OCC-33214d16f95cg | 2023-05-31 | 2021-06-30 |
| OCC-75d17c23c1dag | 2024-09-30 | 2022-01-31 |

So the side the trace names is the undated feed, not the cap. PROS-2018-0016's "no DD payment on its
record" is a stop in Feb 2018. Book-wide, 379 catch-ups on 63 accounts took a DD basis on a bill paid on
receipt.

**The fix.** Billing takes `payment_channel_at_feed(customer_data, period_end)`, and the catch-up's basis
asks it at the catch-up's own bill. The published run bills once, reads the spells over the issued bills
(the key the ledger uses), and re-bills the 63 accounts (`rebill_catchups_off_direct_debit`).
Knowledge: `back_billing_and_liability.md` section 16. Test:
`tests/simulation/test_a_catchup_on_a_cancelled_direct_debit_is_capped_at_twelve_months.py`. It reds
on today's code, and under the mutation that points the catch-up back at the undated channel.

**Not yet seen on a book.** The 11 move only on the next fresh run. Prediction, filed now: on it, no
domestic catch-up from May 2018 on a bill the ledger records as paid on receipt has
`catchup_back_billing_cap_applied` false with a window over 12 months.
**Left open:** the DD balance book's copy of the same defect,
`SEAT_FINDING_THE_DD_BALANCE_BOOK_KEEPS_A_LEVEL_DD_RUNNING_AFTER_THE_MANDATE_ENDED_2026-11-03.md`.
