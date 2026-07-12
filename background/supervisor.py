"""THE SUPERVISOR -- sole authority for turn-granting (2026-07-09, doorbell
failure #4, R3 architecture-level rebuild, director-direct).

A single dumb loop. Every POLL_INTERVAL_SECONDS: if the session is idle AND
real work exists on disk (an open agenda, unprocessed staging, an urgent
from_rich message, a usage-limit pause that just ended, OR -- 2026-07-10,
SELF_DIRECTION_AND_PARALLELISM.md Problem 1, REDESIGNED same-day per a
director audit + R3 -- a dial-weighted draw from docs/design/
maturity_map.yaml's real capability atoms with an open gap, falling back to
the original PRIORITIES.md "## Backlog" prose scan only if the YAML is
unavailable), grant exactly one turn via the locked relay, verify it was
consumed, and log the decision either way -- every cycle, not just the
interesting ones.

The self-refill check (`_actionable_backlog_item()`) is a cheap mechanical
heuristic, not comprehension -- it never treats a BLOCKED or REVIEW GATE
line as self-refillable, and it never says what to do beyond "something is
open," matching R7 exactly like every other reason string here. The
granted session decides what's actually worth doing by reading
PRIORITIES.md itself, same as always.

Why this exists (three independent things broke the same night, see
docs/retrospectives/2026-07-09-doorbell-failure-4-supervisor.md):

1. background/agenda.py's should_nudge() is nudge-ONCE-per-snapshot (R5's
   "never repeat an unchanged status" applied to turn-granting, not just
   alerting). One nudge fired, was logged delivered, and then never fired
   again for that snapshot -- even though the work behind it sat undone for
   5+ hours. Polling every cycle regardless of prior "success" kills this
   bug outright: `should_nudge` is never consulted at all any more.
2. staging_watcher.py -- a multi-responsibility daemon (git fetch, new-file
   notify, wake, agenda-nudge, monthly maintenance) -- went silently inert
   for 5+ hours while still alive (not hung: wchan=hrtimer_nanosleep, no
   blocking syscall observed), taking every one of those responsibilities
   down with it. A single-purpose daemon with no network calls and no other
   duties in its hot loop has a much smaller surface for this class of
   silent stall. THIS is why the supervisor never calls git, NTFY (except
   the rare stuck-escalation), or anything else that can block -- only
   local disk reads and the already-hardened tmux relay.
3. session_watchdog's autoloop DID keep polling every ~10 minutes and
   logged "delivered (confirmed)" 34 consecutive times over 5.5 hours --
   and produced no observable work. Verified pane-consumption is evidently
   not sufficient proof a turn actually executed (root cause not fully
   observable from outside the Claude Code CLI process -- see R9 note in
   the retrospective). Polling alone does not detect this; it just makes
   the same silent failure repeat faster. The supervisor additionally
   tracks a narrow key of real work-state (_stuck_key(), disk-persisted in
   STUCK_STATE_FILE) across cycles: if it keeps granting turns for the SAME
   unchanged key past STUCK_THRESHOLD_SECONDS of wall-clock time, that is
   no longer an ordinary retry -- it escalates with one NTFY (deduped per
   stuck key, R5-compliant) instead of retrying silently forever. This is
   the one piece beyond the director's literal spec, added because failure
   #4 specifically would NOT have been caught by polling cadence alone.
   REDESIGNED 2026-07-11 (R3, second failure of this exact mechanism,
   director-caught): the original in-memory grant-COUNT version's
   fingerprint included PRIORITIES.md's mtime and the raw unprocessed-
   staging list, so real work on OTHER items (editing PRIORITIES.md) and
   transient run_complete_*.md churn both reset the "unchanged" counter to
   1 every time, masking a full night where the actual blocker (two staged
   files) never moved. Replaced with a disk-persisted, wall-clock tracker
   keyed narrowly enough to exclude both noise sources -- see _stuck_key().

Every other turn-granting path (session_watchdog's autoloop nudge, its
REVIEW_GATE reply relay, staging_watcher's new-file wake and agenda-nudge,
dispatcher's URGENT promotion) still exists as an optional fast-path hint
-- when they work, the session responds sooner than the next supervisor
cycle. But none of them is load-bearing any more: if every one of them
silently fails simultaneously, exactly as happened tonight, the supervisor
still guarantees a turn within POLL_INTERVAL_SECONDS.

R7 applies to the granted-turn text itself: it carries ZERO content
authority, a doorbell only ("work exists, read it from disk yourself"),
never a directive -- same discipline as every other wake in this codebase.

4. WORK-GRANTING REDESIGN (2026-07-12, R3_WORK_GRANTING_REDESIGN.md, P0,
   9th idle variant, director-caught from the live console -- "the
   director is hand-typing 'self-refill next atom' -- he is manually
   performing the supervisor's core function"). Root cause named precisely
   in the redesign order: granting was TRIGGER-DRIVEN ("doorbell -> if
   nothing there -> idle") when it must be BACKLOG-DRIVEN ("doorbell (if
   any) -> handle it -> THEN draw the next atom from the map, always").
   The concrete bug: `find_work()`'s "unprocessed staging" check included
   `run_complete_*.md` -- the auto-process daemon's OWN routine
   coordination marker, landing every ~13min on sim_runner's own cadence,
   needing no granted turn at all to be handled -- in the SAME list used to
   decide "real work exists on the instruction channel." So as long as
   that marker sat in docs/staging/ (nearly always), `find_work()` returned
   "unprocessed staging -- run_complete_X.md" and NEVER reached the
   self-refill draw below it. The granted session then correctly concluded
   "that's the daemon's own work, nothing for me to do" -- individually
   correct, collectively wrong: ~35 open map atoms sat idle while this
   repeated every ~2 minutes. Fixed: (1) `_real_staged_instructions()`
   excludes daemon markers from the instruction-channel check entirely
   (`_is_daemon_marker()`); (2) the self-refill draw (`_self_refill_draw()`)
   is now UNCONDITIONAL -- it runs and gets appended to the reason even
   when a real agenda/urgent/staged item already fired, so a granted turn
   is never JUST daemon housekeeping with no real capability-building work
   attached; (3) `find_work()` now returns `(reason, map_exhausted)` --
   `map_exhausted` is True only when the self-refill draw itself found
   nothing (every atom blocked/complete, or the map unreadable), distinct
   from "didn't draw because something else took priority" (requirement 4:
   escalate on CANNOT-draw, never on didn't-draw); (4) an idle-turn counter
   (`_record_idle_turn()`/`IDLE_TURN_COUNTER_FILE`) instruments the
   "nothing to do" state directly rather than letting it pass silently
   (requirement 1: target is zero, and every occurrence is now visible in
   the log, not just inferred from its absence).
"""
from __future__ import annotations

