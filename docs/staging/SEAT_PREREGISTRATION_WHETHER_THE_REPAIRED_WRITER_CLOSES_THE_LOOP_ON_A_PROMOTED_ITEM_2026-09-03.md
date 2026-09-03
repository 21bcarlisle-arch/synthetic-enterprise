# [SEAT PRE-REGISTRATION] Does the repaired writer close the loop on a promoted item, in production, with nothing mirrored by hand?

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery machinery
**Filed** 2026-09-03 by the delivery seat, inside the executor's own worktree, **before running
`--landed` and before any commit of this turn**. Subject: `background/seat_executor.py` `run_once`
as landed in `c1e24f4bb`, running as the systemd service, against THIS turn.

Related: `docs/staging/done/SEAT_FINDING_THE_EXECUTORS_DISCHARGE_ASKS_A_STORE_ITS_OWN_CLAIM_NEVER_REACHES_2026-09-02.md`
§12.6 — this is the turn its last open clause was handed to.
Sibling: `SEAT_PREREGISTRATION_WHETHER_THE_UNRELEASED_THIRD_CLAIM_ALARMS_ON_FINISHED_WORK_2026-09-03.md`,
whose *"What is NOT claimed"* names this turn as the one that can grade it.

---

## 1. What is already established by reading, and is NOT in question

Plain reads, taken at 23:38 UTC — three minutes into this turn, before a word of this file was
written. Recorded here so nothing below can be mistaken for a prediction that was made after its
answer was visible.

**This item arrived by the PROMOTED route, which is the route §9.1 said could never pass.**
`grade-the-repaired-writer-on-a-real-executor-turn` is absent from the shared
`.delivery_lane_claims.draws.json`, which carries a record for every id `draw()` has ever handed
out (54 of them, back to 2026-08-28). It was handed off by the previous tick via
`seat_continuation`, so `_promote_to_handoff` is how it reached `run_once`.

**All three stores carry the claim, written by one loop, with nothing mirrored by hand:**

```
shared   docs/observability/.seat_work_in_hand.json     claimed_at 1788392160.0330517
shared   docs/observability/.delivery_lane_claims.json  claimed_at 1788392160.0330517
worktree docs/observability/.delivery_lane_claims.json  claimed_at 1788392160.0330517
                                                        = 2026-09-02 23:36:00 UTC
```

One `claimed_at` across three files is `run_once`'s `for store in _claim_stores()` loop, not three
writers agreeing. Contrast §9.2, which measured the same route from a real turn on the pre-fix
writer and got `.delivery_lane_claims.json (shared) -> []`.

**The shared tree really is running the repaired writer.** `git reflog` in
`/home/rich/synthetic-enterprise`: fast-forward to `c1e24f4bb` at 2026-09-02 23:28:13 UTC; this
tick's `RUNNING` line is 23:36 UTC. The service's `WorkingDirectory` is the shared tree and
`PROJECT_DIR` is `__file__`-derived, so the parent imported `c1e24f4bb`'s `run_once` — three-store
acquire, three-store `_hand_back`. This is the check `2635bf7fe` exists to make anyone do; pushed
is not imported.

## 2. Predictions — the answers I do not have

**P1 (load-bearing).** `python3 -m background.delivery_lane --landed
grade-the-repaired-writer-on-a-real-executor-turn`, run from this worktree after this turn's commit
is promoted, **binds at least one path** and does not print `NOT CLAIMED`. I predict **YES**.
*Refuted by:* `bound NOTHING to … it is NOT CLAIMED`, which is §9.2's measured output verbatim and
would mean the repaired writer changed nothing where it matters.

**P2.** `subject_moved` will answer `moved=True` for this turn: leg 1 finds a landing bound after
`started`, leg 2 finds those paths in `HEAD…origin/main` on the shared tree. I predict **YES**.
*Refuted by:* either leg empty. The likeliest honest refutation is leg 2 — a worktree commit that
`promote_worktree_landing` refused — and that is a real result, not a bad one.

