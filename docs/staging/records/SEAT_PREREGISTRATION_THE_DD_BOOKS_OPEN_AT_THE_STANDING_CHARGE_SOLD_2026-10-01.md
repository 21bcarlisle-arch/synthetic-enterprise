**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# Pre-registration: the DD books open at the standing charge sold

Claim `open-the-dd-books-at-the-standing-charge-sold`. Filed BEFORE the run, 2026-10-01.

## The change

`simulation/run_phase4c_on_phase2b._opening_dd_by_customer` passes
`simulation.experienced_bill_shock.sold_standing_charge` (the first settled month's standing charge
per day, ex-VAT) as `contracted_standing_charge_per_day_ex_vat`, beside the rate sold it already
passes. That is what the bill-shock caller has done since 7c872f2d0. Without records, nothing
changes and the cap fallback stays as it is.

## The measurement

One default world, both arms in one process (`/var/tmp/se-dd-books-sc-sold/measure.py`, built on
`/var/tmp/se-dd-books-rate-sold/measure.py`):
- **rate**: the rate sold only, with the standing charge left to the door's 53p inc-VAT 2024 fallback
- **rate+sc**: the rate and the standing charge sold

## Predictions

- **P0 placebo.** `n_opened` is the same in both arms (247 last run). The standing charge never
  turns an amount into None, because a None charge falls back.
- **P1 direction.** At least 80% of accounts open LOWER under rate+sc. The world's dated charges sit
  below 53p inc-VAT for most of 2016–2021, and 22p gas in 2016 is the item's own example.
- **P2 magnitude.** For pre-2019 gas, the median fall in the monthly opening is between £6 and £11.
  (53 − 22×1.05) p/day × 365/12 ≈ £9.
- **P3 sign flip exists.** At least one account opens HIGHER under rate+sc: 2022-or-later
  electricity, where the dated charge exceeds 53p.
- **P4 books.** The annual review's `increase_count` does not fall: lower openings mean more
  reviews go up. The balance book's `portfolio_final_held_credit_gbp` does not rise.
