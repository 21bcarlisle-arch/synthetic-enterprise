**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The seventh cold read finds the Explore tariff label ignoring the term in force: an SVT customer is told "your fixed tariff is ending" four years after it ended (2026-11-03)

**Source.** Class N16 of the seventh cold read, on the 0a6391d186 book
(`docs/staging/records/SEAT_READING_THE_SEVENTH_COLD_READ_ON_THE_0A6391D186_BOOK_2026-11-03.md`, reader's O1 and
O2). It is BLOCKING because it is a new class, and the correctness stretch cannot exit while it stands.

**What the page prints.** The renewal slot, SYN-2016-031, 24 Jan 2024:
- the customer sees "Your fixed tariff is ending. We have an offer for you." and "Your tariff: Fixed from 25 Jan 2019";
- the back office shows "Tariff: Fixed at 152.0 £/MWh from 25 Jan 2019".

**What the record holds.** SYN-2016-031's bills (`term_tariff_type`) run as follows: fixed 2016-01 to 2017-01, SVT
to 2019-01, fixed 2019-02 to 2020-01, **SVT 2020-02 to 2024-01**, then fixed. In Jan 2024 the household had been
on the default tariff for four years. It was being offered a fix, not renewing one.

**Across the cast:** 26 moments print a tariff, and on 22 of them a bill is on record. On those 22:
- 11 print "Fixed …" while the household is billed on SVT (renewal, mover, debt);
- 8 print "Standard variable" while it is billed on a fixed term (switch-in, estimate trap, storage);
- 3 agree.

**Cause** (`tools/generate_explore_cast.py`):
- Line 497 prints "Fixed from <date>" if any renewal is on record and "Standard Variable" otherwise.
- Line 543 sets `on_fix` if any renewal predates the moment.
- Line 395 prints the back-office "Fixed at … from …" the same way.
- None of them reads the term in force. A fix that rolled to SVT stays "Fixed" forever, and a joining fix (not a
  `renewed` event) is shown as SVT. The bills carry `term_tariff_type`, so the fix is page-side.

**What this re-diagnoses.** Every read since the first has filed "a fix billed at the cap" (first read O5, here O1:
"Fixed at 152.0 £/MWh … 399 kWh … £125.95"). On the cast households that is at least partly this label: the bills
are SVT bills at the cap, under a stale "Fixed" label. Whether any fixed-term bill in the book is still priced off
its contract is a separate question, which `SEAT_FINDING_THE_PRINTED_RATE_AGAINST_THE_CONTRACTED_TARIFF_2026-10-26.md`
measured. The sixth read's O15 (an account's current tariff name over a fixed-term bill in Section B) is the
same kind of error on another surface.

**Why no row caught it.** `INV_COMMITTED_PRICE_IS_THE_TARIFFS_PRICE_PER_FUEL_AT_A_DATE` is UNCHECKABLE by the runner,
since the panel is computed in the page. No row grades a printed tariff label against the billed term at the same date.
