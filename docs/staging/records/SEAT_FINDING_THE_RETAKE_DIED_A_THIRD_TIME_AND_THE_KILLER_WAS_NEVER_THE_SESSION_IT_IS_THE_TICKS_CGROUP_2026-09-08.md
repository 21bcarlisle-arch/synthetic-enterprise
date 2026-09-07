**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the level/selection re-take died in silence and its preregistration says it is in flight)

# FINDING — the re-take died a third time, and the killer was never the session; it is the tick's cgroup

Beside `SEAT_PREREGISTRATION_WHAT_THE_CURRENT_BOOK_RETAKE_OF_THE_LEVEL_SELECTION_SPLIT_CAN_AND_CANNOT_SETTLE_2026-09-07.md`
and `SEAT_CORRECTION_THE_FIRST_RETAKE_LEFT_NO_EVIDENCE_IT_SURVIVED_ITS_OWN_LAUNCH_AND_THE_RELAUNCH_IS_PINNED_TO_A_LATER_SHA_2026-09-07.md`.
Both stand; neither is edited. This records what happened to the relaunch they describe.

## The relaunch those documents call live is dead

The 09-07 correction ends by describing a relaunch at 22:31 as running, and it was — a waiter
watched it for a full 300 seconds and recorded a live pid at 22:36:36. It died anyway.

| evidence | value |
|---|---|
| launched | 22:31:36, pid 3419044, child python 3419050, sha `ab6f36d10` |
| waiter verdict | live at 60/120/180/240/300s — the launch was *verified* by the standard this lane set |
| log last written | **22:37:33**, 17,195 bytes, ~6 minutes in |
| `…_relaunch.rc` | **never written** |
| artefact `…_2026-09-07.json` | **never written** |
| observed at | 00:29, both pids gone |

**The rc file is the load-bearing absence.** The wrapper was `set -u`, not `set -e`: on any exit of
the python child it reaches `echo "END …"` and writes the rc. The log contains **no `END` line**, so
the wrapper died *while python was still running*. Parent and child went together. That is a group
kill from outside, not a module failing.

## The three causes this lane had already queued up, and why each is refuted

| candidate | refuted by |
|---|---|
| OOM | `dmesg -T \| grep -c 3419050` → **0**. Every OOM line on this box names an `ops2-peak-kill-selftest-<pid>.scope`, a deliberate self-test that kills its own python3 at a byte-identical `anon-rss:523136kB`. None ever held our pid. |
| the 90-minute worktree reaper | `fork_reconciler.MIN_REAP_AGE_SECONDS` reaps **directories**, never processes, and its stated invariant never reaps a **locked** worktree. `/var/tmp/se-valuearms-20260907` is locked and still on disk. |
| the module raising | zero `Traceback` in 17KB of captured stderr; the log ends on a clean line boundary mid-enumeration. |

## The cause, and it is not a new discovery — it is a recorded one that this launch did not apply

```
$ cat /proc/self/cgroup            # inside this scheduled tick
0::/user.slice/user-1000.slice/user@1000.service/app.slice/worker-tick.service
```

The tick is a systemd oneshot with `KillMode=control-group`: when it finishes, systemd kills
**every process in its cgroup**. `setsid` changes the **session** and the **process group**. A
cgroup is neither. So the 22:31 launch's careful `pid=pgid=3419044` proves a detach that is
irrelevant to the actual killer, and the signature — log ending mid-enumeration, no `END rc=`, no
traceback, no OOM record naming the pid — is the documented cgroup-kill signature, matched on all
four legs.

**This is the third death of the same job to the same cause, and the second time the fix was
already known.** The mechanism, the diagnostic signature and the remedy were all recorded after the
fifth and sixth deaths of a *different* job on 2026-08-29, and again from the delivery seat's own
cgroup on 2026-09-06. Each relaunch since has correctly fixed the thing the *previous* death
exposed — buffering, then stream capture, then an rc file — and re-bought the same killer, because
**the launcher was never the subject of the fix.**

## Why the instrumentation that was supposed to diagnose this could not

The 09-07 wrapper's rc file was designed to tell "gone" from "gone with rc=137". It cannot: a
SIGKILL to the cgroup takes the wrapper too, so the rc file is absent in *exactly* the case it was
built to describe. **An exit-status file written by the process being killed cannot report its own
kill.** The verdict has to come from something outside the cgroup — which systemd already holds and
was never asked for.

## What was done

Relaunched at **00:32:23** under a transient user unit, which reparents the job to the user manager
and out of the tick's cgroup:

```
systemd-run --user --unit=value-cycle-ab-current-book \
  /var/tmp/relaunch_value_cycle_ab_current_book_2026-09-08.sh
```

| | |
|---|---|
| pinned to | `04361d6c7` — HEAD at relaunch, repinned from `ab6f36d10` and recorded here |
| tree | `/var/tmp/se-valuearms-20260907` (locked) |
| log / rc / artefact | `/var/tmp/value_cycle_ab_current_book_2026-09-08.{log,rc,json}` — all outside both trees |

**The control is keyed to the property, not to a live pid**, because a live pid is precisely what
the last two launches had while they were about to be killed:

```
$ cat /proc/3661620/cgroup
0::/user.slice/user-1000.slice/user@1000.service/app.slice/value-cycle-ab-current-book.service
```

Its own cgroup, not `worker-tick.service`. The child python (3661631) is in it too.

`--collect` is deliberately **not** passed. It would garbage-collect the unit on exit, discarding
the exit record. Left uncollected, systemd holds the verdict three deaths could not produce:
`systemctl --user show value-cycle-ab-current-book.service -p Result -p ExecMainStatus`.

## What is still owed, and it is not this run

1. **There is still no shared launcher.** `grep -rln systemd-run tools/ background/` returns
   bespoke sites, and this turn wrote a fourth script in `/var/tmp`. Every long job re-invents the
   launch and re-discovers the cgroup by dying. The one-leg fix is a helper that launches into a
   transient unit and returns the unit name; the register to delete afterwards is the sequence of
   per-job shell scripts in `/var/tmp`.
2. **This job has no checkpointing.** It writes its artefact once, at the end, so each death
   re-buys the whole run. Three deaths have now cost roughly five hours of wall-clock for zero
   figures. A run that banked partial state would have made each death cheap.
3. **No mechanism anywhere can notice a detached run has died.** The prereg asserted "the run is in
   flight" for six hours after its subject was a corpse, and the only reason it was caught is that
   a human-written doorbell sent a tick to look. That is the standing defect this lane keeps
   re-encountering from a new direction.

## What this does not claim

Nothing about level versus selection. The prereg's four predictions remain unread and unrefuted —
no artefact has ever existed. This finding is about the launcher, and the run it describes was
alive when this was written, which is a claim with a five-minute proof behind it and no more.
