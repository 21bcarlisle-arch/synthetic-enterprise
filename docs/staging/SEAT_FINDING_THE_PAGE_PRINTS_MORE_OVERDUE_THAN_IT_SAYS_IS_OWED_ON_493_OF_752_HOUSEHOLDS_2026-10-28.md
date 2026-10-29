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

**Re-graded on the fresh 1a02c46116 run (2026-10-28): 12,730 steps on 495 households.** The +2,550 is
the gas-leg settlement fix f805a94834. The desk's 40,005 step amounts are identical between the books,
and only the page's owed bound fell, because a gas page no longer carries an unsettled credit. So the
fix exposed more of this finding's cause rather than adding a new one. The exception's ceiling is
re-based to 12,730. Attribution beside
`records/SEAT_PREREGISTRATION_THE_EBSS_SHARE_FIX_READ_ON_A_FRESH_RUN_AT_1A02C46116_2026-10-28.md`.

## Built (2026-10-28, item `the-desk-is-posted-the-issued-bill-not-true-kwh-revenue`)

The desk is posted the issued bill. `_post_month_bill` asks `StopNoticeBoard.issued_bill_for` for
the month's bill, which runs the assembly door over the leg's rows through that month. It posts
`arrears_engine.payer_ask_gbp` of that bill. That is the engine's own ask, factored out of
`_resolve_bills`: the payer's share of the window, net of EBSS. A held bill posts nothing. The
board's memo serves its own stop-notice ask and the desk's from one rebuild. Knowledge:
`debt_and_collections.md` §7.2.

- On a 2016 run, 4,769 of 4,769 posted leg-months equal the ask over the whole-book published bill.
- On the 1a02c46116 book, 1,331 of 1,331 leg-months on 40 sampled legs agree.
- The extra cost is at most about 13.5 min a run, not the 90 estimated above.

The exception's ceiling is unchanged until the fresh run is graded:
`records/SEAT_PREREGISTRATION_THE_DESK_POSTED_THE_ISSUED_BILL_READ_ON_A_FRESH_RUN_2026-10-28.md`.

## The second cause traced: three write-off dates for one leaver's debt (2026-10-28, item `the-desk-fix-is-graded-on-a-fresh-run`)

**How much.** On the 1a02c46116 ledger, 720 of the 12,730 breaches, on 112 households, fall on or
after the page's first write-off on that household. `/var/tmp/desk-wo-probe/probe.py` rebuilds the
row and reproduces the 12,730 to the step. The other 12,010 come before any write-off, which is
the price cause the desk fix addresses.

**Where.** C6 is an SME leaver. Its final bill was issued on 5 Apr 2017 and fell due on 19 Apr 2017.
- **The page** writes the unpaid July 2016 bill off on 19 Apr 2017, the final bill's due date. That
  is the world's `simulation/arrears_engine.balance_settlement_from_outcomes` under the labelled C4
  convention (`WRITE_OFF_DATE_CONVENTION = "final_bill_due_date"`). From that day the page owes
  nothing.
- **The company's sweep** (`company/billing/arrears_engine.closed_balance_write_offs`) writes a
  closed account off a year after its final bill (`CLOSED_ACCOUNT_WRITE_OFF_AFTER_FINAL_BILL_DAYS`).
  `LivePaymentTriad.write_off_closed_balances` runs it only after the loop. Its docstring gives the
  reason: bills post in term order, not date order. By then every in-loop journey has already been
  walked, so no journey sees a write-off at close.
- **The desk's journey** therefore chases on: a statement on 26 Apr, an interest notice on 19 May,
  a final demand on 3 Jun and debt recovery on 18 Jun 2017. It writes the debt off at the six-year
  bar, on 19 Apr 2023, by `limitation_act_1980_s5`.

That is three dates for one write-off.

**Why it is not fixed this turn.** The run-side cause is plain, but the remedy is not.
`debt_and_collections.md` lists the close-to-write-off clock as a supplier policy Ofgem says
differs (GAP, l. 287). It also records Centrica's "enforcement continues after the accounting
write-off". Chasing a closed balance for a while is therefore real practice. The defect is that the
page and the desk take their write-off from different engines on different clocks. What it needs:
- one write-off home: the company's own decision, which the page prints;
- the sweep run where the journey can see it.

The second is the run's ordering problem the docstring names. Both are a design change to which
engine the page's arrears history reads, so this cause stays recorded and open. It is P7 of
`records/SEAT_PREREGISTRATION_THE_DESK_POSTED_THE_ISSUED_BILL_READ_ON_A_FRESH_RUN_2026-10-28.md`.

