# Prereg: the lineage-keyed decided-differently sign on four unseen seeds

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Item:** `ab5-preregister-lineage-keyed-d-on-unseen-seeds`

## Why this exists

Increment 3 of `records/SEAT_RESULT_THE_DECIDED_DIFFERENTLY_SIGN_OVER_FIVE_SEEDS_ON_ONE_WEATHER_STORE_2026-09-29.md` answered the pre-registered D: **not distinguishable** (3/5 positive, t-CI [−£579, +£1,522]). Both negative seeds (22222 and 44444) are seeds where the value arm's price churned C5, and C5's gain moved to its home-move successor `C5_2`, which sits outside a by-account key. When the successor is folded into its predecessor, all five seeds are positive. That fold was keyed after seeing 44444, so it is a lead and not a grade. This prereg grades it on seeds the ab5 record has never seen.

The question it answers: **on what the per-customer arm decided differently from flat rules, does it make more money, with a decision's consequences followed through the home move it caused?**

## When, and on what

- **Written:** 2026-09-29 ~23:58Z, delivery seat, before launch. No output from any seed below exists.
- **Code:** the same pin as ab5, `/var/tmp/se-ab5-b79e2c0e8`, which is detached at `b79e2c0e8` and `git worktree lock`ed. `legA.sh` (sha256 `a3703047…203b`, unchanged) refuses to run unless `git diff b79e2c0e8 -- . ':!docs'` is empty and `weather_store_digest()` equals `e11451b5…d242`. Only the seed changes between this family and the graded five, which is the point.
- **Seeds (unseen):** 55555, 66666, 77777, 99999. None of them is 11111, 22222, 33333, 44444 or 88888.
- **Shape:** one unit, `/var/tmp/se-ab5-out/legsL.sh` (sha256 `44b547f2…57ca`). It waits on the PB6 EH-2 arms (pid 1677297, `arms.sh`, three serial arms that started 23:51Z) through `tools.wait_for` with the 6h ceiling that tool allows. Then it runs two 2-seed legs, strictly one after the other: `55555,66666` writes `runL1.json` and `77777,99999` writes `runL2.json`. Each leg has two seeds because `noise_floor` refuses a one-seed leg (runA2's death). The expected cost is ~93 min per seed and an 11.5 GiB peak, so about 6h10m after the arms finish.
- **Grader:** `/var/tmp/se-ab5-out/grade_lineage.py` (sha256 `7638f037…6ecc`), written and run on the five seen seeds before launch. The graded invocation is `grade_lineage.py runL1.json runL2.json`, which reads the unseen seeds only.

## Definitions (D_lin)

- **Lineage root.** A home-move successor joins the account named by its `successor_of`. The source is the artefact's field if present. Otherwise it is `saas.customers.SUCCESSOR_CUSTOMERS` read from the **pinned** worktree (C1_2…C6_2 → C1…C6). The chain is followed to its root.
- A lineage's difference is the sum of `value_arm_net − level_arm_net` over its members.
- A lineage is **DECIDED** if any member has `decided_differently > 0`. It is **ROSTER-ONLY** if it is not decided and any member appears in one arm's log only. Otherwise it is **A**.
- **D_lin** = the sum over DECIDED lineages, excluding PROS-2016-0098's lineage. That exclusion is the same one the ab5 prereg made, for the same reason: 0098's churn roll is a two-state switch.

**Reference values on the SEEN seeds (not a grade; they are what the predictions are calibrated from).** The values are: 11111 +£1,110.19, 22222 +£1,004.21, 33333 +£1,038.66, 44444 +£784.65, 88888 +£1,110.66. Mean +£1,009.68, sd £133.98. The lineage key differs from increment 3's roster-only fold by about £1 per seed, because it also folds `C3_2` (which was in A) into C3 (which is in D). ROSTER-ONLY lineages number n=0 on every seen seed, and A_lin is within ±£3.10.

## Predictions (fixed before launch)

| id | line | prediction | refuted if |
|---|---|---|---|
| **L1** | D_lin on each unseen seed | positive on each, within +£600 to +£1,300 | any seed ≤ £0 (sign), or any seed outside the band (size) |
| **L2** | seed-level, the four unseen seeds | **95% t-CI excludes zero**, and the mean falls within +£800 to +£1,200 | CI includes zero, or mean outside the band |
| **L3** | A_lin on each seed | within ±£25 | \|A_lin\| > £25 on any seed. **\|A_lin\| > £100 refutes the key**: something moved where nothing was decided |
| **L4** | ROSTER-ONLY lineages | n=0 on every seed | any roster-only lineage carries more than £100 |
| L5 (context) | how many seeds land in the churned-C5 state | 1–2 of 4 (2/5 seen) | not graded |
| L6 (context) | 0098's switch state | mixed | not graded |

**Plain answer rule.** If L1's sign leg and L2's CI leg both hold, the answer is **yes**: on what it decided differently, the per-customer arm beats flat rules at this pin, on unseen seeds, by about £1,000 over the book's life. If either fails, the answer is **we cannot say**. A seed-level exact sign test on four seeds cannot go below p=0.125. So a 4/4 is reported with that p beside it, and the t-CI (the determinism was shown in increment 3: 33333 replicated on 0 of 164 accounts different) is what carries the grade.

**Confidence, stated so it can be wrong:** L1 sign ~80% (the four unseen seeds all positive); L2 ~85%; L3 ~90%; L4 ~75%. The live risk to L4 is a lineage whose predecessor is not decided differently but whose successor is in one log only. The key's reading of that case is "roster-only", and on the seen seeds it has not happened.

**What would make this prereg the wrong test.** If a new seed shows a DIFFERENT account whose decision's consequence escapes by some route other than a home move (e.g. a debt sale or a re-acquisition under a new id), that is not a lineage and D_lin will not catch it. It would show as L4 or L3 failing. Name it; do not re-key after the fact.

## Launch record

- **First launch at 00:00:12Z refused itself**, before any seed ran: `wait_for` refuses a deadline over 21,600 s, and the wrapper asked for 43,200. The log is kept as `runL.refused1.log`. The deadline was set to 21,600; nothing else changed. If the three PB6 arms outlast 6h, the wait refuses again (exit 91) and runs nothing.
- **Launched 2026-09-30T00:00:28Z** as unit `longjob-ab5-lineage-unseen` through `background.launch_long_job`, in a cgroup of its own (verified). It was admitted with 10,198 MB resident + 11,800 MB declared peak = 21,998 of 23,008 MB. The log is `/var/tmp/se-ab5-out/runL.log`, the artefacts are `runL1.json` and `runL2.json`, and the liveness claim is recorded. At launch the log reads `WAITING for PB6 EH-2 arms pid 1677297`, the unit's MainPID is 2141363, and it is waiting on the PB6 arms pid 1677297 (null arm running; planted and head still to come).
- **Known exposure, not fixed here:** `sim-runner`'s annual report cycles to ~6 GiB and is not a predecessor. That co-residence is what killed runa2b. If a leg dies of OOM, its seed pair is relaunched once and the finding goes to the admission, not to this prereg.
- **Grading** is handed on through `seat_continuation` for when `runL2.json` exists. Expect it about 6h10m after the arms finish.
