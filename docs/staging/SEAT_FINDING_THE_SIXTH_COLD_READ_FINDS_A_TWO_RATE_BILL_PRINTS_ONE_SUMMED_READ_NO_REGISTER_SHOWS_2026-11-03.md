**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The sixth cold read finds that a two-rate bill prints one summed read, which no register on the meter shows (2026-11-03)

**Source.** This is class N12 of the sixth cold read, on the 85b044be54 book
(`docs/staging/records/SEAT_READING_THE_SIXTH_COLD_READ_ON_THE_85B044BE54_BOOK_2026-11-03.md`).
- The seat found it during named check (b): do storage-heated pages bill Day and Night?
- It is BLOCKING because it is a new class, and the correctness stretch cannot exit while a page carries one.

**What the page prints.** PROS-2017-0233 is the storage-heating slot, on its Billed stage (bill INV12356, Aug 2018):
- the bill: "Usage (Day) 131.8 kWh × 13.13p/kWh" and "Usage (Night) 52.3 kWh × 3.37p/kWh". This is right;
- the panel under it, "Meter reads behind it": "Opening read 3,622.7", "Closing read 3,806.8",
  "Difference charged 184.1 kWh".

**What the record holds.** The register reads are right:
- Day 1,978.5 → 2,110.3 and Night 1,644.2 → 1,696.5.
- 3,622.7 is Day plus Night, and so is 3,806.8. This is a traditional Economy 7 meter, whose display shows its
  registers and no sum of them. *Corrected 2026-11-03 by the blind row-writer:* a smart (SMETS2) meter does keep a
  total register equal to the band sum (`docs/market_research/a_multi_register_meters_bands_add_up_to_its_total.md`).
  So the defect on either meter type is the sum printed *instead of* the band reads, not a total printed at all.
- A customer checking the bill against the meter, or a meter reader, could not reconcile it.
- The first bill prints "Opening read 0.0" over Day 0.0 and Night 0.0. That is the open opening-read finding
  (`…PRINTS_6436_OPENING_READS_NOBODY_TOOK_2026-10-28.md`), not this class.

**Confirmed in the page code.**
- `site/explore/index.html` `gasReadRows(inv)` prints `inv.opening_read_kwh` and `inv.closing_read_kwh` for any bill
  without a `read_unit`, which means every electricity bill.
- It never reads `inv.registers`, which carries each register's own opening and closing read.
- Book-wide, this affects every bill on a profile class 2 page that the Billed stage shows: 1,731 bills on 39 pages
  hold two registers.

**Why no row caught it.**
- `INV_TOU_BANDS_SUM_TO_THE_TOTAL` and `INV_E7_METER_BILLED_ON_TWO_REGISTERS` grade the record, which is right.
- No row grades what the reads panel prints against the registers it sits under.
- A blind row should grade the printed read set: one opening and closing read per register the bill charges.

**The fix, for whoever draws it.**
- Print one opening/closing pair per entry of `inv.registers` when there are two or more, labelled as the bill's
  usage lines are, as Day and Night.
- The summed pair stays only for a single-register meter.
- A door test should render a PC2 bill and fail if a printed read equals the sum of two register reads.
- This is page-only. The ledger and the bill are right.
- Reverse: delete this file.
