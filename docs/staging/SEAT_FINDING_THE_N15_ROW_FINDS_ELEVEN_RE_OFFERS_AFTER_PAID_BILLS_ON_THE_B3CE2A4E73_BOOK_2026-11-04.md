**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The blind N15 row finds 11 "further bill missed" re-offers after paid bills on the b3ce2a4e73 book, where the fix predicted 0 (2026-11-04)

**Source.** `INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL` (`tools/domain_invariant_runner.py`, written blind from
`docs/market_research/company_debt_management.md`), run on `/var/tmp/fresh-grade-b3ce2a4e73/ledger.json`.

**What it counts.** Re-offers of the repayment plan where no bill of the billing account fell due since the journey's
previous offer, or every bill that did was paid in its window (cash issue..due inclusive on the leg, plus credit applied).

| Book | Breaches / re-offers |
|---|---:|
| 0a6391d186 (published) | 4,610 / 6,599 |
| b3ce2a4e73 (fresh, carries 6a3da3e48) | **11 / 1,241** |

The seat's own census of the same book read 0 of 2,224 (`records/SEAT_RECORD_THE_B3CE2A4E73_BOOK_GRADED_..._2026-11-04.md` (b)).
The two definitions differ in two named ways, so this is not yet a contradiction of the fix:
- **9 of the 11** are bills settled by `credit_applied_gbp` or a scheme credit. Counting cash only, the row reads 2 (both
  SYN-2016-021). The desk appears to treat a bill paid by credit as missed. The knowledge page says a bill is missed
  when it was not paid; a credit pays it. Candidate defect, not attributed.
- **The window.** The row opens at the previous offer ("further"); the census asked about bills falling due on the
  re-offer's day. SYN-2016-021 on 2023-09-18 is a re-offer with no bill due since the previous offer.

Examples: PROS-2021-0236 2024-08-22, SYN-2016-021 2023-09-18, SYN-2016-445 2023-02-19.

**Next.** Trace the 9 credit-settled cases against how the desk decides "missed"; if it reads cash only, the fix is to
count credit applied. The row's exception ceiling (4,610, N15) still holds the b3ce book inside it.

## Traced (2026-11-04, claim `trace-credit-settled-reoffers-b3ce2a4e73`)

The 11 split on whose error it is. "Credit-settled" was not one class: the row's 9 included 3 DD returns and
1 late payment.

| Re-offer | What the bill was | Whose error |
|---|---|---|
| PROS-2021-0236 2024-08-22 | gas £20.21, asked £0.00 (credit applied 20.21) | desk |
| SYN-2016-210 2024-11-15 | gas £37.09, asked £25.78, paid on its due date | desk |
| SYN-2016-445 2023-02-19, 05-18, 07-25 | asked net of a credit, paid on the due date | desk |
| SYN-2016-021 2023-09-18, 10-19 | prepayment statement, asked net of a credit, paid at the meter | desk |
| SYN-2016-066 2022-02-17, -380 2022-07-22 | DD returned; credit bills of 2022-06-30 / 10-31 settled it months later | row |
| SYN-2016-306 2017-09-16 | DD returned; £7.58 later credit + £33.89 late cash for the prior bill | row |
| PROS-2020-0016 2023-05-17 | paid 37 days late; window held the prior bill's late £19.37 + £67 EBSS | row (lenient window) |

**The desk's 7.** The household is asked the bill less the leg's credit (`live_payment_triad.record_period`,
`credit_taken`; SLC 31H.12), and pays it. The company ledger keeps the bill whole and the credit as an
unearmarked `ADJUSTMENT_CREDIT`, which oldest-first gives to the arrear an open journey always has. So
`bill_paid_in_its_window` compared the cash with the face and called the bill missed. No ledger-balance
reading can fix this, because the balance is in arrears on every re-offer day. **Fixed:** the triad tells
both desks what each netted bill asked (`CollectionsJourneyDesk.note_bill_asked`), and the window test
reads that. Control:
`tests/company/billing/test_a_reoffer_follows_a_missed_bill_not_a_standing_arrear.py::test_a_bill_a_credit_bill_paid_down_is_judged_on_what_it_asked`.
Its mutation (reading the face) goes red. The wiring leg is in
`tests/background/test_a_credit_bill_comes_off_the_legs_next_collection.py`.

