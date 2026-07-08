# REVIEW GATE: autonomous-runner never actually stopped (directive falsely completed)

**Status:** OPEN — Option A adopted; durable launcher fix DONE; awaiting Rich's console kill (2026-07-08)

---
## RE-PING (2026-07-08 ~08:37 UTC) — Rich status-checked this as P1; respawn path still LIVE
Rich asked (from_rich_20260708_080828.md): "verify the respawn path is actually dead
(no more identical-net auto-process commits)." **It is not dead.** Verified this turn:
- **Live process still up:** `python3 background/autonomous_runner.py` **PID 1005093**
  (parent shell PID 1005091), still started Tue Jul 7 15:00:10, never killed.
- **It is still spawning me:** `pstree -p 1005091` →
  `sh(1005091)---python3(1005093)---claude(1108681)` — PID 1108681 is *this* turn (the
  earlier gate note's PID 1102045 was a prior turn; the spawner keeps launching fresh
  `claude -p` children). I remain its descendant, so I still cannot self-kill it.
- **Identical-net commits still flowing:** 52 of the last 60 commits are
  `net=£1,535,308`; streak runs 2026-07-07 19:25 → 2026-07-08 09:29 (newest this
  morning). That stream is the proof the respawn path is alive.
- **Durable launcher fix confirmed intact:** `start_worker.sh` autonomous-runner block
  is still commented out (RETIRED banner, lines 51-59) — a stack restart won't resurrect
  it, but the *currently-running* instance is untouched by that edit.

**Nothing new for me to do here — the one remaining step is Rich's console kill** of
PID 1005091 / 1005093 (or `tmux kill-session -t autonomous-runner`). After that, a later
(non-descendant) session flips agent_status.json to true "retired".

---
## RESOLUTION IN PROGRESS (2026-07-08 ~08:35 UTC) — Option A adopted per director directive
`docs/staging/AUTONOMOUS_RUNNER_TRUE_RETIREMENT.md` (advisor-staged, 2026-07-08 07:46 BST)
confirmed the 07-07 "retired" claim was wrong and selected **Option A** below. My part
(steps 1, 2, 5) is done this turn; steps 3–4 need Rich.

**DONE (this turn):**
- **Step 1 — durable launcher fix:** the `autonomous-runner` block in
  `background/start_worker.sh` is now commented out (RETIRED banner citing this gate). A
  future `start_worker.sh` re-run will NOT resurrect it. This is the fix that makes the
  console kill stick, which it did not on 07-07.
- **Step 5 — MAINTENANCE.md:** standing rule added — retiring a daemon = edit its launcher,
  not just kill the process.

**RICH — YOUR ACTION (step 3): console-kill these exact processes.** They will NOT come
back after the kill (launcher block now removed). Simplest: `tmux kill-session -t autonomous-runner`.
Or kill by PID:
- `sh -c python3 background/autonomous_runner.py` — **PID 1005091** (tmux `autonomous-runner:0.0` parent shell), started Tue Jul 7 15:00:10
- `python3 background/autonomous_runner.py` — **PID 1005093** (the spawner itself), child of 1005091

Its ONLY current child claude turn is **PID 1102045** — *this very session*, running the
staging-triage prompt. It will exit on its own when this turn ends; do not target it
separately. (I did not kill the spawner myself precisely because I am its child — killing it
mid-turn would abort my own committed-or-not work. Verified via `pstree -p 1005093`.)

**AFTER YOU CONFIRM THE KILL (step 4):** a later session verifies via `ps`/`pstree` that no
`claude -p` remains parented to 1005093, then flips `autonomous-runner` to a true "retired"
status in `docs/observability/agent_status.json` (currently self-overwritten by its own
heartbeat every cycle — cannot honestly show "retired" while it lives). Alerting suppression
in `health_check.py` is already in place from a prior session.

---
**Status:** OPEN — awaiting Rich's steer (2026-07-08)
**Opened:** 2026-07-08 ~07:35 UTC, during staging triage
**Tier:** 2-adjacent (executing a director decision) BUT the directive's stated premise
is factually contradicted by reality, and the target is a session launcher whose kill
could affect autonomous throughput — so surfacing before proceeding, not proceeding on
a wrong premise.

