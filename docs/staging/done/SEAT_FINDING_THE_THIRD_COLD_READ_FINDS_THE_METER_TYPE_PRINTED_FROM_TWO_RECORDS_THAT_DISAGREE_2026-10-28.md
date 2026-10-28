**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The third cold read finds the meter type printed from two records that disagree (2026-10-28)

**Source.** The third cold read's O25, on the 129e7de698 book
(`records/SEAT_READING_THE_THIRD_COLD_READ_ON_THE_129E7DE698_BOOK_2026-10-28.md`, class N8). It is BLOCKING
because it is the read's only new class, and the correctness stretch cannot exit while a page carries it.

**What the page prints.** On SYN-2016-479 and PROS-2025-0153, one household page carries both:
- the header panel's "Meter	Traditional";
- the day clock's "This household has a smart meter and there is still no day to draw".

**Where each comes from.**
- The header comes from `tools/generate_customer_data._meter`. That asks `saas.customers` and
  falls back to "Traditional" when the record carries no smart flag.
- The day clock comes from `site/explore/index.html` `hhDayPanels`, which reads
  `HH_META.smartUnread[group]`, a different record.
- On this ledger SYN-2016-479 is billed on read type `M` on all 15 periods of both fuels.

**Before deciding which is right, what each counts.** The header label means the meter installed
at the premises. The day clock's group means a meter capable of half-hourly reads that is not being
read that way. Both should rest on one fact: the meter type the company holds for the supply point.
**I cannot yet say** which record is wrong. `_meter`'s docstring records the same class fixed once
before for C1 (2026-07-09), but on the label side only.

**Next.**
1. Trace both sources for the two households.
2. Make the page take the meter type from one home, the company's own record of the supply point.
3. Add a blind row, written from the smart-metering knowledge page rather than this code: "every
   meter type a household page prints, in any panel, is one value per supply point and agrees with
   the read types billed".
4. Grade it on the next fresh run.

## Done

2026-10-28, item `the-meter-type-has-one-home`. Graded in
`records/SEAT_PREREGISTRATION_THE_METER_LABEL_FROM_THE_BILLED_READS_GRADED_ON_THE_129E7DE698_BOOK_2026-10-28.md`.

- **Which record was wrong: the header.** On the 129e7de698 book the day clock's "smart meter" was
  true: SYN-2016-479 has 15 of 15 smart reads and PROS-2025-0153 has 1 of 1. The header's
  "Traditional" came from `saas.customers` read at page-build time. That book carries no smart flag
  for a drawn household. The same default mislabelled **273 of 1,293 accounts**. Their read type `M` is
  prepayment charged at the meter, which is consistent with a smart prepayment meter.
- **Why the two disagreed on one page.** The cold read's scratch render rebuilt the customer records
  and not `explore_hh_days.json`, so the day clock read a 26 Oct feed. The publish chain rebuilds
  both. Even so, two records were one too many.
- **The one home.** `tools/generate_customer_data.meter_types_billed` gives the meter of each
  account's latest read in the run's `meter_read_log`, the reads its bills were cut on. `_meter`
  labels from that, and prints `None` ("—") when there is no read, never "Traditional" by default. The
  day clock (`site/explore/index.html` `hhDayPanels`) chooses its sentence from the same field on the
  household's electricity record. It no longer reads `smart_meter_but_no_hh_reads`, which stays
  published for its counts. Rebuilt on the 129e7de698 book, all 1,293 labels agree with the reads:
  282 Smart, 1,011 Traditional.
- **A third record, found while tracing: the cast's truth panel.** `generate_explore_cast._truth`
  prints "Smart meter Yes/No" from `customer_sample.json`. `generate_customer_sample` read that flag
  from the same import-time book, so it printed "No" on 56 households billed on smart reads (C7, C8,
  C9 and 53 OCC/PROS legs). It now takes the flag from `meter_types_billed` too. With no read the row
  prints "Not recorded" rather than "No". Rebuilt on the 129e7de698 book: 1,293 of 1,293 agree with
  the reads.
- **Controls.** `tests/tools/test_generate_customer_data.py` holds the label to the billed reads on
  both meter types, after a meter exchange, and with no read. `tests/tools/test_generate_explore_hh_day.py`
  reds if the day clock reads a second meter record again, or loses either sentence.
  `tests/tools/test_generate_customer_sample.py` holds the sample's flag to the reads, against a roster
  that says the opposite on both meter types.
- **Not done here: step 3's blind row.** The ruling wants it written by an agent that has not read
  this code, and I have read it. It is handed on as `the-meter-type-row-written-blind`.