**The row's 4.** `_bills_missed` adds the export's `credit_applied_gbp` whatever the payment outcome. On a
failed bill, that field is the credit netted into the arrears case later (`generate_billing_ledger`: the
case's `CREDIT_APPLIED` stages, dated months after the due date). That is not money in the window. Only on
a successful payment is it the credit netted at issue. The fourth is the window's stated lenience: cash for
an older debt counts. Filed for the row's blind writer. I did not edit the row, because it was written
blind and I have now read the code it tests.

**Prediction, written before the next fresh book is run.** Re-offers move by under 1%. The row reads
between 0 and 8 breaches per 1,241-scale book. None of them is a successful-payment bill whose cash plus
the credit netted at issue covers it. Every remaining breach is a failed or late bill (the row's class).
Journeys, cures and money figures do not change, because a re-offer moves no money.

**Reverse:** delete this file; revert the commit that adds `note_bill_asked`.

## The row's 4, amended blind (2026-11-04, claim `n15-row-credit-applied-on-a-failed-bill-is-later-credit`)

A writer with no access to company/, simulation/ or background/ (nor this file) amended `_bills_missed` from the
knowledge pages and the ledger data alone:
- **Credit.** The bill's `credit_applied_gbp` is no longer read. Credit counts only as carried on a payment record
  posted against the bill, on that record's date, when the payment went through. In the data, 67 bills whose own
  collection was returned carry `credit_applied_gbp` with nothing dated in their window; 25 successfully collected
  bills had their credit netted after the due date, so "outcome success" alone would still have been too lenient.
- **The window's lenience, decided: tightened.** Cash posted against an older invoice no longer pays this bill
  (`account_hierarchy_payment_allocation.md` s.1: the remittance names the bill; oldest-first gives it to the older
  bill too). A payment naming no bill still counts (none on this book). This overrides the debt page's lenient design
  choice, which was written for an unearmarked balance; the row's reading says so.

**Graded on `/var/tmp/fresh-grade-b3ce2a4e73/ledger.json`.** Writer's prediction, filed before running: 11 → 7, the
four named here clearing. Result: **7 of 1,241**, the same four. One rule at a time: credit only → 8 (PROS-2020-0016
stays); attribution only → 9 (SYN-066, -380 stay). The 7 left are exactly the desk's class, fixed in ba868134c, which
this ledger predates, so the next fresh book should read 0 on this row. My earlier prediction (0–8, every survivor a
failed or late bill) is wrong in its second half on this ledger: the survivors are the desk's netted-credit bills,
because this ledger predates the desk fix. It still stands for a post-ba868134c book.

One mutation does not fire: counting a failed payment's netted credit. That is an equivalence on this data: none of
the 1,896 failed payment records carries `credit_applied_gbp`.

## Pre-registered for the first post-ba868134c book (2026-11-04 12:10Z, claim `n15-grade-on-a-post-ba868134c-book`)

Filed before the run finished. The book is the `sim_runner` run that started about 11:50Z on the shared tree at
5d3d11da0c (it carries ba868134c and 5d3d11da0). Between b3ce2a4e73 and 5d3d11da0c, the only change under
`company/ saas/ simulation/ sim/` is `company/billing/collections_journey.py`, the desk fix. So the N15 row moves on
one variable.

- **The N15 row reads 0 breaches.** The 7 netted-credit re-offers on b3ce2a4e73 (PROS-2021-0236, SYN-2016-210,
  SYN-2016-445 x3, SYN-2016-021 x2) are no longer offered. If any breach survives, it is a class the trace did not
  name, and it gets traced and not explained away.
- **Re-offers fall by at least 7 from 1,241 and by under 1%** (between 1,229 and 1,234), on the row's own count.
- **Unchanged:** the account count (1,291) and the invoice count (52,715). A re-offer moves no money, so the bills do not
  change.

### Amended before the result (2026-11-04 13:55Z)

The run named above never ran. The runner restarted at 12:30Z, held, deferred four cycles, and started the first run
carrying both fixes at 13:24Z on **4669d77ddd** (`run_output_4669d77ddd_20261104T132452Z.json`). That commit also
changes `simulation/dd_balance_book.py` (a bill in a spell off DD is no longer reviewed or barred at review). That
change moves what a DD collects, so it can move failures, journeys and re-offers. **The book now moves on two
variables, not one.**
- **Stands:** the N15 row reads 0. A breach is judged one bill at a time, so attributing a survivor needs no clean
  diff: each one gets traced, and none is explained away.
- **Withdrawn, as not attributable:** the re-offer range of 1,229–1,234. The DD book can move it in either direction.
  I will report the count, and I will not read it as the desk fix's effect.
- **Stands:** accounts 1,291. Invoice count 52,715, because the DD change moves amounts, not the number of bills. Not
  carried over: re-offers move no money. On this book, money can move.
