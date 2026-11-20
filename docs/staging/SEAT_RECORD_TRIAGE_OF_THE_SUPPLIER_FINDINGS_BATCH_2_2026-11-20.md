**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Triage of the supplier-lane findings, batch 2 of about 5 (2026-11-20)

Claim `triage-the-supplier-money-findings-batch-2`, continuing
`docs/staging/SEAT_RECORD_TRIAGE_OF_THE_SUPPLIER_FINDINGS_BATCH_1_2026-11-20.md` with the same method.
A reading for Monday 23 Nov's balance review.

**Scope.** Lane B-E files at `docs/staging/` root on origin 3704365993: 76, of which 5 are batch 1's
parked rows. This batch is the next **20 oldest by filename date** (17 Oct to 23 Oct). **51 remain**
untriaged after it.

## Counts

| Disposition | Count | Findings (# below) |
|---|---:|---|
| **fixed** | 11 | 4, 5, 6, 7, 8, 9, 10, 11, 14, 19, 20 |
| **real** | 3 | 15, 17, 18 |
| **parked** | 2 | 12, 16 |
| **obsolete** | 4 | 1, 2, 3, 13 |

Fixed and obsolete (15) are archived to `docs/staging/done/` with a `**Disposition:**` line. Real
and parked (5) stay at root with a dated triage line under the header. Lane B-E files at root after
this batch: 61 (51 untriaged, 7 parked, 3 real).

**Batch 1's zero real did not repeat.** Three premises are still true and nothing blocks them. All
three are low rank: none moves a published figure today.

## How the premises were re-measured

As in batch 1: each file read on origin 3704365993 and its premise checked against the code, the
commits and the publisher's gate on the 18 Nov book (`docs/reports/domain_invariants.json`, run
6af7fd0bfd). Two read-only readers split the batch ten and ten. The seat re-read the three real calls
(#18's count re-read from `site/data/dashboard.json`: 193). Every commit id cited was checked as an
ancestor of origin/main with `git merge-base --is-ancestor`. The gate settled #5 (INV_OVERDUE_WITHIN_PAGE_BALANCE,
0 of 6,115) and #14 (INV_READ_DUTY_ANNUAL, 0 of 1,132). It has no row for renewal contribution, the
retention guard, the opex household count or post-departure leg billing, so the rest were settled
from code and commits.

## One disposition each

