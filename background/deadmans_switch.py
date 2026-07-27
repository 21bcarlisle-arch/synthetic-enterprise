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
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background.notify import notify, clear_transition  # noqa: E402
from background import action_needed  # noqa: E402
from background.primary_state_scan import drawable_undrawn_mints  # noqa: E402  (LAW C independent read)

LOG_FILE = PROJECT_DIR / "docs" / "observability" / "deadmans-switch-log.md"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
OBSERVABILITY_DIR = PROJECT_DIR / "docs" / "observability"

POLL_INTERVAL_SECONDS = 300       # 5 minutes -- a safety net, not a turn-granter
BLOCKED_THRESHOLD_SECONDS = 45 * 60   # 45 min of no commit + queued work = BLOCKED
SILENT_STALL_THRESHOLD_SECONDS = 90 * 60  # 90 min of no commit at all = STALL (backstop)
RE_ESCALATE_SECONDS = 60 * 60         # re-alert hourly while still stuck
# EIGHTH CLASS escalation duty (2026-07-27, DIRECTOR_RULING): rest exceeding 2h while any mint is
# open, or exceeding 6h in any circumstance, MUST raise an [ACT] -- neither suppressed by the
# proven-rest fold (that fold silenced the 42h stall). "A machine that rests for 42 hours must be
# shouting, not resting quietly. Silence for a working day is itself the defect."
OPEN_MINT_REST_THRESHOLD_SECONDS = 2 * 60 * 60   # any blocked mint open + rest > 2h -> [ACT]
HARD_REST_CAP_SECONDS = 6 * 60 * 60              # rest > 6h regardless of mints/proven-rest -> [ACT]
_PLANNER_MINTED_PREFIX = "PLANNER_MINTED_"

USAGE_PAUSE_FILENAME = ".usage_pause.json"  # a declared known-quiet window

_IGNORED_STAGING_NAMES = {".gitkeep"}

# Subject prefix of the auto-process publish loop's flat run-complete commits.
# These land every ~15min with identical net figures and carry NO forward work,
# so they must NOT count as liveness (the 2026-07-14 fail-open defect).
_AUTO_PROCESS_SUBJECT_PREFIX = "Auto-process run complete"

# EIGHTH CLASS (2026-07-27, DIRECTOR_RULING_EIGHTH_CLASS): auto-process was not the only no-op
# commit refreshing the liveness clock. Two more classes of NON-WORK commit land in a resting
# window and equally falsely reset "time since last commit":
#   * `chore(liveness): publish heartbeat ...` -- the 2026-07-25 liveness-on-SKIP fix commits these
#     roughly every ~30min so published liveness survives a content-unchanged run. A deadman keyed
#     on "any non-auto-process commit" sees them as forward work and reads healthy forever.
#   * `planner RUNG-7: rest-with-proof ...` -- the planner's OWN rest declaration. On 2026-07-27 the
#     single most-recent non-auto-process commit WAS this bookkeeping commit; the deadman treated the
#     machine's "I am resting" note as evidence the machine was working. A watchdog whose liveness
#     signal is refreshed by the very act of declaring rest can never fire (the R15 fail-open lesson,
#     third occurrence). The fix: the commit clock counts WORK commits only -- chore/* and the
#     planner's rest-proof are excluded, so a window of nothing-but-those looks as stale as it is.
_NON_PROGRESS_SUBJECT_PREFIXES = (
    _AUTO_PROCESS_SUBJECT_PREFIX,
    "chore(",                    # chore(liveness), chore(*) -- housekeeping, never forward work
    "planner RUNG",              # the planner's own rest-with-proof / mint bookkeeping commit
)

# Transition-only + hourly re-escalate is now delegated to the ONE notification contract
# (background.notify), keyed per alarm class so they never mask each other (OPS1 sub-step 6). The
# former module-global _last_*_ts timers are gone -- notify() owns the transition state.
_COMMIT_KEY = "deadman_commit"        # BLOCKED / STALL (shared timer, tier-agnostic state)
_OPEN_MINT_KEY = "deadman_open_mint"          # EIGHTH CLASS: blocked mints open while resting
_HARD_REST_CAP_KEY = "deadman_hard_rest_cap"  # EIGHTH CLASS: rest > 6h in any circumstance
_DRAWABLE_UNDRAWN_KEY = "deadman_drawable_undrawn"  # LAW C: self-drawable mint undrawn while resting
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


