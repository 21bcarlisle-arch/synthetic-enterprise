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
