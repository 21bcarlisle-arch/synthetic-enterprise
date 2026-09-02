#!/usr/bin/env python3
"""docs/staging/ is a QUEUE, and only work belongs in a queue.

REUSE: background/staging_rooms.py
CLASS: CUSTOM
INDEX: searched "staging", "room", "queue", "priority", "order", "classif", "taxonomy",
       "archive", "disposition".
       `background/staging_archive_policy.py` already draws the RECORD-vs-EXHAUST line and is
       the nearest analogue — but it draws it in `done/`, over files that have already left
       the queue, and its question is "what may be moved out of the way of a reader". This
       module's question is the other one: of the files that have NOT left, which are work,
       and in what order. They are deliberately separate because the archive policy's
       fail-safe direction is "when in doubt it is a RECORD, keep it visible", and a queue's
       fail-safe direction is the opposite one, "when in doubt it is WORK, draw it".
       `background/finding_severity.py` owns the `**Severity:** · **Lane:**` header and its
       `header_block()`/`LANES` are IMPORTED here rather than re-implemented, so the chain
       header below is an extension of that one header and not a second one.
       `background/finding_classes.py` classifies a finding by its SUBJECT (which family of
       defect); this classifies by its KIND (which channel it arrived on). Both are needed and
       neither answers the other's question.
       `background/staging_disposition.py` decides whether a PARKED item in `in_progress/` is
       really blocked. It is called by the same draw and left alone.

THE STATE THIS WAS BUILT AGAINST (director, 2026-08-28, measured by him by reading all 49):

    "The draw takes files in alphabetical filename order, and that is the least of it. I read
    all 49. Only about eleven are work. Thirty-four are repeating-alarm files... Four are
    director console transcripts — 163KB of archive. Six are the CLASS registers, which are
    reference and should never drain. Four are real findings. Four different kinds of thing
    share one folder and only one is work. And not one file carries a lane, an epoch or an
    atom id, so the queue is disconnected from the map entirely."

FOUR DEFECTS, EACH WITH ITS OWN REMEDY IN THIS MODULE.

D1 — NO PRIORITY. `supervisor._real_staged_instructions()` returns `sorted(names)` and
`find_work()` renders the whole list into one comma-joined prose reason. Alphabetical order
is not a queue discipline, it is an accident of naming, and here the accident is systematic:
`CLASS_` < `DIRECTOR_` < `WORKER_`, so the six documents that must NEVER drain sort ahead of
the director's guidance, and the guidance sorts ahead of every finding. `ORDER` below is an
explicit rank, and within a rank the tie-break is AGE, because that is what a queue is.

D2 — REFERENCE AND ARCHIVE ARE IN THE WORK CHANNEL. A CLASS register is a standing reference
document: it is *supposed* to sit there forever. A console transcript is an archived record of
a conversation that already happened. Neither can ever be actioned and archived, so while they
are in the root the root can never be empty — and a queue that cannot reach zero cannot signal
"drained". That is how this one reached 49 without anything noticing. They move to
`reference/` and `console/`, which are ROOMS OF THE SAME FOLDER, not deletions.

D3 — ONE DOCUMENT PER FIRING. Handled in `background/alarm_repetition.py`, not here; this
module only has to know that `WORKER_FINDING_REPEATING_ALARM_` is a KIND with its own rank.

D4 — NO LANE, NO EPOCH, NO ATOM. The director's P8: "no systematic link from knowledge to
discovery to atoms to epochs... the queue is disconnected from the map entirely". `chain_of()`
parses that link off the document's own header and `unchained()` counts the items that carry
none. The number that control prints is P8 measured, on the one surface where the disconnect
is visible without an argument.

WHY A ROOM AND NOT A DELETION, AND WHY A READER THAT SPANS ROOMS.
Every file this module relocates stays inside `docs/staging/` and stays committed. That is not
timidity: this project has twice found a control go QUIET rather than loud when the structure
it was keyed to moved (`docs/design/maturity_map.yaml` splitting in two; six readers kept
reading one half and kept passing). Moving files between folders is exactly that hazard. So
every accessor here is a SPANNING reader — `class_document_path()` looks in the room and then
in the root, `work_queue()` names every room it read — and `population_floor_violations()`
exists so that a room emptying underneath a scanner is LOUD.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from background.finding_severity import LANES, header_block

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STAGING_ROOT = REPO_ROOT / "docs" / "staging"

#: The room a standing reference document lives in. A CLASS register is the machine's own
#: index of a family of defects; it is re-rendered in place and never archived, so it is the
#: one kind of staging document for which "still here tomorrow" is correct rather than a
#: symptom.
REFERENCE_DIRNAME = "reference"

#: The room a verbatim director console transcript lives in. It is a RECORD of an exchange
#: that has already been acted on — the acting is what produced the rest of the queue — and at
#: 25-51KB apiece it is the largest thing in the folder and the least drawable.
CONSOLE_DIRNAME = "console"

#: Rooms that exist already and are not this module's to redesign. Named so that
#: `work_queue()` can state what it did NOT read, which is the half of a scan that usually
#: goes unsaid.
PARKED_DIRNAME = "in_progress"
ARCHIVE_DIRNAME = "done"
EXHAUST_DIRNAME = "exhaust"
FYI_DIRNAME = "fyi"

# ---------------------------------------------------------------------------
# KINDS
# ---------------------------------------------------------------------------

#: A standing register. Reference by default — see `KIND_CLASS_DEBT` for the one condition
#: under which a register is work, and why that is not a reversal of D2 below.
KIND_REFERENCE = "reference"
#: A class register that is STILL ACCRUING INSTANCES and carries no recorded decision.
#:
#: D2 below is right that a standing register cannot be a queue item: it is re-rendered in
#: place and never actioned-and-archived, so while every register sat in the work channel the
#: root could never reach zero. That argument turns entirely on a register having NO EXIT.
#: `background/class_debt.py` gives it one — a `## Disposition` section recording a decision
#: about the class (accepted with its cost showing, or closed by a named mechanism). A
#: register with a current decision is reference and is dropped here exactly as before; a
#: register nobody has decided anything about, that produced two or more instances this week,
#: is work. It drains by being DECIDED, never by being consumed, so the root can still reach
#: zero. (Director, 2026-09-01: "cumulative cost should rank a class against other work in the
#: draw ... that makes it a decision rather than a rule, which is what stops it becoming
#: bureaucracy".)
KIND_CLASS_DEBT = "class_debt"
#: The HEAD-RED register, when tests are red at HEAD that nobody has fixed or accepted by name.
#:
#: Director, 2026-09-02: *"the HEAD-green census reports and nothing draws it. Twelve, seventeen,
#: thirty-three and now 830 — each announced, none worked, while everything with a route into the
#: draw gets done."* That is the same argument `KIND_CLASS_DEBT` above answers for a finding class,
#: and it wants the same answer: a register with a NAMED SUBJECT and an EXIT.
#:
#: Ranked BELOW class debt and ABOVE a finding, deliberately. A class register is an argument about
#: a pattern that is still producing instances; this is a list of things that are broken right now
#: at committed HEAD, which is narrower and more certain but also, for any single red, smaller. It
#: beats a finding because a finding describes something that might be wrong and this is something
#: that IS.
KIND_HEAD_RED = "head_red"
#: An archived verbatim transcript. Record, never work.
KIND_CONSOLE = "console"
#: The pipeline's own coordination markers. These self-process on the daemon's cadence and
#: have never needed a granted turn (supervisor's `_is_daemon_marker`, 2026-07-12).
KIND_DOORBELL = "doorbell"
#: An inbound message from the director, routed by `background/dispatcher.py`.
KIND_FROM_RICH = "from_rich"
#: A repeating alarm that escalated itself into the draw (`background/alarm_repetition.py`).
#: WORK — but machine-authored work about the machine, which ranks below a person's ask.
KIND_ALARM = "alarm"
#: Anything a human staged: director guidance, rulings, steers, advisor input.
KIND_DIRECTIVE = "directive"
#: A finding a worker turn wrote about the system.
KIND_FINDING = "finding"
#: A minted work batch awaiting consumption.
KIND_MINT = "mint"
#: Kind could not be determined. Fail-safe: an unrecognised file is WORK, and it is drawn
#: ahead of the alarms, because the harmful misclassification here is a real ask filed as
#: noise. (`staging_archive_policy` fails the other way for the opposite reason: it MOVES
#: files, and this only ORDERS them.)
KIND_UNKNOWN = "unknown"

#: Rank in the draw. Lower is served first. This is the whole of D1.
#:
#: The order is an argument, not a preference:
#:   1 from_rich   — the director is talking to the machine RIGHT NOW.
#:   2 directive   — a person staged an instruction and has not seen it actioned.
#:   3 mint        — a minted batch is work already decomposed; consuming it beats minting more
#:                   (supervisor RUNG 1 already gates RUNG 7 on exactly this).
#:   4 finding     — a worker turn found something real about the system.
#:   5 unknown     — unrecognised, so treated as a real ask until shown otherwise.
#:   60 alarm      — the machine complaining about the machine. Real work, and it must never
#:                   outrank a human's ask again: on 2026-08-25 eighteen copies of ONE alarm
#:                   took the head of the draw and pushed three self-drawable mints to
#:                   positions 43-46 of 48, where no bounded session ever reached them.
#:   - doorbell/reference/console are absent: they are not work and `work_queue()` drops them.
#:
#: 35 class_debt — an accruing class register, BETWEEN mint and finding. The argument is the
#:                 ruling's own: "a class with a live instance list is the artefact that can
#:                 win a draw; twenty siblings filed separately cannot." An individual finding
#:                 is one instance of something; an accruing class is what GENERATES such
#:                 findings, so closing the generator dominates repairing one instance. Below
#:                 a person's ask and below an already-decomposed mint, because neither of
#:                 those is competing with the class — they are the work the class is taxing.
#:
#: SPACED BY TENS so a band can be inserted between two existing ones without renumbering
#: every consumer. Only the ORDER of these values has ever been load-bearing; the tests assert
#: relative rank and never an absolute number.
ORDER: dict[str, int] = {
    KIND_FROM_RICH: 10,
    KIND_DIRECTIVE: 20,
    KIND_MINT: 30,
    KIND_CLASS_DEBT: 35,
    KIND_HEAD_RED: 37,
    KIND_FINDING: 40,
    KIND_UNKNOWN: 50,
    KIND_ALARM: 60,
}

#: Kinds that are not work at all. `work_queue()` returns nothing of these kinds no matter
#: which room the file is sitting in, so a CLASS register that has not yet been moved is
#: already out of the queue — the classification does the work, the move only makes it
#: legible to a reader.
NOT_WORK = frozenset({KIND_REFERENCE, KIND_CONSOLE, KIND_DOORBELL})

_ALARM_PREFIX = "WORKER_FINDING_REPEATING_ALARM_"
_CLASS_PREFIX = "CLASS_"
#: Standing registers whose names do not carry a family prefix. One entry, and it is here
#: rather than given a `HEAD_` prefix because `HEAD_RED_REGISTER` is a singleton: a prefix
#: implies a family and would invite a second one to be created rather than a row added.
_STANDING_REGISTERS = frozenset({"HEAD_RED_REGISTER.md"})
_CONSOLE_PREFIX = "DIRECTOR_CONSOLE_"
_MINT_PREFIX = "PLANNER_MINTED_"
_FROM_RICH_PREFIX = "from_rich_"
_DOORBELL_PREFIXES = ("run_complete_", "run_pending_")
_DIRECTIVE_PREFIXES = ("DIRECTOR_", "ADVISOR_", "BOARD_")
_FINDING_PREFIXES = ("WORKER_FINDING_", "WORKER_ALARM_")


def kind_of(name: str) -> str:
    """The KIND of a staging document, from its name alone.

    From the NAME and not the contents, deliberately. Every consumer of this — the draw, the
    population floor, the migration — has to be able to answer "what is this" for a file it
    cannot read (a permissions error, a half-written file, a file that has just been moved).
    A kind that depended on the body would become UNKNOWN exactly when the disk misbehaves,
    and UNKNOWN ranks as work, so an unreadable folder would flood the draw.

    Order of the tests matters in one place and one only: `DIRECTOR_CONSOLE_` must be tested
    before `DIRECTOR_`, or every transcript classifies as a live directive. That is not a
    hypothetical — it is the state the director found, two 25-51KB transcripts sitting in the
    work channel because their name begins with the same eight letters as a ruling's.
    """
    if name.startswith(_CONSOLE_PREFIX):
        return KIND_CONSOLE
    if name.startswith(_CLASS_PREFIX) or name in _STANDING_REGISTERS:
        # REFERENCE BY NAME, PROMOTED BY STATE — the same two-step a class register takes. The
        # name says "this is a standing document that lives in reference/ and is never archived";
        # whether it is WORK right now is a question about its CONTENT, answered by the splices in
        # `work_queue`. Keeping the room decision here and the rank decision there is what stops a
        # register migrating between folders as its state changes.
        return KIND_REFERENCE
    if name.startswith(_DOORBELL_PREFIXES):
        return KIND_DOORBELL
    if name.startswith(_FROM_RICH_PREFIX):
        return KIND_FROM_RICH
    if name.startswith(_ALARM_PREFIX):
        return KIND_ALARM
    if name.startswith(_MINT_PREFIX):
        return KIND_MINT
    if name.startswith(_DIRECTIVE_PREFIXES):
        return KIND_DIRECTIVE
    if name.startswith(_FINDING_PREFIXES):
        return KIND_FINDING
    return KIND_UNKNOWN


def room_for(kind: str) -> str | None:
    """The room a kind belongs in, relative to the staging root, or None for the root itself."""
    if kind in (KIND_REFERENCE, KIND_CLASS_DEBT, KIND_HEAD_RED):
        # A DRAWN REGISTER IS STILL A REGISTER. `KIND_CLASS_DEBT` is the same document as
        # `KIND_REFERENCE` promoted for one reason (it is accruing and undecided), so its ROOM
        # must not change with its rank — a register that migrated to the root because it became
        # work would be moved back the moment it was decided, and a document that moves rooms on
        # a schedule is how `class_document_path` came to have to span both.
        return REFERENCE_DIRNAME
    if kind == KIND_CONSOLE:
        return CONSOLE_DIRNAME
    return None


# ---------------------------------------------------------------------------
# THE CHAIN — lane, epoch, atom (D4 / the director's P8)
# ---------------------------------------------------------------------------

#: Extends the header `background/finding_severity.py` already owns and parses:
#:     **Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** H41_map_ratchet
#: One header, four fields, one place a reader looks. A second header block would be a second
#: thing to keep in sync, and this project's own decay audit says that is how a field goes
#: stale without anyone being able to point at when.
_EPOCH_RE = re.compile(r"\*\*Epoch:?\*\*:?\s*`?(?P<value>[0-9]+|unassigned)`?", re.I)
_ATOM_RE = re.compile(r"\*\*Atom:?\*\*:?\s*`?(?P<value>[A-Za-z0-9_.\-]+)`?")
_LANE_RE = re.compile(r"\*\*Lane:?\*\*:?\s*`?(?P<value>[A-Za-z0-9_]+)`?")

#: The value that says "this item has been looked at and has no atom yet", as against a field
#: that is simply absent. The distinction is the whole point of having the field: an ABSENT
#: atom means nobody has connected this item to the map, and an EXPLICIT `unminted` means
#: somebody did and the answer was "not yet". Only the first is a defect, and a control that
#: could not tell them apart would either nag forever or go quiet.
UNMINTED = "unminted"


#: An epoch field a writer filled in with "nobody has decided yet". Same argument as
#: `UNMINTED`: the difference between a field nobody filled in and a field somebody filled in
#: with "not yet" is the whole reason to have the field.
UNASSIGNED = "unassigned"


@dataclass(frozen=True)
class Chain:
    """A staging item's link into the maturity map. Any field may be None — absent is a
    reportable state, never a guessed one."""

    path: Path
    lane: str | None
    epoch: int | None
    atom: str | None
    #: True when an `**Epoch:**` field was PRESENT, including `unassigned`. `epoch` stays None
    #: for `unassigned` because there is no number to report, and a caller that treated the
    #: absence of a number as the absence of a decision would nag at every item for ever.
    epoch_declared: bool = False

    @property
    def is_chained(self) -> bool:
        """A lane AND an epoch decision AND an atom decision.

        `unminted`/`unassigned` COUNT. What the director's P8 asks for is the CONNECTION —
        "no systematic link from knowledge to discovery to atoms to epochs" — and a document
        that says "H_harness, epoch unassigned, no atom yet" is connected: somebody read it
        against the map and recorded the answer. A control that demanded a real atom id on
        every queue item would be demanding that every alarm be minted before it is triaged,
        which is a different and much worse rule.
        """
        return bool(self.lane) and self.epoch_declared and bool(self.atom)

    @property
    def is_minted(self) -> bool:
        """Chained to a REAL atom, not to `unminted`. This is the number that should fall as
        the queue is worked; `is_chained` is the number that should be 100%."""
        return self.is_chained and self.atom != UNMINTED

    @property
    def missing(self) -> tuple[str, ...]:
        gaps = []
        if not self.lane:
            gaps.append("lane")
        if not self.epoch_declared:
            gaps.append("epoch")
        if not self.atom:
            gaps.append("atom")
        return tuple(gaps)


def chain_of(path: Path) -> Chain:
    """Parse the chain header off one document. Never raises."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        # UNREADABLE IS NOT UNCHAINED. Reporting a file we could not open as "missing its
        # lane" is a claim about its contents made without reading them, and this project
        # found three controls in one day that refused on input they could not READ. All
        # three fields come back None with `is_chained` False, which is honest, and the
        # caller that cares (`unchained`) skips unreadable files explicitly.
        return Chain(path, None, None, None)
    return chain_of_text(text, path=path)


