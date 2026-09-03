"""Class consolidation for staging findings — atom `OPS10_finding_class_consolidation`.

WHY THIS EXISTS (DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12, clause 1):
"Where findings share a class, they become one class document with an instance list and a
cumulative cost line, superseding the individuals (archived, not deleted). A class with a
live instance list is the artefact that can win a draw; twenty siblings filed separately
cannot."

The first five families are the DIRECTOR'S measurement, named in the ruling and not
re-derived here: publish-gate/wedge (~18), controls that cannot fail (~9), measurements that
mirror the thing they measure (~7), uncommitted/orphaned work (~7), no-caller/never-runs (~5).
`ruling_count` on each class records what he measured so that this module's own count can
be COMPARED with it rather than quietly replacing it.

A SIXTH CLASS WAS REGISTERED 2026-08-28 — `figures_on_a_superseded_clock` — and it is NOT
his. R10 requires that the second instance of a shape register the class rather than fix the
second file, so a class registered later is a normal outcome of that rule and not an
irregularity. It is kept honest by `provenance`: the ruling's five cite the ruling, and this
one cites the finding that named it, so a self-registered class cannot borrow the ruling's
authority merely by sharing the renderer.

WHY MEMBERSHIP IS DERIVED, never a hand-kept list (exit criterion 3): a list written once
stops being true the moment a sixteenth sibling is filed, and stops SILENTLY — the class
document keeps saying fifteen and nobody learns that the family grew. `check()` re-derives
membership from the filesystem every time it runs and names any live finding that belongs
to a class but is not in that class's instance list.

THE SUBJECT IS THE FILENAME AND THE TITLE, not the whole body. Every finding in this
project is named for the thing it found — `WORKER_FINDING_THE_WEDGE_ALARM_IS_DISARMED_BY_
RUNS_THAT_PUBLISH_NOTHING` — so the title IS the project's own one-line statement of the
document's subject. Matching the body instead would put every document that merely
MENTIONS the publish gate into the publish-gate class, which is how a classifier stops
partitioning anything.

...WITH ONE OVERRIDE: a document may REGISTER itself (`declared_class_of`, see the comment
block above it). Title-only is fail-open for a finding titled after its mechanism rather
than its family — it classifies as None, nothing is refused, nothing goes red, and the
class document never learns the family grew. That is the routing half of the same silence
this module was built to end, and it was measured on this module's own population.

AT MOST ONE CLASS (exit criterion 3). Families overlap in the real world: a test that is
unreachable by the gate's selector is both a gate defect and a never-runs defect. The
CLASSES tuple is therefore a declared PRECEDENCE, first match wins, and every other match
is recorded on the classification as `also_matched` and printed by `--list`. A contested
document is visible, never silently filed twice.

THE LANE GUARD, and why consolidation is dangerous without it: severity is lane-scoped
(OPS9/OPS11 — a BLOCKING finding refuses level-raises in ITS OWN lane). Consolidating a
BLOCKING `D_billing_metering` finding into an `H_harness` class document would archive
the individual and leave the D lane with no live blocker — laundering a blocker out of
existence by filing it under someone else's lane. So a class document has ONE lane, and a
member whose lane differs is REFUSED consolidation and stays live in the root. The class
document's own severity is the MAXIMUM over its members for the same reason: a class that
supersedes a blocker is itself blocking.

COST IS MEASURED, never estimated (exit criterion 4): `cost_evidence()` extracts numbers
from the instances' own recorded evidence — an hours figure only counts when a cost word
(wedge, outage, stall, blackout, starved …) sits within `_COST_CONTEXT_WINDOW` characters
of it, so the ageing rule's "72 hours" and a bare "3h" in a log excerpt do not become a
cost. Every extracted figure is printed with its source filename and its verbatim phrase,
because a cost that cannot be traced back to an artefact is precisely the mirror class
this consolidation lists. Each instance contributes ONE figure — its own largest — so a
document that states its episode twice is not billed twice, and the headline is named
`recorded episode-hours` rather than `hours lost` because two findings can describe the
same outage from different angles. What it measures is attention actually spent and
recorded; an instance that never measured its own damage contributes zero.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from background.finding_severity import (
    BLOCKING,
    DOORBELL_PREFIXES,
    LATENT,
    RECORDED,
    FindingSeverity,
    parse_severity_file,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STAGING_ROOT = REPO_ROOT / "docs" / "staging"
ARCHIVE_DIRNAME = "done"
PARKED_DIRNAME = "in_progress"
RECORDS_DIRNAME = "records"

#: The four rooms a staged document can occupy, and the ONE claim each makes about it:
#: the root says LIVE (it rings the doorbell and wins draws), `done/` says CONSUMED,
#: `in_progress/` says PARKED-WITH-AN-OPEN-SUB-ITEM, `records/` says THIS IS NOT WORK AND
#: NEVER WAS. The claims are mutually exclusive, so one name in two rooms is a contradiction
#: whichever pair it is — and the doorbell reads the loudest copy, which is always the root's.
#:
#: `records/` WAS ADDED THE DAY IT WAS NEEDED AND ONE COMMIT LATE. It landed in
#: `staging_rooms` on 2026-09-03 and this tuple was not updated, so when the migration that
#: created it left 37 pre-registrations in BOTH the root and `records/`, `room_collisions`
#: reported nothing and `check()` printed PASS — a collision detector blind to the room that
#: had just been created, which is `controls keyed to a structure that moved` committed by the
#: hand that moved the structure. A new room is not a new room until this tuple knows about it.
ROOM_DIRNAMES = (ARCHIVE_DIRNAME, PARKED_DIRNAME, RECORDS_DIRNAME)

#: Class documents live in the staging root beside the findings they supersede — they are
#: the artefact that wins a draw, so parking them in an archive would defeat the ruling.
#: They are excluded from the classifiable population by this prefix: a class document is
#: about its own family by construction and would otherwise be its own first member.
CLASS_DOC_PREFIX = "CLASS_"

#: Documents authored by someone other than the machine. They are classified for
#: information but never consolidated or archived by this module — see `derive_memberships`.
EXTERNALLY_AUTHORED_PREFIXES = ("ADVISOR_", "DIRECTOR_")

#: SELF-CLEARING ALARMS CANNOT BE SUPERSEDED (2026-08-20, rung-1c BLOCKING draw, H_harness).
#: `background/alarm_repetition.py` escalates a repeating alert into the draw by writing a
#: document named `WORKER_FINDING_REPEATING_ALARM_<slug>_<date>.md` and SUPPRESSING further
#: paging for that signature until the underlying state changes. Two contracts collide there.
#: A class document's is "this supersedes those, which are archived, not deleted"; an alarm's
#: is "I am the live condition and I clear myself". Consolidating one archives an unconverged
#: condition into a cost table while its own pager stays muted — the alert is gone from both
#: channels and nothing converged on anything.
#:
#: OBSERVED, and it is why this is a prefix rule and not a judgement: the deadman's-switch
#: alarm filed TWO documents for ONE signature (`deadman_commit`) minutes apart. The router
#: reads the title, one title said the session "may be WEDGED", and that adverb alone filed it
#: under the publish-gate/wedge class — a class about the control that stops publishing, which
#: this alarm has nothing to do with — while its identical-signature sibling stayed unclassed.
#: A machine writes these titles, so the router is matching on prose no author chose.
#:
#: OUT OF CONSOLIDATION, NOT OUT OF THE POPULATION. These stay in the staging root, keep
#: their severity, keep their lane and stay drawable; `scan_staging_root` and the blocking
#: draw see them exactly as before. The only thing refused is being archived under a class.
SELF_CLEARING_ALARM_PREFIXES = ("WORKER_FINDING_REPEATING_ALARM_",)

#: Severity ordering for the max-over-members rule. UNCLASSIFIED is deliberately absent:
#: an unreadable member is handled explicitly in `class_severity`, never ranked.
_SEVERITY_RANK = {RECORDED: 0, LATENT: 1, BLOCKING: 2}

#: How far from a number a cost word may sit and still make that number a cost.
_COST_CONTEXT_WINDOW = 70


@dataclass(frozen=True)
class FindingClass:
    """One family: the ruling's five, plus any registered later under R10.

    `provenance` is WHO COUNTED, and it is a field rather than a constant because the five
    original classes were the DIRECTOR'S measurement and a class registered later is not. The
    renderer prints it verbatim beside the count, so a class the ruling never named cannot
    borrow the ruling's authority by sharing its template. `ruling_count` is what that source
    measured — for a self-registered class, the number of instances that had been observed when
    it was registered, which R10 requires to be at least two: one instance is not a class.
    """

    id: str
    title: str
    ruling_name: str
    ruling_count: int
    lane: str
    patterns: tuple[re.Pattern[str], ...]
    #: The date in the class document's filename. The five original classes were all registered
    #: on the day of the ruling; a later class carries its own date, because a document named
    #: for a day it was not written on is a small lie that a reader has no way to check.
    registered: str = "2026-08-12"
    #: Empty means the ruling. Anything else is printed instead of the ruling citation.
    provenance: str = ""

    @property
    def document_name(self) -> str:
        return f"{CLASS_DOC_PREFIX}{self.id.upper()}_{self.registered}.md"

    @property
    def provenance_citation(self) -> str:
        if self.provenance:
            return self.provenance
        return (
            f"`DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12`, clause 1, "
            f'"{self.ruling_name}"'
        )


def _p(*alternatives: str) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(a, re.I) for a in alternatives)


#: DECLARED PRECEDENCE — first match wins (see module docstring). The order runs from the
#: most specific mechanism (a gate that wedged publishing) to the most general symptom (a
#: thing that never runs), because the general patterns would otherwise swallow the
#: specific ones and the partition would collapse into one class.
CLASSES: tuple[FindingClass, ...] = (
    FindingClass(
        id="publish_gate_and_wedge",
        title="The publish gate and the wedge: the control that stops publishing, and what it stops on",
        ruling_name="publish-gate/wedge",
        ruling_count=18,
        lane="H_harness",
        patterns=_p(
            r"publish[_ ]gate",
            r"\bwedge\b|\bwedged\b",
            r"pre[_ ]commit[_ ]gate",
            r"\bgate('?s)?\b.*\b(scope|subject|selector|select|lint|scratch|red|green|admission|audit)",
            r"\b(scope|subject|selector|select|lint|scratch|red|green)\b.*\bgate('?s)?\b",
            r"seven[_ ]reds|reds[_ ]live[_ ]at[_ ]head",
            r"\btmpfs\b|\boom\b",
            r"surgical[_ ]land",
        ),
    ),
    FindingClass(
        id="controls_that_cannot_fail",
        title="Controls that cannot fail: vacuous, fail-open, or blind to their own subject",
        ruling_name="controls that cannot fail — vacuous, fail-open, blind",
        ruling_count=9,
        lane="H_harness",
        patterns=_p(
            r"fail[_ -]?open|fail[_ -]?silent|fails?[_ ]open|fails?[_ ]silently",
            r"\bvacuous",
            r"cannot[_ ]fail",
            r"\bdisarm(s|ed|ing)?\b|\bsilenced\b|\bswallow(s|ed)?\b|\bcensors\b",
            r"\bno[_ ]falsifier\b|has[_ ]no[_ ]falsifier",
            r"\bblind(ed|s|ness)?\b",
            r"mutation.*(surviv|patches[_ ]both)|surviv.*mutation",
            r"\b(guard|control|refusal|alarm|gate|check)\b.*\b(did[_ ]not[_ ]fire|never[_ ]fire|does[_ ]not[_ ]fire)",
            r"fires[_ ]on[_ ]the[_ ]word|trips[_ ]on[_ ]the[_ ]word",
        ),
    ),
    FindingClass(
        id="measurements_that_mirror",
        title="Measurements that mirror the thing they measure: the instrument reads its own subject back",
        ruling_name="measurements that mirror the thing they measure",
        ruling_count=7,
        lane="H_harness",
        patterns=_p(
            r"\bmirror(s|ed|ing)?\b",
            r"\b(is|was|are|were)[_ ]the[_ ](compan(y|ys)|organs?|registers?|markers?|panels?)('?s)?[_ ]own\b",
            r"world('?s)?.*\bis[_ ]the[_ ]compan(y|ys)",
            r"belief.*truth|truth.*belief",
            r"own[_ ](claims|rule|render|admission|estimate|belief)",
            r"derived[_ ]from[_ ]the[_ ]same[_ ]source",
        ),
    ),
    FindingClass(
        id="uncommitted_and_orphaned_work",
        title="Uncommitted and orphaned work: finished work that never became part of the tree",
        ruling_name="uncommitted/orphaned work",
        ruling_count=7,
        lane="H_harness",
        patterns=_p(
            r"\buncommitted\b|\bsat[_ ]uncommitted\b",
            r"\borphan(ed|s)?\b",
            r"\buntracked\b",
            r"never[_ ]lands?|unlanded|did[_ ]not[_ ]land|cannot[_ ]land",
            r"landed[_ ]without[_ ]its[_ ]mechanism|without[_ ]its[_ ](mechanism|control)",
            r"ahead[_ ]of[_ ]its[_ ]input",
            r"\bresurrect(ed|ion)?\b",
        ),
    ),
    FindingClass(
        id="no_caller_and_never_runs",
        title="No caller, never runs: code and controls nothing reaches",
        ruling_name="no-caller/never-runs",
        ruling_count=5,
        lane="H_harness",
        patterns=_p(
            r"no[_ ]caller|never[_ ]called|never[_ ]runs?\b|never[_ ]ran\b",
            r"unreachable",
            r"\buntested\b|\bnever[_ ]tested\b",
            r"tests[_ ]the[_ ]gate[_ ]never[_ ]ran",
            r"\bunimportable\b|\bdead[_ ](code|lane)\b",
            r"\binert\b",
        ),
    ),
    #: REGISTERED 2026-08-28 UNDER R10, and the first class here the director's ruling did not
    #: name. R10: "an absurdity-class defect may NOT be closed with an instance fix — closure
    #: requires extending the invariant library so the entire class fails automatically." The
    #: same shape published the same GBP 39,962.17 discrepancy twice in two days, in two
    #: artefacts, from one cause, so the second repair had to register the family rather than
    #: fix the second file.
    #:
    #: LAST IN THE PRECEDENCE, deliberately, and against this tuple's own most-specific-first
    #: ordering. Both founding members DECLARE themselves under `## Class registration`, and a
    #: declaration beats the title regex, so precedence decides nothing for them. What it would
    #: decide is what happens to a FUTURE document that says both "superseded clock" and
    #: "wedged": placed first, this class would quietly start taking documents away from
    #: `publish_gate_and_wedge`, whose members have never been reclassified and should not be.
    #: The patterns below are a backstop for a document that forgets to declare, not the
    #: primary route in.
    FindingClass(
        id="figures_on_a_superseded_clock",
        title=(
            "Figures on a superseded clock: a summary frozen before the rows it summarises "
            "were mutated, published beside a figure re-summed from them"
        ),
        ruling_name="figures on a superseded clock",
        ruling_count=2,
        lane="H_harness",
        registered="2026-08-28",
        provenance=(
            "registered under R10 by `WORKER_FINDING_THE_PUBLISHED_TREASURY_IS_ON_A_"
            "SUPERSEDED_CLOCK_BESIDE_A_REALISED_NET_MARGIN_2026-08-28`, which is the SECOND "
            "instance and names the class; not one of the director's five, and the count is "
            "this module's own"
        ),
        patterns=_p(
            r"superseded[_ ]clock|superseded[_ ]read|superseded[_ ]scalar",
            r"frozen[_ ](scalar|summary|read)",
            r"stale[_ ]scalar",
            r"\btwo[_ ]clocks\b|\bone[_ ]clock[_ ]and[_ ]one[_ ]stale\b",
            r"does[_ ]not[_ ]add[_ ]up|do[_ ]not[_ ]reconcile",
            r"without[_ ]its[_ ]clock|no[_ ]financial[_ ]figure[_ ]without",
        ),
    ),
)

CLASSES_BY_ID = {c.id: c for c in CLASSES}


@dataclass(frozen=True)
class Classification:
    """One document's class. `class_id` is None when nothing matched — UNCLASSED."""

    path: Path
    class_id: str | None
    matched_phrase: str | None = None
    also_matched: tuple[str, ...] = ()
    #: The class this document DECLARED for itself, verbatim, whether or not that token is
    #: a real class id. Carried rather than resolved so that `check()` can tell "declared
    #: nothing" from "declared a name this module does not have" — collapsing those two into
    #: `class_id is None` is the same silence the declaration channel exists to break.
    declared_class_id: str | None = None

    @property
    def is_classed(self) -> bool:
        return self.class_id is not None

    @property
    def is_contested(self) -> bool:
        return bool(self.also_matched)

    def describe(self) -> str:
        contested = f"  [also: {', '.join(self.also_matched)}]" if self.also_matched else ""
        return f"{self.class_id or 'unclassed':<32} {self.path.name}{contested}"


