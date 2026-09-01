#!/usr/bin/env python3
"""What a finding class COSTS, and what that cost entitles it to in the draw.

WHY THIS EXISTS (director, 2026-09-01): *"Each class register carries a cumulative cost and
nothing reads it. Wire it in. Cumulative cost should rank a class against other work in the
draw. A class with few instances and a small cost is honestly acceptable as a limitation,
recorded with its cost beside it. A class with eight instances and hours of outage each is a
debt that should beat new features until it's closed."*

Both halves of that were missing and they had the same cause. `background/finding_classes.py`
renders a cumulative cost into each register and no caller reads it — the register's own
`no_caller_and_never_runs` class, filed against the register. And
`background/staging_rooms.py` classifies `CLASS_*` as `KIND_REFERENCE`, which is in `NOT_WORK`,
so a class register is dropped from `work_queue()` before rank is ever considered. A cost
nothing reads and an artefact that cannot be drawn are one defect seen from two ends.

WHY REFERENCE WAS THE RIGHT ANSWER UNTIL NOW, and what changed. A register is a STANDING
document: it is re-rendered in place and never actioned-and-archived, so while it sat in the
work channel the queue could never reach zero — which is how that folder reached 49 items. The
2026-08-28 fix (make it reference) was correct given that a register had NO EXIT. This module
gives it one: a `## Disposition` section, written by a person or a seat, that records a
DECISION about the class. A register with a current disposition is not work. A register
without one, that is still accruing instances, is. The register drains by being DECIDED, not
by being consumed — so it can be work without ever being a queue item that must disappear.

THAT IS ALSO WHY THIS IS A DECISION AND NOT A RULE, which is the director's own condition for
it not becoming bureaucracy. Nothing here computes whether a class *should* be closed. It
computes what the class has cost, decides only whether that cost has been LOOKED AT, and puts
the un-looked-at ones in front of the work they are competing with. The judgement stays where
judgement belongs.

---

THREE COST TERMS, IN THREE DIFFERENT UNITS, NEVER ADDED TOGETHER.

Adding them would be this project's most-filed publishing defect — two true numbers whose ratio
(or sum) is not a quantity. They measure different things and each is a FLOOR.

T1 RECORDED EPISODE-HOURS — `finding_classes.cost_for_members`, unchanged and re-used, not
   re-implemented. Hours the instances themselves recorded next to a cost word.

   ITS BLIND SPOT, MEASURED ON THIS CORPUS (2026-09-01): 18 of 118 instances record any
   duration at all. Three of the six classes read 0.0 and none of them was free. T1's
   vocabulary (`wedge|outage|stall|blackout|…`) is the AVAILABILITY vocabulary, which is the
   publish-gate class's own vocabulary — so T1 measures loudest on the class it was written
   from (15 of 55 measured) and reads zero on the classes whose damage is denominated in
   invalidated work. A cost measure that reads its own subject back is `measurements_that_
   mirror`, and it is one of the six classes it is used to rank.

T2 PERSISTED-DAYS — how long the instances say a WRONG STATE stayed live. This is the term
   the director asked for: *"it invalidates whatever was built on top of it in between."*

   THE EXTRACTION IS DELIBERATELY NARROW AND IT WAS NARROWED BY MEASUREMENT, not by taste. A
   wide net over "a duration near a damage word" was run against the whole corpus first and
   accepted 15 figures of which SEVEN were wrong: `"three instances in three days"` is a
   recurrence rate, `"forgets a failed collection after three weeks"` is a model parameter,
   `"predates it by two days"` is an offset. The two spurious three-week reads alone would
   have put 42 days on `measurements_that_mirror`, which has no measured cost at all. So the
   rule is the one SYNTAX that discriminated cleanly: the duration must be governed by `for`
   — "false **for six days**", "served a frozen artefact **for four days**", "sat unwired
   **for nine days**" — and a damage word must still be in the window. On the same corpus that
   accepts 7 figures and rejects all 7 known false ones, at the price of missing real costs
   written another way ("repaired eight days earlier", "what the five days actually cost").

   IT MISSES, AND THAT IS THE CORRECT DIRECTION. A floor that under-reads is honest; a total
   inflated by model parameters is the exact defect these registers catalogue. Every accepted
   figure is printed with the sentence it came from, so a wrong one is visible rather than
   buried in a sum.

T3 COMMITS-ON-TOP — how much work landed while the class was known and unclosed, summed over
   the gaps between consecutive instances. Measured from git and from the instances' filename
   dates; no prose, so nothing to mis-parse.

   WHAT IT IS AND IS NOT. It is the DENOMINATOR of the director's sentence — the body of work
   that was built on top of an open class and is therefore exposed to it. It is NOT a claim
   that all of it was invalidated. It is also NOT summable ACROSS classes: six classes were
   open simultaneously, so the same commit appears under all six, and a total would count the
   tree six times. `render()` prints the column and refuses the total.

WHAT CANNOT BE COUNTED, SAID PLAINLY. The director's own example — *"eleven hours of outage
from two same-day findings interacting"* — is not derivable here. T1 takes each document's
largest figure and sums over documents, so two findings that describe one interacting outage
contribute their separate readings and nothing records the combined episode. `same_day_pairs`
counts the PAIRS where such interaction was possible (134 in the publish-gate class) and stops
there. A number for the interaction itself would have to be invented, and an invented cost in
a register whose purpose is to argue for spending real attention is worse than a gap.

---

ACCRUAL, NOT SIZE, IS WHAT PUTS A CLASS IN FRONT OF OTHER WORK.

The obvious rule — draw a class once its cost passes a threshold — needs a threshold, and a
threshold here would be a number picked because a number was needed. The measured property
that actually separates "a debt that should beat new features" from "a limitation we live
with" needs no such number: is the class STILL PRODUCING INSTANCES? A class that stopped
recurring is a limitation whether or not anyone wrote that down. A class that produced two
instances this week is taxing everything currently being built.

So `still_accruing` is `>= 2` instances in the trailing 7 days, and the 2 is R10's own bar
rather than a new one: one instance is not a class, and by the same argument one instance is
not a recurrence. Cost then ORDERS the accruing classes among themselves; it does not decide
membership. On this corpus that ordering is not the one cost alone would give —
`figures_on_a_superseded_clock` has zero recorded hours and all three of its instances inside
the window, and a cost-threshold rule would have ranked the newest, fastest-accruing class
last.

RANK 35, BETWEEN MINT (30) AND FINDING (40), and the argument is the ruling's own: *"a class
with a live instance list is the artefact that can win a draw; twenty siblings filed
separately cannot."* An individual finding is one instance of something; an accruing class is
what generates such findings, and closing the generator dominates repairing one instance.
Below a person's ask and below an already-decomposed mint, because neither of those is
competing with the class — they are the work the class is taxing.

A DISPOSITION RE-ARMS, or it is a silencer. `ACCEPTED` records the instance count it was
accepted AT; two further instances re-open it, on the same argument as above — two is a new
class's worth of evidence arriving after we said we would live with it. `CLOSED` must name a
mechanism, and `mechanism_resolves()` checks it still exists: a closure whose named control
has been renamed or deleted goes LOUD, never quiet. Both of those are this project's own
lesson about controls that cannot fail, applied to the channel that turns these controls off.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from background import finding_classes as fc
from background.staging_rooms import class_document_path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STAGING_ROOT = fc.DEFAULT_STAGING_ROOT

#: Instances within this many days of "now" count toward accrual. Seven days is one week of
#: this project's own cadence and is the shortest window in which "still happening" can be
#: told from "happened once"; it is a window, not a threshold on cost.
ACCRUAL_WINDOW_DAYS = 7

#: Instances inside the window that make a class ACCRUING. Two, because R10 already fixes two
#: as the point at which a repetition becomes a class rather than an instance, and re-using
#: that bar means this module introduces no new number of its own.
ACCRUAL_MIN_INSTANCES = 2

#: Further instances after an ACCEPTED decision that re-open it. Same 2, same argument: two
#: instances is what makes a class, so two instances arriving after "we will live with this"
#: is a new class's worth of evidence against the decision.
REOPEN_AFTER_INSTANCES = 2

#: POPULATION FLOOR, dated 2026-09-01, as every scanning control here must carry: this module
#: reports "no debt" identically whether the classes are clean or the scan found nothing. Six
#: registers holding 118 instances is the state it was built against. A register is never
#: deleted and an instance is never unfiled, so both can only rise; a drop means the scan lost
#: its subject, which is the failure mode that stays quiet without a floor.
FLOOR_CLASSES = 6
FLOOR_INSTANCES = 118

_DATE_IN_NAME = re.compile(r"(20\d\d-\d\d-\d\d)")

_WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
_UNIT_DAYS = {"hour": 1.0 / 24.0, "day": 1.0, "week": 7.0}

#: T2's whole discriminator. `for` is what turns a duration into a span something PERSISTED
#: for, as against a rate ("three instances in three days"), a model parameter ("after three
#: weeks") or an offset ("predates it by two days"). See the module docstring for the measured
#: accept/reject counts that chose this over the wider net.
_PERSISTED_RE = re.compile(
    r"\bfor\s+(?:the\s+)?(?:(\d{1,3}(?:\.\d)?)|("
    + "|".join(_WORD_NUMBERS)
    + r"))\s+(hour|day|week)s?\b",
    re.I,
)

#: A wrong state, named. Deliberately states-not-events, because T1 already owns the event
#: vocabulary (`fc._COST_CONTEXT_RE`) and this term is about what stayed true, not what broke.
#: Both are accepted — a span that is inside T1's vocabulary is still a span.
_PERSISTED_CONTEXT_RE = re.compile(
    r"invalidat\w*|rebuil\w*|re-?run|re-?ran|rework\w*|redone|discard\w*|wasted|"
    r"unusable|serv(ed|ing)|spent|unguarded|undetected|unnoticed|\bsat\b|stale|"
    r"\bfalse\b|\bwrong\b|\bdown\b|\bopen\b|\bfrozen\b|\bblind\b|\bcontinuous\b|"
    r"\bmuted\b|\bdisarmed\b|\bunpublished\b|\bunwired\b",
    re.I,
)
_PERSISTED_WINDOW = 100

#: Unit names, printed everywhere a figure is. Three units exist so that no reader — and no
#: later renderer — can add them up without noticing they are adding hours to commits.
UNIT_HOURS = "recorded episode-hours"
UNIT_DAYS_PERSISTED = "persisted-days"
UNIT_COMMITS = "commits-on-top"

OPEN = "OPEN"
ACCEPTED = "ACCEPTED"
CLOSED = "CLOSED"
DECISIONS = (OPEN, ACCEPTED, CLOSED)

DISPOSITION_HEADING = "Disposition"
_DISPOSITION_HEADING_RE = re.compile(
    rf"^#{{1,6}}[ \t]+{DISPOSITION_HEADING}[ \t]*$", re.M
)
_ANY_HEADING_RE = re.compile(r"^#{1,6}[ \t]", re.M)
_FIELD_RE = {
    "decision": re.compile(r"\*\*Decision:\*\*\s*`?([A-Z_]+)`?"),
    "taken": re.compile(r"\*\*Taken:\*\*\s*`?(20\d\d-\d\d-\d\d)`?"),
    "at": re.compile(r"\*\*At:\*\*\s*(\d+)\s*instance"),
    "mechanism": re.compile(r"\*\*Mechanism:\*\*\s*`([^`]+)`"),
    "because": re.compile(r"\*\*Because:\*\*\s*(.+)"),
}


@dataclass(frozen=True)
class PersistedSpan:
    """One T2 figure: how long something stayed wrong, and the sentence that says so."""

    source: str
    days: float
    phrase: str
    verbatim: str


@dataclass(frozen=True)
class Disposition:
    """A recorded decision about a class, parsed from its register.

    `at_instances` is what makes ACCEPTED a decision rather than a mute: the count the
    decision was taken at is written down, so the decision can be shown to have been
    overtaken by evidence instead of quietly outliving it.
    """

    decision: str
    taken: str = ""
    at_instances: int | None = None
    mechanism: str = ""
    because: str = ""

    @property
    def is_decided(self) -> bool:
        return self.decision in (ACCEPTED, CLOSED)


def parse_disposition(text: str) -> Disposition | None:
    """The decision a class register records about itself, or None if it records none.

    Scoped to the `## Disposition` section for the same reason `finding_classes.
    declared_class_of` scopes its parse: the word ACCEPTED appearing in prose (this docstring
    included) is a mention, and a mention is not a decision.
    """
    heading = _DISPOSITION_HEADING_RE.search(text)
    if heading is None:
        return None
    section = text[heading.end():]
    following = _ANY_HEADING_RE.search(section)
    if following is not None:
        section = section[: following.start()]
    fields = {k: r.search(section) for k, r in _FIELD_RE.items()}
    if fields["decision"] is None:
        return None
    return Disposition(
        decision=fields["decision"].group(1),
        taken=fields["taken"].group(1) if fields["taken"] else "",
        at_instances=int(fields["at"].group(1)) if fields["at"] else None,
        mechanism=fields["mechanism"].group(1) if fields["mechanism"] else "",
        because=fields["because"].group(1).strip() if fields["because"] else "",
    )


def mechanism_resolves(mechanism: str, repo_root: Path | None = None) -> bool:
    """Whether a CLOSED disposition's named mechanism still exists.

    A path is checked on disk; anything else is treated as a dotted module name. Checked
    because a closure is the one thing here that turns a class OFF, and a closure pointing at
    a control that has since been renamed or deleted is a silencer wearing a repair's clothes
    — `stall_class_register`'s G2 guarantee, at the address where it matters most.
    """
    if not mechanism:
        return False
    root = Path(repo_root or REPO_ROOT)
    #: A mechanism may name a test as `path::test_name`; the file is what has to exist.
    candidate = mechanism.split("::", 1)[0]
    if (root / candidate).exists():
        return True
    import importlib.util

    try:
        return importlib.util.find_spec(candidate.replace("/", ".").removesuffix(".py")) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def persisted_spans(text: str, source: str) -> list[PersistedSpan]:
    """Every T2 span `text` records, with the sentence each came from."""
    out: list[PersistedSpan] = []
    text = fc._FENCE_RE.sub("", text)
    for match in _PERSISTED_RE.finditer(text):
        window = text[
            max(0, match.start() - _PERSISTED_WINDOW): match.end() + _PERSISTED_WINDOW
        ]
        if not (
            _PERSISTED_CONTEXT_RE.search(window)
            or fc._COST_CONTEXT_RE.search(window)
        ):
            continue
        amount = (
            float(match.group(1)) if match.group(1)
            else float(_WORD_NUMBERS[match.group(2).lower()])
        )
        out.append(
            PersistedSpan(
                source=source,
                days=amount * _UNIT_DAYS[match.group(3).lower()],
                phrase=" ".join(window.split()),
                verbatim=match.group(0),
            )
        )
    return out


def worst_persisted_per_instance(spans: list[PersistedSpan]) -> list[PersistedSpan]:
    """The single longest span each document records — one document, one figure.

    Same rule and same reason as `finding_classes.worst_per_instance`: a finding that states
    its span twice must not be billed twice.
    """
    best: dict[str, PersistedSpan] = {}
    for span in spans:
        current = best.get(span.source)
        if current is None or span.days > current.days:
            best[span.source] = span
    return list(best.values())


def _instance_dates(paths: list[Path]) -> list[dt.date]:
    """Each instance's date, from its filename. Undated instances are DROPPED, and that is
    reported by `dated` being smaller than the count rather than by a silent shrug — every
    finding in this corpus is named `..._YYYY-MM-DD.md`, so an undated one is an anomaly a
    reader should see rather than a case to absorb."""
    dates: list[dt.date] = []
    for path in paths:
        match = _DATE_IN_NAME.search(path.name)
        if match is None:
            continue
        try:
            dates.append(dt.date.fromisoformat(match.group(1)))
        except ValueError:
            continue
    return sorted(dates)


def _commits_between(start: dt.date, end: dt.date, repo_root: Path) -> int:
    """Commits landed in `[start, end)`. Zero on any git failure — T3 is an EXPOSURE figure,
    and an unavailable git must not manufacture exposure that was never observed. It cannot
    hide a debt either: T3 never decides whether a class is drawn, only how the drawn ones
    are ordered."""
    try:
        proc = subprocess.run(
            ["git", "rev-list", "--count", f"--since={start.isoformat()}",
             f"--until={end.isoformat()}", "HEAD"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=60, check=False,
        )
        return int(proc.stdout.strip() or 0)
    except (OSError, ValueError, subprocess.SubprocessError):
        return 0


@dataclass
class ClassDebt:
    """One class, everything it has cost, and what that entitles it to."""

    finding_class: fc.FindingClass
    instances: int = 0
    dated: int = 0
    measured_instances: int = 0
    recorded_hours: float = 0.0
    persisted_days: float = 0.0
    persisted: list[PersistedSpan] = field(default_factory=list)
    first: dt.date | None = None
    last: dt.date | None = None
    open_days: int = 0
    commits_on_top: int = 0
    same_day_pairs: int = 0
    recent_instances: int = 0
    #: Instances the lane guard refused consolidation. They COUNT toward this class (see
    #: `compute`) and are reported separately so a reader can see that the register's instance
    #: LIST is shorter than its instance COUNT, and why.
    out_of_lane: int = 0
    disposition: Disposition | None = None

    @property
    def class_id(self) -> str:
        return self.finding_class.id

    @property
    def still_accruing(self) -> bool:
        return self.recent_instances >= ACCRUAL_MIN_INSTANCES

    @property
    def measured_fraction(self) -> float:
        return self.measured_instances / self.instances if self.instances else 0.0

    def draw_verdict(self) -> tuple[bool, str]:
        """Whether this class is work right now, and the sentence saying why.

        The order of the tests is the argument. A broken CLOSED comes first because a closure
        that no longer resolves is worse than no closure — it is actively telling every reader
        the class is handled. An overtaken ACCEPTED comes next, because a decision that
        evidence has passed is the one thing a recorded decision is FOR. Only then does
        accrual decide, and only for a class nobody has decided anything about.
        """
        disposition = self.disposition
        if disposition is not None and disposition.decision == CLOSED:
            if not mechanism_resolves(disposition.mechanism):
                return True, (
                    f"CLOSED by `{disposition.mechanism}`, which does not resolve — a closure "
                    "whose mechanism has been renamed or deleted goes loud, never quiet"
                )
            return False, f"CLOSED by `{disposition.mechanism}` on {disposition.taken}"
        if disposition is not None and disposition.decision == ACCEPTED:
            at = disposition.at_instances
            if at is not None and self.instances >= at + REOPEN_AFTER_INSTANCES:
                return True, (
                    f"ACCEPTED on {disposition.taken} at {at} instances, now {self.instances} "
                    f"— {REOPEN_AFTER_INSTANCES} further instances is a class's worth of "
                    "evidence arriving after the decision, so the decision is re-opened"
                )
            if at is None:
                return True, (
                    f"ACCEPTED on {disposition.taken} with no instance count recorded — an "
                    "acceptance that does not say what it was accepted AT can never be shown "
                    "to have been overtaken, which makes it a mute rather than a decision"
                )
            return False, (
                f"ACCEPTED on {disposition.taken} at {at} instances "
                f"(re-opens at {at + REOPEN_AFTER_INSTANCES})"
            )
        if self.still_accruing:
            return True, (
                f"{self.recent_instances} instances in the last {ACCRUAL_WINDOW_DAYS} days "
                "and no recorded decision — still accruing"
            )
        return False, (
            f"{self.recent_instances} instance(s) in the last {ACCRUAL_WINDOW_DAYS} days — "
            "not accruing; a class that has stopped recurring is a limitation being lived "
            "with, and this module does not manufacture a decision nobody took"
        )

    @property
    def drawable(self) -> bool:
        return self.draw_verdict()[0]

    def order_key(self) -> tuple:
        """How accruing classes are ordered against each other.

        INSTANCES LEAD, and the reason is the coverage figure this module prints at the top:
        the count is measured for 100% of the population and every cost term is measured for
        15% of it. A rank led by a 15%-covered measure ranks classes by their MEASUREMENT
        HABIT rather than by their cost — which is `measurements_that_mirror` committed by the
        instrument that ranks it.

        It was written hours-first and that draft is why this comment exists: it put
        `controls_that_cannot_fail` (25 recorded hours, 4 persisted-days) above
        `no_caller_and_never_runs` (0 recorded hours, 14 persisted-days), because a
        lexicographic key over two units silently asserts that ANY quantity of the first beats
        any quantity of the second. That is adding hours to days with the addition hidden in a
        sort. The cost terms are kept as tie-breaks, where they order without being asked to
        commensurate.
        """
        return (
            -self.instances,
            -self.recorded_hours,
            -self.persisted_days,
            -self.commits_on_top,
            self.class_id,
        )

    def one_line(self) -> str:
        mark = "DRAW" if self.drawable else "----"
        return (
            f"{mark} {self.class_id:<32} n={self.instances:<4} "
            f"measured={self.measured_instances}/{self.instances:<4} "
            f"{self.recorded_hours:>7.1f}h {self.persisted_days:>6.2f}d "
            f"{self.commits_on_top:>6} commits  {self.same_day_pairs:>4} same-day pairs  "
            f"{('+%d out-of-lane  ' % self.out_of_lane) if self.out_of_lane else ''}"
            f"{self.draw_verdict()[1]}"
        )


def compute(
    root: Path | str = DEFAULT_STAGING_ROOT,
    *,
    today: dt.date | None = None,
    repo_root: Path | None = None,
) -> list[ClassDebt]:
    """Every class's debt, in draw order (accruing first, then by cost)."""
    root = Path(root)
    repo_root = Path(repo_root or REPO_ROOT)
    today = today or dt.date.today()
    out: list[ClassDebt] = []

    for class_id, membership in fc.derive_memberships(root).items():
        # OUT-OF-LANE INSTANCES COUNT TOWARD THE CLASS, and only consolidation is lane-scoped.
        #
        # THE DEFECT THIS FIXES, found the same day this module landed and by this module's own
        # output. `measurements_that_mirror` was recorded ACCEPTED at 7 instances on the grounds
        # that it had "stopped recurring" — 1 instance in the trailing week. By that evening it had
        # THREE more, all filed that day, all `W2_customer_generator` against an `H_harness`
        # register. `derive_memberships` correctly REFUSES to consolidate them (severity is
        # lane-scoped, and filing a W2 finding under H_harness would launder W2's blocker), and
        # this module then read the same-lane count and reported "not accruing" for a class that
        # had recurred three times in a day.
        #
        # The lane guard is right and stays. What was wrong was reading it as the population:
        # consolidation is a claim about SUPERSESSION, which must not cross a lane; accrual and
        # cost are claims about HOW OFTEN THE SHAPE HAPPENS, which have no lane. A class register
        # that cannot see its own class recurring one lane over is a control whose subject moved —
        # the shape this register exists to catalogue, committed by the instrument that ranks it.
        #
        # Applied here, this reverses the author's own ACCEPTED by that decision's own re-arm rule,
        # which is the mechanism working rather than a special case.
        paths = membership.instance_paths(root) + [
            p for p, _lane in membership.refused_out_of_lane
        ]
        debt = ClassDebt(finding_class=membership.finding_class,
                         instances=len(paths),
                         out_of_lane=len(membership.refused_out_of_lane))

        costs = fc.cost_for_members(paths, root)
        worst = fc.worst_per_instance(costs)
        debt.recorded_hours = sum(item.amount for item in worst)
        debt.measured_instances = len(worst)

        spans: list[PersistedSpan] = []
        for path in paths:
            if not path.exists():
                continue
            spans.extend(
                persisted_spans(
                    path.read_text(encoding="utf-8", errors="replace"), path.name
                )
            )
        debt.persisted = sorted(
            worst_persisted_per_instance(spans), key=lambda s: (-s.days, s.source)
        )
        debt.persisted_days = sum(span.days for span in debt.persisted)

        dates = _instance_dates(paths)
        debt.dated = len(dates)
        if dates:
            debt.first, debt.last = dates[0], dates[-1]
            debt.open_days = (today - dates[0]).days
            debt.recent_instances = sum(
                1 for d in dates if (today - d).days <= ACCRUAL_WINDOW_DAYS
            )
            by_day: dict[dt.date, int] = {}
            for d in dates:
                by_day[d] = by_day.get(d, 0) + 1
            debt.same_day_pairs = sum(n * (n - 1) // 2 for n in by_day.values() if n > 1)
            debt.commits_on_top = sum(
                _commits_between(dates[i], dates[i + 1], repo_root)
                for i in range(len(dates) - 1)
            )

        doc = class_document_path(membership.finding_class.document_name, root)
        if doc.exists():
            debt.disposition = parse_disposition(
                doc.read_text(encoding="utf-8", errors="replace")
            )

        out.append(debt)

    out.sort(key=lambda d: (not d.drawable, d.order_key()))
    return out


def drawable(
    root: Path | str = DEFAULT_STAGING_ROOT, *, today: dt.date | None = None
) -> list[ClassDebt]:
    """The classes that are work right now, in the order they should be served.

    This is the function `background/staging_rooms.work_queue` calls. It is kept trivially
    small and total — no exceptions escape `compute` that would not already have broken the
    draw — because a draw that cannot rank its work must still SEE it.
    """
    return [debt for debt in compute(root, today=today) if debt.drawable]


def floor_violations(debts: list[ClassDebt]) -> list[str]:
    """The dated population floor. A scan reports "no debt" identically whether the classes
    are clean or the subject has moved out from under it; this is what tells those apart."""
    out: list[str] = []
    if len(debts) < FLOOR_CLASSES:
        out.append(
            f"POPULATION FLOOR classes: {len(debts)}, floor {FLOOR_CLASSES} (2026-09-01). A "
            "register is never deleted, so a drop means this scan lost its subject."
        )
    total = sum(d.instances for d in debts)
    if total < FLOOR_INSTANCES:
        out.append(
            f"POPULATION FLOOR instances: {total}, floor {FLOOR_INSTANCES} (2026-09-01). "
            "Instances are archived, never unfiled, so a drop means membership derivation is "
            "reading a subject that has moved."
        )
    return out


def render(
    root: Path | str = DEFAULT_STAGING_ROOT, *, today: dt.date | None = None
) -> str:
    debts = compute(root, today=today)
    lines = ["CLASS DEBT — what each finding class has cost, and what it is owed in the draw",
             "=" * 100, ""]
    total_instances = sum(d.instances for d in debts)
    total_measured = sum(d.measured_instances for d in debts)
    lines.append(
        f"{total_instances} instances across {len(debts)} classes. "
        f"{total_measured} of them ({total_measured / total_instances:.0%}) record any "
        f"duration at all — every figure below is a FLOOR on that basis, never an estimate."
    )
    lines.append("")
    for debt in debts:
        lines.append(debt.one_line())
    lines.append("")
    lines.append(
        f"UNITS ARE NOT ADDED. {UNIT_HOURS} (h), {UNIT_DAYS_PERSISTED} (d) and "
        f"{UNIT_COMMITS} measure three different things. {UNIT_COMMITS} is ALSO not summable "
        "across classes: these classes were open simultaneously, so the same commit sits "
        "under several of them and a total would count the tree once per open class."
    )
    lines.append("")
    lines.append(
        "SAME-DAY PAIRS is where two instances of one class could have INTERACTED, and it is "
        "a count of opportunities, not a cost. The director's own example — eleven hours of "
        "outage from two same-day findings interacting — is not derivable from this corpus: "
        "each document records its own episode, nothing records the combined one, and a "
        "figure for the interaction would have to be invented. The pairs are printed so the "
        "gap has a size."
    )
    lines.append("")
    for debt in debts:
        if not debt.persisted:
            continue
        lines.append(f"{debt.class_id} — {UNIT_DAYS_PERSISTED}, traced:")
        for span in debt.persisted:
            lines.append(
                f"  {span.days:>6.2f}d [{span.verbatim}] {span.source}"
            )
            lines.append(f"          …{span.phrase[:150]}…")
        lines.append("")
    violations = floor_violations(debts)
    lines.append(f"Population floors: {len(violations)} violation(s)")
    for violation in violations:
        lines.append(f"  ! {violation}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(DEFAULT_STAGING_ROOT))
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero on a population-floor violation")
    args = parser.parse_args(argv)

    print(render(args.root))
    if args.check:
        return 1 if floor_violations(compute(args.root)) else 0
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/class_debt.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("class_debt")
    sys.exit(main())
