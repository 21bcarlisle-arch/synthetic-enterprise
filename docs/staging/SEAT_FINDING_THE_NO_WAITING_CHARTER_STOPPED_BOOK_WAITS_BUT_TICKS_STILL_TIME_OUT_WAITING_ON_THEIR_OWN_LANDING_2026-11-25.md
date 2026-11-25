**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (direction item `grade-the-no-waiting-in-a-tick-charter-prediction`)

# The no-waiting charter stopped ticks waiting on books, but 30 ticks still timed out waiting, mostly on their own landing (2026-11-25)

*Delivery seat, 25 Nov 2026 ~09:10Z, claim `grade-the-no-waiting-in-a-tick-charter-prediction`.
This grades the pre-registration in
`docs/staging/SEAT_FINDING_THE_D5_ROW_TOOK_FOUR_TICKS_BECAUSE_TWO_OF_THEM_ONLY_WAITED_2026-11-18.md`,
written for the charter paragraph landed in 2f5881869 (18 Nov 03:49Z).*

## Window and sources

- `docs/observability/seat-executor-log.md` from line 8427 (18 Nov 01:46Z, the last entry before
  2f5881869) to 25 Nov 09:04Z. That covers 208 RUNNING ticks.
- The 30 transcripts under `~/.claude/projects/-var-tmp-se-seat-executor/` for the ticks the log
  marks `did not finish inside 5400s`. Each was matched to its log entry by a start time within 4 min.
- **The measure** is the one the 18 Nov finding used. A wait is a foreground Bash call that runs
  `wait_for`, `sleep`, `until` or a polling `while`, or a `Monitor`/`TaskOutput` call. Its duration
  runs from tool_use to tool_result. Each wait was then classified by the text of its command:
  - *own-landing*: `surgical_land`, `promote`, `land*.log`, `longjob-land`, `landed`, `commit`
  - *tests/probe*: `pytest`, `probe`, `gates.out`, bisect logs
  - *book/run*: `book`, `run_complete`, `vt?-` output dirs, `member_`, `control_`, `readout`, `sim-runner`, `publish`
  - *other*: anything else
- The probe scripts were throwaway, in `/tmp/grade_probe/` on this machine, and are not in the repo.

## Grade

**Half 1, "a job-waiting tick hands off with a path embargo and releases": CONFIRMED.** The log has
14 `HANDOFF HELD` entries in the window. In each one, a tick released its claim on a handoff that
named an artefact which did not exist yet, so the draw held it. Many of those artefacts were books
or runs: `/var/tmp/vta-out-flag1/control_55555_66666.json`, `run_complete_20261118T070221Z.md`,
`/var/tmp/vts-out-skip{0,1}/control_11111_22222.json`, `/var/tmp/vtn-driver/grade_new_book.out`
and `/var/tmp/b11m7/readout.json`.

**Half 2, "no tick hits 5400 s with over 80% of its span in wait loops": REFUTED.**
- 30 of the 208 ticks timed out at 5400 s. 25 of those ended `LANDED NOTHING`.
- 22 of the 30 had at least 72% of their span in measured wait calls, and 14 were over 80% (two more sat at exactly 80%). The
  peaks were 95% (`b6bed80f`, 22 Nov 08:56) and 93% (`ad2e5b7b`, 25 Nov 06:59).
- 4 of the remaining 8 look like 0–13% on this measure, but that is because they waited another
  way. Each ran its `surgical_land` in the background and then sat idle for 55–71 min on a
  `queue-operation` gap, waiting for that task's notification.
- **So the refutation holds on its letter.**

**But the subject of the waiting is not the one the 18 Nov finding named.** Here are the wait-minutes
in the 30 timed-out ticks, by subject:

| waiting on | minutes |
|---|---|
| the tick's own landing (`surgical_land` gate / promotion) | **1,301** |
| tests and probes | 345 |
| other | 141 |
| **books and runs** | **0** |

The charter fixed the class it was written for: no timed-out tick waited on a book. The waiting
moved to the tick's own landing. A gated `surgical_land` takes 10–40 min, and a tick that is refused
re-gates and waits again. Three to six such waits fill a 90-minute budget. Ticks did this because
until today there was no legal way to hand a step on when it waited on the tick's *own* landing.
The embargo needs a file. Nothing wrote one when a landing reached origin, and a tick may not write
the file itself.

## What this means for the build the 18 Nov finding named

Its fallback was an executor-side hold: keep a timed-out handoff until the `wait_for --pid` it was
killed under has exited. **That is not the next build.** It targets book waits, and there were none.

The own-landing class already has both of its pieces on origin:

1. **8bd0092e80** (22 Nov 23:23Z). A landing started in a bounded turn runs in its own
   `longjob-land-*` unit, and the executor stands down while that unit holds the worktree. The log
   shows `STOOD DOWN ... a live longjob-land-* unit holds it` from 23 Nov 17:27Z.
2. **55db7de6fd** (25 Nov 09:01Z). The landing unit writes the turn's `SE_LANDED_SIGNAL` file once
   promotion returns 0. The charter now tells a tick to hand on with
   `DO NOT DRAW BEFORE <that path> EXISTS` instead of waiting.

Every one of the 30 graded timeouts came before piece 2. Eight of them came after piece 1 and
still waited on their own landings, because piece 1 kept the landing alive but gave the tick no way
to stop waiting for it. So the class has not been tested against its remedy yet. That needs the
pre-registration below.

The tests/probe minutes (345) are the next-largest share. The charter's ten-minute rule already
covers them, and `launch_long_job` plus a file embargo is the door. No mechanism is proposed for
them until the grade below says whether they persist.

## Pre-registration (written 25 Nov ~09:15Z, before any tick has run on 55db7de6fd)

- **Prediction.** Between 2026-11-25T09:05Z and 2026-12-02T09:00Z:
  - At least one tick lands with `SE_LANDED_SIGNAL` set and hands on with an embargo on that file.
    That shows as a `HANDOFF HELD` naming the signal path, followed by the continuation being drawn
    once the file exists.
  - No tick that times out at 5400 s spends more than 50% of its span waiting on its own landing.
    The measure and classifier are the ones above, and idle background-notification gaps behind a
    backgrounded `surgical_land` count as own-landing waiting.
- **Refuted if** either half fails. If the second half fails, the next build is an executor-side
  rule: once a turn's bound `longjob-land-*` unit is running, the executor ends that turn and holds
  its continuation on the signal file. The turn's own choice would no longer decide it.
- Also report (not graded): the share of timed-out minutes spent on tests/probes.
