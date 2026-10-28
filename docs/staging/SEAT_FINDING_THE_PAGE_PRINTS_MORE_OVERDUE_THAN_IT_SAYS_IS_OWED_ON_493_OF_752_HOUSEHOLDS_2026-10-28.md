**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The page prints more overdue than it says is owed, on 493 of 752 households (2026-10-28)

**Source:** the first grade of `INV_OVERDUE_WITHIN_PAGE_BALANCE`. That row is the page-graded twin
of `INV_OVERDUE_WITHIN_BALANCE`'s first leg, written for N1 of the second cold read. BLOCKING
because it is the cold read's O10/O16/O18 class ("£23.88 owed" beside "GBP71.73 overdue") at book
scale, and the correctness stretch cannot exit while a page carries it.

**What the row asks.** Every overdue figure a collections step prints ("-- GBPx overdue", the step's
`amount_gbp`) is at least nothing, and at most what the household's pages say is owed at the end of
that day. Owed is the sum over both fuel pages of the last `running_balance_gbp`, because the desk's
journey is on the billing account.

**The grade.** On the 1691ec0ecd book, with ledger and page ledger rebuilt by origin's tools and
the steps taken from the ledger's `collections_desk_journeys` (`/var/tmp/credit-probe/scripts/probe.py`):

- 10,180 of 32,741 steps breach, all above, on 493 of 752 households.
- 1,770 of them print an overdue sum on a day the pages say nothing is owed.
- By excess:

| excess over owed | steps |
|---|---|
| up to £1 | 770 |
| £1 to £10 | 2,641 |
| £10 to £50 | 3,519 |
| £50 to £200 | 2,532 |
| over £200 | 718 |

- By step: arrangement_offered 2,408, missed_payment 2,252, repayment_plan_reoffer 1,692,
  reminder 1,608. Every year from 2016 to 2025 carries breaches.

**One case.** C3, April 2017. The page bill is £28.85, raised on 5 Apr, due on 19 Apr and paid on
3 May, so the page owes £28.85. The desk's missed_payment on 21 Apr prints £30.10 overdue. The two
records of one account price the same bill differently.

**Before differencing, what each figure counts.**
- *Overdue* is the desk's `undisputed_overdue_gbp`, from the company's arrears view
  (`company/billing/arrears_engine`).
- *Owed* is the page ledger's balance, built from the billing ledger's printed bills and payments
  (`tools/generate_payment_ledger_data.build_account_ledger`).

They are different records, and the row asks that the page not print the two in contradiction. I
cannot yet say which record is wrong, or whether both are.

**Next.** Trace C3's April 2017 bill through both records and name where £30.10 and £28.85 part.
Then decide which figure the page should print, from the knowledge layer's collections pages
(`docs/market_research/debt_and_collections.md`). The exception in
`DOMAIN_INVARIANT_EXCEPTIONS.yaml` (ceiling 10,180) is retired by that fix.

**Not established.** The live publish takes its steps from the run's journeys keyed `ACC-<cid>`
(`generate_customer_reaction_chain`). This grade took them from the ledger's journeys, keyed by
billing account. For an electricity leg the two should be the same journey, but that is not
checked. The first live grade will show it.

## Traced (2026-10-28, item `the-desk-and-the-page-price-one-bill-the-same`)

**Where GBP 30.10 and 28.85 part: the desk is never told the bill.** The collections desk's ledger
gets its debits in `background/live_payment_triad.record_period`. The amount comes from
`simulation/run_phase2b._post_month_bill`, which is the month's settled rows summed: `revenue_gbp`,
less void owner charge, occupier debt and occupier scheme credit, then `owed_after_scheme_credit`.
`revenue_gbp` is the world's settlement revenue, priced at **true meter kWh and before VAT**. The
page prints the bill the supplier issued: an estimate, or an actual read with any catch-up, plus VAT
(`company/billing/monthly_bill_assembly` after the loop).
- C3, March 2017 electricity. The run's `true_total_amount_gbp` is 31.6063 including 5% VAT, so
  31.6063 / 1.05 = **30.10**, the desk's figure. The issued estimated bill is **28.85**.
