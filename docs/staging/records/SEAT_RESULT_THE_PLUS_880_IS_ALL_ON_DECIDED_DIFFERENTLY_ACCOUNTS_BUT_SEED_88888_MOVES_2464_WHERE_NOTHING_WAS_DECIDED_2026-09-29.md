# Result: the +£880 is all on accounts the arms decided differently, but at HEAD seed 88888 moves £2,464 on accounts where no renewal was decided at all

**Severity:** LATENT · **Lane:** A_strategy_governance · **Item:** `grade-the-plus-880-once-the-decision-fields-are-on-origin` · **Class:** `measurements_that_mirror`

**Run and prereg**

- **Prereg:** `SEAT_PREREG_THE_PLUS_880_ON_ACCOUNTS_THE_ARMS_DECIDED_DIFFERENTLY_2026-09-29.md`, on origin at `3b9a11eea`. It was written after launch and before any output existed; it says so itself.
- **Run:** `5f05e0068` in `/var/tmp/se-seat-executor`. Seeds 11111 and 88888, `--level-arm`, leg 4b at its default. The artefact is `/var/tmp/se-arrears-lines-head/value_cycle_ab.json` (03:01 BST). Grader: `/var/tmp/se-tick-880/grade880.py`.
- **Checks:** 164 accounts per seed. The per-account value-minus-level sums to `selection_gbp` exactly. Both arms' arrears lines reconcile on both seeds, with 0 accounts off by a penny or more.

**Selection:** −£5,077.37 on seed 11111 and +£3,618.80 on seed 88888. At `fcba478b7` these were −£3,508 and +£707. The run's own verdict: not distinguishable from zero.

## Grades

| Line | Predicted | Measured | Grade |
|---|---|---|---|
| P1: sign of the priced set, ex-0098 | positive on both seeds, £400–£1,400 each | **+£899.56 / +£1,330.85** | **holds** |
| P2: between-seed difference in 0098's level-arm arrears line | grows past −£5,659.81 | +67.28 v −7,177.57, so **−£7,244.85** | **holds** |
| P3: 0098 leaves the level arm on different dates | 2017 v 2020 | **2017-03-23 / 2020-03-22** | **holds** |
| P4a: count of accounts decided differently (D) | 40–70 per seed | **69/164 on both seeds**, CP95 [0.344, 0.500]. That is 69 of the 70 priced accounts, and 0 outside the priced set | **holds** |
| P4b: D's share of the priced-set figure, ex-0098 | ≥ 90% on each seed | **100.0% / 89.9%** | **holds on 11111; misses on 88888 by 0.1 pt** |
| P4c: A set (decided alike) within ±£25 | ±£25 on each seed | **+£7.34 / +£2,598.13** | **holds on 11111; REFUTED on 88888** |
| P4d: 0098's roster-only renewals | on 11111 only | 1 renewal in the value log only on 11111, 0 on 88888 | **holds** (0098 is also in D on both seeds, through its differing offered rates) |
| P4e: sign test across D, ex-0098 | not significant | +21/−24 (p=0.77) and +29/−31 (p=0.90) | **holds** |

**The refutation line fired on one seed.** The prereg said that if A carries more than £100 on either seed, the +£880 cannot be credited to decisions. On seed 88888, A carries +£2,598.

## What that means, stated narrowly

**On the priced accounts, the partition is clean.**
- Every priced account except one is in D on both seeds.
- The one priced account the arms decided alike carries £0.00 on 11111 and +£133.91 on 88888.
- So "priced" and "decided differently" are, at HEAD, the same set to within one account. The upper bound in the 09-28 result is tight.

**The +£880 does not survive as evidence of inference.** The reason is not that it sits on alike accounts; it does not. The reason is that on seed 88888 a same-sized sum moves where nothing was decided:
- 94 never-priced accounts carry **+£2,464**, against +£3 to +£7 at `fcba478b7`.
- The largest are PROS-2018-0035 (+£1,228.68), PROS-2024-0082 (−£1,192.42), PROS-2019-0346 (−£1,135.07), SYN-2016-051 (+£723.66) and PROS-2016-0024 (+£719.78).
- None of them has a renewal row in either arm's log.
- **The differences are in the pre-4c net, not the arrears lines.** For example, PROS-2016-0024 has £3,495.49 v £2,899.25 on the same 201 bills. PROS-2024-0082 has **16 bills in the value arm and 5 in the level arm**.

**Where it comes from.**
- **The value arm is seed-invariant.** PROS-2016-0024 reads £4,118.64 on both seeds, and 0098 reads −£5,622.70 on both.
- **The level arm is not.** On seed 11111 it matches the value arm on these accounts to within £3. On seed 88888 it does not.
- The noise floor re-draws `elasticity` on the level arm (`REDRAW_KEYS`, `tools/run_value_cycle_ab.py:5639`). So the seed-88888 elasticity draw reaches something other than renewal pricing: a different bill count on the same account suggests acquisition timing, and a different net on the same bill count suggests volume or rate.
- **The mechanism is not established.** I have not read which call-sites the patched symbol serves. Why this leak was £3 at `fcba478b7` and £2,464 at `5f05e0068`, on the same seed, is also not established. The candidates are the commits between them that 875322e5a already named: `254b4c1e4` (held bills released) and `e83d571c3` (the world answers the listing lookup). **I cannot yet say** which, and nothing here tests either.

**What this does to the thesis read:**
- The ±£4.2k-to-£8.7k selection switch is now two things. The first is 0098's churn roll: −£5,984 on 11111 and −£176 on 88888. The second is a new, un-decided leak of about £2.5k on 88888.
- The decided-differently set carries +£900 and +£1,197. That is positive on both seeds, but it is not broad: the sign tests give p=0.77 and 0.90. At n=2 it sits beside a non-decision term of the same size.
- **We cannot tell whether the arm's decisions made money.** The grade is that, with the counts above.

## Next, one variable

Take one account, PROS-2024-0082, which has 16 v 5 bills. Read the level arm's first-bill date and the value arm's first-bill date on seed 88888, then name the call-site of the re-drawn elasticity symbol that sets it. If that is acquisition, the partition needs a third category (acquisition decisions or draws), next to renewals and roster. Only after that, re-run seed 88888 at `fcba478b7` against `5f05e0068`, with nothing else changed, to find which commit opened the leak.
