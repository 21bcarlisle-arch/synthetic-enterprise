**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The cadence lever was live and never once served: a deploy restart resets the pause

**Found:** 2026-09-04 ~15:50Z, delivery seat, isolated worktree, working the lane 0 throughput
direction. Pre-registered before measurement in
`SEAT_PREREGISTRATION_WHETHER_THE_CADENCE_LEVER_MADE_PENDING_ZERO_OBSERVABLE_OR_ONLY_REACHABLE_2026-09-04.md`;
two of its three predictions are refuted and the corrections are recorded there beside them.

**Status:** defect NAMED and FIXED in the same commit (`background/sim_runner.py`), which is why
this is RECORDED. What remains owed is stated at the foot and is not mine to smuggle in.

---

## The one-line result

`5952aaa4e` derived a 78-minute producer pause and landed it correctly. It has been live since
13:51Z and **has never once been served to completion**, because `sim-runner` is restarted on
deployment roughly every 30 minutes and the pause lived only in a process's own stack.

## The evidence, and it is exact

`journalctl --user -u sim-runner.service` `Started` stamps (converted to UTC) against the
`run_complete_*.md` marker names, which carry the run instant:

| restart (UTC) | marker |
|---|---|
| 13:22:27 | `run_complete_20260904T132228Z.md` |
| 13:58:47 | `run_complete_20260904T135847Z.md` |
| 14:28:48 | `run_complete_20260904T142849Z.md` |
| 14:48:46 | `run_complete_20260904T144846Z.md` |
| 15:18:47 | `run_complete_20260904T151847Z.md` |

**Five of five post-lever runs began at a restart instant, matching to the second.** Not one
began because a pause elapsed. `sim-runner-log.md` logs `Waiting 4685s before next run...` at
13:51, 14:27, 14:40, 15:17 and 15:48 — the constant is unquestionably live in the running process
— and the shortest of those sleeps was served for **1.7 minutes** before SIGTERM (the 15:17 wait,
replaced by a process `ps` dates to 15:18:47Z). Marker interarrival stayed at ~30 min (36, 30, 20,
30) against a derived period of 78.

`NRestarts=0` on the unit, so this is not systemd's `Restart=on-failure` — it is
`background/deploy_restart.py`, which restarts a daemon holding code that moved. In a tree where
several lanes commit per hour, that fires far more often than once per pause.

## Why this is the interesting shape rather than a bug

The restart is **correct** and is not what changes. It is the deployment step; a daemon serving
stale code is the defect it exists to prevent, and `unit_is_mid_work` already defers it away from
a running simulation. What was wrong is that **the producer's period was a property of process
lifetime rather than of the schedule.**

That gives the class, and it is worth more than the instance: **any pause longer than the
restart interval was unreachable by construction, whatever the constant said.** The lever could
have been derived perfectly — and it was — and still bought nothing. A constant nobody can ever
observe being honoured is indistinguishable from one that is wrong, and nothing in the tree could
tell the difference: the log line said `Waiting 4685s` every single cycle.

## What the fix is

`BETWEEN_RUN_PAUSE_SECONDS` is unchanged. The deadline is now persisted to
`.sim_next_run_not_before.json` **before** the sleep, and `main()` serves the remainder at
start-up. Restarts continue exactly as before; they no longer reset the cadence.

Fails toward running in every direction (absent, unreadable, corrupt, non-instant, already
passed → run now), because a wrong `0.0` costs one early run and a wrong large number costs a
producer that never runs again. The far-future case is clamped to one pause for the same reason.

The recorded instant is validated by `recorded_instant_seconds` — the one definition — not by
`isinstance(v, (int, float))`. That hand-roll is what admitted `0` and `True` into
`first_failure_ts` and rendered a 496,815-hour outage on the director's surface.

## The controls, and the one that was a tautology until mutation said so

Three mutations run with `python3 -B`. Two fired immediately. **The third survived**: replacing
`recorded_instant_seconds` with the `isinstance` hand-roll passed the whole suite.

