"""Dead-man's switch -- director-flagged incident, 2026-07-09.

Deliberately OUTSIDE the tmux/supervisor stack. Doorbell failure #5 proved
that stack's own turn-granting detection (is_session_idle()'s pane-content
inspection) can silently misread state for hours while the process stays
"alive" the whole time -- the daemon never crashed, it just kept granting
the wrong verdict. A watchdog built on the SAME pane-inspection primitive
could fail for the exact same underlying reason (a misread of what the
terminal is showing), so this one uses none of it: no tmux capture, no
regex on pane content, no is_session_idle() call anywhere in this file.

Signal used instead -- objective, external, and something a stuck
supervisor cannot itself corrupt:
  - the most recent git COMMIT timestamp (real forward progress, this
    project's own definition of "done" throughout).

FAIL-SILENT REGRESSION, fixed 2026-07-14 (director P0, "the entire stack
went dark 22:12->04:00 -- no commits, no auto-process, and no ntfy telling
me it stopped"): the previous version ALSO trusted "the most recent mtime
across any file in docs/observability/" as an alive signal. That signal is
CONTAMINATED -- every background daemon (supervisor, sanity, health-check,
and this very switch's OWN 15-min log write) touches that directory each
cycle regardless of whether the main session is making any progress. So
during a 6-hour wedge (a jammed input box refusing every turn grant) the
switch logged "activity recent (0min ago) -- not blocked" every single
cycle while staged files climbed 31->59 and no commit landed. A watchdog
whose liveness signal is refreshed by the watchdog itself can never fire:
the textbook fail-silent control (R15). The fix: the ONLY progress signal
is the git commit clock, which no daemon's logging can move -- only real
work moves it. (The NTFY path was never the problem; it is a direct HTTPS
POST to ntfy.sh, independent of the tmux stack. Detection was the failure.)

FAIL-OPEN REGRESSION, fixed 2026-07-14 (director-named THEATRE control):
keying liveness on ANY git commit was itself a fail-open control. The
auto-process publish loop commits every ~15min ("Auto-process run complete:
... net=£1,521,070") -- flat no-ops with identical net figures and zero
forward work -- yet each one REFRESHED the staleness clock. So the switch
reported "not blocked" straight through a real 83-min executor-idle window
(22:03-23:26) and NEVER fired: a liveness signal a no-op background loop can
refresh is not a liveness signal (the exact watchdog-self-refresh lesson,
R15 FAIL-OPEN). The fix: liveness keys on MEANINGFUL progress only --
_last_meaningful_commit_epoch() ignores flat auto-process run-complete
commits, so a window of nothing-but-auto-process now looks as stale as it
truly is and trips the alarm.

Two alarm tiers, both suppressed only during a declared usage pause
(.usage_pause.json -- a known-quiet window, not a stall):
  - [BLOCKED]: queued work on disk (docs/staging/ not yet in done/) AND no
    commit for BLOCKED_THRESHOLD_SECONDS. The 2026-07-14 outage class --
    fires within ~45min instead of never.
  - [STALL]: no commit for SILENT_STALL_THRESHOLD_SECONDS regardless of
    staging -- the backstop for a wedged-but-empty tree.
Both re-escalate on a bounded cadence (RE_ESCALATE_SECONDS) while the
condition persists (R5: never repeat an unchanged status, but don't go
silent forever either).
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background.ntfy_utils import send_ntfy  # noqa: E402
from background import action_needed  # noqa: E402

LOG_FILE = PROJECT_DIR / "docs" / "observability" / "deadmans-switch-log.md"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
OBSERVABILITY_DIR = PROJECT_DIR / "docs" / "observability"

POLL_INTERVAL_SECONDS = 300       # 5 minutes -- a safety net, not a turn-granter
BLOCKED_THRESHOLD_SECONDS = 45 * 60   # 45 min of no commit + queued work = BLOCKED
SILENT_STALL_THRESHOLD_SECONDS = 90 * 60  # 90 min of no commit at all = STALL (backstop)
RE_ESCALATE_SECONDS = 60 * 60         # re-alert hourly while still stuck

USAGE_PAUSE_FILENAME = ".usage_pause.json"  # a declared known-quiet window

_IGNORED_STAGING_NAMES = {".gitkeep"}

# Subject prefix of the auto-process publish loop's flat run-complete commits.
# These land every ~15min with identical net figures and carry NO forward work,
# so they must NOT count as liveness (the 2026-07-14 fail-open defect).
_AUTO_PROCESS_SUBJECT_PREFIX = "Auto-process run complete"

_last_escalation_ts: float | None = None
# Transition state for the pull-loop transport alarm (OPS1_transport_failure_must_be_loud, §9),
# kept separate from the commit-clock escalation so the two alarm classes never mask each other.
_last_loop_broken_ts: float | None = None
_last_gate_violation_ts: float | None = None


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def _recent_commits(n: int = 200) -> list[tuple[float, str]]:
    """(epoch, subject) for the last n commits, newest first. Returns [] if git
    is unavailable/fails -- an unreadable commit history is treated as NO known
    progress (fails toward "looks stale," R15 fail-closed), never as recent
    activity that didn't happen. n=200 spans ~50h of pure auto-process cadence,
    comfortably past both thresholds even in a marker flood."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--format=%ct%x00%s"],
            cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            out: list[tuple[float, str]] = []
            for line in result.stdout.splitlines():
                if "\x00" not in line:
                    continue
                ct_str, subject = line.split("\x00", 1)
                try:
                    out.append((float(ct_str), subject))
                except ValueError:
                    continue
            return out
    except Exception:
        pass
    return []


