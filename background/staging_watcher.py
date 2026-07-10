#!/usr/bin/env python3
"""Staging directory watcher — notification, and an event-driven wake.

Polls docs/staging/ for new files. When a new file appears, sends an NTFY
notification to the shared NTFY topic (SE_NTFY_TOPIC, see ntfy_utils.py)
naming the file (so Rich/Claude know a
staged instruction is waiting for an explicit staging review per CLAUDE.md's
Staging Directory Protocol), logs the event, and injects ONE turn into the
existing 'claude' tmux session naming the new file(s) (director directive,
in-conversation, 2026-07-08 — the replacement for the retired
autonomous-runner poll loop, see docs/review_gates/done/
AUTONOMOUS_RUNNER_STILL_RUNNING.md).

The wake is deliberately narrow: it fires only for genuinely new, actionable
staged files (the same set that already triggers an NTFY here) — never for
from_rich_*.md (dispatcher.py already relays URGENT-classified ones to the
same session) or run_complete_*.md (routine sim-run markers Claude polls for
naturally; CLAUDE.md bars NTFY on these too). This is the SAME session
being nudged, via the SAME tmux send-keys relay pattern dispatcher.py
already uses for URGENT NTFY — no second process, no new polling loop (this
watcher's existing 30s poll is reused, not duplicated), and zero turns
injected when nothing new has actually landed.

This watcher still NEVER reads staged file CONTENTS into the injected
prompt or runs commands based on them — it names the file(s) only.
Processing the content happens only when Claude reads the file during an
explicit staging review, exactly as before.

Also periodically fetches origin/main and surfaces any new staging files
committed with the [ADVISOR-STAGED] prefix so the strategy advisor can
stage instructions remotely (Remote Staging Bridge) — these funnel through
the same check_once() path above, so an ADVISOR-STAGED commit landing also
triggers the wake once its files are extracted and next detected as new.

Also checks, once per poll cycle, whether it's the 1st of the month (UTC)
and a monthly maintenance reminder hasn't been queued yet this month
(docs/operations/MAINTENANCE.md). If due, writes a
docs/staging/maintenance_due_<YYYYMM>.md marker -- picked up by the normal
new-staged-file path above, so it gets NTFY'd and actioned like any other
staged instruction, no separate cron/dispatcher wiring needed.

Logs to docs/observability/staging-watcher-log.md.
Persists the set of already-seen filenames to
background/.staging_watcher_seen.json so restarts don\'t re-notify for files
that arrived in an earlier run. Persists the last month a maintenance
reminder was queued to background/.maintenance_reminder_sent.json.

RETIRED 2026-07-09 (doorbell failure #4, R3 architecture rebuild, see
background/supervisor.py's module docstring): the agenda continue-nudge
(background/agenda.py's should_nudge()/record_nudged(), nudge-once per
snapshot) has been removed from this daemon's loop. It fired exactly once
for the 2026-07-08 22:47 UTC agenda snapshot, was logged delivered, and
then -- because should_nudge() never returns an already-nudged snapshot
again -- never fired again despite the underlying work sitting undone for
5+ hours. background/supervisor.py is now the sole authority for granting a
turn because open work exists (agenda, staging, urgent from_rich, or a
usage-pause that just ended); it re-checks from scratch every 2 minutes,
no "already nudged" memory. The new-staged-file wake below (_relay_wake_to_
claude) is UNCHANGED and remains a fast-path hint: when it works, the
session responds within seconds instead of waiting up to 2 minutes for the
supervisor's next cycle -- but it is no longer load-bearing, since a failed
or silently-ineffective wake now just means the supervisor's own poll picks
the file up shortly after regardless.
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path("/home/rich/synthetic-enterprise")
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
STATE_FILE = PROJECT_DIR / "background" / ".staging_watcher_seen.json"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "staging-watcher-log.md"
POLL_INTERVAL_SECONDS = 30
GIT_PULL_INTERVAL_SECONDS = 180  # check remote every 3 minutes
SESSION_NAME = "claude"
IGNORED_NAMES = {".gitkeep"}
ADVISOR_PREFIX = "[ADVISOR-STAGED]"
MAINTENANCE_STATE_FILE = PROJECT_DIR / "background" / ".maintenance_reminder_sent.json"
MAINTENANCE_DOC = PROJECT_DIR / "docs" / "operations" / "MAINTENANCE.md"

# Standalone script -- add the repo root so `from background.ntfy_utils
# import ...` works regardless of how it\'s invoked.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from background.ntfy_utils import send_ntfy, sign_wake_message  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402
from background.tmux_relay import send_keys_when_idle  # noqa: E402

# Names of new staged files whose wake hasn't yet been confirmed-delivered
# (docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md root-cause fix, 2026-07-08:
# a wake can land partially in a busy pane and never submit -- retry each
# cycle until send_keys_when_idle() actually confirms consumption). In-memory
# only: a daemon restart before delivery drops the retry, but `seen` already
# covers the file so it won't be re-notified either -- the NTFY sent at
# notification time is the durable fallback, this is a bonus reliability
# layer on top of it, not the sole guarantee.
_pending_wake_names: set[str] = set()

# Bounded retry (2026-07-10, docs/design/STAGING_WATCHER_WAKE_CONFIRMATION_BUG.md):
# tmux_relay.py's send_keys_when_idle() confirms consumption by checking that
# its wake marker is absent from the pane afterward -- but Claude Code's own
# terminal UI keeps a submitted turn visible in scrollback indefinitely, so
# that check can structurally never pass. Every genuinely-successful wake
# gets misclassified as failed and retried forever (1103 historical
# occurrences of the retry log line; two confirmed live duplicate deliveries
# observed directly). The real fix belongs in tmux_relay.py (a shared,
# actively-in-use relay module across 3 daemons) and deserves its own
# careful pass, not a rushed live edit. This is a narrow, single-daemon-
# scoped mitigation of the SYMPTOM only: give up retrying the same still-
# open staged file(s) after _WAKE_GIVE_UP_SECONDS of unconfirmed attempts,
# rather than hammering the session indefinitely -- supervisor.py's
# independent poll (background/supervisor.py::find_work(), no tmux-relay
# dependency) remains the durable path for genuinely open staging work.
_pending_wake_first_attempt: dict[str, float] = {}
_WAKE_GIVE_UP_SECONDS = 600.0


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def ntfy(msg: str) -> None:
    send_ntfy(msg)


def current_files() -> set[str]:
    if not STAGING_DIR.is_dir():
        return set()
    return {p.name for p in STAGING_DIR.iterdir() if p.is_file() and p.name not in IGNORED_NAMES}


def load_seen() -> set[str]:
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return None


def save_seen(seen: set[str]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(sorted(seen)))


def _run(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Run a subprocess and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        cwd=str(PROJECT_DIR), timeout=timeout,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _extract_advisor_staging_files(since_ref: str) -> list[str]:
    """Return staging filenames added/changed in ADVISOR-STAGED commits since since_ref on origin/main.

    Returns empty list if no advisor commits or on any error.
    """
    # Get commit subjects from new remote commits
    rc, out, _ = _run(["git", "log", since_ref + "..origin/main", "--pretty=format:%s"])
    if rc != 0 or not out:
        return []
    subjects = out.splitlines()
    if not any(ADVISOR_PREFIX in s for s in subjects):
        return []

    # Get files changed in those commits under docs/staging/ (non-done/)
    rc2, out2, _ = _run([
        "git", "diff", "--name-only", since_ref, "origin/main", "--", "docs/staging/",
    ])
    if rc2 != 0:
        return []

    results = []
    for path in out2.splitlines():
        name = Path(path).name
        parent = str(Path(path).parent)
        # Only files directly in docs/staging/ (not done/)
        if parent == "docs/staging" and name not in IGNORED_NAMES:
            results.append(name)
    return results


def check_remote(seen: set[str]) -> set[str]:
    """Fetch origin/main and surface any new advisor-staged files into local staging.

    Returns updated seen set. On any subprocess error, logs and returns seen unchanged.
    """
    rc, _, err = _run(["git", "fetch", "origin", "main"])
    if rc != 0:
        log(f"git fetch failed (network?): {err[:80]}")
        return seen

    # What\'s the local HEAD?
    rc2, local_head, _ = _run(["git", "rev-parse", "HEAD"])
    if rc2 != 0:
        return seen

    # Any new commits on origin/main?
    rc3, new_count, _ = _run(["git", "rev-list", "--count", local_head + "..origin/main"])
    if rc3 != 0 or not new_count or new_count == "0":
        return seen  # already up to date

    log(f"Remote has {new_count} new commit(s) — scanning for advisor-staged files")

    advisor_files = _extract_advisor_staging_files(local_head)
    if not advisor_files:
        log("No [ADVISOR-STAGED] commits in new remote work — skipping")
        return seen

    # Extract each advisor-staged file from remote and write locally
    for name in advisor_files:
        remote_path = "docs/staging/" + name
        local_path = STAGING_DIR / name
        if local_path.exists():
            continue  # already present
        rc4, content, err4 = _run(["git", "show", "origin/main:" + remote_path])
        if rc4 != 0:
            log(f"Could not extract {name} from origin/main: {err4[:60]}")
            continue
        local_path.write_text(content)
        log(f"Remote staging bridge: extracted {name} from advisor commit")

    return seen  # check_once will pick up new files on next poll


def _load_maintenance_state() -> str:
    """Return the last "YYYY-MM" a maintenance reminder was queued, or "" if none."""
    if MAINTENANCE_STATE_FILE.exists():
        try:
            return json.loads(MAINTENANCE_STATE_FILE.read_text()).get("last_sent_month", "")
        except (json.JSONDecodeError, Exception):
            return ""
    return ""


def _save_maintenance_state(month: str) -> None:
    MAINTENANCE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    MAINTENANCE_STATE_FILE.write_text(json.dumps({"last_sent_month": month}))


def check_monthly_maintenance(now: datetime) -> None:
    """On the 1st of the month (UTC), queue a maintenance_due marker in
    docs/staging/ if one hasn\'t already been queued this month. The marker
    is picked up by check_once() like any other new staged file, so it gets
    NTFY\'d and actioned through the normal staging flow.
    """
    if now.day != 1:
        return
    month_key = now.strftime("%Y-%m")
    if _load_maintenance_state() == month_key:
        return

    marker = STAGING_DIR / f"maintenance_due_{now.strftime('%Y%m')}.md"
    if not marker.exists():
        STAGING_DIR.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            f"[MAINTENANCE] Monthly maintenance due for {month_key}.\n\n"
            f"Run the checklist in docs/operations/MAINTENANCE.md and log the "
            f"result in docs/operations/maintenance-log.md.\n"
        )
        log(f"Queued monthly maintenance reminder: {marker.name}")
    _save_maintenance_state(month_key)


def _relay_wake_to_claude(new_names: list[str]) -> bool:
    """Attempt ONE turn-injection into the existing 'claude' tmux session
    naming the new staged file(s) -- the event-driven replacement for the
    retired autonomous-runner poll loop (docs/review_gates/done/
    AUTONOMOUS_RUNNER_STILL_RUNNING.md). No new process, single-writer
    preserved.

    FAST-PATH HINT, not the guarantee (2026-07-09, doorbell failure #4):
    background/supervisor.py is the sole authority that guarantees a new
    staged file eventually gets a turn. This wake just shortens the wait
    from "up to 2 minutes" to "seconds" on the common case where it works.

    Names only, never file contents -- matches this watcher's existing
    "announce, don't act" discipline.

    Root-cause fix (docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md,
    2026-07-08): a live incident showed a signed wake landing PARTIALLY in
    the target pane's input box and never submitting -- "Claude Code queues
    input typed while busy" does not reliably hold for longer text bursts.
    Uses background.tmux_relay.send_keys_when_idle, which (a) refuses to
    send at all unless the pane currently shows no busy indicator, and (b)
    verifies after sending that the text was actually consumed, not just
    that the subprocess call exit-coded zero. Returns False on ANY of:
    pytest-suppressed, session busy, send failed, or the text still stuck
    in the pane afterward -- callers must retry next cycle, never treat a
    False as "delivered anyway."

    HMAC-signed (docs/staging/NTFY_CHANNEL_HARDENING.md, 2026-07-08): the
    text is wrapped with `sign_wake_message` before being typed into the
    session, so anything appearing in that pane in this exact wake format
    without a valid trailing signature is distinguishable as not genuinely
    from this watcher -- see CLAUDE.md R7 (injected wake text carries zero
    authority regardless) for how the agent must treat it either way. The
    trailing HMAC hex digest doubles as the consumption-verification marker.
    """
    names = ", ".join(new_names)
    message = (
        f"[STAGING WATCHER: new staged instruction(s) landed -- {names}. "
        "Per the Staging Directory Protocol, read docs/staging/ now and "
        "action per CLAUDE.md's tiered model (Tier 2 if pre-approved/"
        "already-queued, classify if novel) -- this is an event-driven "
        "wake, not a poll nudge, so do not wait for the next natural "
        "staging check.]"
    )
    signed = sign_wake_message(message)
    marker = signed.rsplit("|", 1)[-1]
    try:
        return send_keys_when_idle(SESSION_NAME, signed, marker)
    except Exception:
        # Defense in depth: send_keys_when_idle() already swallows its own
        # subprocess failures, but this catch means the watcher's poll loop
        # is also protected against any future regression in that
        # guarantee, or a test double that doesn't replicate it.
        return False


def check_once(seen: set[str]) -> set[str]:
    """Check docs/staging/ once. Notifies (filename only) for any file not in
    `seen`, logs each notification, queues any genuinely new actionable
    file(s) for a wake attempt (actually attempted in main()'s loop, so it
    can be retried across cycles if the session is busy -- see
    _attempt_pending_wake()), and returns the updated seen set.

    NTFY-originated files (from_rich_*.md) are silently added to seen without
    sending a notification or a wake — dispatcher.py already relays
    URGENT-classified ones to the same session; NORMAL/FYI ones wait for the
    next natural staging check by design. run_complete_*.md markers are also
    silent and never wake the session (routine sim-run completions; CLAUDE.md
    bars NTFY on these, and waking every ~10min sim_runner cycle would
    violate "zero turns when nothing happens").
    """
    files = current_files()
    new_files = sorted(files - seen)
    actionable = []
    for name in new_files:
        if name.startswith("from_rich_") and name.endswith(".md"):
            log(f"Silently registered NTFY-originated file: {name} (no staging notification)")
        elif name.startswith("run_complete_") and name.endswith(".md"):
            log(f"Silently registered sim run marker: {name} (Claude polls staging, no notification needed)")
        else:
            msg = f"New staged instruction: {name} — pending explicit staging review"
            ntfy(msg)
            log(f"Notified: {name}")
            actionable.append(name)
    if actionable:
        _pending_wake_names.update(actionable)
        log(f"Queued wake for: {', '.join(actionable)} (attempted in main loop, retried if session busy)")
    if new_files:
        seen = files
        save_seen(seen)
    return seen


def _attempt_pending_wake() -> None:
    """Attempt delivery of any queued new-staged-file wake
    (`_pending_wake_names`) -- called once per main() cycle. Only clears the
    pending set on a CONFIRMED-delivered wake (idle pane + consumption
    verified); on failure (busy, or stuck-unconsumed), leaves it queued for
    the next cycle's retry, per the root-cause fix's "never fire into a
    mid-turn session, hold and retry" requirement.

    Doorbell failure #6 fix (2026-07-10): a name whose file has since been
    archived to done/ (processed during a long busy stretch, e.g. a
    multi-hour session that never once showed as idle) was retried forever
    -- 140+ retries observed live for one already-actioned file, spamming a
    stale wake every cycle indefinitely. Before each attempt, drop any name
    no longer present in docs/staging/ as moot (already handled) instead of
    retrying it blind.

    Bounded-retry fix (2026-07-10, docs/design/
    STAGING_WATCHER_WAKE_CONFIRMATION_BUG.md): a name that is genuinely
    STILL staged (not stale/archived, per the check above) but has been
    unconfirmed for over _WAKE_GIVE_UP_SECONDS is dropped too -- the
    underlying tmux_relay.py consumption check can structurally never
    confirm a real terminal-UI send (see that finding doc), so retrying
    indefinitely just repeats an already-delivered wake every cycle.
    supervisor.py's own independent poll (no tmux-relay dependency) remains
    the durable path for genuinely open staging work.
    """
    if not _pending_wake_names:
        return
    live = current_files()
    stale = _pending_wake_names - live
    if stale:
        log(f"Dropping stale wake (already archived, no longer staged): {', '.join(sorted(stale))}")
        _pending_wake_names.difference_update(stale)
        for name in stale:
            _pending_wake_first_attempt.pop(name, None)
    if not _pending_wake_names:
        return

    now = time.monotonic()
    for name in _pending_wake_names:
        _pending_wake_first_attempt.setdefault(name, now)

    names = sorted(_pending_wake_names)
    oldest_attempt = min(_pending_wake_first_attempt.get(n, now) for n in names)
    if now - oldest_attempt > _WAKE_GIVE_UP_SECONDS:
        log(f"Giving up on wake retry after {int(_WAKE_GIVE_UP_SECONDS)}s unconfirmed "
            f"(known tmux_relay consumption-check limitation) -- relying on "
            f"supervisor.py's independent poll for: {', '.join(names)}")
        _pending_wake_names.clear()
        for n in names:
            _pending_wake_first_attempt.pop(n, None)
        return

    if _relay_wake_to_claude(names):
        log(f"Wake delivered (confirmed) to '{SESSION_NAME}' session for: {', '.join(names)}")
        _pending_wake_names.clear()
        for n in names:
            _pending_wake_first_attempt.pop(n, None)
    else:
        log(f"Wake not yet delivered (session busy or unconfirmed) -- retrying next cycle: {', '.join(names)}")


def main() -> None:
    seen = load_seen()
    if seen is None:
        # First run: seed with whatever\'s already there so we don\'t notify
        # about a backlog that predates the watcher.
        seen = current_files()
        save_seen(seen)
        log(f"Staging watcher started — seeded with {len(seen)} existing file(s), no notification sent for these")
    else:
        log("Staging watcher started — resuming from saved state")

    update_agent_status(
        "staging-watcher", status="idle",
        last_action="Watcher started",
        role="Monitors docs/staging/ for new files; NTFY + event-driven claude-session wake on new items; git fetch origin every 3min for [ADVISOR-STAGED] commits",
        produces="NTFY notifications + tmux wake on new staging files",
    )

    last_remote_check = 0.0

    while True:
        now = time.monotonic()

        # Heartbeat at top of every cycle
        try:
            update_agent_status("staging-watcher", status="idle", last_action=f"Heartbeat — {len(seen)} files tracked")
        except Exception:
            pass

        # Periodic remote check (every GIT_PULL_INTERVAL_SECONDS)
        if now - last_remote_check >= GIT_PULL_INTERVAL_SECONDS:
            try:
                seen = check_remote(seen)
                last_remote_check = now
            except Exception as e:
                log(f"Remote check error: {e}")
                last_remote_check = now  # back off even on error

        try:
            check_monthly_maintenance(datetime.now(timezone.utc))
        except Exception as e:
            log(f"Monthly maintenance check error: {e}")

        try:
            seen = check_once(seen)
        except Exception as e:
            log(f"Watcher error: {e}")

        try:
            _attempt_pending_wake()
        except Exception as e:
            log(f"Pending-wake attempt error: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