import json
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background import agenda as agenda_module  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402
from background.ntfy_utils import send_ntfy, sign_wake_message  # noqa: E402
from background.tmux_relay import (  # noqa: E402
    ensure_live_tail, is_session_idle, pane_in_copy_mode, send_keys_when_idle,
)

SESSION_NAME = "claude"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "supervisor-log.md"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
USAGE_PAUSE_FILE = PROJECT_DIR / "docs" / "observability" / ".usage_pause.json"

POLL_INTERVAL_SECONDS = 120  # 2 minutes -- polling is explicitly permitted (director, 2026-07-09)

# If the same work-state fingerprint survives this many consecutive granted
# turns (~16 minutes at the default cadence), grants are no longer an
# ordinary retry -- something below the tmux layer is plausibly swallowing
# them. Escalate once per stuck fingerprint rather than retry silently
# forever.
STUCK_THRESHOLD_SECONDS = 3600  # 1 hour wall-clock (2026-07-11 redesign, R3 second
# failure of this mechanism -- director-caught: the old grant-COUNT threshold's
# fingerprint included PRIORITIES.md's mtime and the raw unprocessed-staging list,
# so a full night of zero progress on two genuinely stuck staged files (B2_OPEX_
# TAXONOMY_EXPANSION.md, HARNESS_BEST_PRACTICE_ADOPTION.md) never escalated --
# unrelated real work editing PRIORITIES.md (closing OTHER items) and transient
# run_complete_*.md markers coming and going both reset the "unchanged" counter
# to 1 every time, even though the actual director-relevant blocker never moved.
# Per R3 (two-strike redesign): eliminated the in-memory grant-count fingerprint
# entirely rather than patching it a third time. Replaced with a wall-clock,
# disk-persisted tracker (STUCK_STATE_FILE) keyed narrowly by _stuck_key() to
# exclude exactly those two noise sources, and durable across a daemon restart
# (the old in-memory globals reset silently on any supervisor.py restart, which
# was never itself flagged as a gap until now).
STUCK_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".supervisor_stuck_state.json"

# R3_WORK_GRANTING_REDESIGN.md requirement 1+4 (2026-07-12, P0, 9th idle
# variant): "nothing to do" must be an impossible terminal state while the
# map has open atoms -- instrument it, count it, alarm it, target zero.
# This tracks the ONE case find_work() can now return no reason at all:
# the self-refill draw itself found no candidate (every atom blocked/
# complete/unreadable), distinct from "didn't draw because something else
# took priority" (that always produces a real reason string). Escalates
# once per TRANSITION into this state (R5: never repeat an unchanged
# status), not on every cycle it persists.
MAP_EXHAUSTED_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".supervisor_map_exhausted_state.json"
IDLE_TURN_COUNTER_FILE = PROJECT_DIR / "docs" / "observability" / ".supervisor_idle_turn_count.json"

