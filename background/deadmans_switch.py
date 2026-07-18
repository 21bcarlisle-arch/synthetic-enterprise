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

from background.notify import notify, clear_transition  # noqa: E402
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

# Transition-only + hourly re-escalate is now delegated to the ONE notification contract
# (background.notify), keyed per alarm class so they never mask each other (OPS1 sub-step 6). The
# former module-global _last_*_ts timers are gone -- notify() owns the transition state.
_COMMIT_KEY = "deadman_commit"        # BLOCKED / STALL (shared timer, tier-agnostic state)
_LOOP_BROKEN_KEY = "deadman_loop_broken"
_GATE_VIOLATION_KEY = "deadman_gate_violation"
_FORK_ORPHAN_KEY = "deadman_fork_orphan"
_WORKTREE_UNDECLARED_KEY = "deadman_worktree_undeclared"
_STATUS_STALE_KEY = "deadman_status_stale"


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
        notify(action_needed.format_action_needed(
            entry["item_id"], entry["what"], entry["how"], entry["why"],
        ), kind="real_alarm")
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
    try:
        from background.process_reconciler import evaluate_pull_loop
        st = evaluate_pull_loop()
    except Exception as e:  # a check that cannot run must not crash the deadman cycle
        log(f"pull-loop transport check error: {e}")
        return
    if not st["alarm"]:
        clear_transition(_LOOP_BROKEN_KEY)   # re-arm: a fresh break alarms immediately
        return
    # notify() owns transition-only + hourly re-escalate (state constant; the varying detail is
    # the message, not the transition state, so a changing detail never re-pages on its own).
    notify(
        f"[LOOP BROKEN] Pull-loop transport cannot draw work: {st['detail']}. The autonomous "
        f"worker is idle because the TRANSPORT IS BROKEN, not because there is no work -- check "
        f".claude/hooks/pull_next_work.py (find_work / worker_seat import) and .pull_loop_health.json.",
        kind="real_alarm", transition_key=_LOOP_BROKEN_KEY, state="BROKEN",
        re_escalate_after=RE_ESCALATE_SECONDS,
    )
    log(f"LOOP BROKEN checked (notify-gated): {st['detail']}")


def _check_gate_wall() -> None:
    """Fire a transition-only, LOUD GATE_VIOLATION alarm when an atom was promoted across a gate
    (loop_stage idle->build) with NO director-console authorization (OPS1 gate-wall, director P0).
    Report-only detection: the loop may self-SUSTAIN through open queued work, but must never
    self-PROMOTE across a gate without the director's authenticated act. This is the RUNNING home
    for the alarm (the deadman is the only periodic safety-net daemon). Distinct transition state
    so it is transition-only (R5) and independent of the LOOP_BROKEN / commit-clock alarms."""
    try:
        from background.gate_authorization import evaluate_gate_wall
        st = evaluate_gate_wall()
    except Exception as e:  # a check that cannot run must not crash the deadman cycle
        log(f"gate-wall check error: {e}")
        return
    if not st["alarm"]:
        clear_transition(_GATE_VIOLATION_KEY)
        return
    notify(
        f"[GATE VIOLATION] {st['detail']}. An atom was promoted idle->build with NO director-console "
        f"authorization -- self-PROMOTION across a gate (allowed: self-sustain through OPEN work; "
        f"forbidden: crossing a gate without your act). Check the commit that flipped loop_stage and "
        f"docs/observability/gate_authorizations.jsonl.",
        kind="real_alarm", transition_key=_GATE_VIOLATION_KEY, state="VIOLATION",
        re_escalate_after=RE_ESCALATE_SECONDS,
    )
    log(f"GATE VIOLATION checked (notify-gated): {st['detail']}")


