# Staging-watcher wake: consumption-confirmation check is structurally broken

**Found:** 2026-07-10, live, during B2_OPEX_TAXONOMY_EXPANSION.md's phase close. Not a
staging-content bug (both named files were correctly already-processed/staged) -- a real bug
in `background/tmux_relay.py::send_keys_when_idle()`'s post-Enter consumption check.

## Evidence (observed-with-evidence, not inferred)

- Received the identical `[STAGING WATCHER: ... B2_OPEX_TAXONOMY_EXPANSION.md,
  HARNESS_BEST_PRACTICE_ADOPTION.md ...]` wake twice in this conversation, ~32 seconds apart
  (message IDs `1783709355` and `1783709387`) -- both for files whose content was already
  confirmed unchanged (same hashes as earlier checks this session).
- `docs/observability/staging-watcher-log.md` showed continuous
  `Wake not yet delivered (session busy or unconfirmed) -- retrying next cycle` entries every
  ~30-60s from at least 18:36 UTC through 18:50 UTC for these exact two filenames -- 1103 total
  occurrences of this log line across the file's whole history (chronic, not new).
- Direct `tmux capture-pane -t claude -p` immediately after receiving the second duplicate wake
  showed the wake message's own trailing HMAC marker (`...1783709387|8ec2...064724`) still
  plainly visible in the pane's scrollback, several lines above the current prompt.

## Root cause

`send_keys_when_idle()` (background/tmux_relay.py:283-338) sends the signed wake text, presses
Enter, waits, then checks:

```python
after = capture_pane(session)
if _flatten(verify_marker) in _flatten(after):
    return False  # still sitting unconsumed in the pane
return True
```

This assumes a submitted message disappears from the pane once "consumed" -- true for a
single-line shell prompt, but **false for Claude Code's own terminal UI**, which keeps a
submitted user turn visible in the scrollback as part of the conversation transcript
indefinitely (or until it scrolls out of the capture window). So after a genuinely successful
send-and-consume, the marker is *still there* -- just now as a historical transcript entry
rather than a pending input -- and the check misreads this as "stuck, not consumed."

Practical effect: **every wake that actually succeeds gets misclassified as failed.**
`_pending_wake_names` never clears via the success path in `_attempt_pending_wake()`
(background/staging_watcher.py:347-377); the same names retry every cycle. Each retry that
happens to land during a genuine idle window (e.g. the moment right after Claude finishes
responding to the previous duplicate and before the next stimulus) resends the identical wake
as a brand-new turn -- which is exactly the double-delivery observed above. The only things that
currently stop the loop are (a) the file eventually being archived to `done/`, which the
doorbell-failure-#6 fix (2026-07-10) correctly drops as stale, or (b) the session staying
continuously busy long enough that `is_session_idle()` never returns True again.

## Why this wasn't caught by the failure-#6 fix

That fix (background/staging_watcher.py's `_attempt_pending_wake()` stale-name drop) addresses
a *different* failure mode: a wake still queued for a file that's since been archived. This bug
is upstream of that -- the wake for a file that's *still legitimately staged* (this project's own
2-3 day multi-part builds routinely leave a staging doc open for hours) can loop indefinitely
before archival ever happens, precisely because "confirmed delivered" can structurally never be
true once Claude Code's UI is the thing being scraped.

## Impact assessment

Low safety impact: R7/R8 discipline (this session's own repeated practice) means every duplicate
wake gets independently re-verified against real disk/git state and correctly recognized as
stale/no-new-content before any action is taken -- no wrong action has resulted. The cost is
attention/noise (repeated identical turns) and wasted daemon cycles, not incorrect behavior. A
future, less careful session (or a fresh context with no memory of "I already checked this")
could plausibly re-do already-completed diagnostic work each time this fires, which is the real
risk worth fixing.

## Not fixed this session

Deliberately not patched live: `background/tmux_relay.py` is a shared, actively-in-use relay
module (dispatcher.py, staging_watcher.py, and potentially other daemons all call into it) and
this specific session's own tmux pane was the one being scraped while diagnosing it -- editing
and reasoning about a live confirmation-check while it is actively mid-loop against my own
session risks a worse, harder-to-diagnose interaction than the current noisy-but-harmless
symptom. Registered here for a careful, tested fix in its own pass, not rushed into an already
large build-and-close turn.

## Suggested fix direction (not implemented)

Replace the "marker absent from pane" consumption check with a busy-then-idle transition check:
after sending Enter, poll for the pane to show a BUSY indicator (proving Claude Code actually
started processing the injected turn) and then return to idle -- mirroring the same
busy-spinner/footer-hint logic `is_session_idle()` already uses, just inverted and sequenced.
This distinguishes "never picked up" (stays idle throughout) from "picked up and completed"
(goes busy, then idle) without depending on scrollback content disappearing, which it never
does by design in this terminal UI.

## Symptom mitigation applied (2026-07-10, same session, later)

The bug kept firing live -- 7+ identical duplicate wakes observed in a single conversation
after this finding was first written, each costing a full verify-and-dismiss round-trip.
Rather than risk the `tmux_relay.py` redesign above mid-session (still deliberately deferred,
per the reasoning above), applied a narrow, single-daemon-scoped mitigation of the SYMPTOM only:
`background/staging_watcher.py::_attempt_pending_wake()` now tracks each pending wake's first
unconfirmed-attempt time (`_pending_wake_first_attempt`) and gives up retrying it after
`_WAKE_GIVE_UP_SECONDS` (600s) of no confirmed delivery, logging once and clearing the pending
set rather than hammering the session indefinitely. `background/supervisor.py::find_work()`'s
own independent poll (no tmux-relay dependency at all -- it re-checks disk state every cycle
regardless of wake delivery) remains the durable path for genuinely open staging work, so
nothing is actually lost by giving up on the wake specifically. 4 new tests
(`tests/background/test_staging_watcher.py`), 16,618 tests collected (full suite), epistemic
PASS (no company/saas files touched). This does NOT fix the root cause above -- a future pass
should still redesign `send_keys_when_idle()`'s confirmation check properly.
