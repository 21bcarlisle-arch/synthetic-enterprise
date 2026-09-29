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
