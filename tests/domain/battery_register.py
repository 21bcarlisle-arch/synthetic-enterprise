"""AO8 -- the purchased disqualification batteries, as addressable records.

The advisor scope briefs each end in a DISQUALIFICATION BATTERY: a numbered or
bulleted list of things that, if true of our treatment, mean the treatment is
incomplete. That judgement was bought from outside the code. Left as prose it
cannot fail, so it cannot tell us when the company drifts away from it.

This module is the SEAM between the prose and the suite. It does two separate
jobs, and keeping them separate is the whole design:

  1. `parse_battery_lines(brief)` reads the battery out of the BRIEF ITSELF.
     This is the INDEPENDENT ORACLE. It never reads the register.
  2. `load_register()` reads our dispositions out of `battery_register.yaml`.

`tests/domain/test_battery_register_integrity.py` puts (1) against (2). Because
the oracle derives from the source document rather than from the register, a
battery line cannot be quietly dropped, reworded, or marked done: the brief is
the authority and the register has to answer to it. If the two were derived from
the same place the control would be a tautology and would prove nothing (R15).

DISPOSITIONS -- every line carries exactly one:

  mechanised          A standing check runs with the suite. `check` names it as
                      `module::function` and integrity resolves it by IMPORT --
                      a name that does not resolve is a failure, so "mechanised"
                      cannot be a claim about a test that is not there.
  not_mechanisable    The line is a judgement no assertion can carry (e.g. "a
                      complete treatment answers WHY"). Requires `reason`.
  pending_capability  Testable in principle, but the capability it would test
                      does not exist yet. Requires `reason` naming the blocker.
                      This is a REPORTED GAP, not a pass.

The failure shape this file is built against is the one the atom's own origin
note names: *a battery line converted into a check that silently skips when its
data is absent is worse than leaving it as prose, because it reads as covered.*
So there is no "skip" disposition and no skipif in the battery tests -- absent
data must make a check FAIL, and integrity enforces that structurally.
"""
from __future__ import annotations

import importlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
REGISTER_PATH = Path(__file__).resolve().parent / "battery_register.yaml"

#: Where a brief may live. Briefs start in staging and are archived once
#: processed; resolution is by BASENAME across these roots so archiving a brief
#: never silently decouples it from the register. Fail-closed: a brief that
#: resolves nowhere raises, it does not yield an empty battery (an empty battery
#: would make the completeness check vacuously pass -- the exact fail-open shape
#: this module exists to prevent).
BRIEF_SEARCH_ROOTS = (
    ROOT / "docs" / "staging",
    ROOT / "docs" / "staging" / "done",
    ROOT / "docs" / "staging" / "in_progress",
    ROOT / "docs" / "domain_artefact_library" / "scope_briefs",
)

DISPOSITIONS = frozenset({"mechanised", "not_mechanisable", "pending_capability"})

#: A battery section starts at a heading containing this phrase...
_BATTERY_HEADING = re.compile(r"^#{1,6}\s.*disqualification battery", re.IGNORECASE)
#: ...and ends at the next heading of any level, or at the sources/attribution
#: trailer. Bounding the section EXPLICITLY matters: an unterminated scan would
#: swallow the rest of the document and turn every trailing paragraph into a
#: phantom battery line, which reads as extra coverage rather than as a parse
#: failure.
_SECTION_END = re.compile(r"^(#{1,6}\s|\*\*Sources:\*\*|—\s|--\s)")

#: `1. text` / `- text` / `- **B1 label:** text`
_NUMBERED = re.compile(r"^(\d+)\.\s+(.*)$")
_BULLET = re.compile(r"^[-*]\s+(.*)$")
_BOLD_ID = re.compile(r"^\*\*(B\d+)\b([^*]*)\*\*\s*(.*)$")


@dataclass(frozen=True)
class BatteryLine:
    """One disqualification line, as it appears in the brief."""

    brief: str
    ordinal: int
    label: str
    text: str


@dataclass(frozen=True)
class RegisterEntry:
    """Our disposition of one battery line."""

    id: str
    brief: str
    label: str
    text: str
    disposition: str
    check: Optional[str] = None
    reason: Optional[str] = None