# Names that live directly in docs/staging/ but are not real work items.
_IGNORED_STAGING_NAMES = {".gitkeep"}


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def ntfy(msg: str) -> None:
    send_ntfy(msg)


def _unprocessed_staging_files() -> list[str]:
    """Top-level files directly in docs/staging/ -- excludes done/, fyi/,
    responses/, drafts/ and any other subdirectory automatically (iterdir +
    is_file), and .gitkeep. Covers both staged instruction docs and
    from_rich_*.md files left in place by dispatcher.py (URGENT/NORMAL)."""
    if not STAGING_DIR.is_dir():
        return []
    return sorted(
        p.name for p in STAGING_DIR.iterdir()
        if p.is_file() and p.name not in _IGNORED_STAGING_NAMES
    )


def _is_daemon_marker(name: str) -> bool:
    """True for a routine internal pipeline marker (sim_runner.py/
    process_run_complete.py's own coordination file), never a real
    director/advisor instruction. These self-process on the daemon's own
    cadence with no granted turn required at all -- confirmed directly,
    2026-07-12: dozens of these were picked up and fully processed by
    process_run_complete.py across this entire session with zero agent
    action needed."""
    return (
        (name.startswith("run_complete_") and name.endswith(".md"))
        or (name.startswith("run_pending_") and name.endswith(".md"))
    )


def _real_staged_instructions() -> list[str]:
    """R3_WORK_GRANTING_REDESIGN.md (P0, 9th idle variant, director-caught
    2026-07-12): daemon markers off the instruction channel. The prior
    `_unprocessed_staging_files()` included run_complete_*.md in the SAME
    list `find_work()` used to decide "real work exists on the instruction
    channel" -- so as long as the auto-process daemon's own routine marker
    sat in docs/staging/ (which it does almost continuously, landing every
    ~13min), find_work() returned early with "unprocessed staging --
    run_complete_X.md" and NEVER reached the maturity-map self-refill draw
    below it. The granted session then correctly concluded "that's the
    daemon's own work, nothing for me to do" and ended the turn -- which
    was individually correct (it WASN'T a real instruction) but collectively
    wrong, because "not a real instruction" should have fallen through to
    "so draw the next atom from the map instead," never to "so end the
    turn." This is the root cause named in the redesign order, not a
    coincidence: ~35 open map atoms sat idle while this repeated every
    ~2 minutes, because the doorbell-inspection step never got past a
    marker that was never supposed to gate it in the first place."""
    return [name for name in _unprocessed_staging_files() if not _is_daemon_marker(name)]


def _urgent_from_rich_pending(staged: list[str]) -> str | None:
    """Name of the first unprocessed from_rich_*.md file dispatcher.py has
    classified URGENT (its <!-- Dispatcher: URGENT --> header, prepended in
    place -- dispatcher.py never moves urgent/normal files out of
    docs/staging/, only fyi goes to staging/fyi/), or None."""
    for name in staged:
        if not (name.startswith("from_rich_") and name.endswith(".md")):
            continue
        try:
            content = (STAGING_DIR / name).read_text(encoding="utf-8")
        except OSError:
            continue
        if "Dispatcher: URGENT" in content:
            return name
    return None


def _pause_active_readonly() -> bool:
    """Same check as session_watchdog.usage_pause_active(), but read-only
    -- never deletes the file. session_watchdog remains the sole owner of
    writing/clearing .usage_pause.json and of the enter/exit NTFY
    transitions (background/session_watchdog.py); the supervisor only ever
    reads it, so the two processes can't race on mutating the same file."""
    if not USAGE_PAUSE_FILE.is_file():
        return False
    try:
        data = json.loads(USAGE_PAUSE_FILE.read_text(encoding="utf-8"))
        resume_at = datetime.fromisoformat(data["resume_at"])
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        return False
    if resume_at.tzinfo is None:
        resume_at = resume_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) < resume_at


PRIORITIES_PATH = PROJECT_DIR / "PRIORITIES.md"
MATURITY_MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"


