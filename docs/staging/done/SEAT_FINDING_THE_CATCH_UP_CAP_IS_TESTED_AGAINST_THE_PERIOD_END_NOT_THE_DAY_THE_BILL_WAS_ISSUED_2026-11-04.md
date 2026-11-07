**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The back-billing cap on a catch-up is tested against the bill's period end, not the day it is issued, so 5 pay-on-receipt catch-ups on b3ce2a4e73 reach back more than 12 months uncapped (2026-11-04)

**Source.** N14's prediction (c6e1a29e1: "no domestic catch-up from May 2018 on a bill the ledger records as paid on
receipt has cap_applied false with a window over 12 months") graded on the b3ce2a4e73 book:
`docs/staging/records/SEAT_RECORD_THE_B3CE2A4E73_BOOK_GRADED_AGAINST_ITS_FIXES_PREDICTIONS_2026-11-04.md`, row (a).
Predicted 0, measured 5. The 11 of 0a6391d186 are gone from the DD basis: the N14 fix works.

**What the book holds** (bills in the run JSON joined to the ledger's invoice and its successful payment method):

| Account | Bill period | Issued | Window starts | Days, issue to window | Days, period end to window |
|---|---|---|---|---:|---:|
| SYN-2016-048 | Jan 2025 | 2025-02-07 | 2024-02-01 | 372 | 365 |
| SYN-2016-207 | Apr 2018 | 2018-05-07 | 2016-10-01 | 583 | 576 (rule starts 2018-05-01; period end is 2018-04-30) |
| SYN-2016-240 | Aug 2020 | 2020-09-14 | 2019-09-01 | 379 | 365 |
| SYN-2016-334 | Jan 2021 | 2021-02-05 | 2020-02-01 | 370 | 365 |
| PROS-2020-0016 | Jun 2024 | 2024-07-01 | 2023-07-01 | 366 | 365 |

All five are paid by standard credit, basis `pay_on_bill_true_vs_billed`, `catchup_back_billing_cap_applied` false,
nothing written off (£27.17, £287.15, £38.86, £10.77, £3.55). The reach is 1 to 14 days over the line from the issue date.

**Why.** `company/billing/monthly_bill_assembly.py` (~L947) passes `bill["period_end"]` to `_resolve_catchup` as
`billing_date_iso`, and `BackBillingAssessment.cap_applies` tests `consumption_period_start < billing_date - 365d`
against it. A bill is a demand when it is issued, and the ledger issues it `generation_delay_days` after the period
end. For SYN-2016-207 the period-end date is also before the domestic rule's 1 May 2018 start, so the rule is skipped
entirely on a bill that was issued after it. **I cannot yet say** whether the world's issue delay is known to the
assembly at that point (the ledger computes `issue_date` later, in `tools/generate_billing_ledger.py`); if it is not,
the fix is to hand the assembly the issue date it will print, and if the delay is drawn after, the cap needs the same
draw. Two more rows (SYN-2016-307g, SYN-2016-406g, gas, DD basis, 2019-03) have no successful payment joined to their
own invoice, so they are not in the five; they sit on the DD-deferred basis and are not graded here.

**Size.** £367.50 over five catch-ups; the unbarred share is the days beyond the line, a few pounds. Latent because the
amounts are small, but it is a rule the pages print and the Ombudsman reads at the day.

## Done (2026-11-07)

**Fix.** `build_monthly_bills` takes `bill_issue_date_feed(customer_id, period_end)`, and `_resolve_catchup` is
handed the issue date it returns, not the period end. The world wrapper answers with
`simulated_bill_issue_date`: `bill_due_date` less `PAYMENT_TERMS_DAYS`, which is the ledger's own `issue_date`
(`tools/generate_billing_ledger.py`). The open question above is answered: the delay is a deterministic draw
keyed on (customer, period end), so billing can know it before the ledger prints it. The bill carries the day as
`catchup_billing_date`, and the pre-bill gate's two comparators re-derive the write-off at it. Without this,
`test_the_desk_is_asked_the_capped_catchup_the_page_prints` went red. Its 16-month write-off differed in size
by the delay, so the gate held the bill (mutation-checked: re-dating the gate at the period end reds it). Knowledge:
`docs/market_research/back_billing_and_liability.md` section 17.

**Test.** `tests/simulation/test_a_catchup_is_capped_at_the_day_its_bill_is_issued.py` replays SYN-2016-048's
Jan 2025 bill (issued 2025-02-07, window from 2024-02-01). Both arms run on one run: dated at the period end it is
not capped, and at the issue it is capped with a write-off. With the fix reverted to `period_end` it goes red
(mutation run 2026-11-07). The issue date is also checked against the ledger's for three accounts.

**Before and after on fd91027799** (`docs/reports/run_output_fd91027799_20261105T004022Z.json`, domestic
undercharge catch-ups from May 2018, window more than 365 days before the issue date, cap not applied):
- **Before (measured on the book):** 5 on the pay-on-receipt basis, £45.26 charged. They are SYN-2016-048 (Jan 2025,
  372 days), SYN-2016-158 (Nov 2020, 369), SYN-2016-240 (Aug 2020, 379), SYN-2016-334 (Jan 2021, 370) and
  PROS-2020-0016 (Jun 2024, 366). Each is within 365 days of its period end, so this defect accounts for all 5.
  There are also 143 more on the direct-debit basis. That basis defers the bar to a charge recovery action, so this
  fix does not change them (124 of the 143 are over the line from the period end too).
- **After (the cap decision replayed on those 5 rows, not a re-run book):** `BackBillingAssessment` dated at the
  issue gives `cap_applies` True on all 5. The barred share is 0.27% to 3.84% of each window, so a few pounds in
  all. Dated at the period end it gave False on all 5. **Prediction for the next book:** 0 pay-on-receipt catch-ups
  uncapped over the line from issue. A non-zero count means another cause.

**Reverse:** revert the commit that carries this section.
