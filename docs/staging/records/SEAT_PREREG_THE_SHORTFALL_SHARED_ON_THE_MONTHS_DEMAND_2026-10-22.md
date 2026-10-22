**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `W2_shortfall_shared_on_demand`
**Knowledge:** debt-and-collections -- `docs/market_research/household_budget_w2_4.md`, "2026-10-22: stock or demand"

# Pre-registration: the shortfall shared on the month's demand, not the arrears stock

**Written 2026-10-22, before either arm was launched.** It serves the BLOCKING crisis bad-debt finding
(`SEAT_FINDING_THE_CRISIS_BAD_DEBT_CONTROL_HAS_SKIPPED_..._2026-10-14.md`), whose cause is now one
world rule: the stock reading caps a household's arrears at `C/(A−B)` bills.

## The run

Two arms, world-only to 2023-12-31, default dice, at `df9792c573` plus only the
`THE_SHORTFALL_IS_SHARED_ON_THE_MONTHS_DEMAND` change, in the worktree `/var/tmp/demand-mut`. Driver
`/var/tmp/leaver_trace/dump_arm.py ARM END OUT` (`dump.py`'s body, plus the switch). The grader is
`/var/tmp/leaver_trace/depth.py`, unchanged from the depth grade of 2026-10-21. Both switches above it
are at their defaults (on).

| Arm | `THE_SHORTFALL_IS_SHARED_ON_THE_MONTHS_DEMAND` | Output |
|---|---|---|
| stock (control) | False | `/var/tmp/leaver_trace/arm_stock.json` |
| demand | True | `/var/tmp/leaver_trace/arm_demand.json` |

The control is re-run, not borrowed, because `dump_2023.json` is at an older base. Its depth column
(1.4-2.4 mean months behind at each 31 December, 2016-23) is the expectation for the control.

## Predictions

Depth = `mean_months` in `depth.py`: an account's whole unpaid balance at 31 December over its own
trailing mean monthly bill, over credit accounts with a bill unpaid more than 91 days.

- **D1.** The demand arm's `mean_months` exceeds the control's in **every** year 2019-2023.
- **D2.** The demand arm's `mean_months` at 2023-12-31 is **3 to 9 months** (control 1.4-2.4; the
  record's average is most of a year). Below 3: the rule is not what holds the depth down. Above 9
  in any year: overshoot, so the uncapped stock needs an exit the world lacks.
- **D3.** Pounds: `mean_bal` at 2023-12-31 is **£400 to £1,300** (control about £200; Ofgem £1,303
  per electricity account in arrears).
- **D4.** Heads: `share%` in arrears rises by **0 to +5 points** in each year. The rule does not
  change who is short; a household stays in the pool longer.
- **D5.** The crisis still steps up in pounds: demand `mean_bal` at 2022-12-31 exceeds 2021-12-31.

D1 and D2 together decide the switch. If D1 holds and D2 overshoots, the next step is the
supplier routes that bound debt in the record (repayment plans, Fuel Direct), not reverting to the
stock reading. One seed, so a paired second-seed arm is owed before any default moves.

## Seed 1 graded (2026-10-22, 00:55 BST): D1-D5 all hold

Full table in the result record,
`docs/staging/records/SEAT_RESULT_THE_SHORTFALL_SHARED_ON_THE_MONTHS_DEMAND_SEED_1_2026-10-22.md`.

## Seed 2, pre-registered before launch

The same two arms on dice seed 2 (`dump_arm.py ARM 2023-12-31 OUT 2`, which wraps the run in
`grade_world_debt_against_ofgem.dice_seeded(2)` and refuses a seed that reached no draw). Outputs:
`/var/tmp/leaver_trace/arm_{stock,demand}_s2.json`. **D1-D5 apply unchanged.** What the seed can show
is the same as the shared-shortfall second seed: it re-draws the payment noise around the budget, not
which households the budget puts under water. So it bounds the noise, not the budget population.
