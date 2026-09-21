**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [WORKER] The worker did not die — the box froze, and systemd's own wall clock is the witness

Focus one of the lane-0 item `a-declared-daemon-that-is-absent-must-be-named-as-absent` was:
*"restart `background/background_worker.py` and record in the staging root what its last log line
was and how long it had been dead."* The restart was not needed and the diagnosis in the drawn item
is wrong in mechanism. Both are recorded here, because the remedy that follows from "a daemon died"
is not the remedy that follows from what actually happened.

## What was asked for: the last log line, and how long

Last line `background-worker.service` wrote, `journalctl --user -u background-worker.service`:

```
2026-09-20T17:31:18+01:00  - [2026-09-20 16:31 UTC] [process_run] Publish STANDING RED -- 3 test(s)
  have now refused the publisher 2+ cycles with no landing between: [three site/ here-relative
  pointer tests]. Retrying will not clear these; they are drawn as work in
  docs/staging/reference/PUBLISH_STANDING_RED_REGISTER.md.
```

Next line it wrote: `2026-09-21T08:13:24+01:00`. **Silence: 14h42m.**

The drawn item's "died at 16:31 yesterday" is the UTC stamp inside that line, and it is the right
instant. It is the *cause* that is wrong.

## The worker was not absent, and it was not singled out

It was never restarted by hand in this turn: the unit was already `active (running)` when the turn
opened, and `deploy_restart` had cycled it at 08:13:21 and again at 09:03:21 on its ordinary
ten-minute cadence.

The silence is not the worker's. **The entire user journal — every unit, not one — has zero entries
between 17:31:18 and 08:09:36.** `--since 2026-09-20 17:40 --until 2026-09-21 08:10` over
`journalctl --user` with no unit filter returns nothing. No timer fired. `delivery-seat`,
`daily-self-note`, `head-green-census`, `edge-traffic-capture` and `bill-validation` all resumed
together at 08:09:36, as a boot-like burst.

## The witness: a ten-minute wall clock across a fifteen-hour calendar

`background-worker.service` was `Started` at 17:27:04 and `Stopped` at 08:13:21 — a calendar span
of **14h46m17s**. systemd's own accounting for that same instance:

```
background-worker.service: Consumed 3min 17.608s CPU time over 10min 2.976s wall clock time,
                           1.5G memory peak.
```

`naive-organ`, `staging-watcher` and `supervisor` each report the same shape: `over 10min 02.9s
wall clock time`, all stopped in the same second.

systemd measures that "wall clock" from `CLOCK_MONOTONIC`. **Monotonic advanced 10m03s while the
calendar advanced 14h46m: 14h36m14s of monotonic time did not happen.** That is a suspended VM, not
a stopped process. This is WSL2 on Windows; the host slept and the guest froze with it. Every
declared daemon was frozen mid-instruction and resumed in place — which is why they all stopped in
the same second when `deploy_restart` next ran, and why none of them logged a death.

`uptime -s` still reports a boot of 2026-09-16 04:24:49 and `--list-boots` shows no new boot, so
nothing at the boot layer records this either. **The freeze is visible in exactly one place in this
machine: the difference between a unit's monotonic wall-clock accounting and the calendar.**

## Why this matters more than the instance

A restart is the wrong remedy and would have been recorded as the right one. "The worker died →
restart it" closes with the machine apparently repaired; the next Windows sleep costs another
stretch and the record says the cause was already fixed. Nothing in the tree currently distinguishes
the two, and the seat's brief printed a version of "quiet" for both.

Zero commits over the stretch is the cost, and `delivery-seat`'s own 08:13:47 record names it
without being able to say why: `"thesis_read": "THE MACHINE STOPPED AND NOTHING SAID SO."`

## The instrument half, and what is being done about it

`running_now()` in `background/delivery_seat.py` reads `ps`, matches the ten declared daemons from
`process_manifest.yaml`, and **prints only how many it subtracted** — `daemons_subtracted: 10`. The
complementary set is computed and discarded. A declared daemon that is not on the box therefore
lowers a count that nobody reads a floor on, and the brief's sentence reads the same whether ten
daemons are up or none are. That is a subtraction that hides absence: a control that cannot fail.

The complementary leg is landing in this same stretch as the second commit of this lane-0 item, on
the same reading and the same `ps` — no second mechanism. It names each declared daemon that is
**absent** from the box, and each that is **present but silent** (on the box, but its own unit
journal has gone quiet for longer than a threshold). The second half is the one that would have
caught THIS incident: under a VM freeze the daemons are all present, so an absence-only leg sees
nothing, and the silence is the only observable.

## What is NOT owed here

Nothing in the tree can stop Windows sleeping, and widening what this machine is allowed to do is
the director's alone. This finding does not ask for that. It asks that the machine be able to
*say* it happened, and that a lost stretch not be attributed to a daemon that was healthy.

## Reproducing the reading

```
journalctl --user -u background-worker.service --since "2026-09-20 17:20" --no-pager -o short-iso
journalctl --user --since "2026-09-20 17:40" --until "2026-09-21 08:10" --no-pager | wc -l   # -> 0
journalctl --user --since "2026-09-21 08:13:00" --until "2026-09-21 08:13:30" --no-pager \
  | grep "Consumed"                       # -> "over 10min 02.9s wall clock time" x4
```
