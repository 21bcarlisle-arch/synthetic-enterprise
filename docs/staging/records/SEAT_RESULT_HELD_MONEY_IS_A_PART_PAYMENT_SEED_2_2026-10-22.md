**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `W2_demand_negative_margin_part_payment`
**Knowledge:** debt-and-collections -- `docs/market_research/household_budget_w2_4.md`, "2026-10-22: held money is a part payment"

# Result, seed 2: money held toward a bill as a part payment. H1-H5 all hold again

Pre-registration: `SEAT_PREREG_HELD_MONEY_IS_A_PART_PAYMENT_2026-10-22.md`, "Seed 2, pre-registered
before launch". Both arms ran on dice seed 2 in `/var/tmp/held-mut` (`dice 2 draws` 46,933 off and
46,777 on). The control's dump is **byte-identical** to `arm_demand_s2.json`.

## Depth (`depth.py`)

| Year | Off: share% | On: share% | Off: mean £ | On: mean £ | Off: mean months | On: mean months |
|---|---|---|---|---|---|---|
| 2016 | 2.5 | 1.9 | 195 | 126 | 6.0 | 3.8 |
| 2017 | 6.1 | 5.8 | 166 | 105 | 5.5 | 3.3 |
| 2018 | 8.9 | 8.9 | 221 | 132 | 5.4 | 3.2 |
| 2019 | 9.4 | 9.5 | 277 | 170 | 6.0 | 3.7 |
| 2020 | 9.1 | 9.1 | 123 | 84 | 2.8 | 2.0 |
| 2021 | 11.3 | 10.5 | 141 | 88 | 2.9 | 1.9 |
| 2022 | 13.0 | 11.1 | 348 | 244 | 3.8 | 2.9 |
| 2023 | 14.2 | 13.5 | 710 | 452 | 5.1 | 3.2 |

## Engagement (`engaged.py`): paid anything in the trailing 3 months, accounts in arrears ≥ £100

| Year | Off | On |
|---|---|---|
| 2017 | 25% (n 12) | 100% (n 10) |
| 2018 | 36% (n 14) | 100% (n 14) |
| 2019 | 57% (n 14) | 100% (n 13) |
| 2020 | 67% (n 6) | 83% (n 6) |
| 2021 | 82% (n 11) | 100% (n 8) |
| 2022 | 94% (n 33) | 100% (n 26) |
| 2023 | 60% (n 43) | 90% (n 40) |

## Against the predictions

- **H1 holds.** Deficit account-years with no payment all year fall from **26 to 0**. No account goes 12
  months without a payment (off: 22 accounts, 5 of them past 24 months).
- **H2 holds.** Engagement is 90-100% in every year with n ≥ 10. The DRS anchor is about 90%.
- **H3 holds.** Mean months behind is below the control in all 8 years, and **3.2** at 2023-12-31.
- **H4 holds.** £452 at 2023-12-31 (control £710; Ofgem £1,303).
- **H5 holds.** Heads change by −1.9 to +0.1 points.

Both seeds have held, which meets the pre-registered condition. `HELD_MONEY_IS_A_PART_PAYMENT` defaults
on in its own commit. Across the two seeds, pounds at Q4 2023 are £366-452 against the record's £1,303,
about 3x short.
