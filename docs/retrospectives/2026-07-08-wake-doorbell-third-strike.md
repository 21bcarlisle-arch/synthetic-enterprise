# Retrospective: third wake-doorbell failure — session_watchdog's autoloop send bypassed the Phase SB fix entirely (2026-07-08)

Filed per R3 (two-strike redesign rule) and CLAUDE.md's phase-close retro trigger
("harness rule changed" / repeat problem). Every claim below is labelled **OBSERVED**
(verified directly against a real file/log/test) or **INFERRED** (a conclusion drawn
from observed facts, not itself independently re-run) per R9.

## What happened

**OBSERVED**: `docs/staging/BILL_CORRECTNESS_ADDENDUM.md` and
`docs/staging/DOMAIN_SENSE_AND_COMPLIANCE.md` landed at 20:43 and 20:55 UTC
(`staging-watcher-log.md`). Both wakes are logged as **"Wake delivered (confirmed)"**
by `staging_watcher.py` — its own idle-gated, verified-consumption send
(`send_keys_when_idle`) genuinely succeeded both times. Neither staged doc was actioned
by the live session until the director typed directly in-console over two hours later
(this session, post-`/clear`) asking why.

**OBSERVED**: in the same window, `session-watchdog-log.md` shows its own,
completely separate "Session idle — sending autoloop continuation instruction" firing
on its own ~10-minute cadence (20:44, 20:54, 21:04, 21:14, 21:24, 21:34, 21:44 UTC —
at least 7 times after both docs were staged), each one supposedly instructing the
session to "first check docs/staging/... action it now... repeat until
docs/staging/ is empty" (the actual text of `AUTOLOOP_INSTRUCTION`).

**OBSERVED**: `session_watchdog.py`'s autoloop send (previously line 1193) and its
REVIEW_GATE reply relay (previously line 1140) were direct, unguarded
`subprocess.run(["tmux", "send-keys", ...])` calls — not routed through
`background/tmux_relay.py`'s `send_keys`/`is_session_idle`/`send_keys_when_idle`
primitives at all, despite the module's own docstring claiming session_watchdog.py
already went through it.

**OBSERVED**: commit `cc2d741c` (the 2026-07-08 test-suite-tmux-leak fix, earlier the
same day) explicitly built `tmux_relay.py` as "the ONE place every background daemon
injects text," and explicitly flagged this exact gap in its own commit message:
*"session_watchdog.py's own call sites are left as direct subprocess.run calls for
now... flagged as a follow-up, not silently dropped."* That follow-up was never done.

## Root cause (INFERRED, but tightly grounded in the observed logs/code above)

Two independent daemons write into the same live tmux pane with no coordination:
`staging_watcher.py` (idle-gated via `is_session_idle`'s busy-spinner/footer check,
verified-consumption, now also lock-protected) and `session_watchdog.py`'s autoloop
nudge (a cruder "pane text unchanged for `AUTOLOOP_IDLE_CHECKS` consecutive 60s polls"
heuristic, unguarded, unverified, uncoordinated). The autoloop send fired within ~60
seconds of both confirmed wake deliveries. I have not reproduced the exact interleaving
byte-for-byte (the live pane's history from that window wasn't preserved — `tmux
capture-pane` on this fresh post-`/clear` session only shows the current session's own
scrollback), so the precise mechanism of how the wake's directive got lost (corrupted
input, or a redundant generic nudge racing/overwriting/queuing ahead of the specific one)
is inferred from the code + timing, not directly observed byte-for-byte. What is
observed beyond dispute: two unlocked, uncoordinated writers existed, one of them bypassed
every safety primitive the previous incident built, and the outcome was two P1 docs sitting
unactioned through 7+ "helpful" autoloop nudges that should have surfaced them.

This is the same underlying bug class as the incident `tmux_relay.py` was built to fix
(SB), recurring because the fix was applied to two of three daemons and the third was
explicitly deferred and then forgotten — not because the underlying idle-detection
technique itself failed again.

## Why this is R3, not another patch

