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
import subprocess
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

#: A DENIAL is not a claim. The patterns above are substring regexes with no grammar, so a
#: document stating that it does NOT say a figure is wrong was named as saying it —
#: observed on `WORKER_FINDING_A_MUTATION_THAT_PATCHES_BOTH_SIDES_OF_ITS_SEAM_2026-08-12`
#: ("Not a claim that any published figure is wrong: no gap value ... depends on either
#: control"). Two things keep this guard from becoming the fail-open hole it closes:
#:   * the SHAPE is tight — an explicit denial OF A CLAIM, not the word "not". A sentence
#:     that merely contains a negation still gets named.
#:   * the SCOPE is one sentence, and only the part of it BEFORE the phrase. A denial does
#:     not cover the sentence after it.
#: HONEST LIMIT: a denial expressed any other way (across two sentences, rhetorically,
#: "far from claiming …") is still named. That is the deliberate direction — a false name
#: is answerable in one line, a missed one is the defect this instrument exists to catch.
_DENIAL_RE = re.compile(
    r"\b(?:not|never)\s+(?:a\s+|an\s+|the\s+)?(?:claim|assertion|statement)\b"
    r"|\bno\s+claim\b"
    r"|\b(?:do|does|did|is|are|was|were|am)\s+not\s+(?:claim|assert|say|state|argue)\w*\b"
    r"|\b(?:doesn't|don't|isn't|aren't|didn't)\s+(?:claim|assert|say|state|argue)\w*\b",
    re.I,
)

#: THE DISCHARGE FIELD, 2026-08-12 (rung-1c draw on lane `H_harness`, 14 live blockers).
#:
#: WHY IT EXISTS: a severity header states the state the author FOUND, and nothing ever
#: re-read it. Eight of those fourteen blockers were Expert-Hour reports that repaired
#: their own defect inside the same document ("Mechanised", "R15 both ways", "no published
#: figure moved") — the instrument named as untrustworthy was trustworthy again before the
#: document was saved. Clause 2's release ("until it is repaired, or until the limitation
#: is explicitly recorded and accepted") had no machine-readable form, so a lane's blocker
#: set could only ever GROW: the more honestly an atom audited itself, the more completely
#: it froze twelve other atoms' lane.
#:
#: WHY IT IS NOT `_REPAIRED_RE`: that pattern releases on the word "landed" appearing
#: anywhere in a forty-line header — and "the by-construction gate is silenced by an
#: ordinary word" is already a filed finding of this project against exactly that shape.
#: A release read by the same loose pattern would be the same defect with higher stakes.
#: So the discharge is STRUCTURED and its evidence is CHECKED against the filesystem.
#:
#: THE FORM, one line in the header block:
#:
#:     **Discharged:** `tests/x/test_y.py::test_z`, `tools/y.py` — one line saying why
#:
#: THE RULE, fail-closed at every step (R15 killer pattern 2):
#:   * at least one artefact must be a TEST NODE (`<file>::<name>`) whose file exists AND
#:     whose text contains that node name. A discharge is a claim that a defect can no
#:     longer recur; the only evidence of that shape this project accepts is a named,
#:     runnable falsifier. A discharge naming only prose or only a source file proves the
#:     author typed a path, which is what a vacuous control looks like.
#:   * EVERY named artefact must exist. Any missing one voids the whole discharge.
#:   * a field that is present and does not satisfy this does NOT release the finding: the
#:     severity stands, and the document is surfaced by `false_discharges()`. A malformed
#:     release that silently released would be strictly worse than no release at all.
#:
#: WHAT IT DOES NOT PROVE, stated because an overclaimed control is the class above: it
#: proves a named falsifier EXISTS IN THE INDEX and is addressable, never that the
#: falsifier is a good one or that running it passes. Reviewing the cited test is still a
#: human act.
#:
#: WHICH TREE THE EVIDENCE IS READ FROM, 2026-08-18, and it is the whole point of
#: `_index_files`/`_index_blob` below
#: (`WORKER_FINDING_THE_DISCHARGE_RELEASE_READS_THE_NODE_FROM_THE_WORKING_TREE_AND_ITS_CONTROL_READS_ONLY_THE_FILE_2026-08-18`):
#: this check used to resolve both the file and the node against `repo_root` on disk. That
#: is R15 killer pattern 1, TAUTOLOGY — the author's working tree is the ONE tree
#: guaranteed to contain the work whose absence the check is about, so a discharge citing
#: a long-committed test file and a node that exists only in the author's editor was
#: validated, released to RECORDED, and passed clean by the `tests/architecture/` control
#: built to catch exactly this. Measured then: 195 node-bearing citations across 82
#: committed records, 15 absent from the index, 10 of them invisible to every control
#: because the FILE was committed and only the NODE was not.
#:
#: THE INDEX, not HEAD and not the disk. At pre-commit time the honest question is "will
#: the commit about to be made contain this", and that is the index — a record and its
#: falsifier `git add`ed together are legitimately present. Post-commit the index matches
#: HEAD and the two readings coincide. The cost is real and intended: a discharge does not
#: release until its falsifier is STAGED, which is the same instant the claim becomes true
#: for anyone else.
_DISCHARGED_RE = re.compile(r"\*\*Discharged:?\*\*:?\s*(?P<value>[^\n]+)")
_ARTEFACT_RE = re.compile(r"`([^`]+)`")

