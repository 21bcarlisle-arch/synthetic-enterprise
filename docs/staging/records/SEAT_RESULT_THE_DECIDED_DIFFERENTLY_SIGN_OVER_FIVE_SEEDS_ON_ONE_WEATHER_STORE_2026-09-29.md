# RESULT (INCREMENT 1 OF 2): the decided-differently sign over five seeds on one weather store

**Grades:** `SEAT_PREREG_THE_DECIDED_DIFFERENTLY_SIGN_OVER_FIVE_SEEDS_ON_ONE_WEATHER_STORE_2026-09-29.md`, landed at `a3b1ae3c5` before either run launched, with its launch record at `11801e11f`.

**This increment is not the result.** It grades seeds 33333 and 44444 from `runB.json`. Seeds 11111, 88888 and 22222 are still running, as `longjob-ab5-runa1` and then `longjob-ab5-runa2`, and every line that pools across seeds is **PENDING** until they finish. The prereg's plain answer has not been given yet.

**Grader:** `/var/tmp/se-ab5-out/grade5.py runB.json`, run at 13:40Z on 2026-09-29.

## W — the weather store (graded first; nothing below counts without it)

| arm / seed | digest | verdict |
|---|---|---|
| run B, seeds 33333 and 44444, all arms, before and after each arm | `e11451b5…d242`, equal to the prereg's launch digest | **HOLDS** |
| run A1 (11111, 88888), run A2 (22222) | not yet written | PENDING |

**How W is read, because the artefact does not carry it the way the prereg assumed.** At b79e2c0e8 the per-arm brackets and `same_weather_store` are computed but not serialised. So the grader's per-arm printout is empty. W holds by construction instead:

- Each seed's run raises unless `same_weather_store is True` across its arms (`tools/run_value_cycle_ab.py:5415`).
- The floor-level `book_identity.weather_store` is non-null only when every before/after bracket of every arm of every seed is recorded and all of them agree. Otherwise it raises, or records `weather_store_unavailable_because` (lines 1117–1144).
- `runB.json` has `weather_store = e11451b5…d242` and `weather_store_unavailable_because = null`.

**Across artefacts,** the same digest must appear in `runA1.json` and `runA2.json`. Each leg also refuses to start unless `weather_store_digest()` equals it.

## Per-seed lines (run B)

Reconciliation: on both seeds, the per-account differences sum exactly to `selection_gbp`, and both arms' arrears lines reconcile with 0 accounts off by a penny.

| line | prediction | 33333 | 44444 |
|---|---|---|---|
| selection (context) | — | +£886.02 | −£5,198.45 |
| **P1** D ex-0098 | positive, +£300 to +£1,800 | +£1,037.49, n=69: **HOLDS** | **−£559.81**, n=69: **REFUTED** (wrong sign) |
| per-seed sign test, D ex-0098 | (context) | +23 / −22, p=1.000 | +22 / −24, p=0.883 |
| **P2** A within ±£25 | yes | −£1.89, n=94: **HOLDS** | +£1.37, n=94: **HOLDS** |
| P2 refutation line \|A\| > £100 | not breached | not breached | not breached |
| **P4** D size 60–70 | yes | 70/164, or 69 ex-0098: **HOLDS** | 70/165, or 69 ex-0098: **HOLDS** |
| roster-only (its own category) | — | n=0 | **n=1, +£1,345.47** |
| PROS-2016-0098 (excluded churn roll) | — | −£149.57 | −£5,985.48 |

**Already settled by these two seeds.** "All five positive", given about 25% confidence, is **refuted**, because 44444 is negative. P3(a)'s "4 or 5 of 5" is still reachable, but only if all three pending seeds are positive.

**Not graded by any prereg line, and worth saying.** On 44444, one roster-only account carries +£1,345. Its renewal appears in one arm's log only. That is larger in size than D's sum on that seed. The prereg deliberately keeps roster-only out of both D and A. So a +£1,345 movement sits outside both the "decided" line and the "nothing decided" line. **Named:** it is `C5_2`, the home-move successor of C5. It exists only because the value arm's price churned C5 on the same roll the level arm survived, so it is a decision rather than a harness leak. Folded into C5, it moves D ex-0098 on 44444 from −£559.81 to +£785.66. D stays as pre-registered, but its account keying is too narrow, and the five-seed answer carries that caveat. See `SEAT_FINDING_THE_ROSTER_ONLY_1345_ON_SEED_44444_IS_C5S_HOME_MOVE_SUCCESSOR_AND_A_DECISION_NOT_A_HARNESS_LEAK_2026-09-29.md`.

**D's per-account signs look like coin flips on both seeds.** They are 23/22 and 22/24, and the D sums are carried by a handful of accounts. SYN-2016-013 (+£604), SYN-2016-055 (+£488 to +£492) and PROS-2020-0304 (+£417) are the same accounts and near-identical amounts on both seeds. They are counterweighted on 44444 by C5 (−£1,376).

## PENDING