def _is_auto_process_commit(subject: str) -> bool:
    """A flat auto-process run-complete commit -- the sim-publish loop's ~15min
    no-op. These carry no forward work, so they don't count as liveness."""
    return subject.strip().startswith(_AUTO_PROCESS_SUBJECT_PREFIX)


def _last_meaningful_commit_epoch() -> float:
    """Timestamp of the most recent commit that represents MEANINGFUL PROGRESS,
    not a flat auto-process no-op.

    Meaningful = a commit whose message is NOT an auto-process run-complete. (A
    genuine maturity_map.yaml level_current change is by construction never an
    auto-process commit -- those touch only report/LATEST.md/site/ -- so its
    subject already passes this filter; the two conditions coincide.)

    Fails toward 0.0 ("looks stale") when git is unreadable OR when the window
    contains nothing but auto-process commits -- in the latter case the last
    real commit is genuinely older than the whole window, so "very stale" is the
    honest answer and the alarm should fire. No daemon's logging, and no no-op
    publish loop, can move this signal; only real work does."""
    for epoch, subject in _recent_commits():
        if not _is_auto_process_commit(subject):
            return epoch
    return 0.0


def last_activity_epoch() -> float:
    """The ONLY forward-progress signal: the MEANINGFUL git commit clock.
    Deliberately NOT max()'d with docs/observability/ mtimes (that made the
    switch fail-silent, 2026-07-14) and deliberately NOT keyed on any commit
    (that made it fail-open on flat auto-process no-ops, 2026-07-14). Only a
    non-auto-process commit -- real forward work -- moves this."""
    return _last_meaningful_commit_epoch()


def _usage_pause_active() -> bool:
    """True if a usage pause is currently declared (.usage_pause.json with a
    future resume_at, written by the session when it self-pauses at ~90%). A
    declared pause is a KNOWN-quiet window, not a stall, so both alarm tiers
    are suppressed while it holds. Read directly (no session_watchdog import)
    so this stays independent of that stack. Fails toward 'not paused' (alarm
    active) on any malformed/absent file -- never suppresses on ambiguity."""
    pause_file = OBSERVABILITY_DIR / USAGE_PAUSE_FILENAME
    try:
        data = json.loads(pause_file.read_text(encoding="utf-8"))
        resume_at = datetime.fromisoformat(data["resume_at"])
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError, OSError):
        return False
    if resume_at.tzinfo is None:
        resume_at = resume_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) < resume_at