def _check_fork_lifecycle() -> None:
    """Fire a transition-only, LOUD FORK_ORPHANS alarm when a fork branch never came home --
    unmerged past FORK_DEADLINE (director P0 fork-lifecycle, step 3). Report-first by default
    (detect + alarm, NO reap); enforce-mode (salvage-then-reap) is armed only by the director flag
    after the known orphans are triaged. This is the enforcing home for the doorbell's stated
    merge-or-reap discipline. State keys on the orphan COUNT so a change re-alerts immediately; an
    unchanged count re-escalates hourly (R5)."""
    try:
        from background.fork_reconciler import evaluate_fork_lifecycle
        st = evaluate_fork_lifecycle()
    except Exception as e:  # a check that cannot run must not crash the deadman cycle
        log(f"fork-lifecycle check error: {e}")
        return
    if not st["alarm"]:
        clear_transition(_FORK_ORPHAN_KEY)
        return
    notify(
        f"[FORK ORPHANS] {st['detail']}. Fork branches that built work and never merged home -- "
        f"the fragmentation disease. Reap-only: each is salvage-tagged then reaped (enforce-mode) "
        f"or flagged (report-first); a good orphan is recoverable from its salvage tag and "
        f"re-runnable, never auto-landed unreviewed. Triage: docs/observability/ + salvage/* tags.",
        kind="real_alarm", transition_key=_FORK_ORPHAN_KEY, state=f"orphans:{len(st['orphans'])}",
        re_escalate_after=RE_ESCALATE_SECONDS,
    )
    log(f"FORK ORPHANS checked (notify-gated): {st['detail']}")


def _check_worktree_reconcile() -> None:
    """Fire a transition-only, LOUD WORKTREE_UNDECLARED alarm when a worktree does not belong --
    not the main worktree and not tied to a live in-flight fork (director P0 step 4 / C1). Makes
    parallel OBSERVABLE: worktree accretion becomes visible instead of silent (the disease the
    reconcile discipline covered for processes but not worktrees). REPORT-ONLY -- never prunes
    (G-R3). Same mechanism as the fork lifecycle (belonging is derived from branch state), distinct
    alarm surface. State keys on the undeclared count so a change re-alerts; unchanged re-escalates
    hourly (R5)."""
    try:
        from background.fork_reconciler import evaluate_worktree_reconcile
        st = evaluate_worktree_reconcile()
    except Exception as e:  # a check that cannot run must not crash the deadman cycle
        log(f"worktree-reconcile check error: {e}")
        return
    if not st["alarm"]:
        clear_transition(_WORKTREE_UNDECLARED_KEY)
        return
    notify(
        f"[WORKTREE UNDECLARED] {st['detail']}. Worktrees that are neither main nor a live fork -- "
        f"accretion the reconcile discipline covered for processes but not worktrees. REPORT-ONLY "
        f"(never pruned by inference). Declare it or clean it up through the reconciler.",
        kind="real_alarm", transition_key=_WORKTREE_UNDECLARED_KEY,
        state=f"undeclared:{len(st['undeclared'])}", re_escalate_after=RE_ESCALATE_SECONDS,
    )
    log(f"WORKTREE UNDECLARED checked (notify-gated): {st['detail']}")


def _check_status_honesty() -> None:
    """Fire a transition-only, LOUD STATUS_STALE alarm when LATEST.md describes a non-running daemon
    or a retired governance model as current (director P0 step 5). The stale narrative, re-stamped
    with a fresh timestamp every publish, is what made the director misread the whole system as
    breached tonight. REPORT-ONLY here (the pre-commit gate makes a stale LATEST.md un-committable;
    this makes a stale LIVE one loud). State keys on the stale-claim count."""
    try:
        from background.status_honesty import evaluate_status_honesty
        st = evaluate_status_honesty()
    except Exception as e:  # a check that cannot run must not crash the deadman cycle
        log(f"status-honesty check error: {e}")
        return
    if st["honest"]:
        clear_transition(_STATUS_STALE_KEY)
        return
    notify(
        f"[STATUS STALE] {st['detail']}. LATEST.md describes a system that is not running -- the "
        f"stale narrative re-stamped fresh reads as current and misrepresents the whole system. "
        f"Regenerate the header from declared truth (running manifest + gate-wall + execution model).",
        kind="real_alarm", transition_key=_STATUS_STALE_KEY,
        state=f"stale:{len(st['stale_claims'])}", re_escalate_after=RE_ESCALATE_SECONDS,
    )
    log(f"STATUS STALE checked (notify-gated): {st['detail']}")


