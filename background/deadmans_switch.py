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

from background.notify import notify, clear_transition, current_state  # noqa: E402
from background import action_needed  # noqa: E402
# Top level and no `try`, matching that module's own doctrine: if the guard cannot be imported,
# this module does not import either. An unavailable check is a FAILED check (R15).
from background.live_ledger_guard import guard_live_ledger_write  # noqa: E402
from background.harden_commit import is_harden_commit  # noqa: E402
# The append-or-monotonic episode seam and the loader above it. Same doctrine as the guard above:
# top level and no `try`, because a lost-race episode this module could not measure is a lost-race
# episode it would report as a fresh one — the self-clearing-alarm shape both modules exist for.
from background.episode_monotonic import episode_age_seconds, guard_episode  # noqa: E402
from background.episode_prior import ABSENT as EPISODE_PRIOR_ABSENT  # noqa: E402
from background.episode_prior import (  # noqa: E402
    load_episode_prior,
    preserve_unreadable,
    prior_unreadable,
)
from background.primary_state_scan import drawable_undrawn_mints  # noqa: E402  (LAW C independent read)

LOG_FILE = PROJECT_DIR / "docs" / "observability" / "deadmans-switch-log.md"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
OBSERVABILITY_DIR = PROJECT_DIR / "docs" / "observability"

POLL_INTERVAL_SECONDS = 300       # 5 minutes -- a safety net, not a turn-granter
BLOCKED_THRESHOLD_SECONDS = 45 * 60   # 45 min of no commit + queued work = BLOCKED
SILENT_STALL_THRESHOLD_SECONDS = 90 * 60  # 90 min of no commit at all = STALL (backstop)
RE_ESCALATE_SECONDS = 60 * 60         # re-alert hourly while still stuck
# WHEN A LOST PUSH RACE STOPS BEING BENIGN, and deliberately the SAME quantity this module already
# declares rather than a second tolerance for one condition. `origin_reconcile.REFUSED_RACE` is
# benign only in so far as it self-heals: the next cadence re-fetches, re-merges on the new base and
# gates again. What makes it benign is therefore not the race, it is the healing — so the question
# to ask of it is the one BLOCKED_THRESHOLD_SECONDS already answers, "how long may work sit
# undelivered before that is worth a person's attention". An open fork IS undelivered work; giving
# it its own number would be one name carrying two values by another route. Derived, not picked: at
# POLL_INTERVAL_SECONDS the self-healing retry has had nine goes by the time this elapses.
RACE_PERSISTENCE_SECONDS = BLOCKED_THRESHOLD_SECONDS
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
_FORK_ORPHAN_KEY = "deadman_fork_orphan"
_WORKTREE_UNDECLARED_KEY = "deadman_worktree_undeclared"
_WORKTREE_REAP_KEY = "deadman_worktree_reap"
_ORIGIN_FORK_KEY = "deadman_origin_fork"
#: The episode record for an UNCLOSED run of lost push races. Only the race path writes it and that
#: path can only ever EXTEND it (low-water start, high-water count, via `episode_monotonic`); only a
#: reconciler outcome that is NOT a race closes it. That asymmetry is the point — it is the shape
#: `background/self_clearing_alarm_census.py` enumerates, and the direction it fails in is toward
#: remembering an open episode rather than restarting one.
#: A MODULE-LEVEL PATH LITERAL, not a value minted inside a resolver: a state path that only exists
#: inside a function drops out of the census's own AST derivation, so this file would leave the
#: class by becoming invisible to it rather than by being repaired.
ORIGIN_RACE_EPISODE_FILE = OBSERVABILITY_DIR / ".origin_race_episode.json"
_STATUS_STALE_KEY = "deadman_status_stale"