#: THE CONTINUATION RULE, 2026-08-18 (§4 of the same finding). `_DISCHARGED_RE` matches one
#: line. A real discharge naming six falsifiers across six lines was therefore parsed as
#: naming ONE: the release still fired on the first, and five sixths of the claim — including
#: any artefact that did not exist — was outside the checked claim entirely. Silently reading
#: one of six is strictly worse than either parsing all six or refusing the shape.
#:
#: The rule is deliberately narrow, because the alternative (swallow following lines until a
#: blank) would pull the author's prose reason into the artefact list and turn every
#: backticked symbol in it into a claimed path: A LINE THAT ENDS IN A COMMA IS CONTINUED BY
#: THE NEXT ONE. That is the shape a list of artefacts actually has, it is what both
#: multi-line discharges in the corpus use, and a reason line (which ends in a word, a stop
#: or a dash) terminates the value without special-casing.
_CONTINUES = ","


def _discharge_claim(block: str) -> str | None:
    """The document's whole `**Discharged:**` value, continuation lines included."""
    match = _DISCHARGED_RE.search(block)
    if match is None:
        return None
    lines = block[match.start("value"):].splitlines()
    value = [lines[0]]
    for line in lines[1:]:
        if not value[-1].rstrip().endswith(_CONTINUES):
            break
        value.append(line)
    return "\n".join(value)


#: Cached per (root, index stamp): the stamp changes on every `git add`, so a long-lived
#: supervisor process cannot answer from a stale index, and a tick that classifies ~120
#: documents still pays one subprocess rather than one per citation.
_INDEX_FILES_CACHE: dict[tuple[str, int, int], frozenset[str]] = {}
_INDEX_BLOB_CACHE: dict[tuple[str, int, int, str], str | None] = {}


def _index_stamp(root: Path) -> tuple[int, int] | None:
    """(mtime_ns, size) of the index backing `root`, or None when there is no readable one.

    Handles the linked-worktree case (`.git` is a FILE naming the real git dir) because the
    pre-commit gate builds the would-be tree in exactly one of those.
    """
    dot = root / ".git"
    index = dot / "index"
    if dot.is_file():
        try:
            pointer = dot.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            return None
        if not pointer.startswith("gitdir:"):
            return None
        gitdir = Path(pointer.split(":", 1)[1].strip())
        index = (gitdir if gitdir.is_absolute() else (root / gitdir)) / "index"
    try:
        st = index.stat()
    except OSError:
        return None
    return (st.st_mtime_ns, st.st_size)


