**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

# Pre-registration: the company's DD books opened at the rate each account was sold at

Claim `open-the-dd-books-at-the-rate-the-account-was-sold-at`. Filed 2026-10-01 BEFORE the change
meets a world. No figure below has been computed. Continues
`SEAT_PREREGISTRATION_PB4_THE_OPENING_DD_AT_THE_RATE_SOLD_2026-10-01.md`, which moved only the
bill-shock caller and handed this one on.

## The change (one variable)

`simulation/run_phase4c_on_phase2b._opening_dd_by_customer` takes the run's settlement book and
passes each account's `sold_unit_rate` (the consumption-weighted rate on its first settled month,
the same reader the experienced bill shock uses) to `opening_monthly_amount`. `main` hands it
`all_records`. The world cannot move: the caller runs after `run_phase2b` returns, and only the DD
review, the DD balance book and the level collection book read its output.

## The run

`/var/tmp/se-dd-books-rate-sold/measure.py`: one default world, then both arms over the SAME
customers, bills and records in one process: the cap arm (no records) and the rate-sold arm.

## Predictions

| | Prediction | Why |
|---|---|---|
| R0 | **Placebo: the DD population is identical across arms.** The balance book's `n_customers + unestimated` is equal in both. | Only the opening amount moves; who pays by DD does not. If this differs, something else changed. |
| R1 | Cap arm opens **0** pre-2019 accounts; the rate-sold arm opens **≥ 90%** of pre-2019 accounts that have bills. | No cap before January 2019; every billed account has a first settled month with a rate (31/31 in the PB4 run). |
| R2 | The balance book's unestimated count falls to **≤ 5%** of its DD population in the rate-sold arm. | Same reason; the residue is accounts with no rate in their first month. |
| R3 | On accounts opened in both arms, the median sold/cap ratio is **< 1**, and **≥ 75%** sit below 1. | The renewal desk ceilings a resi fixed strike at the cap. All 4 cap quotes measured in PB4 were over-set. |

Aggregate held credit is not predicted. Accounts opened lower hold less credit, but the pre-2019
accounts that come into the book add credit. I cannot say which effect is larger.

## What would refute the plan

If R0 fails, the comparison is discarded. If R3 fails (median ≥ 1), the sold rate sits above the cap
for most post-2019 accounts. That contradicts the desk's ceiling, and the ceiling gets investigated
before this lands.