**Also seen, not traced.** C6's desk journeys close "cured" (overdue nothing) and reopen the next
day on the same GBP 130.50 overdue: on 15 Oct and 16 Oct 2016, and on 19 Apr and 20 Apr 2017. A
journey that cures without a payment covering the overdue item is a separate question for
`company/billing/collections_journey`.

## Graded on a fresh run (2026-10-28): 12,730 -> 9,455, with what is left named

The fresh run at b2fc50facf carries the desk fix. It grades **9,455 of 32,726** steps (P1 held at
≤ 10,230). The four classes left are below; the probe is `/var/tmp/desk-wo-probe/lag.py`.

- **723, after the page's write-off.** The three write-off dates above. Open.
- **2,985, at most 2p.** The desk's ask and the printed bill round apart. Explained, not traced to
  the line.
- **466, a payment the page shows that the desk has not yet seen.** The page posts a direct debit on
  its due date, and the desk gets it when it crosses: 1 day on 315 steps, 7 days on 144. Explained.
- **5,280, not attributed.** The lead is OCC-198d2b2c01a7, April 2025. Every bill is paid on the
  page, while the desk prints GBP 102.17 and then GBP 225.97 overdue. The page's payments come from
  the world engine's resolved outcomes (`arrears_engine.resolved_settlement`). The desk's come from
  what the triad delivered. Trace whether those two payment records agree on a bill, starting from
  that case. That is the next step on this finding.

The exception is re-based to 9,455 with these classes in its reason. This finding stays open on the write-off
dates and the 5,280.

## 2026-10-28, evening: the 5,280 traced (the-page-and-the-desk-read-one-payment-record)

The two records disagree on every occupier's bill. `per_customer_behavioral` was built for the
roster's customers only, so none of the 253 `OCC-` legs carried `world_payment_truth`. For those
legs, `_resolve_bills` drew each bill's outcome a second time. OCC-198d2b2c01a7g's gas bill 808 is
paid on its due date on the page and unpaid on the desk.

- **Fixed in the run.** Every leg the triad posted now gets the truth. The test is
  `tests/simulation/test_an_occupiers_bills_read_the_triads_payment_truth.py`, red on origin.
- **No run carries the fix yet.**
- **What it covers.** 2,005 of the 5,280. It also covers 448 of the 466 that the class above
  explained as a direct debit in flight, so that explanation is refuted for those 448.

What remains on non-`OCC-` accounts is 3,275:
- **Up to 2,067 come after a credit bill the desk is never posted.** The run posts `max(0, ask)`.
- **487 are the row netting one fuel's credit against the other fuel's debt.**
- **The rest are pennies that add up across open bills.**

The split and the predictions are in
`docs/staging/records/SEAT_PREREGISTRATION_AN_OCCUPIERS_BILLS_READ_THE_TRIADS_PAYMENT_TRUTH_2026-10-28.md`.
That record also covers the write-off dates. The close-to-write-off clock is a GAP in
`debt_and_collections.md` §2.7, so giving the book one date is a design choice across three records.

Still open on this finding:
- the credit-bill posting;
- the write-off date;
- the grade on a fresh run.

## 2026-10-29: the write-off date is one (item `the-write-off-date-is-one-for-the-page-the-sweep-and-the-desk`)

Class (a) is built, not yet graded. The company's write-off of a closed account, a year after its
final bill, is the one date. The desk writes the balance off on that day inside its walk, and the
journey ends. The world's close write-off, which the page and the P&L read, is dated by it through
`collections_communication.closed_account_write_off_date`. Knowledge: `debt_and_collections.md`
s.7.3. Control: `tests/company/billing/test_a_leavers_debt_has_one_write_off_date.py`. Predictions:
`records/SEAT_PREREGISTRATION_ONE_WRITE_OFF_DATE_FOR_A_LEAVERS_DEBT_ON_A_FRESH_RUN_2026-10-29.md`.
The known residue was a dual-fuel account where one fuel leaves and the other stays.

**Graded 2026-10-29 on `fresh-run-209c3350ab`: class (a) is 0 steps (723).** The residue did not
appear. Desk statute-bar write-offs on leavers went from 106 to 0, and the post-loop sweep posted 0
(106). The row as a whole breaches 2,500 of 19,491 steps on that book, and none of them is class (a).
Results, and an unattributed −3.7% in close write-offs that the 0b28 run will split:
`records/SEAT_PREREGISTRATION_ONE_WRITE_OFF_DATE_FOR_A_LEAVERS_DEBT_ON_A_FRESH_RUN_2026-10-29.md`.

