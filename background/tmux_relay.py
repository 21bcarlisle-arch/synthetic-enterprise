"""Shared tmux send-keys relay -- the ONE place every background daemon
injects text into a live tmux session (session_watchdog.py, dispatcher.py,
staging_watcher.py all call this rather than invoking `tmux send-keys`
directly).

Built with a structural test-isolation guard: refuses to run under pytest,
regardless of whether any individual test remembers to mock it.

Incident (2026-07-08): several existing tests in test_staging_watcher.py
mocked `ntfy` but not the new tmux-relay call `check_once()` gained that
same day; every full-suite pytest run after that point sent real text into
the live 'claude' session using those tests' own fixture filenames
(TASK_NEW.md, A.md, B.md, NEW.md, maintenance_due_202610.md) -- initially
misdiagnosed, in the same session, as an external prompt-injection attack
before the director corrected it with direct evidence (the ntfy.sh topic
history itself was clean). Root cause was purely local test isolation, not
any external channel. See docs/retrospectives/
2026-07-08-test-suite-tmux-leak.md for the full evidence chain.

Rather than relying on every test remembering to mock this call (the thing
that just failed), the guard lives here, once: PYTEST_CURRENT_TEST is set
by pytest for the duration of every test it runs (stable, documented pytest
behaviour, not a private API) -- if set, this function is a silent no-op.
No test, existing or future, can accidentally send real keystrokes into a
live tmux session through this path, even if it forgets to mock anything.

Session isolation guard (docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md,
2026-07-08): every existing call site already hardcodes SESSION_NAME =
"claude", so this guard changes no live behaviour by default -- it exists
so an injection can never silently land in the wrong tmux session if that
constant ever drifts inconsistent across daemons, or a future multi-session
setup introduces a real one. The target is configurable via
SE_TMUX_SESSION_NAME (unset = "claude", matching every current caller);
`send_keys` refuses (no-ops) if `session` doesn't match it.

Idle-gated verified send (2026-07-08, same-day follow-up, director-direct
root-cause fix): a live incident showed a signed wake message landing
PARTIALLY in the target session's input box and never submitting -- a
corrupted fragment sat there, unsubmitted, across many subsequent turns.
A live probe (sending the identical signed text to a throwaway `cat`
session) proved `send_keys` itself transmits the full text correctly,
byte for byte -- the corruption happens in the receiving Claude Code TUI's
own input handling when a long keystroke burst arrives while it is busy
(mid-turn), not in this module. Since that's an external CLI's behaviour,
not something this codebase can patch directly, the fix is defensive on
this side: `send_keys_when_idle()` (a) refuses to send at all unless the
target pane currently shows no busy indicator (spinner + gerund status
line, or an "esc to interrupt"-style footer hint), and (b) after sending,
re-captures the pane and confirms the just-sent text is no longer sitting
there unconsumed -- if it is, the send is treated as failed (not
recorded as delivered) so the caller retries next cycle instead of
silently believing a stuck injection succeeded.

Cross-daemon relay lock (2026-07-08, third wake-doorbell failure,
docs/retrospectives/2026-07-08-wake-doorbell-third-strike.md): the module
docstring above claimed session_watchdog.py already went through this one
relay -- false. Its autoloop-continuation nudge and REVIEW_GATE reply relay
were left as direct, unguarded `subprocess.run(["tmux", "send-keys", ...])`
calls at the 2026-07-08 tmux-leak incident fix (commit cc2d741c), flagged
there as a deliberate follow-up that was never done. Two staged P1 docs sat
unactioned for 2+ hours despite staging_watcher confirming "delivered" wakes
for both, because session_watchdog's own unrelated, unguarded autoloop send
was independently racing the same pane on its own cruder idle heuristic
(pane-text-unchanged-for-N-polls, not the busy-spinner/footer check below),
with no coordination between the two daemons. `relay_lock()` makes the
idle-check+send+verify sequence in `send_keys_when_idle()` an atomic
cross-process critical section (fcntl flock, mirrors background/tree_lock.py
for git writers) so no two daemons can interleave sends into the same pane,
and session_watchdog.py now goes through `send_keys_when_idle()` like every
other caller -- closing the gap rather than adding a second bespoke guard.
"""
from __future__ import annotations