def _is_non_progress_commit(subject: str) -> bool:
    """A NON-WORK commit that must not refresh the liveness clock: an auto-process run-complete,
    a chore/* housekeeping commit (incl. chore(liveness) heartbeat publishes), or the planner's own
    rest-with-proof/mint bookkeeping commit. EIGHTH CLASS (2026-07-27): only a commit outside ALL of
    these classes counts as forward progress. Case-sensitive prefix match on the trimmed subject."""
    s = subject.strip()
    return any(s.startswith(pfx) for pfx in _NON_PROGRESS_SUBJECT_PREFIXES)


def _last_meaningful_commit_epoch() -> float:
    """Timestamp of the most recent commit that represents MEANINGFUL PROGRESS,
    not a flat no-op.

    Meaningful = a commit that is NOT in any non-progress class (`_is_non_progress_commit`):
    not an auto-process run-complete, not a chore/* housekeeping / liveness-heartbeat commit,
    and not the planner's own rest-with-proof bookkeeping commit (EIGHTH CLASS, 2026-07-27). (A
    genuine maturity_map.yaml level_current change is by construction never any of these -- those
    touch only report/LATEST.md/site/ or observability markers -- so its subject already passes
    this filter.)

    Fails toward 0.0 ("looks stale") when git is unreadable OR when the window
    contains nothing but auto-process commits -- in the latter case the last
    real commit is genuinely older than the whole window, so "very stale" is the
    honest answer and the alarm should fire. No daemon's logging, and no no-op
    publish loop, can move this signal; only real work does."""
    for epoch, subject in _recent_commits():
        if not _is_non_progress_commit(subject):
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


# in_progress/ mis-park detection: the SAME canonical function the supervisor draw uses
# (background/staging_disposition) so the deadman [BLOCKED] alarm and the tick's SELF-RECOVERY of
# mis-parked work can never drift. See that module for the full rationale (the 2026-07-20 3-hour
# silent stall). Here it feeds the queued-work set so mis-parked actionable work pages within
# BLOCKED_THRESHOLD as well as being self-recovered by the draw.
_IN_PROGRESS_DIR = STAGING_DIR / "in_progress"


def _misparked_actionable_in_progress() -> list[str]:
    """List in_progress/ docs a worker mis-parked as blocked when their open sub-item is actionable
    NOW. Delegates to the canonical detection; never raises (must not crash the deadman cycle)."""
    try:
        from background.staging_disposition import misparked_actionable_in_progress
        return ["in_progress/" + n for n in misparked_actionable_in_progress(_IN_PROGRESS_DIR)]
    except Exception:
        return []


def _open_blocked_mints() -> list[tuple[str, str]]:
    """(filename, blocking-reason) for every BLOCKED PLANNER_MINTED_* mint parked in in_progress/.
    Read DIRECTLY off disk here (the deadman's whole ethos: trust objective disk/git state, never a
    live heartbeat or another daemon's verdict -- so it stays independent of the supervisor's own
    rest logic, the thing that mis-declared rest legitimate). A `SUPERVISOR_DRAW: self-drawable`
    mint is EXCLUDED (drawable, surfaced by the tick's draw, not a blocker). Reason parsed from the
    mint's own UNBLOCKS/blocked_on line, else a generic. Never raises (must not crash the cycle).
    Reads `STAGING_DIR / in_progress` LIVE (not the frozen `_IN_PROGRESS_DIR`) so the test fixture's
    STAGING_DIR patch isolates it -- the same live-read discipline `_unprocessed_staging_files` uses."""
    ip = STAGING_DIR / "in_progress"
    out: list[tuple[str, str]] = []
    try:
        files = sorted(ip.glob(_PLANNER_MINTED_PREFIX + "*.md"))
    except OSError:
        return []
    for f in files:
        try:
            body = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if re.search(r"SUPERVISOR_DRAW:\s*self-drawable", body[:600]):
            continue
        reason = "blocked (reason unstated in the mint doc)"
        for pat in (r"UNBLOCKS?(?:\s+ON)?:\s*([^\n]+)", r"blocked_on:\s*([^\n]+)"):
            m = re.search(pat, body, re.IGNORECASE)
            if m:
                s = re.sub(r"[*`>~]", "", m.group(1)).strip()
                if s:
                    reason = (s[:160] + "…") if len(s) > 161 else s
                    break
        out.append((f.name, reason))
    return out