def chain_of_text(text: str, *, path: Path | None = None) -> Chain:
    block = header_block(text)
    lane_m = _LANE_RE.search(block)
    lane = lane_m.group("value").strip() if lane_m else None
    if lane is not None and lane not in LANES:
        lane = None  # a lane that is not a lane is not a lane
    epoch_m = _EPOCH_RE.search(block)
    epoch: int | None = None
    if epoch_m:
        raw = epoch_m.group("value").strip().lower()
        if raw != UNASSIGNED:
            try:
                epoch = int(raw)
            except ValueError:
                epoch = None
    atom_m = _ATOM_RE.search(block)
    atom = atom_m.group("value").strip() if atom_m else None
    return Chain(path or Path("<text>"), lane, epoch, atom, epoch_declared=epoch_m is not None)


def stamp_chain(text: str, *, lane: str, epoch: int | str, atom: str,
                severity: str = "LATENT") -> str:
    """Return `text` with a chain header, adding or completing the one header line.

    IDEMPOTENT and NON-DESTRUCTIVE: an existing `**Severity:** … · **Lane:** …` line is
    EXTENDED with the fields it lacks rather than replaced, so the severity a human set and
    the lane a class guard already trusts are never silently overwritten by a default.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines[:4]):
        if "**Severity:**" in line or "**Lane:**" in line:
            parts = [line.rstrip()]
            if "**Epoch:**" not in line:
                parts.append(f"**Epoch:** {epoch}")
            if "**Atom:**" not in line:
                parts.append(f"**Atom:** `{atom}`")
            if "**Lane:**" not in line:
                parts.insert(1, f"**Lane:** {lane}")
            lines[i] = " · ".join(parts)
            return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    header = (f"**Severity:** {severity} · **Lane:** {lane} · "
              f"**Epoch:** {epoch} · **Atom:** `{atom}`\n")
    return header + "\n" + text.lstrip("\n")


# ---------------------------------------------------------------------------
# THE QUEUE
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QueueItem:
    path: Path
    kind: str
    rank: int
    mtime: float

    @property
    def name(self) -> str:
        return self.path.name


def work_queue(root: Path | str = DEFAULT_STAGING_ROOT) -> list[QueueItem]:
    """Every drawable item in the staging root, in the order it should be served.

    SPANS THE ROOT ONLY, on purpose. `in_progress/` has its own three re-surfacing nets in
    `background/staging_disposition.py` that the same draw already calls, and duplicating
    that reasoning here would make two answers to one question. `reference/` and `console/`
    are excluded because nothing in them is ever work. `done/`, `exhaust/`, `fyi/` are
    exhausted, archived and informational respectively.

    Sorted by (rank, mtime, name): the KIND decides the band, AGE decides within it, and the
    name only ever breaks a tie between two files of the same kind written in the same second
    — which is the only job a filename ever had here.

    THE ONE EXCEPTION IS THE CLASS REGISTERS, and it is why `mtime` is not the within-band
    tie-break for them. `kind_of` answers from the NAME alone and must keep doing so (see its
    docstring: every consumer has to be able to classify a file it cannot read). Whether a
    register is work depends on its ACCRUAL and its DISPOSITION, which are properties of the
    corpus and not of the filename, so the promotion is made here — the one place that is
    already reading the filesystem. A register's mtime is when it was last re-rendered, which
    is meaningless as a queue age, so `class_debt` supplies the within-band order instead.
    """
    root = Path(root)
    if not root.is_dir():
        return []
    items: list[QueueItem] = []
    for p in root.iterdir():
        if not p.is_file() or p.suffix != ".md":
            continue
        kind = kind_of(p.name)
        if kind in NOT_WORK:
            continue
        try:
            mtime = p.stat().st_mtime
        except OSError:
            mtime = 0.0
        items.append(QueueItem(p, kind, ORDER.get(kind, ORDER[KIND_UNKNOWN]), mtime))
    items.sort(key=lambda i: (i.rank, i.mtime, i.path.name))
    return _with_the_head_red_register(root, _with_accruing_class_registers(root, items))


def _with_accruing_class_registers(root: Path, items: list[QueueItem]) -> list[QueueItem]:
    """Splice the drawable class registers into the queue at rank 35.

    FAIL-OPEN, deliberately, and it is the same call `supervisor._unprocessed_staging_files`
    already makes about this module: a draw that cannot rank its work must still SEE it. If
    `class_debt` cannot be imported or cannot read the corpus, the queue is exactly what it
    was before this function existed — the findings, mints and asks are all still there and
    still in order. What is lost is a promotion, which is a degradation; what would be lost by
    raising is the whole queue, which is a stall.

    The within-band order comes from `class_debt.drawable()`, which returns the registers
    already sorted, so `enumerate` preserves it through the outer sort by giving each a
    distinct increasing sub-key in the `mtime` slot.
    """
    try:
        from background import class_debt
        debts = class_debt.drawable(root)
    except Exception:
        return items
    if not debts:
        return items
    rank = ORDER[KIND_CLASS_DEBT]
    promoted = [
        QueueItem(
            class_document_path(debt.finding_class.document_name, root),
            KIND_CLASS_DEBT,
            rank,
            float(position),
        )
        for position, debt in enumerate(debts)
    ]
    merged = items + promoted
    merged.sort(key=lambda i: (i.rank, i.mtime, i.path.name))
    return merged


def _with_the_head_red_register(root: Path, items: list[QueueItem]) -> list[QueueItem]:
    """Splice the HEAD-red register into the queue at rank 37 when anything is owed.

    FAIL-OPEN for the same reason as its sibling above: a draw that cannot rank one register must
    still see every finding, mint and ask. What is lost by returning early is a promotion; what
    would be lost by raising is the whole queue.

    It is spliced only when `drawable()` is non-empty, so a green HEAD does not park a permanent
    item in the draw. **That is the "zero means zero" property, enforced here rather than
    promised in the document** — the register stops being work by there being nothing owed.
    """
    try:
        from background import head_red_register
        if not head_red_register.drawable(root):
            return items
        path = Path(root) / REFERENCE_DIRNAME / head_red_register.REGISTER_NAME
        if not path.is_file():
            return items
    except Exception:
        return items
    merged = items + [QueueItem(path, KIND_HEAD_RED, ORDER[KIND_HEAD_RED], 0.0)]
    merged.sort(key=lambda i: (i.rank, i.mtime, i.path.name))
    return merged


def queue_census(root: Path | str = DEFAULT_STAGING_ROOT) -> dict[str, int]:
    """How many files of each KIND are sitting in the staging ROOT — including the kinds that
    are not work, because "six reference documents are still in the queue folder" is exactly
    the fact this census exists to make visible."""
    root = Path(root)
    census: dict[str, int] = {}
    if not root.is_dir():
        return census
    for p in root.iterdir():
        if p.is_file() and p.suffix == ".md":
            k = kind_of(p.name)
            census[k] = census.get(k, 0) + 1
    return census


def unchained(root: Path | str = DEFAULT_STAGING_ROOT) -> list[Chain]:
    """Drawable items carrying no link to the map. P8, counted.

    Unreadable files are EXCLUDED, not reported: a file we could not open has not been shown
    to be missing anything.
    """
    out: list[Chain] = []
    for item in work_queue(root):
        try:
            item.path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        chain = chain_of(item.path)
        if not chain.is_chained:
            out.append(chain)
    return out


# ---------------------------------------------------------------------------
# SPANNING READS — a room must never be able to hide a document
# ---------------------------------------------------------------------------


def class_document_path(name: str, root: Path | str = DEFAULT_STAGING_ROOT) -> Path:
    """Where a CLASS register lives — the reference room if it is there, else the root.

    THE FALLBACK IS THE POINT, and it is not defensive coding. Moving a file is how a control
    goes quiet: it keeps reading the old location, finds nothing, and reports nothing wrong.
    Every reader of a class document goes through here, so a register in either room is found
    by all of them, and the migration cannot half-happen. The RETURN for a document that is in
    neither is the reference room — the place it should be — so a writer creating a fresh one
    puts it in the right room without needing to know that.
    """
    root = Path(root)
    in_room = root / REFERENCE_DIRNAME / name
    if in_room.exists():
        return in_room
    in_root = root / name
    if in_root.exists():
        return in_root
    return in_room


def reference_documents(root: Path | str = DEFAULT_STAGING_ROOT) -> list[Path]:
    """Every CLASS register, wherever it currently sits. Deduplicated by NAME with the room
    winning, so a half-finished move reads as one document and not two."""
    root = Path(root)
    found: dict[str, Path] = {}
    for p in sorted(root.glob(f"{_CLASS_PREFIX}*.md")):
        found[p.name] = p
    room = root / REFERENCE_DIRNAME
    if room.is_dir():
        for p in sorted(room.glob(f"{_CLASS_PREFIX}*.md")):
            found[p.name] = p
    return [found[k] for k in sorted(found)]


# ---------------------------------------------------------------------------
# POPULATION FLOORS — a room that empties must be LOUD
# ---------------------------------------------------------------------------

#: The floor under each room, dated, as the delivery seat's own standing rule requires: a
#: scanning control without one reports "nothing found" identically whether the subject is
#: clean or gone. Five emptied subjects were found in one day by floors of exactly this shape.
#:
#: `reference` — six CLASS registers existed on 2026-08-28 and a register is never deleted,
#: so this can only rise. A drop means a register was lost or the room moved.
#: `console`   — the two transcripts migrated on 2026-08-28. Same argument.
POPULATION_FLOORS: dict[str, int] = {
    REFERENCE_DIRNAME: 6,
    CONSOLE_DIRNAME: 2,
}


def population_floor_violations(root: Path | str = DEFAULT_STAGING_ROOT) -> list[str]:
    """Rooms holding fewer documents than they held when the floor was set."""
    root = Path(root)
    out: list[str] = []
    for dirname, floor in sorted(POPULATION_FLOORS.items()):
        room = root / dirname
        if not room.is_dir():
            out.append(
                f"ROOM MISSING {dirname}/: floor is {floor} document(s) and the room does not "
                f"exist. Either the migration was reverted or the room was renamed; either way "
                f"every reader keyed to it is now finding nothing and saying nothing."
            )
            continue
        n = sum(1 for p in room.iterdir() if p.is_file() and p.suffix == ".md")
        if n < floor:
            out.append(
                f"POPULATION FLOOR {dirname}/: {n} document(s), floor {floor}. A room that "
                f"loses documents silently is the failure this floor exists to make loud."
            )
    return out


# ---------------------------------------------------------------------------
# REPORT
# ---------------------------------------------------------------------------


def render(root: Path | str = DEFAULT_STAGING_ROOT) -> str:
    root = Path(root)
    lines = ["STAGING ROOMS", "=" * 60, ""]
    census = queue_census(root)
    lines.append("Staging ROOT by kind:")
    for kind in sorted(census):
        mark = "  (not work)" if kind in NOT_WORK else ""
        lines.append(f"  {kind:<12} {census[kind]:>3}{mark}")
    lines.append("")
    queue = work_queue(root)
    lines.append(f"Work queue: {len(queue)} item(s), in draw order")
    for i, item in enumerate(queue, 1):
        lines.append(f"  {i:>3}. [{item.kind}] {item.name}")
    lines.append("")
    gaps = unchained(root)
    minted = sum(1 for i in queue if chain_of(i.path).is_minted)
    lines.append(f"Unchained work items (P8): {len(gaps)} of {len(queue)}")
    for chain in gaps:
        lines.append(f"  - {chain.path.name}: missing {', '.join(chain.missing)}")
    lines.append("")
    lines.append(f"Chained to a REAL atom: {minted} of {len(queue)} "
                 f"(the rest say `{UNMINTED}` — triaged, not yet minted)")
    lines.append("")
    violations = population_floor_violations(root)
    lines.append(f"Population floors: {len(violations)} violation(s)")
    for v in violations:
        lines.append(f"  ! {v}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(DEFAULT_STAGING_ROOT))
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero on a population-floor violation")
    args = parser.parse_args(argv)
    print(render(args.root))
    if args.check and population_floor_violations(args.root):
        return 1
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/staging_rooms.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("staging_rooms")
    raise SystemExit(main())