Still open on this finding: the rest of the row (the "other" class), graded by the 0b28 run.

## 2026-10-29: the 209c3350ab book's 2,500, every step by cause (item `the-overdue-rows-820-unexplained-steps-on-the-209c-book`)

Counted by the row's own evaluator, so 2,500 exactly. (A) 2,328 steps are 1p to 7p: the desk asked
the biller's unrounded total, but the page prints the total its rounded lines foot to. Fixed: one
`saas.money.printed_bill_money` for both. (B) 140 are a mover's part-paid final bill whose part never
crossed to the desk. Fixed: it crosses as a card payment. (C) 32 on 4 households: the desk took
some cash on a part-paid final bill, and its source is not traced. The "675 up to £1" did not
survive the row's own count: nothing breaches by between 10p and £1. Causes, the refuted
hypothesis for C, and the prediction for the next fresh run:
`docs/staging/records/SEAT_PREREGISTRATION_THE_OVERDUE_ROWS_2500_STEPS_BY_CAUSE_ON_THE_209C_BOOK_2026-10-29.md`.

## 2026-10-29: the desk's untraced cash on four part-paid final bills (item `the-desks-untraced-cash-on-four-part-paid-final-bills`)

**The class.** On 209c3350ab, 32 steps on OCC-6e59dd8b63e8, OCC-b3b4e19ff255, SYN-2016-016 and
SYN-2016-083 look as though the desk took some cash on a part-paid bill, but less than the part. For
083, the bill is 118.33, the page's part payment 71.28 and the desk's overdue 89.80, so the desk
looks to have taken 28.53. The method: `/var/tmp/deskcash/replay.py` replays the live triad's
`record_period` over the household's own book invoices and reads the desk ledger.

**What it is, on three of the four: a credit bill, not cash.** The replay posts the page's own
118.33 and reproduces 89.80, so the in-loop bill is not the cause. The ledger shows a -28.53 credit
bill (Jul 2017) posted as `ADJUSTMENT_CREDIT` on 14 Aug 2017. The page nets that credit off the
leg's next bill: the household pays 37.41 of 65.94 on 14 Sep 2017. In the triad the household paid
the whole 65.94, so the 28.53 sat unused on the desk for 18 months and then came off the Jan 2019
failed bill. The desk's "cash" equals the page's `credit_applied_gbp` on each household:
- 083: 28.53;
- b3b4: 83.74;
- 016: 4.33 + 3.40 against 7.75, within 2p.

**The fourth, OCC-6e59dd8b63e8, took no cash.** The desk holds both bills whole (22.81 + 29.01, as
51.81). The excess is the gas leg's part payment, 11.03 against 11.02. That is the plain part-paid
class, which the classifier's 1p tolerance missed by a penny of rounding.

**Fixed: the household is asked the net bill.** `record_period` holds a credit bill per leg. It
asks the leg's next bill net of the credit for the collection, the DD request and the budget. The
bill debit stays whole. A credit that meets an open unpaid bill on the leg is not held, because the
page nets it there and the desk's oldest-first allocation already does. The draws are keyed by
period, so no outcome moves. After the fix the replay of 083 pays 37.41 on 14 Sep 2017. The account
is at zero until Jan 2019, and the desk then holds the whole 118.33.
- Control: `tests/background/test_a_credit_bill_comes_off_the_legs_next_collection.py`. Both legs
  red under each of the two mutations: no netting, and no open-bill guard.
- Knowledge: `debt_and_collections.md` §7.3.

**With 714b0ce3c's part-payment fix, all four households meet the page.** The replay on the trunk
carries both fixes:
- 083 prints 47.05 against 47.05;
- b3b4 prints 260.36 against 260.36;
- 6e59 prints 40.78 against 40.79;
- 016 prints 79.01 against 79.02 on 18 Mar 2018. From April it is 3.41 below: the electricity leg's
  closing credit, which the desk nets across fuels on one account.

Prediction for the next fresh run: class C is 0 steps.

**Exposed, not fixed here: the triad draws a non-final bill as a mover's exit.** It passes
`due_date` where `mover_final_bill_outcome` takes the bill's `period_end`, and the other three
callers pass `period_end`. The test is "period month ≥ last supplied month", so the
month-before-the-move bill, which falls due in the move month, is drawn as an exit as well.
- Three of these four part-paid bills are not final bills: 083's Jan 2019, 016g's Feb 2018 and
  b3b4's Dec 2024.
- The seed string also differs from the DD book's draw of the same bill.
- This is the next increment on this item.