def _is_daemon_marker(name: str) -> bool:
    """Auto-process markers (run_complete_/run_pending_*.md) are the pipeline's
    OWN coordination files, not director instructions -- they must not count as
    'blocked on queued work' (R3, extended 2026-07-14 per director: 'run_complete
    markers are STILL landing in docs/staging -- the R3 exclusion is incomplete').
    A pile of unarchived markers is auto-process LAG; if that ever means genuine
    inactivity it surfaces via the [STALL] tier (the commit clock, which no marker
    can move), never as a false [BLOCKED] on instructions that don't exist."""
    return (name.startswith("run_complete_") or name.startswith("run_pending_")) and name.endswith(".md")


def _unprocessed_staging_files() -> list[str]:
    if not STAGING_DIR.is_dir():
        return []
    return sorted(
        p.name for p in STAGING_DIR.iterdir()
        if p.is_file() and p.name not in _IGNORED_STAGING_NAMES and not _is_daemon_marker(p.name)
    )


def _reping_open_action_needed_items() -> None:
    """Daily re-ping for anything genuinely waiting on Rich's own input
    (2026-07-11, director rule) -- independent of whether the tmux/
    supervisor stack itself looks stalled (that's the [BLOCKED] class
    below). An item here can sit open for days while everything else runs
    fine; the staging-activity check would never catch that on its own."""
    for entry in action_needed.due_for_reping():
        send_ntfy(action_needed.format_action_needed(
            entry["item_id"], entry["what"], entry["how"], entry["why"],
        ))
        action_needed.register_item(
            entry["item_id"], entry["what"], entry["how"], entry["why"],
        )
        log(f"Re-pinged open action-needed item: {entry['item_id']}")


def _check_pull_loop_transport() -> None:
    """Fire a transition-only, first-class LOOP_BROKEN alarm when the pull-loop transport
    cannot draw (OPS1_transport_failure_must_be_loud, §9). This is the RUNNING home for the
    alarm -- the deadman is the only periodic safety-net daemon; run_health_check() is not on
    any timer. The commit-clock tiers below catch total silence; THIS catches the specific,
    faster, typed case the commit clock misses for up to 90 min -- a loop that fires but errors
    on every draw (the day-long bug), including when the queue is a MAP draw (no staged files),
    which [BLOCKED] would never see. Distinct transition state, so it is transition-only (R5)
    and never masks / is masked by the commit-clock alarm."""
    global _last_loop_broken_ts
    try:
        from background.process_reconciler import evaluate_pull_loop
        st = evaluate_pull_loop()
    except Exception as e:  # a check that cannot run must not crash the deadman cycle
        log(f"pull-loop transport check error: {e}")
        return
    now = time.time()
    if not st["alarm"]:
        _last_loop_broken_ts = None
        return
    if _last_loop_broken_ts is not None and (now - _last_loop_broken_ts) < RE_ESCALATE_SECONDS:
        log(f"LOOP BROKEN (still) -- suppressed (re-alerts hourly): {st['detail']}")
        return
    send_ntfy(
        f"[LOOP BROKEN] Pull-loop transport cannot draw work: {st['detail']}. The autonomous "
        f"worker is idle because the TRANSPORT IS BROKEN, not because there is no work -- check "
        f".claude/hooks/pull_next_work.py (find_work / worker_seat import) and .pull_loop_health.json."
    )
    log(f"LOOP BROKEN NTFY sent: {st['detail']}")
    _last_loop_broken_ts = now


