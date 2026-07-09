# Retrospective: doorbell failure #4 — architecture rebuild (THE SUPERVISOR)

Filed per R3 (two-strike redesign rule, now at strike 4 on the same broad
mechanism) and CLAUDE.md's phase-close retro trigger (a harness rule
changed). Every claim below is labelled **OBSERVED** (verified directly
against a real file/log/test) or **INFERRED** (a conclusion drawn from
observed facts, not itself independently re-run) per R9.

## What happened

**OBSERVED**: two staged P1 docs (BILL_CORRECTNESS_ADDENDUM.md,
DOMAIN_SENSE_AND_COMPLIANCE.md) landed 2026-07-08 20:43/20:55 UTC. Defect 1
was closed the same session (commit 32ab2a4c, ~22:42 UTC) and the agenda
was updated to point at Defects 2-4. Nothing further happened until the
director asked directly, in-console, over 8 hours later (2026-07-09,
post-`/clear`).

**OBSERVED**: `staging-watcher-log.md` shows the agenda continue-nudge
fired exactly once, at 22:47 UTC, logged "delivered (confirmed)". No
further agenda-nudge log line ever appears for any later cycle.

**OBSERVED**: `background/agenda.py`'s `should_nudge()` returns `None` for
any agenda snapshot (identified by its own `updated_at`) that has already
been nudged once (`record_nudged()`), by design — the docstring names this
explicitly: "Nudge-once discipline (R5: never repeat an unchanged
status)". Since the agenda was never advanced again after 22:42 UTC (no
session picked up Defects 2-4), no later cycle could ever produce a second
nudge for that snapshot. This is a direct, mechanical cause: the one
authoritative "resume the open agenda" signal fired once and then went
permanently silent for that state, by design, regardless of whether the
first nudge actually produced work.

**OBSERVED**: `session-watchdog-log.md` shows a *different* mechanism —
the autoloop continuation nudge — firing "Session idle — sending autoloop
continuation instruction" 34 times between 22:47 UTC (2026-07-08) and
04:32 UTC (2026-07-09), roughly every 10 minutes, continuously. Per the
code (`background/session_watchdog.py::check_autoloop`, as fixed the
previous session), that log line only executes after
`send_keys_when_idle()` returns `True` — i.e. the pane was idle, the send
subprocess succeeded, and the signed marker text was confirmed absent from
a post-send pane capture (the verified-consumption check built to fix the
prior strike-3 incident). All 34 of these were logged as confirmed
delivered. None produced any observable work: the agenda was never
advanced, no commit landed, docs/staging/ was never touched.

**INFERRED (not independently reproduced)**: the exact mechanism by which
34 consecutive "confirmed-delivered" sends produced zero turns is not
directly observable from outside the Claude Code CLI process — this
matches the epistemic position of the prior (Phase SB) incident, whose own
conclusion was that a related class of bug lives inside the CLI's own
input handling, not in this codebase. One plausible mechanism considered
but not confirmed: `tmux_relay.capture_pane()`'s default 30-line window
could report a long signed message as "no longer visible" because it
scrolled out of the captured range during a redraw, not because it was
genuinely submitted and processed as a turn — this would produce exactly
the observed signature (a "successful" consumption check with no
resulting work) but was not proven against the live process.

**OBSERVED**: `background/staging_watcher.py`'s process (pid 1169056) was
alive throughout the same window (`ps` showed ~10h continuous elapsed
time) but stopped producing ANY log output after 2026-07-09 00:04 UTC for
over 5.5 hours, despite every branch of its main loop being wrapped in a
broad `try/except` that logs on any error, and despite a periodic
(3-minute) git-fetch check that should have logged something every cycle
regardless of outcome. `/proc/<pid>/status` showed state `S (sleeping)`
and `/proc/<pid>/wchan` showed `hrtimer_nanosleep` at the moment of
inspection — i.e. not blocked in any syscall, apparently mid-way through
an ordinary `time.sleep()`. **INFERRED**: the precise reason the loop
stopped producing log lines was not established (no stack trace was
obtainable — `/proc/<pid>/stack` returned permission denied). Restarting
the process (R2) immediately restored normal logging. Whatever the cause,
a multi-responsibility daemon (git fetch, new-file notify, wake,
agenda-nudge, monthly maintenance, all in one process) going silently
inert took every one of those responsibilities down simultaneously.

## Why this is R3 at the architecture level, not another patch

Four independent failures of the same broad "get a turn granted to the
session" mechanism, each with a different proximate cause:

1. Pre-Phase-SB: raw, unguarded `tmux send-keys` corrupted a busy pane's
   input box. Fixed with `is_session_idle`/`send_keys_when_idle`.
2. 2026-07-08 17:47: an urgent from_rich message was classified and
   queued but never delivered. Fixed by the same idle-gated primitive.
3. 2026-07-08 (same day, strike 3): `session_watchdog.py`'s autoloop nudge
   was still using a raw, unguarded send (a known, explicitly-flagged
   deferred gap from the strike-1/2 fix) and raced `staging_watcher.py`'s
   now-safe wake into the same pane with no coordination. Fixed with
   `relay_lock()`, a shared cross-daemon lock.
