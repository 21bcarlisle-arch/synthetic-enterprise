# A lane unit that crashes twice running is seen, and the 10-09 shape is repaired

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `a-lane-unit-that-crashes-twice-is-seen-and-repaired` (Lane 0)

Items 2 and 3 of the interactive lane's 13:57Z answer to the director
(`docs/staging/console/SEAT_REPLY_2026-10-09.md`). Item 1, prevention, landed as `470f2a746`.

## Premise, re-measured at draw

`470f2a746` is the prevention leg, so its being on origin does not spend the premise. Nothing on
origin read the timer units' journals. The duplicate claim the draw named was this draw's own write,
22 s old when the turn began, and no rival `surgical_land` was running.

## What was built

`background/lane_unit_crash.py`, which rides `reconcile_watch` (every five minutes), plus one
sentence in the seat brief (`delivery_seat._lane_crash_sentence`).

- **Detect.** A run is one systemd invocation. It is finished when systemd logs the start job's
  `JOB_RESULT`, and it crashed when that result is not `done` and the service's output holds a
  traceback. When the two newest finished runs of `worker-tick` or `seat-executor` both crashed,
  the brief names the unit and its exception line, and NTFY fires once per streak (keyed to the
  streak's first invocation).
- **Repair.** This happens only when both tracebacks end in the same `ImportError`,
  `ModuleNotFoundError` or `AttributeError`, the innermost frame is the same file in both, and that
  file is tracked and differs from HEAD in the shared tree. The copy is then preserved through
  `refresh_to_head.preserve` to `refs/preserved/refresh-to-head/lane-unit-crash-<unit>-<id>`. Its
  `-S` recovery route is proved before anything is written, then HEAD's bytes go over it, and NTFY
  says so. Every other cause is held, and the NTFY gives the reason. A preservation that refuses
  also counts as a hold.

## My prediction, refuted, and the correction

I pre-registered two predictions before the first live read. The live journal would read clean,
because the lanes had recovered at about 14:50Z. The 09:00–10:30Z window would read as crashed twice.

**The live read was refuted.** It said both lanes had crashed twice *now*. The cause was in the first
draft: it treated a run as finished only once systemd logged `EXIT_STATUS`. systemd writes that line
only when the main process fails, so the reader never saw a clean run. It skipped past every
recovered run to the two newest crashes. I moved the finish marker to `JOB_RESULT`, which every run
carries ("Finished" / "Failed to start"). After that change the live journal reads clean for both
units, and the 10-09 window reads crashed twice:

| unit | 10-09 window | failing frame | plan against today's shared tree |
|---|---|---|---|
| worker-tick | crashed twice, `AttributeError ... held_at_dispatch` | `background/worker_tick.py` | hold: file already matches HEAD |
| seat-executor | crashed twice, same | `background/seat_executor.py` | hold: file already matches HEAD |

Both plans read "hold" today, and that is correct: the director's hand repair already restored both
files. On 10-09 at 09:15Z both files were dirty against HEAD, so the plan would have been
"restore".

## Controls (`tests/background/test_a_lane_unit_that_crashes_twice_is_seen_and_repaired.py`)

The fixture is the real 10-09 worker-tick journal: one clean run, then the first two crashed runs.
The draw's own log lines are trimmed out. Each leg's control first shows that its rare branch can
be taken. For detection: a clean run followed by one crash is not "twice", and two crashes are.
For repair: one input is restored and two are held.

Nine mutations were run, and every one reds:

| mutation | leg | result |
|---|---|---|
| `all` → `any` in `reading` | detect | red |
| finish keyed to `EXIT_STATUS` (the first draft) | detect | red |
| page on every pass (drop the streak key) | detect | red |
| rider removed from `reconcile_watch.run` | detect | red |
| brief sentence returns `""` | detect | red |
| `plan` holds unconditionally | repair | red (2) |
| `REPAIRABLE = ()` | repair | red (2) |
| `restore` skips the write | repair | red |
| drop the "already matches HEAD" hold | repair | red |

**Two timer cycles.** The second crash finishes, and the next reconcile tick (within 5 minutes)
preserves the copy and writes HEAD. The third lane run, one 10-minute cycle later, therefore runs
HEAD's file. The fixture test shows that one `check()` pass after the second crash does the repair.

## Limits, said plainly

- The reader looks at the newest 3000 journal lines per unit. A crash streak longer than about 20 h
  at roughly 25 lines per run would move `streak_from` and page a second time.
- The repair restores only the **innermost** frame's file. When the stale copy is a different file
  (for example the module that lost a name, while the crashing caller is clean), the plan says
  "already matches HEAD" and holds. That is the safe direction. Prevention (`470f2a746`) covers
  the reverse half.
- Item 4 of the reply was to deliver the focus item to the interactive session when the broken
  thing is the lanes themselves. It is not built here.
