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
