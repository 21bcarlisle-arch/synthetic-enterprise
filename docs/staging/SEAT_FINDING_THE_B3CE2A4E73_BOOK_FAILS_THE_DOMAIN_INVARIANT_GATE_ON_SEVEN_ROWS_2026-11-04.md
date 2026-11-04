**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The b3ce2a4e73 book would be refused by the domain-invariant gate: 203 unexcepted breaches on seven rows (2026-11-04)

**Source.** `/var/tmp/fresh-grade-b3ce2a4e73/grade.txt`, the whole suite over 1,291 accounts, `enforce: true`. Full table
and the departures from the 85b044be54 chain in
`docs/staging/records/SEAT_RECORD_THE_B3CE2A4E73_BOOK_GRADED_AGAINST_ITS_FIXES_PREDICTIONS_2026-11-04.md`.
It is BLOCKING because the publisher would refuse this book when the window opens and the ruling's exit test is this gate.

| Row | Breached | Exception ceiling | First examples |
|---|---:|---:|---|
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 128 | none | OCC-75d17c23c1da, 2022-07-16 to 2022-09-16: page prints 336.84 overdue against a balance of 273.62, on `arrangement_offered` and `repayment_plan_reoffer` steps |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 53 | 3 | OCC-00909e50a521 electricity 2020-02..06 (5 bills) ratio 0.235 against a band of 0.333-3.0; OCC-14d60fd5bb78, OCC-288aa561d534, OCC-2cf83688b2d2 |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 14 | 6 | PROS-2017-0233 electricity 2019 and 2020 (10 and 5 months billed on the carbon panel), PROS-2020-0167 2024 |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 5 | 1 | OCC-bad56e8f97f9 (revenue 2595.34 against 857.08 billed), PROS-2020-0025, OCC-8c6b8bb21743, SYN-2016-264, SYN-2016-604g |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 1 | none | SYN-2016-110 electricity 2018-11 |
| INV_PERIODS_CONTIGUOUS | 1 | none | SYN-2016-604g gas, 2017-06-30 -> 2017-08-01, 32 days |
| INV_OPENING_IS_THE_PREVIOUS_CLOSING | 1 | none | SYN-2016-604g gas register 1, 2017-08-01, opening 253.6 kWh above the previous close |

**What it is not.** The four rows the 85b044be54 grade refused on (E7 two registers, read monotonic, ToU bands sum, estimate
after actual) are 0, 0, 0 and 1. The three supplier fixes' predictions hold except the cap edge (separate finding).

**Attribution: I cannot yet say.** More than one thing changed between the two books. Two cautions for whoever draws this:
- The revenue row compares page revenue (here from `per_customer_lifetime`, a substitution for summing `p2b__all_records`
  that the pickle chain used) against page bills. Re-grade it from the pickles, or from the pages built in
  `/var/tmp/fresh-grade-b3ce2a4e73/tree`, before treating the five as the book's.
- `INV_OVERDUE_WITHIN_PAGE_BALANCE` was CLEAN on the 85b044be54 grade (0), so 128 is a new regression, not a first
  count. The five examples the runner keeps are all one account, OCC-75d17c23c1da, on `arrangement_offered` and
  `repayment_plan_reoffer` steps printing 336.84, 316.80, 352.72 overdue against balances of 273.62, 253.58, 289.50.
  N15 (6a3da3e48) changed exactly when a re-offer step exists, and the commit's test names no print-side row. Candidate,
  not attribution: the steps that now survive are the ones where the standing arrear exceeds the page's balance.
  Related and older: `SEAT_FINDING_THE_PAGE_PRINTS_MORE_OVERDUE_THAN_IT_SAYS_IS_OWED_ON_493_OF_752_HOUSEHOLDS_2026-10-28.md`.

**Prediction, filed before any trace:** the 53 estimated-run breaches concentrate on the accounts N14's second pass
re-billed (`rebill_catchups_off_direct_debit`, 63 on the 0a6391d186 book), because that pass rewrites the estimated runs
this row bounds; if fewer than half of the 53 are on re-billed accounts, the cause is elsewhere (candidates: the world
change moving true use under the estimates, or the draw). Two accounts, SYN-2016-604g's pair, are one gap in a gas
leg's periods in 2017 and look like a single defect.

**Reverse:** delete this file.