def log(msg: str, path=None) -> None:
    """Append one line to the deadman's diagnostic log.

    A TEST PROCESS MAY NOT WRITE THE LIVE LOG (2026-08-21, finding
    `WORKER_FINDING_THE_OPERATIONAL_SUITE_WRITES_FAKE_LOOP_BROKEN_ALARMS_INTO_THE_LIVE_DEADMAN_LOG_2026-08-20`;
    the sibling call named as owed by 637d93472, which closed the same class on
    `suite_duration_watch.record`).

    CLOSED AT THE CHOKE POINT, NOT AT THE INSTANCE (R10). The reported instance is
    `tests/background/test_transport_failure_loud.py`, which is `operational`-marked, calls the
    real `_check_pull_loop_transport()`, and isolates the loud side effects (`send_ntfy`,
    `TRANSITIONS_FILE`) but not this quiet one — so every operational suite run injected
    fabricated `[LOOP BROKEN] ... cannot draw: import failed` lines into the one record a human
    reads to diagnose a broken draw loop, while the transport was `HEALTHY_IDLE` throughout.
    That same test file already monkeypatches `pull_loop_monitor.LOG_FILE` for exactly this
    reason (a 2026-07-17 comment says so), which is the class in one file: *a test isolates the
    paths it thought of*. Relying on the next author to think of one more path is what failed
    twice; the writer refuses instead.

    `path or LOG_FILE` is read at CALL time, so the established
    `monkeypatch.setattr(mod, "LOG_FILE", tmp_path / ...)` isolation keeps working unchanged and
    a caller may also pass a destination explicitly."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    dest = guard_live_ledger_write(path or LOG_FILE, writer="deadmans_switch.log")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "a") as f:
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
    a chore/* housekeeping commit (incl. chore(liveness) heartbeat publishes), the planner's own
    rest-with-proof/mint bookkeeping commit, or a HARDEN re-verification pass. EIGHTH CLASS
    (2026-07-27): only a commit outside ALL of these classes counts as forward progress.

    HARDEN exclusion (2026-07-27, WORK_DEFINITION §1 amendment, via `is_harden_commit`): a HARDEN
    re-verify "never counts as work for the deadman clock". The `chore(harden` form already matched
    the `chore(` prefix above; the new coverage is the `[HARDEN <atom>]` form, which touches real
    code/tests and so previously refreshed liveness as a "work commit" — so a HARDEN-only window now
    ages toward the rest cap exactly as a genuinely idle window does. Case-sensitive."""
    s = subject.strip()
    return is_harden_commit(s) or any(s.startswith(pfx) for pfx in _NON_PROGRESS_SUBJECT_PREFIXES)


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
    carried_nothing = _commits_that_changed_nothing()
    for epoch, subject in _recent_commits():
        if _is_non_progress_commit(subject):
            continue
        if (epoch, subject) in carried_nothing:
            continue
        return epoch
    return 0.0