def _git(root: Path, *args: str) -> str | None:
    """git stdout, or None for EVERY failure mode. None means "cannot answer", never "no"."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout if result.returncode == 0 else None


def _index_files(root: Path) -> frozenset[str] | None:
    """Every path the index carries, or None when the index cannot be read.

    R15 killer pattern 3, FAIL-SILENT: git missing, `root` not a work tree, or an index that
    lists NOTHING all return None and the caller REFUSES the discharge. An empty set would
    read as "the repository contains nothing", which is a verdict this function has no
    evidence for.
    """
    stamp = _index_stamp(root)
    key = (str(root), *stamp) if stamp else None
    if key is not None and key in _INDEX_FILES_CACHE:
        return _INDEX_FILES_CACHE[key]
    out = _git(root, "ls-files", "-z")
    if out is None:
        return None
    files = frozenset(p for p in out.split("\0") if p)
    if not files:
        return None
    if key is not None:
        _INDEX_FILES_CACHE[key] = files
    return files


def _index_blob(root: Path, relative: str) -> str | None:
    """The file's text AS THE INDEX HAS IT, or None when it cannot be read."""
    stamp = _index_stamp(root)
    key = (str(root), *stamp, relative) if stamp else None
    if key is not None and key in _INDEX_BLOB_CACHE:
        return _INDEX_BLOB_CACHE[key]
    blob = _git(root, "show", f":{relative}")
    if key is not None:
        _INDEX_BLOB_CACHE[key] = blob
    return blob

#: THE EXONERATION FIELD, 2026-08-12. Full rationale on `parse_exoneration` below. Note it is
#: NOT a second discharge: a discharge releases a SEVERITY (the defect can no longer recur);
#: this releases a CITATION (this document is not the cause of THIS red) and leaves the
#: severity exactly where the author put it. The census finding that provoked it is a live,
#: open, LATENT backlog item and stays one — the defect was that answering the draw made the
#: next draw worse, not that the answer was wrong.
_NOT_A_SUSPECT_RE = re.compile(r"\*\*Not-a-suspect-for:?\*\*:?\s*(?P<value>[^\n]+)")


@dataclass(frozen=True)
class Discharge:
    """One document's discharge claim, already checked against the filesystem.

    `released` is True only when the claim is well-formed AND every artefact it names
    exists AND at least one of them is a test node that its file actually defines.
    """

    artefacts: tuple[str, ...]
    released: bool
    reason: str

    def describe(self) -> str:
        return f"{'RELEASED' if self.released else 'REFUSED '} {self.reason}"


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


def parse_discharge(text: str, repo_root: Path | str = REPO_ROOT) -> Discharge | None:
    """The document's `**Discharged:**` claim, CHECKED — or None when it makes no claim.

    Never raises and never guesses: an artefact the index does not carry, a node name the
    index's copy of its file does not define, or a claim with no test node at all all return
    `released=False` WITH the reason, so the refusal is reportable rather than a silent
    non-event. The evidence is read from the INDEX — see `_DISCHARGED_RE` above for why the
    working tree is the one tree that cannot be asked.
    """
    claim = _discharge_claim(header_block(text))
    if claim is None:
        return None

    root = Path(repo_root)
    artefacts = tuple(a.strip() for a in _ARTEFACT_RE.findall(claim) if a.strip())
    if not artefacts:
        return Discharge((), False, "discharge names no artefact in backticks")

    tracked = _index_files(root)
    if tracked is None:
        return Discharge(
            artefacts, False,
            "the index cannot be read, so this claim cannot be checked — an unavailable "
            "check is a FAILED check (R15), never a release",
        )

    missing: list[str] = []
    unstaged: list[str] = []
    nodes_ok: list[str] = []
    nodes_bad: list[str] = []
    for artefact in artefacts:
        file_part, _, node = artefact.partition("::")
        if file_part not in tracked:
            (unstaged if (root / file_part).exists() else missing).append(artefact)
            continue
        if not node:
            continue
        blob = _index_blob(root, file_part)
        (nodes_ok if (blob is not None and node in blob) else nodes_bad).append(artefact)

    if missing:
        return Discharge(artefacts, False, f"artefact does not exist: {', '.join(missing)}")
    if unstaged:
        return Discharge(
            artefacts, False,
            "artefact does not exist in the index — it is on this disk only, so no clone "
            f"can run it; `git add` it in the commit that carries this claim: {', '.join(unstaged)}",
        )
    if nodes_bad:
        return Discharge(
            artefacts, False,
            "the index's copy of the file does not define the node (a node that exists only "
            f"in the working tree is not a landed falsifier): {', '.join(nodes_bad)}",
        )
    if not nodes_ok:
        return Discharge(
            artefacts,
            False,
            "discharge names no test node (`file::name`) — a release needs a named falsifier",
        )
    return Discharge(artefacts, True, f"discharged by {', '.join(nodes_ok)}")


