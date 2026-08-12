"""Severity + lane parsing for staging findings — atom `OPS9_finding_severity_field`.

WHY THIS EXISTS (DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12, clause 2):
a staging root of ~120 undifferentiated findings cannot be drawn against. The count of
documents measures the rate of self-scrutiny, not the state of the project. Severity is
the gate instead of the count — and a severity a machine cannot read is prose, so the
ruling's mechanisms (OPS11's lane-scoped refusal, OPS12's blocker precedence) all read
THIS parser rather than a second hand-kept list that could disagree with it.

THE THREE VALUES, verbatim from the ruling:
  BLOCKING — a control or instrument in this area is untrustworthy, or a published figure
             may be wrong. New level-raises in the affected LANE are refused until it is
             repaired, or until the limitation is explicitly recorded and accepted.
  LATENT   — real defect; does not invalidate anything published or any control's verdict.
  RECORDED — known limitation, accepted, no work owed.

THE HEADER, one line inside the document's header block:

    **Severity:** LATENT · **Lane:** H_harness

WHY THE LANE IS PART OF THE PARSE, not a separate lookup: clause 2's refusal is
lane-scoped ("progress in every other lane continues untouched"). A severity without a
lane cannot be acted on — nothing downstream can tell which lane to refuse — so a header
carrying a severity and no lane is UNCLASSIFIED, not a half-answer.

FAIL-CLOSED, deliberately (R15 killer pattern 2, FAIL-OPEN — passes on missing/malformed
input): an absent, duplicated-into-prose or unparseable header reads as UNCLASSIFIED and
is SURFACED. It is never silently defaulted to LATENT. Defaulting to LATENT would be
exactly the anti-pattern clause 2 names — deciding one's own finding is not BLOCKING in
order to keep a lane open — implemented as an accident instead of a decision.

WHY THE FIRST OCCURRENCE WINS AND PROSE DOES NOT RESCUE IT: several findings written
before this atom used `**Severity:** this is the mechanism that kept ...` as a prose
sentence. Scanning past a malformed occurrence to find a well-formed one further down
would make the parser fail OPEN on precisely the documents most likely to be
mis-headered. The first `**Severity:**` in the header block IS the header; if its value
is not one of the three tokens, the document is unclassified and says so.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STAGING_ROOT = REPO_ROOT / "docs" / "staging"

BLOCKING = "BLOCKING"
LATENT = "LATENT"
RECORDED = "RECORDED"
UNCLASSIFIED = "UNCLASSIFIED"

#: The three values the ruling defines. UNCLASSIFIED is NOT one of them — it is the
#: fail-closed answer, reported separately so it can never be mistaken for a decision.
SEVERITIES = (BLOCKING, LATENT, RECORDED)

#: Lane vocabulary. HARD-CODED on purpose: reading `docs/design/maturity_map.yaml` at
#: import time would make every importer of this module fail when that live record is
#: mid-write (the import-time-constant-from-a-live-record class, already filed against
#: this project). Drift is caught by a TEST that compares this tuple with the map, which
#: is where a vocabulary disagreement belongs — visible, not fatal.
LANES = (
    "A_strategy_governance",
    "B_commercial",
    "C_customer_ops",
    "D_billing_metering",
    "E_finance_treasury",
    "F_risk_compliance",
    "G_data_learning",
    "H_harness",
    "W1_market_weather",
    "W2_customer_generator",
    "W3_industry_systems",
    "W4_the_wall",
    "W5_banking_payment_rails",
)

#: Machine-generated DOORBELLS, excluded from the classified population by exact prefix.
#: `run_complete_*`/`run_pending_*` are written by the auto-processor on every sim run and
#: archived minutes later; `from_rich_*` is the director's own inbound message. None of the
#: three is an authored finding, and requiring a severity on them would make the
#: zero-unclassified control flap red on the ordinary operation of the machine — an alarm
#: that fires on normal behaviour is one nobody reads. The list is EXACT-PREFIX and short
#: on purpose: it is a population boundary, and a boundary wide enough to hide a finding
#: behind would be the fail-open shape this module exists to refuse.
DOORBELL_PREFIXES = ("run_complete_", "run_pending_", "from_rich_")

#: A header line must sit in the document's header block — the prose before the first
#: `## ` section, and never more than this many lines in. A severity buried in §7 is not
#: a header, and treating it as one would let a document be classified by a sentence its
#: own reader would never see.
HEADER_BLOCK_MAX_LINES = 40

_SEVERITY_RE = re.compile(r"\*\*Severity:?\*\*:?\s*(?P<value>\S+)")
_LANE_RE = re.compile(r"\*\*Lane:?\*\*:?\s*`?(?P<value>[A-Za-z0-9_]+)`?")

#: Phrases whose plain meaning is "an instrument, a control, or a published figure in
#: this area is wrong". Clause 2: such a finding is BLOCKING BY CONSTRUCTION. These
#: patterns do not classify anything — they NAME documents whose own text says one thing
#: and whose header says another, which is exit criterion 4.
_BY_CONSTRUCTION_PATTERNS = (
    re.compile(r"\bpublished (?:figure|figures|number|numbers)\b[^.\n]{0,90}"
               r"\b(?:wrong|incorrect|overstat\w*|understat\w*|invalid\w*)", re.I),
    re.compile(r"\b(?:instrument|control|gate|check|oracle|measure|metric)\b[^.\n]{0,90}"
               r"\b(?:is|was|are|were)\s+(?:lying|untrustworthy|wrong|broken)", re.I),
    re.compile(r"\b(?:we|it) (?:published|publish) (?:a )?wrong\b", re.I),
    re.compile(r"\bcannot be trusted\b", re.I),
)

#: The namer stands down on a document whose header block says the defect is discharged.
#: These are not a loophole — they are clause 2's OWN two releases ("until it is repaired,
#: or until the limitation is explicitly recorded and accepted"). The anti-loophole is the
#: SCOPE: the word must appear in the HEADER BLOCK, where the next reader meets it, never
#: in a retrospective paragraph forty lines down that says a similar thing was fixed once.
_REPAIRED_RE = re.compile(
    r"\b(?:FIXED|CLOSED|REPAIRED|repaired|landed|relieved|CLEARED|cleared"
    r"|DISCHARGED|discharged|accepted)\b"
)


@dataclass(frozen=True)
class FindingSeverity:
    """One document's classification. `severity` is UNCLASSIFIED unless BOTH halves parse."""

    path: Path
    severity: str
    lane: str | None
    reason: str | None = None

    @property
    def is_classified(self) -> bool:
        return self.severity in SEVERITIES

    @property
    def is_blocking(self) -> bool:
        return self.severity == BLOCKING

    def describe(self) -> str:
        tail = f" ({self.reason})" if self.reason else ""
        return f"{self.severity:<12} {self.lane or '-':<24} {self.path.name}{tail}"