def _commits_that_changed_nothing() -> set:
    """`(epoch, subject)` of recent commits whose tree equals one of their own parents'.

    THE SECOND LEG, AND THE ONE THAT WOULD HAVE CAUGHT 2026-09-02. `_is_non_progress_commit` is a
    DENYLIST OF SUBJECT PREFIXES, so it is fail-open on the next no-op class by construction --
    and the next one arrived. `origin_reconcile` put 29 empty merges on origin over three and a
    quarter hours, subject *"merge origin/main: automatic reconciliation in an isolated
    worktree"*, matching no prefix in the list. Every one of them refreshed this clock, so the
    STALL alarm stayed clear through the whole outage while nothing whatever was happening.
    Director: *"a daemon producing empty merges lit up every liveness surface you have."*

    A denylist cannot be repaired by adding this one subject to it; the class is "commits that do
    not change the repository", and `commit_narrative` decides that STRUCTURALLY -- tree against
    every parent's tree -- so no future message can walk past it.

    BOTH LEGS ARE KEPT because neither implies the other: a `chore(` commit that really does write
    files is still not forward progress, and an empty commit with a work-like subject is still not
    forward progress. Only a commit outside both classes moves the clock.

    THE LIMIT, stated rather than discovered: the join is `(epoch, subject)` and not a sha, because
    `_recent_commits` yields no sha and is pinned by name in eleven tests that supply synthetic
    rows. Two DIFFERENT commits sharing a second AND a subject line, one of them real work, would
    let that one be skipped. Unreachable in practice and it fails toward "looks stale", which is
    the safe direction for a watchdog. Returns an empty set when the history cannot be read, and
    then the subject leg stands alone exactly as it did before.
    """
    try:
        from background import commit_narrative
        rows = commit_narrative.read_commits(PROJECT_DIR, limit=200)
    except Exception:  # noqa: BLE001 - a watchdog must not die of its own instrument
        return set()
    return {(float(r["epoch"]), r["subject"]) for r in rows if r["carries_work"] is False}


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
        # THE WHOLE DOCUMENT, AND THE EXACT COMPLEMENT OF `drawable_undrawn_mints`.
        #
        # This read was `body[:600]`, hand-copied from `primary_state_scan` -- the same convention
        # with THREE implementations, two of them carrying the same bounded read. On 2026-09-02
        # `PLANNER_MINTED_reversibility_action_and_act_2026-07-29.md` was found carrying its
        # `SUPERVISOR_DRAW: self-drawable` marker at character 3513, behind 3.5 KB of tick history
        # prepended above it. Neither bounded reader could see it, so it was INVISIBLE as drawable
        # and ALARMED as blocked -- for a month, on a block its own text records as dissolved on
        # 2026-08-03. Widening 600 would only move the date.
        #
        # The two sets are now complements by construction over one file glob: a mint is drawable
        # iff it carries the self-drawable marker and no blocked marker, and blocked otherwise. A
        # document that appeared in both sets is what let the alarm and the draw disagree in
        # silence, each right by its own reading.
        if (re.search(r"SUPERVISOR_DRAW:\s*self-drawable", body, re.IGNORECASE)
                and not re.search(r"SUPERVISOR_DRAW:\s*blocked", body, re.IGNORECASE)):
            continue
        reason = "blocked (reason unstated in the mint doc)"
        for pat in (
            r"UNBLOCKS?(?:\s+ON)?:\s*([^\n]+)",
            r"blocked_on:\s*([^\n]+)",
            # R10 CLASS FIX (2026-07-29, docs/design/BLOCKED_ITEM_LITERAL_ACTS.md): four blocked
            # mints (intra_year_price_cap_granularity, money_representation_evidence,
            # payment_channel_dd_consistency_invariant, supply_start_semantic_separation) carry
            # their reason ONLY in the `<!-- BLOCK_RELEASE: <token> -- <reason> -->` marker, which
            # the two prose patterns above do not read -- so they surfaced to the director as
            # "reason unstated" when the reason WAS stated. The director's own complaint ("four
            # items blocked, reason unstated") was this parser-format mismatch, not missing reasons.
            # Read the marker as the final fallback so the false-"unstated" report cannot recur.
            r"BLOCK_RELEASE:\s*([^\n>]+)",
        ):
            m = re.search(pat, body, re.IGNORECASE)
            if m:
                s = re.sub(r"[*`>~]", "", m.group(1)).strip().rstrip("- ").strip()
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
            topic_class=_digest_classes().ACTION_NEEDED,
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
            topic_class=_digest_classes().ACTION_NEEDED,
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
            topic_class=_digest_classes().ACTION_NEEDED,
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
        ), kind="real_alarm", topic_class=_digest_classes().ACTION_NEEDED)
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
        topic_class=_digest_classes().BLOCKED_WORK,
    )
    log(f"LOOP BROKEN checked (notify-gated): {st['detail']}")


# _check_gate_wall() DELETED 2026-08-03 (director console, finishing
# DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY). It paged a LOUD [GATE VIOLATION] whenever an atom
# went loop_stage idle->build "with NO director-console authorization" -- i.e. it alarmed on the
# machine doing exactly what THE_STANDARD now requires it to do. An alarm is not a gate, but this
# one existed solely to report the absence of director authorisation, which is the class the ruling
# deletes; leaving it would have kept paging the director about non-events.


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
        topic_class=_digest_classes().DRIFT,
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
        # The message calls itself REPORT-ONLY and names accretion, which is the definition of
        # DRIFT: nothing here is due within the hour. It paged five times on 2026-08-13, each
        # about a different transient temp worktree.
        topic_class=_digest_classes().DRIFT,
    )
    log(f"WORKTREE UNDECLARED checked (notify-gated): {st['detail']}")


