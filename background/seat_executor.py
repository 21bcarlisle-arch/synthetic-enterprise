"""The seat's work, continued without the director — in its own worktree, one bounded piece.

Director, 2026-08-31: *"the contradiction resolves onto me pressing enter. That has been the
biggest single drag on this project for a fortnight."* This is the piece that removes it.

WHAT IT IS, IN ONE LINE: a bounded `claude -p` session in an ISOLATED worktree that takes the next
claimed piece of seat work, lands it through `surgical_land`, promotes it through
`promote_worktree_landing`, and exits.

WHY THIS CAN EXIST NOW AND COULD NOT THIS MORNING
--------------------------------------------------
`background/delivery_seat.py` may not write code, and its own docstring gives the reason:
*"reverting would make this the second writer it exists not to be."* That reason was sound and is
now obsolete — not by argument, by two landings:

  * `178bf5a56` — `surgical_land` works from a `git worktree`. The probe also showed that a
    worktree land commits to the worktree's own DETACHED HEAD and leaves `main` untouched, so an
    isolated writer cannot move the shared branch by committing.
  * `tools/promote_worktree_landing` — integration is now a route with four refusals rather than a
    remembered sequence of git commands.

So this is not a second writer on the shared tree. **It writes no CODE there at all** — every edit
it makes is in the worktree, and the only shared-tree files it touches are the observability
ledgers in `SHARED_TREE_WRITES` below.

That distinction is stated precisely because the first draft of this docstring claimed it never
wrote to the shared tree *at all*, which was false the moment it logged anything. A log and a pid
file cannot live in the worktree: `ensure_worktree` resets that tree at the start of every turn, so
a pid written there would vanish before the liveness check that needs it, and the log would lose
every turn's record. They live in `docs/observability/`, the directory every daemon in this project
appends to by design, alongside the handoff store the promotion below writes, and
`test_the_executor_writes_no_code_to_the_shared_tree` holds the list to exactly those.

THE FOUR REFUSALS BEFORE IT RUNS, and each is a way an unattended writer goes wrong
-----------------------------------------------------------------------------------
  * **another executor is running.** A pid file with a liveness check, not a bare lock — a lock
    left by a killed process is a machine that never runs again.
  * **an interactive seat is live AND the item was not handed over.** The heartbeat
    `.claude/hooks/stamp_seat_heartbeat.py` stamps on every tool call a session makes; if it is
    warm, a human is holding this seat. What that protects against is TWO WRITERS CHOOSING FROM
    THE SAME QUEUE, so the refusal asks about contention rather than presence. **A continuation
    runs.** It is the seat writing down, deliberately and in full context, *"this piece is for
    whoever runs next"* — and the seat that wrote it is nearly always still alive, because it
    writes the handoff and then keeps working. Refusing on presence refuses every handoff there
    will ever be, which is what the first version of this module did.

    **A re-derived `direction.unreachable_focus` item still stands down THIS tick — and is now
    PROMOTED into the handoff store on the way out, so a later tick takes it (2026-09-01).** The
    refusal as written on 2026-08-31 declined it and stopped there, which read as caution and
    measured as severance: `_interactive_seat_is_live` is true whenever any session is running and
    one always is, so the item was not sometimes declined, it was never reachable by any tick.
    Thirty-two consecutive stand-downs across five work ids are in the log. Deferring by one tick
    keeps everything the refusal was actually protecting — a live seat part-way through the item
    with nothing claimed gets the rest of the cycle to land something the path guard can then see —
    while `_promote_to_handoff` makes the route terminate.
  * **there is nothing to do.** No continuation and no unclaimed focus item is a legitimate
    resting state, recorded with its reason. `delivery_seat`'s skip rule already says why: running
    anyway produces a confident restatement, which reads downstream exactly like a decision.
  * **the work duplicates a live claim.** `seat_work_in_hand.refuse_if_duplicated`, keyed on
    PATHS rather than names, because the duplication that actually happened was two writers
    choosing the same work under two different labels.

WHAT IT STILL CANNOT DO, AND THESE ARE NOT HYPOTHETICAL
--------------------------------------------------------
It cannot tell whether its own work was any good. Every landing is gated and every finding filed,
and the director reviews retrospectively — that is a mitigation, not a proof, and an unattended
writer can be confidently wrong for hours. It also cannot see work another writer has decided on
but not yet claimed; the path guard closes the claimed case only.

**It is OFF by default.** `--once` runs a single bounded turn; nothing schedules it. Arming it is a
separate act, deliberately, so that the first unattended writer in this project's history is
started by someone rather than by a landing.
"""
from __future__ import annotations

import argparse
import calendar
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background import delivery_lane, seat_work_in_hand  # noqa: E402
from background.fork_salvage import salvage_worktree  # noqa: E402
from background.live_ledger_guard import guard_live_ledger_write  # noqa: E402
from background.seat_work_in_hand import DuplicateWork  # noqa: E402
from tools.wait_for import pid_is_alive  # noqa: E402

LOG_FILE = PROJECT_DIR / "docs" / "observability" / "seat-executor-log.md"
PID_FILE = PROJECT_DIR / "docs" / "observability" / ".seat_executor.pid"

#: EVERY path in the shared tree this module may write. The claim "it is not a second writer" rests
#: on this list being exhaustive and on every entry being observability rather than code, so the
#: list is the control's subject rather than a comment.
#:
#: THE THIRD ENTRY ARRIVED WITH THE PROMOTION (2026-09-01). `_promote_to_handoff` writes the
#: handoff store, which is a shared-tree write and has to be declared as one. It is still not code:
#: it is the same `docs/observability/` ledger the interactive seat writes with
#: `seat_continuation --hand-off`, behind the same `live_ledger_guard`, and this module now writes
#: it for the same reason the seat does.
SHARED_TREE_WRITES = (LOG_FILE, PID_FILE, delivery_lane.seat_continuation.STORE)
WORKTREE = Path(os.environ.get("SE_EXECUTOR_WORKTREE", "/var/tmp/se-seat-executor"))

#: A bounded turn. Long enough for a real piece of work including a capture; short enough that a
#: wedged session frees the lane the same hour.
SESSION_TIMEOUT_SECONDS = 90 * 60

MODEL = os.environ.get("SE_EXECUTOR_MODEL", "claude-opus-5")


class StoodDown(Exception):
    """A named reason this tick is not running. Never an error — a recorded decision."""