@dataclass(frozen=True)
class CostItem:
    """One traced cost figure: a number, its unit, and the words it came from."""

    source: str
    amount: float
    unit: str
    phrase: str


@dataclass
class ClassMembership:
    """A class, its consolidated members, and the members it REFUSED."""

    finding_class: FindingClass
    #: Live members: still in the staging root, not yet archived under this class.
    members: list[Path] = field(default_factory=list)
    #: Already-consolidated instances: named by the existing class document AND present in
    #: the archive. Carried so that re-rendering ADDS the sixteenth instance instead of
    #: forgetting the first fifteen — the first draft of the renderer emptied every class
    #: document the moment its members were archived, which is the same "the record is the
    #: population" mistake this module exists to refuse.
    archived: list[str] = field(default_factory=list)
    refused_out_of_lane: list[tuple[Path, str | None]] = field(default_factory=list)

    @property
    def count(self) -> int:
        """The one number this class prints. Exit criterion 5 makes the printed count and
        the instance list the SAME object, so they cannot disagree — the one-name-one-number
        class has already been filed once against this project's own registers."""
        return len(self.members) + len(self.archived)

    def instance_names(self) -> list[str]:
        """Every instance this class holds, live or archived, in one sorted list."""
        return sorted([p.name for p in self.members] + list(self.archived))

    def instance_paths(self, root: Path) -> list[Path]:
        """Where each instance currently LIVES — the root before consolidation, the
        archive after it. Severity and cost are read from these, so the class document
        says the same thing before and after the move."""
        root = Path(root)
        archive = root / ARCHIVE_DIRNAME
        by_name = {p.name: p for p in self.members}
        return [by_name.get(name, archive / name) for name in self.instance_names()]