def header_block(text: str) -> str:
    """The prose before the first `## ` section, capped at HEADER_BLOCK_MAX_LINES."""
    lines: list[str] = []
    for line in text.splitlines()[:HEADER_BLOCK_MAX_LINES]:
        if line.startswith("## "):
            break
        lines.append(line)
    return "\n".join(lines)


def parse_severity_text(text: str, path: Path | None = None) -> FindingSeverity:
    """Parse a severity header out of `text`. Never raises; never defaults to a severity."""
    where = path or Path("<text>")
    block = header_block(text)

    severity_match = _SEVERITY_RE.search(block)
    if severity_match is None:
        return FindingSeverity(where, UNCLASSIFIED, None, "no severity header")

    raw = severity_match.group("value").strip().strip("`*_.,:;")
    value = raw.upper()
    if value not in SEVERITIES:
        return FindingSeverity(
            where, UNCLASSIFIED, None, f"severity value not one of {'/'.join(SEVERITIES)}: {raw!r}"
        )

    lane_match = _LANE_RE.search(block)
    if lane_match is None:
        return FindingSeverity(where, UNCLASSIFIED, None, "severity present, lane missing")

    lane = lane_match.group("value").strip()
    if lane not in LANES:
        return FindingSeverity(where, UNCLASSIFIED, None, f"lane not a known lane: {lane!r}")

    return FindingSeverity(where, value, lane)