def log(message: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    with LOG_FILE.open("a") as fh:
        fh.write(f"- [{stamp}] {message}\n")


#: The log lines that name a work id this executor actually SPAWNED A TURN FOR.
#:
#: STAND-DOWNS ARE NOT IN IT, deliberately. A stand-down names the item it declined, and counting
#: it as drawn would make the drawn channel report a steer as biting on the exact turns where it
#: was refused. So this under-reports rather than over-reports, which is the safe direction for a
#: channel whose job is to notice a steer that is NOT biting (`atoms_drawn_since` names the same
#: limit for the same reason).
#:
#: THE EXCLUSION LIVES IN TWO PLACES -- this pattern and the extraction in `ids_run_since` -- and
#: mutating either ALONE survives, because each makes the other unreachable. That is recorded here
#: rather than left for the next person to read as coverage: the control that proves stand-downs
#: are excluded has to move both sites at once, and `test_the_drawn_channel_reads_the_executors_
#: OWN_LOG` was mutation-proven that way.
_TURN_LINE = re.compile(
    r"^- \[(?P<stamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC\] "
    r"(?:RUNNING (?P<running>\S+) in "
    r"|FINISHED (?P<finished>[^:\s]+): "
    r"|LANDED NOTHING: (?P<nothing>[^,\s]+), )"
)


def _shared_tree_log() -> Path:
    """The executor log on the SHARED tree, whichever tree this module was imported from.

    THERE IS ONLY ONE SEAT EXECUTOR AND ONE LOG, and it lives on the shared tree. `LOG_FILE` is
    derived from `__file__`, so a module imported out of a linked worktree resolves it to that
    worktree -- where the log is absent, and `ids_run_since` returned `[]` without a word. The
    union in `focus_drawn_since` then quietly lost a whole channel and the brief read
    `drawn: [], steered: false`: *"the previous direction named work and NONE of it was drawn --
    if this repeats, the steer is a no-op"*. That is the precise false reading the third channel
    was built to abolish, reintroduced by path resolution rather than by logic, and it is
    REACHABLE because a drawn tick runs in a worktree and is told to orient there.

    Measured 2026-09-02, same commit, same code, two trees: from the worktree
    `ids_run_since(now-24h)` answered `[]`; from the shared tree, nine ids.

    `git rev-parse --git-common-dir` is the question "where is the real tree" asked of the only
    thing that knows. Falls back to `LOG_FILE` when git will not answer or the shared copy is
    absent, which preserves the deliberate missing-log-is-empty behaviour rather than trading one
    silent failure for a noisy one on a path an orientation must survive.
    """
    try:
        out = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=str(PROJECT_DIR),
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return LOG_FILE
    if out.returncode != 0 or not out.stdout.strip():
        return LOG_FILE
    common = Path(out.stdout.strip())
    if not common.is_absolute():
        common = (PROJECT_DIR / common).resolve()
    shared = common.parent / "docs" / "observability" / LOG_FILE.name
    return shared if shared.exists() else LOG_FILE


def ids_run_since(cutoff: float, *, path: Path | None = None) -> list[str]:
    """Work ids this executor took a turn on at or after `cutoff`, read from its own log.

    THE THIRD DRAWN CHANNEL, and it exists because the other two cannot see this route at all.
    `delivery_seat.build_brief` reported `drawn: []` for five ids while this log carried seven
    RUNNING/FINISHED pairs naming them: the atom stall tracker is keyed by maturity-map atom id and
    a Lane 0 slug is by construction not one, and `delivery_lane.drawn_since` records what the
    LANE handed out -- which is empty for an item the executor took as a promoted continuation,
    because that route never goes through `draw()`. Two channels, and the one route that had
    actually run was in neither. A steer that IS biting presenting as a steer that is not is the
    same fail-silent shape as an exit code standing in for a landing; both instruments were
    reporting on themselves rather than on their subject.

    MINUTE RESOLUTION, from the log's own stamp. A line inside the cutoff minute reads as before
    it -- under-reporting by up to 60s, again the safe direction.

    Never raises: it is called from an orientation that must not be lost to a missing log.

    THE DEFAULT IS THE SHARED TREE'S LOG, not this tree's -- see `_shared_tree_log` for what that
    cost before it was. `path=` still overrides for tests, which need a fixture rather than the
    live artefact; the two want opposite things from this constant and only the explicit argument
    can hold both.
    """
    log_file = path or _shared_tree_log()
    try:
        text = log_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    found: set[str] = set()
    for line in text.splitlines():
        match = _TURN_LINE.match(line)
        if not match:
            continue
        work_id = match["running"] or match["finished"] or match["nothing"]
        if not work_id or work_id in found:
            continue
        try:
            when = calendar.timegm(time.strptime(match["stamp"], "%Y-%m-%d %H:%M"))
        except ValueError:
            continue
        if when >= float(cutoff):
            found.add(work_id)
    return sorted(found)


def _interactive_seat_is_live(now: float | None = None) -> bool:
    """Is a human-driven seat session holding this seat right now?

    ASKS `seat_continuity.state()` RATHER THAN RE-DERIVING LIVENESS. The first draft of this
    carried its own `INTERACTIVE_SEAT_WARM_SECONDS` threshold, which would have been a second
    answer to a question that already has an owner — the exact defect the end-to-end canon names,
    written into the module built to remove it. `seat_continuity` already reasons about this
    properly: death needs TWO signals (a silent heartbeat AND no live interactive process), with a
    fail-silent escape at `CERTAINLY_DEAD_SECONDS` so a stopped machine cannot look alive forever.

    ABSENT reads as NOT LIVE, deliberately. The safe direction here is to RUN: standing down on a
    missing observability file would give this executor a way to be silently switched off by an
    unrelated deletion, which is the control-goes-quiet class rather than a safety property.
    """
    from background import seat_continuity

    try:
        return seat_continuity.state(now=now) == seat_continuity.LIVE
    except Exception:  # noqa: BLE001 - liveness must never take the tick down
        return False


def _is_handed_off(item: dict, now: float | None = None) -> bool:
    """Was this item written by the interactive seat as a continuation, rather than re-derived?

    ASKS `seat_continuation` RATHER THAN INFERRING FROM THE ITEM'S SHAPE. A continuation and a
    focus item are both `{"id": ..., "what": ...}` dicts by the time `next_item` returns one, so a
    duck-type check would be a second, weaker answer to a question the store already owns -- and
    the store applies the six-hour window, which is what stops a handoff from outliving the tree it
    reasoned about.

    Absent or unreadable store reads as NOT handed off, which is the conservative direction here:
    it costs a stand-down that says why, and the alternative would let an unreadable file license
    an unattended writer to run beside a live seat.
    """
    from background import seat_continuation

    try:
        return any(c.get("id") == item.get("id") for c in seat_continuation.live(now=now))
    except Exception:  # noqa: BLE001 - a handoff store must never cost the machine a tick
        return False


#: WHAT `done_means` SAYS FOR AN AUTOMATIC PROMOTION, and why a constant is honest here.
#:
#: `seat_continuation.hand_off` refuses a handoff without a `done_means`, for a good reason: "a
#: tick handed a topic writes a restatement of it". That refusal guards a HUMAN handoff, where the
#: seat holds the context and is the only thing that can state an exit test. It cannot guard this
#: one, because a focus item genuinely has no exit test -- that is what makes it direction rather
#: than an atom (`delivery_lane` §"DONE IS DERIVED"), and scraping a marker out of its prose would
#: manufacture the field rather than carry it.
#:
#: The constant costs nothing that the refusal was protecting, because `delivery_lane.doorbell`
#: formats only `what`, `why` and `id`: `done_means` NEVER REACHES THE TICK'S PROMPT for either
#: kind of item. The tick is already told, in the doorbell itself, to decide what done means. So
#: what this string is for is the READER of the store -- it says the entry was written by the
#: machine at derivation rather than by a session, which is the provenance `seat_continuation`
#: exists to keep legible.
AUTO_PROMOTION_DONE_MEANS = (
    "DERIVED, NOT DECLARED -- this entry was promoted automatically by seat_executor at "
    "derivation, not written by a session. A focus item has no exit test; done is when the seat's "
    "next orientation stops naming it (delivery_lane, 'DONE IS DERIVED'). The tick decides what "
    "done means for the piece it takes, exactly as the doorbell tells it to."
)


def _promote_to_handoff(work_id: str, now: float | None = None) -> tuple[bool, str]:
    """Write a re-derived focus item into the handoff store. Returns `(promoted, refusal)`.

    THE ONE CALL SITE IS THE STAND-DOWN ABOVE, and the write happens on the tick that DECLINES the
    work rather than on the tick that takes it. That ordering is the mechanism: it turns an
    unclaimed decision, which loses to a live heartbeat every single time, into a claimed handoff,
    which the same guard already lets through.

    IT GOES THROUGH `delivery_lane.hand_off_focus` RATHER THAN WRITING THE STORE DIRECTLY, and the
    refusal that route carries is the reason. `hand_off_focus` re-reads
    `direction.unreachable_focus` and raises unless `work_id` is a LIVE, DRAW-UNREACHABLE focus
    item -- so this cannot promote an atom the dial-weighted draw already reaches, cannot promote
    an expired direction record, and cannot promote something invented in between. Promoting work
    the draw can already reach would create a second route to the same item, which is the
    duplication the path-keyed guard exists to refuse.

    NEVER RAISES. A handoff store must not cost the machine a tick, and the caller stands down with
    the named reason either way -- which is also how a promotion that stops working stays visible
    rather than going quiet.
    """
    try:
        delivery_lane.hand_off_focus(work_id, AUTO_PROMOTION_DONE_MEANS, now=now)
    except Exception as exc:  # noqa: BLE001 - see NEVER RAISES above
        return False, f"{type(exc).__name__}: {str(exc).strip()[:160]}"
    return True, ""


#: A worktree declares itself IN USE by dropping this file with the owning pid in it. Any writer
#: may write one -- the seat executor does it automatically, an interactive session working in a
#: worktree can do it by hand -- and the daemons that sweep worktrees read it.
OWNER_MARKER = ".se_worktree_owner"

#: HOW LONG A CLAIM LASTS. A marker is a LEASE, not a deed: it expires, and an expired claim is
#: not a live writer whatever pid it names.
#:
#: DERIVED, NOT PICKED. The longest a writer may legitimately hold a worktree is one bounded turn
#: -- `SESSION_TIMEOUT_SECONDS` above, which systemd enforces -- plus a grace for a slow start and
#: for clock skew between the marker's mtime and the turn's real end. A writer that genuinely needs
#: longer re-writes its marker, which is one line and refreshes the lease.
#:
#: WHY A PID ALONE WAS NOT ENOUGH (2026-09-01, director: "give them a lifetime"). Five worktrees
#: carried a marker naming pid 215 -- the tmux SERVER, started 2026-08-24 and alive for as long as
#: the console is. `pid_is_alive(215)` is true today and will be true next month, so every one of
#: those five read as "a live writer holds this worktree" a full day after its writer had gone. The
#: reaper is ARMED and refused all five; `fork_salvage` skipped all five. The isolation machinery
#: was working and nothing could ever tidy up behind it.
#:
#: A bare pid is a WEAK IDENTITY, and the pid a hand-working session can most easily name is the
#: longest-lived process on the box -- so the failure is not one careless write, it is the shape of
#: the claim. A lease fixes the class: whatever pid is named, the claim dies of old age.
OWNER_LEASE_SECONDS = SESSION_TIMEOUT_SECONDS + 30 * 60


def _claim_age_seconds(marker_path, now: float | None = None) -> float | None:
    """Seconds since the ownership claim at `marker_path` was last written, or None if unreadable.

    Its own function so the lease decision is testable without a clock, and so an unreadable mtime
    is a distinct answer from a fresh one -- an mtime that cannot be read must not silently become
    "written just now", which is the fail-open that would restore the immortal claim."""
    try:
        return (time.time() if now is None else now) - marker_path.stat().st_mtime
    except OSError:
        return None


def worktree_is_live(path) -> bool:
    """Is a writer's process still working inside this worktree?

    THE ONE HOME FOR THE QUESTION, and it is public because two daemons outside this module have to
    ask it. `background/fork_salvage` sweeps worktrees for uncommitted work and commits it;
    `background/fork_reconciler` reaps worktree directories and its reaper is ARMED. Both were
    written when no worktree on this machine had a resident writer — reasonably, because until
    2026-08-31 none did.

    WHAT IT COST, TWICE IN ONE EVENING. `fork_salvage` committed `SALVAGE(auto)` inside
    `/var/tmp/se-seat-executor` four minutes into the executor's first turn — an ungated commit
    under a running writer's HEAD, which rode onto `main` beneath the landing because the promotion
    route was then verifying only the tip. **Ninety minutes later it did the same to the delivery
    seat's own landing worktree**, mid-preparation, and the first version of this function did not
    cover it: it compared against `WORKTREE` and nothing else, so it exempted the executor and left
    every other writer exposed. That is the wrong subject. The property is *a live writer*, not
    *this module's path*.

    And `fork_reconciler`'s reaper is the sharper one, still un-fired only by luck: it refuses a
    DIRTY worktree, and the executor is dirty for most of a turn — but there is a window at the
    start of every turn, after `ensure_worktree` resets and cleans and before the first edit, when
    the tree is clean and detached at `origin/main`, which is to say MERGED and **reap-eligible**.
    `git worktree remove` on a live writer is the whole turn gone.

    ANY WRITER MAY DECLARE ITSELF, which is what makes this general rather than a special case for
    one daemon. `OWNER_MARKER` holds the owning pid; this executor writes one for its own worktree,
    and a session working in a worktree by hand can write one too. The executor's own `PID_FILE` is
    still honoured for the worktree it owns, so nothing depends on the marker having been written.

    A PID **WITH A LIVENESS CHECK**, never the file's mere existence. A killed writer leaves its
    marker behind, and that worktree holds exactly the abandoned work those daemons exist to rescue
    and reap — the 2026-08-03 sweeps found modules that existed nowhere else, one `rm -rf` from
    being lost. Exempting a path outright would trade one collision for a class of silent losses.

    AND A LEASE ON TOP OF THE PID (2026-09-01). A live pid is necessary and was not sufficient: see
    `OWNER_LEASE_SECONDS` for the five worktrees that spent a day claimed by the tmux server. Both
    legs must hold — the named process alive AND the claim younger than the lease — because either
    one alone has a permanent failure mode: a pid alone never expires, and an mtime alone would
    release a worktree whose writer is mid-turn but wrote its marker early.
    """
    try:
        resolved = Path(path).resolve()
    except (OSError, ValueError):
        return False

    # 1. THE MARKER, which any writer can drop. Checked first because it is the general answer.
    try:
        marker_path = resolved / OWNER_MARKER
        marker = int(marker_path.read_text().strip())
        age = _claim_age_seconds(marker_path)
        # An unreadable mtime (age is None) FAILS THE LEASE. The marker was readable a line ago, so
        # this is a genuine anomaly, and the safe direction for an anomaly here is "the claim is not
        # established" -- the dirty check and the salvage step still stand between that answer and
        # any loss.
        if pid_is_alive(marker) and age is not None and age < OWNER_LEASE_SECONDS:
            return True
    except (OSError, ValueError):
        pass

    # 2. GIT'S OWN LOCK, which is a claim no process death can invalidate.
    #
    # ADDED 2026-09-02, after a marker proved untrustworthy in the one way that matters. A landing
    # worktree's marker held the pid of a shell that had already exited -- `$$` from a command whose
    # shell did not outlive it -- so leg 1 correctly said "no writer" and the reaper removed the
    # directory nine minutes into its commit gate. Switching that landing to `git worktree lock`
    # protected it from the reaper, which refuses a locked worktree outright... and then
    # `fork_salvage` committed into it anyway, because IT asks this function and this function did
    # not know about locks. Two daemons, two liveness signals, one of them invisible to the other.
    #
    # A lock is the better claim on its own merits: it is git's own mechanism, it is declarative, it
    # survives any process, and it carries a human-readable reason. Honouring it here is what makes
    # `git worktree lock` a claim BOTH daemons respect, because both come through this door.
    #
    # A LOCK IS A DELIBERATE ACT AND IS NOT LEASED. Unlike a pid, nobody leaves one behind by
    # crashing -- you have to type it -- so a stale lock is a person's mistake to undo with
    # `git worktree unlock`, and the reaper's report names it every cycle. The accretion risk this
    # module worries about is a marker nobody meant to leave; a lock is the opposite.
    try:
        locked = subprocess.run(
            ["git", "-C", str(PROJECT_DIR), "worktree", "list", "--porcelain"],
            capture_output=True, text=True, timeout=30)
        if locked.returncode == 0:
            here = False
            for line in (locked.stdout or "").splitlines():
                if line.startswith("worktree "):
                    here = Path(line.split(" ", 1)[1]).resolve() == resolved
                elif here and line.startswith("locked"):
                    return True
    except (OSError, ValueError, subprocess.SubprocessError):
        pass

    # 3. THIS EXECUTOR'S OWN WORKTREE, via the pid file it already keeps. Kept so the executor is
    #    covered even on a turn where the marker could not be written.
    try:
        if resolved != WORKTREE.resolve():
            return False
        return pid_is_alive(int(PID_FILE.read_text().strip()))
    except (OSError, ValueError):
        return False


def _worktree_claims() -> Path:
    """The delivery-lane claims store INSIDE the executor's worktree.

    `delivery_lane.PROJECT_DIR` is `Path(__file__).resolve().parent.parent`, so the child running
    `python3 -m background.delivery_lane --landed/--release <id>` with its cwd in the worktree
    imports the WORKTREE's copy of the module and reads and writes THIS file. The shared store
    never hears it. That is not a bug to route around -- it is what worktree isolation is for --
    so both readers here ask both stores instead, and `delivery_lane.CLAIMS_FILE` keeps pointing
    at the tree that imported it.
    """
    return WORKTREE / "docs" / "observability" / delivery_lane.CLAIMS_FILE.name


def _claim_stores() -> tuple[Path, ...]:
    """EVERY store a turn's claim is written to. ACQUIRE AND RELEASE BOTH ITERATE THIS.

    That is the entire reason this is a function and not a tuple literal written out twice. The
    claim loop in `run_once` gained a store on 2026-09-02 and `_hand_back` did not, so from that
    commit the executor wrote three claims per turn and released one. `seat_work_in_hand`'s copy
    was the orphan, and because it is written with `paths=[]` and `record_landing` only ever binds
    paths into the DELIVERY-LANE store, its idle clock started at the claim and could never
    restart -- no matter what the turn landed.

    WHAT THAT COST, measured on the live record rather than reasoned about. Forty-five minutes
    after each turn (`seat_work_in_hand.STALE_AFTER_SECONDS`) the next unattended writer to call
    `refuse_if_duplicated` swept the orphan and escalated `[SEAT] <id> was claimed and has not
    moved`. Three consecutive executor turns of 2026-09-02 are appended to
    `docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-08-26.md` by that route, and the
    last of them -- `an-exit-code-is-not-a-landing` -- has a log line reading `1 of 1 bound
    path(s) moved on the shared tree` for the same turn. Two instruments on one turn disagreeing,
    and the alarm was the one with no way to be right: it reads the only store the turn's paths
    never reach.

    The three answer three different questions, which is why they are three files and not one:

      * `seat_work_in_hand` -- the CROSS-LANE PATH GUARD's store (`refuse_if_duplicated`).
      * the SHARED delivery-lane store -- what `next_item` filters on, so it is what stops a
        concurrent draw handing this item to a second writer mid-turn.
      * the WORKTREE's delivery-lane store -- the one the CHILD reaches, because its cwd is the
        worktree and `python3 -m background.delivery_lane --landed <id>` imports that copy.

    NOT the same list as `_still_claimed` reads, and that asymmetry is deliberate: that function
    asks whether the TICK released, and a tick can only reach the two delivery-lane stores.
    """
    return (delivery_lane.claims_mod.CLAIMS_FILE, delivery_lane.CLAIMS_FILE, _worktree_claims())


def _still_claimed(work_id: str) -> bool:
    """Is the lane's claim on this id still held? An unreadable store reads as STILL CLAIMED.

    Conservative in the direction that costs a repeat rather than a loss: mistakenly discharging a
    handoff loses the seat's judgement about what comes next, and mistakenly keeping one costs a
    tick that finds the work already done and says so.

    BOTH STORES, AND `held` IN EITHER IS NOT ENOUGH -- it must be held in BOTH. `run_once` writes
    the claim to both, so the id going ABSENT from either one is a release that really happened:
    from the worktree store when the tick ran `--release` (its cwd is the worktree, so that is the
    copy it reaches), from the shared store when a tick or a sweep released it there.

    THIS USED TO ASK ONE STORE AND IT WAS THE WRONG ONE. `run_once` claimed via
    `claims_mod.claim(...)` with no `path=`, which is `seat_work_in_hand`'s store, and this asked
    `delivery_lane.held()`, which is a different file. The condition was therefore never true, the
    discharge fired unconditionally, and its stated reason -- *"the tick released its claim"* --
    was false on all six turns of 2026-09-02 that carry it. R15's fourth shape arriving through
    the discharge door instead of the refusal door. Finding:
    `docs/staging/done/SEAT_FINDING_THE_EXECUTORS_DISCHARGE_ASKS_A_STORE_ITS_OWN_CLAIM_NEVER_REACHES_2026-09-02.md`.
    """
    for store in (delivery_lane.CLAIMS_FILE, _worktree_claims()):
        try:
            if work_id not in delivery_lane.held(path=store):
                return False
        except Exception:  # noqa: BLE001
            return True
    return True


def _hand_back(work_id: str, claimed_at: float) -> None:
    """Release the claims THIS turn took, in EVERY store it took them in, and only if still ours.

    IT RELEASED ONE OF THREE UNTIL 2026-09-03 and the orphan alarmed on finished work 45 minutes
    later. `_claim_stores()` is now the single list both ends read; read its docstring for the
    measurement. A store added there and released here is one change, not two that can drift.

    WHY THE EXECUTOR RELEASES ITS OWN CLAIM AT ALL, and it is the clause that makes claiming in
    this store safe. `delivery_lane.next_item` skips any id in `held()` -- that filter is the
    entire mechanism by which an item is not handed out twice. So a claim left standing after the
    turn ends does not protect anything; it SUPPRESSES THE RE-OFFER that a `LANDED NOTHING`
    verdict exists to produce, and the item would wait for the 100-minute sweep instead of the
    next tick. Buying the verdict's *yes* at the price of the re-offer would be the same defect one
    door along, which is why the repair is not the one-line diff the finding proposed.

    The claim is real and load-bearing FOR THE DURATION OF THE TURN: it is what stops a concurrent
    draw handing the same item to a second writer while this one is running.

    MATCHED ON `claimed_at`, so this releases what it took rather than whatever is there now. If
    another writer re-claimed the id mid-turn, that claim is theirs and outlives this call.

    Never raises, and PER STORE rather than once around the loop: a turn that has already produced
    its verdict must not lose it to bookkeeping, and one unreadable store must not cost the release
    of the two beside it.
    """
    for store in _claim_stores():
        try:
            rec = delivery_lane.claims_mod._load(store).get(work_id)
            if isinstance(rec, dict) and float(rec.get("claimed_at", 0)) == claimed_at:
                delivery_lane.claims_mod.release(work_id, path=store)
        except Exception:  # noqa: BLE001
            continue


def seat_continuation_drop(work_id: str) -> bool:
    """Drop a discharged continuation. Never raises -- a handoff store must not cost a tick."""
    try:
        from background import seat_continuation

        return bool(seat_continuation.drop(work_id))
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------------------------------------
# THE VERDICT. It reads the SUBJECT, and it is deliberately not the exit code.
#
# WHAT IT REPLACED, AND WHAT THAT COST. The turn's outcome used to be `f"{work_id}: rc={returncode}"`
# logged as `FINISHED`. `land-the-dd-inference-organ-and-unwedge-every-lanes-publish` took four
# consecutive turns on 2026-09-02 -- 15:36, 16:35, 17:37 and the promotion before them -- and every
# one logged `FINISHED ... rc=0`. Eleven hours. The work did not land, the publish stayed wedged,
# and the seat that had RANKED the item read its own log and saw four successes. An exit code is a
# fact about a PROCESS; the claim is about a TREE. Reporting the first as the second is R15's
# fail-silent killer, and this module was the instrument least able to notice, because it was the
# one reporting on itself.
#
# THE TWO LEGS, and each is load-bearing on its own.
#
#   1. THE TICK BOUND A LANDING DURING THIS TURN. `delivery_lane.record_landing` is where a tick
#      says "this commit is mine", and it already refuses a commit that is unreadable, empty, or
#      older than the id's first draw. Leg 1 asks whether that binding happened AFTER this turn
#      started -- a tombstone from a previous turn is the across-turns fail-open, and the first
#      draft of this check (bound paths non-empty) would have had exactly it: turn 1 binds, turns
#      2-4 land nothing, all four read as landed.
#
#   2. THE SHARED TREE AGREES. Leg 1 alone is still the tick reporting on itself, and it passes
#      for the precise failure that motivated all this: `git show` reads the shared OBJECT
#      DATABASE, which a linked worktree writes into, so a commit made in the worktree and never
#      promoted binds perfectly well. Leg 2 asks git whether those paths actually moved on the
#      shared tree between the sha the turn started on and the sha now. A worktree commit that was
#      never promoted fails it, which is the whole point.
#
# NEITHER LEG IS THE SESSION'S OWN ACCOUNT OF ITSELF.
# ---------------------------------------------------------------------------------------------


def shared_tree_changes_since(base: str) -> tuple[set[str], str]:
    """Paths that changed on the SHARED tree since `base`, plus a reason if it cannot be read.

    BOTH ENDS OF THE SHARED TREE ARE ASKED -- its own HEAD and `origin/main` -- because a turn's
    landing is observable at either. `promote_worktree_landing` moves the shared branch, and the
    push that follows is a separate act that fails on its own often enough to have a standing
    alarm here. Reading only `origin/main` would call a landed-but-unpushed increment nothing;
    reading only HEAD would miss a turn that landed and pushed while the shared HEAD sat behind.

    THREE-DOT, so only the far side's changes count. Two-dot would credit this turn with paths
    that moved on the BASE side of a divergence -- another lane's revert reading as this tick's
    landing.

    `(set(), reason)` when git will not answer, and the caller treats that as NOTHING LANDED. An
    unavailable check is a failed check; the direction it must fail in is the one that costs a
    repeated turn rather than one that consumes work nobody did.
    """
    if not base:
        return set(), "the turn recorded no base sha, so there is nothing to compare against"
    changed: set[str] = set()
    unreadable: list[str] = []
    for ref in ("HEAD", "origin/main"):
        try:
            out = subprocess.run(
                ["git", "diff", "--name-only", "--no-renames", f"{base}...{ref}"],
                cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.SubprocessError) as exc:  # noqa: PERF203
            unreadable.append(f"{ref}: {exc.__class__.__name__}")
            continue
        if out.returncode != 0:
            unreadable.append(f"{ref}: git refused ({(out.stderr or '').strip()[:100]})")
            continue
        changed |= {ln.strip() for ln in out.stdout.splitlines() if ln.strip()}
    if not changed and unreadable:
        return set(), "the shared tree could not be read -- " + "; ".join(unreadable)
    return changed, ""


def bound_landing(work_id: str) -> tuple[float, list[str]]:
    """The newest landing bound to `work_id`, from EITHER store this turn could have written.

    TWO STORES, AND THE SECOND IS NOT BELT-AND-BRACES. `delivery_lane.PROJECT_DIR` is derived from
    `__file__`, so the child running `python3 -m background.delivery_lane --landed <id>` with its
    cwd in the worktree imports the WORKTREE's copy of the module and binds into the WORKTREE's
    claims store. The shared store never hears about it. A verdict that read only the shared store
    would therefore answer LANDED NOTHING for every correctly-behaved turn as well as every failed
    one -- a constant verdict, which is not a control (R15).

    The worktree's store is the STRONGER witness where it exists: `ensure_worktree` resets that
    tree at the start of every turn, so anything in it was written by THIS turn's child. It is
    still only leg 1 -- the shared tree has to agree separately.

    `(0.0, [])` if neither store carries one. Never raises.
    """
    best: tuple[float, list[str]] = (0.0, [])
    for store in (delivery_lane.CLAIMS_FILE, _worktree_claims()):
        try:
            when, paths = delivery_lane.last_landing(work_id, path=store)
        except Exception:  # noqa: BLE001
            continue
        if when > best[0] and paths:
            best = (when, paths)
    return best


def subject_moved(work_id: str, base: str, since: float) -> tuple[bool, str]:
    """Did `work_id`'s bound paths actually move on the shared tree during this turn?

    `since` is the instant the turn's session was spawned; `base` the sha the shared tree was at
    then. Returns `(moved, reason)` and the reason is written for the log either way -- a refusal
    that does not name its cause is how the previous verdict survived four turns.
    """
    landed_at, landed_paths = bound_landing(work_id)
    if landed_at <= since or not landed_paths:
        return False, ("no landing was bound to the claim during this turn -- the tick never ran "
                       "`--landed`, or `record_landing` refused the commit it named "
                       "(`python3 -m background.delivery_lane --landed <id>` prints the reason)")
    changed, unreadable = shared_tree_changes_since(base)
    if unreadable:
        return False, unreadable
    overlap = sorted(set(landed_paths) & changed)
    if not overlap:
        return False, (f"the tick bound {len(landed_paths)} path(s) from a commit the SHARED tree "
                       f"does not carry -- a worktree commit that was never promoted reads exactly "
                       f"like this, and `tools.promote_worktree_landing` is what moves it")
    return True, (f"{len(overlap)} of {len(landed_paths)} bound path(s) moved on the shared tree, "
                  f"including {overlap[0]}")


def _another_executor_is_running() -> bool:
    """A pid file WITH a liveness check. A bare lock left by a killed process never runs again.

    `/proc` RATHER THAN THE SIGNAL-0 PROBE, and that is a safety invariant rather than a style
    choice. `tests/background/test_substep4_exit.py::test_reaper_absent_no_kill_path_in_background`
    greps every `background/*.py` for any signal-sending call, because the exit-143 vector that
    killed an interactive session came from a reaper in this directory; the control is deliberately
    blind to the signal ARGUMENT, since a probe and a kill differ by one integer and a grep that
    trusted the integer would have to be right about every future edit. The first draft of this
    function used the signal-0 probe and reddened that control plus its twin in
    `test_process_reconciler.py`, wedging the operational-layer signal for every lane.

    `tools.wait_for.pid_is_alive` is the reuse, and it is also the better probe: the signal form
    raises PermissionError for a live process owned by someone else -- which the first draft had to
    special-case, and `/proc` does not. `background/worker_tick.py::_pid_alive` reaches the same
    conclusion for the same reason; this one is public and takes no second copy.
    """
    try:
        pid = int(PID_FILE.read_text().strip())
    except (OSError, ValueError):
        return False
    return pid_is_alive(pid)


def ensure_worktree(base: str) -> Path:
    """The executor's own worktree at `base`, created if absent and reset to it if present.

    RESET, not merge: this worktree holds no history worth keeping between turns. Anything it
    landed was promoted at the end of the turn that landed it.

    THE SENTENCE THAT USED TO FINISH THAT PARAGRAPH WAS FALSE, AND IT COST A 2h25m MEASUREMENT.
    It read: *"anything it did not land was not finished — carrying that forward would hand the
    next turn a tree it did not build."* That is true of a turn's scratch and false of a DETACHED
    background job, which is the one thing here deliberately built to outlive the turn that
    launched it. A `systemd-run --user` unit is the sanctioned way to run a measurement longer
    than a bounded invocation; it keeps writing into this worktree for HOURS after its launching
    turn is gone. On 2026-09-03 `se-noise-floor-all-20260903b.service` finished at 15:18:37 and
    wrote `docs/observability/value_cycle_ab_s1_noise_floor_20260903.json` — the undecomposed
    floor leg, the last input the published live-world bound was waiting on. The next call to this
    function, at 15:35:25, reset and then `git clean -qfd`'d it away 17 minutes later. Untracked
    and never added, it went to no commit and no object: `find / -xdev` returns nothing.

    THE HARM IS THE MISREADING, NOT THE HOUR. `-qfd` is silent, so an absent `--out` path is the
    only trace — and an absent artefact is exactly what a run STILL IN PROGRESS looks like. That
    is the third distinct cause of one absence: the OOM kill, then the headroom refusal that
    returned 2 without writing, and now this. Both earlier fixes are still correct and neither
    could have caught this one, because here the run SUCCEEDED and printed its answer.

    SO: SALVAGE, THEN RESET. `fork_salvage.salvage_worktree` is the reuse — it is fail-safe, never
    raises, and already commits untracked work to the worktree's own (here detached) HEAD, which
    is how the 15:14:18 salvage commit was still recoverable from the reflog after this same
    reset. Scratch still gets discarded from the working tree; the difference is that it is
    discarded INTO an object that can be dug back out, instead of into nothing.
    """
    if not (WORKTREE / ".git").exists():
        WORKTREE.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "worktree", "add", "--detach", "-q", str(WORKTREE), base],
            cwd=str(PROJECT_DIR), check=True, capture_output=True, timeout=300,
        )
    else:
        subprocess.run(["git", "fetch", "--quiet", "origin"],
                       cwd=str(WORKTREE), capture_output=True, timeout=300)
        salvage_worktree({"path": str(WORKTREE), "branch": None})
        subprocess.run(["git", "reset", "--hard", "-q", base],
                       cwd=str(WORKTREE), check=True, capture_output=True, timeout=300)
        subprocess.run(["git", "clean", "-qfd"],
                       cwd=str(WORKTREE), capture_output=True, timeout=300)
    return WORKTREE