Strike 1: original raw-`send_keys`-into-busy-pane corruption (pre-Phase-SB), fixed by
adding `is_session_idle`/`send_keys_when_idle` to `tmux_relay.py`, applied to
`staging_watcher.py`/`dispatcher.py` only.
Strike 2: the 17:47 urgent-from_rich failure the director flagged same day, root-caused
and closed by the same Phase SB fix.
Strike 3 (this one): a *different* call site in a *different* daemon, never migrated,
silently reintroducing the identical failure mode two hours later the same day.

Per R3, patching `session_watchdog.py` with its own bespoke idle check (a fourth
variant of "is this pane idle") would be strike-2-style repair on a component that has
now failed three times. The fix instead **eliminates the duplicate mechanism**:
`session_watchdog.py` now calls the exact same `send_keys_when_idle()` every other
daemon uses, and a new cross-process `relay_lock()` (fcntl, mirrors
`background/tree_lock.py`'s git-write serialization) makes the idle-check+send+verify
sequence atomic across daemons, so two callers can never interleave into the pane
regardless of which one gets there first.

## Fixes landed this session

1. `background/tmux_relay.py`: added `relay_lock()` (cross-process fcntl lock, 5s
   timeout — a legitimate holder's critical section is under ~2s) wrapping
   `send_keys_when_idle()`'s idle-check+send+verify sequence.
2. `background/session_watchdog.py`: migrated both raw call sites —
   - Autoloop continuation nudge: now HMAC-signed (`sign_wake_message`, consistent with
     every other wake in the codebase) and sent via `send_keys_when_idle`. A failed send
     no longer counts against `MAX_AUTOLOOP_PER_HOUR` and naturally retries next poll
     (the existing idle-streak bookkeeping already re-attempts every cycle once past
     threshold — no new retry machinery needed).
   - REVIEW_GATE reply relay: `read_and_clear_response()` still consumes the response
     file exactly once (avoiding replay), but the decision is now buffered in memory
     (`_pending_gate_decision`) until `send_keys_when_idle` confirms delivery — a busy
     pane no longer silently loses Rich's approve/hold decision.
3. 4 new tests in `test_tmux_relay.py` (relay_lock serializes sequential acquisitions;
   times out and raises when already held; `send_keys_when_idle` fails safe when the
   lock is held by another process). 4 tests in `test_session_watchdog.py` updated to
   mock `send_keys_when_idle` instead of raw `subprocess.run` (matching the pattern
   already used in `test_staging_watcher.py`), plus 2 new tests for the retry-on-busy
   paths. 342 background tests pass (338 pre-existing + 4 net new), full epistemic PASS.
4. `session_watchdog` tmux daemon killed and restarted with the fix; verified live
   (clean startup log line, `SE_NTFY_TOPIC` present in `/proc/<pid>/environ` — same
   verification pattern as the NTFY channel hardening phase).

## What is genuinely still open (found this session, not yet fixed — tracked explicitly so it can't be silently dropped again)

- `session_watchdog.py::check_session_usage()` sends `/usage` + `Escape` via raw,
  unlocked `subprocess.run` (separate call site, lines ~1049/1052). Same class of gap,
  lower risk (brief, self-contained round-trip inside an already-idle-gated branch of
  `check_autoloop`), not implicated by tonight's observed evidence. Not fixed tonight to
  avoid unverified scope creep on a component I can't currently live-test end to end.
- `session_watchdog.py::_relay_inbound_command()` (the from_rich NTFY-command relay,
  line ~636) still carries the exact comment this incident disproves — *"Claude Code
  queues input typed while busy, so this is safe whether the session is idle or
  mid-task"* — and sends raw/unlocked. Whether this duplicates or races
  `dispatcher.py`'s own URGENT from_rich relay (verified safe in Phase SA) was not
  checked this session.
Both registered in PRIORITIES.md backlog (not left as a comment alone — that's exactly
how the session_watchdog gap from `cc2d741c` got lost) for a follow-up phase.