def _check_worktree_reap() -> None:
    """RUN the worktree reaper. Not a second report -- the one thing that CLEARS what
    `_check_worktree_reconcile` above merely names.

    THE REAPER HAD NO CALLER, ANYWHERE, FROM THE DAY IT WAS BUILT (2026-07-18) TO 2026-09-01.
    `evaluate_worktree_reap` is a careful mechanism: two modes, its own arming flag, a live/locked/
    dirty/main refusal set, no `--force`, serialized through the shared tree lock, mutation-proven
    both ways. Its own atom record predicted this in terms -- *"arm the flag and wire it to the
    reconcile-watch/deadman cadence, else the mechanism stays a library nobody calls: an unwired
    reaper is prose"* -- and then nobody wired it. The flag was armed at some point since, which is
    worse than neither: `enforce=True` on a function no scheduler calls reads, to anyone checking,
    as a reaper that is running and finding nothing to do.

    So the director's six accreting worktrees had three independent reasons to survive, and this was
    the outermost: the only worktree code on the cycle was the REPORTER. "Being reported rather than
    cleared" was the literal architecture.

    Report-only stays report-only if the flag is absent -- this call does not arm anything; it makes
    the armed mechanism run. Never raises (a check that cannot run must not crash the cycle)."""
    try:
        from background.fork_reconciler import evaluate_worktree_reap
        st = evaluate_worktree_reap()
    except Exception as e:  # a check that cannot run must not crash the deadman cycle
        log(f"worktree-reap error: {e}")
        return
    log(f"WORKTREE REAP ({'enforce' if st['enforce'] else 'report-first'}): {st['detail']}")
    if not st["alarm"]:
        clear_transition(_WORKTREE_REAP_KEY)
        return
    notify(
        f"[WORKTREE REAP] {st['detail']}",
        kind="real_alarm", transition_key=_WORKTREE_REAP_KEY,
        # Keyed on the STRANDED COUNT and not on the detail line: the detail carries paths and
        # tallies that move every cycle, and a state that moves every cycle is a transition check
        # that cannot suppress anything (which is what tree divergence has been doing to this
        # channel all day). A count that stops falling is the condition worth hearing about.
        state="stranded:{}".format(sum(1 for k in st["kept"]
                                       if _reap_refusal_is_stranded(k.get("reason", "")))),
        re_escalate_after=RE_ESCALATE_SECONDS,
        topic_class=_digest_classes().DRIFT,
    )


def _reap_refusal_is_stranded(reason: str) -> bool:
    """`fork_reconciler.refusal_is_stranded`, imported at the point of use so this module stays
    importable when that one is not. An unavailable classifier counts nothing as stranded, which
    understates the alarm rather than inventing one."""
    try:
        from background.fork_reconciler import refusal_is_stranded
    except Exception:  # noqa: BLE001
        return False
    return refusal_is_stranded(reason)


def _check_origin_fork() -> None:
    """CLOSE the fork with origin, rather than reporting that one exists.

    Director, 2026-09-02: *"a staged document arriving should never block your landing."* It was
    doing exactly that — `.last_publish_cause.json` read `behind_origin`, the site was 3.2h stale
    and five landings sat local-only, all on one condition that a document staged to origin had
    opened.

    ON THIS CADENCE AND NOT IN THE PUBLISH PATH, which is the objection the publish path's own
    refusal raises and it is a fair one: a gated merge takes longer than a publish cycle. Here it
    has as long as it needs, and by the time the publish cycle looks, the refusal has nothing left
    to refuse.

    Never raises. A reconciler that took the deadman down would trade a stale site for a dead
    watchdog."""
    try:
        from background import origin_reconcile
        r = origin_reconcile.reconcile()
    except Exception as e:  # a check that cannot run must not crash the deadman cycle
        log(f"origin-reconcile error: {e}")
        return
    log(f"ORIGIN FORK ({r['status']}): {r['detail']}")
    if r["status"] in (origin_reconcile.LEVEL, origin_reconcile.RECONCILED,
                        origin_reconcile.PUSHED, origin_reconcile.FAST_FORWARDED):
        _close_race_episode("the reconciler reached origin")
        clear_transition(_ORIGIN_FORK_KEY)
        return
    if r["status"] == origin_reconcile.GATE_RUNNING:
        # NOT A FORK CONDITION AND NOT A CLEARANCE. The gate holds the lock, so nothing was even
        # looked at; alarming would be reporting a state that was not observed, and clearing would
        # be reporting agreement that was not observed either. Wait for the next cadence.
        #
        # AND IT DOES NOT TOUCH AN OPEN RACE EPISODE EITHER, for exactly the same reason. Closing
        # it would be asserting the race healed on a cycle that did not look; extending it would be
        # counting a cycle that did not try as a loss. The episode is measured in ELAPSED TIME and
        # not in cadences precisely so that a stretch of unlooked-at cycles neither shortens nor
        # inflates it — the clock is the one thing that keeps running when nothing was observed.
        return
    if r["status"] == origin_reconcile.REFUSED_RACE:
        _report_lost_push_race(r)
        return
    _close_race_episode(f"the reconciler now reports {r['status']}, which is not a race")
    notify(
        f"[ORIGIN FORK] {r['status']}: {r['detail']} — origin is {r['behind']} commit(s) ahead and "
        f"the fork could NOT be closed automatically, so landings and publishing stay blocked "
        f"until someone reconciles.",
        kind="real_alarm", transition_key=_ORIGIN_FORK_KEY,
        state=f"{r['status']}:{r['behind']}", re_escalate_after=RE_ESCALATE_SECONDS,
        # BLOCKED_WORK, not drift: while this stands, nothing this machine does can reach origin.
        topic_class=_digest_classes().BLOCKED_WORK,
    )