def _actionable_backlog_item() -> str | None:
    """FALLBACK ONLY as of 2026-07-10 -- see `_maturity_map_draw()`, now the
    primary self-refill source. Kept only for the case maturity_map.yaml is
    ever missing/unreadable (graceful degradation, same style as the rest of
    this module), so self-refill never regresses to nothing.

    R3 note (2026-07-10, director audit -- "was that gap a session pause, an
    empty-agenda idle, or grants that produced nothing? ... if genuine idle,
    R3 applies to the refill logic"): this heuristic was found to be the
    root cause of a genuine 2h40m idle hole (11:00-14:40) -- it only scanned
    text AFTER the literal "## Backlog" heading for the exact substring "NOT
    YET STARTED", and by that date NONE of the real backlog bullets used
    that exact phrase (they said "NOT STARTED"/"BLOCKED"/"PARTIALLY CLOSED"
    etc.), while every item registered elsewhere in the file (the "# ==="
    sections above the Backlog heading) was structurally invisible to it
    regardless of wording. Same failure class as an earlier incident where a
    phrase accidentally DID match and caused repeated false grants -- two
    strikes on the same fragile prose-substring mechanism. Per R3 (redesign,
    not patch again), the primary mechanism is now the dial-weighted
    maturity-map draw below, which reads structured YAML fields
    (level_current/level_target) instead of matching free-form English
    prose that changes every time someone edits PRIORITIES.md."""
    try:
        text = PRIORITIES_PATH.read_text(encoding="utf-8")
    except OSError:
        return None
    # 2026-07-10, third instance of the same self-referential false-positive
    # class found in one self-audit (nineteenth dial-weighted draw): a raw
    # `text.find("## Backlog")` matches the FIRST occurrence of that
    # substring anywhere in the file -- including inside this very
    # docstring's own prose describing the mechanism, or inside a past
    # commit's write-up quoting the heading name in the file itself (both
    # observed live). A real markdown heading is always anchored at the
    # start of a line; a heading name merely mentioned mid-sentence is not.
    # `re.search(..., re.MULTILINE)` with `^` fixes this at the root rather
    # than continuing to reword prose to dodge the same substring forever.
    match = re.search(r"^## Backlog", text, re.MULTILINE)
    if match is None:
        return None
    idx = match.start()
    for line in text[idx:].split("\n"):
        if "NOT YET STARTED" in line and "BLOCKED" not in line and "REVIEW GATE" not in line:
            # Return a short, stable identifier (first ~80 chars) -- enough
            # for the log/fingerprint to distinguish backlog items from each
            # other without embedding the full line (R7: doorbell, not a
            # directive -- the granted session re-reads PRIORITIES.md itself).
            return line.strip().lstrip("#- ").strip()[:80]
    return None


def _maturity_map_draw(rng: Any = None) -> str | None:
    """Primary self-refill source (2026-07-10, MATURITY_MAP.md Section 6/8:
    "Supervisor self-refill draws work from lanes proportional to dials").
    Reads docs/design/maturity_map.yaml, keeps atoms with a real gap
    (level_current is not None and level_current < level_target -- an
    atom with level_current: null is an honestly-unassessed atom, never
    self-refillable), and makes ONE weighted-random draw where each atom's
    weight is its own `dial_inherited` (the director-ratified per-lane dial
    from MATURITY_MAP.md Section 8) -- lanes with a higher dial are more
    likely to be drawn, matching the equaliser's intent, without the
    supervisor needing to understand what "DISCOVER" vs "BUILD" means (R7:
    the granted session reads the atom's own loop_stage/evidence itself and
    decides what kind of turn that implies).

    Still a cheap, blocking-call-free, no-comprehension read (module
    docstring's own constraint) -- one file read + one weighted choice, no
    network, no git. Returns None (graceful degradation) if the YAML is
    missing, unreadable, malformed, or has no atom with a real gap."""
    try:
        import yaml
    except ImportError:
        return None
    try:
        atoms = yaml.safe_load(MATURITY_MAP_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(atoms, list):
        return None
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and "id" in a}

    def _dependencies_met(atom: dict) -> bool:
        """2026-07-10, real observed gap (first draw of W1_2_generate_futures
        surfaced its own unmet dependency W1_reveal_over_time, level 0/3) --
        a `depends_on` entry that isn't itself at/above its target level means
        the atom's own foundation doesn't exist yet, so drawing it produces
        real but premature/unbuildable "work". A dependency id not present in
        the map at all is treated as unmet (fail closed, not silently
        ignored) rather than assumed satisfied."""
        for dep_id in atom.get("depends_on") or []:
            dep = by_id.get(dep_id)
            if dep is None:
                return False
            dep_level = dep.get("level_current")
            dep_target = dep.get("level_target")
            if dep_level is None or dep_target is None or dep_level < dep_target:
                return False
        return True

    def _is_valid_candidate(a: dict) -> bool:
        """2026-07-10, HARDEN-stage adversarial review of this exact function
        (H1_supervisor_turn_granting's own Expert Hour): a single malformed
        atom (wrong type -- e.g. a quoted "2" instead of 2 -- or an explicit
        `dial_inherited: null`) would previously raise TypeError from the
        `<` comparison or `max()` below, uncaught until main()'s outer
        try/except, which logs and moves on -- but does NOT fall through to
        the backlog-prose fallback, because the exception aborts
        find_work()'s whole function body before it reaches that later
        line. Since this only matters when agenda+staging are BOTH empty
        (exactly self-refill's own use case), an unhandled malformed atom
        would silently reintroduce the identical idle-hole class of bug
        this entire mechanism was built to eliminate. Isolating validation
        per-atom means one bad edit degrades to "skip this one atom", not
        "the whole draw silently stops working every cycle forever until a
        human notices and fixes the YAML"."""
        if not isinstance(a, dict):
            return False
        level_current, level_target = a.get("level_current"), a.get("level_target")
        if level_current is None or level_target is None:
            return False
        dial = a.get("dial_inherited", 1)
        try:
            has_gap = level_current < level_target
            _ = max(1, dial)
        except TypeError:
            return False
        if not has_gap:
            return False
        if a.get("loop_stage") == "idle":
            # 2026-07-10, real observed gap: the third live draw surfaced
            # W3_1_price_cap_binding (loop_stage=idle) -- per MATURITY_MAP.md
            # Section 6's own schema, "idle" specifically means NOT currently
            # in the Hardening Loop (parked -- e.g. explicitly sequenced
            # after other steps in its own programme doc). Drawing it as if
            # it were live discover/build work wastes a turn on something
            # the map's own data already says isn't due yet.
            return False
        return _dependencies_met(a)

    candidates = [a for a in atoms if _is_valid_candidate(a)]
    if not candidates:
        return None
    weights = [max(1, a.get("dial_inherited", 1)) for a in candidates]
    picker = rng or random
    chosen = picker.choices(candidates, weights=weights, k=1)[0]
    return (
        f"{chosen['id']} -- {chosen.get('name', '?')} "
        f"(lane={chosen.get('lane', '?')}, dial={chosen.get('dial_inherited', '?')}, "
        f"level {chosen['level_current']}->{chosen['level_target']}, "
        f"loop_stage={chosen.get('loop_stage', '?')})"
    )


