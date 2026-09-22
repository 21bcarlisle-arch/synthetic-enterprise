**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the level/selection re-take died in silence and its preregistration says it is in flight)

# CORRECTION — beside `SEAT_PREREGISTRATION_WHAT_THE_CURRENT_BOOK_RETAKE_OF_THE_LEVEL_SELECTION_SPLIT_CAN_AND_CANNOT_SETTLE_2026-09-07.md`

That document opens **"The run is in flight."** It was not. Every prediction in it stands unchanged
and unread — this corrects the run it describes, not a single number it predicted.

## What is being corrected

| the prereg says | what was true |
|---|---|
| "The run is in flight" | pid 3046198 was gone; no artefact was ever written at `/var/tmp/value_cycle_ab_current_book_2026-09-07.json` |
| pinned to `153e90cd0` | the relaunch is pinned to **`ab6f36d10`** — see *The relaunch* below |
| log `…_2026-09-07.log` | that file is the **corpse's** log and is preserved untouched; the live run writes `…_2026-09-07_relaunch.log` |

## And a correction to the correction, because the death has been mis-dated

The drawn item that sent me here says the first launch *"died at roughly 56 minutes"*. **Nothing on
disk supports that, and the figure comes from reading a launch stamp as a death stamp.**

| evidence | time |
|---|---|
| worktree `/var/tmp/se-valuearms-20260907` created | 19:44:44 |
| the log's ONE line — a pytensor `g++ not detected` warning, on **stderr**, emitted at import | 19:44:50 |
| `docs/observability/book_growth_campaign.json` + `book_subset_verdict.json` written inside the worktree by `live_population._resolve_campaign` | 19:44:52 |
| anything at all, anywhere, attributable to that run, after that | **nothing** |

The log's mtime of 19:44 is the timestamp of its only line, and that line is written seconds after
the interpreter starts. It dates the **start**. The last evidence the run was alive is **eight
seconds** after launch. The death is therefore **undated**: it happened somewhere between 19:44:52
and 22:14, when it was found gone. It may have been a minute in; it may have been an hour.

This is worth writing down as its own shape, because it is the same one this seat keeps paying for:
*a timestamp on the last line of a log dates the last WRITE, and if the process wrote once at
startup and was then killed, that is the launch time wearing a death time's clothes.*

## Why there was no diagnosis, and what is not the cause

The log holds stderr and **not one byte of stdout**. The same tool, run to completion at 03:46 the
same morning (`/var/tmp/ab_leg_id_fixed.log`), wrote **28 MB** of stdout and ended `END … rc=0`.
So one of two things happened, and no record on this machine can separate them: stdout was never
redirected into that file, or it was redirected and lost in python's block buffer when the process
was killed. **The launch command was recorded nowhere** — not in the prereg, not beside the log —
so which of the two it was cannot now be established. That absence is the actual defect.

Three candidate causes are ruled out on evidence rather than on plausibility:

- **Not the headroom refusal.** `floor_run_headroom_refusal()` is consulted only on the
  `--noise-floor-seeds` branch of `tools/run_value_cycle_ab.py`. This was `--level-arm`, which
  never reaches it. It would also have printed and exited, flushing on the way out.
- **Not the worktree reaper.** The worktree was locked, and the sweeps either side of the launch
  report `WORKTREE REAP (enforce): no reapable worktree dirs`.
- **Not a recorded OOM.** The only OOM kills in the kernel log that day are inside
  `ops2-peak-kill-selftest-*` scopes, each at an identical 523,136 kB anon-rss — the selftest
  killing its own fixture. None names this run. That does **not** clear OOM as a cause; it means
  the kernel has no record of it, which is a different and weaker statement.

## The relaunch

| | |
|---|---|
| launcher | `/var/tmp/relaunch_value_cycle_ab_current_book_2026-09-07.sh` — **on disk, outside both trees**, so the next session diagnosing a death reads the command instead of reconstructing it |
| command | `python3 -u -m tools.run_value_cycle_ab --level-arm --out /var/tmp/value_cycle_ab_current_book_2026-09-07.json` |
| launched | 2026-09-07 **22:31:36**, under `setsid`, its own session, stdin from `/dev/null` |
| pid | **3419050** (python), 3419044 (wrapper), pgid 3419044 |
| tree | `/var/tmp/se-valuearms-20260907`, locked, **repinned `153e90cd0` → `ab6f36d10`** |
| log | `/var/tmp/value_cycle_ab_current_book_2026-09-07_relaunch.log` — **both streams**, `-u` so a kill cannot swallow the trail |
| exit status | `/var/tmp/value_cycle_ab_current_book_2026-09-07_relaunch.rc` — written by the wrapper, so "gone" can be told from "gone with rc=137" |
| artefact | `/var/tmp/value_cycle_ab_current_book_2026-09-07.json`, outside both trees |

**Proof of life, which is what the drawn item asked for.** `tools/wait_for.py --pid 3419050
--deadline 300 --heartbeat 60` was run against the **pid**, not a pattern, so it cannot self-match.
It returned **rc=1 DEADLINE** — *"DEADLINE after 300s … pid 3419050"* — which for a waiter is the
verdict "still running", and here that is the success. Four heartbeats at 60/120/180/240s each
found the pid live. Over the same five minutes:

| | at launch | at +5 min |
|---|---|---|
| log | 2 lines (the wrapper's own stamp) | 12 lines / 5,065 bytes |
| last line | `CMD python3 -u -m tools.run_value_cycle_ab …` | `Starting treasury: £250000.00` |
| RSS | 429 MB | 882 MB |

That is past import and into the run proper, through the population build and the EAC/AQ totals
(`Elec EAC: 464,284 kWh  Gas AQ: 997,550.9 kWh`) — the exact interval in which the first attempt
left no trace at all.

**The book has moved, and that is the one substantive change to the prereg.** "The current book"
now means `ab6f36d10`, **seventeen** commits later than the `153e90cd0` the prereg names. The prereg's four
predictions were written before any run existed and are unaffected in kind; prediction 1 —
*`value_advantage_gbp` lands outside the 09-03 run's £2,336* — is if anything on firmer ground,
because more of the book has moved under it than the 24 files it counted.

## What is still not done

The floor leg. The prereg is explicit that a single three-arm run **cannot** make the page state a
split, whatever its own share comes out at, because `_composition_in_this_world` reads seed rows
from the floor and a three-arm run carries none. It is deliberately not launched beside this one:
two hour-scale simulations on this guest is how a leg gets OOM-killed, and an OOM-killed leg writes
no artefact and reads exactly like one still running — which is the sentence this whole correction
exists to stop being written again.

Next session: `…_relaunch.rc` exists and holds `0` → copy the artefact into `docs/observability/`,
point `CURRENT_WORLD_THREE_ARM_PATH` at it, regenerate, land, then launch the floor leg. `.rc`
holds anything else → the log now says why, which is the whole difference from this morning.
