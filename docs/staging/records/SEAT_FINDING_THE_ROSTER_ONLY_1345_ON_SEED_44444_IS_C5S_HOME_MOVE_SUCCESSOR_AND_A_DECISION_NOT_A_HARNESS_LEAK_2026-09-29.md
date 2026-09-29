**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING: the roster-only +£1,345 on seed 44444 is C5's home-move successor, and it is a decision, not a harness leak

**Subject.** Increment 1 of `SEAT_RESULT_THE_DECIDED_DIFFERENTLY_SIGN_OVER_FIVE_SEEDS_ON_ONE_WEATHER_STORE_2026-09-29.md` found one roster-only account on seed 44444 worth +£1,345.47 and did not name it. **Source:** `/var/tmp/se-ab5-out/runB.json`, `seeds[1]` (seed 44444), read only. No simulation was run.

## The account

**`C5_2`.** It is the only entry in `selection_roster_difference.accounts_only_in_the_value_arm`, and `accounts_only_in_the_level_arm` is empty. It is in the value arm's `value_arm_net_by_account_gbp` at +£1,345.47 and missing from the level arm's. Its `decided_differently_by_account` row is `in_value_log_only: 2`, with every other count at 0. `saas/customers.py` registers it with `"successor_of": "C5"`.

## The mechanism: (a), a decision the arm made one account upstream

| | value arm | level arm |
|---|---|---|
| C5 first renewal, 2016-12-31 | margin £59/MWh, offered £181.91 | margin £26/MWh, offered £148.91 |
| p_retain at that renewal | 0.2135 | 0.7198 |
| roll (**the same draw in both arms**) | 0.2812 → **churned** | 0.2812 → renewed |
| C5 after that | left 2016-12-31, net £260.20 | 5 renewals, left 2020-12-30, net £1,636.16 |
| C5_2 | activates 2016-12-31, renews 2017-12-31 and 2018-12-31 (margins £84 and £96), left 2018-12-31, net £1,345.47 | never exists |

The churn branch in `simulation/run_phase2b.py` (around line 2660) looks up `SUCCESSOR_MAP[billing_account]` when the event's `home_move_won` fires. It then activates the successor from the churn date: `won_successor_activations[successor_id] = term_start_str`. So C5_2 exists **only in an arm where C5 churned**, and C5 churned only in the value arm because of the value arm's price. The roll is identical, so the world did not diverge. The decision did.

**It is not (b).** Nothing upstream of a decision separated the rosters. Seed 33333 has an empty roster difference. On 44444 the one divergence is the child of the one decision that D grades most heavily, C5 at −£1,375.96.

## What it does to the grade

D is keyed by **billing account**. A successor tenure carries a new key, so it falls into roster-only, and C5's single decision is split across the partition:

| | £ |
|---|---|
| C5, in D | −1,375.96 |
| C5_2, roster-only | +1,345.47 |
| **C5 + C5_2 (one supply point, one decision)** | **−30.49** |
| D ex-0098 on 44444, **as pre-registered** | **−559.81** |
| D ex-0098 on 44444 with C5_2 folded into C5 by `successor_of` | **+785.66** |

**So on 44444, D's partition decides P1's sign.** With the successor folded in, P1 would not be refuted on this seed. The prereg's D is **not** changed here. P1 stays refuted as graded, because re-partitioning after seeing the answer would be exactly the move a prereg exists to prevent. But the prereg's D is **too narrow**. It counts the price of a decision and leaves out the successor tenure that the decision caused. The five-seed answer must carry this caveat beside it. It should also carry a clearly labelled, ungraded diagnostic line for D folded by `successor_of`, for every seed. Seed 44444 alone is enough to show the difference can reverse a seed's sign.

**Not established here: whether C5_2 is the same household.** The successor shares C5's premises and EAC (`EFFECTIVE_EAC_KWH` copies the predecessor's). "Home-move won" could mean we followed the occupant or won the premises' next occupant. Either way it is causally downstream of C5's churn, which is all this finding needs. The fold is by supply-point lineage, not by household.

## The field the artefact lacks

The artefact **does** tell (a) from (b), but only by joining dates across blocks: C5's value-arm `left_at` equals C5_2's activation date, and the roll is the same in both arms. It does not name the lineage. **The missing field is a per-account `successor_of` (or `activated_by_churn_of`) in `*_decisions_by_account`.** Without it, the grader can only fold successors by reading `saas/customers.py`. With it, the fold is one line. That field is the cheap harness change. It should land in `tools/run_value_cycle_ab.py` before any re-run that is meant to grade a household-keyed D, and it does not affect the running legs.
