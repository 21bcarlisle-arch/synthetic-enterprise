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

## Done

*3 Nov 2026, worker (lane 0 draw `n16-the-explore-label-reads-the-term-in-force-and-the-storage-slot-reads-heating`).*

- **The label reads the term in force.** `tools/generate_explore_cast.py` `_leg_term` / `term_in_force` now
  read each leg's `term_tariff_type` from the bill whose period has begun by the moment. A `renewed` record
  after that period start counts as a fix begun before its first bill. The customer's "Your tariff", the
  back office's "Tariff" and the renewal message all go through it. A dual-fuel home whose legs differ
  prints each leg's term. The renewal message says "Your fixed tariff is ending" only on a fix, and "You are
  on our standard variable tariff" on SVT. The glossary no longer says every renewal is a fix ending.
- **Agreement table** (probe `/var/tmp/n16-probe/agree.py`: each billed moment against the bill covering
  its date, on the same book). Before: **2 of 21** agree. After: **20 of 21**. The one left is SYN-2016-031's
  "Renewed" moment on 24 Jan 2024. Its covering bill is the January SVT bill, and the label is the fix that
  began that day, confirmed by the February bill (fixed). It is the term in force, not a disagreement.
  Five moments have no covering bill (after supply ended, or before the first bill). They print the last
  term on record. The finding's own count was 3 of 22 on a slightly different moment set; this note uses the
  probe's count for both before and after.
- **What it re-diagnoses.** On the cast, "a fix billed at the cap" was this label. SYN-2016-031 now reads
  "Standard variable since 1 Feb 2020" at its renewal decision. SYN-2016-210 and SYN-2016-368 read "Standard
  variable since 1 May 2020" and "since 1 Sep 2019" over their SVT bills. Whether any fixed-term bill in the
  book is priced off its contract is still the question measured in the separate contracted-tariff finding.
- **The storage slot reads heating, not the meter.** New check: at least 53% of actual-read units must be on
  the night register (`STORAGE_NIGHT_SHARE_FLOOR`, the lowest share Nottingham CHA measured in storage homes),
  across bills that include a winter and a summer one. The winter bill shown must be an actual read. K8:
  `docs/market_research/a_storage_heated_homes_default_tariff_is_two_rate.md`, "Telling a storage-heated
  home from its bills". The slot now holds **PROS-2020-0189**: 81% night across its actual reads, and the Dec
  2020 bill shows Night 1,013.2 kWh against Day 174.8 kWh, on an actual read. PROS-2017-0233 (45%, no actual
  reads) no longer qualifies.
- **The door.** `site/explore/test_the_tariff_label_is_the_term_in_force.py` grades every printed label
  against the household's own published bills. It reds on the 0a6391d186 cast (37 disagreements over 20 graded
  moments) and is green on the regenerated one. It also grades the storage slot's night share from the
  customer file. Unit legs are in `tests/tools/test_generate_explore_cast.py`.
- **Left open, not this class.** The new storage household carries one `above_cap` flag (Jun 2022, 28.71p
  against a single-rate ceiling of 28.34p). The coverage check grades a two-rate bill against the single-rate
  ceiling, whereas the cap grades it on the multi-register benchmark (SLC 28AD.36(a)). Separately,
  `test_every_gap_the_cast_finds_is_accounted_for_by_an_open_finding` is red in the shared tree only, because
  another lane has moved the EV and above-cap findings to `done/` without committing the move. Both are still
  open in HEAD.
