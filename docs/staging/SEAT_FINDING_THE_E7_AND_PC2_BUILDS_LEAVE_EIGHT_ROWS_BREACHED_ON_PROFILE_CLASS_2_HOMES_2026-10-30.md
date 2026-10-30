**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The E7 and PC2 builds leave eight rows breached on profile class 2 homes, and the publish is refused (2026-10-30)

Found grading the fresh cd4fc5b8d8 book
(`docs/staging/records/SEAT_RECORD_THE_CD4FC5B8D8_BOOK_GRADED_AND_ITS_PAGES_BUILT_2026-10-30.md`), under ruling
step 3's storage-heating cause.

The 3dc5a92948 book had 0 unexcepted breaches. This book has 1,034 across 9 rows.
- 690 are the SVT one-price row, which pooled single-rate and E7 SVTs. Graded per metering arrangement they are
  0, and the record's commit fixes the row.
- **The other 344 sit on profile class 2 accounts, every one of them**, apart from the 6 PC1 EBSS breaches,
  which are the old ceiling.

The Economy 7 two-register bill (fca63e87d) and the PC2 per-register estimate (32ddfa8ca) landed together, so I
cannot yet say which build, or which row, owns each one. What is established is where they land. Every breach is
listed in `/var/tmp/grade-cd4f-trace/all_hits.json`.

## The trace owed, row by row, and what each looks like so far

1. **INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE, 4 accounts.** The page's bills before VAT fall well short of the
   revenue the settlement records hold:
   - PROS-2017-0336: £25,178 against £29,052
   - SYN-2016-565: £15,538 against £17,035
   - PROS-2020-0189: £7,487 against £7,711
   - OCC-8c6b8bb21743: £1,850 against £1,987

   This looks like the bill and not the row. A register's energy or charge is in revenue but not on the
   printed bill. Check first whether `_real_invoice` and the page sum both registers' lines.
2. **INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL, 120 on 22 accounts.** The carbon panel reads mostly *more*
   than the usage panel, for example OCC-23ee23cb44e4 at 3,396 against 2,491 kWh in 2022. That is consistent
   with one panel counting a total register beside its Day and Night registers, or the other counting one band.
3. **INV_EBSS_CREDIT_EACH_MONTH / _ON_THE_BILL, 15 new on PC2.** These are electricity bills from Nov 2022 to
   Mar 2023 printing a £0 EBSS credit against £65-£66 due. The likely cause is the multi-register bill path
   dropping the credit line.
4. **INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS, 170 on 31 accounts.** These are seasonal: 87 above,
   concentrated Nov-Mar, and 83 below, concentrated Jun-Sep. That is the pattern of a PC2-shaped estimate graded
   against the row's PC1 reshaping. The PC2 estimate finding's P2 named this cause in advance, but the row's
   bound on a PC2 home has not been read. If that is the cause, the row needs PC2's shape. If it is not, the
   estimator is wrong.
5. **INV_E7_METER_BILLED_ON_TWO_REGISTERS 4 and INV_TOU_BANDS_SUM_TO_THE_TOTAL 2.** Both are on
   OCC-23ee23cb44e4 and OCC-7e06d09fc108, two occupier accounts whose first two bills print `Anytime` before
   switching to Day/Night. The two band rows read -481 and -260 kWh at that change.
   - The occupier account's opening path appears not to take the PC2 stamp until its second month.
   - The E7 finding's N1 allowed flags only on one-band stubs, and these are breaches.
6. **INV_PERIODS_CONTIGUOUS 2.** These are gaps between periods: 62 days on OCC-8c6b8bb21743 (Mar-Jun 2025) and
   152 days on PROS-2020-0189 (Oct 2024-Apr 2025). Both accounts are PC2, and both are also on the revenue row.
   A missing run of bills would explain both rows on those accounts.
7. **The storage-heating Explore slot.** It is empty on "the record names no profile class 2 meter" for all
   132 households its rule matches, while 31+ accounts carry PC2 periods. The slot reads a field the E7 build
   does not write, or reads it from somewhere else. `tools/generate_explore_cast.py` is the place to start.

## What done means

Each row is traced to the bill or to the row. Each bill defect is fixed with a test that reds on the
cd4fc5b8d8 shape. A row defect is fixed the way the SVT row was. A fresh run then grades all eight at or below
the 3dc5a92948 counts. The storage slot either fills or names a check that is true of the book.

## Traced 2026-10-30: each point named bill, row or record, with its fix

Severity is now LATENT, not BLOCKING. Every point has a landed fix. What is left is the next fresh
run grading the predictions in
`docs/staging/records/SEAT_PREREGISTRATION_THE_PC2_FIXES_PREDICTED_PER_ROW_FOR_THE_NEXT_FRESH_RUN_2026-10-30.md`.
No run was launched.

- **1 (revenue): the bill.** `_real_invoice` and the page sum both registers. The cause is upstream.
  `_estimated_settlement_records` scaled each record by Day's ratio alone, so Night took Day's ratio
  (PROS-2017-0336, December 2022: estimate 2,843 kWh, charged as 38,178). The inflated winters broke
  the resi ceiling and stayed held, 180 held bills on 5 PC2 accounts. They were billed at the next
  actual read, where SLC 21BA wrote off anything over 12 months old. Fixed: each register takes its
  own ratio. The new test reds on the cd4fc5b8d8 code (Night 266 against 133).
- **3 (EBSS): the bill, the same cause.** All 15 PC2 hits are "no bill", which are held bills. There
  is no multi-register path that drops the credit.
- **6 (gaps): the bill, the same cause.** Both gaps are runs of held bills at the end of the book.
- **5 (Anytime first bills): the world's record.** It is not the PC2 stamp: the stamp and the band
  fields are there from day one. `sim/customer_state_layer.as_void_row` zeroed `consumption_kwh` and
  kept the occupied day's `tou_*_kwh`. The bands stopped reconciling with the bill, its registers were
  withheld, and the page printed one Anytime register. Fixed with a test.
- **2 (carbon against usage): the bill, the same cause.** The page printed the intended kWh, while the
  usage panel read the mis-scaled bill total. All 79 account-year kWh hits agree within 1% at the
  intended estimates with held months left out. The 41 month-count hits are held months.
- **4 (estimate row): the row, as P2 predicted, and partly the bill.** The row reshaped a PC2 meter on
  the domestic (PC1) shape. It now takes each register's reference from the printed register reads,
  reshaped on PC2's register share (twelve-month table added to the K8 page). Re-graded on the same
  ledger: 170 -> 10. Several of the 10 are bills point 1 moves. The rest are for the run to say.
- **7 (storage slot): the page.** `tools/generate_explore_cast.py` reads `profile_class` from the
  customer page, and `tools/generate_customer_data.py` never wrote it. The page now carries the latest
  bill's class, and the MPAN top line prints it (02, not a hard-coded 01). Whether a PC2 home then
  passes the slot's use predicates is for the run to say.