def resolve_brief(basename: str) -> Path:
    """Locate a brief by basename. Raises rather than returning None."""
    for root in BRIEF_SEARCH_ROOTS:
        candidate = root / basename
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"scope brief {basename!r} not found under any of "
        f"{[str(r.relative_to(ROOT)) for r in BRIEF_SEARCH_ROOTS]}. "
        "The register cites it, so this is a broken reference, not an empty battery."
    )


def _battery_section(text: str) -> list[str]:
    """Return the raw lines of the disqualification-battery section."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if _BATTERY_HEADING.match(line):
            start = i + 1
            break
    if start is None:
        return []
    out: list[str] = []
    for line in lines[start:]:
        if _SECTION_END.match(line):
            break
        out.append(line)
    return out


def parse_battery_lines(basename: str) -> list[BatteryLine]:
    """THE INDEPENDENT ORACLE: read a brief's battery from the brief itself.

    Never consults the register. Handles both shapes the advisor uses -- the
    numbered `1. text` list and the `- **B1 label:** text` bullet list.
    """
    path = resolve_brief(basename)
    section = _battery_section(path.read_text(encoding="utf-8"))
    out: list[BatteryLine] = []
    for raw in section:
        stripped = raw.strip()
        if not stripped:
            continue
        label: Optional[str] = None
        body: Optional[str] = None

        m = _NUMBERED.match(stripped)
        if m:
            label, body = m.group(1), m.group(2)
        else:
            m = _BULLET.match(stripped)
            if m:
                inner = m.group(1).strip()
                bold = _BOLD_ID.match(inner)
                if bold:
                    # Keep the advisor's own short descriptor ("No contractless
                    # energy:") joined to the body -- it names what the line is
                    # FOR, and dropping it loses the point of the check.
                    label = bold.group(1)
                    body = f"{bold.group(2).strip()} {bold.group(3).strip()}".strip()
                else:
                    label, body = str(len(out) + 1), inner
        if body is None or label is None:
            # A continuation line of the previous item -- append, never invent
            # a new battery line out of a wrapped paragraph.
            if out:
                prev = out[-1]
                out[-1] = BatteryLine(
                    prev.brief, prev.ordinal, prev.label, f"{prev.text} {stripped}".strip()
                )
            continue
        out.append(
            BatteryLine(
                brief=basename,
                ordinal=len(out) + 1,
                label=label,
                text=_clean(body),
            )
        )
    return out


def _clean(text: str) -> str:
    """Strip markdown emphasis so register text compares to brief text stably."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return " ".join(text.split()).strip()


def load_register() -> list[RegisterEntry]:
    raw = yaml.safe_load(REGISTER_PATH.read_text(encoding="utf-8")) or {}
    entries = raw.get("entries") or []
    return [
        RegisterEntry(
            id=e["id"],
            brief=e["brief"],
            label=str(e["label"]),
            text=e["text"],
            disposition=e["disposition"],
            check=e.get("check"),
            reason=e.get("reason"),
        )
        for e in entries
    ]


def registered_briefs() -> list[str]:
    raw = yaml.safe_load(REGISTER_PATH.read_text(encoding="utf-8")) or {}
    return list(raw.get("briefs") or [])


def resolve_check(dotted: str):
    """Resolve `module::function` to the callable, raising if it is not there.

    "Mechanised" is a claim that something RUNS. This is what makes the claim
    falsifiable: a register entry naming a test that was renamed or deleted
    fails integrity instead of continuing to read as covered.
    """
    if "::" not in dotted:
        raise ValueError(f"check {dotted!r} must be 'module::function'")
    module_name, func_name = dotted.split("::", 1)
    module = importlib.import_module(module_name)
    if not hasattr(module, func_name):
        raise AttributeError(f"{module_name} has no test function {func_name!r}")
    return getattr(module, func_name)


