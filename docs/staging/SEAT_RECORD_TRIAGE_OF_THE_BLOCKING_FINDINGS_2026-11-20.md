# Triage of the ten BLOCKING findings (2026-11-20)

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

Plan item 2 of `docs/operations/WEEKLY_BALANCE_REVIEW_2026-11-16.md` §5, claim
`triage-the-ten-blocking-findings`. This is the reading for Monday 23 Nov's balance review.

## Counts

| Disposition | Count | Findings |
|---|---:|---|
| **fixed** | 7 | E7 two registers; PC2 unread month; b3ce2a4e73 gate; page overdue; second cold read's rows; leg one / SVT; nine customer-years |
| **real** | 2 | the printed-register finding's E2 (now LATENT, D48); the Expert Hour on the live doors (now LATENT, SITE1) |
| **parked** | 0 | |
| **obsolete** | 1 | the book value counts customers who left |

The 10 are the files whose first line reads `**Severity:** BLOCKING`. `background.finding_severity`
counted 8 BLOCKING this morning, not 10. The two it left out (leg one, nine customer-years) carry a
`**Discharged:**` line, so the classifier already read them as discharged. After this commit it
reads **0 BLOCKING**: 8 files are archived to `done/` and 2 are re-graded LATENT.

## How the premises were re-measured

Every file was read against what origin publishes. The main instrument is the publisher's own
gate on the **18 Nov book**: `docs/reports/domain_invariants.json`, run `6af7fd0bfd`, 1,306
accounts, committed in 43fa9534d9. It reads `enforce: true, refuse: false, unexcepted: []`, and
8 rows are excepted. Each row count below comes from that file, so readers can check it.

## One disposition each

| # | Finding (docs/staging/) | Premise re-measured on origin | Disposition |
|---|---|---|---|
| 1 | `SEAT_FINDING_AN_ECONOMY_7_METER_IS_BILLED_ON_ITS_TWO_REGISTERS_2026-10-30` | INV_E7_METER_BILLED_ON_TWO_REGISTERS **0 of 28,227** (was 1,638); INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER 0 of 461. N1 and N3 held | **fixed**: e400c589d8, 308a3f168e. Archived |
| 2 | `SEAT_FINDING_A_PC2_METERS_UNREAD_MONTH_IS_ESTIMATED_PER_REGISTER_2026-10-30` | P1 held: INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS **0 of 31,641**. P3 held: E7 row 0 | **fixed**: 32ddfa8ca2. The summer residual on heated homes is #5's E2 and is not this build's. Archived |
| 3 | `SEAT_FINDING_THE_B3CE2A4E73_BOOK_FAILS_THE_DOMAIN_INVARIANT_GATE_ON_SEVEN_ROWS_2026-11-04` | The premise was "the publisher would refuse this book". The 18 Nov book went through the gate with 0 unexcepted. All seven rows are CLEAN or within their ceiling: overdue-page 0/6,115, est-run 8 (excepted, ceiling 8), carbon panel 0/8,808, billed ex-VAT 0/1,306, follows-latest-actuals 0, periods contiguous 0/105,904, opening = previous closing 0/55,486 | **fixed**: by publish 43fa9534d9 (book 6af7fd0bfd). Archived |
| 4 | `SEAT_FINDING_THE_PAGE_PRINTS_MORE_OVERDUE_THAN_IT_SAYS_IS_OWED_ON_493_OF_752_HOUSEHOLDS_2026-10-28` | INV_OVERDUE_WITHIN_PAGE_BALANCE **0 of 6,115** (was 10,180 of 32,741); INV_OVERDUE_WITHIN_BALANCE 0 of 975 | **fixed**: the last causes were the level-DD dunning chain, d8264b525e, 8e73c52356, 78f82e4242, 189b32460e, 703edeb89b. Archived |
| 5 | `SEAT_FINDING_THE_PRINTED_REGISTER_FIX_EXPOSES_ESTIMATES_FROM_ONE_READ_AND_PRINTS_6436_OPENING_READS_NOBODY_TOOK_2026-10-28` | E1 and E3 built (opening = previous closing 0/55,486). E4 built (INV_TOU_BANDS_SUM_TO_THE_TOTAL 0/90). E5 traced. **E2 is open**: INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER is 8 of 4,428, excepted at its ceiling of 8. Of those, 7 are electrically heated homes estimated on the class-average shape, 3 to 5 times the meter in summer | **real**, rank 1, re-graded **LATENT**: the gate passes with it excepted under a named cause. Atom: `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`. Stays at root |
| 6 | `SEAT_FINDING_THE_SECOND_COLD_READS_ROWS_FIND_A_LATE_DIRECT_DEBIT_AN_UNSHOWN_PRICE_GUARANTEE_AND_ESTIMATES_TOO_CLOSE_TO_THE_MONTH_2026-10-28` | R1 payment record **0 of 1,132** (was 181). R2's EPG line is on the bill, and its print scatter is excepted at 319 under leg one's row. R5 smart-on-own-reads 0 of 20. Billed ex-VAT 0 of 1,306. No exception on the book names R3, R4 or R5 | **fixed**: the R1 world fix in this file's own 28 Oct entry, then the page and estimator commits that #3 and #5 trace. Archived |
| 7 | `SEAT_FINDING_LEG_ONE_GRADES_FOUR_OF_THE_FIVE_UNCHECKABLE_ROWS_AND_FINDS_SVT_PRICED_PER_ACCOUNT_BEFORE_THE_CAP_2026-10-30` | INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW **0 of 32,592** (was 1,068). INV_UNIT_RATE_EPG_HOUSEHOLD 319 of 3,197, excepted as print and volume scatter, with its retirement named | **fixed**: ed8684442b. It was already `Discharged:`. Archived |
| 8 | `WORKER_FINDING_NINE_CUSTOMER_YEARS_BILL_LESS_THAN_THEIR_GROSS_MARGIN_AT_ORIGIN_2026-10-14` | `tests/tools/test_bill_correctness_addendum_defect4.py` is **14 passed** on the committed 6af7fd0bfd ledger (`docs/state/billing_ledger.json.gz`): 0 inversions. The C7 rows lapse by construction (`EXCUSED_UNTIL_THE_BOOK_CARRIES`, 6208ea6dd2) | **fixed**: 650fdcdd7, e6785dce5, 6208ea6dd2. Archived |
| 9 | `WORKER_FINDING_THE_EXPERT_HOUR_ON_THE_LIVE_DOORS_FAILS_ON_A_NET_MARGIN_OF_UP_TO_55_PCT_AND_AN_ARREARS_COUNT_THAT_READS_EBSS_AS_DEBT_2026-11-11` | It was BLOCKING because two published figures were wrong. Both are fixed on the live feeds. `site/data/dashboard.json`'s `net_margin_pct` is null for every year, with its status. `site/data/company.json`'s `arrears.in_arrears` is **59 of 1,306** on Ofgem's 91-day definition (was 705). Still open: the reviewer's B2 (book size across four sources) and B3 (the publish status on every door), and the fresh blind Hour that SITE1's done-means asks for | **real**, rank 2, re-graded **LATENT**: the blocking half is fixed by 601929ce0b. Atom `SITE1_expert_doors`. Stays at root as SITE1's routing note |
| 10 | `WORKER_FINDING_THE_BOOK_VALUE_COUNTS_CUSTOMERS_WHO_HAVE_ALREADY_LEFT_2026-08-13` | The open item was "the featured household must prefer a supplied account, and a forward-value panel must state status". The page it named (`site/company/index.html`) no longer exists. No page renders `company.json`'s `household` block. Its `clv_gbp` is null. `DRILLDOWN_ID = "C1"` is still hardcoded, but it feeds no forward value on any page | **obsolete**: the surface it guarded is gone. Archived. If a household drill-down comes back, the rule here (prefer a supplied account, print status beside any forward value) is the spec |