- W, P1, P2 and P4 for seeds 11111, 88888 and 22222.
- **P3(a)**, the seed-level sign over all five seeds.
- **P3(b)**, the pooled account-level sign test. For B alone it is +45 / −46, p=1.000, which is not a grade.
- The seeds-needed figure.
- The plain answer.

---

# INCREMENT 2: seeds 11111 and 88888 graded, and the pooled lines over four seeds

**Grader:** `python3 /var/tmp/se-ab5-out/grade5.py runB.json runA1.json`, run at ~17:34Z on 2026-09-29 (tick worker). `runA1.json` was written at 16:07 local by `longjob-ab5-runa1`. Everything above this line is left as written.

**Seed 22222 is MISSING.** `longjob-ab5-runa2` waited 3h09m for its predecessors, passed both of `legA.sh`'s checks (code equal to b79e2c0e8 outside `docs/`, and digest e11451b5…d242), then died at 16:08:02 local, status 1. The cause is in `/var/tmp/se-ab5-out/runA2.log`: `noise_floor` raises `AssertionError: a noise floor needs at least two seeds; got 1` (`tools/run_value_cycle_ab.py:6612` at b79e2c0e8). A one-seed leg was never admissible, and nothing checked that when the legs were split. No 22222 figure exists. The leg is relaunched as `22222,33333`; see the end of this increment.

## W — the weather store, runA1

| artefact | digest | verdict |
|---|---|---|
| `runA1.json` (11111, 88888) | `e11451b5…d242`, the only digest across both artefacts, equal to the launch digest | **HOLDS** |
| `runA2.json` (22222) | not written | MISSING |

## Per-seed lines (runA1)

Reconciliation: on both seeds the per-account differences sum exactly to `selection_gbp`, and both arms' arrears lines reconcile with 0 accounts off.

| line | prediction | 11111 | 88888 |
|---|---|---|---|
| selection (context) | — | −£4,873.11 | +£958.02 |
| **P1** D ex-0098 | positive, +£300 to +£1,800 | +£1,111.11, n=69: **HOLDS** | +£1,109.49, n=69: **HOLDS** |
| per-seed sign test, D ex-0098 | (context) | +24 / −22, p=0.883 | +24 / −22, p=0.883 |
| **P2** A within ±£25 | yes | +£1.19, n=94: **HOLDS** | −£1.89, n=94: **HOLDS** |
| P2 refutation line \|A\| > £100 | not breached | not breached | not breached |
| **P4** D size 60–70 | yes | 70/164, or 69 ex-0098: **HOLDS** | 70/164, or 69 ex-0098: **HOLDS** |
| roster-only | — | n=0 | n=0 |
| PROS-2016-0098 (excluded churn roll) | — | −£5,985.41 | −£149.57 |

As predicted, neither seed reproduces the `5f05e0068` figures (+£900 and +£1,197); the store changed in between.

## Pooled lines over four seeds (11111, 33333, 44444, 88888)

| line | prediction | result | verdict |
|---|---|---|---|
| **P3(a)** seed-level sign of D ex-0098 | 4 or 5 positive of 5 | **3/4 positive**, exact sign p=0.625. Mean +£674.57, sd £823.63, 95% t-CI [−£636.02, +£1,985.16] | Still reachable only if 22222 is positive. At four seeds: **not distinguishable** |
| seeds needed | (the result must state it) | **~6** seeds at this spread for mean/SE > 1.96 | — |
| **P3(b)** pooled account-level sign test | p > 0.05 | **+93 / −90, p=0.883** | **HOLDS** (and the pairs are not independent across seeds, so even this overstates the evidence) |
| "all five positive" | ~25% | refuted in increment 1 (44444) | REFUTED |

**Roster-only successor fold (UNGRADED, not a prereg line).** Folding each home-move successor into its predecessor, only 44444 changes: `C5_2` into C5 moves D ex-0098 from −£559.81 to **+£785.66**. With the fold, all four seeds are positive: mean +£1,010.94, sd £154.06, 95% t-CI [+£765.83, +£1,256.04]. The lineage is read from `saas.customers`, because the artefact predates the `successor_of` field. That is a post-hoc re-keying, so it is reported beside the pre-registered D and does not replace it.

**Not graded by any prereg line, and worth saying.** The whole four-seed ambiguity in the pre-registered D rests on one account pair on one seed. `C5_2` is C5's home-move successor, created because the value arm's price churned C5 on a roll the level arm survived. So it is a decision, not a harness leak (`3e608eefc`). The pre-registered D keys decisions by account, which is too narrow: it leaves a decision's consequence in the roster-only bucket. The seeds-needed figure of ~6 is almost entirely the width that one pair adds. Two further things are seen in the artefacts and not graded. First, D's composition is nearly identical on every seed: the same top accounts carry it, at the same amounts to the penny (SYN-2016-013 +£603.93, SYN-2016-055 +£491.58, PROS-2020-0304 +£417.25, SYN-2016-064 −£409.62). So the seeds are far from independent draws of D, and the t-CI over seeds describes the few draws that differ. Second, the seeds fall into two states on 0098's churn roll: 11111 and 44444 give about −£5,985, and 33333 and 88888 give −£149.57, with A exactly −£1.89 on both. That is the two-state switch in `SEAT_FINDING_THE_SELECTION_RESIDUAL_IS_A_TWO_STATE_SWITCH_PRICED_AS_A_GAUSSIAN_SPREAD_AND_THE_LEVEL_ARM_CARRIES_ALL_OF_IT_2026-09-27.md`, now visible across seeds.

