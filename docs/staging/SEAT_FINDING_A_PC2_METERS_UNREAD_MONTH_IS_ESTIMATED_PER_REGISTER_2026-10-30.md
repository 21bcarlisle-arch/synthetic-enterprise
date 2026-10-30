**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A PC2 meter's unread month is estimated per register on PC2's published shape: the build and the predictions for the next fresh run (2026-10-30)

This is the estimate half of choice 3 in `docs/market_research/a_storage_heated_homes_default_tariff_is_two_rate.md`,
and the last storage-heating cause in ruling step 3
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`). The K8 page
was amended before the build, with the section *What PC2's published shape says about an unread month*
and GAPs G6-G8.

## The defect

The E7 build (e400c589d) billed a PC2 meter on its Day and Night registers but left two problems in the estimate:

1. **The estimate was the meter's total, shaped by the PC1 proxy.** A storage home's Night register is
   the seasonal one: PC2 puts 4.1 times as much of the year's night use in January as in August, against
   PC1's 1.4. A total on PC1's shape therefore carries winter night heat into a summer month.
   The probe `/var/tmp/pc2-shape-probe/table.py` builds a 7,000 kWh home at a 60% night share and
   estimates each month from its last three monthly reads. The old estimate is 16-36% high from April
   to August and 15-33% low from September to December.
2. **The total was split into registers in the unread month's own settled ratio.** No read gave the
   company that split, so it was world truth reaching the bill (`_estimated_settlement_records` scaled
   every row by one ratio).

## The build

- **`company/billing/unread_month_estimate.py`**: adds `PC2_MONTHLY_REGISTER_SHARE`, 24 monthly
  per-register shares from UKERC's verbatim `ProfileClass2.csv`. It is the same published table the world
  settles on, run through the BSC season calendar for 2016-2025, split at 00:30-07:30, and copied as
  knowledge. It does not import `sim/`.
- The module also adds `estimate_unread_register_kwh` (each register's own advance over its own PC2 weight),
  `opening_register_estimate_kwh` (the registry EAC split on PC2, page G7) and `split_on_register_shape`.
- **`company/billing/monthly_bill_assembly.py`**: on a meter `tou_desk.meter_is_economy_7` reports, each
  actual read records each register's advance. This includes the advance across an estimated run, through
  the pending run's `used_register_kwh`.
- An unread month on such a meter is estimated per register by the same three routes as before:
  - its own reads;
  - else the registry EAC;
  - else, when switched on, the annualised total (G8).
  
  Each route is split on PC2. The Day and Night rows are each scaled by their own register's ratio. A
  month with a register that has no settled rows falls back to one ratio.
- **Test**: `tests/company/billing/test_a_pc2_meters_unread_month_is_estimated_per_register.py`.
  - The home in the test doubles its Night use in an unread August.
  - The PC2 meter bills 319.0 kWh: Day 185.8, plus Night 133.2 on PC2's shape. The same home on PC1
    bills 389.9 kWh, split in the true month's ratio.
  - Three mutations each turn the test red, as the file records.
- The 2,533 tests under `tests/company/billing` and the E7 test pass.

## What this does not settle

- **The row grades on PC1's shape.** `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` reshapes its
  references on the DESNZ PC1 proxy for every meter, so it encodes one method. The director's ruling of
  30 Oct, step 6, already asks for it to be redrawn against the supplier's declared estimation policy.
  - `/var/tmp/pc2-shape-probe/band.py` measured the new estimate at night shares of 45% and 60%, with
    monthly reads. Every month sits inside the band: 1.25-2.07 times its lower edge and 0.48-0.92 times its upper.
  - The book's reads are sparser. A short reference across a season change is where a breach could
    come from.
- **G6-G8 on the K8 page**: the 1997 table rather than the period's coefficients; one registration EAC
  rather than one per register; an annualised advance on the total.
- **Other estimate routes stay on PC1's shape**: a void stub's even spread (`_estimate_records_at_tariff_rate`),
  and the tools `closing_estimate_run_money` and `theft_void_screen_probe`.

## Predictions for the next fresh run (filed before it exists)

These replace N5 in `SEAT_FINDING_AN_ECONOMY_7_METER_IS_BILLED_ON_ITS_TWO_REGISTERS_2026-10-30.md`, which
predicted that the three would NOT leave without this build.

- **P1.** E2 (a)'s three summer over-estimates (PROS-2017-0336, PROS-2024-0010, SYN-2016-565) leave
  `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS`. If any stays, the first cause to check is the
  reference window: its last two reads span a season change, and the row reshapes that span on PC1.
- **P2.** No storage home gains a breach of that row from the estimator. Any new breach is the row's
  PC1 reshaping (ruling 30 Oct, step 6), not this estimate, and is graded as such.
- **P3.** `INV_E7_METER_BILLED_ON_TWO_REGISTERS` stays at 0 breaches. Estimated E7 bills still print both
  registers, and they add up.
- **P4.** Across the storage homes, estimated kWh per estimated bill falls from April to August and
  rises from September to December, compared with the e400c589d build's run. The non-E7 book is
  byte-identical: the new branch is gated on the PC2 stamp.
