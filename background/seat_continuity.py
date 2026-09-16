#!/usr/bin/env python3
"""An interrupted interactive session hands its work over without anyone noticing it stopped.

REUSE: background/seat_continuity.py
CLASS: CUSTOM
INDEX: searched "seat", "stall", "watchdog", "heartbeat", "session", "resume", "handoff",
       "continuity". Four organs came back and each is used rather than rebuilt.
       `seat_work_in_hand` holds CLAIMS with a deadline and is the closest sibling -- it is
       imported, not duplicated, and this module supplies the half its docstring does not
       claim to cover. `interactive_session_probe.interactive_claude_pids()` already reads
       /proc for interactive seats and is the second liveness signal here. `deadmans_switch`
       watches whether the STACK is alive off git commit time -- the signal the director
       named as no longer sufficient, see below. `alarm_repetition.escalate` is the filing
       path and is called directly. What none of them does is notice that the SEAT
       specifically has stopped and turn what it was holding into something a fresh session
       can pick up.

WHY THIS EXISTS
---------------
Director, 2026-08-24: *"Third or fourth time an Anthropic API error has stopped this session
mid-work. The ticks recover on their own -- they just draw again next cycle -- but the
interactive seat doesn't, and nothing notices it has stopped. With ticks at 4h, commit silence
no longer distinguishes a slow cadence from a dead session ... I shouldn't be the mechanism
that spots a stall."*

THE SIGNAL THE OLD WATCHERS USE, AND WHY IT STOPPED WORKING. `deadmans_switch` measures the
newest git commit and pages when the tree goes quiet. That was a good proxy while the tick ran
every 60s and committed constantly: quiet meant broken. It is not a good proxy now. The tick
was slowed to 4h on 2026-08-22 and to 30 min on 2026-08-24, and at either cadence a perfectly
healthy machine is quiet for long stretches. So commit silence has become ambiguous exactly as
the director says -- it no longer separates "slow on purpose" from "the seat died mid-edit".

WHAT THIS MEASURES INSTEAD: TOOL CALLS BY THE SEAT. A live interactive session runs tools
continuously; a dead one runs none, immediately, whatever the tick cadence is. That signal is
specific to the seat, it is unaffected by how often anything else commits, and it goes silent
the instant the session dies rather than one cadence later.

AND IT IS NOT WRITTEN BY THE SEAT. `.claude/hooks/stamp_seat_heartbeat.py` is a PreToolUse
hook, so the HARNESS writes it on every tool call the seat makes. That matters twice. It
cannot be forgotten -- `seat_work_in_hand.claim()` has to be CALLED by the session, which is
an exhortation wearing a mechanism's clothes, and a session that dies before remembering to
claim leaves nothing behind. And it cannot be gamed: a seat that has stopped cannot keep
writing it, which is precisely the failure mode a self-written heartbeat has.

IT PROVES LIVENESS AND NEVER PROGRESS, and the distinction is the whole R15 argument.
`seat_work_in_hand`'s docstring rejects a seat-written heartbeat because "a heartbeat the seat
writes itself would be satisfied by the seat writing a heartbeat -- the tautology R15 names
first". That objection is about PROGRESS and it still stands: nothing here is ever evidence
that work advanced, and `stale_claims()` still decides that from commits touching the claimed
paths. A session can be perfectly alive by this measure and still be stalled, and the claim
deadline is what catches that. The two organs answer different questions and neither can cover
for the other.

ONE ROW PER SEAT, BECAUSE THE POPULATION IS NOT ONE (2026-09-16)
----------------------------------------------------------------
`.seat_heartbeat.json` was a single record and the thing it measures is not single-valued:
measured at 14:20Z, `/var/tmp/se-seat-executor` and `/home/rich/synthetic-enterprise` held TWO
LIVE SEATS at once, not one seat and one stale checkout. The store is therefore keyed by session
id. Two seats are two rows; one dying leaves its own row to go cold on its own clock, and
`sweep()` reads PER ROW so a survivor can never answer LIVE on a dead seat's behalf.

That is also what makes the shared-tree redirect correct, and it was refused until it was true:
`_resolve` carries the argument, and the reason the `git worktree list` sweeper the finding asked
for is refused in its place (the file is TRACKED, so enumerating worktrees enumerates CHECKOUTS —
three of four held a byte-identical 16-day-old record no seat there ever wrote). What replaces it
is the `tree` field on each row, so a handoff for a seat that died in a linked worktree reads
THAT tree's uncommitted work rather than the sweeper's.

TWO SIGNALS, AND DEATH NEEDS BOTH
---------------------------------
Declaring a LIVE seat dead is the expensive error, not the cheap one: a handoff would be filed
for work still in progress, a tick would adopt it, and two writers would edit the same files in
one shared tree -- which this project has already paid for once (2026-07-05, one writer's
staged files swept into another's commit). So `state()` requires BOTH a heartbeat that has gone
quiet AND `interactive_session_probe` finding no interactive session running at all. Either
alone returns LIVE.

WITH ONE EXCEPTION, because two-of-two is a fail-silent shape. If the probe cannot read /proc
it reports nothing, and "nothing" would then read as alive for ever -- an unavailable check is
a FAILED check (R15). So a heartbeat older than `CERTAINLY_DEAD_SECONDS` is death on its own: a
seat that has not run a single tool in four hours is not working, whatever /proc does or does
not say.

WHAT A HANDOFF CARRIES, and why it is derived rather than dictated. The director offered two
shapes -- the work made adoptable, or the session's state written down. This does both from
sources that survive the session dying, because anything the seat would have had to write down
ITSELF is exactly what an API error prevents it from writing:

  - the CLAIMS it held (`seat_work_in_hand`), which say what it thought it was doing;
  - the UNCOMMITTED PATHS in the tree, which are the work it actually left behind -- the real
    state, in the only form that cannot go stale;
  - the LAST TOOLS it ran, from the hook's own rolling tail, which say where it had got to;
  - its own last commit, which says where the finished part ended.

Filed into `docs/staging/`, which is already the tick's doorbell. The recovery agent is
therefore the tick -- the one thing in this system that provably recovers itself -- rather than
a new daemon that would need its own watcher. Nothing new has to be trusted.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from background.live_ledger_guard import guard_live_ledger_write, shared_tree_live_record

PROJECT_DIR = Path(__file__).resolve().parent.parent
HEARTBEAT_FILE = PROJECT_DIR / "docs" / "observability" / ".seat_heartbeat.json"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"

#: How long the seat may run no tools before its silence counts toward death. This is an INPUT
#: to the verdict, never the verdict: on its own it only says the seat is quiet, and a seat can
#: be quiet because one tool call is taking a long time.
#:
#: 20 minutes, from the two real numbers this repo has: a commit through the full gate takes
#: ~15 minutes and occasionally more, so anything under about 20 would call an honest fight
#: with the gate a death; and the tick runs every 30 minutes, so a dead session is adopted
#: inside one cadence. Paired with the probe, so a genuinely slow tool call is never death --
#: the session is still running.
SILENT_AFTER_SECONDS = 20 * 60

#: Death on the heartbeat ALONE, with no corroborating pid check. This is the fail-silent
#: escape: `interactive_claude_pids()` reading nothing must not mean "alive for ever". Four
#: hours is chosen so it can never fire on a live seat -- no tool call takes four hours, and a
#: seat waiting on the director is still running its Stop-hook chain.
CERTAINLY_DEAD_SECONDS = 4 * 60 * 60

#: How many recent tool calls the heartbeat keeps. Enough to say where the session had got to,
#: bounded so the file cannot grow without limit. It is a TAIL, not a transcript: the
#: transcript is Claude Code's and this must not become a second copy of it.
TOOL_TAIL = 12

LIVE, DEAD, ABSENT = "LIVE", "DEAD", "ABSENT"

#: The keyed store's one top-level field: session key -> that seat's beat. See `_seats`.
SEATS = "seats"

#: A ceiling on rows, so a store nobody sweeps cannot grow without limit. Rows are removed as
#: they are swept, so reaching this means the sweep itself has stopped -- the oldest beats are
#: dropped first, which is the direction that keeps the LIVE seats the executor must see.
MAX_SEATS = 64


def _resolve(path: Path | None, *, for_write: bool = False) -> Path:
    """Where this seat's book actually lives.

    THE REFUSAL RECORDED HERE ON 2026-09-16 IS WITHDRAWN, ON THE MEASUREMENT THAT REPLACED IT.
    It refused the shared-tree redirect because "the record is single-valued and the population
    is not": merging two concurrent seats' beats onto one record yields the SURVIVOR's answer, so
    a dead seat's row would be kept warm by a live one in another tree and swept by nobody. That
    reasoning was right about a single-valued record and is simply not about this one. The store
    below holds ONE ROW PER SEAT, so two live seats are two rows, and one dying leaves its own row
    to go cold on its own clock. The redirect's premise -- that a seat is a thing on this MACHINE,
    like `launch_liveness`'s `systemctl --user` unit, and not a thing in a tree -- was never in
    dispute; only the record's shape was.

    AND THE ENUMERATING SWEEPER THE FINDING ASKED FOR IS REFUSED IN ITS PLACE, on measurement
    taken 2026-09-16T15:30Z across all four linked worktrees. `.seat_heartbeat.json` is TRACKED,
    so `git worktree list` does not enumerate seats -- it enumerates CHECKOUTS. Three of the four
    worktrees held a byte-identical record (session `761ae288`, pid 3745366, 16 days old) that no
    seat in any of them ever wrote; it is what git put there. A sweeper walking worktrees would
    have filed three handoffs for one session that was never in those trees, and a phantom handoff
    is worse than a missed one because it sends the next tick to adopt work that does not exist.
    The discriminator `git diff HEAD` would tell a checkout from a beat, but only as a one-shot
    over residue: once every seat writes the one book, no worktree copy is ever written again and
    there is nothing left to enumerate. That is the register CLAUDE.md says to delete rather than
    write -- so what replaces it is the `tree` field on each row, which names the tree that seat
    was actually beating in, asked of the seat rather than of git's checkout table.

    THE COST IS A `git` SUBPROCESS PER TOOL CALL and it is paid rather than optimised away. The
    hook is a fresh process, so no module-level cache outlives it. There is a cheaper answer --
    a linked worktree's `.git` is a FILE naming the shared gitdir -- and taking it would put a
    SECOND implementation of "where is the shared tree" in this repo, which is already a filed
    finding. One answer, one owner.
    """
    p = path or HEARTBEAT_FILE
    return Path(shared_tree_live_record(p, for_write=for_write))


def _read(path: Path | None = None) -> dict:
    """The whole store, always in keyed shape. `{}` when there is nothing readable."""
    p = _resolve(path)
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # A corrupt heartbeat is not evidence of life. It falls through to ABSENT (no seats),
        # which files no handoff -- the same direction as never having run.
        return {}
    if not isinstance(data, dict):
        return {}
    return data if isinstance(data.get(SEATS), dict) else _adopt_legacy(data)


def _adopt_legacy(data: dict) -> dict:
    """A pre-keyed single record, read as the one-row store it was.

    NOT A MIGRATION STEP TO DELETE LATER. The file is TRACKED, so every linked worktree holds
    git's checkout of whatever shape was committed last, and a checkout of the old shape will
    keep arriving in new worktrees for as long as that commit is anyone's merge base. Reading it
    as one row is also exactly right: it WAS one seat's beat, and it keeps the existing legs of
    `state()` and `sweep()` measuring the same thing across the change rather than going quietly
    green on an unrecognised file.
    """
    if not isinstance(data.get("ts"), (int, float)):
        return {}
    return {SEATS: {_key(str(data.get("session_id") or ""), data.get("pid"), data.get("tree")): data}}


def _key(session_id: str, pid, tree) -> str:
    """The row's key. The session id when there is one, and never a collapsing default.

    An empty `session_id` is the degenerate case the hook can hand us (a payload without one),
    and keying every such seat on `""` would re-create the single-valued record this store
    replaces -- in the one case nobody would look at. pid-and-tree is not as good an identity as
    a session id, but it is an identity, and two anonymous seats stay two rows.
    """
    return session_id or f"pid-{pid}@{tree or ''}"


def _seats(store: dict) -> dict:
    seats = store.get(SEATS)
    return seats if isinstance(seats, dict) else {}


def note_activity(tool: str, *, session_id: str = "", pid: int | None = None,
                  path: Path | None = None, now: float | None = None,
                  staging_dir: Path | None = None) -> None:
    """Record that the seat just ran a tool. Called by the PreToolUse hook, never by the seat.

    Writes through a temp file and replaces, because this runs on EVERY tool call and a
    half-written heartbeat read by the 5-minute sweep would be a corrupt file that reads as
    ABSENT -- i.e. the recovery mechanism disabled by its own write pattern.

    ONE ROW PER SEAT, KEYED BY SESSION, AND THE ROW IS THE ONLY THING THIS TOUCHES. Every other
    seat's row is read and written back unchanged, so a beat is no longer an overwrite of the
    population by whichever seat moved last. That is what lets the shared-tree redirect be
    correct here -- `_resolve` carries the full argument, including the sweeper it refuses.

    THERE IS NO LONGER A HANDOFF FILED FROM THIS HOOK, and its removal is the keyed store paying
    for itself. The old code watched for "a different session arriving on a cold heartbeat" and
    filed for the predecessor before overwriting it, because the overwrite was about to destroy
    the only record of a seat the 5-minute sweep had not yet reached. Nothing is destroyed now:
    the predecessor's row is still there, on its own clock, for `sweep()` to find. Keeping the
    old leg as well would buy nothing and would spend `_uncommitted_paths`' `git status` on a
    tool call. The property it protected -- a dead seat's state survives a new session arriving --
    is the one the test asserts, rather than the mechanism that used to deliver it.

    THE GUARD IS ASKED ABOUT THE PATH THE CALLER NAMED, BEFORE THE REDIRECT MOVES IT, for the
    reason `launch_liveness.save` records: `guard_live_ledger_write` refuses on
    `is_live_record_path`, whose room is derived from THIS tree's `LIVE_RECORD_DIR`, and a path
    already redirected to the shared tree is outside that room. Resolving first and guarding
    second would hand a test process the real heartbeat with the guard still called, still
    passing, and permanently unreachable for exactly the callers the redirect applies to.
    """
    named = path or HEARTBEAT_FILE
    now = time.time() if now is None else now
    store = _read(named)
    seats = dict(_seats(store))
    pid = os.getpid() if pid is None else pid
    tree = str(PROJECT_DIR)
    key = _key(session_id, pid, tree)

    prev = seats.get(key) if isinstance(seats.get(key), dict) else {}
    tail = list(prev.get("recent_tools") or [])[-(TOOL_TAIL - 1):]
    tail.append({"tool": tool, "at": now})
    seats[key] = {
        "ts": now,
        "pid": pid,
        "session_id": session_id,
        # WHICH TREE THIS SEAT IS BEATING IN, and the handoff is wrong without it. The sweeper
        # may be running in a different tree from the seat it is filing for, and the work that
        # seat left behind is uncommitted in ITS tree -- so `_uncommitted_paths` and the last
        # commit are asked of this path, not of the sweeper's own `PROJECT_DIR`.
        "tree": tree,
        "tool_count": int(prev.get("tool_count", 0)) + 1,
        "recent_tools": tail,
    }
    try:
        guard_live_ledger_write(named, writer="seat_continuity.note_activity")
        _write(_prune(seats), path=named)
    except OSError:
        return  # a hook must never break the session it is observing


def _prune(seats: dict) -> dict:
    """Keep the store bounded, dropping the OLDEST beats first. See `MAX_SEATS`."""
    if len(seats) <= MAX_SEATS:
        return seats
    ordered = sorted(seats.items(), key=lambda kv: float(kv[1].get("ts") or 0), reverse=True)
    return dict(ordered[:MAX_SEATS])


def _write(seats: dict, *, path: Path | None = None) -> None:
    """Replace the store atomically.

    Through a temp file, because this runs on EVERY tool call and a half-written store read by
    the 5-minute sweep would be a corrupt file that reads as ABSENT -- i.e. the recovery
    mechanism disabled by its own write pattern.

    THE TEMP NAME CARRIES THE PID, which the single-tree version did not need. Concurrent seats
    used to write their own trees' files and could not collide; they now share one book, so a
    fixed `.tmp` name would have two seats writing one temp file and each replacing the other's
    half-written bytes -- an atomic-write idiom that is not atomic between writers. A lost beat
    is the cheap direction (the next tool call restamps it) but a torn read is not, and this is
    the write pattern that would produce one. Last writer still wins on the FILE, which is
    correct: each writer has just read the store and is putting back every other seat's row
    unchanged, so the loss is bounded to one beat of one row rather than the population.
    """
    p = _resolve(path, for_write=True)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps({SEATS: seats}, indent=2) + "\n", encoding="utf-8")
    tmp.replace(p)


def _any_interactive_seat() -> bool | None:
    """Is ANY interactive Claude session running? None when this machine cannot tell.

    DELIBERATELY NOT A PID MATCH, and the first draft's attempt at one is why. A hook runs as
    a CHILD of the session, so `os.getpid()` inside it is the hook's own pid and `getppid()`
    is whatever shell the harness spawned it through -- neither is the seat, and matching
    either against `interactive_claude_pids()` would have failed always, quietly, and in the
    direction that never declares death.

    The weaker question is enough because it is paired with silence. "No interactive session
    exists at all" plus "no tool has run in 20 minutes" is death. "Some session exists" is
    ambiguous -- it may be the same seat mid-call, or a NEW one that has not stamped yet --
    and ambiguity resolves to LIVE, because the expensive error here is two writers on one
    tree. The new-session case is caught at its own first tool call instead, in
    `note_activity`.

    None when /proc is unreadable: this machine cannot answer, and guessing would fork work.
    """
    try:
        from background.interactive_session_probe import interactive_claude_pids

        pids = interactive_claude_pids()
    except Exception:  # noqa: BLE001 - an unavailable probe is an unknown, not a verdict
        return None
    if pids:
        return True
    if not Path("/proc").is_dir():
        return None
    return False


def state(*, path: Path | None = None, now: float | None = None,
          session_id: str | None = None) -> str:
    """LIVE, DEAD or ABSENT. See the module docstring for why death needs two signals.

    TWO QUESTIONS NOW, AND ONLY ONE OF THEM IS THE POPULATION'S. With `session_id`, this is that
    seat's own verdict, which is what `sweep()` asks -- per row, so a live seat cannot hold a
    dead one's row warm. Without it, the answer is over the WHOLE population: LIVE if ANY seat is
    live, ABSENT if there are no rows at all, DEAD only when every row is dead.

    THE UNION IS CORRECT FOR THE CALLER THAT ASKS IT AND WOULD BE A FAIL-SILENT FOR THE OTHER,
    which is why they are different calls rather than one. `seat_executor._interactive_seat_is_live`
    asks "may an unattended delivery turn run in this tree", and the safe answer when ANY human
    seat is live is stand down -- so the union is the honest reading and a per-seat one would let
    an executor run beside a live seat in another tree. `sweep()` asks "did THIS seat die holding
    work", and the union there is exactly the survivor's answer the keyed store exists to end.
    """
    if session_id is None:
        seats = _seats(_read(path))
        if not seats:
            return ABSENT
        now = time.time() if now is None else now
        verdicts = [_verdict(rec, now) for rec in seats.values()]
        if LIVE in verdicts:
            return LIVE
        return DEAD if DEAD in verdicts else ABSENT
    rec = _seats(_read(path)).get(session_id) or {}
    now = time.time() if now is None else now
    return _verdict(rec, now)


def _verdict(rec: dict, now: float) -> str:
    """One seat's verdict from one row. The two-signal reasoning is the module docstring's."""
    ts = rec.get("ts")
    if not isinstance(ts, (int, float)):
        return ABSENT
    # suppression-lint: not-a-suppression silence -- this is an ELAPSED TIME in seconds since
    # the seat's last heartbeat, not a mechanism that quiets anything. It is the INPUT to a
    # liveness verdict that pages harder the larger it gets; nothing is folded, throttled or
    # held back on it, and no alarm is re-armed.
    silence = now - float(ts)
    if silence >= CERTAINLY_DEAD_SECONDS:
        return DEAD                      # the fail-silent escape; no corroboration needed
    if silence < SILENT_AFTER_SECONDS:
        return LIVE
    return DEAD if _any_interactive_seat() is False else LIVE


def _uncommitted_paths(tree: Path | str | None = None) -> list[str] | None:
    """SOURCE paths the seat left behind, IN THE TREE THAT SEAT WAS BEATING IN.

    `tree` defaults to this process's own `PROJECT_DIR` and is passed by `sweep()` from the
    dead seat's row. Asking the sweeper's own tree instead is the defect the keyed store would
    otherwise introduce: one book now means the shared tree's 5-minute sweep files handoffs for
    seats that died in linked worktrees, and their uncommitted work is in THEIR tree. A handoff
    listing the sweeper's dirty paths would be confidently, plausibly wrong -- it would name real
    files, held by somebody, just not by the seat the document is about.

    `None` when git could not be asked at all.

    THE MEASURED DEFECT, 2026-08-25. This was a bare `git status --porcelain`, and on this tree
    that answers 582 -- of which 397 are documents in `docs/staging/` and 84 are the daemons'
    own logs under `docs/observability/`, rewritten every minute by processes that have nothing
    to do with the seat. The handoff document therefore listed sixty log files, said "…and 499
    more", and directly above them said "Nothing was claimed."

    Two consequences, and the second is the expensive one. The document was useless: the 49
    real source files -- an entire uncommitted VAT-basis repair among them -- were buried in
    machine exhaust. And `_handoff_for`'s "died holding nothing, file nothing" guard became
    UNREACHABLE, because `docs/observability/` is never clean, so every dead seat filed,
    forever, whatever it had or had not been doing.

    IT IS ALSO A MIRROR, in this repo's own sense (CLASS_MEASUREMENTS_THAT_MIRROR): the handoff
    writes itself into `docs/staging/`, so the next handoff counted the previous handoff as work
    the seat left behind. The instrument was reading its own output back.

    REUSED, NOT REBUILT (AO2). `tree_divergence.changed_paths` already answers exactly this
    question -- "source files diverging from HEAD, generated artefacts and runtime state
    excluded" -- for the daily squatting report, with the same `GENERATED_PREFIXES` reasoning
    and the same `None`-not-`[]` failure contract. Duplicating that list here would have given
    this module a second, quietly diverging opinion about what counts as source.

    `docs/staging/` is dropped ON TOP of that, and only here: a staged document is already IN
    the tick's draw by the act of existing there, so naming it as unadopted work is telling the
    reader about the queue he is currently reading.
    """
    from background import tree_divergence

    root = Path(tree or PROJECT_DIR)
    if not root.is_dir():
        # The seat's tree is GONE -- a linked worktree removed since it died. That is not a
        # clean tree and must not read as one: whatever it was holding went with it, and the
        # reader needs to be told that rather than shown an empty list. Same direction as git
        # refusing to answer, and `handoff_document` already renders None as UNKNOWN.
        return None
    paths = tree_divergence.changed_paths(root)
    if paths is None:
        return None  # git could not answer; an unavailable check is not an empty tree (R15)
    return sorted(p for p in paths if not p.startswith("docs/staging/"))


#: How many top-level areas the subject names before it stops. `alarm_repetition._slug` keeps the
#: first TEN words of the normalised subject, and each area costs one word (two when it is a
#: dotted filename like `CLAUDE.md`, which normalise splits). Four leaves room for the rest of
#: the sentence and still tells two bodies of work apart.
SUBJECT_AREAS = 4

#: Directories, not loose files. A top-level file diverging (`CLAUDE.md`, `head.txt`) is almost
#: always another lane's edit rather than the shape of the seat's work, and letting each one
#: claim an area slot pushed the real directories out of the subject entirely -- measured: the
#: first draft's subject read "CLAUDE.md, PRIORITIES.md, _r11_tmp.mjs, background" and never
#: reached simulation or tests, where the actual orphaned repair was.
_LOOSE_FILE = "the tree root"


def _held_areas(uncommitted: list[str] | None) -> str:
    """The subject's discriminator: WHICH work is being held, in words that survive
    `alarm_repetition.normalise` AND fit inside `_slug`'s ten-word window.

    It has to be WORDS and it has to be EARLY. normalise() replaces every number with `#`, so a
    count cannot tell two documents apart; the path list is far too long for a filename; and
    anything past the tenth word never reaches the slug at all -- the first draft of this put
    the areas at the end of the sentence, and every seat death still produced one identical
    filename, which is the same bug in the opposite direction.

    Top-level areas are the right grain: stable when one file of a body of work gets committed
    (which should NOT re-file), different when the seat was holding something else entirely
    (which SHOULD).
    """
    if uncommitted is None:
        return "an unreadable tree"
    if not uncommitted:
        return "nothing"
    areas = sorted({p.split("/", 1)[0] if "/" in p else _LOOSE_FILE for p in uncommitted})
    named = ", ".join(areas[:SUBJECT_AREAS])
    return named + (" and elsewhere" if len(areas) > SUBJECT_AREAS else "")


def _last_commit(tree: Path | str | None = None) -> str:
    """The dead seat's tree's last commit -- a linked worktree is usually on a different one."""
    root = Path(tree or PROJECT_DIR)
    if not root.is_dir():
        return "(the seat's tree is gone)"
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%h %s"],
                             cwd=root, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return "(unreadable)"
    return out.stdout.strip() if out.returncode == 0 else "(unreadable)"


def handoff_document(rec: dict, claims: dict, uncommitted: list[str] | None, now: float) -> str:
    """The handoff, as markdown. Pure, so a test judges the same text a reader gets.

    `uncommitted` is None when git could not be asked. That is NOT rendered as a clean tree:
    the reader is told the tree could not be read and to look himself, because "the seat died
    and we cannot see what it left" is the one state where a silent empty list does real damage.
    """
    # suppression-lint: not-a-suppression silence_h -- the same elapsed time in HOURS, used
    # only to render the sentence a human reads ("ran no tool for 3.2h"). It is reported, not
    # acted on.
    silence_h = (now - float(rec.get("ts", now))) / 3600.0
    tree = rec.get("tree") or str(PROJECT_DIR)
    tools = ", ".join(t.get("tool", "?") for t in (rec.get("recent_tools") or [])) or "none recorded"
    claim_lines = "\n".join(
        f"- `{k}` — claimed {(now - float(v.get('claimed_at', now))) / 3600.0:.1f}h ago"
        + (f". The seat said: {v['note']}" if v.get("note") else "")
        + (f"\n  paths: {', '.join(v.get('paths') or []) or '(none declared)'}")
        for k, v in sorted(claims.items())
    ) or "- Nothing was claimed. Whatever it was doing, it did not say."
    if uncommitted is None:
        dirty = ("- **The tree could not be read** — `git status` failed here, so this list is\n"
                 "  UNKNOWN, not empty. Run `git status` yourself before concluding nothing was left.")
        more = ""
    else:
        dirty = "\n".join(f"- `{p}`" for p in uncommitted[:60]) or "- Nothing. The tree is clean."
        more = (f"\n…and {len(uncommitted) - 60} more.\n" if len(uncommitted) > 60 else "")

    return f"""**Severity:** LATENT · **Lane:** H_harness