| # | Finding (docs/staging/) | Disposition | Evidence / reason |
|---|---|---|---|
| 1 | `SEAT_FINDING_B11_THE_SWITCH_HAZARD_KEYED_ON_MONTHS_ON_DEFAULT_RANKS_SWITCHERS_AT_ONE_CUT_OF_THREE_2026-10-17` | **obsolete** | Slice-11 record, questions answered: rescale stays fit_window; "every account opens fixed" refuted (43% open on the default); fresh-seed verdict with 9ca9727748 and M7 prereg 7036dcbd54. |
| 2 | `WORKER_FINDING_A_READ_INSTRUCTION_AT_THE_ELEVENTH_ESTIMATE_..._2026-10-17` | **obsolete** | Overtaken: wired 301ab175b3, on 026b3c650d, graded a0bbbf6ea8. Access rate stays a GAP on the knowledge page and D48. |
| 3 | `WORKER_FINDING_B11_THE_HAZARD_THAT_SEES_WHAT_A_SUPPLIER_HOLDS_..._2026-10-17` | **obsolete** | Slice-10 record; next steps done in slice 11 (forward_clv.py:1041); gradient question moved to PB4. |
| 4 | `WORKER_FINDING_THE_COMPANY_DECIDES_A_DUAL_HOUSEHOLD_PER_LEG_..._2026-10-18` | **fixed** | d96d33f3de (next_best_action.py:246,279), on in every standing policy since f6e23a5359. Residual below. |
| 5 | `SEAT_FINDING_A_LEAVER_NEVER_READ_BILLS_A_QUARTER_..._2026-10-19` | **fixed** | 6208ea6dd2 (C7 billed/true 0.236 to 1.003); 3e0f624a6f, 166ce2b5b5. INV_OVERDUE_WITHIN_PAGE_BALANCE CLEAN. |
| 6 | `SEAT_FINDING_THE_DECISION_PROBE_SEES_A_DUAL_HOUSEHOLD_ONLY_..._2026-10-19` | **fixed** | 608c0d0fa4 riding_leg_row (tools/decision_probe.py:309); prereg G1-G7 held. |
| 7 | `WORKER_FINDING_THE_SWITCH_KEYS_WHOLE_BOOK_GAIN_OVER_FLAT_..._2026-10-19` | **fixed** | Within-segment ranking (forward_clv.py:428); graded 27ca9dc7a2; stamp c52f831135. |
| 8 | `SEAT_FINDING_C34S_RENEWAL_MARGIN_IS_THE_ALL_IN_RATE_..._2026-10-20` | **fixed** | term_contribution at every decision site (renewal_advice_desk.py:114,141); c61d8b608c, ec7fd9942b; graded 42d4e8e3d5, b8c665948c. |
| 9 | `SEAT_FINDING_D48_THE_UNBILLED_ACCRUAL_IS_THE_ENERGY_THE_PRE_BILL_GATE_HELD_2026-10-20` | **fixed** | 75aff1401e; releases pre_bill_validation.py:417. K6 stays a GAP on D48's L3 park. |
| 10 | `SEAT_FINDING_THE_FLAT_SUPPLIER_REACHABILITY_LEG_IS_KEYED_TO_THE_CUT_2026-10-20` | **fixed** | abe7ce5336 on bf0997494b; leg kept by 94b281af7e. |
| 11 | `SEAT_FINDING_THE_MEDIAN_RENEWAL_READS_NEGATIVE_..._2026-10-20` | **fixed** | ec7fd9942b (renewal_advice_desk.py:100,136); K8 in next_best_action_and_cross_sell.md s6.1. Floor residual to B12, below. |
| 12 | `SEAT_FINDING_THE_RETENTION_GUARD_WEIGHS_THE_SPREAD_OVER_WHOLESALE_..._2026-10-20` | **parked** | Value defect fixed (c61d8b608c, ec7fd9942b). The engagement weighting is a queued arm (retention_weighs_engagement off) behind churn_roll, candidate A, M7 (81042a7c3c). C29. Revisit 2026-11-27 with batch 1 #1. |
| 13 | `SEAT_FINDING_B11_SIX_SEEDS_CAN_RESOLVE_THE_KEY_..._2026-10-21` | **obsolete** | Power analysis answered; GAP 1 done in records/SEAT_PREREG_B11_M7_..._2026-11-14.md, which cites it. |
| 14 | `SEAT_FINDING_THE_READ_INSTRUCTION_PERFORMS_21B4_FOR_NO_MONEY_..._2026-10-21` | **fixed** | Flip with the visit cost, 026b3c650d (read_duty_register.py:63; accounting_close.py:163). INV_READ_DUTY_ANNUAL 0 of 1,132. |
| 15 | `WORKER_FINDING_B8_SECOND_EXPERT_HOUR_..._MEASURED_UPLIFT_NOTHING_MEASURES_2026-10-21` | **real (low)** | Q6 (975c90319a) shows the holdout is right off at this scale, so the B8 row's "proven by measured uplift" (simplifications/B8 map_notes) cannot be met. Reword the row (B8). The same claim at THE_MODEL_ON_A_PAGE.md:244,379 is a director document: a proposal, not an edit. Knowledge gap: Q9. |
| 16 | `WORKER_FINDING_D48_THE_ESTIMATED_SHARE_IS_FLAT_..._2026-10-21` | **parked** | Exchange built off (a60376f887); bill side 397cc8df3c; flip pre-registered 8fdd23cad4, queued after retention-netting. D48. Gap: in-book install rate. Revisit 2026-12-04. |
| 17 | `WORKER_FINDING_THE_READ_INSTRUCTION_IS_ON_AND_CHARGES_469_VISITS_..._2026-10-21` | **real (low)** | Value arms grade on SETTLED_BASIS (tools/run_value_cycle_ab.py:1399), before cost to serve, so an arm-dependent account-6100 cost (the read visit) is invisible to them. D48 / value-cycle harness. Gap: access rate. |
| 18 | `SEAT_FINDING_THE_OPEX_LEDGER_COUNTS_165_HOUSEHOLDS_..._2026-10-22` | **real (low)** | Unchanged since b29c074822 (generate_dashboard_data.py:1309). Now 193 households against about 191 gas and 278 electricity accounts in 2025: the count still tracks gas legs, so GBP 316.54 per household is likely overstated. LATENT (no page renders it). Unminted (B2 opex ledger). The one-variable get_customer check can run today. |
| 19 | `WORKER_FINDING_A_DUAL_HOUSEHOLD_THAT_LEAVES_ON_ITS_ELECTRICITY_LEG_..._2026-10-22` | **fixed** | 2b81e1466d (run_phase2b.py:3011,3283,6549); tests off HEAD_RED_REGISTER. |
| 20 | `SEAT_FINDING_EXPLORES_CAST_FINDS_STANDARD_VARIABLE_BILLS_ABOVE_THE_CAP_..._2026-10-23` | **fixed** | 28398fcdda, 55eee3e723/06266f4f14, d14ff599e5; coverage_verdict(explore_cast.json) red [], accounted []. |

