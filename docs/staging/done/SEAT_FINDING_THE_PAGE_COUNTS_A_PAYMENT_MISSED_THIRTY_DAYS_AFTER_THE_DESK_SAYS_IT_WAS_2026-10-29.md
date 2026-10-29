**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The page counts a payment missed thirty days after the desk says it was, so a debt story opens on "0 missed" (2026-10-29)

**Source:** leg two of the third cold read
(`records/SEAT_READING_THE_THIRD_COLD_READ_ON_THE_129E7DE698_BOOK_2026-10-28.md`). The debt slot's
validity predicate in `tools/generate_explore_cast.py` now reads the page's own record
(`_debt_page_failures`). One of its three checks refuses a story whose page prints "nothing missed
or returned" beside a moment that says a payment was not made. SYN-2016-356 printed "4 of 4 bills
paid, 0 returned, 0 missed" at its "Missed a payment" moment.

**What the two records each count.**
- The household summary's `Payment record` (`payment_record`) counts a bill as missed once its due
  date **plus `PAYMENT_WINDOW_DAYS` (30)** has passed with no payment on it. That is
  INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE's stated belief.
- The desk's `collections_missed_payment` is dated when "a bill is unpaid past its due date". That is
  the due date, with no window.

So on a household's first miss, the page's own summary says nothing was missed until 30 days
into the journey. That is the definition with two homes, not a counting error.

**Measured.**

| book | debt-rule matches | refused by this check |
|---|---|---|
| 209c3350ab | 402 | 112 |
| the published book in `site/data/customers` at the time of writing | 599 | 599 |

On the published book this check alone empties the slot. On 209c3350ab the slot fills (PROS-2018-0222).

**What closes it.** One definition of a missed payment that both the summary and the desk's moment
print. Either the counter counts the bill the desk has opened a journey on, or the moment is dated
at the end of the window. This choice touches the payment-record row, so it goes knowledge page first
(K8). The predicate is not patched around it. `ACCOUNTED_BY["debt"]` names this finding while the
slot is empty for this reason.

**Noted on the 209c3350ab fill, not checked:** PROS-2018-0222 moved out on 13 Aug 2019, and its debt
story collects the final balance with no moment showing the move. The tariff row prints one
"132.0 £/MWh" fix across both fuels, which is the first read's O1/O2 class. The fourth cold read
should grade both.

## Done

2026-10-29: a missed payment now has one definition, and both records read it.
- **The definition.** A bill not paid by its due date is missed from the day after:
  `company/billing/collections_journey.missed_on` / `bill_missed`.
- **The desk** opens its journey on that day.
- **The household summary's `payment_record`** counts the bill missed from the same day, and counts a
  returned DD on the day it is returned.
- **The knowledge** is in `debt_and_collections.md` s.7.5. The 30 days was the Bacs retry window, not
  a miss.
- **The invariant row** now reads the due date, and so does the runner's own evaluator, which still
  imports nothing it grades.
- **Measured** in `records/SEAT_PREREGISTRATION_ONE_DEFINITION_OF_A_MISSED_PAYMENT_ON_BOTH_BOOKS_2026-10-29.md`:
  - 209c3350ab: this check's refusals fell from 112 to 0, and the slot fills with PROS-2016-0054.
  - The published book's inputs: the slot fills with SYN-2016-592.
  - The published pages as they stand carry no due dates. The slot is honestly empty with that
    reason. `ACCOUNTED_BY["debt"]` now names the finding for that cause, not this one.