def _check_repo_not_bare() -> None:
    """H26 (2026-07-18): fire the cause-agnostic core.bare corruption guard BETWEEN commits, not
    only at the next `tree_lock()` acquisition. `tree_lock.assert_repo_not_bare()` already covers
    the per-commit path (wired into `tree_lock().__enter__`); this gives it a periodic,
    commit-independent home too, so a bare-flip that happens while nothing is actively committing
    (the real 2026-07-18 incident: silent, mid-session, no commit in flight at the moment it
    flipped) still surfaces within one deadman cycle (<= POLL_INTERVAL_SECONDS) instead of waiting
    for whenever the next commit attempt happens to occur. The guard itself owns the
    auto-repair/alarm/transition-dedup (shared transition key, so a per-commit catch and a
    periodic catch of the SAME still-unrepaired state never double-page); this is just the
    commit-independent trigger."""
    try:
        from background.tree_lock import assert_repo_not_bare, RepoBareError
    except Exception as e:  # a check that cannot even import must not crash the deadman cycle
        log(f"repo-bare check unavailable: {e}")
        return
    try:
        assert_repo_not_bare()
    except RepoBareError as e:
        log(f"REPO BARE caught by periodic check (auto-repair attempted, alarm sent): {e}")
    except Exception as e:  # any other failure must not crash the deadman cycle
        log(f"repo-bare check error: {e}")


def run_cycle() -> None:
    _reping_open_action_needed_items()
    _check_pull_loop_transport()
    _check_gate_wall()
    _check_fork_lifecycle()
    _check_worktree_reconcile()
    _check_status_honesty()
    _check_repo_not_bare()

    # A declared usage pause is a known-quiet window, not a stall -- suppress
    # both tiers (but keep re-ping above, which is a different alert class).
    if _usage_pause_active():
        log("Usage pause active -- known-quiet window, alarm suppressed")
        clear_transition(_COMMIT_KEY)
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
            # Fully clean re-arms the alarm (matches the prior _last_escalation_ts = None here,
            # and NOT in the staged-but-recent branch above).
            log(f"Clean -- no queued work, last commit {since_commit / 60:.0f}min ago")
            clear_transition(_COMMIT_KEY)
        return

    if blocked:
        shown = ", ".join(staged[:3]) + ("..." if len(staged) > 3 else "")
        msg = (
            f"[BLOCKED] Dead-man's switch: {since_commit / 60:.0f} min since the last git "
            f"COMMIT, and {len(staged)} unprocessed staging file(s) ({shown}). The "
            f"supervisor/tmux stack or the main session may be stuck (e.g. a jammed input "
            f"box refusing turn grants) -- check the session directly."
        )
    else:  # silent_stall with an empty queue -- the backstop tier
        msg = (
            f"[STALL] Dead-man's switch: {since_commit / 60:.0f} min with no git commit and "
            f"no queued work moving. The main session may be wedged even though nothing is "
            f"queued -- check it directly."
        )
    # BLOCKED and STALL share ONE transition (state "STUCK") so a tier flip within the re-escalate
    # window does not re-page -- exactly the prior shared-_last_escalation_ts behaviour, now in the
    # contract. notify() owns transition-only + hourly re-escalate.
    notify(msg, kind="real_alarm", transition_key=_COMMIT_KEY, state="STUCK",
           re_escalate_after=RE_ESCALATE_SECONDS)
    log(f"commit-clock alarm checked (notify-gated) -- {since_commit / 60:.0f}min since commit")


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