## The two checks batch 1 handed on

- **W3_3's map row was stale, and is corrected in this commit.** 3d75dfd74e graded the book on 19
  Nov (P1 median ratio 1.000 every year), but the row still read L0 and "PARKED ... unpark when
  that book is graded". It now reads L2 (target), self-certified in
  `docs/observability/gate_authorizations.jsonl` with its End-to-end clause. The deemed/flex
  writers' latent defect stays in wrong_triage. B12 is unblocked and is the next move there.
- **The director's 12 Oct DD4b ruling was NOT in `for_the_director`** (4 rows, none on it). It is
  raised now as `your-12-oct-ruling-build-the-world`. It recommends building DD4b on a stated
  amplitude range that starts at zero, and grading the plan's shock-avoidance at both ends, as his
  take-up ruling already does. Due 2026-12-04.

## Found on the way

- **C29's block_reason was false, and is corrected in this commit.** It said "HELD ON THE
  DIRECTOR" on row does-a-retention-discount-offered-to-a, which the seat withdrew on 10 Oct. The
  real hold is the machine queue.
- **Two cost floors disagree** (from #11): the competitive ceiling's floor (renewal_desk.py:187)
  omits capital, and term_cost_floor includes it, a gap of up to GBP 4.82/MWh. Routed to B12, with
  #11's owed attribution of the rate-minus-floor spread.
- **Per-leg renewal pricing on the value arm** (from #4; value_based_renewal.py:647 "a dual-fuel
  household reaches it twice"). Only on the value_arm experiment policy. No atom; it matters only if
  that arm goes on.
- **Stale rows, not edited here:** EP17's block_reason still waits on a 19 Oct publish; D48's
  `expert_hour.last` says the accrual is unbuilt (75aff1401e built it). Both are for the next map pass.
- **Possibly dead excuses:** `tests/tools/test_bill_correctness_addendum_defect4.py:179-195` holds four C7 rows
  excused until the book carries 6208ea6dd, which every current book does. Check the test's own
  reachability control (:474) before deleting.
- **`tools/generate_explore_cast.py:1596`** holds four ACCOUNTED_BY entries coverage_verdict reports spent
  (one names #20). Archiving #20 does not red it, but the entries are dead.

## Next

Batch 3: the next 20 oldest lane B-E files at root (from 22 Oct). Same method.