**Plain answer at four seeds (interim, not the prereg's five-seed answer):** on the pre-registered D, **we cannot yet say**. D is positive on 3 of 4 seeds, and the t-CI spans zero. About 6 seeds would be needed at this spread. With the successor fold, D is positive on all four seeds, with a CI clear of zero. But that is a re-keying made after seeing 44444, so it is a lead, not a grade.

## Relaunch of 22222

- By 16:08 the pinned worktree `/var/tmp/se-ab5-b79e2c0e8` had been removed. It was re-created at 17:34Z with `git worktree add --detach` at `b79e2c0e8`. `weather_store_digest()` there = `e11451b5…d242`, equal to the prereg's, because the store is tracked in the repo (`sim/weather_world/`).
- No other `--level-arm` process was resident. It was launched at 17:35:09Z as unit `longjob-ab5-runa2b` through `background.launch_long_job` under `setsid`, with its own cgroup verified. The command is `legA.sh /var/tmp/se-ab5-out/runA2.json 22222,33333`, with no predecessor pids, and the log is `/var/tmp/se-ab5-out/runA2b.log`.
- 33333 is paired so that `noise_floor` admits the leg. It also replicates runB's 33333 from the same code and store. **Prediction, written before it finishes:** 33333 reproduces runB's D ex-0098 of +£1,037.49 to the penny. The run is seeded and the code and store are pinned, so any difference is a nondeterminism finding in its own right.
- Increment 3 gives the five-seed plain answer and the 33333 replicate verdict when `runA2.json` lands.

### The second death, 19:07Z: what the kernel chose and what else was resident

`longjob-ab5-runa2b` did not finish. The kernel reading comes from `journalctl -k` at 20:07:18–19 BST (19:07Z) on 2026-09-29:

- **Chosen:** pid 1033543 (python3, the leg itself), anon-rss 10.2 GiB. It was a *global* OOM (`constraint=CONSTRAINT_NONE`, `task_memcg=…/longjob-ab5-runa2b.service`), and swap was exhausted (`Free swap = 0kB` of 8 GiB). The unit's summary: 1h32m wall, 10.2G memory peak, 1.6G swap peak, `Failed with result 'oom-kill'`. The leg was the largest task, so every task sat at `oom_score_adj` 200 and the kernel's choice follows from size alone.
- **Resident beside it:** two further python3 processes, **pid 1259605 at 6.1 GiB rss and pid 1259606 at 5.2 GiB rss** (plus 0.1–1 GiB of swap each). Together they held more than the leg did. Everything else was under 1.4 GiB (tailscaled, weston, journald, and the claude sessions).
- **Who they were: I cannot say from the kernel dump.** It records no cgroup for non-chosen tasks. By the observed pid rate (~2.9k/min between 1033543 at 17:35Z and ~1.59M at 20:48Z), they started around 18:50–18:55Z. Consecutive pids are consistent with a pair of forked workers, such as a gate's pytest workers. `sim-runner.service` also restarted at 18:58:51Z, and its cycles peak at 5.6–6.1G by its own unit summaries. **sim-runner is a permanent daemon that routinely peaks at ~6 GiB, and a gate run can add two more multi-GiB workers.** So the rule this item's launch obeyed ("no other process over 2 GB other than the permanent daemons") was satisfied at launch and did not protect the leg: the contention arrived 1h30m after launch. The box is 24 GiB, and 10.2 (leg) + 6.1 + 5.2 exceeds it once swap is gone.

### Relaunch 3: `longjob-ab5-runa2c`, 20:49:13Z

- The pinned worktree had been removed again. It was re-created with `git worktree add --detach /var/tmp/se-ab5-b79e2c0e8 b79e2c0e8` and is now `git worktree lock`ed, so a prune cannot take it mid-run. The digest there is `e11451b5…d242`, equal to the prereg's.
- At launch, no process over 2 GiB was resident (`ps` by rss), and none of `tools.run_value_cycle_ab`, `_pb6_engagement_recovery_arm` or `run_annual_report` was running. Available memory was 20.8 GiB of 24.0.
- Unit `longjob-ab5-runa2c`, cgroup verified, through `background.launch_long_job`. The command is `legA.sh /var/tmp/se-ab5-out/runA2.json 22222,33333`, with no predecessor, and the log is `/var/tmp/se-ab5-out/runA2c.log`.
- **If this leg dies a third time, it is not retried.** It comes back as a question about the leg's memory: 10.2 GiB is not shareable on a 24 GiB box with a 6 GiB daemon cycling beside it.
