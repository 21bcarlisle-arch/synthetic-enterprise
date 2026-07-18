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

# Archive-on-answer mechanism (2026-07-14, director triage #3: "archive-on-
# answer never landed"). A stale from_rich_*.md ("Are you busy?") re-jammed
# the director's box TWICE because answered messages were never moved to
# docs/staging/done/ -- so supervisor.py kept granting a turn on it every
# ~2min and dispatcher.py kept re-surfacing it. This is the MECHANISM (a
# sweep this daemon runs every cycle), NOT a convention the interactive agent
# must remember to honour. It never deletes -- only moves to done/.
#
# Two machine-checkable "no longer live" signals, both non-agent-dependent:
#   (A) SUPERSEDED -- a strictly-newer from_rich_*.md sits in the root, i.e.
#       the director engaged again; the older ping is moot. Gated by a
#       minimum age so a genuine multi-part instruction sent as a burst
#       (several messages within minutes) is NOT swept mid-conversation.
#   (B) STALE -- older than an absolute backstop threshold; the last/only
#       lingering message that no newer engagement will ever supersede must
#       still stop re-granting turns. A day-old ping sitting in the scanned
#       root is exactly the spam this closes; moved (recoverable), never lost.
DONE_DIRNAME = "done"
# Absolute backstop: a from_rich older than this is swept even with no newer
# engagement (the last-message case). Generous -- the supervisor grants a
# turn within ~2min of a real instruction landing, so a genuinely-open item
# is actioned in minutes, never left a day; anything still sitting here after
# this long has been answered-but-not-archived (the exact defect) or is dead.
FROM_RICH_STALE_SECONDS = 24 * 3600
# A superseded (newer-engagement-exists) from_rich is only swept once it is at
# least this old, so two messages that are part of ONE burst/multi-part
# instruction are never torn apart while both are still live.
FROM_RICH_SUPERSEDE_MIN_AGE_SECONDS = 30 * 60

# Instruction-doc (advisor/director staged .md, NOT a from_rich or a daemon
# marker) stale backstop. Same defect class as the from_rich one, one channel
# over: a director/advisor instruction doc that has been actioned+consumed but
# never manually moved to done/ keeps re-granting supervisor turns forever
# (observed 2026-07-16: 6 such docs, some already archived-in-done/-on-origin,
# left stale root copies re-jamming the box every ~2min for hours). There is no
# "superseded" signal for these (unlike from_rich), so the only mechanism is an
# absolute-age sweep. Deliberately LONG (a real, still-unactioned directive must
# NEVER be swept before the loop has actioned it -- the supervisor grants a turn
# within ~2min, so anything sitting this long is consumed-but-unarchived or
# dead) and ALWAYS NTFYs on sweep, so nothing is ever lost silently: the doc is
# moved (never deleted, content preserved in done/ + git) and the director is
# told to verify it was actioned.
INSTRUCTION_STALE_SECONDS = 48 * 3600

# Standalone script -- add the repo root so `from background.ntfy_utils
# import ...` works regardless of how it\'s invoked.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from background.notify import notify  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402

# PULL-LOOP MIGRATION (2026-07-15, STAGING_PULL_LOOP_RESCOPE.md): the staging
# watcher NO LONGER types a wake into the live 'claude' pane. Keystroke
# injection is deleted (banned; five deaths). It still NOTIFIES Rich by NTFY
# when a genuinely-new staged instruction lands; the session picks the file up
# via STAGING + the pull-loop draw (supervisor.find_work polls staging on its
# own, no tmux dependency), which was always the durable guarantee anyway --
# the tmux wake was only ever a best-effort latency shortcut on top of it.


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def ntfy(msg: str):
    """Returns notify()'s result (a truthy send id on success) so callers can tell
    whether the send actually landed -- 2026-07-18 class fix, action_needed's send-
    clock must only advance on a CONFIRMED send, never merely because this was
    called."""
    return notify(msg, kind="director_echo")


_ARTIFACT_SUFFIXES = (".bak", ".orig", ".tmp", ".swp", "~")


def _is_artifact(name: str) -> bool:
    """True for non-instruction droppings that must NEVER trigger a staging
    notification: editor/git/backup artifacts, esp. the `*.local-*.bak` files
    (a changing-hash name each cycle => an endless stream of 'new' files =>
    notification spam). 2026-07-16 director: stop announcing these."""
    return name.endswith(_ARTIFACT_SUFFIXES)