def parse_severity_file(path: Path) -> FindingSeverity:
    """Parse one file. An unreadable file is UNCLASSIFIED — an unavailable check is a
    FAILED check (R15 killer pattern 3), not a pass."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return FindingSeverity(path, UNCLASSIFIED, None, f"unreadable: {exc.__class__.__name__}")
    return parse_severity_text(text, path)


def scan_staging_root(root: Path | str = DEFAULT_STAGING_ROOT) -> list[FindingSeverity]:
    """Classify every `*.md` in the staging ROOT, counted FROM THE FILESYSTEM.

    Exit criterion 2 of the atom: the population is the glob, never a hand-kept list —
    a list is what lets a document be complete by being forgotten. Subdirectories
    (`done/`, `in_progress/`) are deliberately out of scope: `done/` is the archive and
    `in_progress/` is a separate build queue with its own doorbell.
    """
    return [parse_severity_file(p) for p in classifiable_documents(root)]


def classifiable_documents(root: Path | str = DEFAULT_STAGING_ROOT) -> list[Path]:
    """Every `*.md` in the staging root that is not a machine-generated doorbell."""
    return [
        p for p in sorted(Path(root).glob("*.md"))
        if not p.name.startswith(DOORBELL_PREFIXES)
    ]


def unclassified(results: list[FindingSeverity]) -> list[FindingSeverity]:
    return [r for r in results if not r.is_classified]


def blocking_by_lane(results: list[FindingSeverity]) -> dict[str, list[FindingSeverity]]:
    """BLOCKING findings grouped by lane — the input OPS11/OPS12 read."""
    out: dict[str, list[FindingSeverity]] = {}
    for r in results:
        if r.is_blocking and r.lane:
            out.setdefault(r.lane, []).append(r)
    return out


def by_construction_evidence(text: str) -> list[str]:
    """The phrases in `text` that say an instrument/control/published figure is wrong."""
    return [m.group(0).strip() for pattern in _BY_CONSTRUCTION_PATTERNS
            for m in pattern.finditer(text)]


def by_construction_violations(
    root: Path | str = DEFAULT_STAGING_ROOT,
) -> list[tuple[FindingSeverity, str]]:
    """Documents whose own text says an instrument is wrong, classified anything but
    BLOCKING (exit criterion 4). Returns (classification, first matched phrase).

    This NAMES; it does not classify. A named document is either mis-headered or its
    header block should say what repaired it — both are answerable, and both are the
    point: the rule is checkable rather than merely written down.
    """
    violations: list[tuple[FindingSeverity, str]] = []
    for path in classifiable_documents(root):
        result = parse_severity_file(path)
        if result.severity == BLOCKING:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        block = header_block(text)
        if _REPAIRED_RE.search(block):
            continue
        evidence = by_construction_evidence(text)
        if evidence:
            violations.append((result, evidence[0]))
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(DEFAULT_STAGING_ROOT))
    parser.add_argument("--list", action="store_true", help="print every document")
    parser.add_argument(
        "--by-construction", action="store_true",
        help="name non-BLOCKING documents whose own text says an instrument is wrong",
    )
    args = parser.parse_args(argv)

    results = scan_staging_root(args.root)
    counts = {value: sum(1 for r in results if r.severity == value) for value in SEVERITIES}
    open_ = unclassified(results)

    if args.list:
        for r in results:
            print(r.describe())

    print(f"documents (from filesystem): {len(results)}")
    for value in SEVERITIES:
        print(f"  {value:<12} {counts[value]}")
    print(f"  {UNCLASSIFIED:<12} {len(open_)}")

    for lane, found in sorted(blocking_by_lane(results).items()):
        print(f"BLOCKING lane {lane}: {', '.join(f.path.name for f in found)}")

    if args.by_construction:
        for result, evidence in by_construction_violations(args.root):
            print(f"BY-CONSTRUCTION {result.severity} {result.path.name}: {evidence[:110]}")

    for r in open_:
        print(f"UNCLASSIFIED {r.path.name}: {r.reason}")
    return 1 if open_ else 0


if __name__ == "__main__":
    sys.exit(main())