def subject_of(path: Path, text: str = "") -> str:
    """The classification subject: the filename plus the document's first heading.

    Underscores become spaces so a filename reads like the sentence it is; the patterns
    then match either form. The heading is included because a handful of older findings
    carry a terse filename and a full-sentence title.
    """
    stem = path.stem.replace("_", " ")
    heading = ""
    for line in text.splitlines():
        if line.startswith("# "):
            heading = line[2:]
            break
    return f"{stem}\n{heading}"


def classify_subject(subject: str, path: Path | None = None) -> Classification:
    """Assign at most one class to `subject`, by declared precedence."""
    where = path or Path("<text>")
    hits: list[tuple[str, str]] = []
    for finding_class in CLASSES:
        for pattern in finding_class.patterns:
            match = pattern.search(subject)
            if match:
                hits.append((finding_class.id, match.group(0).strip()))
                break
    if not hits:
        return Classification(where, None)
    winner_id, phrase = hits[0]
    return Classification(where, winner_id, phrase, tuple(h[0] for h in hits[1:]))


#: THE SELF-DECLARATION CHANNEL, and why the title alone was not enough.
#:
#: The module docstring above is right that the BODY is the wrong subject: match it and every
#: document that merely MENTIONS the publish gate joins the publish-gate class, and the
#: classifier stops partitioning. But title-only is FAIL-OPEN in the other direction, and the
#: failure is silent: a finding that genuinely belongs to a class but is titled for its
#: MECHANISM rather than its FAMILY classifies as None, is not refused and not flagged, and
#: the class document simply never learns it exists.
#:
#: That is not hypothetical. `WORKER_FINDING_THREE_CONSECUTIVE_PASSES_RECORDED_A_LANDING_
#: THAT_IS_IN_NO_COMMIT_2026-08-19` is a member of `uncommitted_and_orphaned_work` by its own
#: written registration, and `--check` PASSED with it live and unlisted for the whole of its
#: six-pass history, because its title names the landing procedure and carries no
#: `uncommitted`/`orphan`/`untracked` token. It filed that against itself as item 3.
#:
#: The fix is a declaration, not a wider net: the document states its class as an ACT, under
#: its own heading, and that act BEATS the title regex — a document that knows its family is
#: better evidence than a keyword that happens to be in its filename. Scoping the parse to the
#: section is what keeps this from re-opening the hole the docstring refuses: a class id
#: quoted in prose (this comment block included) is a mention, and a mention is not a claim.
_CLASS_REGISTRATION_HEADING_RE = re.compile(r"^#{1,6}[ \t]+Class registration[ \t]*$", re.M)
_ANY_HEADING_RE = re.compile(r"^#{1,6}[ \t]", re.M)
_DECLARATION_RE = re.compile(r"\bBelongs to\s+`([A-Za-z0-9_]+)`")


