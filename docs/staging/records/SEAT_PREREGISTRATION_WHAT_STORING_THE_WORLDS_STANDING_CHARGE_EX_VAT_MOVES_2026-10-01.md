**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# Pre-registration: what storing the world's standing charge ex-VAT moves

Claim `close-the-vat-basis-class-in-the-world`, item (1). Written before either arm ran.

## The change

`simulation/policy_costs._ELEC_SC_PENCE_PER_DAY_BY_YEAR` and `_GAS_SC_PENCE_PER_DAY_BY_YEAR` are
re-read from Ofgem's cap level model v1.31: the nil-consumption allowance on the direct-debit sheets,
which is ex-VAT, taking the regional median of each cap period and the day-weighted mean over each
calendar year. Two things move at once, and they are separable by arithmetic at the input, not in
the run. The **basis** is ÷1.05 on every row. The **level** is re-sourced: the pre-2022 rows were
unsourced "market averages", and the 2022 row was the Q4 figure applied to the whole year.

| year | elec old → new (p/day) | ratio | gas old → new | ratio |
|---|---|---|---|---|
| 2016 | 24 → 19.22 | 0.801 | 22 → 20.93 | 0.951 |
| 2019 | 27 → 22.13 | 0.820 | 25 → 25.14 | 1.006 |
| 2021 | 29 → 23.57 | 0.813 | 26 → 25.10 | 0.965 |
| 2022 | 46 → 40.22 | 0.874 | 28 → 25.97 | 0.928 |
| 2023 | 53 → 50.13 | 0.946 | 29 → 27.70 | 0.955 |
| 2024 | 61 → 57.11 | 0.936 | 31 → 28.57 | 0.922 |

For 2022 onward the pure basis share of each ratio is 0.952. The rest is level.

## The run

Two processes on the same base and with the same script (`/var/tmp/se-sc-exvat/measure.py`). They
run in sequence, not in parallel, because there are 239 OOM kills on this guest. The `old` arm puts
the previous tables back in place before anything is imported downstream.

## Predictions

- **P0, placebo.** `n_customers` is equal in both arms. Nothing upstream of settlement reads the
  standing charge.
- **P1, exact.** For each year and fuel, `sc_by_year_fuel` new ÷ old equals the table ratio above
  to 1e-3, as long as the population of account-days is unchanged. If churn moves, P1 is read
  only on years before the first divergence.
- **P2.** Total standing-charge revenue falls by 8–16%.
- **P3.** `margin_total` falls by between 0.75× and 1.25× of the standing-charge revenue fall.
  Standing-charge revenue goes into margin 1:1, and I predict that the feedback through renewal
  pricing (`value_based_renewal._observed_standing_charge_gbp`) is small.
- **P4.** All 8 of the 2023 electricity accounts that opened HIGHER than the 53p fallback in
  `SEAT_FINDING_THE_DD_BOOKS_NOW_OPEN_AT_THE_STANDING_CHARGE_SOLD...` now open lower, because
  50.13 × 1.05 = 52.64p, which is below 53p. The 20 accounts from 2024–25 stay higher, but by about
  £1.24/month less: (64.05 − 59.97)p × 30.4 days.
- **P5.** Every account's opening DD is lower than or equal to its `old` value.
