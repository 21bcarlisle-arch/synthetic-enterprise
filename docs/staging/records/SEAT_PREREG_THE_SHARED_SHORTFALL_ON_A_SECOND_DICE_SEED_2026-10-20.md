**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `the-budget-shared-shortfall-second-seed`
**Knowledge:** debt-and-collections -- `docs/market_research/household_budget_w2_4.md`, "Graded (2026-10-20): sharing the shortfall removes the pre-crisis excess, on one seed"

# Pre-registration: the shared shortfall on a second dice seed

**Written 2026-10-20, before any of the three arms was launched.** This is the second seed owed by
the one-seed grade. That grade held the finding's prediction. One seed cannot default a world switch
on.

## The run

Three arms, world-only to 2024-12-31, at `5a2468fdf` (origin/main), in the worktree
`/var/tmp/budget-seed2`. Each arm goes through `background.launch_long_job`, one after another. The
driver is `/var/tmp/budgetpay/capture_arm6.py ARM OUT 2024-12-31 2`:

| Arm | `BUDGET_DECIDES_PAYMENT` | `ENERGY_SHARES_THE_SHORTFALL` | Output |
|---|---|---|---|
| off | False | False | `/var/tmp/budgetpay/seed2_off.json` |
| basket first | True | False | `/var/tmp/budgetpay/seed2_basket.json` |
| shared | True | True | `/var/tmp/budgetpay/seed2_shared.json` |

**Dice seed 2.** Seed 1 used the default dice. `grade_world_debt_against_ofgem.dice_seeded` salts
every per-period payment draw, and the capture refuses a salt that reached no draw.

**What a dice seed varies, and what it does not.** The salt reaches `_period_substream` in
`simulation/payment_behaviour_source.py` alone: the payment event, its reason, representation and
later settlement. The household budget draws from its own substreams: income, composition, housing,
savings and the yearly income move. So this seed re-draws the payment noise around the budget, and
**not** which households the budget puts under water. It answers the question the one-seed grade
asked: is a paired difference of 0 to 2 accounts out of about 200 noise? It does not re-draw the
budget population. That is a separate robustness question, and it is not run here.

**Base.** The base is 77 commits past seed 1's `78a36a84c`. The three new arms share it, so they are
paired with each other and not with seed 1's arms. The grader's control
(`/var/tmp/budgetpay/grade6.py`, which is `grade4.py`/`grade5b.py`'s readings with the inputs moved
to argv) was run first on `world2_off`, `world4` and `world5`. It re-printed seed 1 exactly: basket
U1 23% and £828; shared U1 6%, £244, and an excess of +0.9 at most in 2016-2021.

## Predictions (bands copied from the one-seed grade)

Shared arm, against off on the same seed:

- **P1.** Every Q4 2016-2021 shared-off difference, electricity heads aged over 91 days, is within
  **±1.0 point**. (Seed 1: -1.0 to +0.9.)
- **P2.** U1 is **10% or less**: the share of budget-under-water electricity accounts that never
  settle a late bill. (Seed 1: 6%.)
- **P3.** Pounds behind per account behind at Q4 2023 are **£200-500**. (Seed 1: £244.)
- **P4.** The crisis step-up survives: the Q4 2022 less Q4 2021 diff-in-diff is **> 0**. (Seed 1:
  +1.6.)
- **P5.** U4, P(unpaid → unpaid) among the under-water accounts, is **≥ 0.9**. (Seed 1: 0.926.)

The basket-first arm is the contrast. If it also shows no excess on this seed, then seed 1's
shared result cannot be credited to the switch:

- **B1.** The basket-off difference is above +1 in **at least 3 of the 6** years 2016-2021. (Seed 1:
  5 of 6.)
- **B2.** Basket £ per account behind at Q4 2023 is **£500 or more**. (Seed 1: £828.)

On the instrument:

- **I1.** The budget-under-water set is the same in both ON arms and equals seed 1's size: **55
  accounts, 31 of them electricity**. If it differs, the dice reach the budget after all, and the
  paragraph above is wrong.

## What each outcome does

- **P1-P5 and B1 all hold →** the switch decision stands on two dice draws. Then, as its own
  commit with a line on the knowledge page: `BUDGET_DECIDES_PAYMENT = True` and
  `ENERGY_SHARES_THE_SHORTFALL = True`. The world change is decided blind to company results.
- **P1 fails** (any year outside ±1) **→** both switches stay False. The residual excess is the
  next cause, and the housing draw (R10) is the candidate.
- **P3 or P4 fails →** the switches stay False. The level or the crisis shape is wrong in a way one
  seed hid.
- **B1 fails while P1 holds →** I cannot attribute the change to the shared shortfall on this seed.
  The switches stay False and I file that as a finding.