# The interactive seat stopped mid-work, and this is what it was holding

**Filed automatically by `background/seat_continuity.py`, not by a person.** The seat ran no
tool for **{silence_h:.1f}h** and its process is gone. It did not stop on purpose: an
interactive session that finishes says so, and this one just stopped — which is the shape an
Anthropic API error leaves behind, four times now by the director's count.

This document exists so that nobody has to notice. It is a staged doc, so the next worker tick
draws it like any other work.

## What it had claimed

{claim_lines}

## What it left in the tree, uncommitted

**In `{tree}`** — which may not be the tree you are reading this in. Seats beat into one book
per machine, so the 5-minute sweep files for seats that died in linked worktrees too, and the
work below is uncommitted THERE. `cd` to it before you read a diff.

SOURCE paths only — the daemons' own output under `docs/observability/`, `site/` and the rest
of `tree_divergence.GENERATED_PREFIXES` is excluded, and so is `docs/staging/`, which is the
queue you are reading this from. This is the real state, and more reliable than anything the
session could have written about itself, because an API error is precisely the thing that
stops it writing.

{dirty}
{more}
## Where it had got to

- Last tools it ran, oldest first: {tools}
- Tool calls this session: {rec.get('tool_count', '?')}
- The seat's pid, now gone: `{rec.get('pid', '?')}`
- Last commit on that tree: `{_last_commit(tree)}`