4. This incident: even with every known race and corruption bug fixed,
   the system as a whole still failed — one authoritative path (`agenda.
   should_nudge`) was designed to never retry by policy, and the other
   (`session_watchdog`'s autoloop) retried faithfully and still produced
   nothing, undetected for 5+ hours because nothing was watching for the
   *absence of progress* despite repeated "success" logs, and a
   multi-responsibility daemon's silent stall took multiple redundant
   paths down at once rather than leaving at least one alive.

Patching strike 4 the same way as strikes 1-3 (find the one broken call
site, fix it) does not fit the evidence: the specific sends that fired
were, by the codebase's own verification logic, successful. The director's
diagnosis — polling was banned in favour of event-driven "nudge once,
never repeat" designs, and that policy is what let a state stay stuck for
hours even while individual retries kept "succeeding" — is the better fit,
and is the basis for this rebuild.

## What was built: THE SUPERVISOR

`background/supervisor.py` (new): a single-purpose, single-responsibility
daemon. Every `POLL_INTERVAL_SECONDS` (120s): if the session is idle
(`tmux_relay.is_session_idle`) AND real work exists on disk (open agenda,
unprocessed staging file, urgent from_rich message, or a usage-limit pause
that just ended), grant exactly one turn via the same locked, verified
relay every other daemon uses (`tmux_relay.send_keys_when_idle`, itself now
wrapped in `relay_lock()`), and log the decision every cycle — not just
the interesting ones. No git calls, no NTFY except the rare stuck
escalation below, nothing else in its hot loop that could block it the way
`staging_watcher.py` apparently got blocked.

**Beyond the director's literal spec** (flagged explicitly, not silently
added): the supervisor also tracks a fingerprint of real work-state
(agenda `updated_at` + the exact set of unprocessed staging filenames)
across cycles. If the same fingerprint survives `STUCK_GRANT_THRESHOLD`
(8) consecutive granted turns — roughly 16 minutes — that is no longer an
ordinary retry; it sends one NTFY escalation (deduped per stuck
fingerprint, R5-compliant) instead of retrying silently forever. This is
the one piece that directly targets failure mode 4 specifically: without
it, a rebuilt supervisor polling every 2 minutes would still have produced
"confirmed delivered" logs with zero progress, just faster and for longer
before anyone noticed.

Every other turn-granting path was demoted, not removed wholesale, based
on whether it still adds value:
- `session_watchdog.py`'s autoloop nudge: **removed** (its own send code
  and the now-dead `MAX_AUTOLOOP_PER_HOUR`/`autoloop_times` cap it was
  gated behind). It was strictly slower (10min vs 2min) and no better at
  detecting the "confirmed but ineffective" failure than what replaced it.
  Its idle-streak state machine is unchanged and still gates REVIEW_GATE
  reply relay, permission-prompt detection, and the proactive usage-pause
  check — none of which the supervisor handles.
- `background/agenda.py`'s `should_nudge()`/`record_nudged()`/
  `is_stale_enough_to_nudge()`: **removed** (the directly-implicated nudge
  -once mechanism). `test_agenda.py` gained an explicit guard test against
  reintroducing it.
- `staging_watcher.py`'s new-staged-file wake: **kept as a demoted
  fast-path hint** — genuinely useful (seconds instead of up to 2 minutes)
  when it works, and no longer load-bearing since the supervisor's own
  poll independently detects any unprocessed staging file.
- `dispatcher.py`'s URGENT tmux relay: **kept as a demoted fast-path
  hint**, same reasoning — the supervisor reads the
  `<!-- Dispatcher: URGENT -->` header dispatcher.py already prepends to
  the file, straight off disk, independent of dispatcher.py's own
  in-memory `_pending_urgent` retry queue or process health.

## Usage-limit pause/resume as NTFY transitions

Per the director's instruction ("so the director never has to guess"):
entering a proactive usage pause and the pause window ending each now fire
exactly one NTFY (in `session_watchdog.py`, which remains the sole owner
of writing/clearing `.usage_pause.json` — `supervisor.py` only ever reads
it, read-only, to avoid the two processes racing on the same file). This
reverses an earlier deliberate suppression (Rich flagged usage-limit NTFYs
as spam on 2026-06-16) — the earlier complaint was about a *repeating*
notification; a clean one-shot enter/exit pair is exactly what R5 permits
and does not repeat.

## Testing

`tests/background/test_supervisor.py` (27 tests): work-detection for each
of the four "work exists" conditions, the read-only pause check, the
stuck-fingerprint escalation (fires once at threshold, dedups, resets on
real progress, fires again for a new stuck state, does not fire on failed
deliveries), and four tests explicitly simulating each historical failure
mode by name (busy-pane refusal, urgent-from_rich independent of
dispatcher, relay-lock mutual exclusion against a concurrent daemon, and
34-confirmed-grants-zero-progress triggering exactly one escalation —
reproducing the real incident's exact grant count).

`tests/background/test_agenda.py`, `test_session_watchdog.py`,
`test_staging_watcher.py`: updated for the removed nudge/autoloop-send
code paths; net additions include a retirement guard
(`test_nudge_once_mechanism_is_retired`) and coverage for both new NTFY
transitions.

16,026 tests pass (full suite minus the standing --ignore list of slow
simulation integration suites), epistemic PASS.

## Deployment

`background/health_check.py` and `background/start_worker.sh` updated to
expect/start the new `supervisor` tmux session. `staging-watcher` was
restarted (it was the stalled process); `session-watchdog` was restarted
with the autoloop-removal fix; `supervisor` started fresh. All verified
live (R2) — see the commit(s) landing this retrospective for the exact
verification evidence quoted in the closing NTFY.