import datetime as _dt
import fcntl
import json
import os
import re
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

DEFAULT_SESSION_NAME = "claude"

# Director-present hold (2026-07-14, director: "you still pasted 3 things just
# now ... as I type"): while the director is actively steering the interactive
# session, NO daemon may inject into the pane -- the human is using it. The
# supervisor's legitimate autonomous turn-grants were landing in his live input
# box during interactive steering (injection-log: supervisor.py:grant_turn). This
# is the human-presence arm of the one-gate rule, enforced in `_safe_to_inject`
# so EVERY gated writer honours it, not just the supervisor.
_DIRECTOR_PRESENT_FILE = Path(__file__).resolve().parent.parent / "docs" / "observability" / ".director_present.json"

_RELAY_LOCK_FILE = Path(__file__).resolve().parent.parent / "docs" / "observability" / ".tmux_relay.lock"
# DEFECT_TMUX_PANE_INJECTION.md (2026-07-13, director P2): source-attributable
# logging for EVERY send-keys injection, so a future storm is diagnosable in
# seconds (which script, when, what) instead of an hour of SIGSTOP forensics.
_INJECTION_LOG = Path(__file__).resolve().parent.parent / "docs" / "observability" / "injection-log.jsonl"


def _log_injection(session: str, keys, outcome: str) -> None:
    """Append one JSONL record per send_keys attempt: timestamp, the calling
    script (walked off the stack), a payload hash + head, and the outcome
    (sent/failed/suppressed_*). Best-effort -- never raises into the caller."""
    try:
        import sys
        # Never write the production log from a test run. The send_keys tests
        # deliberately delenv PYTEST_CURRENT_TEST to exercise the real path, so
        # guard on pytest's module presence instead (stays imported regardless).
        if "pytest" in sys.modules:
            return
        import hashlib
        import inspect
        import json

        source = "unknown"
        for fr in inspect.stack()[2:]:
            base = fr.filename.rsplit("/", 1)[-1]
            if base != "tmux_relay.py":
                source = f"{base}:{fr.lineno}:{fr.function}"
                break
        payload = " ".join(str(k) for k in keys)
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source": source,
            "session": session,
            "outcome": outcome,
            "payload_sha1_10": hashlib.sha1(payload.encode("utf-8", "replace")).hexdigest()[:10],
            "payload_len": len(payload),
            "payload_head": payload[:80],
        }
        with open(_INJECTION_LOG, "a") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass
# Short on purpose: a legitimate holder's critical section is a single
# idle-check + send + ~1.5s verify sleep + re-capture, so a few seconds is
# generous headroom. Daemons poll every 30-60s anyway, so a lock-contention
# failure just retries next cycle rather than blocking a poll loop for long.
_RELAY_LOCK_TIMEOUT_SECONDS = 5.0


class RelayLockTimeout(Exception):
    """Raised when the cross-daemon relay lock could not be acquired in time."""


