**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** unbilled-energy-and-revenue-assurance

# D48's Expert Hour fails, and the level stays at L2. The measure is honest; the row claims an accrual and a settlement reconciliation it does not do, and the estimated share barely moves through the smart roll-out (2026-10-14)

**Fate (2026-10-14):** ATOM -- D48 stays at L2, harden. The two row-claim MAJORs are fixed in this commit (title: the accrual is a GAP; twin: reads, not settled kWh). The measure findings are the next harden work.

*Worker tick, 2026-10-14. This was run from the brief `SEAT_BRIEF_D48_EXPERT_HOUR_A_REVENUE_ASSURANCE_LEAD_JUDGES_BILLED_AGAINST_USED_2026-10-14.md` (now in done/).*

**How it was run.**
- The reviewer was a fresh Opus instance with no tools. It was shown only the `tools/blind_review.py` packet (domain billing, the revenue-assurance persona, and the brief's §2 restatement recorded as `restated`).
- Its priors, its first doubt and an 18-entry battery were recorded with `--record` at 2026-10-14T11:42:25Z, before any figure was shown. This is in `docs/observability/blind_review_ledger.jsonl` with `independence: false`, and `--audit` passes 11 of 11.
- After that, the reviewer was shown the live figures from `site/data/billing_accuracy.json` (run_output_2248e3baf_20261013T134447Z).
- **Its verdict: no sign-off.** Restricted context gives blindness, not independence: the reviewer is the same model family as the builder.

**Its priors** (for example, an estimated share of 35-45% falling to 10-20% across the smart roll-out, and a barred share of about 0.1-0.5% of revenue) are in the ledger record.

**Its first doubt:** it is called billed-against-used, but nothing is reconciled against settlement.

## Adjudication against the code, not the description

| # | The reviewer's MAJOR | Verdict | Evidence |
|---|---|---|---|
| 1 | There is no settlement leg | **CONFIRMED, live in the claim** | The row's `real_world_twin` is "reconciling billed kWh against settled kWh". The knowledge note's K6 (settled ≠ billed) is listed, and the module's docstring says "K4-K7 cannot arise in the run yet". Filed: `SEAT_FINDING_D48_THE_ROW_CLAIMS_A_SETTLEMENT_RECONCILIATION_AND_NO_SETTLED_KWH_IS_READ_2026-10-14.md` |
| 2 | The month-end accrual is missing | **CONFIRMED, live in the claim** | The row title ends "...and the accrual". The module's docstring says "True unbilled revenue (used and not yet billed) is still not computed". K1 is estimated energy already billed and not yet trued up; it is a different quantity. Filed: `SEAT_FINDING_D48_THE_ROW_TITLE_CLAIMS_THE_ACCRUAL_AND_THE_MODULE_SAYS_IT_IS_NOT_COMPUTED_2026-10-14.md` |
| 3 | Barred kWh and barred £ disagree about 60x | REFUTED | The two cover different populations by design: K3 is pay-on-bill energy, and the direct-debit (DD) money line is DD balance money (`test_the_dd_money_line_is_never_folded_into_k3`). The page says so in its first DD sentence. |
| 4 | 36.3% barred is implausible, because 21BA does not reach DD shortfalls | **Rule REFUTED, magnitude PLAUSIBLE** | "A direct debit statement is not a charge" (Ombudsman, `back_billing_and_liability.md` §44). The 36% follows from `seek_balance_at_review: false`, which asks for the balance only at the final bill. Whether a real supplier lets a shortfall age out is open. Filed: `SEAT_FINDING_D48_A_THIRD_OF_DD_ACCOUNTS_ASKED_FOR_THEIR_BALANCE_LOSE_PART_OF_IT_BECAUSE_THE_REVIEW_NEVER_ASKS_2026-10-14.md` |
| 5 | The 66% estimated share has no year split and sits far above priors | **CONFIRMED by measurement** | Split by year from the run's own bills: electricity is 68-70% from 2016 to 2022, then 59-61% for 2024-25; gas is 72% → 59%. The share hardly falls through the smart roll-out. Filed: `SEAT_FINDING_D48_THE_ESTIMATED_SHARE_FALLS_ONLY_TEN_POINTS_THROUGH_THE_SMART_ROLL_OUT_2026-10-14.md` |
| 6 | Electricity December cohorts run +8 to +11% net (2016-19), then step at 2020 | PLAUSIBLE | Not measured this turn. Electricity's net true-up for calendar 2020 is +34,823 kWh, which is consistent with lockdown use. The persistent winter under-bill before 2020 is the open part. Filed: `SEAT_FINDING_D48_ELECTRICITY_DECEMBER_ESTIMATES_UNDER_BILL_BY_A_TENTH_IN_EVERY_PRE_2020_YEAR_2026-10-14.md` |
| 7 | The sign convention is not stated | REFUTED | The page note says: "A positive net correction is an undercharge." |

| Minor | Verdict | Evidence |
|---|---|---|
| The "£80 an account" mean is over all 422 accounts, not the 153 barred | **CONFIRMED** | 33,770 / 422 = £80.0. Filed: `SEAT_FINDING_D48_THE_DD_MEAN_BARRED_READS_PER_BARRED_ACCOUNT_AND_IS_OVER_EVERY_ACCOUNT_ASKED_2026-10-14.md` |
| The median is uncited | REFUTED | The page reads "Ofgem 2018, citing Citizens Advice, 2017". |
| The 2024 cohort is graded on survivors | REFUTED as hidden | The "Runs never read" column sits beside it. |
| A "May 2019 for gas" start for the barred share was expected | REFUTED (the reviewer's prior was wrong) | `back_billing.py`: domestic from 2018-05-01 for both fuels, sourced. Measured: no electricity kWh barred before 2019, and gas's first barred kWh is in 2018. |
| Prepayment is mixed in | REFUTED | The world has no prepayment channel. This is a known, named gap. |

**Verdict: FAIL. D48 is held at L2.** Two MAJORs are confirmed and live (#1, #2). Both are claim-over-build, and either fix closes them: narrow the title and twin to what is measured, or build the leg. #5 is a fidelity finding about the world's reads, not this module. None is fixed in this turn, as the brief asked.