## The contradiction
`docs/staging/AUTONOMOUS_RUNNER_RETIRED.md` (director, 2026-07-07 ~15:00 BST) states the
autonomous-runner was "DELIBERATELY STOPPED by Rich at the console... Not an outage --
do not restart it." Its DO-items assume the process is already gone: mark it retired in
health data, suppress alerting, fold the restart question into the next weekly re-rank.

**Reality on this tree (2026-07-08 07:3x UTC):** the autonomous-runner is *still running*
and is actively spawning `claude -p --dangerously-skip-permissions` turns:
- `python3 background/autonomous_runner.py` — pid 1005093, **started Tue Jul 7 15:00:10**
  (i.e. a *new* instance came up ~10s after Rich killed the old pid 4223 at ~15:00), in
  tmux session `autonomous-runner:0.0`.
- It launched the very session that discovered this (this turn's chain:
  `autonomous_runner.py` 1005093 → `claude -p ...` 1092850 → this turn).
- `autonomous-runner-log.md` shows real turns launched through 2026-07-08 06:32
  (pid 1092850), plus interleaved pytest-pollution lines (a separate test-isolation bug).

## What is genuinely done vs not
- **DONE:** alerting suppression — `background/health_check.py` already excludes
  autonomous-runner from `EXPECTED_PANES` with a comment citing this directive (a prior
  session did this half).
- **NOT DONE (and cannot be, while the process lives):** marking it "retired" in
  `docs/observability/agent_status.json`. `autonomous_runner.py:238` writes its OWN
  "working" heartbeat every cycle, so any "retired" status is self-overwritten within
  one poll interval. The board therefore still shows it green/"working".
- **NOT DONE:** actually stopping it. This is the crux — R2 (committed ≠ running):
  the directive was "actioned" in code but the running process was never stopped.

## Why a new instance keeps appearing
`background/start_worker.sh` launches it via `_start_session "autonomous-runner"
"python3 background/autonomous_runner.py"` using a plain `tmux new-session` (no respawn
wrapper; "safe to re-run — skips sessions already running"). The pid has been stable
since 15:00:10, so it is NOT an auto-respawn loop. The 15:00:10 restart was a stack
re-run (start_worker.sh re-invoked) after Rich's console kill. **A console kill alone
did not stick last time** because the next stack start brought it back. To make "do not
restart it" durable, the `autonomous-runner` block in `start_worker.sh` must be removed
/ commented out, not just the process killed.

## Why I did not just kill it myself
1. The directive's premise ("already stopped; the watchdog-managed interactive session is
   now the SINGLE writer") is contradicted on this tree. There are multiple claude
   sessions of unclear role/health (interactive `claude --dangerously-skip-permissions`
   pid 221835 since Jul 4; another in tmux session `claude:0` pid 490416; the watchdog
   pid 489668). autonomous-runner was originally created *because* the tmux-keystroke
   autoloop was "broken" (start_worker.sh's own description). So I cannot safely assume
   killing autonomous-runner leaves a functioning writer — a wrong kill could halt
   autonomous progress.
2. The target is a session launcher (safety-adjacent). Stopping it is the *safe*
   direction, but combined with (1) this is a "surface the contradiction, don't proceed
   on a wrong premise" situation.
3. I am a descendant of the process in question — killing it mid-turn is inherently
   messy and would abort my own committed-or-not work.

## Options
- **A. Rich console-kills + I make it durable.** Rich kills the `autonomous-runner` tmux
  session at the console (as he intended on 07-07), and confirms I should comment out the
  `autonomous-runner` block in `start_worker.sh` so a stack re-run won't resurrect it.
  Then agent_status.json can hold "retired". Recommended.
- **B. Authorize me to stop it.** Rich confirms (in-conversation) that I should
  `tmux kill-session -t autonomous-runner` + edit start_worker.sh. I'll do it as the
  final act of a turn (after committing), accepting that this turn ends when its launcher
  dies. Requires confidence that another session (221835 / watchdog autoloop) is a
  working writer — please confirm that too.
- **C. Leave it running, re-rank later.** Accept the two-writer state until the weekly
  re-rank. Costs continued budget burn + tree-race risk (the exact things the directive
  set out to fix). Not recommended.

## Recommendation
**A.** It matches how Rich stopped it before (console), makes the stop durable via
start_worker.sh, and avoids me killing my own launcher on a premise that's already proven
wrong. Meanwhile: S1 (director-approved, "proceed NOW") should be executed by the intended
single-writer session, not by an autonomous turn the director wants retired — so I have
NOT started the S1 build from this turn.