- April 2017: 29.1387 / 1.05 = **27.75**, the desk's figure on 19 May. The page bill is 26.03.
- C6 (SME, July 2016) shows the catch-up face. That month's bill is an actual read carrying a
  catch-up credit, printed at GBP 33.80. The desk holds the month's settled revenue, GBP 130.50 ex
  VAT, and chases it for months.

**Which record is right: the page.** `docs/market_research/debt_and_collections.md` §1 says "A
domestic energy debt is a sum the supplier has billed". Its "Does not see" list says the company
cannot see "the true consumption behind an estimated bill". The amount owed includes VAT, which the
bill charges.

So the desk's figure is wrong twice over:
- it is an amount no bill states;
- it is a **wall breach**, because the company's ledger is posted from ground truth.

This is the same class as the in-loop DD review fixed on 13 Oct
(`a_suppliers_annual_dd_review_is_sized_from_its_own_issued_bills_not_true_consumption_2026-10-13.md`).
Its remedy is the one that applies here.

**How much of 10,180 this cause explains: at least 2,886, measured on the book with no run.**
`/var/tmp/desk-price-probe/probe2.py` and `probe3.py` rebuild the desk's overdue at the desk's own
prices.
- Unpaid at d means issued by d and not paid by d. A residential account counts its whole balance;
  a business account counts its overdue items only.
- This reproduces the printed figure to the penny on 12,637 of 32,741 steps.
- Repricing those steps' bills at the page's issued totals, graded by origin's runner, takes the row
  from **10,180 to 7,294**.
- Of those 7,294, 486 are reproduced steps that still breach after repricing. One cause is visible
  in them: a bill the page has written off (`arrears_history` WRITTEN_OFF, C6 July 2016) that the
  desk still chases.
- The other **6,808** are on steps the reconstruction does not reproduce: payment dates, part
  payments and plan instalments, which the reconstruction approximates. **I cannot yet say** what
  share of those the price cause carries. A run with the fix measures it, and it is not graded here.

**The journey key ('not established' above): the same journey on an electricity leg.**
- The ledger re-keys the run's `collections_journeys` by stripping `ACC-`
  (`tools/generate_billing_ledger.py`, `journeys_by_account`) and hands them to every leg of
  `billing_account_of(cid)`.
- The live publish asks `"ACC-" + cid` (`tools/generate_customer_reaction_chain.py`).
- For an electricity leg both name the triad's `ACC-<billing account>` (`live_payment_triad.account_of`).
  That is one row of the run, so it is one journey.
- A gas leg's file asks `ACC-<cid>g`, which the triad never writes. So the live page prints each
  step once, on the electricity page. That is what the row's "graded once" already assumes.
- That publish code's comment "one per fuel leg" is stale since B13.
- No account on this book lacks an electricity file (0 of 603 accounts with journeys), so no
  household loses its steps from the page.

**The fix (not landed this turn).** Post the issued bill to the desk in the loop. Any bill-shaped
desk input must equal the bill the page prints.
- The door is the same one the DD review and the stop-notice board already ask in the loop:
  `simulation.run_phase4c_on_phase2b.build_monthly_bills` over the leg's settled rows so far.
- Cost: a naive monthly rebuild is about 54M row-months at ~100us, roughly 90 min added to a 55 min
  run.
- `dd_collection_book.StopNoticeBoard.notice_as_of` already rebuilds every DD leg's bills monthly,
  over rows before the bill's month. The desk at month m needs rows through m, which is the stop
  board's ask at m+1. One memo keyed (leg, cutoff) serves both, so the extra cost falls on non-DD
  legs only.
- Then a fresh run, graded against a pre-registration. The exception's ceiling moves only on that
  run's measured count.
