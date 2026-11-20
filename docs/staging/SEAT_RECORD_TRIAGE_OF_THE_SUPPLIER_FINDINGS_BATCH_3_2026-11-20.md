**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Triage of the supplier-lane findings, batch 3 (2026-11-20)

Claim `triage-the-supplier-money-findings-batch-3`. This batch continues
`docs/staging/SEAT_RECORD_TRIAGE_OF_THE_SUPPLIER_FINDINGS_BATCH_2_2026-11-20.md` and uses the same method. It is a reading for
Monday 23 Nov's balance review.

**Scope.** On origin f2c4806c88 there are 64 lane B-E files at the `docs/staging/` root, and 54
carry no `Triage, 20 Nov 2026` line. One of those 54 had in fact been triaged already, in
`SEAT_RECORD_TRIAGE_OF_THE_BLOCKING_FINDINGS_2026-11-20.md` #5 (the printed-register fix, real
rank 1), under a differently worded line, so it was skipped. This batch takes the next **20 oldest
from 22 Oct by filename date** (23 Oct to 29 Oct). **33 remain** untriaged.

**Three strays from batch 1's census.** Of the 33, the three oldest are dated 3 Oct and 7 Oct:
B8's per-method slopes note, C32's expert hour, and the DD-opening cohort split. Their first line
is a title, not a `**Lane:**` header, so batch 1's 91-file census missed them. Batch 4 should take
them first.

## Counts

| Disposition | Count | Findings (# below) |
|---|---:|---|
| **fixed** | 9 | 1, 2, 7, 9, 10, 11, 14, 15, 20 |
| **real** | 8 | 4, 5, 6, 8, 12, 13, 16, 17 |
| **parked** | 1 | 3 |
| **obsolete** | 2 | 18, 19 |

Fixed and obsolete files (11) are archived to `docs/staging/done/` with a `**Disposition:**` line.
Real and parked files (9) stay at the root with a dated triage line under the header. After this
batch the root holds 53 lane B-E files: 33 untriaged, and 20 carrying a triage line (9 from this
batch, 10 from batches 1-2, and the one blocking-ten item).

**Real rose from 3 to 8.** These are later findings (26-27 Oct), from the cold reads and the
billing gates, and most are residuals of files that were mostly fixed. Only #6 is ranked high, and
it is already being worked.

## How the premises were re-measured

Each file was read on origin f2c4806c88. Its premise was checked against the code, the commits and
the publisher's gate on the 18 Nov book (`docs/reports/domain_invariants.json`, run 6af7fd0bfd).
One reader also re-ran the bill validator's `compare_account` over the committed ledger (53,605
invoices) to get live AGREED/DISAGREED counts for #11, #13 and #15. Two read-only readers took ten
files each. The seat triaged #19 itself, and re-read #5 (`run_phase2b.py:5205`) and #6
(`site/data/value_arms.json`, generated 18 Nov). Every commit id was checked as an ancestor of
origin/main.

## One disposition each

