**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (direction item `why-one-focus-row-absorbed-four-ninety-minute-ticks`)

# The D5 row took four ticks because two of them only waited on a running job, and no filter skipped the contact-cause steer (2026-11-18)

*Claim `why-one-focus-row-absorbed-four-ninety-minute-ticks`. This follows
`SEAT_FINDING_FOCUS_WAITED_ON_RANK_NOT_ON_CONTINUATIONS_2026-11-18.md`, which raised both questions.
Two of that finding's claims were wrong, and they are corrected there.*

## Sources

- `docs/observability/seat-executor-log.md`, lines 8388–8404 (17 Nov 15:17–20:58Z).
- The four tick transcripts under `~/.claude/projects/-var-tmp-se-seat-executor/` (ba52345f,
  8e6ffc16, e3fb3fb0, 36618fa6). Each Bash call is put in one of three groups: waiting
  (`wait_for`, `until`, `sleep` or `while` loops), landing (`surgical_land`, `promote_worktree`) or
  other. The minutes are the union of each group's call intervals, so background waits that
  overlap are counted once.
- `docs/direction/decisions.jsonl`, the 12:20, 15:22 and 18:22 records.

## (a) Why D5 was drawn four times

At 15:17 the D5 row was not drawn as focus of the 15:22 record. It was drawn from the **12:20**
record, where it was `focus[1]`; `focus[0]` had already been drawn. An interactive seat was live, so
the executor stood down and **promoted** the row into the continuation store. From then on it was a
continuation. `find_work` tries `_continuation` before `_focus` unless a chain leg is armed, and here
none was. So each later re-offer beat every focus row of both later records.

| tick | waiting on jobs | landing | ended | what it waited on |
|---|---|---|---|---|
| 15:26 | 33 of 84 min (39%) | 47 min | 5400 s timeout, claim kept, HANDOFF STANDS | pair 2 (`/var/tmp/vta-out-flag1/member_33333_44444.json`) |
| 16:56 | 80 of 84 min (96%) | 0 | 5400 s timeout, claim kept, HANDOFF STANDS | the d5book-pause watch, sim-runner's journal, pair 2 (on disk 17:41Z) |
| 18:37 | 87 of 88 min (99%) | 0 | 5400 s timeout, LANDED NOTHING | `wait_for --pid 577704`, the D5-on book launched 18:19Z |
| 20:07 | 18 of 51 min (35%) | 20 min | released, DISCHARGED | the publisher on the finished book |

All four were the same continuation, re-offered by HANDOFF STANDS. None was a sweep. None was a new
offer from a record either: the 18:22 record still listed D5 as `focus[2]`, but focus never had to
offer it. **About 218 of the 307 tick-minutes went to waiting on jobs. The 16:56 and 18:37 ticks did
nothing else.** The row's done condition ("graded and published") was blocked on a book that took
hours. Each tick waited inside its own 90-minute budget instead of handing off with an embargo. The
embargo grammar (`awaited_paths`, `DO NOT DRAW BEFORE <path> EXISTS`) has existed since September.
The ticks were never told to use it.

What the waiting cost: the 18:22 record says the offer-gate item was "ready at 17:41Z and was not
drawn". The 18:37 tick was the slot it would have had.

## (b) Why `the-contact-cause-steer-is-logged-for-the-backlog` was never drawn

**No `_focus` filter skipped it. `_focus` was never asked.** At 15:26 and 16:56 the continuation leg
returned D5 before focus was consulted. The steer was done anyway, inside the 15:26 D5 tick. The
advisor file `DIRECTOR_STEER_CONTACT_CAUSE_...` came first in that tick's prompt as RUNG ZERO
(`advisor_channel.prefix`). The tick spent its 47 landing minutes on that steer and landed it as
6f0b5eb1c (16:12Z) and 4df9f5d00c. The 18:22 record then dropped it from focus as finished. The
focus row and the rung-zero prefix were the same work by two routes. The prefix got there first, as
it is meant to.

## Proposed change, made in this landing

A paragraph in `CHARTER_BODY` (`background/seat_executor.py`). It tells a tick not to spend its
turn waiting on a job that will take longer than about ten minutes. Instead the tick lands what it
has, hands the waiting step on with `DO NOT DRAW BEFORE <absolute path> EXISTS`, releases its claim
and ends. This reuses `awaited_paths`. No new mechanism is added. Checked: `awaited_paths` reads a
plain path phrase and ignores the backticked placeholder.

Why a prompt line and not a mechanism: the waits were the tick's own choice, made with the grammar
already available. An executor-side guard (for example, holding a timed-out handoff until a
`wait_for --pid` it was killed under has exited) would act only after 90 minutes were already
spent. It stays the next step if this prediction fails.

## Pre-registration (written before any tick has run on this charter)

- **Prediction.** Within the next 7 days, at least one executor tick whose work waits on a run,
  book or publish ends by writing a handoff with a path embargo and releasing its claim. That shows
  in the log as DISCHARGED or NO HANDOFF TO DROP, with a new handoff id carrying `DO NOT DRAW
  BEFORE`. No tick should hit the 5400 s timeout with more than 80% of its span in `wait_for`/sleep
  loops.
- **Refuted if** a tick hits `did not finish inside 5400s` with more than 80% of its span spent
  waiting (measured as above) after this charter landed. If that happens, build the executor-side
  hold.
