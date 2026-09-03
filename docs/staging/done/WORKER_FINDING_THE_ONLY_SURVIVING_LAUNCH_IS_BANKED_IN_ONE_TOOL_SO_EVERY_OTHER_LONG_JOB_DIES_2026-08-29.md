**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `A48_enterprise_value_is_the_method_not_the_book`

# WORKER FINDING — the launch that survives a tick is banked inside one tool, so the arms re-run has now died twice and two pre-registrations are ungradeable

**Found:** 2026-08-29 13:52–14:05Z, working the Lane 0 delivery item "land the arms code and re-run
the comparison on today's book". Incidental to that item's stated scope and it is what blocks it.

## The doorbell's premise was already false, and that is the small half

The item's part (1) said `tools/generate_value_arms_data.py` and
`site/test_the_baseline_comparison_reaches_the_reader.py` were "modified and uncommitted since
18:28Z yesterday" and must be landed first. **Both paths are clean.** `_market_reaction()` is in
`d123831b9`; the 17.89% sample sentence and its four controls are in `9c626f05d`. Part (4) is
landed too. Nothing to land, nothing to revert — the doorbell is quoting a tree state that two
commits have already reversed.

So the whole of this item reduced to parts (2) and (3): re-run both legs on one clock, and grade
the pre-registration. Neither has been possible for two days, for a reason nobody has written down.

## Observed, with evidence

**The re-run has now died twice, mid-flight, leaving no artefact and no error.**

```
$ head -1 docs/observability/three_arm_sourced_cost_run.log      # the 2026-08-28 pre-registered run
START 2026-08-28T20:01:29Z pid=3268202 pgid=3268202 sess=3268202
$ tail -1 docs/observability/three_arm_sourced_cost_run.log | cat -A | tail -c 60
 ... 3,174,200 settlement periods processed (latest: 2019-07-12 period 44   <-- no trailing $
$ grep -c Traceback docs/observability/three_arm_sourced_cost_run.log
0

$ head -1 docs/observability/arms_rerun_20260829.log             # the 2026-08-29 replacement run
START 2026-08-29T11:53:54Z pid=294764 pgid=294764
$ tail -1 docs/observability/arms_rerun_20260829.log | cat -A | tail -c 60
 ... 10,960,900 settlement periods processed (latest: 2024-05-14 period 8   <-- no trailing $
$ grep -c Traceback docs/observability/arms_rerun_20260829.log
0
$ ls docs/observability/value_cycle_ab_s1_*20260829*.json
ls: No such file or directory
```

Both end on a **truncated line** — killed mid-write, not crashed. Neither wrote its artefact.
`value_cycle_ab_s1_three_arm_sourced.json` has never existed in the tree or in any commit.

**It is not OOM, and I nearly filed that it was.** `dmesg` shows 64 kills today, all `python3`, all
at a byte-identical `anon-rss:523136kB`, all `oom_score_adj:200`. That regularity is the tell: they
belong to `oom_memcg=.../ops2-peak-kill-selftest-<pid>.scope` — a self-test that allocates until it
is killed, on purpose, hourly. The arms PIDs appear in `dmesg` zero times, and
`resource_headroom.sample()` reports 17.4 GB available of 24.0 GB. **A repeating alarm that is
someone's deliberate self-test is a very good way to get the wrong cause**, and the only thing that
stopped it here was checking whether the victim PID was the one I cared about.

## The cause, and it is already written down in this repository

The tick runs inside a systemd service, and that service kills by cgroup:

```
$ cat /proc/self/cgroup
0::/user.slice/user-1000.slice/user@1000.service/app.slice/worker-tick.service
$ systemctl --user show worker-tick.service -p KillMode -p Type -p Delegate
Type=oneshot
KillMode=control-group
Delegate=no
```

`KillMode=control-group` on a `oneshot` means: when the tick finishes, systemd SIGTERMs **every
process in the cgroup**. `setsid` does not escape a cgroup. It changes the session and the process
group, and the cgroup is neither. That is why the 2026-08-28 run recorded
`pid==pgid==sess=3268202` — a textbook POSIX detach, demonstrably held — **and died anyway.**

