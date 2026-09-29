# Prereg: the sign of the decided-differently set over five seeds on one weather store

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Item:** `rerun-the-value-cycle-ab-on-one-weather-store-with-more-seeds`

## When, and on what

- **Written:** 2026-09-29 ~08:51Z (tick worker), before either launch. The predictions below were fixed before any output existed. The only later edit is this launch record.
- **Launched:** unit `longjob-ab5-runa` at 08:51:17Z and `longjob-ab5-runb` at 08:51:42Z, both through `launch_long_job`, with logs and artefacts in `/var/tmp/se-ab5-out/run{A,B}.{log,json}`. The second launch was not refused on headroom.
- **Code:** worktree `/var/tmp/se-ab5-b79e2c0e8`, detached at origin/main `b79e2c0e8`. It carries `c39e01693`, `e297d1169` and `b9c9092e6`. Nothing else writes to it.
- **Weather store at launch:** `weather_store_digest()` = `e11451b5ebf3708fdcd7482df7a48236df79e541b2858558dbeaa57cb210d242`.
- **Seeds:** 11111, 88888 (the two already graded) and 22222, 33333, 44444 (new).
- **Shape:** two `--level-arm` noise-floor runs launched in parallel through `background/launch_long_job.py`, from the same pinned worktree: run A = `11111,88888,22222`, run B = `33333,44444`. They share code and store, so they are one family split for wall-clock. If the second launch is refused on headroom, it runs after the first. That changes the timing and nothing else.

## Definitions

These are unchanged from `SEAT_PREREG_THE_PLUS_880_ON_ACCOUNTS_THE_ARMS_DECIDED_DIFFERENTLY_2026-09-29.md`.

- **D (decided differently):** an account with at least one renewal whose offered rate differs between the arms, or where one arm priced and the other declined.
- **Roster-only:** renewals that appear in one arm's log only. They are their own category, not D.
- **A (decided alike):** zero differing renewals and zero roster-only renewals.
- **The per-account quantity:** value-arm minus level-arm, which is pre-4c net plus arrears lines. It is read from each seed's `noise_floor` row.
- **PROS-2016-0098 is excluded from D throughout.** Its effect is a churn roll: its level-arm self leaves at different dates on different seeds, which is not a decision.

## Predictions

**W. The weather store.**
- Every arm of every seed reports the same `weather_store` digest, and it equals the value above.
- `same_weather_store` is True in both artefacts.
- If W fails, nothing below is graded. That run is a refusal, not a result.

**P1. D's sign, one line per seed.**
- **Prediction:** D's value-minus-level, excluding 0098, is **positive on each of the five seeds**, between +£300 and +£1,800 on each.
- **Confidence:** about 60% per seed, and about 25% that all five are positive.
- **Reason:** +£900 and +£1,197 were measured on 11111 and 88888 at `5f05e0068`. But the per-account sign tests were p=0.77 and p=0.90, so the sum is carried by a few accounts. A single seed flipping sign would not surprise me.
- **Seeds 11111 and 88888 are not expected to reproduce** the earlier figures. The store changed (`f0ba399a4`) between that run and this one, for all arms.

**P2. A stays within ±£25, one line per seed.**
- **Prediction:** A's value-minus-level is within ±£25 on each seed.
- The same bound applies to the never-priced accounts, which are a subset of A.
- **Confidence:** about 75%. The +£2,598 on 88888 was attributed to the store swap under the last arm, and that swap is now refused by construction. If A breaches £25 on any seed while W holds, the leak was **not** the store alone, and the +£880 reading loses its footing again.
- **Refutation line, carried over:** |A| > £100 on any seed means money moves where nothing was decided, and D's sum cannot be credited to decisions on that seed.

**P3. The pooled sign test on D.**
- **(a) Seed level.** The sign of D's sum across the five seeds.
  - **This test cannot reach significance.** At n=5, 5/5 has an exact two-sided p of 0.0625, which is above 0.05. So the strongest possible outcome is "suggestive, not distinguishable".
  - **Prediction:** 4 or 5 positive of 5.
- **(b) Account level, pooled.** The exact two-sided sign test on every (account, seed) pair in D, excluding 0098, with ties at ±£0.005 dropped.
  - **Prediction:** **p > 0.05.** It is not distinguishable from zero.
  - The earlier per-seed splits were 21/24 and 29/31. Pooling five seeds of roughly 45 to 60 non-tied pairs each gives about 250 pairs, which is enough to detect a 57/43 split. I predict the split is closer to even than that.
  - **Caveat:** the pairs are not independent across seeds, because the same account appears five times. So even a p < 0.05 here overstates the evidence. The result will say so.

**P4. D's size.** 60 to 70 accounts per seed. It was 69 of 164 on both earlier seeds.

## The plain answer the result must give

The result must say one of the following:
- "D's sign is distinguishable from zero", with the test and bound.
- "It is not."
- "We cannot yet say", with the bound.

Given P3(a)'s arithmetic, the prediction is: **not distinguishable at five seeds.** The result will also state how many seeds, at the observed per-seed spread, would make the seed-level mean distinguishable.

## How it will be graded

- **Grader:** a script over both artefacts. It reads `decided_differently_by_account`, the arms' `*_net_by_account_gbp` and the `*_arrears_lines_by_account_gbp`.
- **Checks before grading:** the per-account sums reconcile to `selection_gbp`, and the arrears lines reconcile per account.
- **Output:** a `SEAT_RESULT_` beside this file, with one row per prediction and per seed. Its first row is each arm's weather-store digest and the `same_weather_store` verdict.