def _close_race_episode(because: str) -> None:
    """End an open lost-race episode, naming what ended it. Silent when none was open.

    THE ONLY WAY THE EPISODE EVER SHORTENS, and it is deliberately not on the failure path: the
    race branch may extend the record and nothing else, so a reconciler that keeps losing cannot
    reset the clock its own alarm reads. Never raises — a bookkeeping failure here must not take
    the deadman down, and leaving a stale episode open makes the alarm louder, not quieter.
    """
    try:
        prev, verdict = load_episode_prior(ORIGIN_RACE_EPISODE_FILE)
        if verdict == EPISODE_PRIOR_ABSENT:
            return
        age = episode_age_seconds(prev, "race_since", time.time())
        log("ORIGIN FORK race episode CLOSED after {} ({} lost race(s)): {}.".format(
            "an unmeasurable interval" if age is None else f"{age / 60:.0f} min",
            prev.get("races", "?"), because))
        ORIGIN_RACE_EPISODE_FILE.unlink(missing_ok=True)
    except Exception as e:  # noqa: BLE001 — see docstring: never take the cycle down
        log(f"origin-race episode close error: {e}")


def _extend_race_episode(now: float) -> tuple[dict, bool]:
    """Record one more lost push race. Returns `(episode, measurable)`.

    `measurable` is FALSE when the record was present and could not be read. That is not the same
    fact as no record — `background/episode_prior.py` exists because five carriers had conflated
    exactly these two — and here the difference decides whether the caller may call a race benign.
    A race is benign only in so far as it is SELF-HEALING, and an unreadable record is precisely
    the state in which self-healing cannot be shown. So it is reported, never suppressed.
    """
    prev, verdict = load_episode_prior(ORIGIN_RACE_EPISODE_FILE)
    measurable = not prior_unreadable(verdict)
    if not measurable:
        preserve_unreadable(ORIGIN_RACE_EPISODE_FILE)
    proposed = {"race_since": now, "races": int(prev.get("races") or 0) + 1}
    episode = guard_episode(prev, proposed,
                            since_fields=("race_since",), streak_fields=("races",))
    dest = guard_live_ledger_write(ORIGIN_RACE_EPISODE_FILE,
                                   writer="deadmans_switch._extend_race_episode")
    dest.write_text(json.dumps(episode, indent=2), encoding="utf-8")
    return episode, measurable