## For each one still real: is there a knowledge gap behind it?

1. **E2, heated homes' summer estimates (D48). Yes, a named GAP.** The exception's `retired_by`
   is "the estimate following the home's own seasonal shape … whether a GB supplier does so is a
   GAP; knowledge page first". The page is
   `docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md`. Its line
   ~240 says it is still a GAP whether a supplier's billing estimate follows the settlement EAC.
   The related SPAR value is already with the director (2721453029), and D48 built the BSC blend
   behind a switch (617ec5faa9). This one is a practitioner question (K4), after the BSC/MRA
   search. Nothing here should be invented to close it.
2. **SITE1 remainder. No knowledge gap. It is site-lane work.** One insight sits under it,
   though. The full-cost margin was withheld because it reads 20–31% against a published 2–5%.
   That rests on the standing-charge seam (findings of 14 Oct and 9 Nov), which W3_3 holds paused.
   The margin cannot be published again until that seam is resolved. That is a modelling gap, not
   a missing source.

## Found on the way (LATENT, recorded here rather than as a new file)

`company/billing/ledger_store.resolve_ledger` prefers the plain `billing_ledger.json` whenever it
exists. That file is git-ignored, while `.gz` is the committed form. In this executor worktree a
stale plain ledger was left by an earlier turn's scratch run (`source_json: /var/tmp/w14/run.json`).
It shadowed the committed 18 Nov `.gz`, and `test_bill_correctness_addendum_defect4` went **red
on a mixed book**: 5 "inversions", including PROS-2017-0286. The same test on the `.gz` passes 14
of 14. On the shared tree the plain file is the current book, so origin is not red. The hazard is
still real: any worktree with a leftover plain ledger reads a different book from the one
committed. The fix is a one-leg check: refuse, by name, when both forms exist and their
`meta.source_json` differ. It is handed on, not built here.

## Next

The 92 supplier money findings (lanes B, C, D and E) are handed on in batches of about 20, the
same way: `triage-the-supplier-money-findings-batch-1`.
