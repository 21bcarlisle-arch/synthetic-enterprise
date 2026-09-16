**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [SEAT] Pre-registration: what `.launch_records.json`'s loader and writers will do, written before I ran any of it

**This is a pre-registration, not a finding.** It is filed BEFORE the measurement whose answer
decides the disposition row, so that the row cannot be read as a verdict fitted to whatever came
back. Corrections go beside the predictions, in this file, not instead of them.

## Why the measurement exists

`tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned` is RED
at HEAD on `.launch_records.json` — a live census hit with no row in
`docs/design/self_clearing_alarm_dispositions.json`. The writer is `background/launch_liveness.py`.

The register demands two independent answers, and the second is the one a one-line append skips:

1. **The verdict** (`_verdicts`): `real` iff the path carries an episode-scoped field — an
   episode-start timestamp or a consecutive-failure counter — **that an alarm reads for SEVERITY**,
   and a write that has not demonstrated the episode ended can shorten or reset it. Otherwise
   `benign`, with a mandatory reason.
2. **The `loader` field** (`_verdicts._scope_of_benign`): does the carrier's loader tell ABSENT from
   PRESENT-BUT-UNREADABLE, and what does the WRITER do on top of a lost read? A read-modify-write
   over the whole record can DESTROY the record on a corrupt read, where a pure reader only loses a
   suppression. `benign` says nothing about this, and a row with no `loader` is a gap, not a pass.

`background/launch_liveness.py::load` is `json.loads(...)` under a bare `except Exception` returning
`[]`, and `record`/`check`/`save` are read-modify-writes over the whole list. So question 2 is live.

## What the census derived (not a prediction — already measured, `derive()` at HEAD)

- `failure_writers`: `launch_liveness.py::check`, `launch_liveness.py::record` — both
  "read-modify-writes its own state (a failure outcome overwrites the episode)".
- `alarm_readers`: `deadmans_switch.py::_check_launch_artefacts_landed`, `::main`, `::run_cycle`.
- Writers also include `tools/os_open_uprn.py::build_grid`/`::main`, which do not touch this path —
  a parameter-seam artefact of the derivation, noted so the row is not read as claiming they do.

## The predictions

Written before running anything. The partition is the register's seven-member one: absent, empty
file, truncated JSON, `null`, `{}`, `{"a": 1}`, `[1, 2, 3]`.

**P1 — the loader conflates ABSENT with UNREADABLE.** `load()` returns `[]` for *every* member
except `[1, 2, 3]`, which it returns unchanged because the `isinstance(data, list)` check tests the
container and not its elements. Nothing raises. The caller therefore cannot tell "no launches have
ever been recorded" from "the file is corrupt", and there is no third return value in which the
difference could be carried.

**P2 — `record()` is the destructive half.** Given a corrupt store, `record(job=X)` writes
`[X_entry]` — every OTHER job's record is gone, including any settled verdict and its evidence.
This is the ranking `_scope_of_benign` asks for: destructive on a corrupt read, not merely a lost
suppression.

**P3 — `check()` is NOT destructive on a corrupt read.** `if settled:` guards the writeback, and a
`[]` load settles nothing, so `check()` on a corrupt store writes nothing at all. It loses the
opportunity to settle, and that is all. I predict the census's `failure_writers` entry for `check`
is right about the SHAPE (it is a read-modify-write) and wrong about the CONSEQUENCE here.

**P4 — the `[1, 2, 3]` member reaches the deadman as an exception, and fails CLOSED.**
`check()` calls `entry.get(...)` on an `int` → `AttributeError`; `_check_launch_liveness` catches
`Exception`, logs, and `return`s **without** `clear_transition`. So a corrupt store does not crash
the deadman cycle and does not clear the alarm. If this prediction is wrong in the second half —
if the alarm clears — that is a fail-open and a finding of its own.

**P5 — a relaunch erases an unsettled death, and no guard stops it.** `record()` filters the
existing row out by job name *unconditionally*: `[r for r in load(path) if r.get("job") != job]`.
It does not look at `claim`. So the sequence — job X dies; the deadman has not cycled, so X's
record still claims `live`; X is relaunched — deletes the stale claim before anything can settle
it, and the `[LAUNCH DIED]` `real_alarm` that `_check_launch_liveness` exists to raise never fires.
I predict `launch_long_job.launch()` does **not** prevent this: `name_is_held()` refuses only a
relaunch over a *live* unit, and `clear_a_corpse()` explicitly clears the name of a dead one and
proceeds.

P5 is the prediction I am least sure of and the one that decides the verdict, because it is the
only route by which a write shortens something an alarm reads.

## What I will do with each answer, decided now

- **If P5 holds**, the row cannot be a bare `benign`. There is no episode-start timestamp or
  failure counter read for severity — `launched_at` and `settled_at` are read by nothing outside
  `launch_liveness` itself, so the literal `real` test is not met and forcing `real` would demand
  an `episode_monotonic` streak guard over a field (`claim`) that is not a streak. The honest row
  is `benign` **on the register's own question** with the suppression named in the `why`, plus a
  separate finding for the suppression, so that the register is not asked to carry a defect its
  verdicts cannot express.
- **If P5 fails** — if some guard I have not found refuses a relaunch over an unsettled `live`
  record — the row is plainly `benign` and the finding is not filed.
- **If P1 or P4 come back other than predicted**, the `loader` field says what actually happened
  and this file is corrected beside the prediction, not rewritten.

## What came back — written after, beside the predictions and not instead of them

All five held. Recorded here because a pre-registration whose outcome section is missing is
indistinguishable from one written after the answer.

| | Prediction | Outcome |
|---|---|---|
| P1 | loader conflates ABSENT with UNREADABLE; `[1,2,3]` survives | **HELD.** absent/empty/truncated/`null`/`{}`/`{"a":1}` all → `[]`, nothing raised; `[1,2,3]` returned unchanged |
| P2 | `record()` destroys other jobs' records on a corrupt read | **HELD.** `['alpha','beta']` + one `record('gamma')` over corrupt bytes → `['gamma']` |
| P3 | `check()` writes nothing on a corrupt read | **HELD.** 0 settled, bytes byte-identical. The census's `failure_writers` note on `check` is right about the shape, wrong about the consequence here |
| P4 | `[1,2,3]` → `AttributeError`, deadman logs and does **not** clear | **HELD.** `AttributeError: 'int' object has no attribute 'get'`; `_check_launch_liveness` catches, logs, returns without `clear_transition` — fail-closed, no finding |
| P5 | a relaunch deletes an unsettled `live` row; `launch()` does not prevent it | **HELD**, and worse than predicted: `clear_a_corpse`'s `reset-failed` *also* destroys the systemd exit record `reask()` depends on, so the death is unsettleable by a second, independent route I had not predicted |

Per the decision recorded above: P5 held, so the row is `benign` on the register's own question with
the suppression named in its `why`, and the suppression is filed separately as
`SEAT_FINDING_A_RELAUNCH_DELETES_THE_UNSETTLED_LIVE_RECORD_OF_THE_DEATH_IT_IS_RELAUNCHING_AFTER_2026-09-16.md`.

*Filed 2026-09-16 by the delivery seat, claim `self-clearing-alarm-census-launch-records-disposition`.*
