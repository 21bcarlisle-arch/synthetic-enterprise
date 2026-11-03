**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The seventh cold read finds the collections desk reporting "a further bill missed" after a bill paid in full, on 57% of its re-offers (2026-11-03)

**Source.** Class N15 of the seventh cold read, on the 0a6391d186 book
(`docs/staging/records/SEAT_READING_THE_SEVENTH_COLD_READ_ON_THE_0A6391D186_BOOK_2026-11-03.md`, reader's O7).
It is BLOCKING because it is a new class, and the correctness stretch cannot exit while it stands.

**What the page prints.** The storage-heating slot, PROS-2017-0233, moment 3:
- "A further bill missed past the top rung: payment plan offered again -- £35.45 overdue";
- beside it, "3 of 4 bills paid, 1 returned, 1 missed".

**What the record holds** (`site/data/customers/PROS-2017-0233.json`):
- One direct debit is returned, on 16 Oct 2017, for the £35.45 September bill.
- Every later bill is collected in full on its due date: £39.31 on 14 Nov, £51.31 on 16 Dec, £53.06 on 19 Jan.
- The balance stays at £35.45 after each collection, so the arrear is never collected and never planned.
- The desk logs a re-offer on 15 Nov, 17 Dec and 20 Jan, each saying "a further bill missed". No bill was missed.

**Book-wide** (published pages at 1eaf19d78d): 6,599 `collections_repayment_plan_reoffer` events on 237 accounts.
On 3,772 of them (57%), on 222 accounts, the latest bill before the re-offer was paid in full between its issue
and the re-offer.

**Most likely cause, not yet measured.** `company/billing/collections_journey.py:484` re-offers when
`bill_missed` is true at the plan rung. `bill_missed` (line 98) asks whether "a payment landed on it on or before
its due date". If payments are allocated oldest-first, each on-time collection of exactly the new bill is
applied to the old arrear, and the new bill reads as missed. So the event is triggered by a standing arrear and
worded as a fresh miss. **I cannot yet say** whether the allocation is the cause. The first measurement: for
PROS-2017-0233's 31 Oct bill, what `first_paid` the desk held on 15 Nov.

**Why it matters to a customer.** Under SLC 27 and the Standards of Conduct, a supplier's collections contact must
be accurate. Telling a customer who paid on time that they missed a bill is a complaint in itself. The arrear
that is never collected or planned is a separate, known class: "debt held flat after the last rung".

**Why no row caught it.** `INV_COLLECTIONS_EVENTS_ORDERED` grades the order of rungs, not whether the event that
moved the case happened. No row asks whether a "missed" step follows a missed payment.

## Done (2026-11-03)

**The cause, measured. The oldest-first hypothesis above is refuted.** The desk held no `first_paid` at all.
`CollectionsJourneyDesk.advance` passed `bill_missed = on in missed` to `_step`, and `missed` is the set of
days after *every* bill's due date. So the re-offer fired on the calendar alone, and no allocation was read.
For PROS-2017-0233 the 31 Oct bill (£39.31, due 14 Nov) was collected in full on 14 Nov. On 15 Nov the desk
re-offered because a bill's due date had passed. The same happened on 17 Dec and 20 Jan. The new test
reproduces those three dates on today's code. Oldest-first would have given the same wrong answer, because
it puts the £35.45 on the newest bill. That is why the fix does not use it.

**Book-wide on the published 0a6391d186 pages** (legs grouped by base account, each bill judged on its own
leg's cash). All 6,599 re-offers share this one code path.
- 4,742 (72%), on 235 accounts, fell on a day when every bill then falling due had been paid in full
  between its issue and its due date.
- 1,756, on 123 accounts, followed a bill that was short.
- 101, on 3 accounts, fell on a day with no published bill falling due. That is not traced.

**The rule, written before the build:** `docs/market_research/company_debt_management.md`, "A further bill
missed means the bill was not paid". Oldest-first allocation ages the balance. It is not a statement that a
bill was missed. Under SLC 0 the contact must be "complete, accurate and not misleading". The test of "this
bill was paid" is the desk's own choice, recorded as GAP A6.

**The fix:** `collections_journey.bill_paid_in_its_window`. A re-offer now needs a bill that falls missed that
day *and* whose cash from issue to due falls short of it. The standing arrear is left alone, as `1eaf19d78`
recorded: the case still holds its rung until it cures.

**Control:** `tests/company/billing/test_a_reoffer_follows_a_missed_bill_not_a_standing_arrear.py`. It is red
on origin's code and green after the fix. It asserts the partition first: the same account re-offers when
December is truly missed.

**Not yet graded:** the prediction on the knowledge page. Re-offers should fall to between 1,600 and 1,900,
with none after a bill paid in its window. It needs the next full run. `INV_COLLECTIONS_EVENTS_ORDERED`
still grades order only. A domain-invariant row that asks whether a re-offer follows an unpaid bill is the
next control, for the suite.