def _check_open_mint_escalation(since_commit: float) -> None:
    """EIGHTH CLASS escalation duty (2026-07-27, director ruling). Two independent [ACT] triggers,
    NEITHER suppressed by the proven-rest fold (which is exactly what silenced the 42h stall):
      * OPEN-MINT: any BLOCKED mint open AND rest (since the last WORK commit) >= 2h -> [ACT] naming
        each blocked mint and what it is blocked on, so the director can unblock / re-scope / wall it.
      * HARD CAP: rest >= 6h in ANY circumstance (even with no mint open) -> [ACT] backstop.
    Both are transition-only + hourly re-escalate via notify() (OPEN-MINT keyed on the blocked-set
    signature so a changed set re-alerts immediately; the CAP on a constant flag), so a stable state
    pages once then hourly, never every 5-min cycle. `since_commit` is on the WORK-only clock (the
    H2 fix), so a window of nothing-but-liveness/chore/rest-proof commits still trips these."""
    blockers = _open_blocked_mints()
    if blockers and since_commit >= OPEN_MINT_REST_THRESHOLD_SECONDS:
        detail = "; ".join(f"{n} -> {r}" for n, r in blockers)
        notify(
            f"[ACT] {len(blockers)} minted work item(s) BLOCKED and un-worked for "
            f"{since_commit / 3600:.1f}h (no forward-work commit) -- the machine is resting beside "
            f"open mints, not working them. Escalate each (unblock / re-scope / wall): {detail}. "
            f"A blocked batch is a reason to plan more or escalate, never a licence to rest "
            f"(R17, EIGHTH CLASS 2026-07-27).",
            kind="real_alarm", transition_key=_OPEN_MINT_KEY,
            state="mints:" + ",".join(sorted(n for n, _ in blockers)),
            re_escalate_after=RE_ESCALATE_SECONDS,
        )
        log(f"OPEN-MINT escalation checked (notify-gated) -- {len(blockers)} blocked, "
            f"{since_commit / 3600:.1f}h since a work commit")
    else:
        clear_transition(_OPEN_MINT_KEY)

    if since_commit >= HARD_REST_CAP_SECONDS:
        notify(
            f"[ACT] Dead-man HARD REST CAP: {since_commit / 3600:.1f}h with no forward-WORK commit "
            f"(liveness / chore / planner-rest-proof commits excluded). Rest exceeding 6h must raise "
            f"an [ACT] in ANY circumstance -- proven-rest or not; 42h of quiet rest is itself the "
            f"defect. Check the tick: is the authorized set genuinely empty at every level, or is a "
            f"gate / mint batch deadlocked (EIGHTH CLASS 2026-07-27)?",
            kind="real_alarm", transition_key=_HARD_REST_CAP_KEY, state="CAP",
            re_escalate_after=RE_ESCALATE_SECONDS,
        )
        log(f"HARD REST CAP escalation checked (notify-gated) -- {since_commit / 3600:.1f}h since a work commit")
    else:
        clear_transition(_HARD_REST_CAP_KEY)