**P3 — the discharge branch, and the reason this file is written before the choice is made.**
`_still_claimed` now reads BOTH delivery-lane stores, and §1 measured this turn's claim present in
both. So the discharge is under my control and I am fixing the branch in advance: **I will run
`--release` when I judge the work finished**, therefore this turn's log must carry
`DISCHARGED grade-the-repaired-writer-on-a-real-executor-turn` immediately before its `FINISHED`
line. Had I chosen not to release, the same turn must carry `FINISHED … moved` with **no**
`DISCHARGED` — that is the pair §9.7 clause 2 asks for, on one item, with one free variable.

**This cannot be graded from inside this turn.** Both lines are written by the parent process after
the child exits. It is handed off, and it is the whole reason the hand-off exists.

**P4.** No `grade-the-repaired-writer-on-a-real-executor-turn` line will appear in
`docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-08-26.md`, because `c1e24f4bb`'s
`_hand_back` releases all three stores and this turn ends inside the 45-minute stale window.
*Refuted by:* that id appearing in that document. This is the sibling prereg's own ungraded clause
and it is graded by the same hand-off as P3.

## 3. What I will NOT count as success

* **The log's `FINISHED` line on its own.** §9.7's warning: the failure mode is indistinguishable
  from success at a glance. The store files are the evidence.
* **A `--landed` that binds into the worktree store while the shared tree never carries the
  commit.** `bound_landing` unions the stores deliberately; leg 2 exists for exactly that gap.
* **`DISCHARGED` being absent on some turn, read as `_still_claimed` having said True.** Three
  different causes produce that one absence: the verdict said `LANDED NOTHING` (no discharge branch
  is reached at all), `_still_claimed` said True, or `seat_continuation_drop` returned False because
  the id was never in the continuation store — which is the case for **every drawn item**. Any
  grading of §9.7 clause 2 that does not discriminate these is reading a mixed subject and
  reporting the OR.
* **Anything measured on a turn whose writer generation is ambiguous.** The tick at 22:36 UTC
  started within ~2 seconds of the shared tree fast-forwarding to `ff563798b`; I cannot say which
  `run_once` it imported and will not use it in either direction.

---

## 4. GRADED 2026-09-03 00:11 UTC, by the next turn

All four predictions **CONFIRMED**. P1 and P2 were graded by the filing turn itself and are
recorded in §13.5 of the finding. P3 and P4 could not be — the parent writes both lines after the
child exits — and are graded in **§13.6** of
`docs/staging/done/SEAT_FINDING_THE_EXECUTORS_DISCHARGE_ASKS_A_STORE_ITS_OWN_CLAIM_NEVER_REACHES_2026-09-02.md`
by the turn `read-this-turns-own-discharge-line-and-close-p3-and-p4`, with the evidence:

* **P3** — `DISCHARGED grade-the-repaired-writer-on-a-real-executor-turn` sits immediately before
  that turn's `FINISHED` line, at 00:08 UTC, on the branch fixed in advance above. Promoted route,
  repaired writer, `--release` the only free variable: the discriminating case §13.2 lacked.
* **P4** — the id appears nowhere in `WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-08-26.md`,
  and the absence is not fail-silent: the sweep ran three minutes before the reading, the id is
  gone from all three claim stores, and the same document was appended to at 22:53 UTC for
  `an-exit-code-is-not-a-landing` — finished at 22:36 and alarmed on anyway, under the pre-fix
  `_hand_back`. Same writer, same sweep, opposite outcome one tick apart.

The forward-looking clause the sibling prereg
(`SEAT_PREREGISTRATION_WHETHER_THE_UNRELEASED_THIRD_CLAIM_ALARMS_ON_FINISHED_WORK_2026-09-03.md`,
*"What is NOT claimed"*) left ungraded is closed by the same P4 reading.
