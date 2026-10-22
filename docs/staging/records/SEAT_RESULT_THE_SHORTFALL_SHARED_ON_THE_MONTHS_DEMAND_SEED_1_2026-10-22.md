**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `W2_shortfall_shared_on_demand`
**Knowledge:** debt-and-collections -- `docs/market_research/household_budget_w2_4.md`, "2026-10-22: stock or demand"

# Result, seed 1: sharing the shortfall on the month's demand lifts the world's arrears depth about 2x, inside every band

Pre-registration: `SEAT_PREREG_THE_SHORTFALL_SHARED_ON_THE_MONTHS_DEMAND_2026-10-22.md` (filed before
launch). Two arms, world-only to 2023-12-31, default dice, at `df9792c573` plus the switch (landed as
`f9bbffbfd`). Grader `/var/tmp/leaver_trace/depth.py`, unchanged. **The re-run stock arm is
byte-identical to the 2026-10-21 `dump_2023.json`**, so the switch's off path is inert, and the
eleven intervening commits did not move this world.

| 31 Dec | in arrears, stock / demand | share %, stock / demand | mean £, stock / demand | mean months, stock / demand | median months, stock / demand |
|---|---|---|---|---|---|
| 2016 | 8 / 17 | 1.2 / 2.6 | 56 / 184 | 2.0 / 5.7 | 1.0 / 5.8 |
| 2017 | 27 / 37 | 4.7 / 6.5 | 54 / 169 | 1.6 / 5.6 | 1.0 / 1.6 |
| 2018 | 24 / 32 | 5.1 / 6.8 | 59 / 262 | 1.4 / 6.5 | 0.9 / 1.9 |
| 2019 | 28 / 33 | 6.9 / 8.2 | 74 / 306 | 1.9 / 6.8 | 1.9 / 2.1 |
| 2020 | 30 / 31 | 8.5 / 8.8 | 89 / 147 | 2.2 / 3.3 | 1.9 / 1.9 |
| 2021 | 32 / 35 | 9.1 / 9.9 | 92 / 170 | 2.2 / 3.6 | 1.8 / 2.0 |
| 2022 | 47 / 53 | 13.0 / 14.6 | 198 / 307 | 2.4 / 3.5 | 1.7 / 2.3 |
| 2023 | 51 / 67 | 13.4 / 17.5 | 198 / 580 | 1.6 / 4.3 | 1.3 / 1.9 |

**Against the pre-registration.**
- **D1, demand deeper in every year 2019-2023: HELD.** 6.8, 3.3, 3.6, 3.5, 4.3 against 1.9-2.4.
- **D2, 2023 depth 3-9 months, and no year above 9: HELD.** 4.3. The maximum is 6.8, in 2019. No overshoot.
- **D3, 2023 mean £400-1,300: HELD.** £580, against Ofgem's £1,303. Still about 2.2x short.
- **D4, heads up 0 to +5 points in each year: HELD.** +0.3 to +4.1. The 2023 rise is at the band's edge.
- **D5, the crisis steps up in pounds: HELD.** £170 at 2021, £307 at 2022, £580 at 2023.

**What the prediction did not name.**
1. **The median barely moves** (1.9 against 1.3 at 2023). The gain is in a tail, the budget's
   persistent deficit households, not in the typical account in arrears. The pool stays bimodal,
   as the 23:35 grade found: most of it is the per-bill draw's one parked bill.
2. **Depth falls from 6.8 (2019) to 3.3 (2020)**, where the record rises every year. I cannot yet
   say why. Two candidates: the deep pre-2020 debtors leaving or closing (which the leaver census can
   test), or their income move ending the spell. Per-account, not run-level: n is about 30.
3. Pounds are still about 2.2x short in 2023 and 3.3x short in 2017.

**Ruling.** Seed 1 supports the switch. Per the pre-registration, a second seed is owed before the
default moves, and it is queued (`longjob-shortfall-{stock,demand}-arm-s2`, same bands). One seed of
about 30 accounts per year cannot bound a paired difference of a few accounts in heads, but it can
bound one of 2x in depth.
