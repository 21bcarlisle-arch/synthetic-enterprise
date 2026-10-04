**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# The DD books now open at the rate sold, and 28 accounts were sold above the cap the door reads

Claim `open-the-dd-books-at-the-rate-the-account-was-sold-at`. This records the results against
`docs/staging/records/SEAT_PREREGISTRATION_THE_DD_BOOKS_OPEN_AT_THE_RATE_SOLD_2026-10-01.md`,
which was filed before the run.

## What changed

`simulation/run_phase4c_on_phase2b._opening_dd_by_customer` now takes the run's settlement book.
For each account it passes `sold_unit_rate`, the consumption-weighted rate on the account's first
settled month, as `contracted_unit_rate_per_mwh_ex_vat`. `main` hands it `all_records`. Accounts
with no rate in their first month still fall back to the cap. Controls are in
`tests/simulation/test_the_dd_books_open_at_the_rate_sold.py`, and three mutations bite: rate
never passed, `main` passing no records, and a missing rate becoming 0.

## Results (one default world, both arms in one process, `/var/tmp/se-dd-books-rate-sold/out.json`)

| | Predicted | Measured | Verdict |
|---|---|---|---|
| R0 placebo | balance-book DD population equal | cap 95 + 99 unestimated = 194; sold 194 + 0 = 194 | **holds** |
| R1 | cap opens 0 pre-2019; sold opens ≥ 90% of billed pre-2019 | cap 0; sold 127. The cap arm's review left exactly 127 unestimated. The pre-2019 denominator was not counted directly | **holds** (denominator inferred, not counted) |
| R2 | unestimated ≤ 5% of the DD population | 0 / 194 | **holds** |
| R3 | median sold/cap < 1, and ≥ 75% below 1 | median 0.869; 89 / 120 = **74.2%** below 1 | **median holds; share REFUTED** |

Other effects (not predicted):
- The annual review grows from 265 to 770 reviews, with unestimated accounts falling from 127 to 0.
- The balance book's portfolio final held credit falls from £3,823 to £2,310. Its peak month moves
  from 2025-06 to 2017-06, because the pre-2019 book is now in it.

## The refutation: 28 accounts sit 1–4% ABOVE the cap

The sold/cap ratios split three ways:

- 89 sit below 1 (quartiles 0.80 and 0.87).
- 4 sit at 1.000.
- 28 sit at 1.014–1.040, tightly clustered at 1.03–1.04.

A fixed strike ceilinged at the cap cannot produce that. A tight band a few percent above the cap
looks like a basis gap between two "caps". One candidate is the world charging the default-tariff
rate for a different payment method or region than the cap the opening door resolves. Another is a
first month that straddles a cap change. **I cannot yet say which.** Before testing it: for those
28, compare the world's first-month rate with the door's cap for the same date, region and payment
method.

This does not undo the landing. The pre-registration blocked landing only on median ≥ 1. The
accounts above the cap now open 1–4% higher than before, and they open at the rate they were
actually charged.

## Downstream, now out of step: `tools/dd_opening_arms.py`

`estimate_opening_by_customer` describes itself as "the LIVE rule, measured through the live call
site". It calls `_opening_dd_by_customer(customers)` with no records, so it now measures the
**cap fallback**, not production. Its substrate is `docs/reports/run_output_latest.json`, which
carries bills and no settlement records, so it cannot pass what the live call needs. Rebuilding the
rate from `average_unit_rate_gbp_per_mwh` on the first bill would be a second implementation of the
arm, which its own docstring warns against. The published `site/data/dd_opening_arms.json` is
therefore a cap-arm comparison. Next steps: have the run output carry the per-account opening
amounts the run actually used, or the sold rate itself, and have the instrument read those.
Handed on as a continuation.

## Downstream, also out of step: the standing charge sold

7c872f2d0 landed while this was being gated. It gave `opening_monthly_amount` a
`contracted_standing_charge_per_day_ex_vat` and deliberately left this caller on the 53p 2024
fallback. So the DD books and the experienced bill shock now agree on the rate sold and **not** on
the standing charge. The docstring now says so. Passing `sold_standing_charge` here is the next
one-variable step. It was not folded into this landing, because it is a second variable this run
did not measure. Handed on as a continuation.
