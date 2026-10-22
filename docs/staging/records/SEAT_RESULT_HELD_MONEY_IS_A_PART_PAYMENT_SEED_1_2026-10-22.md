**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `W2_demand_negative_margin_part_payment`
**Knowledge:** debt-and-collections -- `docs/market_research/household_budget_w2_4.md`, "2026-10-22: held money is a part payment"

# Result, seed 1: money held toward a bill as a part payment. H1-H5 all hold

Pre-registration: `SEAT_PREREG_HELD_MONEY_IS_A_PART_PAYMENT_2026-10-22.md`.
- Both arms ran world-only to 2023-12-31 with default dice, in `/var/tmp/held-mut` (origin/main
  187c2a999 plus the switch). Each log's first line names the switch value and that worktree's module.
- The control's dump is **byte-identical** to `arm_demand.json` (the demand reading's seed-1 arm at
  df9792c57), so the base move changed nothing in the world.

## Depth (`depth.py`), mean months behind and £ per credit account in arrears at 31 December

| Year | Off: share% | On: share% | Off: mean £ | On: mean £ | Off: mean months | On: mean months |
|---|---|---|---|---|---|---|
| 2016 | 2.6 | 2.0 | 184 | 117 | 5.7 | 3.6 |
| 2017 | 6.5 | 6.1 | 169 | 111 | 5.6 | 3.6 |
| 2018 | 6.8 | 6.8 | 262 | 145 | 6.5 | 3.6 |
| 2019 | 8.2 | 8.2 | 306 | 183 | 6.8 | 4.2 |
| 2020 | 8.8 | 8.8 | 147 | 106 | 3.3 | 2.4 |
| 2021 | 9.9 | 9.4 | 170 | 114 | 3.6 | 2.5 |
| 2022 | 14.6 | 13.3 | 307 | 213 | 3.5 | 2.7 |
| 2023 | 17.5 | 17.4 | 580 | 366 | 4.3 | 2.7 |

## Engagement (`engaged.py`): paid anything in the trailing 3 months, accounts in arrears ≥ £100

| Year | Off | On |
|---|---|---|
| 2017 | 40% (n 15) | 100% (n 13) |
| 2018 | 31% (n 13) | 100% (n 13) |
| 2019 | 54% (n 13) | 100% (n 12) |
| 2020 | 90% (n 10) | 100% (n 10) |
| 2021 | 79% (n 14) | 100% (n 12) |
| 2022 | 94% (n 32) | 100% (n 27) |
| 2023 | 62% (n 45) | 91% (n 44) |

## Against the predictions

- **H1 holds.** Deficit account-years with no payment all year fall from **24 to 0**. No account goes
  12 months without a payment; the longest gap is 6 months.
- **H2 holds.** Engagement is 91-100% in every year, against 31-94% off. The DRS anchor is about 90%.
- **H3 holds.** Mean months behind is below the control in **all 8** years, and **2.7** at 2023-12-31
  (band 1.5-4.5).
- **H4 holds.** £366 at 2023-12-31 (band £250-600; control £580; Ofgem £1,303).
- **H5 holds.** Heads change by −1.3 to 0 points in every year.

## What it means

- More than half of the pounds the demand reading added at Q4 2023 (£214 of the £382 between £580 and the stock reading's
  £198) came from households paying nothing. That is not how a household in arrears behaves in the
  record.
- The 2019-to-2020 fall in depth shrinks (6.8 to 3.3 becomes 4.2 to 2.4), but it does not go away.
- The crisis still steps up in pounds (2021 £114, 2022 £213, 2023 £366).
- **The pounds gap to Ofgem widens, from about 2.2x to about 3.6x.** Under F11 that is the safe
  direction. The finding's open question, what holds world pounds below the record, is now asked of
  households that do pay.
