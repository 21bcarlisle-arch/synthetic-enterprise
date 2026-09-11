**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — a shared launcher so a long job stops rediscovering the cgroup by dying)

# RESULT — the launch and its record are now one call, and censusing for the shape found a live instance in the publisher

Discharges item 1 of "what is still owed" in
`docs/staging/records/SEAT_FINDING_THE_RETAKE_DIED_A_THIRD_TIME_AND_THE_KILLER_WAS_NEVER_THE_SESSION_IT_IS_THE_TICKS_CGROUP_2026-09-08.md`,
which asked for exactly this and named the register to delete afterwards. That finding stands
unedited; items 2 (no checkpointing) and 3 (nothing notices a death) are **not** discharged here —
3 was already answered by `background/launch_liveness.py` + the deadman, and this closes the gap
between them.

**Falsifiers:** `tests/background/test_launch_long_job.py::test_a_launch_whose_record_cannot_be_written_is_stopped`,
`tests/background/test_launch_long_job.py::test_a_real_launch_detaches_and_logs_both_streams`,
`tests/background/test_the_out_of_band_refresh_outlives_the_publisher.py::test_the_stale_refresh_goes_through_the_one_launcher`.

## What was built

`background/launch_long_job.py`. It launches into a transient `systemd-run --user` unit and writes
the `launch_liveness` record **in the same call**. Landed `0b3efd0a7`.

The second half is the whole point, and it is the vacuity the drawn item named:
`launch_liveness.record()` existed and `deadmans_switch._check_launch_liveness` re-asked it on a
timer, but nothing PERFORMED a launch — so writing the record stayed something the launcher had to
remember, and a live floor leg ran unrecorded for 35 minutes after the mechanism existed. Here
there is no `--no-record` flag to forget: **a job whose record could not be written is stopped.**
That trade is deliberate and costly (a failed JSON write can kill a healthy long run). It is still
right: running-and-invisible is the state that cost four launches, and a relaunch is one command.

## The census found a live instance, and it was not in /var/tmp

Having built the thing, I greped the committed tree for the shape rather than assuming the five
throwaway scripts were the whole population. `background/process_run_complete.py` spawned the
weekly frozen-policy baseline refresh — a multi-minute decade replay — like this:

```python
proc = subprocess.Popen([sys.executable, "-m", "tools.run_frozen_baseline", "--if-stale"],
                        stdout=DEVNULL, stderr=DEVNULL, start_new_session=True)
# "Detached via start_new_session so it outlives this publish process"
```

That comment is the claim three deaths refuted. Every user unit on this machine reports
`KillMode=control-group` (checked, 2026-09-08: all of `background-worker`, `deadmans-switch`,
`worker-tick`, `reconcile-watch`, `delivery-seat` and the rest). `setsid` changes the session and
the process group; a cgroup is neither. **Both streams went to `DEVNULL`, so a death and a success
left the identical trace** — which is why this has never been noticed and why I cannot say how
often it has died. It now goes through the launcher.

**A green control was pinning the defect.** `test_spawns_detached_when_stale_and_never_runs_inline`
ended `assert kwargs.get("start_new_session") is True, "must be detached to outlive publish"`. It
was keyed to today's answer rather than to the property, so it went red the moment the code became
more honest. Renamed, rewritten against the route, and its real subject (never inline) kept.

## What the door test caught, on its first run

Nine tests against a fake runner were green on top of a launcher that could not read a live unit's
state at all. `_show` was built with `-p=ActiveState`; `systemctl show` **accepts that form, prints
nothing, and exits 0**. So every property read came back empty with a healthy rc, `name_is_held`
read the empty answer as "the name is free", and the fixed unit name — the one protection systemd
gives for free — would have failed open and started a second copy of a long job beside a running
one. The fake was more permissive than its subject (it matched any argv *containing* the property
name), which is how nine green tests sat on a fail-open. Both fixed: the real form, and a fake that
answers only what the real thing answers.

## The register that was deleted

Five bespoke launch scripts in `/var/tmp`, confirmed not running, each having learned a different
subset of one lesson:

| script | what it had | what it lacked |
|---|---|---|
| `relaunch_value_cycle_ab_current_book_2026-09-07.sh` | `-u`, both streams to one file, rc file | the unit — launched with `setsid`, died |
| `relaunch_value_cycle_ab_current_book_2026-09-08.sh` | the transient unit, cgroup line in the log | any record a later reader could re-ask |
| `relaunch_value_cycle_floor_2026-09-08.sh` | the unit, `PYTHONUNBUFFERED` | the record — this is the leg that ran unrecorded for 35 min |
| `run_fuel_mix_poison_d7eb36a0b901_v2.sh` | the unit, START/END lines | the record; its own pristine-restore trap is job-specific and not a launcher concern |
| `direction_battery_run.sh` | the unit | the log properties, the record, everything else |

`ab_leg_id_fixed.sh`, `red_baseline_run.sh`, `census_run2_launch.sh` and the two earlier fuel-mix
scripts are **left alone and are not launchers** — they hand-roll START/END logging but were run
inline or under someone else's unit. Saying so rather than deleting nine files and calling it five.

## What this does not claim

**It does not claim every long job now goes through it.** Two committed sites still detach by
session and were left: `background/worker_tick.py` (blocks until the child exits, so it is
*supposed* to live inside the tick) and `tools/measure_publish_gate_subject_cost.py`'s `--detach`
fallback (documented as the inferior route beside its own `--systemd`). Neither is a defect. I did
**not** build an architecture control forbidding a second way, on the `wait_for` model: the honest
allowlist for it would have been most of the census above, and a control whose exemptions are the
population is not a control. The one-leg version is that the tree now has a launcher good enough
that writing a sixth shell script is more work than calling it.

**It does not claim the publisher's refresh now completes.** It claims it is launched into a cgroup
the publisher's teardown cannot reach, and that a death is now recorded rather than silent. Whether
it succeeds is a thing the next `launch_liveness --check` will say, and it is the first time that
question has been askable.

## The trap this nearly set, recorded because it was nearly missed

The first draft of the module's docstring cited the tool it generalises by path. The capability
index reads a path in prose as a caller edge, so that citation made an unrelated orphan read as
reachable and the `--freeze` silently **deleted its row** from the ratchet's floor — arming a red in
someone else's lane the next time anyone reworded a comment. Caught by diffing the baseline both
directions rather than reading the "froze N orphans" line. The provenance is still in the docstring;
the path is not.
