# Prereg: how much of the +£880 sits on accounts where the two arms decided differently, and the 0098 re-measure at HEAD

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Item:** `grade-the-plus-880-once-the-decision-fields-are-on-origin`

## When this was written, which is not when the item asked

- **Written:** 2026-09-29 01:30Z (tick worker).
- **The run was already launched**, and not by this item. pid 1743658 started at 23:34:37Z in `/var/tmp/se-seat-executor`, 20 seconds after that worktree committed `5f05e0068`, which added the decision fields. The command was `tools.run_value_cycle_ab --level-arm --noise-floor-seeds 11111,88888 --out /var/tmp/se-arrears-lines-head/value_cycle_ab.json`, with leg 4b at its default.
- **Nobody was watching it.** No waiter was alive, `se-arrears-wait.log` was empty, and no prereg for it existed on origin or in either tree.
- **The item required a prereg BEFORE launch, so this one is late.** It is still a prediction, not a report. When it was written, the output directory was empty. Seed 11111 had finished (`seed 1/2 done`, 4,170 s), but its row goes into the artefact only when the run ends, and I read no per-account line from the log. Seed 88888 was part-way through.
- **The code is `5f05e0068`.** That commit sits on top of `f997f8bf7` (the arrears lines) and the balance-at-close write-off rule. The weather store (`f0ba399a4`, 01:25Z) landed after launch and is **not** in this run.

## What is being compared

The basis is `SEAT_RESULT_NO_ARTEFACT_RECORDS_WHAT_EITHER_ARM_DECIDED_AND_THE_PRICED_SET_CARRIES_A_STABLE_PLUS_880_2026-09-28.md`, measured at `fcba478b7`.

- **"Priced set":** accounts where the value arm priced at least one renewal. There were 70 of 164.
- **"+£880":** value-minus-level summed over the priced set, with PROS-2016-0098 excluded. It read +£877 to +£884.
- **"Decided differently" (D):** accounts with `decided_differently_by_account` showing at least one renewal where the offered rate differs, or where one arm declined and the other priced.
- **Roster-only:** renewals that appear in one arm's log only. They count as their own category, never as D.
- **"Decided alike" (A):** every account with zero differing renewals and zero roster-only renewals.

## Predictions

**P1. Sign at HEAD.** Priced-set value-minus-level, excluding 0098, is **positive on both seeds**, between +£400 and +£1,400 on each.
- Why it may move: `254b4c1e4` released held bills after `fcba478b7`.
- Why I predict the sign holds: that change acts on both arms alike.

**P2. `875322e5a`'s prediction, adopted as written.** The between-seed difference of 0098's level-arm arrears line grows in magnitude past −£5,659.81.
- Confidence: about 60%.
- The mechanism is more issued bills that can fail. What I have not seen is how many of 0098's bills were held at `fcba478b7`.

**P3. 0098 still leaves the level arm at different dates on the two seeds**, as it did before: 2017-03-23 on 11111 and 2020-03-22 on 88888.
- Confidence: about 80%.
- None of the landed commits touches the retention roll or the elasticity re-draw.

**P4. The partition.**
- (a) **The count of D accounts per seed is 40 to 70.** The value arm prices a per-customer margin and the level arm prices a flat one, so an offered rate that is exactly equal should be rare. The ceiling is the priced set, because never-priced accounts are identical by construction.
- (b) **The D set carries at least 90% of the priced-set, ex-0098 value-minus-level on each seed.**
- (c) **The A set's value-minus-level is within ±£25 on each seed**, the same order as the never-priced set's +£3 to +£7.
- (d) **0098 shows roster-only renewals on seed 11111 and not on 88888.** On 11111 its level-arm self leaves in 2017, so its later renewals exist in the value log alone.
- (e) **The sign test across D accounts stays non-significant**, with two-sided p > 0.05 on each seed. The +£880 was concentrated (21 v 25 at `fcba478b7`), and a decision partition should not make it broad.

## What refutes the inference reading

If A carries more than £100 of value-minus-level in magnitude on either seed, then money moves where the arms decided alike, and the +£880 cannot be credited to decisions.

If P4(b) fails the other way (D carries less than half), the same conclusion follows.

**"We cannot tell at n=2" is a legitimate grade for any line.**

## How it will be graded

1. Read directly from the artefact's per-seed `noise_floor` rows: `decided_differently_by_account`, `{value,level}_arm_net_by_account_gbp` and `{value,level}_arm_arrears_lines_by_account_gbp`.
2. Clopper–Pearson 95% bounds on each count out of 164, and out of the priced set.
3. An exact two-sided sign test across D accounts, with ties at ±£0.005 excluded.
4. Grade every line above in a `SEAT_RESULT_` at a named origin commit.
