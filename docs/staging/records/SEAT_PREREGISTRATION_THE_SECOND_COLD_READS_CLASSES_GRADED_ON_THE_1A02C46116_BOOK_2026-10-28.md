**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the second cold read's classes graded on the 1a02c46116 book, and N4 measured (2026-10-28)

Item `the-second-cold-reads-new-classes-become-rows`. The classes are N2, N3, N5, N6 and N7 of
`SEAT_FINDING_THE_SECOND_COLD_READ_FINDS_SEVEN_NEW_CLASSES_AND_THE_SUITE_GRADES_A_RECORD_THE_PAGE_DOES_NOT_PRINT_2026-10-28.md`,
plus section 2 (estimate against the meter) of
`SEAT_FINDING_A_SUCCESSOR_PAGE_PRINTS_A_DIFFERENT_MPAN_AND_ESTIMATES_RUN_FIVE_TIMES_THE_METER_2026-10-28.md`.

**The book.** `/var/tmp/fresh-run-out-1a02c46116`, with its ledger rebuilt at HEAD 2ebb0ac18a into
`/var/tmp/n2n7-grade/ledger.json` by `/var/tmp/fresh-run-scripts/build_ledger.py` (55 s). The page
records are built in memory from that ledger, the way `/var/tmp/ebss1a02-scripts/grade.py` does.

## N4: filed before the measurement

**What is measured.** For each fuel, the same accounts' billed kWh, apportioned to calendar years
by the days of each bill, over accounts supplied for the whole of 2021, 2022 and 2023. Reported as
the ratio of sums and the median per-account ratio, 2021→2022 and 2021→2023. The figure is
unadjusted for weather: the world runs on the real weather, so it compares with the published
UNADJUSTED change.

**The instrument the item names does not answer this.** `domestic_shift_response_arc.json` is a
time-of-use arc. It gives the share of peak use SHIFTED as a function of a peak-to-off-peak price
ratio. It says nothing about how much annual use falls when the price LEVEL rises. The published
level response is in `docs/market_research/how_much_a_same_households_use_moves_year_on_year_and_in_2022.md`
§2. DESNZ, 2021→2022: electricity −8.5% temperature-corrected and −10.3% unadjusted; gas −11.6%
and −19.2%. SERL, same households in winter 2022/23 against 2021/22, weather-corrected median:
electricity −8.4%, gas −10.8%. The cumulative fall 2021→2024 in England and Wales was 9% for
electricity and 13% for gas. The measurement is graded against that note, and the arc is reported
beside it as the wrong instrument.

**Predictions.**
- **P-N4a.** Electricity, same accounts, 2021→2022 ratio of sums between 0.97 and 1.03. The cold
  reader's three years were 2,467, 2,511 and 2,494 kWh, so I expect no price response, against a
  published unadjusted −10.3%.
- **P-N4b.** Gas, same accounts, 2021→2022 between 0.88 and 1.00: the weather share of the published
  −19.2% only (a mild 2022), with no price response on top.
- **P-N4c.** Both fuels' 2021→2023 changes are smaller in magnitude than the published cumulative
  falls (−9% electricity, −13% gas).

If P-N4a holds, the world carries no price-level demand response. That is a world fidelity gap,
filed as a finding, and nothing is built here (the item says build nothing).

## The six rows

A blind agent wrote these with no code access. It read only the knowledge pages, docs/market_research
and the commons. Its blindfold disclosure is in the finding. The predictions below were filed after
the rows and the evaluators, and before any grade ran. Harness: `/var/tmp/n2n7-scripts/grade.py`.

| row | class | grades | prediction |
|---|---|---|---|
| `INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE` | N2 | page | **R1.** BREACHED on 5% to 40% of accounts. The settlement-side revenue values true kWh, and the bills value billed kWh. |
| `INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE` | N3 | page | **R2.** BREACHED on 20% to 60% of accounts with collections due. Today's counter counts ledger rows and arrears cases, not bills. |
| `INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL` | N5 | page | **R3.** BREACHED on more than half of account-years. The carbon panel sums billed kWh by the year a bill starts. The usage panel sums settlement kWh by the month a bill ends. One quantity has two homes. |
| `INV_SMART_METER_BILLED_ON_ITS_OWN_READS` | N6 | invoice | **R4.** BREACHED in every fuel-year that has Smart bills. Nothing I know of makes a Smart meter read more often than a traditional one. |
| `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` | N7 | invoice | **R5.** BREACHED on 10% to 40% of graded estimated bills. |
| `INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER` | estimate against the meter | invoice | **R6.** BREACHED on 1% to 10% of graded runs. SYN-2016-565's shape is not unique. |

**R7.** The 45 rows already in the suite grade as they did on the 1a02c46116 grade
(`/var/tmp/ebss1a02-grade/grade.txt`), except where 971a37583c and ec079776de, which landed since,
reach them. `INV_MPAN_CORE_FORMAT` stays clean. `INV_OVERDUE_WITHIN_PAGE_BALANCE` may move, because
the desk is now posted the issued bill.

## N4 grade (written after the measurement; predictions above unedited)

| | prediction | result | grade |
|---|---|---|---|
| P-N4a | electricity 2021→2022 within 0.97 to 1.03 | 0.997 (139 accounts) | HOLDS |
| P-N4b | gas 2021→2022 within 0.88 to 1.00 | 0.978 (109 accounts) | HOLDS |
| P-N4c | 2021→2023 smaller than −9% / −13% | −2.2% / −2.9% | HOLDS |

The table and its reading are in the finding's "N4 measured" section.

## Grade of the six rows (written after the grade; predictions above unedited)

Ledger rebuilt at 2ebb0ac18a. `/var/tmp/n2n7-scripts/grade.py`, output in
`/var/tmp/n2n7-grade/grade.{txt,json}` (before the fixes) and `grade_after.*` (after them).

| | prediction | result | grade |
|---|---|---|---|
| R1 | N2 breaches 5% to 40% of accounts | 288 of 1,293 (22.3%), plus 28 flagged | HOLDS. The cause I named (true kWh against billed kWh) is wrong: 266 of 316 are the Energy Price Guarantee |
| R2 | N3 breaches 20% to 60% | 631 of 1,125 (56.1%) | HOLDS. 181 after the per-bill counter, all a late DD success with no return |
| R3 | N5 breaches more than half of account-years | 10 of 5,576 | REFUTED. The usage panel reads the run's bills, which carry the same kWh as the invoices. The ten are held bills |
| R4 | N6 breaches every fuel-year with Smart bills | 4 of 7, and 2 flagged with no estimate at all | REFUTED in part. It is one household, C2 |
| R5 | N7 breaches 10% to 40% | 292 of 24,886 (1.2%) | REFUTED: the estimator follows its reads far more often than I expected |
| R6 | the run row breaches 1% to 10% | 11 of 4,311 (0.3%) | REFUTED: 10 of the 11 are one cause, occupier zero windows |
| R7 | the 45 earlier rows unchanged | identical counts; `INV_OVERDUE_WITHIN_PAGE_BALANCE` still 12,730 | HOLDS. ec079776de is run-side, so a rebuilt ledger cannot show it |

I over-predicted R3, R5 and R6 the same way. I expected the record to be noisier than it is.
After the fixes and the six exceptions, the gate reads **0 unexcepted breaches, 12 excepted**.
Causes: `SEAT_FINDING_THE_SECOND_COLD_READS_ROWS_FIND_A_LATE_DIRECT_DEBIT_AN_UNSHOWN_PRICE_GUARANTEE_AND_ESTIMATES_TOO_CLOSE_TO_THE_MONTH_2026-10-28.md`.
