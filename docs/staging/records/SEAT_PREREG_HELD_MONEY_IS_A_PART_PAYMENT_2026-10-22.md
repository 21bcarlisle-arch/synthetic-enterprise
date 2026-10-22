**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `W2_demand_negative_margin_part_payment`
**Knowledge:** debt-and-collections -- `docs/market_research/household_budget_w2_4.md`, "2026-10-22: held money is a part payment"

# Pre-registration: money held toward a bill is a part payment, not money to share again

**Written 2026-10-22, before either arm was launched.** It serves the BLOCKING crisis bad-debt finding
(`SEAT_FINDING_THE_CRISIS_BAD_DEBT_CONTROL_HAS_SKIPPED_..._2026-10-14.md`, "2026-10-22 (early)"), which
named the zero-payment population and left it unchanged (one variable).

## The run

There are two arms, world-only to 2023-12-31, with default dice. They run at origin/main plus only the
`HELD_MONEY_IS_A_PART_PAYMENT` change, in the worktree `/var/tmp/held-mut`. The driver is
`/var/tmp/leaver_trace/dump_held.py ARM END OUT`. Graders: `depth.py` (unchanged), `engaged.py` and
`zero_pay.py` (all three in `/var/tmp/leaver_trace/`). Every other switch is at its default, so the
demand reading is on.

| Arm | `HELD_MONEY_IS_A_PART_PAYMENT` | Output |
|---|---|---|
| held off (control) | False | `/var/tmp/leaver_trace/arm_held_off.json` |
| held on | True | `/var/tmp/leaver_trace/arm_held_on.json` |

The control is re-run because the base has moved since `arm_demand.json`. Its depth column should
reproduce `arm_demand.json` (3.3-6.8 mean months, £580 at 2023) to within dice noise.

## Predictions

The replay of the rule alone (`replay_held.py`, on the seed-2 bills) gives the direction and size.
- **H1.** In the held-on arm, deficit account-years with no payment in the year fall from about 26 to
  **at most 3**, and no account has a 24-month no-payment run.
- **H2.** Engagement (`engaged.py`, paid anything in the trailing 3 months) is **at least 80%** in
  every year 2017-2023 with n ≥ 10. The control is 25-62% pre-crisis and at 2023.
- **H3.** Depth falls. Held-on `mean_months` is **below** the control's in at least 5 of the 8 years,
  and at 2023-12-31 it is **1.5 to 4.5** months (control about 5; the replay roughly halves unpaid
  bills).
- **H4.** Pounds: held-on `mean_bal` at 2023-12-31 is **£250 to £600** (control about £580-710; Ofgem
  £1,303).
- **H5.** Heads: `share%` in arrears changes by **−4 to +1 points** each year. A household that
  part-pays leaves the 91-day pool sooner, so the share can only fall or hold.

**What decides the switch.** H1 and H2 are the fidelity case: the record's ~90% engaged against the
control's 25-60%. H3-H4 are its cost: depth and pounds move away from Ofgem. If H1-H2 hold, the switch
goes on after a second seed whatever H3-H4 show (F11), and the depth gap is recorded as a gap the
demand reading had been closing with households that never paid. If H2 fails (still under 80%), the
non-payment comes from somewhere else, and the switch stays off pending that cause.

## Seed 1 graded (2026-10-22, 03:05 BST): H1-H5 all hold

Full table in `docs/staging/records/SEAT_RESULT_HELD_MONEY_IS_A_PART_PAYMENT_SEED_1_2026-10-22.md`.

## Seed 2, pre-registered before launch

The same two arms on dice seed 2: `dump_held.py ARM 2023-12-31 OUT 2`, which wraps the run in
`grade_world_debt_against_ofgem.dice_seeded(2)` and refuses a seed that reached no draw. Outputs:
`/var/tmp/leaver_trace/arm_held_{off,on}_s2.json`. **H1-H5 apply unchanged.** The control should
reproduce `arm_demand_s2.json`. As with the demand reading, the seed re-draws the payment noise and not
the budget population, so it bounds the noise. If both seeds hold, the switch defaults on in its own
commit.
