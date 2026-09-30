# Finding: a long job that dies is now shown dead in the brief, beside the running block

**Severity:** RECORDED · **Lane:** H_harness · **Claim:** `a-long-job-that-dies-is-shown-dead-in-the-brief`

## What was wrong

`delivery_seat.running_now()` lists only the jobs that are still alive. On 2026-09-29 two jobs died:

- `ab5-runA`, OOM-killed at 10:01:46Z.
- `ab5-runA2`, exit 1 at 15:08:02Z.

`launch_liveness.check` settled each one to `died` in the launch register within minutes. Nothing the seat orients on reads that register, so each death stayed invisible for over an hour.

## What landed

- **`delivery_seat.ended_since(since)`** reads the register. It lists every `launch_long_job` job that was launched or settled inside the stretch and is no longer `live`. Deaths sort first, and each row carries its result and exit status.
  - An unreadable register returns `available: False`, which is a different answer from an empty list.
- **The brief** gains an `ended` key beside `running`. `_prompt` renders it as a sentence directly after the running block:
  - one form when the reading failed,
  - one form when nothing ended,
  - one form listing the jobs that ended.
- **`is_material`** now returns true when a long job died in the stretch. Without this, a stretch where the only event was a death was skipped as quiet, and skipping it is exactly how the death stayed invisible. A stretch whose only ending was a success stays quiet.
- **The end time comes from systemd**, via `ExecMainExitTimestamp` read with `--timestamp=utc`. Both `launch_liveness.systemd_probe` and `launch_long_job.liveness_probe` now ask for it, and `check` stores `exited_at`, `result` and `exit_status` on the record when it settles a job.
  - Records settled before this change have only `settled_at`. The brief shows that value as `ended by …`, which is an upper bound and not the exit time.

## Two things this found

- **The direction item says `ab5-runA2` died at "16:08Z". That time is wrong.** Systemd's own exit timestamp in UTC is 15:08:02Z; 16:08 is BST. The 10:01Z time given for `ab5-runA` is correct.
- **The window is keyed to the settle time, not the exit time.**
  - A settle always follows its exit, so an exit inside the stretch implies a settle inside it. The mutation that dropped the exit term from the window test stayed green for that reason: it is an equivalence, not a missing test. The redundant term was removed.
  - Keying to the settle time also catches a death that happened before the last orientation but was only settled after it. That orientation could not have seen it.

## Controls

The controls are in `tests/background/test_a_long_job_that_dies_is_shown_dead_in_the_brief.py`.

- The first test checks the whole partition, before any test checks row content. Four rows go in: a death inside the window, a success inside the window, a death before the window, and a job still live. The two in-window rows must appear and the other two must not.
- `ab5-runA2`'s real record appears with `exit-code`/`1`.

Mutations run:

| Mutation | Result |
|---|---|
| `is_material` clause | red |
| `ended_at` falling back to the settle time | red |
| window filter | red |
| `LIVE` skip | red |
| `ended_sentence` | red |
| `check` copy loop | red |
| settle term dropped from window | red |
| exit term dropped from window | green: equivalence, term removed |

## Done means

The next brief shows the ended-jobs block. Against the live register it lists both 09-29 deaths, and `is_material` reads `2 long job(s) died in the stretch`. The seat can now mark the machine row about the 10:01Z kill as corrected.