def _check_gate_wall() -> None:
    """Fire a transition-only, LOUD GATE_VIOLATION alarm when an atom was promoted across a gate
    (loop_stage idle->build) with NO director-console authorization (OPS1 gate-wall, director P0).
    Report-only detection: the loop may self-SUSTAIN through open queued work, but must never
    self-PROMOTE across a gate without the director's authenticated act. This is the RUNNING home
    for the alarm (the deadman is the only periodic safety-net daemon). Distinct transition state
    so it is transition-only (R5) and independent of the LOOP_BROKEN / commit-clock alarms."""
    global _last_gate_violation_ts
    try:
        from background.gate_authorization import evaluate_gate_wall
        st = evaluate_gate_wall()
    except Exception as e:  # a check that cannot run must not crash the deadman cycle
        log(f"gate-wall check error: {e}")
        return
    now = time.time()
    if not st["alarm"]:
        _last_gate_violation_ts = None
        return
    if _last_gate_violation_ts is not None and (now - _last_gate_violation_ts) < RE_ESCALATE_SECONDS:
        log(f"GATE VIOLATION (still) -- suppressed (re-alerts hourly): {st['detail']}")
        return
    send_ntfy(
        f"[GATE VIOLATION] {st['detail']}. An atom was promoted idle->build with NO director-console "
        f"authorization -- self-PROMOTION across a gate (allowed: self-sustain through OPEN work; "
        f"forbidden: crossing a gate without your act). Check the commit that flipped loop_stage and "
        f"docs/observability/gate_authorizations.jsonl."
    )
    log(f"GATE VIOLATION NTFY sent: {st['detail']}")
    _last_gate_violation_ts = now


def run_cycle() -> None:
    global _last_escalation_ts

    _reping_open_action_needed_items()
    _check_pull_loop_transport()
    _check_gate_wall()

    # A declared usage pause is a known-quiet window, not a stall -- suppress
    # both tiers (but keep re-ping above, which is a different alert class).
    if _usage_pause_active():
        log("Usage pause active -- known-quiet window, alarm suppressed")
        _last_escalation_ts = None
        return

    now = time.time()
    since_commit = now - last_activity_epoch()
    staged = _unprocessed_staging_files()

    blocked = bool(staged) and since_commit >= BLOCKED_THRESHOLD_SECONDS
    silent_stall = since_commit >= SILENT_STALL_THRESHOLD_SECONDS

    if not (blocked or silent_stall):
        if staged:
            log(
                f"Work queued ({len(staged)} file(s)) but commit recent "
                f"({since_commit / 60:.0f}min ago) -- not blocked"
            )
        else:
            log(f"Clean -- no queued work, last commit {since_commit / 60:.0f}min ago")
            _last_escalation_ts = None
        return

    if _last_escalation_ts is not None and (now - _last_escalation_ts) < RE_ESCALATE_SECONDS:
        log(
            f"STALL (still) -- {since_commit / 60:.0f}min since commit, "
            f"{len(staged)} file(s) queued -- suppressed (re-alerts hourly)"
        )
        return

    if blocked:
        shown = ", ".join(staged[:3]) + ("..." if len(staged) > 3 else "")
        send_ntfy(
            f"[BLOCKED] Dead-man's switch: {since_commit / 60:.0f} min since the last git "
            f"COMMIT, and {len(staged)} unprocessed staging file(s) ({shown}). The "
            f"supervisor/tmux stack or the main session may be stuck (e.g. a jammed input "
            f"box refusing turn grants) -- check the session directly."
        )
        log(f"BLOCKED NTFY sent -- {since_commit / 60:.0f}min since commit, {len(staged)} file(s) queued")
    else:  # silent_stall with an empty queue -- the backstop tier
        send_ntfy(
            f"[STALL] Dead-man's switch: {since_commit / 60:.0f} min with no git commit and "
            f"no queued work moving. The main session may be wedged even though nothing is "
            f"queued -- check it directly."
        )
        log(f"STALL NTFY sent -- {since_commit / 60:.0f}min since commit, empty queue")
    _last_escalation_ts = now


def main() -> None:
    log("Dead-man's switch started -- independent of tmux/supervisor stack")
    while True:
        try:
            run_cycle()
        except Exception as e:
            log(f"Dead-man's switch cycle error: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