def _report_lost_push_race(r: dict) -> None:
    """A lost push race has a TRUTHFUL name (`REFUSED_RACE`, landed 3d5694078) and, until now, an
    untruthful message: it fell through to the fork alarm and told the director that *"landings and
    publishing stay blocked until someone reconciles"* — for an outcome that clears itself on the
    next five-minute cadence, with nothing for him to reconcile and nothing for him to do. That
    costs the only scarce resource here, because he acts on BLOCKED_WORK.

    NOT SUPPRESSED BESIDE `GATE_RUNNING`, and the difference between the two is the whole design.
    `GATE_RUNNING` means nothing was LOOKED at. A race means the reconciler looked, built the merge,
    gated it clean, and still could not push — the fork IS open and it STAYED open. Silencing that
    outright would open a fail-silent hole exactly where it hurts most: a persistently lost race is
    a reconciler that has stopped converging, and it would never page at all.

    So the benign case is the SELF-HEALING one, and the test is whether it healed. Below
    RACE_PERSISTENCE_SECONDS the episode is logged and nothing is sent; at or beyond it the
    director hears about it — under BLOCKED_WORK, which by then is finally true — with a message
    that names what is actually happening and does not ask him to merge anything by hand.
    """
    now = time.time()
    try:
        episode, measurable = _extend_race_episode(now)
    except Exception as e:  # noqa: BLE001 — bookkeeping must not take the cycle down...
        episode, measurable = {}, False   # ...but it must not silence the race either.
        log(f"origin-race episode bookkeeping error: {e}")
    races = episode.get("races", "?")
    age = episode_age_seconds(episode, "race_since", now) if measurable else None

    if age is None:
        # FAIL LOUD, AND SAY WHICH FAILURE IT IS. "We cannot tell" is a result and belongs on the
        # surface. The alternative direction — treat an unmeasurable episode as a fresh one — is
        # the 2026-08-09 shape verbatim: a record that cannot be read reporting a fresh episode
        # inside an old one, and here it would be a standing race that never pages.
        notify(
            f"[ORIGIN FORK] the push was refused as a lost race ({r['detail']}) and this machine "
            f"CANNOT SAY how long that has been going on: the episode record at "
            f"{ORIGIN_RACE_EPISODE_FILE.name} is present and unreadable (preserved alongside). A "
            f"lost race is benign only while it is self-healing, and that is exactly what cannot "
            f"be shown here — so it is reported rather than assumed. Origin is {r['behind']} "
            f"commit(s) ahead.",
            kind="real_alarm", transition_key=_ORIGIN_FORK_KEY,
            # Keyed to the CONDITION and not to `behind`, which moves every cadence: a state that
            # moves every cycle is a transition check that cannot suppress anything.
            state="race:unmeasurable", re_escalate_after=RE_ESCALATE_SECONDS,
            topic_class=_digest_classes().BLOCKED_WORK,
        )
        return

    if age < RACE_PERSISTENCE_SECONDS:
        log(f"ORIGIN FORK race (BENIGN, self-healing): lost the push race, {races} in this episode, "
            f"{age / 60:.0f} min in. Nothing is owed — the next cadence re-merges on the new base. "
            f"Not paged below {RACE_PERSISTENCE_SECONDS / 60:.0f} min.")
        return

    notify(
        f"[ORIGIN FORK] the reconciler has lost the push race {races} time(s) over "
        f"{age / 3600:.1f}h and is NOT converging. Each cycle it fetches, merges, gates the merge "
        f"CLEAN — and then origin moves before the push lands, so the whole gate is spent and the "
        f"fork stays open. Origin is {r['behind']} commit(s) ahead. THERE IS NOTHING TO MERGE BY "
        f"HAND: the merge already works. Something is pushing to origin faster than a gate run "
        f"takes, and that is what needs looking at.",
        kind="real_alarm", transition_key=_ORIGIN_FORK_KEY,
        # KEYED TO THE EPISODE, not to today's count or today's `behind`. Both move every cadence,
        # and a state that changes every cycle sends every cycle — which is how this channel has
        # buried its own signal before. One episode is one condition; `re_escalate_after` is what
        # re-tells him while it stands, and a genuinely new episode changes the key.
        state="race:{}".format(int(float(episode.get("race_since") or 0))),
        re_escalate_after=RE_ESCALATE_SECONDS,
        # BLOCKED_WORK, and by this point it is TRUE: the fork has been open for as long as this
        # module's own definition of work sitting undelivered, and nothing is reaching origin.
        topic_class=_digest_classes().BLOCKED_WORK,
    )


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
        from background.tree_lock import RepoBareError, assert_repo_not_bare
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


def _flush_notification_digest() -> None:
    """Send the batched-notification digest when it is due (G-N4, director 2026-08-12).

    It RIDES this timer rather than owning a daemon: the digest is throttled, not scheduled,
    so a stopped deadman DELAYS a digest and can never lose one (the queue is append-only and
    the high-water mark only moves on a confirmed delivery). Swallows its own exceptions for
    the same reason every other check here does -- a digest must never take the deadman down,
    and an unflushed queue is self-healing on the next cycle.
    """
    try:
        from background import notification_digest
        result = notification_digest.maybe_flush()
        if result is not None:
            log(f"Notification digest flushed: {result}")
    except Exception as exc:                                   # pragma: no cover - defensive
        log(f"Notification digest flush failed (queue intact): {type(exc).__name__}: {exc}")


#: The transition key for the publishing-down page. One key, so a freeze pages once when it
#: starts and once when it clears, with an hourly re-escalate while it persists.
_PUBLISHING_KEY = "content_publishing_state"


def _digest_classes():
    """The G-N3 class vocabulary, imported lazily so a notification module problem can never stop
    this daemon from starting -- it is the watchdog, and it has to outlive what it watches."""
    from background import notification_digest
    return notification_digest