def _resolve_claude() -> str | None:
    for candidate in (os.environ.get("CLAUDE_BIN"), "claude",
                      str(Path.home() / ".nvm/versions/node/v24.16.0/bin/claude")):
        if not candidate:
            continue
        try:
            if subprocess.run(["which", candidate], capture_output=True,
                              text=True, timeout=10).returncode == 0:
                return candidate
        except Exception:  # noqa: BLE001
            continue
    return None


CHARTER = """You are the delivery seat, continuing work autonomously in an ISOLATED git worktree.

YOU ARE NOT ON THE SHARED TREE. Your cwd is a linked worktree; nothing you do here can touch
another writer's uncommitted work. That isolation is the whole reason you are allowed to run.

HOW TO LAND, and there is no other way:
  1. `python3 -m tools.surgical_land -m "<message>" <exact paths>` — the sanctioned door. It works
     from this worktree. Hook bypass is a wall: never --no-verify, never a hand-built commit.
  2. `python3 -m tools.promote_worktree_landing . --work-id <your claim id>` — gets the landing onto
     origin/main, or refuses with a named cause. If it refuses because origin moved, re-gate on the
     new base and land again. Never force anything.
  3. `python3 -m background.delivery_lane --landed <your claim id>` — binds the paths that commit
     touched to your claim. THIS IS WHAT THE TURN IS JUDGED ON. When the turn ends, the executor
     asks whether those bound paths moved on the SHARED tree; a turn that landed nothing, or that
     committed here and never ran step 2, is logged `LANDED NOTHING` and the item is re-offered
     rather than consumed. Your exit code is not consulted.

IF IT IS BIGGER THAN ONE TURN, LAND THE PART YOU FINISHED. A landed increment proves the work is
moving; an unlanded whole proves nothing and is lost when this turn ends.

WRITE DOWN WHAT YOU FOUND. A finding in docs/staging/ with its severity header, and a
pre-registration BEFORE any measurement whose answer you do not already know.

WHEN YOU ARE DONE, hand the next piece on:
  `python3 -m background.seat_continuation --hand-off ID WHAT WHY DONE_MEANS`
"""