@contextmanager
def relay_lock(timeout: float = _RELAY_LOCK_TIMEOUT_SECONDS):
    """Hold an exclusive cross-process lock for the duration of the `with`
    block, serializing every daemon's idle-check+send+verify sequence onto
    the live tmux session so two daemons can never race into the same pane.
    Mirrors background/tree_lock.py's git-write serialization. Raises
    RelayLockTimeout on timeout (a stuck holder should surface, not hang
    every other daemon's poll loop indefinitely) -- send_keys_when_idle()
    catches this and treats it as an ordinary failed-send/retry-next-cycle
    outcome."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        yield
        return
    _RELAY_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    fh = open(_RELAY_LOCK_FILE, "w")
    deadline = time.monotonic() + timeout
    try:
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise RelayLockTimeout(
                        f"Could not acquire tmux relay lock ({_RELAY_LOCK_FILE}) within {timeout}s"
                    )
                time.sleep(0.2)
        yield
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()

# A busy pane shows a spinner glyph + gerund-form status line ending in a
# live elapsed-time counter (e.g. "✽ Running the Epoch-2 desk-work evidence
# pass… (51s)") -- the "(<N>s)"/"(<N>m <N>s)" suffix is what's genuinely
# unique to an in-progress task; a bare ellipsis is NOT, because Claude
# Code's own persistent completed/pending task-list panel (bullets ◼ ◻ ✔ ✘)
# stays visible in the pane indefinitely and its lines are truncated with
# "…" too. The original regex (no elapsed-time requirement, 2026-07-08)
# matched those static checklist lines as "busy" -- confirmed live
# (2026-07-09): the supervisor logged "Session busy" every single 2-minute
# cycle for ~7 hours straight while the session was genuinely idle for
# almost all of it, because a completed task-list block sat in the pane's
# last 30 lines the whole time. Real work (a staged BUDGET_UNCONSTRAINED.md)
# went undelivered for hours as a direct result -- this is the exact bug R4
# was supposed to have already caught, in the same function, one day older.
# NOTE (DEFECT_TMUX_PANE_INJECTION.md, 2026-07-13): the elapsed-time token is
# no longer at the END of the line -- Claude Code now appends a token counter
# INSIDE the parens, e.g. "✽ Metamorphosing… (19m 43s · ↓ 64.5k tokens)". The
# old `\)\s*$` end-anchor stopped matching, so EVERY busy turn read as idle and
# daemons injected mid-turn (the input box filled with 300+ [Pasted text #NNN]).
# Anchor on a word boundary after the "s" instead, so any trailing content
# inside/after the parens is tolerated. Still requires a real "(<N>s)"/"(<N>m
# <N>s)" live timer (a bare ellipsis on a static completed-task-list line must
# NOT match -- see test_busy_spinner_requires_elapsed_time_suffix_not_just_ellipsis).
_BUSY_SPINNER_LINE = re.compile(r"^\s*\S\s+\S.*\(\d+(?:m\s*\d+\s*)?s\b", re.MULTILINE)

# Claude Code's footer shows an "esc to interrupt"-style hint (sometimes
# truncated to "esc …" in a narrow pane) only while a turn is actively
# running; an idle prompt's footer does not mention "esc" in this context.
# The check must be scoped to the actual footer line (identified by the
# stable "bypass permissions" marker), not a bare substring search across
# the whole pane -- found live (2026-07-09, doorbell failure #5) that a
# pane-content word merely CONTAINING "esc" (e.g. "description") would
# otherwise false-positive as busy.
_BUSY_FOOTER_HINT = "esc"
_FOOTER_LINE_MARKER = "bypass permissions"


def _configured_session_name() -> str:
    return os.environ.get("SE_TMUX_SESSION_NAME", DEFAULT_SESSION_NAME)


def pane_in_copy_mode(session: str) -> bool:
    """True if `session`'s active pane is in tmux copy-mode/view-mode
    (`#{pane_in_mode}`) -- i.e. showing frozen scrollback (the CLI's own
    "Jump to bottom" hint is one visible symptom) rather than the live
    tail, and swallowing keystrokes as copy-mode navigation instead of
    forwarding them to the running program. Fails safe: any capture error
    returns False (never claims copy-mode when we can't confirm it)."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return False
    try:
        result = subprocess.run(
            ["tmux", "display-message", "-p", "-t", session, "-F", "#{pane_in_mode}"],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0 and result.stdout.strip() == "1"
    except Exception:
        return False


def exit_copy_mode(session: str) -> bool:
    """Send tmux's copy-mode 'cancel' command (bound to q/Escape in the
    copy-mode key table) to snap `session`'s pane back to the live tail.
    Returns True only if the command was issued successfully -- not proof
    copy-mode actually cleared; callers that need certainty should re-check
    `pane_in_copy_mode()`."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return False
    try:
        result = subprocess.run(
            ["tmux", "send-keys", "-X", "-t", session, "cancel"],
            capture_output=True, timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def ensure_live_tail(session: str) -> None:
    """Best-effort: if `session`'s pane is frozen in copy-mode/scrollback,
    clear it so subsequent idle-checks and sends see/reach the real live
    pane. Root cause (2026-07-09, R4): a pane left in copy-mode all morning
    showed stale scrollback ("Jump to bottom") to every daemon -- capture_pane
    read frozen content instead of the live tail, and injected keystrokes
    were consumed by tmux as copy-mode navigation rather than reaching the
    running CLI, so grants silently vanished with no error anywhere. No-op
    (and safe) if the pane is not in copy-mode, or under pytest."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return
    if pane_in_copy_mode(session):
        exit_copy_mode(session)
        time.sleep(0.2)


def send_keys(session: str, *keys: str) -> bool:
    """Send `keys` (the trailing tmux send-keys arguments, e.g. a text
    string plus "Enter", or a bare "Escape") to tmux session `session`.

    Returns True if the subprocess call was attempted and returned exit
    code 0, False otherwise (including when suppressed under test, when
    `session` doesn't match the configured target, or on any exception --
    callers treat this as best-effort, matching how every existing call
    site already handled a dead/missing tmux session).

    Low-level primitive -- fires unconditionally (no idle check, no
    delivery verification). Wake-injection call sites should use
    `send_keys_when_idle()` instead; this is kept for direct/diagnostic
    use (and is what `send_keys_when_idle()` itself calls internally).
    """
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return False
    if session != _configured_session_name():
        _log_injection(session, keys, "suppressed_session_mismatch")
        return False
    try:
        result = subprocess.run(
            ["tmux", "send-keys", "-t", session, *keys],
            capture_output=True, timeout=5,
        )
        _log_injection(session, keys, "sent" if result.returncode == 0 else "failed")
        return result.returncode == 0
    except Exception:
        _log_injection(session, keys, "exception")
        return False


def capture_pane(session: str, lines: int = 30) -> str:
    """Return the last `lines` of `session`'s pane content, or "" on any
    failure (missing session, tmux unavailable, suppressed under test).
    Read-only -- never types anything."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return ""
    try:
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", session, "-p", "-S", f"-{lines}"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""


def _flatten(text: str) -> str:
    """Strip all whitespace so a substring check survives the pane's own
    line-wrapping (a long single logical line gets word-wrapped across
    multiple visual lines at the pane's fixed width)."""
    return re.sub(r"\s+", "", text)


def _is_busy_content(content: str) -> bool:
    """True if the pane content shows ANY busy indicator. Broadened beyond the
    original spinner+footer-"esc" check (DEFECT_TMUX_PANE_INJECTION.md): the
    old fail-OPEN check declared idle whenever its two specific patterns were
    absent, so newer Claude Code busy states -- "Waiting for background agent…"
    (shown the ENTIRE time a background fork runs), "Levitating…", or an
    "esc to interrupt" hint on a line OTHER than the bypass-permissions footer
    -- slipped through and got injected mid-turn."""
    if _BUSY_SPINNER_LINE.search(content):
        return True
    flat = _flatten(content).lower()
    # "esc to interrupt" anywhere (wrap-safe via the flattened capture), plus
    # current gerund status words the spinner-timer regex alone can miss.
    if "esctointerrupt" in flat:
        return True
    if "waitingforbackground" in flat or "levitating" in flat:
        return True
    # Legacy: an "esc" hint on the bypass-permissions footer line.
    footer_line = next(
        (line for line in content.splitlines() if _FOOTER_LINE_MARKER in line), ""
    )
    if _BUSY_FOOTER_HINT in footer_line.lower():
        return True
    return False


def is_session_idle(session: str) -> bool:
    """Best-effort idle detection: True only if the pane shows no busy
    indicator. Fails safe -- any capture error or a busy pattern returns False
    (never assume idle when we can't actually confirm it).

    NOTE: still single-capture (fail-open on an UNKNOWN busy state). The
    broadened `_is_busy_content` closes the states seen in the wild
    (DEFECT_TMUX_PANE_INJECTION.md); the stronger byte-stability gate (a
    processing pane is never static) is queued separately (H16) because it
    needs the send_keys_when_idle flow tests reworked around the extra
    capture."""
    content = capture_pane(session)
    if not content or _is_busy_content(content):
        return False
    return True


def _poll_until(session: str, want_idle: bool, timeout: float, interval: float) -> bool:
    """Poll `is_session_idle(session)` until it equals `want_idle`, or
    `timeout` seconds elapse. Returns whether the wanted state was
    observed in time (bounded -- never spins forever)."""
    deadline = time.monotonic() + timeout
    while True:
        if is_session_idle(session) == want_idle:
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(interval)


_INJECT_STABILITY_INTERVAL = 0.8


def _pane_has_pending_input(content: str) -> bool:
    """True if the pane's INPUT box already holds UNCONSUMED content -- a prior
    injection that has not been submitted. Format-INDEPENDENT: keys on the input
    prompt glyph and the literal paste-chip marker, never the moving spinner.

    This is the accumulation guard (DEFECT_TMUX_PANE_INJECTION REOPENED): while
    ANY input sits unconsumed, never inject more -- so a wrong idleness guess can
    leave at most ONE chip, never the 300-deep [Pasted text #NNN] pile the
    director saw."""
    if not content:
        return False
    if "[Pasted text" in content or "[Image #" in content:
        return True
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("❯"):
            if s[len("❯"):].strip():
                return True
    return False


def _director_present() -> bool:
    """True if a director-present hold is active (`.director_present.json` with a
    future `until`): the interactive session marks the director as actively
    steering, and while it holds NO daemon may inject into the pane. Fails safe
    toward NOT present (absent / malformed / expired -> autonomous operation
    resumes normally) so a stale hold can never permanently freeze the loop."""
    try:
        data = json.loads(_DIRECTOR_PRESENT_FILE.read_text(encoding="utf-8"))
        until = _dt.datetime.fromisoformat(data["until"])
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError, TypeError, OSError):
        return False
    if until.tzinfo is None:
        until = until.replace(tzinfo=_dt.timezone.utc)
    return _dt.datetime.now(_dt.timezone.utc) < until


def mark_director_present(minutes: float = 30.0) -> None:
    """Called by the interactive session when the director is actively steering,
    to HOLD all autonomous pane injection for `minutes` (refresh on each
    interaction). Bounded TTL so the hold auto-expires when he goes quiet and the
    autonomous loop resumes without anyone clearing anything."""
    until = (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(minutes=minutes)).isoformat()
    _DIRECTOR_PRESENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    _DIRECTOR_PRESENT_FILE.write_text(json.dumps({"until": until}), encoding="utf-8")


def clear_director_present() -> None:
    """Release the hold immediately (autonomous injection resumes next cycle)."""
    try:
        _DIRECTOR_PRESENT_FILE.unlink()
    except FileNotFoundError:
        pass


def _safe_to_inject(session: str) -> bool:
    """The injection gate, REDESIGNED (2026-07-13, DEFECT_TMUX_PANE_INJECTION
    REOPENED, R3 -- pane-scrape idleness GUESSING failed twice against a moving
    spinner format it does not control). Conditions, ALL required, so a wrong
    idleness guess can never convert into accumulated pane input:
      0. NO director-present hold -- while the human is actively steering the
         session, no daemon may type into his box (2026-07-14, added after the
         supervisor's turn-grants kept landing in the live input box as he typed);
      1. no unconsumed input already in the box (accumulation can't compound);
      2. no known busy indicator (belt);
      3. BYTE-STABLE across a short re-capture -- a processing session's pane
         mutates every second because the spinner's elapsed-time counter TICKS
         (and streamed output changes), whatever the spinner's text format is,
         so instability is a format-proof 'busy' signal; only a genuinely idle
         prompt is static.
    Fails safe: any capture error or ambiguity returns False."""
    if _director_present():
        return False
    c1 = capture_pane(session)
    if not c1 or _pane_has_pending_input(c1) or _is_busy_content(c1):
        return False
    time.sleep(_INJECT_STABILITY_INTERVAL)
    c2 = capture_pane(session)
    if not c2 or c2 != c1 or _pane_has_pending_input(c2) or _is_busy_content(c2):
        return False
    return True


def send_keys_when_idle(
    session: str, text: str, verify_marker: str,
    post_send_wait: float = 1.5, post_type_wait: float = 0.3,
    busy_confirm_timeout: float = 10.0, completion_timeout: float = 90.0,
    poll_interval: float = 1.0,
) -> bool:
    """Only inject `text` + Enter if `session` is currently idle at its
    prompt; verify both that the text actually reached the input line and
    that it was subsequently consumed, rather than trusting a
    fire-and-forget send.

    `verify_marker` should be a short, distinctive substring of `text`
    (e.g. the trailing HMAC hex digest of a signed wake message) --
    checked against the flattened (whitespace-stripped) pane capture, so
    word-wrapping can't hide a still-stuck fragment.

    Sequence: clear any frozen copy-mode/scrollback first (R4, 2026-07-09
    -- see `ensure_live_tail()`), confirm idle, send `text` WITHOUT Enter
    and confirm the marker actually landed in the pane (proof the
    keystrokes reached the input line rather than being silently swallowed
    -- e.g. by tmux copy-mode interpreting them as navigation, the exact
    failure mode that motivated this split), only then send Enter.

    Consumption is then confirmed via a busy-THEN-idle state transition,
    NOT by the marker disappearing from the pane (redesigned 2026-07-10,
    docs/design/STAGING_WATCHER_WAKE_CONFIRMATION_BUG.md): Claude Code's
    own terminal UI keeps a submitted turn visible in scrollback
    indefinitely, so "marker absent" could structurally never become true
    even after a fully successful send -- every genuine success was being
    misclassified as still-stuck, causing duplicate wake deliveries
    (observed live: 1103 retry-log occurrences, confirmed duplicate sends
    ~32s apart in one real session). Instead: wait (bounded by
    `busy_confirm_timeout`) for the pane to go BUSY -- proof Claude Code
    actually picked up the turn, held under the same lock as the send so
    no other daemon's own idle-check can race a competing send into the
    still-transitioning pane -- then release the lock and wait (bounded by
    `completion_timeout`) for the pane to return to IDLE -- proof the turn
    completed. A session that never picks up the turn, or is still busy
    past `completion_timeout`, returns False; the caller's own
    is_session_idle() gate on its NEXT call correctly refuses to re-send
    while the pane is genuinely still busy, so this can't itself cause a
    duplicate.

    The send itself runs inside `relay_lock()` so a second daemon calling
    this concurrently can't interleave its own send (see module docstring,
    "Cross-daemon relay lock") -- but the (potentially long) wait for
    completion runs outside the lock, so a slow turn doesn't block every
    other daemon's own sends for its whole duration.
    """
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return False
    try:
        with relay_lock(timeout=_RELAY_LOCK_TIMEOUT_SECONDS):
            ensure_live_tail(session)
            # REDESIGNED gate (R3): byte-stability + input-box-occupancy, not a
            # single-snapshot spinner-format guess. See _safe_to_inject.
            if not _safe_to_inject(session):
                return False
            if not send_keys(session, text):
                return False
            time.sleep(post_type_wait)
            landed = capture_pane(session)
            if not landed or _flatten(verify_marker) not in _flatten(landed):
                # Text never reached the input line -- e.g. swallowed by
                # copy-mode navigation, or the pane wasn't actually focused
                # on an input prompt. Not delivered; do not send Enter into
                # whatever state the pane is actually in.
                return False
            if not send_keys(session, "Enter"):
                return False
            time.sleep(post_send_wait)
            went_busy = _poll_until(
                session, want_idle=False,
                timeout=busy_confirm_timeout, interval=poll_interval,
            )
    except RelayLockTimeout:
        return False  # another daemon is mid-send -- retry next cycle
    if not went_busy:
        return False  # never picked up -- genuinely inert/stuck send
    return _poll_until(
        session, want_idle=True,
        timeout=completion_timeout, interval=poll_interval,
    )


def read_slash_dialog_when_idle(
    session: str, command: str, parse, dismiss_key: str = "Escape",
    render_wait: float = 2.0,
):
    """Inject a bare slash command (e.g. "/usage") that opens a transient
    dialog, read the dialog back, parse it, and dismiss it -- but ONLY when
    the pane is safe to inject into, under the SAME cross-daemon relay lock and
    the SAME `_safe_to_inject` gate as every other pane writer.

    This exists because a slash command is a SECOND kind of pane write that
    `send_keys_when_idle` (built for chat text confirmed by a busy->idle turn)
    does not model: a slash command opens a modal dialog rather than starting a
    turn, so there is no busy transition to confirm against. Before this helper,
    `check_session_usage` fired `/usage` + Enter with a RAW, unguarded
    `subprocess.run(["tmux","send-keys",...])` -- no idle check, no lock, no
    log, no verification -- so on a busy/mid-turn pane the keystrokes were NOT
    recognised as a slash command (a slash command is only recognised as the
    ENTIRE input on an idle prompt) and piled up UNSUBMITTED in the input box,
    once per watchdog cycle: the "/usage repeated dozens of times" the director
    saw (DEFECT_TMUX_PANE_INJECTION REOPENED, 2026-07-14, R10 'ONE gate for ALL
    pane writers'). Routing it here closes that second bypass.

    Verify-submit-landed-or-roll-back (director's explicit requirement):
      * refuse entirely unless `_safe_to_inject` (idle + empty box + byte-stable)
        -- a slash command can NEVER be submitted mid-turn, so if we can't
        confirm idle we send nothing at all (returns None = "unknown");
      * after sending, `parse(pane_text)` succeeding IS the read-back proof the
        command was recognised and its dialog rendered (submit landed);
      * always dismiss the dialog (`dismiss_key`); and if parse FAILED -- the
        command may be sitting unrecognised in the box -- clear the input line
        (Ctrl-U) so it can never accumulate into the [Pasted text #NNN] pile.

    Returns `parse()`'s result, or None (no-op under pytest, pane not safe,
    lock contended, or dialog never rendered). Every send is logged via the
    shared `send_keys` primitive, so a future storm is diagnosable from
    injection-log.jsonl like any other pane write."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return None
    try:
        with relay_lock(timeout=_RELAY_LOCK_TIMEOUT_SECONDS):
            ensure_live_tail(session)
            if not _safe_to_inject(session):
                return None  # never inject a slash command into a non-idle pane
            if not send_keys(session, command, "Enter"):
                return None
            time.sleep(render_wait)
            pane_text = capture_pane(session, lines=60)
            result = parse(pane_text)
            send_keys(session, dismiss_key)
            if result is None:
                # Dialog never rendered -- the command may be sitting unconsumed
                # in the input line. Clear it (Ctrl-U) so it cannot accumulate.
                send_keys(session, "C-u")
            return result
    except RelayLockTimeout:
        return None  # another daemon is mid-send -- retry next cycle
