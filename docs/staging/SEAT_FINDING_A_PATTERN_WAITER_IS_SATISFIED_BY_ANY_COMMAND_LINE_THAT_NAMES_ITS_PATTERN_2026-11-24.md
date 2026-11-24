**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A pattern waiter is satisfied by any command line that names its pattern, so "the book ran" can mean "something mentioned the book"

Found by the delivery seat on 24 Nov 2026 while explaining land9's false FINISHED (claim
`the-msc-landing-is-re-armed-on-artefacts-not-process-names`). **Not fixed here:** the item says
not to fix `tools/wait_for.py` in this item.

## The instance

land9 (`/var/tmp/se-msc-keep/land9.sh`) waited with
`tools/wait_for.py --pattern "tools.run_annual_report" --start-grace 21600 --deadline 21600`.
For 12,904 s every heartbeat said `no process matches`. At 12,994 s (13:29:24Z) it returned
`FINISHED`, which needs `ever_present`. So one 15 s poll, at about 13:29:09Z, matched something, and
the next poll did not. No book ran:

- `docs/observability/sim-runner-log.md` shows `DEFERRED` at 13:24Z and again at 13:29Z.
- No `run_output_*.json` is newer than 20 Nov.

Two minutes later land9 saw rankq live and exited 7.

## The class, reproduced

`_is_probe_noise` drops only these lines:
- the `pgrep`/`grep` itself,
- a `claude` argv,
- lines where the pattern appears only inside a `wait_for` call.

Every other argv that the pattern hits counts as the subject. The pattern is also a **regex**, so
the `.` in `tools.run_annual_report` matches `/`, and `tools/run_annual_report.py` in any argv is a
hit. Reproduced on 24 Nov at about 16:15Z:

    ( sleep 3; bash -c 'sleep 15; : cat tools/run_annual_report.py' ) &
    python3 tools/wait_for.py --pattern "tools.run_annual_report" --start-grace 40 --deadline 60 --poll 2 --subject demo
    -> FINISHED after 18s waiting for demo (deadline 60s) -- no process matches 'tools.run_annual_report'   rc=0

A no-op shell whose argv only *mentions* the path was taken for the book. When it exited, the waiter
reported the book finished. The Bash tool runs every command as `bash -c '<command>'`. So any
session that runs `sed -n 1,40p tools/run_annual_report.py`, `git log -- tools/run_annual_report.py`
or a `pytest` naming such a path satisfies a waiter on the producer for as long as that command runs.

## Which process it was at 13:29Z: not established

What the record does and does not show:

- **Claude sessions:** no Claude session transcript has a tool call between 13:28:00Z and 13:29:30Z
  that names `annual_report`. All 18 transcripts written after 13:28Z were searched.
- **What was new in that window:**
  - a `surgical_land` gate from `/var/tmp/wt-w2p-shape`, 13:28:41Z to about 13:29:55Z, landing
    4f9e788e7. sim-runner's 13:29Z line shows its 2190 MB reservation.
  - `deploy-restart.service`, 13:28:50Z to 13:29:13Z. This runs about 97 times a day and was never
    seen before, so it is unlikely.
- **The gate:** none of the gate's hook lines names the pattern (the ratchet is
  `tools.annual_report_import_ratchet`, which the regex does not hit). The gate's test selection
  for that commit was not logged, so the gate is the leading candidate, but it is not proven.

The cause is the class, not this one process: **any** short-lived argv that names the path ends the
wait. The reproduction above shows that.

## land9's first silent end, 07:18Z: a different cause, established

The first arming was `setsid nohup /var/tmp/se-msc-keep/land9.sh` (06:36:48Z), run from the worker
`claude -p` session 5c612688. That session ran inside `worker-tick.service`. The session's last
entry is 07:17:59Z, and `worker-tick.service` finished at 07:18:01Z ("44min 18s wall clock").
`KillMode=control-group` then killed everything left in the unit's cgroup. `setsid` changes the
session and the process group, not the cgroup, so it was killed too.

This is the exact defect `background/launch_long_job.py`'s docstring exists for. The kill also
took the waiter's block-buffered stdout before any line was flushed, which is why the log holds only
"armed". The 09:52Z re-arm went through `launch_long_job` and survived. **The two deaths have
different causes.**

## What was done instead of fixing wait_for

land10 (`/var/tmp/se-msc-keep/land10.sh`, unit `longjob-land10-msc-replacement-win-artefact-waits`,
armed 16:22:09Z through `launch_long_job`) waits on artefacts only:

- **First wait:** rankq's unit is inactive and `/var/tmp/vtn-driver/grade_rankq.out` exists.
- **Second wait:** a `docs/reports/run_output_<sha>_*.json` that is newer than the arming stamp,
  whose `<sha>` descends from 31bf40e03, and whose size is stable over two polls.

The refusal to gate beside rankq or a book is kept. It now re-asks for up to 12 h before it refuses,
and its pattern is `-m tools[.]run_annual_report`.

Its probe was run against fake books. A non-descendant sha, an unknown sha, and a descendant older
than the arming were all refused, and a descendant written after arming was accepted. A missing
arming stamp now fails closed: the first probe found that `[ f -nt <missing> ]` is true.

`LAND10_DRY=1` reached the gate's door on origin 79fc1fbdb8. Every path applied cleanly, and the
census was clean apart from the declared drop (log: `/var/tmp/se-msc-keep/land10-dry.log`).

## What the fix would be (not done here)

Two directions are possible:
- make `--pattern` match only argv[0..1] of a process, or match a fixed string;
- retire `--pattern` waits on producers in favour of artefact waits.

The second is what land10 does. Either way, a mutation test for it is to start
`bash -c 'sleep 5; : <pattern>'` and assert the waiter does not report FINISHED.