def current_files() -> set[str]:
    if not STAGING_DIR.is_dir():
        return set()
    return {p.name for p in STAGING_DIR.iterdir()
            if p.is_file() and p.name not in IGNORED_NAMES and not _is_artifact(p.name)}


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
        # Do NOT resurrect a doc that has already been consumed+archived to
        # done/ (2026-07-16 re-stick root cause): while local HEAD is behind
        # origin, local_head..origin/main keeps containing the [ADVISOR-STAGED]
        # commits that first added these docs, so this bridge re-materialised
        # them into root every cycle even after they were moved to done/ --
        # re-jamming the supervisor forever. An archived copy in done/ is the
        # canonical "consumed" signal; skip it. (A genuine re-issue reuses a
        # fresh name, as advisor/director docs already do.)
        if (_done_dir() / name).exists():
            continue
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


def _done_dir() -> Path:
    """docs/staging/done/, derived from STAGING_DIR at CALL time so tests that
    monkeypatch STAGING_DIR get a matching done/ dir (see action_needed.py's
    _resolve_path for the same call-time-vs-def-time lesson)."""
    return STAGING_DIR / DONE_DIRNAME


def _from_rich_timestamp(path: Path) -> datetime:
    """The UTC datetime a from_rich_*.md represents. Parses the canonical
    `from_rich_YYYYMMDD_HHMMSS.md` name ntfy_responder.py writes; falls back
    to the file's mtime if the name doesn't parse (never raises -- a sweep
    must not crash on an oddly-named file)."""
    stem = path.name[len("from_rich_"):].removesuffix(".md")
    try:
        return datetime.strptime(stem, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        except OSError:
            return datetime.now(timezone.utc)


def archive_from_rich(path: Path) -> bool:
    """Move an answered/superseded from_rich_*.md into docs/staging/done/.
    NEVER deletes a message -- only moves it (a redundant identical copy
    already in done/ is the one exception, since the content is preserved
    there; a copy with DIFFERING content is kept under a suffixed name so
    nothing is ever lost). Idempotent: a name whose file is already gone from
    the root is a no-op success. Returns True once the message is in done/,
    False only on a real move error."""
    name = path.name

    def _cleared() -> bool:
        # The signalled state ended cleanly -> drop the fire-once register item so
        # the daily re-ping can never resurrect a notification for an archived doc.
        try:
            from background import action_needed
            action_needed.clear_item(f"staged:{name}")
        except Exception:
            pass
        return True

    if not path.exists():
        return _cleared()  # already archived / gone -- idempotent success
    done = _done_dir()
    try:
        done.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        log(f"archive-on-answer: could not create done/ for {name}: {e}")
        return False
    dest = done / name
    if dest.exists():
        try:
            if dest.read_bytes() == path.read_bytes():
                path.unlink()  # exact duplicate already preserved in done/
                return _cleared()
        except OSError:
            pass
        i = 1
        while (done / f"{path.stem}.dup{i}{path.suffix}").exists():
            i += 1
        dest = done / f"{path.stem}.dup{i}{path.suffix}"
    try:
        path.rename(dest)
        return _cleared()
    except OSError as e:
        log(f"archive-on-answer: move failed for {name}: {e}")
        return False


def sweep_answered_from_rich(now: datetime | None = None) -> list[str]:
    """Move every from_rich_*.md in the staging root that is no longer live
    (superseded by a newer engagement, or past the absolute stale backstop)
    into docs/staging/done/. Returns the list of archived filenames.

    This is the archive-on-answer MECHANISM -- run once per poll cycle by
    main(), independent of the interactive agent. A FRESH, unanswered
    from_rich (the newest one, younger than the stale backstop) is never
    touched, so the director's live question always keeps its turn-grant;
    only the moot ones stop re-jamming the box."""
    if not STAGING_DIR.is_dir():
        return []
    now = now or datetime.now(timezone.utc)
    entries = [
        (p, _from_rich_timestamp(p))
        for p in STAGING_DIR.iterdir()
        if p.is_file() and p.name.startswith("from_rich_") and p.name.endswith(".md")
    ]
    if not entries:
        return []
    newest_ts = max(ts for _, ts in entries)
    archived: list[str] = []
    for p, ts in entries:
        age = (now - ts).total_seconds()
        superseded = ts < newest_ts  # a strictly-newer from_rich exists
        stale = age >= FROM_RICH_STALE_SECONDS
        if not ((superseded and age >= FROM_RICH_SUPERSEDE_MIN_AGE_SECONDS) or stale):
            continue
        if archive_from_rich(p):
            archived.append(p.name)
            reason = "superseded" if superseded else "stale"
            log(f"archive-on-answer: swept {p.name} to done/ "
                f"({reason}, age {int(age)}s)")
    return archived


def _is_instruction_doc(p: Path) -> bool:
    """True for a staged instruction .md in the root that relies on a manual
    agent `mv` to done/ (there is no code that auto-archives it) -- i.e. an
    advisor/director doc, NOT a from_rich_*.md (swept by sweep_answered_from_rich)
    and NOT a daemon marker (run_complete_/run_pending_, archived by
    process_run_complete.py). Only these fall through every automated archive
    path, so only these can re-stick indefinitely."""
    n = p.name
    if not (p.is_file() and n.endswith(".md") and n not in IGNORED_NAMES):
        return False
    if n.startswith("from_rich_") or n.startswith("run_complete_") or n.startswith("run_pending_"):
        return False
    return True


def sweep_stale_instruction_docs(now: datetime | None = None) -> list[str]:
    """Archive-on-consumption backstop for instruction docs. Move any
    instruction .md in the staging root older than INSTRUCTION_STALE_SECONDS
    into docs/staging/done/ and NTFY the director to verify it was actioned.
    Returns the list of archived filenames.

    This closes the re-stick class the from_rich sweep already closes for its
    channel: a consumed-but-unarchived director/advisor doc no longer re-grants
    supervisor turns forever. It NEVER deletes (archive_from_rich only moves;
    content is preserved in done/ and git history) and ALWAYS alerts, so a
    genuinely-unactioned doc that ages out (e.g. during a long loop outage) is
    surfaced, not lost. The threshold is deliberately long so a live directive
    the loop simply hasn't reached yet is never swept out from under it."""
    if not STAGING_DIR.is_dir():
        return []
    now = now or datetime.now(timezone.utc)
    archived: list[str] = []
    for p in STAGING_DIR.iterdir():
        if not _is_instruction_doc(p):
            continue
        try:
            age = now.timestamp() - p.stat().st_mtime
        except OSError:
            continue
        if age < INSTRUCTION_STALE_SECONDS:
            continue
        if archive_from_rich(p):  # name-agnostic mover: content-safe + idempotent
            archived.append(p.name)
            log(f"archive-on-consumption: swept stale instruction doc {p.name} "
                f"to done/ (age {int(age)}s)")
            ntfy(f"[STAGING BACKSTOP] Auto-archived stale instruction doc "
                 f"{p.name} (unactioned {int(age / 3600)}h in staging root). "
                 f"Moved to done/ (not deleted). Verify it was actioned.")
    return archived


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
            # THE fire-once-then-daily gate (2026-07-16, same rule as escalations):
            # announce a staged doc ONCE; never re-announce while it sits open. The
            # persistent register (not just the in-memory `seen`) makes this survive
            # restarts and the tracked-state-file resets that caused the re-announce.
            from background import action_needed
            item_id = f"staged:{name}"
            if action_needed.should_notify(item_id):
                action_needed.register_item(
                    item_id,
                    what=f"New staged instruction: {name}",
                    how="Action it (staging = approval), then archive to done/.",
                    why="A staged director/advisor instruction is awaiting processing.",
                )
                # CLASS FIX (2026-07-18): register_item() above never advances the
                # send-clock -- only a CONFIRMED successful send (a truthy id) does,
                # via mark_sent(). Without this, a failed send here would still let
                # due_for_reping() consider the item "recently pinged" forever if
                # register_item stamped the clock (it no longer does) -- and
                # conversely, without mark_sent a SUCCESSFUL send here would leave
                # the item looking never-sent, so the deadman's daily sweep would
                # re-fire it every cycle instead of once a day.
                sent_id = ntfy(f"New staged instruction: {name} — pending review")
                if sent_id:
                    action_needed.mark_sent(item_id)
                log(f"Notified (once): {name}")
            else:
                log(f"Suppressed re-announce (fire-once, already open): {name}")
            actionable.append(name)
    if actionable:
        # PULL-LOOP MIGRATION (2026-07-15): no tmux wake -- the NTFY above tells
        # Rich; the session draws the file via staging + the pull-loop.
        log(f"New actionable staged file(s) notified: {', '.join(actionable)} "
            "(served via staging + pull-loop draw, no pane injection)")
    if new_files:
        seen = files
        save_seen(seen)
    return seen


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

        # Archive-on-answer sweep: move any answered/superseded/stale
        # from_rich_*.md to done/ so it stops re-granting supervisor turns.
        try:
            sweep_answered_from_rich()
        except Exception as e:
            log(f"archive-on-answer sweep error: {e}")

        # Archive-on-consumption backstop: move any long-stale instruction doc
        # (consumed but never manually archived) to done/ + NTFY, so it stops
        # re-granting supervisor turns forever (the 2026-07-16 re-stick class).
        try:
            sweep_stale_instruction_docs()
        except Exception as e:
            log(f"archive-on-consumption sweep error: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
