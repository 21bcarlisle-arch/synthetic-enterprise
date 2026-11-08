**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The ninth cold read finds direct debits collected on weekends and on Christmas Day: 29% of collections fall on a day Bacs does not settle (N22, 2026-11-08)

**Found by.** The ninth cold read's O18, on the af31e73fa7 book
(`records/SEAT_READING_THE_NINTH_COLD_READ_ON_THE_AF31E73FA7_BOOK_2026-11-08.md`). The reader, a revenue-assurance
auditor, quoted "25 Dec 2017 payment received £-46.85", "26 Feb 2017" (a Sunday), "10 May 2025" (a Saturday) and
"14 Oct 2017" (a Saturday). None of the eight earlier reads raised it.

**Confirmed over every page.** The page files are `/var/tmp/ninth-read/tree/site/data/customers/`, and the script is
`/var/tmp/ninth-read/scripts/candidates.py`.
- 10,546 of 36,096 direct-debit collections (**29.2%**) fall on a non-working day: 5,184 on a Saturday, 5,191 on a
  Sunday and 171 on 25 Dec, 26 Dec or 1 Jan.
- They are spread over 922 accounts.
- 2/7 is 28.6%. So the collection dates are drawn with no working-day calendar at all.

**Why it is wrong.** Bacs processes and settles on banking days only. A collection due on a weekend or bank holiday
settles on the next working day (or the one before, under the originator's rules). The knowledge page
`docs/market_research/payments_and_direct_debit_2026-10-25.md` already counts in working days for advance notice,
AUDDIS and ARUDD. No row grades the date a collection lands.

**What it touches.** Every dated DD credit on the page ledger. It also touches the level DD schedule
(`level_dd_collections`, a fixed day of the month), and so any "missed by the due date" test that compares a
collection date with a due date.

**Next.** A blind row has been written (`INV_*` rows from `/var/tmp/ninth-read/blind_rows_N22_N24.yaml`, landed
`checkable: false`). Its evaluator is owed. The fix belongs where collection dates are drawn. **I cannot yet say** whether that is the
world's draw or the supplier's schedule, because I have not read either for this.

**Reverse.** Delete this file.
