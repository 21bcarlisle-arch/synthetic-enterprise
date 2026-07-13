# 2026-07-13 — "committed != running" recurred a second time; mechanised it this time

**Claim discipline (R9): everything below is observed-with-evidence.** Process start times are from
direct `ps -o pid,lstart,cmd` reads against the real running PIDs; commit timestamps are from `git log`;
the live log excerpts are quoted verbatim from `docs/observability/supervisor-log.md`.

## What happened

Built and pushed `ANTI_LIVELOCK_AND_WIDTH.md`'s fix (commit `b7b9e360`, 2026-07-13 05:35:23) to
`background/supervisor.py` — an anti-livelock stall tracker plus a fix so the idle/DISCOVER-FRAME tier
grants up to 6 concurrent atoms per cycle instead of a hard-capped 1. Verified it directly against the
real map (`_idle_discover_frame_draw_concurrent()` returned 6 real distinct atoms in a manual call) and
shipped it with 240 passing tests.

For the next ~17 minutes, every single self-refill doorbell this session actually received kept
granting exactly ONE atom per cycle, repeating the same handful of atoms (`W1_reveal_over_time`,
`W2_2_population_draw`, `C2_discovery_through_interfaces`, `B4_competitor_field`) — the EXACT symptom
the fix was supposed to eliminate. Checked `ps -o pid,lstart,cmd -p $(pgrep -f supervisor.py)`: the live
process had started `2026-07-12 20:29:13` — over eight hours before the fix even existed on disk. The
running process had never re-read the file; it was still executing the pre-fix, single-atom-only code
the entire time the fix sat correctly committed, tested, and pushed.

Restarted the `supervisor` tmux session (`tmux kill-session -t supervisor && bash
background/start_worker.sh`). The very next log line confirmed the fix genuinely working:
`CONCURRENT idle-tier self-refill: 6 DISCOVER/FRAME atoms this cycle (atoms-drawn-per-cycle=6)` — a
real 6-atom grant, repeated on subsequent cycles.

While building the fix for THIS incident, ran the new stale-code check against the whole daemon set and
found it was not isolated: `session-watchdog` (edited this same session, for the Tier-1 model-switch
change) and `ntfy-responder` (edited 2026-07-11, running since 2026-07-08) were ALSO running stale
code — three daemons, not one. Restarted both; confirmed clean afterward.

## Root cause, not the instance

This is the identical class already found once before, named directly in `background/health_check.py`'s
own pre-existing docstrings: "CANNOT-draw... supervisor tmux daemon had stale pre-fix code loaded since
14:14; restarted, confirmed live via the next real draw" (2026-07-12). Same daemon, same mechanism, same
manual fix — restart it, verify, move on. That manual fix held for exactly one incident before recurring.

The real mechanism gap: nothing in this project's own considerable observability stack (`health_check.py`,
`session-watchdog`, `sanity_daemon.py`) ever compared a long-running daemon's own process start time
against its own script file's last-modified time. Every other class of staleness this project catches
(stale dependencies in the maturity map, stale staging messages, a missing tmux pane) has a real,
automated check. This one — arguably the highest-leverage one, since it silently defeats every OTHER
fix shipped to a running daemon until someone happens to notice the symptom and manually diagnoses it
— had none.

## The fix, verified not asserted

Built `background/health_check.py::_check_stale_running_code()`: for every `EXPECTED_PANES` daemon,
finds its real process start time via `ps -eo lstart,args` and compares it against its own script
file's mtime. A process that started before its own script was last modified is flagged as a named,
concrete finding (which daemon, since when, how many minutes of drift) — not a silent assumption.

Verified for real, immediately, against the actual live stack — not a synthetic test only: ran it before
any restart and it correctly flagged all three genuinely-stale daemons (`supervisor`, `session-watchdog`,
`ntfy-responder`) with real drift figures; ran it again after restarting all three and got a clean
`None`. 6 new tests added (a mocked-`ps` unit-test suite plus a `run_health_check()` integration test),
30/30 pass in `test_health_check.py`, 708/708 pass across `tests/background/`.

Wired into two places: `run_health_check()`'s own routine report (so `health_check.py --quiet`, already
invoked at `background/start_worker.sh`'s own startup, catches this going forward) and
`session_watchdog.py::_verify_daemon_set_after_restart()` (built earlier this same session for the
daemon-liveness ask), which already calls `run_health_check()` after every main-session restart — this
new check rides along for free.

## The class-level lesson (R10 applied to a harness defect, not a simulation one)

**A committed, tested, pushed fix is not "done" until the process it targets has actually restarted and
that restart has been verified** (R2, "committed != running", already a named rule in this project —
this incident is that rule failing to generalise from "the interactive session" to "every long-running
background daemon"). The manual instance-fix (restart, check the log) worked both times it was applied,
but relied on someone noticing the symptom and correctly diagnosing the cause each time — exactly the
"exhortation, not mechanism" failure mode `MAKE_IT_STICK.md` already names. This retro converts it: any
future code change to a long-running daemon's own script now has a real, automated, already-wired check
that will flag the staleness the next time `health_check.py` runs, rather than depending on a human (or
this agent) catching a symptom by inference.

## What was NOT lost / genuine scope of harm

No data corruption, no incorrect BUILD output, no wrong decisions made from stale data — this was
purely a **process** defect (the harness's own draw mechanism running old logic), never touching
simulation ground truth or company-layer output. Real cost: roughly 17 minutes where the anti-livelock
fix's own real value (wider, faster self-refill throughput) was unrealised, plus an unmeasured but
likely longer window where `session-watchdog`'s and `ntfy-responder`'s own more recent edits were
similarly inert. No incorrect claim was made to the director before this was caught and fixed within
the same session.

## Follow-up (done inline, not a vague TODO)

Audited all three currently-stale daemons found via the new check, not just the one that produced the
originally-noticed symptom — `session-watchdog` and `ntfy-responder` were found and fixed in the same
pass, before this retro was even written, matching R10's own "closure requires extending the invariant
library... so the entire class fails automatically thereafter" discipline.