`tools/measure_publish_gate_subject_cost.py:216-232` says this, in the repository, in prose,
already:

> INFERRED (R9 …): what survives a process-GROUP kill does not survive a killer that enumerates a
> launcher's DESCENDANTS. `start_new_session` changes the session and group; it does not change the
> child's `ppid` … The reparenting is the point: `systemd-run` hands the job to the user manager, so
> the child's parent is init and no descendant-walk from any tick can reach it.

That file escalated to `--systemd` / `_systemd_run_argv` on 2026-08-11 and it has worked since.

## The part that is worth the finding

**The fix is real, correct, and reachable from exactly one module.**

```
$ grep -rln "systemd-run" tools/ background/ --include=*.py --include=*.sh
tools/measure_publish_gate_subject_cost.py
```

One caller, for one fixed unit name (`MEASUREMENT_UNIT_NAME = "publish-gate-subject-cost"`), for one
measurement. There is no shared "run this long job so it outlives the tick" launcher, so every
*other* long job is launched by whatever the tick types that day — and what a tick types is
`setsid`, because `setsid` is the folk answer and it is the one written in
`WORKER_FINDING_THE_DETACH_THAT_FIXED_THE_DEATH_IS_NOT_IN_THE_REPO_2026-08-10` as the
recommendation that closed it.

**This is that same finding, recurring, one level up.** 2026-08-10 said: the detach that fixed the
death is not in the repo. It was then put in the repo — *in one tool*. The class was closed on an
instance. A generalisable launcher was never the subject, so the next long job in a different lane
inherited none of it, and the failure came back wearing the same clothes: a bounded tick, a
~2-hour job, a truncated log, no artefact, no error, and a pre-registration that cannot be graded.

**Its cost is on the live page right now.** `site/data/value_arms.json` carries
`run_generated_at: 2026-08-28T14:08:48Z` against a noise floor measured `2026-08-27T23:32:17Z` —
two clocks, on a book of 210 settled accounts that today's campaign no longer produces — and the
reason is not that anyone chose to leave it there. It is that the instrument that would replace it
has been killed at the tick boundary twice.

## What I did

**Launched it through the mechanism the repo already knows about**, rather than a third `setsid`:

```
$ systemd-run --user --unit=arms-rerun-20260829 tools/run_arms_rerun_detached.sh
$ systemctl --user show arms-rerun-20260829.service -p ActiveState -p MainPID
ActiveState=active
MainPID=438742
   CGroup: /user.slice/…/app.slice/arms-rerun-20260829.service   <-- NOT worker-tick.service
```

Both legs are in one process in that script, deliberately: the `staleness_caveat` /`clock_caveat`
defect is two artefacts on two clocks, and two separately-launched legs is how that happens. It
will outlive this tick, which is the whole point and is the one claim here I could not verify
inside the tick that makes it — **the artefacts are what settle it, and their absence at the next
tick would refute me.**

**Did not** re-run anything over the published artefacts, and did not grade the pre-registration:
there is still nothing to grade it against, and the honest STATUS beside the prediction says so.

## Recommendation — one mechanism, not one more caller

Give the repo a **shared** detached-launch helper (`tools/detached_launch.py`, or lift
`_systemd_run_argv` out of `measure_publish_gate_subject_cost` into something importable) that takes
a unit name and an argv and returns the pid, and make `run_value_cycle_ab` and the other long jobs
call it. R15 both ways, and **key the control to the property, not to today's answer**: the test
that matters is *a child launched through the helper survives its launcher's cgroup being stopped*,
mutated by launching the same child with `start_new_session=True` and asserting it does **not**
survive. A test that kills by `killpg` proves the wrong proposition — it is green today and the runs
still died, which is precisely the shape `CONTROLS_THAT_CANNOT_FAIL.md` is about.

`tools/run_arms_rerun_detached.sh` is deliberately a thin, single-purpose script and should be
**deleted by whoever builds the helper**. It is the increment that unblocks today's measurement, not
the mechanism — filing it as the mechanism would be closing this class on an instance for the second
time.