def _self_refill_draw() -> str | None:
    """The backlog-driven draw itself (maturity map, falling back to
    PRIORITIES.md prose only if the YAML is unavailable) -- factored out so
    find_work() can call it UNCONDITIONALLY (R3_WORK_GRANTING_REDESIGN.md
    requirement 2: "every granted turn ends with real work drawn... THEN
    draw the next atom from the map, always"), not merely as a fallback
    reached only when nothing else fired."""
    map_draw = _maturity_map_draw()
    if map_draw:
        return f"self-refill from maturity map (dial-weighted): {map_draw}"
    backlog_item = _actionable_backlog_item()
    if backlog_item:
        return f"self-refill from PRIORITIES.md backlog (fallback, maturity map unavailable): {backlog_item}"
    return None


def find_work(resumed_from_pause: bool) -> tuple[str | None, bool]:
    """Return (reason, map_exhausted). `reason` is a human-readable string
    if any real work exists (an instruction-channel doorbell, and/or a
    self-refill draw), else None. `map_exhausted` is True only when the
    self-refill draw itself found no candidate at all (every atom
    blocked/complete/unreadable) -- distinct from "didn't draw because an
    agenda/urgent item took priority" (requirement 4: escalate on
    CANNOT-draw, never on didn't-draw). Checked fresh every cycle -- no
    "already nudged" memory, by design (that memory is exactly what caused
    failure #4's silent gap).

    R3_WORK_GRANTING_REDESIGN.md (P0, 9th idle variant, 2026-07-12,
    director-caught): work-granting was TRIGGER-DRIVEN ("doorbell -> if
    nothing there -> idle") when it must be BACKLOG-DRIVEN ("doorbell (if
    any) -> handle it -> THEN draw the next atom from the map, always").
    Two changes from the pre-redesign version: (1) the "unprocessed
    staging" check now uses `_real_staged_instructions()`, which excludes
    routine daemon markers (run_complete_*.md) -- these used to look like
    "real work exists on the instruction channel" and short-circuit this
    function before it ever reached the self-refill draw, even though the
    daemon marker needed no granted turn to be handled at all. (2) the
    self-refill draw is now UNCONDITIONAL: it runs and gets appended to the
    reason even when a real agenda/urgent/staged item already fired, so a
    granted turn is never JUST "here's today's daemon housekeeping" with no
    real capability-building work attached."""
    if resumed_from_pause:
        return "usage-limit pause just ended -- resume work", False

    primary: str | None = None

    agenda = agenda_module.load_agenda()
    if agenda:
        primary = f"agenda open -- phase '{agenda.get('phase', '?')}', step '{agenda.get('step', '?')}'"
    else:
        staged = _real_staged_instructions()
        urgent = _urgent_from_rich_pending(staged)
        if urgent:
            primary = f"urgent from_rich queued -- {urgent}"
        elif staged:
            primary = f"unprocessed staging -- {', '.join(staged)}"

    refill = _self_refill_draw()

    if primary and refill:
        return f"{primary}; ALSO -- {refill}", False
    if primary:
        return primary, False
    if refill:
        return f"agenda+staging empty -- {refill}", False

    # Nothing anywhere -- requirement 1: this must be an impossible
    # terminal state while the map has open atoms, so reaching here means
    # the map itself is genuinely exhausted (every atom blocked/complete)
    # or unreadable, which is itself a finding worth surfacing once
    # (see _check_map_exhausted_escalation), not a silent "idle, no work".
    return None, True