## What to do with it — decide, do not just re-run

**Adopt** if the uncommitted paths above are coherent work part-way to something: read the
diff, finish it, commit it. That is the cheap outcome and the usual one.

**Discard** if the diff is a half-applied edit that no longer makes sense — `git checkout --`
the paths and take the claim from scratch. Say which you did.

Do NOT assume the work is wrong because the session died. The failure was in the transport,
not in the edit; the tree state above is exactly what a healthy session would have had at that
moment.

Archive to `docs/staging/done/` once the paths above are either committed or reverted.
"""


def sweep(*, path: Path | None = None, now: float | None = None,
          staging_dir: Path | None = None) -> str | None:
    """File a handoff for EVERY seat that has died, in whichever tree it died in.

    Returns the family document's path if anything was filed, else None — None when every seat
    is alive, absent, or died holding nothing, because a handoff for a clean tree with no claims
    would be noise and this module's whole purpose is to stop the director being the one who
    notices things.

    PER ROW, NEVER OVER THE POPULATION, and that is the whole repair. The old code asked
    `state()` for one verdict over one record: with two seats beating into one book, a live seat
    would answer LIVE for a dead one and its work would be orphaned in silence — the FAIL-SILENT
    that made the shared-tree redirect refusable before this store existed.

    A SWEPT ROW IS REMOVED, NOT THE FILE. The old `_clear()` unlinked the whole heartbeat, which
    on a keyed store would delete every LIVE seat's row as a side effect of one seat dying — and
    would leave no shared copy for `shared_tree_live_record` to find, splitting the book at the
    next beat from a linked worktree. Removal is also what bounds the store: a row exists from
    its seat's first tool call until its death is filed, and dead-holding-nothing removes the row
    without filing, so nothing accumulates on the quiet path either.
    """

    named = path or HEARTBEAT_FILE
    now = time.time() if now is None else now
    seats = dict(_seats(_read(named)))
    filed: str | None = None
    swept = False
    for key, rec in sorted(seats.items()):
        if not isinstance(rec, dict) or _verdict(rec, now) != DEAD:
            continue
        try:
            filed = _handoff_for(rec, now=now, staging_dir=staging_dir) or filed
        except Exception:  # noqa: BLE001 - one unfileable seat must not strand the others
            continue
        del seats[key]
        swept = True
    if swept:
        try:
            _write(seats, path=named)
        except OSError:
            pass
    return filed


def _handoff_for(rec: dict, *, now: float, staging_dir: Path | None = None) -> str | None:
    """File the handoff for one dead seat's row."""
    from background import alarm_repetition, seat_work_in_hand

    claims = seat_work_in_hand._load(seat_work_in_hand.CLAIMS_FILE)
    uncommitted = _uncommitted_paths(rec.get("tree"))
    if not claims and uncommitted == []:
        return None  # died holding nothing; a handoff here would be the noise this replaces
    # `uncommitted is None` falls THROUGH the guard on purpose: git could not be asked, so we do
    # not know that it held nothing, and for an alarm the safe failure is to file (R15).

    # ONE DOCUMENT PER UNADOPTED BODY OF WORK -- NOT ONE PER INTERRUPTION (2026-08-25).
    #
    # The subject used to carry the dead session's id, on the argument that "two interruptions
    # are not one condition recurring: each carries a DIFFERENT set of uncommitted paths, and
    # folding the second into the first would silently discard exactly the state this module
    # exists to preserve." That argument was sound about a real risk and false about this tree,
    # and it cost eighteen documents in nine hours -- SESSION_B_C_D_A_A_E, SESSION_F_E_EE_A_E,
    # SESSION_C_C_A and fifteen more, each 4.6KB, all of them listing the same daemon logs and
    # all of them saying "Nothing was claimed". They took the head of the tick's draw queue and
    # pushed three self-drawable mints to positions 43-46 of 48, where no bounded session ever
    # reached them. The machine's alarms had become the machine's workload.
    #
    # The path sets did not in fact differ: they were 99% `docs/observability/` churn, which is
    # the defect `_uncommitted_paths` above now fixes. Once the list is SOURCE only, two seats
    # dying over the same unadopted work are holding the same thing, and that IS one condition
    # -- it stays live until the work is adopted or reverted, which is precisely the semantics
    # `alarm_repetition`'s still-live append gives for free.
    #
    # THE OLD ARGUMENT IS STILL HONOURED, not overruled: a second interruption over DIFFERENT
    # work must still get its own document. It does, because the subject names the work rather
    # than the session -- the count of held source paths and the first of them by path order.
    # Same work, same subject, one document; different work, different subject, two.
    #
    # (The session id also could not de-duplicate even when it was wanted to. A UUID survived
    # `alarm_repetition.normalise` in fragments -- see the UUID rule added there the same day.)
    message = (
        f"[SEAT] {_held_areas(uncommitted)} left uncommitted by a session that stopped "
        f"mid-work holding {len(claims)} claim(s)"
    )
    filed = alarm_repetition.escalate(
        message,
        key="seat-continuity",
        repeats=1,
        first_ts=float(rec.get("ts", now)),
        staging_dir=staging_dir,
        now=now,
    )
    # ONE DOCUMENT, EVERY EPISODE'S PAYLOAD IN IT (2026-08-28, director: "ten of them the
    # identical finding").
    #
    # The two arguments above are BOTH right and the old code could only honour one at a time.
    # "Two deaths over the same unadopted work are one condition" is right, and so is "the
    # second death may be holding something else entirely, and folding it into the first would
    # discard exactly the state this module exists to preserve." The 2026-08-25 fix chose the
    # first by making the FILENAME carry the held areas — which meant a tree whose dirty set
    # moved by one directory filed another document, and nine of them were in the root on
    # 2026-08-28, all saying the same thing.
    #
    # Neither argument needs to lose. The identity is the CONDITION (one document, keyed on
    # `seat-continuity`), and the payload is the EPISODE (one section inside it, appended, never
    # overwritten). A reader gets one queue item and every dead seat's held state under it.
    #
    # Appending rather than overwriting is the half that makes the preservation real: the old
    # code wrote the handoff over `escalate()`'s body on the FIRST firing only, so every
    # subsequent death's tree state was lost even before the family rule.
    target = filed or alarm_repetition._live_finding_for(
        message, key="seat-continuity", staging_dir=staging_dir or alarm_repetition.STAGING_DIR)
    if target is None:
        return None
    try:
        _append_episode(target, handoff_document(rec, claims, uncommitted, now), now=now)
    except OSError:
        pass
    return str(target)


