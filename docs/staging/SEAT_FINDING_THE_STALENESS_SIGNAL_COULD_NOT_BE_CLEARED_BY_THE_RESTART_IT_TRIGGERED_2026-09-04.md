**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The staleness signal could not be cleared by the restart it triggered, so three daemons were killed every ten minutes for hours

**Found:** 2026-09-04, delivery seat, while checking the deployment reading the director asked for.
Reproduced from `journalctl` and the live artefact, not inferred.

---

## What happened

`background/boot_sha.changed_paths_since(sha)` is `git diff --name-only <boot_sha> --`: the daemon's
boot **commit** against the **working tree**. `deploy_restart.restart_plan` restarts every unit whose
resulting set is non-empty.

Three modules had carried **uncommitted** working-tree edits in the shared tree for 27.4 hours
(`background/head_red_register.py`, `background/gap_ledger_reconciler.py`,
`tools/couple_value_based_pricing.py`, mtime `1788415856`). They sit in the import closure of six
daemons. So six daemons were `stale`, and were restarted.

**A restart stamps `boot_sha := HEAD` and does not touch the working tree.** The diff therefore
returns the same three files the instant the daemon comes back up. The remedy cannot clear the
condition that triggers it, so the loop is permanent by construction rather than by timing:

```
2026-09-04T10:18:30  Stopped/Started deadmans-switch, naive-organ, staging-watcher
2026-09-04T10:28:31  Stopped/Started deadmans-switch, naive-organ, staging-watcher
2026-09-04T10:38:31  Stopped/Started deadmans-switch, naive-organ, staging-watcher
```

Ten minutes, on the dot. **`deadmans-switch` is this project's stall alarm** — the independent thing
that notices when the seat has stopped committing — and it had never been up for longer than ten
minutes. An alarm that is restarted more often than its own escalation thresholds (45 min BLOCKED,
90 min STALL) can never reach them. `NRestarts` is `0` for every unit, which is why nothing noticed:
a `systemctl restart` issued by another process does not increment systemd's own restart counter.

## The measurement error under it

A daemon imports its modules **off the disk** at start. A file whose bytes were last written 27.4
hours ago was already in that state when a process that started ten minutes ago loaded it. **That
process holds today's content and is not behind on it at all.** The subject was dated from the boot
*commit* when the thing being asked about is a *process*.

`changed_paths_since`'s docstring justifies including uncommitted edits, and is right to — but only
for edits that reached the disk *after* the process started, which it never checked.

## The same error, published to the reader

`unincorporated_for_s` is `max(now - mtime)` over that same set, so it inherited the false positives
and added one of its own. On the live feed at the time of writing:

- **Six of eleven rows published a time-behind larger than the row's own running age** — up to 27
  hours against processes ten minutes old. That is impossible under the meaning the column states
  ("the interval it has been running without this").
- **Six rows carried the identical figure `97646.4`, to the tenth of a second.** `max()` kept landing
  on `head_red_register.py`, which all six import. `staging-watcher` had exactly one changed module —
  that file — which is why its age *is* the shared value.

That is the **not-per-daemon defect `unincorporated_for_s`'s own docstring says it retired**, back by
a different route. It had stopped being a property of a commit and become a property of a *file*.
This is the third time this column has been wrong (field rename `b0bceffae`, subject mismatch
`1b98c8360`, and now its set), and each previous fix moved the defect rather than removing it,
because each fixed the *reducer* and none asked what the *set* was.

## What was done

`deploy_restart.unincorporated_since_start` dates the set from the process: keep only the changed
paths whose mtime on the loading disk is newer than `now - running_age_s`. Verdict and clock are
taken on that same set, preserving the property `1b98c8360` established. It fails closed in both
directions — an undatable process (no running age) drops nothing, and a path that will not stat is a
deletion and is kept. `predates_start` publishes what the dating removed, because a staleness set
that shrinks silently is the fail-open case.

**The loop-breaking property is structural, not numerical:** the condition is now one a restart can
actually clear, because after a restart the process start is newer than the file.

## Verified against the live world

Replayed on the shared tree's real mtimes and running ages (`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_DATING_STALENESS_FROM_PROCESS_START_ENDS_THE_RESTART_LOOP_2026-09-04.md`
carries the predictions, written first):

| daemon | before | after | why |
|---|---|---|---|
| `staging-watcher`, `supervisor` | RED | **green** | only ever held the 27.4h files |
| `deadmans-switch`, `naive-organ` | RED | RED | genuinely behind on `boot_sha.py`, **written 31s ago** by a live lane |
| `background-worker`, `sim-runner` | RED | RED | 4–5 of their files dropped as already-loaded; the rest are real |
| `worker-seat-manager` | RED | RED | up 10.8 days, module rewritten 60h ago — really behind |

The six identical values are gone. No row's time-behind exceeds its running age.

## Still open — filed, not fixed here

`unincorporated_for_s` **can return a negative number.** `daemon_deployment_report` samples `now =
time.time()` once and stats the files afterwards, so a file written in between has `mtime > now` and
the column publishes a negative age. I hit `-73.9` reproducibly while replaying against a stale
`now`, and `boot_sha.py` is being rewritten every few minutes by an active lane, so the live window
is small but open. It is **not fixed in this commit** because the obvious clamp to `0.0` would break
`test_the_time_column_cannot_disagree_with_the_verdict`'s invariant (`bool(time) == bool(verdict)`) —
a row would say "behind on 1 module" and "0m". Deciding between a floor, a `None`, and changing the
invariant is a separate judgement and deserves its own commit rather than being smuggled into this
one.
