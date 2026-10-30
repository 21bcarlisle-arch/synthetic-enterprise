**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# Pre-registration: what the next fresh run should grade on the eight PC2 rows, filed before any run (2026-10-30)

Filed with the fixes for
`docs/staging/SEAT_FINDING_THE_E7_AND_PC2_BUILDS_LEAVE_EIGHT_ROWS_BREACHED_ON_PROFILE_CLASS_2_HOMES_2026-10-30.md`.
No run was launched. Each number below is a prediction for the next fresh run at or after this commit.
Where it says "the run decides", I could not measure it on the cd4fc5b8d8 book.

## The one cause behind five rows

`_estimated_settlement_records` scaled each settlement record by one ratio, taken from the first
register found. The world's daily record carries both registers, so that was always Day's ratio.
A PC2 estimate's Night was therefore Day's estimate over Day's settled kWh, times the settled Night.

- On the cd4fc5b8d8 book, 738 of 1,335 PC2 estimated bills (34 accounts) were charged off their own
  estimate, from 0.28x to 13.4x.
- PROS-2017-0336, December 2022: estimate 2,843 kWh, charged as 38,178.
- The page printed the intended kWh (the read log's `estimated_consumption_kwh`) beside the
  mis-scaled money and the mis-scaled bill total.
- The inflated winter estimates broke the resi ceiling. They sat above every rate the meter had
  measured, so they stayed held: 180 held PC2 bills, released only at the next actual read, where
  SLC 21BA wrote off the part older than 12 months.

Measured on the book's own inputs: at the intended estimates, 9 of the 180 stay held, all on the
three electric-heating accounts the carbon exception already names (PROS-2024-0010, PROS-2025-0106,
SYN-2016-582). None of the nine falls between October 2022 and March 2023.

## Per row (cd4fc5b8d8 count -> predicted)

| Row | cd4fc5b8d8 | Predicted | Bill or row | Basis |
|---|---:|---:|---|---|
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 4 | <= 1 (the excepted PROS-2017-0117) | bill (point 1) | The four are the held-then-written-off winters. Not measured: the write-off needs the run. |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 120 | <= 6 (the excepted class) | bill (point 2) | All 79 account-year kWh hits agree within 1% at intended estimates with held months left out. The 41 month-count hits are held months. |
| INV_EBSS_CREDIT_EACH_MONTH / _ON_THE_BILL | 21 / 21 | 6 / 6 (the excepted void and deemed months) | bill (point 3) | All 15 PC2 hits are "no bill", which are held bills. None of the 9 left held is in the window. |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 170 | <= 10 | row (point 4), plus the bill | The row reshaped a PC2 meter on PC1's shape, and is now graded per register on PC2's shape. Re-graded on the same ledger: 10. Of those, 4 sit on bills point 1's fix moves and 2 on the void bills point 5 fixes. The run decides the rest. |
| INV_E7_METER_BILLED_ON_TWO_REGISTERS | 4 | 0 | world record (point 5) | Void days kept their band kWh. |
| INV_TOU_BANDS_SUM_TO_THE_TOTAL | 2 | 0 | world record (point 5) | The -481 and -260 kWh were the Anytime stubs. |
| INV_PERIODS_CONTIGUOUS | 2 | 0 | bill (point 6) | Both gaps are runs of held bills at the book's end (OCC-8c6b8bb21743 April-May 2025, PROS-2020-0189 November 2024-March 2025). Neither account is among the 9 left held. |
| Storage-heating Explore slot | empty | fills | page (point 7) | The page never wrote `profile_class`. Whether a PC2 home passes the slot's own use predicates is for the run to decide. |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 4 (excepted) | <= 4 | bill | The two PC2 runs were inflated estimates. The run decides. |

**Refutation.** Any row above its predicted count on the next fresh run refutes the claim that this
cause explains it, and is traced again. I will not re-explain it after the fact.

## Not fixed here, seen

- `INV_SVT_ONE_PRICE` (690) was the row, fixed in 8b046d413.
- The usage panel's docstring says "real settlement consumption", but it sums the bills'
  `total_consumption_kwh`, estimates included. It only agreed with the carbon panel because both
  read bills.
- The EAC split before a meter's reads span an advance gives a storage home about 50/50 Day/Night
  on PC2's average shape, against its real ~95% Night (GAP G7 on the knowledge page). The
  estimate's total is right in scale. The split is the GAP's.