def _stuck_key(reason: str) -> str:
    """The narrow, comparable state used to detect 'no real progress' --
    deliberately NOT the full find_work() reason string or a broad snapshot
    of everything on disk (2026-07-11 redesign; see STUCK_THRESHOLD_SECONDS
    for why the prior broad fingerprint silently masked a full night of a
    genuinely stuck 'unprocessed staging' case).

    Two specific exclusions, both confirmed root causes:
    - run_complete_*.md markers are excluded from the staging list used
      here. They self-process on sim_runner's/background_worker's own
      pipeline cadence; their transient appearance/disappearance is routine
      housekeeping, not evidence a DIFFERENT stuck staged file has moved.
    - PRIORITIES.md's mtime is folded in ONLY for the self-refill-from-
      backlog path, where an edited file genuinely is the progress signal
      (a self-refill turn closing item X changes the file even though the
      next self-refill draw's reason text might otherwise look the same).
      For the unprocessed-staging/urgent/agenda paths it is irrelevant noise
      -- real work closing some OTHER, unrelated item was resetting the
      stuck-clock for these two untouched files every time overnight."""
    agenda = agenda_module.load_agenda()
    if agenda:
        return json.dumps({"kind": "agenda", "updated_at": agenda.get("updated_at")}, sort_keys=True)
    if "self-refill from PRIORITIES.md backlog" in reason:
        try:
            priorities_mtime = PRIORITIES_PATH.stat().st_mtime
        except OSError:
            priorities_mtime = None
        return json.dumps({"kind": "backlog", "priorities_mtime": priorities_mtime}, sort_keys=True)
    # Reuse the single source of truth for "what's a routine daemon marker"
    # (_is_daemon_marker) rather than a second, independently-drifting copy
    # of the same exclusion list.
    non_transient_staged = _real_staged_instructions()
    return json.dumps({"kind": "staging", "reason": reason, "staged": non_transient_staged}, sort_keys=True)