#: The heading under which each dead seat's held state is recorded, one section per episode.
EPISODES_HEADING = "## Episodes — what each dead seat was holding"


def _append_episode(path: Path, handoff: str, *, now: float) -> None:
    """Add one episode's handoff to the family document, keeping every earlier one.

    The handoff's own `**Severity:**` header and `# ` title are stripped: they belong to the
    document, and repeating them per episode would give one file four severity headers, which
    `finding_severity.parse_severity_file` reads the FIRST of. A document whose severity
    depends on which episode was appended last is a control keyed on an accident.
    """
    stamp = datetime.fromtimestamp(now, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = "\n".join(
        line for line in handoff.splitlines()
        if not line.startswith("**Severity:**") and not line.startswith("# ")
    ).strip()
    # Each episode's own sections demote by one level so they nest under the episode heading
    # rather than closing it — otherwise `## What it left in the tree` would end the Episodes
    # section and the next append would land outside it.
    body = re.sub(r"(?m)^## ", "#### ", body)
    section = f"### {stamp}\n\n{body}\n"
    text = path.read_text(encoding="utf-8", errors="replace")
    if EPISODES_HEADING not in text:
        text = text.rstrip() + f"\n\n{EPISODES_HEADING}\n"
    path.write_text(text.rstrip() + "\n\n" + section, encoding="utf-8")


def main() -> int:
    now = time.time()
    seats = _seats(_read())
    print(f"seat-continuity: {state(now=now)} over {len(seats)} seat(s)")
    for key, rec in sorted(seats.items(), key=lambda kv: -float(kv[1].get("ts") or 0)):
        age = (now - float(rec.get("ts") or 0)) / 60.0
        print(f"  {_verdict(rec, now):6} {key[:8]:8} pid {rec.get('pid', '?'):<8} "
              f"{age:6.1f} min ago  {rec.get('tree', '?')}")
    # SWEEP UNCONDITIONALLY, because the verdict above is the POPULATION's and the sweep is per
    # row. Gating it on `state() == DEAD`, as this used to, would mean one live seat suppressed
    # the handoff for a dead one -- the survivor's answer, in the one place it files nothing.
    filed = sweep(now=now)
    print(f"  handoff: {filed or 'nothing to hand over'}")
    return 0


if __name__ == "__main__":
    # SEAT GUARD, first non-import statement (2026-08-27). A daemon started from a
    # foreign seat writes this tree while the real seat is also writing it; the guard
    # refuses instead. Structural rule, enforced by
    # tests/background/test_seat_guard_daemons.py::TestStructuralLock.
    from background._seat import refuse_if_foreign

    refuse_if_foreign("seat_continuity")
    raise SystemExit(main())