The cause is worth recording. `0` and `True` yield `owed == 0.0` under *both* implementations —
the one definition rejects them as non-instants; the hand-roll accepts them as 1970 and then
calls the deadline "already passed". **Same number, opposite meanings.** A control asserting the
number could not distinguish them and was therefore asserting nothing. Re-keyed to the *reason*,
the mutation dies. The number was the tautology; the reason is the control.

## P2 REFUTED — `pending == 0` is observed, and the episode still cannot close

The prediction was that `pending == 0` would be unobservable at a ~1.6% duty. Wrong.
`pending_run_complete_markers()` returns **0** right now, with 1,516 markers archived; the
supersede-retirement sweep is keeping the queue empty and the direction's stated acceptance test
— *"the run queue is empty"* — **is met.**

The episode still does not close, and **the binding constraint has moved off cadence entirely**:

```
episode_clean_publishes: 0      last_clean_publish: null      episode_failures: 15
failures[].cause: behind_origin, gate_refusal, behind_origin
```

`record_publish_gate_success` is only reached by a publish that commits, and every cycle refuses
at the last step — *"origin/main is 3 commit(s) AHEAD of HEAD"* — after regenerating every
surface. So `pending == 0` is TRUE and **unrecordable**, which is the same shape as the defect
the previous lane 0 commit fixed on the proposal side, at a different seam.

**This is the next lever and it is not cadence.** Already filed as
`SEAT_FINDING_THE_PUBLISHER_CHECKS_BEHIND_ORIGIN_ONCE_AT_THE_END_OF_A_CYCLE_THE_TREE_OUTRUNS_FIVE_TIMES_OVER_2026-09-04.md`
— cited rather than duplicated. Every cycle's full compute is now discarded at the commit step,
which is precisely the waste the producer-side finding measured, moved downstream.

## Observed in passing, not actioned

1. **A transient `ImportError` in the live daemon.** At 15:48Z: *"publish-gate outcome recording
   failed (non-fatal): cannot import name `recorded_instant_seconds` from
   `background.episode_monotonic`"*. The name is present at line 145 in both HEAD and the shared
   tree, and the file's mtime is 15:48Z — another lane was rewriting it as the daemon imported
   it. A torn read of a source file under a live daemon, not a broken landing. It means
   publish-gate outcome recording is silently skipped whenever it happens.

   **ACTIONED 2026-09-04, delivery seat, and the observation above understated it.** "Non-fatal"
   is true of the run loop and false of the measurement: the outcome being routed is usually a
   FAILURE, so one that never arrives makes the episode read one failure SHORT of what happened —
   the under-reporting `episode_monotonic` exists to prevent, arriving by the one route that guard
   cannot see, because the guard is downstream of the import that failed.

   The repair is `background/publish_outcome_route.py`: a bounded retry (two attempts, 1s apart)
   over the torn import, keyed to `ImportError`/`SyntaxError` — the two shapes a half-written
   module takes — and to nothing else, because a detector that raises on real state will raise
   again a second later. A lost record is now logged as **LOST**, naming its consequence, rather
   than as "skipped" or "non-fatal", both of which read benign.

   **The interesting part is that the first draft of the fix was in the wrong file.** There were
   two byte-for-byte twins of this wrapper — `background_worker._record_publish_gate_outcome` and
   `sim_runner._record_publish_gate_outcome` — and I repaired the worker, which is *not* where the
   loss was observed. One requirement, two implementations, fixed in one and live in the other:
   this project's most expensive recurring shape, reproduced inside the repair for it, and caught
   only by re-reading the log line quoted above against the code I had just changed. Hence one
   module and a control that fails asymmetrically — mutate either wrapper back and that one's leg
   goes red while the other stays green. Controls:
   `tests/background/test_a_torn_import_lost_a_publish_outcome_silently.py`, twelve, six mutations
   run and fired.
2. **The refuted "TWO full suite runs" note still stands at `process_run_complete.py:301`.** The
   correction landed at line 370 for a *different* constant in the same file; the original claim
   was left uncorrected beside it. Owed, small, and deliberately not smuggled into this commit.

## What is owed next

- The `behind_origin` refusal — now the only thing between a drained queue and a closed episode.
- Observing the persisted pause actually hold across one restart (~78 min of wall clock; not
  verifiable inside this turn, and stated rather than claimed).
