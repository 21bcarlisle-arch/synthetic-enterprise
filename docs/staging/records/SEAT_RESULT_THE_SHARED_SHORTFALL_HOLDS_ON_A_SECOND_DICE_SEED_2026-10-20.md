**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `the-budget-shared-shortfall-second-seed-grade`
**Knowledge:** debt-and-collections -- `docs/market_research/household_budget_w2_4.md`, "Graded, second seed (2026-10-20)"

# Result: the shared shortfall holds on a second dice seed, so both budget switches default on (2026-10-20)

Graded against `SEAT_PREREG_THE_SHARED_SHORTFALL_ON_A_SECOND_DICE_SEED_2026-10-20.md`, with the bands
exactly as filed. The three arms finished at 17:34 BST (`seed2_driver.log` ends `ALL_DONE`). The grader
was `python3 /var/tmp/budgetpay/grade6.py seed2_off.json seed2_basket.json seed2_shared.json`. Its
control was re-run in this turn on seed 1's `world2_off`, `world4_on_income_moves` and
`world5_on_shared_shortfall`. It re-printed U1 23%/£828 and 6%/£244 before the new arms were read.

| Q4, electricity | OFF | basket first | shared | basket-off | shared-off |
|---|---|---|---|---|---|
| 2016 | 0.8%, £69 | 1.9%, £117 | 0.8%, £69 | +1.2 | +0.0 |
| 2017 | 3.1%, £80 | 5.7%, £161 | 4.0%, £72 | +2.6 | +0.9 |
| 2018 | 7.2%, £59 | 9.1%, £189 | 7.2%, £59 | +1.9 | +0.0 |
| 2019 | 7.9%, £70 | 9.1%, £273 | 7.4%, £72 | +1.2 | -0.5 |
| 2020 | 11.9%, £64 | 12.6%, £204 | 11.4%, £65 | +0.7 | -0.5 |
| 2021 | 9.7%, £91 | 12.0%, £306 | 9.2%, £94 | +2.3 | -0.5 |
| 2022 | 7.3%, £81 | 11.0%, £365 | 8.9%, £142 | +3.7 | +1.6 |
| 2023 | 8.4%, £165 | 11.4%, £1,011 | 9.4%, £302 | +3.0 | +1.0 |
| 2024 | 9.4%, £110 | 11.8%, £872 | 10.4%, £136 | +2.4 | +1.0 |

## Graded

- **P1, each Q4 2016-2021 shared-off within ±1.0: holds.** The range is -0.5 to +0.9.
- **P2, U1 at 10% or less: holds.** 2 of 31, which is 6%.
- **P3, £200-500 at Q4 2023: holds.** £302.
- **P4, a Q4 2022 less Q4 2021 diff-in-diff above 0: holds.** +2.1.
- **P5, U4 at 0.9 or more: holds.** 0.926 (n=530).
- **B1, basket-off above +1 in at least 3 of 6 years: holds.** 5 of 6, the same as seed 1.
- **B2, basket at £500 or more at Q4 2023: holds.** £1,011.
- **I1, the same under-water set in both ON arms, 55 accounts with 31 electricity: holds.**

## Did the seed actually vary anything? Asked before crediting the result

U1 (6% and 23%) and U4 (0.926) repeat seed 1 exactly. A placebo seed would look the same, so the
question had to be asked. The answer is that the seed did reach the draws. The off arm differs
from seed 1 in every year: heads at Q4 2016 are 2 against 6, and at Q4 2022 they are 14 against 20.
The draws differ too (37,077 here). The repeats are what I1 predicted. Under water, the budget
decides payment and the dice do not, so the never-settle count on a fixed under-water set cannot
move. **So this seed tests P1, P3, P4 and B1-B2: the parts the payment noise reaches. It does not
re-test U1 or U4, and it does not re-draw which households go under water.** The prereg named that
limit before the run.

## Also noticed, not graded

On this seed the OFF world has no crisis step-up at all. Q4 2022 (7.3%) is below Q4 2021 (9.7%).
With the shared switch on, the arm still falls slightly (9.2% to 8.9%), and the step-up shows only
in pounds: £94 to £142 to £302. The diff-in-diff is positive because the off arm falls further.
That is a step-up relative to the counterfactual, not a rise in the level. It matters for the crisis
bad-debt validator, which grades levels by year. It is recorded in that finding.

## What this does

Per the prereg's rule (P1-P5 and B1 all hold): `BUDGET_DECIDES_PAYMENT = True` and
`ENERGY_SHARES_THE_SHORTFALL = True`, as their own commit, with a line on the knowledge page. The
decision is a world-fidelity one. It was made on world-only arms and is blind to company results.
