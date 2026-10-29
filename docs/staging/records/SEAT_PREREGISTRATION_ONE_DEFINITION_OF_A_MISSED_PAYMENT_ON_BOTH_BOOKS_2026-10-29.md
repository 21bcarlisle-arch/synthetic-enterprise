**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# Pre-registration: one definition of a missed payment, graded on the 209c3350ab book and the published book (2026-10-29)

**Question.** The finding `SEAT_FINDING_THE_PAGE_COUNTS_A_PAYMENT_MISSED_THIRTY_DAYS_AFTER_THE_DESK_SAYS_IT_WAS_2026-10-29.md`
says the page's payment record counts a bill as missed at due date + 30 days, while the desk opens
its journey at due date + 1. The change gives one function the job:
`company.billing.collections_journey.missed_on(due)`, the day after the due date. A bill not paid by
its due date is missed from that day. The household summary's `payment_record` and the desk's
`collections_missed_payment` both read it. What happens to the debt slot on each book?

**Why the due date.** `debt_and_collections.md` §7.5 (written in the same commit) gives the
reasoning. In short, the published reading of a missed payment is a payment EVENT on the due date:
a returned DD, or a pay-on-receipt bill past its due date. The 30 days is the Bacs re-presentation
window. For standard credit it was the invariant row's own labelled belief.

**Books.**
- 209c3350ab pages: `/var/tmp/debt-slot-209c/tree/site/data/customers`, built at 8c55d9b6cb.
- The published book: `site/data/customers` at origin 714b0ce3c7.
- Probe: `/var/tmp/onemiss-scripts/debt_slot.py`. Lag table: `/var/tmp/onemiss-scripts/lag.py`.

**Measured before this was written (discovery, not a prediction).** On the 209c pages, the first
payment against non-prepayment bills lands as follows:
- DD: on or before the due date on 98.1% of bills; 1 to 30 days late on 280.
- Standard credit: 921 of 9,008 are 1 to 30 days late.

So about 1,200 bills move from paid to missed, and no DD settlement lag inflates the count.

**Predictions, written before the after-run.**

| book | quantity | before (the finding) | predicted after |
|---|---|---|---|
| 209c3350ab | debt-rule matches | 402 | 402 (the rule does not read the record) |
| 209c3350ab | refused by "nothing missed or returned" | 112 | at most 5 |
| 209c3350ab | slot | filled, PROS-2018-0222 | filled. Same household at 60% confidence |
| published | debt-rule matches | 599 | 599 |
| published | refused by "nothing missed or returned" | 599 | at most 5 |
| published | slot | empty, by this check alone | filled at 60%. If empty, by another named check, not this one |

Residual refusals by this check have one cause I can foresee: the desk (FIFO over the balance) and the
page (a payment carrying the bill's own number) read "paid" differently. That is a second
difference in definition, and it will be counted, not hidden.

## Result

Outputs are in `/var/tmp/onemiss/`: `before_*.txt`, `after_*.txt`, `final_209c.txt` and
`after_pubrebuild.txt`. The published book was measured twice:
- on its pages as published;
- on its pages rebuilt from its own run output (`run_output_latest.json.gz`, stamped 4ae8da9b0f) with
  today's code, in scratch tree `/var/tmp/onemiss/pubtree`.

| book | quantity | predicted | measured | verdict |
|---|---|---|---|---|
| 209c3350ab | matches | 402 | 402 | right |
| 209c3350ab | refused by the check | at most 5 | 3 under the definition alone, then 0 | right |
| 209c3350ab | slot | PROS-2018-0222 at 60% | filled by PROS-2016-0054 | **wrong household** |
| published, as published | refused by the check | at most 5 | 602, unchanged | **wrong** |
| published, as published | slot | filled at 60% | empty | **wrong** |
| published, rebuilt from its inputs | refused by the check | at most 5 | 45 | **wrong** |
| published, rebuilt from its inputs | slot | filled | filled by SYN-2016-592 | right |

**209c3350ab.** The slot now has 103 valid households, against 31 before.
- PROS-2016-0054 has the deepest valid journey. It was refused before by the very check this change
  answers.
- Its record reads "9 of 10 bills paid, 1 returned, 1 missed" at "Missed a payment", and its
  counters agree with every later moment.

**The 3 residuals were a second class, which I had not foreseen.** In each, a DD was returned on its
due date, and the story's moment was dated that same day. The bill was not yet missable, and the
counter counted returns only on bills past due, so the page printed "0 returned" beside "Direct
debit returned". A return is an attempt and counts when it happens. With that change, 0 remain.

**The published pages, as published: my prediction was wrong because its frame was wrong.** None of
the 52,782 bills on those pages carries a due date: they were exported before the field existed.
The record could count no miss under either definition. The check now names that cause instead of
"nothing missed": `SEAT_FINDING_THE_PUBLISHED_BOOKS_PAGES_CARRY_NO_DUE_DATE_SO_ITS_DEBT_SLOT_STAYS_EMPTY_UNTIL_THE_NEXT_PUBLISH_2026-10-29.md`.

**The published book rebuilt from its inputs: 45, not at most 5, all of one class.**
- In every one, the desk opened its journey on the 29th of a month while every bill on the page was
  paid on its due date. That run's desk dated bills differently from its billing ledger.
- 9ad5af9a75 (28 Oct, after 4ae8da9b0f) gave the desk the billing ledger's due date, and the
  209c3350ab book shows none of this class.
- This is the "paid read two ways" difference I foresaw, but from a different cause: the due date,
  not FIFO.
- Of 602 matches, 157 pass every check. The cast fills 7 of 8 slots; only `storage_heating` is empty.

## Re-read on the fresh 9553d403b7 book (2026-10-29)

Record: `SEAT_RECORD_THE_FRESH_RUN_AT_9553D403B7_GRADES_THE_OVERDUE_AND_MISSED_PAYMENT_FIXES_2026-10-29.md`.
- The definition is graded by the suite: `INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE` is 0 of 1,130 accounts, with the page's
  counter built by `missed_on` in memory (`/var/tmp/smallexc/build_book.py`).
- **The debt slot's rows (matches, refusals by this check, the household) were not re-read.** This book's
  site pages were not built: `debt_slot.py` reads a customers directory, and the 209c pages' build is not scripted
  anywhere this session could find. That is the one row of this record left open on this book.