def declared_class_of(text: str) -> str | None:
    """The class id this document declares for itself under `## Class registration`.

    Returns the token VERBATIM and does not check it against `CLASSES_BY_ID` — resolving it
    here would let a typo read as "declared nothing", which routes the document nowhere and
    says nothing about it. `check()` makes an unknown token a failure instead.
    """
    heading = _CLASS_REGISTRATION_HEADING_RE.search(text)
    if heading is None:
        return None
    section = text[heading.end() :]
    following = _ANY_HEADING_RE.search(section)
    if following is not None:
        section = section[: following.start()]
    match = _DECLARATION_RE.search(section)
    return match.group(1) if match else None


def classify_file(path: Path) -> Classification:
    """Classify one file: its own declaration if it makes one, otherwise its title.

    An unreadable file is UNCLASSED and says so — an unavailable check is a FAILED check
    (R15 killer pattern 3), so it must never quietly become a member of anything.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return Classification(path, None)
    by_title = classify_subject(subject_of(path, text), path)
    declared = declared_class_of(text)
    if declared is None:
        return by_title
    if declared not in CLASSES_BY_ID:
        # UNCLASSED, but the bad token is carried out so `check()` can name it. Guessing the
        # nearest class would consolidate — and archive — a document on a typo.
        return Classification(path, None, declared_class_id=declared)
    # The declaration wins, and any class the TITLE matched is demoted to `also_matched`
    # rather than dropped: a contested document stays visible to `--list`, which is the
    # at-most-one-class rule's release valve and not a thing to spend on the declaration.
    contested = tuple(
        c for c in (by_title.class_id, *by_title.also_matched) if c and c != declared
    )
    return Classification(path, declared, f"Belongs to `{declared}`", contested, declared)



#: THE REFERENCE ROOM (2026-08-28, director: "Six are the CLASS registers, which are reference
#: and should never drain ... Four different kinds of thing share one folder and only one is
#: work"). A class register is a STANDING document — it is re-rendered in place and is never
#: actioned and archived — so while it sat in the staging root the root could never reach zero,
#: and a queue that cannot signal "drained" is how that folder reached 49 items.
#:
#: THE LOOKUP SPANS BOTH ROOMS, and that is the load-bearing part rather than a courtesy.
#: Moving a file is precisely how a control goes QUIET instead of loud: it keeps reading the
#: old path, finds nothing, and reports nothing wrong. (This project found six readers still
#: reading one half of a map that had split in two, all of them passing.) `class_document_path`
#: in `background/staging_rooms.py` is the ONE place that knows where a register may be, so a
#: register in either room is found by every reader here, and a half-finished move cannot
#: produce a silent pass. Falls back to the root if that module is unavailable — an import
#: failure must not turn every register into MISSING and wedge the publish gate.
def _class_doc_path(root: Path, name: str) -> Path:
    try:
        from background.staging_rooms import class_document_path
        return class_document_path(name, root)
    except Exception:
        return Path(root) / name

def classifiable_documents(root: Path | str = DEFAULT_STAGING_ROOT) -> list[Path]:
    """Every `*.md` in the staging root that is neither a machine doorbell nor a class
    document. Counted FROM THE FILESYSTEM — the population is the glob, never a list."""
    return [
        p
        for p in sorted(Path(root).glob("*.md"))
        if not p.name.startswith(DOORBELL_PREFIXES) and not p.name.startswith(CLASS_DOC_PREFIX)
    ]


def class_severity(members: list[Path]) -> tuple[str, list[FindingSeverity]]:
    """The MAXIMUM severity over the members, with each member's parsed severity.

    Why maximum and not modal: a class document supersedes its instances, so if any
    instance says a control is untrustworthy, the class says it too. Taking anything less
    would let consolidation launder a blocker into a housekeeping note — the very move
    clause 2 of the ruling forbids.
    """
    parsed = [parse_severity_file(p) for p in members]
    if not parsed:
        return LATENT, parsed
    if any(s.severity not in _SEVERITY_RANK for s in parsed):
        # An unreadable or unclassified member cannot be shown to be harmless, so it counts
        # as the worst case rather than being dropped out of the maximum. Fail-closed: an
        # unavailable input is a FAILED input (R15 killer pattern 3), never a quiet zero.
        return BLOCKING, parsed
    best = max(_SEVERITY_RANK[s.severity] for s in parsed)
    return next(v for v, rank in _SEVERITY_RANK.items() if rank == best), parsed


_COST_WORDS = (
    r"wedge|wedged|outage|stall|stalled|blackout|blocked|starv\w*|deadlock|down|"
    r"invisible|silent|episode|lost|late|unpublish\w*|red\b|paused|halt\w*"
)
_COST_CONTEXT_RE = re.compile(_COST_WORDS, re.I)
_HOURS_RE = re.compile(r"(?<![\w.])(\d{1,3}(?:\.\d)?)\s?(?:h\b|hr\b|hrs\b|-?hours?\b)", re.I)
_FENCE_RE = re.compile(r"^```.*?^```", re.M | re.S)
#: The unit marking "this instance names a published figure", counted as documents, never
#: summed as a quantity: the number of documents that touch published output is a count,
#: and adding it to hours would be the wrong-unit class this project has already filed.
FIGURE_UNIT = "published-figure mention"

_FIGURES_RE = re.compile(
    r"published[_ ](?:figure|figures|number|numbers|value|values|panel)", re.I
)


def cost_evidence(text: str, source: str) -> list[CostItem]:
    """Every cost figure `text` records, with the words it came from.

    Two narrowings, both learned from this corpus rather than assumed:

    * A number only becomes a cost when a cost word sits within `_COST_CONTEXT_WINDOW`
      characters of it. Without that, the ruling's own "72 hours" ageing threshold would
      be billed to some class as damage — an estimate wearing a measurement's clothes.
    * FENCED CODE BLOCKS ARE STRIPPED FIRST. A pasted pytest line reading
      `assert '-1 day(s) old'` is quoted evidence, not a statement of what the defect
      cost; the first draft of this function billed exactly that line to a class. Cost is
      claimed in the author's prose or it is not claimed.

    Hours only. Days were dropped after the code-fence false positive above: the corpus
    writes multi-day damage in words ("eight days"), which no digit pattern reaches, so a
    days rule bought nothing but a way to be wrong.
    """
    items: list[CostItem] = []
    text = _FENCE_RE.sub("", text)
    for pattern, unit in ((_HOURS_RE, "hours"),):
        for match in pattern.finditer(text):
            start = max(0, match.start() - _COST_CONTEXT_WINDOW)
            end = min(len(text), match.end() + _COST_CONTEXT_WINDOW)
            window = text[start:end]
            if not _COST_CONTEXT_RE.search(window):
                continue
            phrase = " ".join(window.split())
            items.append(CostItem(source, float(match.group(1)), unit, phrase))
    for match in _FIGURES_RE.finditer(text):
        start = max(0, match.start() - _COST_CONTEXT_WINDOW)
        end = min(len(text), match.end() + _COST_CONTEXT_WINDOW)
        items.append(CostItem(source, 1.0, FIGURE_UNIT,
                              " ".join(text[start:end].split())))
    return items


def worst_per_instance(costs: list[CostItem]) -> list[CostItem]:
    """The single largest HOURS figure each source document records.

    Why per-instance maximum and not a plain sum over every extracted number: a finding
    states its episode more than once ("31h", then "the 25h window inside it"), and
    summing those inside one document invents time nobody lost. One document, one figure.
    """
    best: dict[str, CostItem] = {}
    for item in costs:
        if item.unit != "hours":
            continue
        current = best.get(item.source)
        if current is None or item.amount > current.amount:
            best[item.source] = item
    return list(best.values())


def cost_for_members(members: list[Path], root: Path) -> list[CostItem]:
    """Cost evidence for every member, read from wherever the member currently lives —
    the staging root before consolidation, the archive after it."""
    items: list[CostItem] = []
    for member in members:
        path = member if member.exists() else Path(root) / ARCHIVE_DIRNAME / member.name
        if not path.exists():
            continue
        items.extend(cost_evidence(path.read_text(encoding="utf-8", errors="replace"),
                                   member.name))
    return items


def derive_memberships(root: Path | str = DEFAULT_STAGING_ROOT) -> dict[str, ClassMembership]:
    """Derive every class's membership from the live staging root.

    The lane guard lives here: a document whose OWN severity header names a different lane
    from the class document's is refused consolidation and stays live, because archiving
    it would remove its lane's blocker while filing it under someone else's lane.
    """
    memberships = {c.id: ClassMembership(c) for c in CLASSES}
    for path in classifiable_documents(root):
        classification = classify_file(path)
        if not classification.is_classed:
            continue
        if path.name.startswith(EXTERNALLY_AUTHORED_PREFIXES):
            # OUT OF POPULATION. Clause 5 of the same ruling exists because four advisor
            # documents sat unopened for a week; folding one into a class document and
            # archiving it would be that silence with a mechanism behind it. Another
            # party's ask is dispositioned individually, answered to its author.
            continue
        if path.name.startswith(SELF_CLEARING_ALARM_PREFIXES):
            # OUT OF CONSOLIDATION — see `SELF_CLEARING_ALARM_PREFIXES`. Same door as the
            # one above and for the same reason at a different address: consolidation is a
            # supersession claim, and neither an absent author's ask nor a live self-clearing
            # alarm is a thing this module is entitled to supersede.
            continue
        severity = parse_severity_file(path)
        if severity.severity == RECORDED:
            # OUT OF POPULATION, read from OPS9's parse rather than a second list. A class
            # document exists to argue one repair against one cumulative cost; a RECORDED
            # document is a landed record with nothing owed, so it has no repair to argue
            # and no cost to add. Folding reports of FIXES into a class of DEFECTS would
            # inflate every instance list with work already done.
            continue
        membership = memberships[classification.class_id or ""]
        if severity.lane != membership.finding_class.lane:
            # Fail-closed, including a missing lane: a document that cannot be SHOWN to be
            # in this lane is not consolidated. Archiving it would remove its own lane's
            # finding while recording it under this one.
            membership.refused_out_of_lane.append((path, severity.lane))
            continue
        membership.members.append(path)

    for membership in memberships.values():
        membership.archived.extend(
            archived_instances(Path(root), membership.finding_class)
        )
    return memberships


def archived_instances(root: Path, finding_class: FindingClass) -> list[str]:
    """Instances the existing class document names AND that are present in the archive.

    The archive presence requirement is deliberate: it is what stops the class document
    from being its own evidence. A name that has been deleted (or resurrected back into
    the root, which `check()` reports separately) does not silently keep counting as a
    consolidated instance just because a document still lists it.
    """
    doc = _class_doc_path(root, finding_class.document_name)
    if not doc.exists():
        return []
    listed = _INSTANCE_LINE_RE.findall(doc.read_text(encoding="utf-8", errors="replace"))
    archive = root / ARCHIVE_DIRNAME
    return sorted(name for name in listed if (archive / name).exists())


#: THE DECISION SECTION, CARRIED THROUGH A RE-RENDER VERBATIM.
#:
#: `background/class_debt.py` reads a `## Disposition` section off these registers to decide
#: whether a class is still work. This renderer rewrites the whole file, so without this the
#: first `--render` after a decision was taken would silently delete it and put the class back
#: at the head of the draw — and it would look like the decision was never made rather than
#: like it was destroyed. That is the same argument this module already makes for `archived`
#: (a re-render must ADD the sixteenth instance, not forget the first fifteen), at the one
#: place where the thing being forgotten is a judgement a person made.
#:
#: CARRIED VERBATIM AND NOT PARSED. This module does not need to understand a disposition to
#: preserve one, and a carry-through that re-serialised it from a parse would silently drop
#: any field the parser did not know about — including a field a later reader depends on.
#: STOPS AT THE FOOTER RULE AS WELL AS AT THE NEXT HEADING. The generated footer is `---`
#: followed by prose and carries no heading, so a lookahead for headings alone ran the captured
#: section to end-of-file and swallowed it — and the renderer then appended a second footer. That
#: was caught on the first real re-render and is exactly the shape of a carry-through that
#: preserves more than it was asked to.
_DISPOSITION_SECTION_RE = re.compile(
    r"^#{1,6}[ \t]+Disposition[ \t]*$.*?(?=^#{1,6}[ \t]|^---[ \t]*$|\Z)", re.M | re.S
)


def existing_disposition_section(root: Path | str, finding_class: FindingClass) -> str:
    """The `## Disposition` section the register already carries, verbatim, or ""."""
    doc = _class_doc_path(Path(root), finding_class.document_name)
    if not doc.exists():
        return ""
    match = _DISPOSITION_SECTION_RE.search(
        doc.read_text(encoding="utf-8", errors="replace")
    )
    return match.group(0).rstrip() if match else ""


def render_class_document(
    membership: ClassMembership,
    root: Path | str = DEFAULT_STAGING_ROOT,
) -> str:
    """Render one class document: header, instance list, measured cost, what is owed.

    The printed count is `membership.count`, which IS the length of the list the same
    call renders. Exit criterion 5 is met by construction, and `check()` re-reads the
    rendered file to prove it stayed met.

    Rendering is IDEMPOTENT and ADDITIVE: instances already archived under this class are
    carried through from the existing document, so a re-render after the move keeps the
    fifteen and adds the sixteenth rather than emptying the list.
    """
    root = Path(root)
    finding_class = membership.finding_class
    members = membership.instance_paths(root)
    severity, parsed = class_severity(members)
    costs = cost_for_members(members, root)
    worst = worst_per_instance(costs)
    hours = sum(item.amount for item in worst)
    largest = max((item.amount for item in worst), default=0.0)
    figure_docs = sorted({c.source for c in costs if c.unit == FIGURE_UNIT})
    blocking = [s for s in parsed if s.severity == BLOCKING]

    lines: list[str] = []
    lines.append(f"# [CLASS] {finding_class.title}")
    lines.append("")
    lines.append(f"**Severity:** {severity} · **Lane:** {finding_class.lane}")
    lines.append("")
    lines.append(
        f"**Instances:** {membership.count} · **Class:** `{finding_class.id}` · "
        f"**Source's own count:** ~{finding_class.ruling_count} "
        f"({finding_class.provenance_citation})"
    )
    lines.append("")
    lines.append(
        "**THIS IS A REGISTER, NOT A QUEUE ITEM. Do not archive it.** Since 2026-09-01 an "
        "accruing class register is DRAWN as work (`background/class_debt.py`, rank 35), and a "
        "drawn document is normally actioned and moved to `done/`. Doing that here is the "
        "2026-08-23 failure: a bulk archive carried all five registers out of the root and "
        "wedged four consecutive publish cycles behind `MISSING CLASS DOC` while the files sat "
        "intact in `done/`. **You action this document by writing a decision into its "
        "`## Disposition` section** — repaired and closed by a named mechanism, or accepted as "
        "a limitation with its cost beside it. That is what takes it out of the draw, and it "
        "stays exactly where it is."
    )
    lines.append("")
    lines.append(
        "This document supersedes the individual findings listed below, which are "
        f"**archived, not deleted**, in `docs/staging/{ARCHIVE_DIRNAME}/`. Membership is "
        "DERIVED, never hand-kept: `python3 -m background.finding_classes --check` "
        "re-derives it from the filesystem and fails if a live finding belongs to this "
        "class and is not listed here, if a listed instance is missing from the archive "
        "or has come back to the root, or if the count above stops equalling the length "
        "of the list below."
    )
    lines.append("")
    lines.append(f"## The {membership.count} instances")
    lines.append("")
    for path in sorted(members, key=lambda p: p.name):
        lines.append(f"- `{path.name}` — {parse_severity_file(path).severity}")
    lines.append("")

    lines.append("## Cumulative cost, measured from the instances' own recorded evidence")
    lines.append("")
    if worst:
        lines.append(
            f"**{hours:.1f} recorded episode-hours** across {len(worst)} of the "
            f"{membership.count} instances; largest single recorded episode "
            f"**{largest:g}h**; {len(figure_docs)} instance(s) name a published figure in "
            "scope."
        )
        lines.append("")
        lines.append(
            "**The definition, because a bare sum here would be the very defect this "
            "class catalogues.** Each instance contributes the LARGEST duration it "
            "records with evidence — one figure per document, so a finding that states "
            "the same episode twice is not billed twice. The sum is then over DOCUMENTS, "
            "not over distinct outages: two findings describing the same wedge from "
            "different angles each contribute, so this is *recorded episode-hours*, not a "
            "claim that this many distinct hours were lost. An instance that never "
            "measured its own damage contributes zero, which makes the figure a floor on "
            "attention spent and never an estimate. Every line below is traceable to the "
            "document and the sentence it came from — a cost that cannot be traced is the "
            "mirror class this consolidation itself lists."
        )
        lines.append("")
        for item in sorted(worst, key=lambda c: (-c.amount, c.source)):
            lines.append(f"- **{item.amount:g} {item.unit}** — `{item.source}`: "
                         f"…{item.phrase[:180]}…")
    else:
        lines.append(
            f"**0 hours traced** across {membership.count} instances. No instance in this "
            "class recorded a duration with evidence, so the traced cost is zero — which "
            "is a statement about the instances' measurement, not a claim that the class "
            "was free. No prose estimate is offered in its place."
        )
    lines.append("")

    if blocking:
        lines.append("## What is owed")
        lines.append("")
        lines.append(
            f"{len(blocking)} of these instances are BLOCKING, so this class document is "
            f"BLOCKING in `{finding_class.lane}` (the class inherits the MAXIMUM severity "
            "of its members — consolidation must never launder a blocker into a "
            "housekeeping note). Each is discharged the way clause 2 allows: repaired, or "
            "the limitation explicitly recorded and accepted."
        )
        lines.append("")
        for result in sorted(blocking, key=lambda s: s.path.name):
            lines.append(f"- `{result.path.name}`")
        lines.append("")

    if membership.refused_out_of_lane:
        lines.append("## Refused consolidation — out of lane, still live")
        lines.append("")
        lines.append(
            "These documents match this class but carry a different lane. They are NOT "
            "archived and NOT superseded: severity is lane-scoped, so filing them here "
            "would remove their own lane's finding while recording it under "
            f"`{finding_class.lane}`."
        )
        lines.append("")
        for path, lane in sorted(membership.refused_out_of_lane, key=lambda t: t[0].name):
            lines.append(f"- `{path.name}` — lane `{lane}`")
        lines.append("")

    disposition = existing_disposition_section(root, finding_class)
    if disposition:
        lines.append(disposition)
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "Generated by `background/finding_classes.py` (atom "
        "`OPS10_finding_class_consolidation`). Regenerate with "
        "`python3 -m background.finding_classes --render`; verify with `--check`. "
        "The `## Disposition` section, if any, is written by hand and carried through a "
        "re-render verbatim — `background/class_debt.py` reads it to decide whether this "
        "class is still work, and ranks it in the draw by what it has cost."
    )
    lines.append("")
    return "\n".join(lines)


_PRINTED_COUNT_RE = re.compile(r"\*\*Instances:\*\*\s*(\d+)")
_INSTANCE_LINE_RE = re.compile(r"^- `([^`]+\.md)` — [A-Z]+$", re.M)


@dataclass
class CheckResult:
    failures: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures


def _room_names(room: Path) -> set[str]:
    if not room.is_dir():
        return set()
    return {p.name for p in room.glob("*.md") if p.is_file()}


def room_collisions(root: Path | str = DEFAULT_STAGING_ROOT) -> list[tuple[str, str, str]]:
    """Every document name occupying more than one staging room, as (name, roomA, roomB).

    POPULATION IS THE ROOMS, NOT A LIST. Rule 3 above only ever asks about names a class
    document already carries, so it can only see a resurrection of a consolidated WORKER
    finding. The state that cost a rung-1c draw on 2026-08-12 was an ADVISOR findings note
    — dispositioned into `in_progress/` with its severity downgraded BLOCKING -> OPEN, and
    a stale root copy still reading `**Severity:** BLOCKING` — which no class document has
    ever named, so no listed-instance walk could reach it. It is checked here by being a
    file in a room, which is the one property every staged document has.

    ALL THREE PAIRINGS, not one. The 2026-08-12 both-rooms census was run root-vs-`done/`
    by hand and declared zero; it was zero, and root-vs-`in_progress/` held one while
    `done/`-vs-`in_progress/` held three — a document simultaneously archived as consumed
    and parked as open. A census over one of three pairs reads exactly like a clean sweep.
    """
    root = Path(root)
    rooms = {"root": _room_names(root)}
    for dirname in ROOM_DIRNAMES:
        rooms[dirname] = _room_names(root / dirname)

    collisions: list[tuple[str, str, str]] = []
    labels = sorted(rooms)
    for i, left in enumerate(labels):
        for right in labels[i + 1 :]:
            for name in sorted(rooms[left] & rooms[right]):
                collisions.append((name, left, right))
    return sorted(collisions)


def check(root: Path | str = DEFAULT_STAGING_ROOT) -> CheckResult:
    """Re-derive membership and verify the seven things that can silently rot.

    0. No document registers itself under a class id this module does not have. A typo in
       the declaration is indistinguishable from no declaration at all unless something
       asks — the fail-open the registration channel closes, reproduced one level down.

    1. Every live finding maps to AT MOST ONE class or to unclassed (exit criterion 3).
    2. Every live finding that belongs to a class is listed in that class's document —
       the sixteenth-instance detector, without which consolidation decays the day after
       it lands.
    3. Every listed instance is IN the archive and NOT back in the root (exit criterion 2;
       the resurrection class, `WORKER_FINDING_ARCHIVED_STAGING_PATHS_ARE_RESURRECTED_ON_
       THE_SHARED_TREE_2026-08-10`, is this exact move's known failure mode here).
    4. The count printed in each class document equals its instance list's length
       (exit criterion 5, the one-name-one-number class).
    5. No document name occupies two staging rooms (`room_collisions`) — rule 3's
       subject widened from "names a class document lists" to "files in the rooms",
       because the resurrection that cost a rung-1c draw was of a document no class
       document has ever named.
    6. The severity PRINTED in each class document still equals `class_severity` over
       its instances — the release valve, and the one rule here that can lower a
       severity rather than raise one.

    WHY 6 EXISTS. `render_class_document` derives severity correctly, so the printed
    header is right the moment it is written and never again. OPS9's discharge (a
    `**Discharged:**` header, filesystem-checked) reads a member down to RECORDED, which
    is how a blocker is meant to be released; but a consolidated member lives in the
    ARCHIVE, and nothing re-reads the class document after it changes. Discharge every
    blocking member of a class and the class document goes on printing BLOCKING, `check()`
    goes on passing, and `_blocking_lane_draw` goes on freezing the lane off a header no
    control any longer stands behind. Rules 1-5 could each only ever ADD an obligation, so
    a lane's blocker set could only grow — the same shape as the defect the discharge
    header was built to fix, one layer up, which is where a new layer above a control
    inherits the control's subject and not its release.
    """
    root = Path(root)
    archive = root / ARCHIVE_DIRNAME
    result = CheckResult()

    for name, left, right in room_collisions(root):
        result.failures.append(
            f"TWO ROOMS {name}: present in {left} AND {right} — the rooms make "
            "mutually exclusive claims (live / consumed / parked), and the doorbell "
            "reads the root copy"
        )

    for path in classifiable_documents(root):
        classification = classify_file(path)
        declared = classification.declared_class_id
        if declared is not None and declared not in CLASSES_BY_ID:
            result.failures.append(
                f"UNKNOWN DECLARED CLASS {path.name}: registers itself under `{declared}`, "
                f"which is not one of {', '.join(CLASSES_BY_ID)}. Left unchecked a typo in "
                "the declaration reads exactly like no declaration at all — the document "
                "routes nowhere and nothing goes red, which is the fail-open the "
                "registration channel exists to close, one level down"
            )
        if classification.is_contested:
            result.notes.append(
                f"CONTESTED {path.name}: {classification.class_id} "
                f"(also matched {', '.join(classification.also_matched)})"
            )

    for finding_class in CLASSES:
        doc = _class_doc_path(root, finding_class.document_name)
        if not doc.exists():
            # A CLASS DOCUMENT THAT WENT MISSING WAS USUALLY ARCHIVED, NOT LOST, and the
            # two states want opposite repairs. `--render` is right when the document was
            # never written; it is WRONG when a sweep moved this one into `done/`, because
            # re-rendering writes a second copy and leaves the archived one behind — the
            # TWO ROOMS state, i.e. the next refusal. On 2026-08-23 a bulk archive carried
            # all five class documents out of the root and wedged FOUR consecutive publish
            # cycles behind `MISSING CLASS DOC` while the files sat intact in `done/`; the
            # generic hint pointed at the one repair that would have made it worse. So say
            # WHICH ROOM holds it and name the move back, and keep the bare failure for the
            # genuinely-absent case.
            elsewhere = [
                dirname
                for dirname in ROOM_DIRNAMES
                if (root / dirname / finding_class.document_name).exists()
            ]
            if elsewhere:
                result.failures.append(
                    f"MISPLACED CLASS DOC {finding_class.document_name}: absent from the "
                    f"staging root, present in {'/ and '.join(elsewhere)}/ — a class "
                    "document lives in the ROOT (its MEMBERS are what get archived). Move "
                    f"it back (`git checkout HEAD -- docs/staging/"
                    f"{finding_class.document_name}` then delete the archived copy); do "
                    "NOT `--render`, which would leave both rooms populated"
                )
            else:
                result.failures.append(f"MISSING CLASS DOC {finding_class.document_name}")
            continue
        text = doc.read_text(encoding="utf-8", errors="replace")

        instances = derive_memberships(root)[finding_class.id].instance_paths(root)
        if instances:
            # An EMPTY class is a stub, not a defect: `_write_class_documents` renders a
            # document for every declared class, and one nobody has filed against has no
            # severity to derive. The vanished-archive case is not silently agreed with
            # either — `instance_paths` still yields the missing paths, which read as
            # unreadable, which `class_severity` ranks BLOCKING, and rule 3 names the
            # files. Only a class with something to derive from is compared.
            printed_severity = parse_severity_file(doc).severity
            derived, _parsed = class_severity(instances)
            if printed_severity != derived:
                result.failures.append(
                    f"STALE SEVERITY {finding_class.document_name}: prints "
                    f"{printed_severity}, instances derive {derived} — re-render "
                    "(`--render`); a discharged member does not release the class "
                    "document until the header is rewritten"
                )

        listed = _INSTANCE_LINE_RE.findall(text)
        printed = _PRINTED_COUNT_RE.search(text)
        if printed is None:
            result.failures.append(f"NO PRINTED COUNT {finding_class.document_name}")
        elif int(printed.group(1)) != len(listed):
            result.failures.append(
                f"COUNT MISMATCH {finding_class.document_name}: printed "
                f"{printed.group(1)}, list holds {len(listed)}"
            )

        for name in listed:
            if (root / name).exists():
                result.failures.append(
                    f"RESURRECTED {name}: superseded by {finding_class.document_name} "
                    "but present in the staging root"
                )
            if not (archive / name).exists():
                result.failures.append(
                    f"ARCHIVE MISSING {name}: named by {finding_class.document_name}, "
                    f"absent from docs/staging/{ARCHIVE_DIRNAME}/"
                )

        live = [p.name for p in derive_memberships(root)[finding_class.id].members]
        for name in live:
            if name not in listed:
                result.failures.append(
                    f"UNCONSOLIDATED {name}: belongs to {finding_class.id}, not listed in "
                    f"{finding_class.document_name}"
                )

    return result


def _write_class_documents(root: Path) -> list[Path]:
    written: list[Path] = []
    for membership in derive_memberships(root).values():
        doc = _class_doc_path(root, membership.finding_class.document_name)
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text(render_class_document(membership, root), encoding="utf-8")
        written.append(doc)
    return written


def consolidate(root: Path | str = DEFAULT_STAGING_ROOT, *, apply: bool = False) -> list[str]:
    """Move every consolidated member out of the work channel and into the archive.

    THE STEP THIS MODULE WAS BUILT AROUND AND NEVER TOOK. Every other part of the mechanism is
    here and has been since 2026-08-12: `derive_memberships` picks the members, the lane guard
    refuses the ones it may not supersede, `render_class_document` writes them into the register
    as an instance list, `archived_instances` reads them back out of `done/`, `instance_paths`
    spans both rooms so the register says the same thing before and after, and `check()` verifies
    the whole thing holds. The class document's own printed text says the members are
    *"archived, not deleted, in docs/staging/done/"*. **Nothing moved them.** So every classed
    finding was named as an instance in a register AND left sitting in the root as a document,
    and the register — the artefact built to let one argument win a draw instead of twenty
    siblings losing it separately — became a second copy of the pile rather than a replacement
    for it.

    Director, 2026-09-03: *"Findings that share a class go to the class register as instances,
    not to the root as documents; the register already exists for exactly that."* It does. This
    is the four lines that make the sentence true.

    RENDER BEFORE MOVE, ALWAYS, and the order is not cosmetic. `derive_memberships` reads the
    LIVE root; move first and the register would be re-rendered from an empty membership and
    would forget the instances it had just lost — the exact "the record is the population"
    mistake `ClassMembership.archived` exists to refuse, committed by the tool that maintains it.

    REFUSALS ARE NOT MOVED and are not silent. A member refused out of lane, an externally
    authored ask, a self-clearing alarm and a RECORDED document are all excluded upstream by
    `derive_memberships`, which is why this function has no opinion about them: they never appear
    in `members`. What it does report is anything it declined to move HERE — a destination that is
    already occupied by a different document — because a consolidation that quietly overwrote an
    archived instance would destroy the evidence the register cites.
    """
    root = Path(root)
    archive = root / ARCHIVE_DIRNAME
    out: list[str] = []
    if apply:
        for doc in _write_class_documents(root):
            out.append(f"rendered {doc.name}")
    for membership in derive_memberships(root).values():
        for path in list(membership.members):
            dst = archive / path.name
            verb = "CONSOLIDATE" if apply else "WOULD CONSOLIDATE"
            if dst.exists() and dst.read_bytes() != path.read_bytes():
                out.append(
                    f"REFUSED {path.name}: a DIFFERENT document of that name is already in "
                    f"{ARCHIVE_DIRNAME}/. The register cites the archived copy; overwriting it "
                    f"would destroy the evidence. Resolve by hand."
                )
                continue
            out.append(f"{verb} [{membership.finding_class.id}] {path.name}")
            if apply:
                archive.mkdir(parents=True, exist_ok=True)
                moved = subprocess.run(["git", "mv", str(path), str(dst)],
                                       cwd=str(root.parent.parent),
                                       capture_output=True, text=True)
                if moved.returncode != 0:
                    path.replace(dst)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(DEFAULT_STAGING_ROOT))
    parser.add_argument("--list", action="store_true", help="print every document's class")
    parser.add_argument("--render", action="store_true", help="(re)write every class doc")
    parser.add_argument("--check", action="store_true", help="verify the consolidation holds")
    parser.add_argument("--consolidate", action="store_true",
                        help="move consolidated members into done/ (dry run without --apply)")
    parser.add_argument("--apply", action="store_true", help="with --consolidate, actually move")
    args = parser.parse_args(argv)

    if args.consolidate:
        for line in consolidate(args.root, apply=args.apply):
            print(line)
        if not args.apply:
            print("\n(dry run -- re-run with --apply to move)")
        return 0

    root = Path(args.root)
    memberships = derive_memberships(root)

    if args.list:
        for path in classifiable_documents(root):
            print(classify_file(path).describe())

    for membership in memberships.values():
        finding_class = membership.finding_class
        print(
            f"{finding_class.id:<32} instances={membership.count:<3} "
            f"ruling~{finding_class.ruling_count:<3} "
            f"refused_out_of_lane={len(membership.refused_out_of_lane)}"
        )

    if args.render:
        for doc in _write_class_documents(root):
            print(f"wrote {doc}")

    if args.check:
        result = check(root)
        for note in result.notes:
            print(note)
        for failure in result.failures:
            print(failure)
        print(f"check: {'PASS' if result.ok else 'FAIL'} ({len(result.failures)} failures)")
        return 0 if result.ok else 1
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/finding_classes.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("finding_classes")
    sys.exit(main())
