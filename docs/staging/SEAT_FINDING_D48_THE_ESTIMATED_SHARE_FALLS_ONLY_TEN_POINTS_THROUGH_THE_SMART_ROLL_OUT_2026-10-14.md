**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** unbilled-energy-and-revenue-assurance

# The estimated share of billed kWh falls only about ten points from 2016 to 2025, through the whole smart roll-out (2026-10-14)

*From D48 Expert Hour, 2026-10-14. Adjudication: `SEAT_FINDING_D48_THE_EXPERT_HOUR_FAILS_ON_THE_CLAIM_NOT_THE_MEASURE_2026-10-14.md`. Not fixed in the turn that found it.*

The page publishes one cumulative figure (66.5% electricity, 64.7% gas). Split by period_end year from the bills of run_output_2248e3baf_20261013T134447Z (39,084 bills), it is:

| Year | Electricity, estimated kWh | Gas, estimated kWh |
|---|---|---|
| 2016 | 68% | 72% |
| 2017 | 70% | 66% |
| 2018 | 69% | 67% |
| 2019 | 70% | 63% |
| 2020 | 69% | 65% |
| 2021 | 67% | 68% |
| 2022 | 67% | 64% |
| 2023 | 61% | 65% |
| 2024 | 59% | 59% |
| 2025 (H1) | 61% | 59% |

The share by bill count tracks the share by kWh within 3 points in every year.

The reviewer's prior was 35-45% falling to 10-20%, with gas above electricity. Its level assumed quarterly billing. This book bills monthly, and under monthly billing about 70% of bills on estimates is not by itself implausible for traditional meters. **The trend is the defect.** About 10% of installed smart meters are not in smart mode (`q6_smart_not_in_smart_mode_share`). A book that went smart at anything near the national rate should have shed most of its estimates by 2024.

Slice 4 attributed the level to "the world's flat gas-heated homes". That explains a level, not a flat trend, and it was measured on an older run.

**Not established:**
- the book's smart share by year (`meter_reads.meter_type_for_customer` reads `smart_meter`, stamped at acquisition);
- whether a smart meter installed after acquisition ever reaches the read model.

**Measure first:** the smart share among billed accounts by year, set beside the estimated share for smart and traditional accounts separately.