def _self_drawable_undrawn() -> list[tuple[str, str]]:
    """LAW C INDEPENDENT READ: (filename, title) for every SELF-DRAWABLE mint parked in
    `in_progress/`. Delegated to `background.primary_state_scan` -- a module that imports NOTHING
    from supervisor.py, so this verdict is a SECOND source that can disagree with the tick's own
    `_is_drained_and_gated()` enumeration (source A). Reads the LIVE `STAGING_DIR / in_progress`
    (not the frozen `_IN_PROGRESS_DIR`) so the test's STAGING_DIR patch isolates it, matching
    `_open_blocked_mints`. Never raises."""
    try:
        return drawable_undrawn_mints(STAGING_DIR / "in_progress")
    except Exception:
        return []


def _check_drawable_undrawn_escalation(since_commit: float) -> None:
    """LAW C escalation duty (2026-07-27, DIRECTOR_RULING_FAILURE_BIAS_LAWS). The deadman must NOT
    accept the tick's self-declared rest as sufficient -- it INDEPENDENTLY scans primary state for
    a self-drawable mint sitting undrawn. If one has sat un-worked while NO forward-WORK commit has
    landed for OPEN_MINT_REST_THRESHOLD (2h), the draw is either wedged or wrongly resting beside
    drawable work -> [ACT], un-suppressible by the proven-rest fold (fired here, before it).

    This is the counterpart to `_check_open_mint_escalation`: that pages on BLOCKED mints (awaiting
    the director); this pages on SELF-DRAWABLE mints the tick itself should have drawn. Together
    they leave no mint class silent. Keyed on the drawable-set signature so a changed set re-alerts
    immediately and a stable one pages once then hourly (R5). `since_commit` is on the WORK-only
    clock, so a window of nothing-but-liveness/chore/rest-proof commits still trips it."""
    undrawn = _self_drawable_undrawn()
    if undrawn and since_commit >= OPEN_MINT_REST_THRESHOLD_SECONDS:
        detail = "; ".join(f"{n} ({t})" for n, t in undrawn)
        notify(
            f"[ACT] {len(undrawn)} SELF-DRAWABLE mint(s) have sat UNDRAWN in in_progress/ for "
            f"{since_commit / 3600:.1f}h with no forward-work commit -- the tick is supposed to DRAW "
            f"these, so either the draw is wedged or it is resting beside drawable work. This page is "
            f"an INDEPENDENT read of disk (LAW C), so it fires even if the tick's own enumeration "
            f"reports the authorized set empty. Draw them or explain why they are stuck: {detail}. "
            f"(DIRECTOR_RULING_FAILURE_BIAS_LAWS LAW C, 2026-07-27.)",
            kind="real_alarm", transition_key=_DRAWABLE_UNDRAWN_KEY,
            state="undrawn:" + ",".join(sorted(n for n, _ in undrawn)),
            re_escalate_after=RE_ESCALATE_SECONDS,
        )
        log(f"DRAWABLE-UNDRAWN escalation checked (notify-gated) -- {len(undrawn)} self-drawable "
            f"mint(s) undrawn, {since_commit / 3600:.1f}h since a work commit")
    else:
        clear_transition(_DRAWABLE_UNDRAWN_KEY)


def _reping_open_action_needed_items() -> None:
    """Daily re-ping for anything genuinely waiting on Rich's own input
    (2026-07-11, director rule) -- independent of whether the tmux/
    supervisor stack itself looks stalled (that's the [BLOCKED] class
    below). An item here can sit open for days while everything else runs
    fine; the staging-activity check would never catch that on its own.

    CLASS FIX (2026-07-18, director-caught real incident): this used to call
    action_needed.register_item() unconditionally right after the notify()
    attempt -- regardless of whether the send actually succeeded. register_item
    stamped a fresh timestamp that should_notify()/due_for_reping() then read as
    "just pinged", so a governance [ACT] item that was registered/re-registered
    several times with EVERY send failing (a caller with no SE_NTFY_TOPIC) never
    actually paged the director's phone, yet looked quiet for the next 24h each
    time. Fix: only a CONFIRMED successful send (notify() returning a truthy id)
    advances the send-clock, via action_needed.mark_sent() -- never
    register_item(), which no longer gates anything. A failed/falsy send leaves
    the item due, so the very next deadman cycle (<= POLL_INTERVAL_SECONDS)
    retries instead of going silent for a day."""
    # CLASS FIX (2026-07-21, R10): before re-pinging, reconcile the register against
    # observable staging state -- clear any `staged:` item whose doc has left the root
    # by ANY archival route (done/, in_progress/, removed), not just the single sweep
    # that used to be the sole clear path. This is what stops an already-consumed steer
    # from being re-pinged to the director daily. Fail-safe: a reconcile error never
    # blocks the re-ping pass (Rule 0).
    try:
        for item_id in action_needed.reconcile_staged_items(STAGING_DIR):
            log(f"Reconciled (cleared) already-archived staged item: {item_id}")
    except Exception as _e:
        log(f"staged-item reconcile skipped (non-fatal): {_e}")
    for entry in action_needed.due_for_reping():
        sent_id = notify(action_needed.format_action_needed(
            entry["item_id"], entry["what"], entry["how"], entry["why"],
        ), kind="real_alarm")
        if sent_id:
            action_needed.mark_sent(entry["item_id"])
            log(f"Re-pinged open action-needed item: {entry['item_id']}")
        else:
            log(
                f"Re-ping SEND FAILED for open action-needed item: {entry['item_id']} "
                "-- send-clock left untouched, remains due next cycle (not silenced)"
            )


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