def _load_stuck_state() -> dict:
    if not STUCK_STATE_FILE.exists():
        return {}
    try:
        return json.loads(STUCK_STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_stuck_state(state: dict) -> None:
    STUCK_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STUCK_STATE_FILE.write_text(json.dumps(state, sort_keys=True))


def _check_stuck_escalation(reason: str) -> None:
    """Wall-clock, disk-persisted escalation (2026-07-11 redesign) -- see
    STUCK_THRESHOLD_SECONDS and _stuck_key(). Persisting to disk (rather
    than an in-memory counter) means a supervisor.py restart mid-stuck-
    period does not silently reset the clock either -- another latent gap
    the prior in-memory-only design had."""
    key = _stuck_key(reason)
    state = _load_stuck_state()
    now = time.time()
    if state.get("key") != key:
        _save_stuck_state({"key": key, "first_seen_at": now, "escalated": False})
        return
    first_seen_at = state.get("first_seen_at", now)
    elapsed = now - first_seen_at
    if elapsed >= STUCK_THRESHOLD_SECONDS and not state.get("escalated"):
        minutes = int(elapsed // 60)
        ntfy(
            f"Supervisor: granting turns for ~{minutes}min for the same work "
            f"({reason}) with no state change -- something below the tmux "
            "layer may be swallowing turns (see doorbell failure #4), or "
            "this is genuinely blocked and needs your input."
        )
        log(f"STUCK escalation sent -- ~{minutes}min unchanged -- {reason}")
        state["escalated"] = True
        _save_stuck_state(state)


def _load_idle_turn_count() -> int:
    if not IDLE_TURN_COUNTER_FILE.exists():
        return 0
    try:
        return json.loads(IDLE_TURN_COUNTER_FILE.read_text()).get("count", 0)
    except (json.JSONDecodeError, OSError):
        return 0


def _record_idle_turn() -> int:
    """R3_WORK_GRANTING_REDESIGN.md requirement 1: instrument the impossible
    state, don't just prevent it silently. Returns the new total (all-time,
    persisted) count of cycles where find_work() found genuinely nothing --
    target is zero; every increment is itself visible in the log, not just
    inferred from its absence."""
    count = _load_idle_turn_count() + 1
    IDLE_TURN_COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    IDLE_TURN_COUNTER_FILE.write_text(json.dumps({"count": count}, sort_keys=True))
    return count


def _load_map_exhausted_state() -> dict:
    if not MAP_EXHAUSTED_STATE_FILE.exists():
        return {}
    try:
        return json.loads(MAP_EXHAUSTED_STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_map_exhausted_state(state: dict) -> None:
    MAP_EXHAUSTED_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    MAP_EXHAUSTED_STATE_FILE.write_text(json.dumps(state, sort_keys=True))


def check_map_exhausted_escalation(map_exhausted: bool) -> None:
    """R3_WORK_GRANTING_REDESIGN.md requirement 4: escalate on CANNOT-draw,
    never on didn't-draw. `map_exhausted` is True only when find_work()'s
    self-refill draw genuinely found no candidate at all -- every atom
    blocked/complete, or the map is unreadable. That is itself a real
    finding (either the whole map is done, which would be remarkable, or
    something is wrong with the map/its dependency graph) -- fire ONE NTFY
    on the TRANSITION into this state (R5: never repeat an unchanged
    status), not every cycle it persists, and clear cleanly the moment real
    work resumes so a later genuine recurrence escalates again."""
    state = _load_map_exhausted_state()
    was_exhausted = state.get("exhausted", False)
    if map_exhausted and not was_exhausted:
        ntfy(
            "Supervisor: the maturity-map self-refill draw found NO candidate "
            "atom at all (every atom blocked/complete, or the map is "
            "unreadable) with no agenda/urgent/staged instruction either -- "
            "this is a genuine CANNOT-draw, not a routine idle tick. Check "
            "docs/design/maturity_map.yaml directly."
        )
        log("MAP-EXHAUSTED escalation sent -- self-refill found no candidate at all")
        _save_map_exhausted_state({"exhausted": True})
    elif not map_exhausted and was_exhausted:
        log("Map-exhausted state cleared -- real work available again")
        _save_map_exhausted_state({"exhausted": False})


# Auto-clear (ADVISOR_STEER_OVERNIGHT.md item 2, 2026-07-11 -- authorized
# in-console 2026-07-11 morning via mid-turn window message, genuineness
# confirmed by Rich over NTFY the same day: "CONFIRMED: all recent mid-turn
# window messages were genuinely me -- the sequencing/auto-clear one...
# Act on all of them." docs/staging/done/from_rich_20260711_105502.md).
# The feature was authorized but never built -- a real session sat at 649k
# [tokens] begging for a manual /clear the same night this was staged.
#
# Approximation, stated plainly rather than hidden: there is no token-count
# API available to an external daemon, so this uses the current session's
# own transcript FILE SIZE (bytes) as a proxy, calibrated empirically
# against this actual project's transcripts (JSONL structural overhead --
# tool_use/tool_result blocks, timestamps, escaping -- inflates bytes/token
# well above plain text's ~4:1 ratio; this session's own transcript ran
# ~25 bytes/token at a self-reported ~649k-token mark). Recalibrate this
# constant if it drifts badly from reality; it is a proxy, not a promise.
AUTO_CLEAR_BYTES_THRESHOLD = 10_000_000  # ~400k tokens at the ~25 bytes/token calibration above
CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects" / "-home-rich-synthetic-enterprise"
AUTO_CLEAR_LOG_FILE = PROJECT_DIR / "docs" / "observability" / "supervisor-auto-clear-log.md"


def _latest_transcript_size_bytes() -> int | None:
    """Size in bytes of the most-recently-modified session transcript in
    this project's Claude Code projects directory -- a proxy for "the
    currently active session's context size" (there is no direct API to ask
    an external daemon process for another process's live token count).
    Returns None if the directory or any transcript is missing (fails
    closed -- no transcript found means no auto-clear decision can be made,
    not "assume huge and clear")."""
    if not CLAUDE_PROJECTS_DIR.is_dir():
        return None
    transcripts = list(CLAUDE_PROJECTS_DIR.glob("*.jsonl"))
    if not transcripts:
        return None
    latest = max(transcripts, key=lambda p: p.stat().st_mtime)
    try:
        return latest.stat().st_size
    except OSError:
        return None


def _git_tree_clean() -> bool:
    """True if the working tree has no uncommitted changes -- part of the
    "clean boundary" test (work pushed, nothing in flight). Fails closed
    (False, i.e. NOT clean / do not clear) on any error, since a spurious
    clear mid-uncommitted-work is the harmful failure mode, not a missed
    clear opportunity."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_DIR, capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return False
        return result.stdout.strip() == ""
    except Exception:
        return False


def should_auto_clear() -> bool:
    """Both halves of the authorized condition: context > ~400k (transcript-
    size proxy) AND a clean boundary (session idle -- reusing the exact same
    is_session_idle() gate turn-granting itself trusts -- and the working
    tree has no uncommitted changes, i.e. nothing in flight). Fails closed
    (False) if the transcript size can't be determined at all, rather than
    guessing."""
    size = _latest_transcript_size_bytes()
    if size is None or size < AUTO_CLEAR_BYTES_THRESHOLD:
        return False
    if not is_session_idle(SESSION_NAME):
        return False
    return _git_tree_clean()


def maybe_auto_clear() -> bool:
    """If should_auto_clear(), inject /clear via the same locked, idle-
    gated, verified relay every other daemon uses, log the event, and
    return True (caller should skip this cycle's normal turn-grant --
    the NEXT cycle's ordinary idle-check + find_work()/grant_turn() flow
    naturally serves as "re-grants with the standard boot" once the pane
    goes idle again post-clear, so no separate boot injection is needed
    here). Returns False (no-op) if the condition isn't met."""
    if not should_auto_clear():
        return False
    size = _latest_transcript_size_bytes()
    ok = send_keys_when_idle(SESSION_NAME, "/clear", "/clear")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    AUTO_CLEAR_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUTO_CLEAR_LOG_FILE, "a") as f:
        f.write(
            f"\n- [{ts}] Auto-clear {'sent' if ok else 'FAILED to send'} "
            f"-- transcript size {size} bytes (threshold {AUTO_CLEAR_BYTES_THRESHOLD})"
        )
    log(f"Auto-clear {'sent' if ok else 'FAILED to send'} -- transcript size {size} bytes")
    return ok


def grant_turn(reason: str) -> bool:
    """Attempt exactly one turn-grant via the locked, idle-gated, verified
    relay (background.tmux_relay.send_keys_when_idle) -- the same primitive
    every other daemon uses, so this can never race a fast-path hint firing
    at the same moment (relay_lock makes the two mutually exclusive)."""
    message = (
        f"[SUPERVISOR: turn granted -- {reason}. Read the relevant state "
        "from disk yourself (R7: this is a doorbell, not an instruction) "
        "and proceed per CLAUDE.md's tiered model.]"
    )
    signed = sign_wake_message(message)
    marker = signed.rsplit("|", 1)[-1]
    return send_keys_when_idle(SESSION_NAME, signed, marker)


# Mutable across main() loop iterations.
_was_paused = False


def run_cycle() -> None:
    global _was_paused

    paused_now = _pause_active_readonly()
    if paused_now:
        log("Usage pause active -- skipping (no grant)")
        _was_paused = True
        return
    resumed_from_pause = _was_paused
    _was_paused = False

    # R4 (2026-07-09): a pane frozen in tmux copy-mode/scrollback ("Jump to
    # bottom") reads as stale content to is_session_idle() below and
    # swallows any later send as copy-mode navigation -- clear it before
    # trusting the idle check at all. send_keys_when_idle() does this too
    # (defence in depth), but doing it here as well means this cycle's own
    # busy/idle log line reflects the real live pane, not frozen scrollback.
    if pane_in_copy_mode(SESSION_NAME):
        ensure_live_tail(SESSION_NAME)
        log("Pane was in scroll/copy-mode -- cleared before idle check")

    if not is_session_idle(SESSION_NAME):
        log("Session busy -- skipping this cycle")
        return

    if maybe_auto_clear():
        # Skip this cycle's normal turn-grant -- the pane just received
        # /clear and needs to settle; the NEXT cycle's ordinary idle-check +
        # find_work()/grant_turn() flow naturally re-grants with the
        # standard boot once the pane goes idle again post-clear.
        return

    reason, map_exhausted = find_work(resumed_from_pause)
    check_map_exhausted_escalation(map_exhausted)
    if reason is None:
        total = _record_idle_turn()
        log(f"Idle, no work -- map genuinely exhausted (all-time idle-turn count: {total})")
        return

    _check_stuck_escalation(reason)

    if grant_turn(reason):
        log(f"Turn granted (confirmed) -- {reason}")
    else:
        log(f"Turn grant not delivered (busy/unconfirmed) -- retrying next cycle -- {reason}")


def main() -> None:
    log("Supervisor started -- sole authority for turn-granting")
    update_agent_status(
        "supervisor", status="idle",
        last_action="Supervisor started",
        role="Sole authority for turn-granting: polls every 2min, grants one turn via the locked relay when idle+work exists, escalates if grants stop producing progress",
        produces="tmux turn-grants + stuck-state NTFY escalation",
    )
    while True:
        try:
            run_cycle()
        except Exception as e:
            log(f"Supervisor cycle error: {e}")
        try:
            stuck_state = _load_stuck_state()
            elapsed_min = int((time.time() - stuck_state.get("first_seen_at", time.time())) // 60)
            update_agent_status(
                "supervisor", status="idle",
                last_action=f"Cycle complete -- current stuck-key unchanged for ~{elapsed_min}min",
            )
        except Exception:
            pass
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