def _is_test_file(artefact: str) -> bool:
    """A path this project would recognise as a pytest module. The exoneration below is a
    claim about ONE RED, and a red is identified by its blocking TEST — accepting a module
    path would let a document exonerate itself against a whole subsystem in one line."""
    name = Path(artefact.partition("::")[0]).name
    return name.startswith("test_") and name.endswith(".py")


@dataclass(frozen=True)
class Exoneration:
    """One document's `**Not-a-suspect-for:**` claim, already checked against the filesystem.

    `valid` is True only when the claim is well-formed AND every path it names is an
    existing TEST file. `covers()` is the second half: valid alone suppresses nothing.
    """

    artefacts: tuple[str, ...]
    valid: bool
    reason: str

    def covers(self, test_files) -> bool:
        """True only when this claim answers EVERY blocking test of the red in hand.

        Both halves are the blanket-opt-out guard. Naming ANY of the red's tests rather
        than ALL of them would let a one-line field mute a document across reds it never
        examined; covering the EMPTY trail would exonerate every document against every
        red at once, which is the same mute button reached from the other side."""
        if not self.valid:
            return False
        wanted = {str(t).strip() for t in (test_files or []) if str(t).strip()}
        if not wanted:
            return False
        named = {a.partition("::")[0].strip() for a in self.artefacts}
        return wanted <= named


def parse_exoneration(text: str, repo_root: Path | str = REPO_ROOT) -> Exoneration | None:
    """The document's `**Not-a-suspect-for:**` claim, CHECKED — or None when it makes none.

    WHY THIS FIELD EXISTS (2026-08-12, RUNG-1c BLOCKING draw, lane `H_harness`):
    `process_run_complete.linked_findings` links a staged finding to a publish wedge by
    LEXICAL CO-OCCURRENCE with the red's blame trail. An accusation and a refutation are
    the same tokens, so a document that correctly denies being the cause — which it can
    only do by NAMING the cause — scores as a BETTER suspect than one that says nothing.
    Observed: re-freezing one finding with provenance took it from 2 needle hits to 7, and
    it was re-cited verbatim to the next priority-zero draw. The RUNG-1 draw offers two
    dispositions and the citation could observe exactly one: fix-and-archive clears it;
    "re-freeze with provenance" is by construction a document that STAYS in the scanned
    root, so it could never clear it. R11's orphan transition — a release whose effect is
    nothing, on a channel with no other release. This field is that release.

    THE FORM, one line in the header block:

        **Not-a-suspect-for:** `tests/background/test_x.py` — one line saying why

    THE RULE, fail-closed at every step (R15 killer pattern 2, FAIL-OPEN):
      * every named path must be a TEST file (`test_*.py`) that EXISTS. A missing path —
        a typo, or a test since deleted — voids the whole claim and the document stays a
        suspect. A release that fired on unverifiable evidence would be strictly worse
        than no release, because it would hide a real cause behind a plausible sentence.
      * the claim must sit in the HEADER BLOCK, so a sentence buried in §4 prose cannot
        suppress a citation the reader never sees.
      * suppression additionally requires `covers()` — the claim must name EVERY blocking
        test of the red in hand. Exonerating for test A does nothing when the red is B.

    WHAT IT DOES NOT PROVE, stated because an overclaimed control is a filed class here: it
    proves the author named a specific, existing test and staked the document's citation on
    it. It does not prove the denial is correct. Reviewing that is still a human act — the
    field's contribution is that the denial is now READABLE by the instrument it answers.
    """
    match = _NOT_A_SUSPECT_RE.search(header_block(text))
    if match is None:
        return None

    root = Path(repo_root)
    artefacts = tuple(a.strip() for a in _ARTEFACT_RE.findall(match.group("value")) if a.strip())
    if not artefacts:
        return Exoneration((), False, "exoneration names no artefact in backticks")

    non_tests = [a for a in artefacts if not _is_test_file(a)]
    if non_tests:
        return Exoneration(
            artefacts, False,
            "exoneration must name a blocking TEST (`test_*.py`), not: " + ", ".join(non_tests),
        )
    missing = [a for a in artefacts if not (root / a.partition('::')[0]).is_file()]
    if missing:
        return Exoneration(artefacts, False, f"artefact does not exist: {', '.join(missing)}")
    return Exoneration(artefacts, True, f"not a suspect for {', '.join(artefacts)}")