def build_prompt(item: dict) -> str:
    return CHARTER + "\n\nTHE WORK:\n\n" + delivery_lane.doorbell(item)


def run_once(*, dry_run: bool = False, now: float | None = None) -> tuple[bool, str]:
    """One bounded turn. Returns `(ran, detail)`; a stand-down is `(False, reason)`, never a raise."""
    try:
        if _another_executor_is_running():
            raise StoodDown("another executor is already running")

        item = delivery_lane.next_item(now=now)
        if item is None:
            raise StoodDown("nothing to do: no continuation and no unclaimed focus item")

        work_id = item["id"]

        # THE SEAT-IS-LIVE STAND-DOWN NOW ASKS ABOUT CONTENTION, NOT PRESENCE (2026-08-31).
        #
        # It used to run FIRST and refuse on a warm heartbeat alone, which made this executor
        # unrunnable in exactly the situation it was built for. What it is protecting against is
        # TWO WRITERS CHOOSING WORK FROM THE SAME QUEUE. A continuation is not that: it is the
        # interactive seat writing down, deliberately and in full context, *"this piece is for
        # whoever runs next"*. Standing down on a handoff because the session that WROTE the
        # handoff is still alive refuses the one thing the mechanism exists to do -- and the
        # session is nearly always still alive, because it writes the handoff and then keeps
        # working.
        #
        # THE 2026-08-31 NARROWING LEFT A FOCUS ITEM OUTSIDE IT, AND THAT WAS SEVERANCE RATHER
        # THAN CAUTION (measured, 2026-09-01). `_interactive_seat_is_live` is true whenever any
        # session is running and one always is, so a focus item was not SOMETIMES declined -- it
        # was never reachable. `docs/observability/seat-executor-log.md` records thirty-two
        # identical stand-downs unbroken from 2026-08-31 23:35, five different work ids, zero
        # turns. A refusal whose condition is never false is not a control; it is a disconnected
        # wire that reports itself as safety.
        #
        # SO THE STAND-DOWN NOW PROMOTES INSTEAD OF DISCARDING. The item is written into the
        # handoff store here, at derivation, and THIS tick still stands down -- which keeps the
        # whole of what the old refusal was actually protecting: a live seat part-way through the
        # item with nothing claimed gets the rest of this cycle, and by the next tick it will have
        # either landed something (the path guard three lines below then sees it) or moved on. The
        # cost is one tick of latency. What it buys is a route that terminates.
        #
        # WHY NOT AUTO-RUN, AND WHY NOT "ESCALATE AFTER N DECLINES". Running immediately removes
        # the window the live seat needs; escalating after N declines is a stall wearing an
        # alert's clothes -- it converts a severed route into a louder severed route, and there is
        # nobody on the other end of it at 03:00, which is exactly when this executor matters.
        if _interactive_seat_is_live(now) and not _is_handed_off(item, now=now):
            promoted, refusal = _promote_to_handoff(work_id, now=now)
            if not promoted:
                raise StoodDown(
                    f"an interactive seat is live and {work_id!r} was not handed off to a tick, "
                    f"and it could not be promoted either: {refusal}"
                )
            raise StoodDown(
                f"an interactive seat is live, so {work_id!r} is PROMOTED rather than run: it is "
                "now a continuation a later tick can take, and this tick leaves the live seat the "
                "rest of the cycle to claim paths against it"
            )

        try:
            seat_work_in_hand.refuse_if_duplicated(
                list(item.get("paths") or []), exclude=work_id)
        except DuplicateWork as exc:
            raise StoodDown(f"the work duplicates a live claim: {exc}") from exc

        if dry_run:
            # A DRY RUN THAT WRITES NOTHING CANNOT DEMONSTRATE ANYTHING. Every other outcome of
            # this function reaches the log -- RUNNING, FINISHED, STOOD DOWN -- and this one
            # returned silently, so "the executor can reach a handed-off focus item" was an
            # argument about the code rather than a record of it having happened. It is marked
            # DRY RUN in the ledger precisely so it can never be read back as a real turn.
            log(f"DRY RUN: would run {work_id} -- all four refusals passed")
            return False, f"would run {work_id} (dry run)"

        claude_bin = _resolve_claude()
        if claude_bin is None:
            raise StoodDown("claude binary not found")

        base = subprocess.run(["git", "rev-parse", "origin/main"], cwd=str(PROJECT_DIR),
                              capture_output=True, text=True, timeout=60).stdout.strip()
        worktree = ensure_worktree(base or "origin/main")

        # THE CLAIM GOES IN THREE PLACES AND EACH ONE ANSWERS A DIFFERENT QUESTION. It used to go
        # in one, and it was the one nothing downstream asked. `_claim_stores()` names the three
        # and says what each is for -- and `_hand_back` iterates THE SAME FUNCTION, so a store
        # added to the acquire is released by construction rather than by remembering. It was two
        # written-out loops for one day and they had already drifted by the end of it.
        #
        # `claimed_at` is captured because `_hand_back` matches on it: this releases the claim it
        # took, never whatever happens to be there when the turn ends.
        claimed_at = time.time()
        for store in _claim_stores():
            delivery_lane.claims_mod.claim(
                work_id, note=str(item.get("what") or "")[:200], paths=[],
                path=store, now=claimed_at)
        # Guarded like every other live-record write here: an unattended writer whose pid file a
        # test can forge is one a test can make look alive or dead.
        guard_live_ledger_write(PID_FILE, writer="seat_executor.run_once").write_text(
            str(os.getpid()))
        # DECLARE THE WORKTREE IN USE, in the worktree itself, so the daemons that sweep worktrees
        # can see it without knowing anything about this module. See `worktree_is_live`.
        try:
            (worktree / OWNER_MARKER).write_text(str(os.getpid()) + "\n")
        except OSError:
            pass  # a marker that cannot be written costs the PID_FILE route below, not the turn
        log(f"RUNNING {work_id} in {worktree} on {base[:9]}")

        # THE INSTANT THE SUBJECT IS MEASURED FROM. Taken before the spawn, from the same clock
        # `record_landing` compares commit timestamps against, so "bound during this turn" is a
        # comparison between two facts about git rather than a claim about the session.
        started = time.time()
        try:
            proc = subprocess.run(
                [claude_bin, "-p", "--dangerously-skip-permissions", "--model", MODEL,
                 build_prompt(item)],
                cwd=str(worktree), capture_output=True, text=True,
                timeout=SESSION_TIMEOUT_SECONDS,
                env=dict(os.environ, DISABLE_AUTOUPDATER="1", SE_SEAT_EXECUTOR="1"),
            )
            how = f"rc={proc.returncode}"
        except subprocess.TimeoutExpired:
            how = f"did not finish inside {SESSION_TIMEOUT_SECONDS}s"
        finally:
            PID_FILE.unlink(missing_ok=True)

        # THE SESSION'S OWN OUTCOME IS NOW A FOOTNOTE, not the verdict. `how` is still logged
        # because it separates a crash from a clean no-op when reading back, but nothing branches
        # on it: a turn that exits 0 and lands nothing and a turn that times out having landed an
        # increment are DIFFERENT results, and the exit code has them exactly backwards.
        moved, why = subject_moved(work_id, base, started)

        # ORDER IS LOAD-BEARING, both halves of it.
        #
        # READ FIRST: `_still_claimed` asks whether the TICK released, and `_hand_back` releases
        # this turn's own claim. Run in the other order, the executor's own bookkeeping would look
        # exactly like the tick saying it was finished, and every turn would discharge -- the same
        # unconditional discharge this repair removes, rebuilt out of the repair itself.
        #
        # HAND BACK ON BOTH PATHS, including `LANDED NOTHING`: the claim is what `next_item`
        # filters on, so holding it past the turn suppresses the re-offer rather than protecting
        # anything. The refusal has to leave the work in the pool AND drawable.
        tick_released = not _still_claimed(work_id)
        _hand_back(work_id, claimed_at)

        if not moved:
            detail = (f"LANDED NOTHING: {work_id}, bound paths unchanged since {base[:9]} "
                      f"({how}) -- {why}")
            # NO DISCHARGE. The claim stays whatever the tick left it, and the handoff is NOT
            # dropped, so `seat_continuation` re-offers the item to the next tick instead of it
            # being consumed by a turn that did nothing. This is the half that makes the verdict
            # worth reading: a refusal that still let the work be discharged would be a louder
            # version of the same eleven hours.
            log(detail)
            return True, detail
        detail = f"{work_id}: {how} -- {why}"

        # A RELEASED CLAIM DISCHARGES THE HANDOFF (2026-08-31), and the two stores had never
        # spoken. `seat_continuation` re-offers a live continuation on every tick until its six-hour
        # window closes; `delivery_lane` claims are released by the tick calling `--release` when it
        # judges the work finished. Nothing connected them, so the FIRST handoff this executor ever
        # took was drawn twice -- 18:12 and again at 19:06 on the same id.
        #
        # RE-OFFERING IS DELIBERATE while work is unfinished: the charter tells a tick to land the
        # part it finished, and a piece bigger than one turn must come back. So the signal is not
        # "a turn ended", it is "the tick said it was done" -- which is exactly what releasing the
        # claim means. If it did not release, the continuation stands and the next tick continues.
        # THE ABSENCE OF A DISCHARGE NOW NAMES ITS CAUSE, and that is not decoration.
        #
        # Until 2026-09-03 the only line written here was the DISCHARGED one, so a turn that did
        # not discharge was a SILENCE -- and three different things produce that same silence:
        # the verdict said LANDED NOTHING and returned above; `tick_released` was False; or
        # `seat_continuation_drop` found nothing, which is the case for EVERY DRAWN ITEM because a
        # draw writes no continuation record. Grading the finding's own §9.7 prediction --
        # "DISCHARGED on some turns and not others" -- ran straight into that: the one absence on
        # the live log was a drawn item, so it could not be attributed to the discharge condition
        # at all, and the flattering reading was the unearned one. An instrument whose negative
        # result carries no cause cannot be read back, which is the same complaint this whole
        # finding makes about the positive one.
        #
        # NEITHER NEW WORD CONTAINS "DISCHARGED", deliberately: the controls above assert on that
        # token, and a reason line that made them pass by string coincidence would be worse than
        # no reason line.
        if not tick_released:
            log(f"HANDOFF STANDS {work_id}: the tick did not release its claim, so the "
                "continuation is re-offered to the next tick rather than consumed")
        elif not seat_continuation_drop(work_id):
            log(f"NO HANDOFF TO DROP {work_id}: the tick released its claim, but no continuation "
                "record held this id -- a DRAWN item never has one, so this turn says nothing "
                "either way about the discharge condition")
        else:
            log(f"DISCHARGED {work_id}: the tick released its claim, so the handoff is done "
                "and will not be re-offered")
        log(f"FINISHED {detail}")
        return True, detail

    except StoodDown as reason:
        log(f"STOOD DOWN: {reason}")
        return False, str(reason)


def main(argv=None) -> int:  # pragma: no cover - operator surface
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--once", action="store_true", help="run a single bounded turn")
    ap.add_argument("--dry-run", action="store_true",
                    help="run every refusal and name what it WOULD take; spawn nothing")
    ap.add_argument("--status", action="store_true", help="print what a turn would do now")
    args = ap.parse_args(argv)

    if args.status or args.dry_run:
        ran, detail = run_once(dry_run=True)
        print(json.dumps({"would_run": ran, "detail": detail,
                          "interactive_seat_live": _interactive_seat_is_live(),
                          "another_executor": _another_executor_is_running()}, indent=1))
        return 0
    if args.once:
        ran, detail = run_once()
        print(detail)
        return 0 if ran else 0
    ap.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    from background._seat import refuse_if_foreign  # seat guard, FIRST act

    refuse_if_foreign("seat_executor")
    raise SystemExit(main())