def validate(entries: list[RegisterEntry], oracle: dict[str, list[BatteryLine]]) -> list[str]:
    """Return every problem with `entries` measured against `oracle`.

    Factored out of the test so the mutation suite can poison a register in
    memory and prove each rule FIRES on its own named defect. A control nobody
    has watched fail is not evidence (R15).
    """
    problems: list[str] = []

    # -- vacuity: an empty oracle would make every completeness rule below pass
    # over nothing. This is the fail-open shape that matters most here.
    total_oracle = sum(len(v) for v in oracle.values())
    if total_oracle == 0:
        problems.append("VACUOUS: the oracle parsed zero battery lines from the briefs")
    for brief, lines in oracle.items():
        if not lines:
            problems.append(f"VACUOUS: {brief} parsed to zero battery lines")

    by_id = {e.id: e for e in entries}
    if len(by_id) != len(entries):
        problems.append("duplicate id in register")

    # -- completeness: every line in every brief is dispositioned, verbatim
    oracle_ids: set[str] = set()
    for brief, lines in oracle.items():
        for line in lines:
            expected_id = f"{_slug_for(brief)}-{line.label}"
            oracle_ids.add(expected_id)
            entry = by_id.get(expected_id)
            if entry is None:
                problems.append(f"DROPPED: {expected_id} is in {brief} but not in the register")
                continue
            if entry.text != line.text:
                problems.append(
                    f"DRIFTED: {expected_id} text does not match the brief.\n"
                    f"  brief:    {line.text}\n"
                    f"  register: {entry.text}"
                )
    for entry in entries:
        if entry.id not in oracle_ids:
            problems.append(f"PHANTOM: {entry.id} is in the register but in no brief")

    # -- disposition discipline
    for entry in entries:
        if entry.disposition not in DISPOSITIONS:
            problems.append(f"{entry.id}: unknown disposition {entry.disposition!r}")
        elif entry.disposition == "mechanised":
            if not entry.check:
                problems.append(f"{entry.id}: mechanised with no check named")
            else:
                try:
                    resolve_check(entry.check)
                except Exception as exc:  # noqa: BLE001 -- any failure to resolve is the defect
                    problems.append(
                        f"UNBACKED: {entry.id} claims mechanised via {entry.check} "
                        f"but it does not resolve: {exc}"
                    )
        else:
            if not (entry.reason or "").strip():
                problems.append(
                    f"{entry.id}: disposition {entry.disposition} requires a reason "
                    "naming the blocker -- an unexplained gap reads as a decision"
                )
            elif len((entry.reason or "").split()) < 5:
                problems.append(f"{entry.id}: reason too thin to be a blocker: {entry.reason!r}")

    # -- at least one line must actually run, or this is prose with extra steps
    if not any(e.disposition == "mechanised" for e in entries):
        problems.append("VACUOUS: no battery line is mechanised -- nothing runs with the suite")

    return problems


#: brief basename -> register id prefix. Kept beside the parser rather than in
#: the builder so validate() can rebuild an expected id without importing tools/.
_SLUGS = {
    "CARBON": "CARB",
    "CFD_AND_ASSETS": "CFD",
    "CHANGE_OF_TENANCY": "COT",
    "ELECTRICITY": "ELEC",
    "GAS": "GAS",
    "INDUSTRY_BOUNDARY": "IND",
    "NONCOMMODITY_COST_STACK": "NCS",
    "PREPAYMENT_ESTATE": "PPM",
}


def _slug_for(basename: str) -> str:
    key = basename.replace("ADVISOR_SCOPE_BRIEF_", "").rsplit("_", 1)[0]
    if key not in _SLUGS:
        raise KeyError(f"no id prefix registered for brief {basename!r}")
    return _SLUGS[key]


def build_oracle(briefs: Iterable[str]) -> dict[str, list[BatteryLine]]:
    return {brief: parse_battery_lines(brief) for brief in briefs}


def by_disposition(entries: Iterable[RegisterEntry]) -> dict[str, list[RegisterEntry]]:
    out: dict[str, list[RegisterEntry]] = {d: [] for d in DISPOSITIONS}
    for e in entries:
        out.setdefault(e.disposition, []).append(e)
    return out
