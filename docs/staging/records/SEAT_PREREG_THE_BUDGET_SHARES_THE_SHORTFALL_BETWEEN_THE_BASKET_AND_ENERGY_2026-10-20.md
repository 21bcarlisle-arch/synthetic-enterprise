**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `the-budget-orders-energy-as-a-priority-bill-before-the-full-normative-floor`
**Knowledge:** debt-and-collections -- `docs/market_research/household_budget_w2_4.md`, "2026-10-20: what a household short of money cuts, and in what order"

# Pre-registration: the budget shares the shortfall between the basket and energy

**Written 2026-10-20, after the arm was launched and before any of its output existed.** The finding
under test is
`docs/staging/WORKER_FINDING_THE_BUDGET_SPENDS_THE_NORMATIVE_FLOOR_IN_FULL_BEFORE_ENERGY_SO_THE_PRE_CRISIS_HEADS_RUN_HIGH_2026-10-19.md`.

## The one variable

`ENERGY_SHARES_THE_SHORTFALL` in `simulation/household_budget.py`. Off (today), the ex-energy
basket is paid in full and energy takes the whole shortfall. On, money left after housing is shared
between the basket and what is owed on energy pro rata to their sizes. The knowledge page gives the
evidence: housing protected (ONS), essentials and arrears together (JRF, 91% overlap). It also names
the GAP: no source gives the pound split, so pro rata is a stated belief, not a measurement.

## The run

World-only to 2024-12-31, one dice draw, `BUDGET_DECIDES_PAYMENT` on, in the worktree
`/var/tmp/budget-arm5`: 78a36a84c's tree plus only this file's change (`git diff --stat` there:
`simulation/household_budget.py` alone). It is the same sha as the off arm `world2_off.json` and the
income-moves on arm `world4_on_income_moves.json`, so the new arm differs from `world4` in this one
variable. Output: `/var/tmp/budgetpay/world5_on_shared_shortfall.json`. Grader: `grade4.py`'s
readings with the import path repointed (`/var/tmp/budgetpay/grade5.py`). It must first re-print
`world4`'s 23% U1 and £828 exactly.

## Predictions

**The finding's own, filed 2026-10-19 (quoted):** "A floor that compresses toward actual spending
lowers the pre-crisis ON-OFF excess below +1 point in every Q4 2016-2021, and leaves U1 at or under
30%. If the excess stays above +1, the housing draw is the larger part."

**Mine, written now, from the table printed at real inputs (knowledge page):**

- **S1, heads: the finding's line is not met.** The order does not change *who* is short (6.4% of
  households in 2019 under both orders), only by how much. A short household now pays about 70% of
  each bill and clears its oldest bill first. So aged debt arrives later, roughly ten months into a
  spell rather than three, and most spells (about 2.8 years) still reach it. Predicted: the Q4
  ON-OFF excess falls by about half, to +0.3 to +1.8 points in 2016-2021, with **at least one of the
  six years above +1**. If every year is under +1, S1 is refuted and the finding's prediction holds.
- **S2, U1.** The share of budget-under-water electricity accounts that never settle a late bill
  falls from 23% to **10% or less**.
- **S3, pounds.** £ behind per account behind at Q4 2023 falls from £828 to **£200-500** (R1's
  range is £200-400; Ofgem £1,303).
- **S4, U3.** Q4 2022 ON-OFF falls below +3, to **+0.5 to +2.5**.
- **S5, U4.** P(unpaid → unpaid) among the under-water accounts stays **≥ 0.9**. While a backlog
  exists, the current bill is never the one cleared.

## What each outcome does

- Every 2016-2021 year under +1 → the order was the excess. The switch is a candidate to move, but
  only on a second seed: one seed cannot bound a paired difference.
- Any year above +1 → the next layer is the one the finding names: the housing draw (R10, uniform
  £400-1,100 with no tenure link).
- `BUDGET_DECIDES_PAYMENT` stays False whatever this run says. One seed moves no default.