def _check_operational_layer_signal() -> None:
    """H23_publish_gate_scope_marker (L3): drive process_run_complete.py's
    independent-cadence green signal for the operational layer
    (`pytest -m operational`) on this, the ONE standing periodic timer every
    other check in this module already attaches to. COST-AWARE: the signal
    self-throttles internally (run_operational_layer_signal is a no-op unless
    OPERATIONAL_LAYER_CHECK_INTERVAL_SECONDS have elapsed since its last real
    run), so almost every 5-min deadman cycle does nothing here -- the slow
    suite runs on its own hourly cadence, never on the deadman's own cadence.
    Purely observational: it can never affect the content publish gate, only
    page on a PERSISTENT (not single-flake) daemon-lifecycle test regression."""
    try:
        from background.process_run_complete import run_operational_layer_signal
        run_operational_layer_signal()
    except Exception as e:  # a check that cannot run must not crash the deadman cycle
        log(f"operational-layer signal check error: {e}")


def _rest_is_proven_legitimate() -> bool:
    """True ONLY if it can POSITIVELY confirm there is no authorized work anywhere -- the supervisor's
    `_is_drained_and_gated()` (BUILD/SITE/DISCOVER/backlog/forward-discovery-DRAWABLE all empty). This
    is the machine truth behind the 'REST-LEGITIMATE' status line the director told the deadman to
    consume: a proven rest means no commit is EXPECTED, so the [STALL] backstop must not false-page it.

    This reads DISK truth (is there work to do?), not a live-process heartbeat, so consuming it does
    NOT surrender the deadman's independence -- it still fires on a wedged loop that HAS drawable work.
    FAIL-SAFE TOWARD ALARM (R15): any import/read error, or an inability to confirm rest, returns
    False, so the deadman keeps its power to page whenever it cannot PROVE the rest is legitimate."""
    try:
        from background.supervisor import _is_drained_and_gated
        return bool(_is_drained_and_gated())
    except Exception:
        return False


