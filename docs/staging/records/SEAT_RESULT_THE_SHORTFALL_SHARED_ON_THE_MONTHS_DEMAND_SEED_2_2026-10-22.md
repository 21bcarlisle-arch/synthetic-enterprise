**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `W2_shortfall_demand_seed2_grade`
**Knowledge:** debt-and-collections -- `docs/market_research/household_budget_w2_4.md`, "2026-10-22: stock or demand"

# Result, seed 2: the demand reading's depth gain holds on re-drawn payment dice, inside every band

Pre-registration: `SEAT_PREREG_THE_SHORTFALL_SHARED_ON_THE_MONTHS_DEMAND_2026-10-22.md`, section "Seed 2,
pre-registered before launch" (D1-D5 unchanged). Seed 1: `SEAT_RESULT_THE_SHORTFALL_SHARED_ON_THE_MONTHS_DEMAND_SEED_1_2026-10-22.md`.
Two arms, world-only to 2023-12-31, at `df9792c573` plus the switch, worktree `/var/tmp/demand-mut`,
`dump_arm.py ARM 2023-12-31 OUT 2` (units `longjob-shortfall-{stock,demand}-arm-s2`, launched 00:56
BST, finished 01:33). The seed reached the draws: 46,777 payment draws on the stock arm, 46,933 on
the demand arm. Grader `/var/tmp/leaver_trace/depth.py`, unchanged.

| 31 Dec | in arrears, stock / demand | share %, stock / demand | mean £, stock / demand | mean months, stock / demand | median months, stock / demand |
|---|---|---|---|---|---|
| 2016 | 7 / 16 | 1.1 / 2.5 | 64 / 195 | 2.1 / 6.0 | 0.9 / 6.3 |
| 2017 | 25 / 35 | 4.4 / 6.1 | 42 / 166 | 1.1 / 5.5 | 1.0 / 1.2 |
| 2018 | 34 / 42 | 7.2 / 8.9 | 69 / 221 | 1.6 / 5.4 | 1.0 / 1.2 |
| 2019 | 33 / 38 | 8.2 / 9.4 | 77 / 277 | 1.7 / 6.0 | 1.1 / 1.5 |
| 2020 | 31 / 32 | 8.8 / 9.1 | 67 / 123 | 1.7 / 2.8 | 1.1 / 1.2 |
| 2021 | 36 / 40 | 10.2 / 11.3 | 68 / 141 | 1.6 / 2.9 | 1.1 / 1.1 |
| 2022 | 39 / 47 | 10.9 / 13.0 | 227 / 348 | 2.6 / 3.8 | 2.1 / 2.6 |
| 2023 | 38 / 54 | 10.1 / 14.2 | 250 / 710 | 1.7 / 5.1 | 1.2 / 2.5 |

**Against the pre-registration.**
- **D1, demand deeper in every year 2019-2023: HELD.** 6.0, 2.8, 2.9, 3.8, 5.1 against 1.6-2.6.
- **D2, 2023 depth 3-9 months, no year above 9: HELD.** 5.1 (seed 1: 4.3). Maximum 6.0, in 2016 and 2019.
- **D3, 2023 mean £400-1,300: HELD.** £710 (seed 1: £580), against Ofgem's £1,303. Still about 1.8x short.
- **D4, heads up 0 to +5 points in each year: HELD.** +0.3 to +4.1. As on seed 1, the 2023 rise
  (+4.1) is the year nearest the band's edge.
- **D5, the crisis steps up in pounds: HELD.** £141 at 2021, £348 at 2022, £710 at 2023.

**Across the two seeds.** Both seeds hold all five bands, and the paired gain in 2023 depth is
+2.7 and +3.4 months. The stock control's own spread between seeds (2023 mean £198 and £250, share
13.4% and 10.1%) is the size of the dice noise, and the demand arm's depth gain is several times it.
Per the pre-registration, that is the second seed owed before `THE_SHORTFALL_IS_SHARED_ON_THE_MONTHS_DEMAND`
defaults on.

**What repeated, so it is not dice.**
1. **The 2019 to 2020 fall in depth** (seed 1: 6.8 to 3.3; seed 2: 6.0 to 2.8). It is in both seeds,
   so it belongs to the world, not the payment noise. The record rises every year. Candidates are the
   same as seed 1's: deep pre-2020 debtors leaving or closing, or their income move ending the
   spell. I still cannot say which; a per-account trace across 2019-2020 on either arm settles it.
2. **The median barely moves outside 2016 and 2023.** The gain stays in a tail of persistent-deficit
   households, so the pool remains bimodal.
3. **The seed bounds the noise, not the budget population**, as the pre-registration said: both seeds
   share the households the budget puts under water.

**Ruling.** Two seeds support the switch. It moves to default on, in a separate commit that also
handles the controls the world change reds.