def _check_content_publishing() -> None:
    """Page the director when the FIGURES stop reaching origin (2026-08-13).

    THE CLASS THIS CLOSES, and it is not a missing threshold -- it is a missing SENDER.
    `notification_digest` defines four INSTANT classes, taken verbatim from the director's own
    message: action_needed, blocked_work, decision_waiting, publishing_down. A grep of the tree
    on 2026-08-13 found ZERO callers of any of them, and `publishing_down` in particular had
    never been emitted by anything. So the one event he named as "tell me immediately" was the
    one event nothing could tell him about, and he found eighteen hours of frozen content by
    looking at the site.

    WHY HERE. This daemon is deliberately outside the tmux/supervisor stack and already owns the
    periodic cycle the digest flush rides. It is also INDEPENDENT of the publisher in the way
    that matters: it reads the freshness clock off disk rather than asking the publish pipeline
    how the publish pipeline is doing. A publisher that pages about its own health is the
    tautology R15 names -- the wedged component reporting on itself was how the previous freeze
    stayed quiet too.

    NOT the same alarm as the commit clock below. That one fires on "no git commit at all", and
    it stayed SILENT through the whole freeze for a perfectly good reason: commits were landing
    the entire time -- worker commits, and a `chore(liveness)` heartbeat every thirty minutes.
    Liveness is exactly what made the content freeze invisible, so a liveness-shaped alarm could
    never have caught it. This one asks the different question: did the FIGURES move.
    """
    try:
        from background import notification_digest, publish_freshness
        snap = publish_freshness.snapshot()
    except Exception as exc:  # noqa: BLE001 -- a check that cannot run must not crash the cycle
        log(f"content-publishing check error: {type(exc).__name__}: {exc}")
        return

    state = snap.get("state")
    if state == "publishing":
        # Recovery pages ONCE, and only if we actually paged a fault -- `current_state` is asked
        # rather than assumed, because an unconditional send here announces a recovery from a
        # fault that never happened on the first cycle after every restart.
        if current_state(_PUBLISHING_KEY) in ("stale", "unpublished"):
            notify(f"[PUBLISHING] Recovered -- {publish_freshness.describe(snap)}.",
                   kind="real_alarm", transition_key=_PUBLISHING_KEY, state=state,
                   topic_class=notification_digest.PUBLISHING_DOWN)
        else:
            clear_transition(_PUBLISHING_KEY)
        return
    if state == "unknown":
        return  # no measurement is not evidence of a fault -- see is_publishing_down()

    hours = (snap.get("published_age_seconds") or 0) / 3600.0
    detail = (" Content IS still being committed -- so the figures may look like they move, but "
              "only when another writer happens to sweep the regenerated files along. The "
              "PUBLISH PATH itself is what stopped."
              if snap.get("committed_but_unpublished") else
              " The tick may look healthy and the heartbeat may still be landing on origin: "
              "those are the LIVENESS surface and they do not move with the figures.")
    msg = (
        f"[PUBLISHING DOWN] The published figures have not reached origin for {hours:.1f}h "
        f"(state={state}).{detail} Check sim-runner-log.md for the publish outcome -- a commit "
        f"killed by the pre-commit hook deadline is the 2026-08-13 shape."
        if state == "stale" else
        "[PUBLISHING DOWN] No verified content publish has EVER been recorded. Either this is a "
        "fresh install, or the publish clock's state file was lost -- until one publish is "
        "recorded, nothing here can tell a frozen site from a live one."
    )
    notify(msg, kind="real_alarm", transition_key=_PUBLISHING_KEY, state=state,
           re_escalate_after=RE_ESCALATE_SECONDS,
           topic_class=notification_digest.PUBLISHING_DOWN)
    log(f"content-publishing alarm checked (notify-gated) -- {publish_freshness.describe(snap)}")


def run_cycle() -> None:
    _reping_open_action_needed_items()
    _check_pull_loop_transport()
    _check_fork_lifecycle()
    _check_worktree_reconcile()
    _check_worktree_reap()
    _check_origin_fork()
    _check_status_honesty()
    _check_repo_not_bare()
    _check_operational_layer_signal()
    _check_content_publishing()
    _flush_notification_digest()

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
           re_escalate_after=RE_ESCALATE_SECONDS,
           topic_class=_digest_classes().BLOCKED_WORK)
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
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/deadmans_switch.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("deadmans_switch")
    main()