def run_cycle() -> None:
    _reping_open_action_needed_items()
    _check_pull_loop_transport()
    _check_gate_wall()
    _check_fork_lifecycle()
    _check_worktree_reconcile()
    _check_status_honesty()
    _check_repo_not_bare()
    _check_operational_layer_signal()

    # A declared usage pause is a known-quiet window, not a stall -- suppress
    # both tiers (but keep re-ping above, which is a different alert class).
    if _usage_pause_active():
        log("Usage pause active -- known-quiet window, alarm suppressed")
        clear_transition(_COMMIT_KEY)
        return

    now = time.time()
    activity_epoch = last_activity_epoch()
    since_commit = now - activity_epoch
    # EIGHTH CLASS escalation duty (2026-07-27): raise an [ACT] on open blocked mints (rest > 2h) and
    # on any rest > 6h, BEFORE and INDEPENDENT of the proven-rest fold below -- the fold silenced the
    # 42h stall, so these two triggers must not pass through it. Evaluated every cycle; notify() owns
    # transition-dedup so a stable state pages once then hourly. Guarded on a REAL, readable commit
    # clock (activity_epoch > 0): the git-unreadable sentinel (0.0 -> since_commit ~= now) is the
    # [BLOCKED]/[STALL] tier's territory (it already fails-closed toward alarm there), not a genuine
    # 6h rest window, so we don't double-page it here.
    if activity_epoch > 0:
        _check_open_mint_escalation(since_commit)
        # LAW C (2026-07-27): the INDEPENDENT primary-state read -- a self-drawable mint sitting
        # undrawn pages regardless of what the tick's own enumeration claims. Same WORK-clock guard.
        _check_drawable_undrawn_escalation(since_commit)
    # Queued work = top-level staging PLUS actionable work a worker mis-parked into in_progress/
    # (2026-07-20 class fix): the latter is invisible to the draw AND was invisible to this alarm, the
    # exact 3-hour silent stall. Including it means mis-parked actionable work pages within
    # BLOCKED_THRESHOLD, not after hours.
    staged = _unprocessed_staging_files() + _misparked_actionable_in_progress()

    blocked = bool(staged) and since_commit >= BLOCKED_THRESHOLD_SECONDS
    stall_by_clock = since_commit >= SILENT_STALL_THRESHOLD_SECONDS
    # PROVEN-REST FOLD (director console 2026-07-22, point 3): a legitimate proven rest -- the
    # authorized set is empty at EVERY level (R17) -- means NO commit is EXPECTED, so the STALL
    # backstop must NOT false-page it. Tonight's 19:33 [STALL] was exactly this: all forward-discovery
    # tracks dispositioned, every lane drained-and-gated, the tick resting with proof -- not wedged.
    # Only suppress when we can POSITIVELY confirm rest is legitimate; if work is drawable but no
    # commit is moving, that IS a real stall and still pages (fail-safe toward alarm).
    #
    # LAW C INDEPENDENCE (2026-07-27): `_rest_is_proven_legitimate()` is the SUPERVISOR's own verdict
    # (`_is_drained_and_gated()`) -- a checker trusting the checked. LAW C forbids resting on one
    # source: the deadman ALSO reads primary state directly (`_self_drawable_undrawn()`, no supervisor
    # import) and a self-drawable mint sitting undrawn VETOES the suppression, so a false "drained"
    # enumeration can no longer fold the [STALL] backstop. Two sources that can disagree.
    undrawn_now = _self_drawable_undrawn()
    proven_rest = (not staged) and stall_by_clock and _rest_is_proven_legitimate() and not undrawn_now
    silent_stall = stall_by_clock and not proven_rest

    if not (blocked or silent_stall):
        if proven_rest:
            log(
                f"[STALL] suppressed -- {since_commit / 60:.0f}min with no commit, but rest is PROVEN "
                "legitimate (authorized set empty at every level: BUILD/SITE/DISCOVER/backlog/"
                "forward-discovery-drawable all empty per _is_drained_and_gated). A proven rest is not "
                "a stall (R17). Re-arming."
            )
            clear_transition(_COMMIT_KEY)
        elif staged:
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
        if undrawn_now:
            # LAW C: primary state (independent of the tick's enumeration) shows a self-drawable
            # mint the draw has NOT picked up. Name it -- the [STALL] is not "nothing to do", it is
            # "drawable work the tick is silently not drawing".
            names = ", ".join(n for n, _ in undrawn_now[:3]) + ("..." if len(undrawn_now) > 3 else "")
            msg = (
                f"[STALL] Dead-man's switch: {since_commit / 60:.0f} min with no git commit while "
                f"{len(undrawn_now)} SELF-DRAWABLE mint(s) sit undrawn in in_progress/ ({names}). The "
                f"tick's own enumeration may report rest legitimate, but an INDEPENDENT read of disk "
                f"(LAW C) shows drawable work -- the draw is wedged or wrongly resting. Check it."
            )
        else:
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