def parse_severity_file(path: Path, repo_root: Path | str = REPO_ROOT) -> FindingSeverity:
    """Parse one file. An unreadable file is UNCLASSIFIED — an unavailable check is a
    FAILED check (R15 killer pattern 3), not a pass.

    A VALID discharge (see `_DISCHARGED_RE`) reads the document down to RECORDED — clause
    2's own release, made machine-readable. An INVALID one leaves the severity exactly
    where the header put it and is surfaced by `false_discharges()`.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return FindingSeverity(path, UNCLASSIFIED, None, f"unreadable: {exc.__class__.__name__}")

    parsed = parse_severity_text(text, path)
    if not parsed.is_classified or parsed.severity == RECORDED:
        return parsed
    discharge = parse_discharge(text, repo_root)
    if discharge is None or not discharge.released:
        return parsed
    return FindingSeverity(path, RECORDED, parsed.lane, discharge.reason)


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


def false_discharges(
    root: Path | str = DEFAULT_STAGING_ROOT, repo_root: Path | str = REPO_ROOT
) -> list[tuple[Path, Discharge]]:
    """Documents that CLAIM a discharge the filesystem refuses.

    This is the half that stops the field being a loophole: a release that does not
    release must be LOUD, because the author who wrote it believes the finding is closed
    and will not look again. Silence here would turn every typo into a clean lane.
    """
    out: list[tuple[Path, Discharge]] = []
    for path in classifiable_documents(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        discharge = parse_discharge(text, repo_root)
        if discharge is not None and not discharge.released:
            out.append((path, discharge))
    return out


def _is_denied(text: str, start: int) -> bool:
    """True when the phrase at `start` sits inside an explicit denial of the claim.

    The sentence is the run back to the previous `.` or newline — the same boundary the
    patterns themselves respect (`[^.\\n]{0,90}`), so evidence and denial are read at one
    scale rather than two.
    """
    cut = max(text.rfind(".", 0, start), text.rfind("\n", 0, start))
    return _DENIAL_RE.search(text[cut + 1:start]) is not None


def by_construction_evidence(text: str) -> list[str]:
    """The phrases in `text` that say an instrument/control/published figure is wrong.

    A phrase inside its own denial is not one of them (see `_DENIAL_RE`).
    """
    return [m.group(0).strip()
            for pattern in _BY_CONSTRUCTION_PATTERNS
            for m in pattern.finditer(text)
            if not _is_denied(text, m.start())]


def by_construction_violations(
    root: Path | str = DEFAULT_STAGING_ROOT, repo_root: Path | str = REPO_ROOT
) -> list[tuple[FindingSeverity, str]]:
    """Documents whose own text says an instrument is wrong, classified anything but
    BLOCKING (exit criterion 4). Returns (classification, first matched phrase).

    This NAMES; it does not classify. A named document is either mis-headered or owes a
    `**Discharged:**` field saying what repaired it — both are answerable, and both are
    the point: the rule is checkable rather than merely written down.

    THE ONLY RELEASE IS THE STRUCTURED DISCHARGE, checked against the filesystem. It used
    to be a bare word match (`FIXED|landed|cleared|accepted|…`) anywhere in the header
    block, which meant one incidental clause — "prior work landed separately" — took a
    document carrying two matching phrases off the census entirely
    (`WORKER_FINDING_THE_BY_CONSTRUCTION_GATE_IS_SILENCED_BY_AN_ORDINARY_WORD_2026-08-12`,
    defect 1: the fail-open shape in its purest form, the checker passing because it never
    looked). A discharge the filesystem REFUSES does not release either — otherwise the
    typo that voids the release also hides the finding it failed to close.
    """
    violations: list[tuple[FindingSeverity, str]] = []
    for path in classifiable_documents(root):
        result = parse_severity_file(path, repo_root)
        if result.severity == BLOCKING:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        discharge = parse_discharge(text, repo_root)
        if discharge is not None and discharge.released:
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

    refused = false_discharges(args.root)
    for path, discharge in refused:
        print(f"FALSE-DISCHARGE {path.name}: {discharge.reason}")

    for r in open_:
        print(f"UNCLASSIFIED {r.path.name}: {r.reason}")
    return 1 if (open_ or refused) else 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/finding_severity.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("finding_severity")
    sys.exit(main())