| # | Finding (docs/staging/) | Disposition | Evidence / reason |
|---|---|---|---|
| 1 | `SEAT_FINDING_SVT_BILLS_ABOVE_THE_CAP_ARE_TWO_DEFECTS_..._2026-10-23` | **fixed** | 4bc21e9209, 4ef70aba92, 1e358809be, 1ee7ec58d0. INV_UNIT_RATE_SVT_* all read CLEAN. EPG_HOUSEHOLD has 319 breaches, all excepted and about 0.01p over the bound, so they are rounding, not this defect. |
| 2 | `SEAT_FINDING_A_DUAL_FUEL_HOUSEHOLD_IS_TWO_ACCOUNTS_IN_COLLECTIONS_2026-10-25` | **fixed** | c5a3e96fee keys the ledger to the household, and b7b17b8bf3 fixes the departure leg. Both xfails are gone. SLC 27.8D's cross-fuel offset moved to N29. |
| 3 | `SEAT_FINDING_SIX_VAT_READERS_STILL_ASK_NO_DATE_..._2026-10-25` | **parked** | Still true, and there are now nine undated readers plus the gate's own (`domain_invariants.py:1325`). Nothing can reach them until a run passes Oct 2026, which waits on EP16. The code could be fixed early. Revisit 2026-12-18. |
| 4 | `SEAT_FINDING_TWO_SMART_METER_SERIES_AND_A_DISPUTED_R2_DATE_2026-10-25` | **real (low)** | Two smart-meter series are still live: `saas/smart_meter_rollout.py` gates ToU, beside the world's DESNZ series. Whether R2 is 4 or 5 months is still open. The exit_fee item is obsolete. Atom EP5. |
| 5 | `SEAT_FINDING_A_DUAL_HOUSEHOLDS_TWO_FUELS_ANSWER_THEIR_ANNIVERSARY_OFFERS_APART_2026-10-26` | **real (med)** | The riding leg still answers its own fix offer. B13 is closed at L2 with this defect open in its own comment. |
| 6 | `SEAT_FINDING_THE_VALUE_TESTS_PUBLISHED_DRAWS_FALL_OUTSIDE_..._2026-10-26` | **real (high)** | The 18 Nov page still publishes draws outside their own re-draws, marked provisional. This is being worked under THE_VALUE_TEST_REDESIGN (s.12f), and the finding is its acceptance check. |
| 7 | `SEAT_FINDING_A_STATUTE_BARRED_WRITE_OFF_LANDS_BEFORE_SIX_YEARS_..._2026-10-26` | **fixed** (code) | `collections_journey.py:365`; 2b70102f9e, 80a9b51794. The invariant is UNREACHED (see below). |
| 8 | `SEAT_FINDING_EXPLORES_SLOTS_PICKED_THE_EXTREME_..._2026-10-26` | **real (low)** | The core is fixed: all 8 slots are filled with valid households. What remains is that the household count reads 766 on Explore and 764 on the home page, with no definition stated. |
| 9 | `SEAT_FINDING_THE_2022_SHOCK_EXAMPLE_COMPARED_A_REPEATED_ESTIMATE_..._2026-10-26` | **fixed** | The shock slot now needs actual reads on both bills, and there is a p1-p99 use band. INV_ANNUAL_USE_* rows are CLEAN or have 0 breaches. |
| 10 | `SEAT_FINDING_THE_DEFAULT_TARIFF_TERM_RATE_AGAINST_ITS_WHOLESALE_FLOOR_2026-10-26` | **fixed** | Superseded by #15. faf7b1a7e4: 27,197 of 27,197 periods clear the floor. |
| 11 | `SEAT_FINDING_THE_DEFAULT_TARIFF_TERM_RATE_AGAINST_THE_PUBLISHED_CAP_2026-10-26` | **fixed** | Within the cap: 27,549 AGREED, 0 DISAGREED. 24963ecd07. |
| 12 | `SEAT_FINDING_THE_MONDAY_RUN_4AE8DA9B0F_IS_REFUSED_BY_TWO_BILLING_GATES_..._2026-10-26` | **real (low)** | Both reds are closed. Its own "still owed" stands: nothing in `saas/` reads `cos_read_settlement_gbp`. D48, and not behind the exchange flip. |
| 13 | `SEAT_FINDING_THE_PRINTED_RATE_AGAINST_THE_CONTRACTED_TARIFF_2026-10-26` | **real (low)** | VAT pennies: 3,020 of 53,605 DISAGREED. Which rounding convention a real bill uses is a knowledge gap. ToU-ness is not on `account_state_log`. D46. See below for the open post-publish red. |
| 14 | `SEAT_FINDING_THE_COMPANYS_OWN_EVENTS_SHOW_NO_RENEWAL_NOTICE_..._2026-10-27` | **fixed** | INV_RENEWAL_NOTICE_42_TO_49_DAYS reads 0 of 1,305 and INV_OVERDUE_WITHIN_BALANCE reads 0 of 975. 25a8be909b. |
| 15 | `SEAT_FINDING_THE_DEFAULT_TARIFF_FLOOR_NOW_COVERS_GAS_AND_NETWORK_AND_POLICY_2026-10-27` | **fixed** | 26,417 AGREED, 0 DISAGREED. The 1,132 UNCHECKABLE are the multi-register floor gap the finding itself names. |
| 16 | `SEAT_FINDING_THE_EIGHT_COLD_READ_ROWS_LEAVE_SIX_UNGRADEABLE_..._2026-10-27` | **real (low)** | Only the export field is left: INV_EBSS_CREDIT_EACH_MONTH and INV_EBSS_CREDIT_ON_THE_BILL read 5 each, all void or deemed months. The raw export carries no void or occupier window. D48. |
| 17 | `SEAT_FINDING_THE_FIRST_COLD_READ_FINDS_PAGE_ARITHMETIC_..._2026-10-27` | **real (med)** | Mostly fixed. Still open: O8 (move rate), O30 (ALP), O4, the copy items, per-leg cost to serve (B13), and the credit-netting accounts (INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO reads 74). Split it into world items and a copy pass. |
| 18 | `SEAT_FINDING_THE_DESK_DUNS_BILLS_THE_LEDGER_HELD_FOR_REVIEW_..._2026-10-28` | **obsolete** | Item 1 is fixed (ec079776de). Item 2 was overtaken by 209c3350ab. One knowledge gap is kept: does limitation run per fuel contract or per household? |
| 19 | `SEAT_FINDING_PROS_2025_0106_CLOSING_BILL_BILLS_THE_HELD_ENERGY_..._2026-10-29` | **obsolete** | A correction record. Its refutation stands, and its carbon-panel question is fixed (914828793b). |
| 20 | `SEAT_FINDING_HELD_ESTIMATES_ON_THREE_ELECTRIC_HOMES_..._2026-10-29` | **fixed** | 54f76662d1 (graded 0 of 9, 55623bfcf5). The exception queue is empty. INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL reads 0 of 8,808. |

## Batch 2's stale rows, corrected in this commit

- **EP17 `block_reason`** waited on the 2026-10-19 publish, which is long spent. Seeds 61101-61118
  are authorised (`varied_population_draw_activation.json`) and in use under the seed-family runner
  (212aad383e, 7036dcbd54). The row now says so. Its `level_current: 0` has not been graded since
  and is left for the next map pass rather than moved here.
- **D48 `expert_hour.last`** said the accrual was not built. 75aff1401e built it, and 126d340121
  reworded the twin. The row now records both answers. It still needs a blind re-run after the
  exchange flip.

## Found on the way

- **The open post-publish red is already fixed on origin.**
  `test_the_published_book_charges_its_contracted_tariff` on 6af7fd0bf is 3 DISAGREED: SVT stubs
  after a ToU term (PROS-2016-0253, PROS-2017-0286, PROS-2021-0313) that are missing their Day/Night
  pair. c6695cd8db fixed `_tou_terms`. The red holds only until the next republish regenerates the
  ledger, so no further work is owed.
- **A guard that cannot fire:** INV_STATUTE_BARRED_WRITE_OFF_AGE is UNREACHED (0 checked) and its
  exception has been retired. `arrears_engine.py:1386`'s limitation branch never runs on the book.
  It needs a planted case before #7 counts as proven.
- **B13 is closed with a known defect open** (#5, and #17's per-leg cost to serve). This is a G9-free
  map correction for the next pass: reopen it, or mint the residual.
- **Stale invariant text:** INV_UNIT_RATE_FIXED (`DOMAIN_INVARIANTS.yaml:1104`) still says the commons
  has no gas allowance, but #15 established that it has one.
- **A stale report:** `docs/reports/bill_validation_comparison.json` (3 Sep) shows 295 VAT
  differences, and the docstring of `tools/bill_validation_comparison.py` says the same. The live
  count is 3,020.
- **#3 includes the gate:** `domain_invariants.py:1325` reads VAT undated too, so INV_VAT_RATE would
  pass a 5% bill in a forward window where the dated law says 0%.
- **`read_true_up_billed_kwh`** counts the estimates billed earlier in the run, not the energy the
  true-up billed (#19). `billing_accuracy.py:846` divides by it, so a held run puts all its metered
  kWh in the numerator against 0 in the denominator. Before anyone cites
  `graded_net_true_up_share`, someone should state what it counts.
- **D48's L3 park does not cover #12's or #16's residuals.** Neither waits on the exchange
  flip.

## Next

Batch 4: the three strays (3 and 7 Oct) and then the next oldest from 29 Oct, 33 in all. Same
method.
