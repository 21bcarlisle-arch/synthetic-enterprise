#!/usr/bin/env python3
"""AO11 — every map cell says when it was asserted and when it was last checked.

WHY THIS EXISTS (addendum ADVISOR_ADDENDUM_ARCHITECTED_OUT_EDGE_INTEGRITY, A2)
-----------------------------------------------------------------------------
A cell reading L0 while its artefacts on disk say L2 is not untidy filing, it
is a VALIDITY-WINDOW FAILURE: an assertion that was true when it was written
and is silently false now, with nothing carrying when it was written or when
it was last checked against reality. The most recent instance is the DD cell
reading level 0, with no ledger entry, while all six sub-parts were built,
committed and live.

Nothing in the governance layer carried either date, so staleness could only
ever be DISCOVERED — by someone happening to look, weeks later. This makes it
a QUERY.

THE THREE CLOCKS
----------------
Per cell, two clocks are derived and one is recorded:

  asserted_at        WHEN THE CLAIM WAS MADE. `git blame` of that atom's own
                     `level_current:` line in maturity_map.yaml, committer
                     time. Derived, so no field can be forgotten, and no turn
                     can back-date it.
  artefacts_moved_at WHEN THE THING IT CLAIMS LAST MOVED. Newest commit
                     touching any path in that atom's `file_scope`. A wholly
                     INDEPENDENT source: the code, not the map.
  verified_at        WHEN SOMEONE LAST CHECKED THE TWO AGAINST EACH OTHER.
                     This one cannot be derived — a check leaves no trace
                     unless it writes one — so it is read from an append-only
                     ledger: this tool's own `--record`, plus the existing
                     `gate_authorizations.jsonl` self-certifications, which
                     ARE a check against evidence at a known moment.

Staleness is then arithmetic: `artefacts_moved_at > max(asserted_at,
verified_at)` means the code moved after the last time anybody looked.

WHY THE BITEMPORAL PRIMITIVE IS *NOT* REUSED (recorded per the atom's own rule)
------------------------------------------------------------------------------
The addendum names `company/interfaces/bitemporal_event_log.py` as the obvious
candidate, and the parent programme's own wall says forced reuse that couples
two purposes is the mirror error of duplication. It was read before this was
written. It does not fit, for three reasons, and the check is recorded here so
the next turn does not have to repeat it:

  1. It models RESTATEMENT of a fact about a real-world period — valid_time is
     a `dt.date` the fact is *about*, and `superseded_by_run` carries Elexon
     settlement runs. A map cell's level is about no period; there is no
     valid-time axis here to populate, so two thirds of the primitive would be
     dead weight carried for the shape of the name.
  2. It is an in-memory log the caller must be TOLD things. Every date here is
     DERIVED from git at query time. Storing them would create the second
     description that rots from the day it is written — the exact defect AO1
     exists to kill.
  3. It lives behind the SIM/company seam. A governance tool that imports the
     layer it steers couples them permanently for no gain.

Git history is already an append-only transaction-time log, and it is the only
one that cannot be forgotten. That is the primitive being reused.

R15 — HOW THIS CONTROL IS BUILT TO BE ABLE TO FAIL
--------------------------------------------------
A staleness report that under-reports looks exactly like a healthy map, so the
integrity checks are the substance:

  VACUITY     Fewer than ATOM_FLOOR cells parsed, or not one cell resolving an
              `asserted_at`, FAILS. Zero stale cells must never be reachable by
              the blame join quietly breaking (the 1557/1557-passed-while-the-
              field-was-absent shape).
  INDEPENDENCE The artefact clock must not come from the map. A cell whose
              file_scope claims `maturity_map.yaml` would be dated against the
              same source as its own assertion — the tautology pattern, where
              the answer is guaranteed rather than measured. Those cells are
              reported TAUTOLOGICAL and are never called current.
  FAIL-SILENT git being unavailable raises. An unavailable check is a FAILED
              check, never an empty stale list.
  NOT-FRESH-BY-DEFAULT  Empty file_scope, untracked artefacts and directory-
              level scope claims are UNVERIFIABLE statuses in their own right.
              None of them is CURRENT. A cell nobody can check must never read
              like a cell somebody checked.

WHAT THIS CANNOT TELL YOU
-------------------------
The clock is FILE-GRANULAR, so it knows that a claimed artefact moved, never
WHY it moved. Hand-checking the first run's four flagged cells found all four
moved for other work: H28's gate file is claimed by three atoms, and H29's
exclusively-claimed `ntfy_utils.py` moved for the NEVER-ASK-WITHOUT-
RECOMMENDING absorption, which has nothing to do with H29's subject.

So a status here is a PROMPT TO LOOK, never a verdict, and `scope_exclusive`
is printed precisely so a shared-file confound is visible instead of passing
as evidence. That is still the whole ask of A2: staleness becomes a QUERY
someone can run in a second, rather than a DISCOVERY someone happens to make
weeks later. A tool that claimed more than this would be inventing certainty
that a file's mtime cannot carry.

ADDITIVE BY DESIGN
------------------
This writes nothing that the draw reads. It does not edit `maturity_map.yaml`;
it appends only to its own ledger. Per the addendum's own mitigation, it
asserts nothing into the draw's input until proven.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MAP_PATH = "docs/design/maturity_map.yaml"
LEDGER_PATH = "docs/observability/map_assertion_provenance.jsonl"
GATE_LEDGER_PATH = "docs/observability/gate_authorizations.jsonl"

# The map has ~205 atoms. A parse resolving fewer than this has broken, and a
# broken parse must never present as a clean map.
ATOM_FLOOR = 100

DAY = 86400.0

# Statuses, worst first. Order is the report order: a contradiction is a defect
# now, staleness is a question, and unverifiable is a gap in what can be asked.
CONTRADICTED = "CONTRADICTED"        # level 0, but every scoped artefact is built and committed
MISSING_ARTEFACTS = "MISSING_ARTEFACTS"  # level >= 2, but no scoped artefact exists on disk
STALE = "STALE"                      # artefacts moved after the last assertion/verification
TAUTOLOGICAL = "TAUTOLOGICAL"        # scope claims the map itself: both clocks share a source
DIRECTORY_SCOPE = "DIRECTORY_SCOPE"  # scope claims a whole directory: ownership unarbitrable
UNTRACKED_ARTEFACTS = "UNTRACKED_ARTEFACTS"  # on disk, not in git, so no clock at all
NO_ARTEFACTS = "NO_ARTEFACTS"        # empty file_scope: nothing to check the claim against
CURRENT = "CURRENT"                  # checked at or after the last artefact move

STATUS_ORDER = [CONTRADICTED, MISSING_ARTEFACTS, STALE, TAUTOLOGICAL, DIRECTORY_SCOPE,
                UNTRACKED_ARTEFACTS, NO_ARTEFACTS, CURRENT]
UNVERIFIABLE = {TAUTOLOGICAL, DIRECTORY_SCOPE, UNTRACKED_ARTEFACTS, NO_ARTEFACTS}


def _git(args: list[str], repo: Path) -> str:
    """Run git, or raise. A git that cannot answer is never a pass."""
    proc = subprocess.run(["git", "-C", str(repo)] + args,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args[:2]), proc.stderr.strip()[:200]))
    return proc.stdout


# ---------------------------------------------------------------------------
# Clock 1 -- when the claim was made (blame of the level_current line)
# ---------------------------------------------------------------------------

_ATOM_RE = re.compile(r"^- id:\s*(\S+)")
_LEVEL_RE = re.compile(r"^\s+level_current:")
_PORCELAIN_HEADER = re.compile(r"^([0-9a-f]{40}) \d+ (\d+)")


def assertion_lines(map_text: str) -> dict[str, int]:
    """atom id -> 1-based line number of ITS OWN `level_current:` line.

    Line-level, not atom-level, on purpose: blaming the whole atom block would
    date the assertion by whichever field was edited last (a note, an evidence
    string), so touching prose would silently reset the clock on the level
    claim. The claim's own line is the only line that means the claim changed.
    """
    out: dict[str, int] = {}
    current: str | None = None
    for n, line in enumerate(map_text.splitlines(), start=1):
        m = _ATOM_RE.match(line)
        if m:
            current = m.group(1)
            continue
        if current and current not in out and _LEVEL_RE.match(line):
            out[current] = n
    return out


def blame_times(repo: Path, path: str) -> dict[int, tuple[float, bool]]:
    """1-based line -> (committer epoch, is_uncommitted).

    Committer time, not author time, so it is on the same clock as the
    `git log --format=%ct` used for the artefacts. Comparing two different
    clocks would put the staleness arithmetic minutes-to-days out for no
    visible reason.
    """
    out: dict[int, tuple[float, bool]] = {}
    line_no: int | None = None
    uncommitted = False
    for raw in _git(["blame", "--line-porcelain", "--", path], repo).splitlines():
        m = _PORCELAIN_HEADER.match(raw)
        if m:
            line_no = int(m.group(2))
            uncommitted = set(m.group(1)) == {"0"}
            continue
        if line_no is not None and raw.startswith("committer-time "):
            out[line_no] = (float(raw.split()[1]), uncommitted)
            line_no = None
    return out


# ---------------------------------------------------------------------------
# Clock 2 -- when the artefacts last moved (independent of the map)
# ---------------------------------------------------------------------------

def path_commit_times(repo: Path) -> dict[str, float]:
    """tracked path -> newest committer epoch touching it.

    One pass over the WHOLE history rather than `git log -1` per path: with no
    depth cutoff, a path untouched for a year still gets its real date. A
    truncated pass would hand old-but-live files "no date", and no-date reads
    as not-stale — a fail-open that would hide exactly the oldest assertions.
    """
    out: dict[str, float] = {}
    ts = 0.0
    for line in _git(["log", "--format=C%ct", "--name-only", "--no-renames"], repo).splitlines():
        if line.startswith("C") and line[1:].isdigit():
            ts = float(line[1:])
        elif line and ts:
            out.setdefault(line, ts)  # log is newest-first, so first seen is newest
    return out


# ---------------------------------------------------------------------------
# Clock 3 -- when anybody last checked (the only recorded one)
# ---------------------------------------------------------------------------

def verification_times(repo: Path) -> dict[str, float]:
    """atom id -> newest recorded verification.

    Two sources, both append-only, both already on disk: this tool's ledger,
    and the existing self-certification ledger. A level self-certified with
    evidence IS a check of the cell against its artefacts at that moment, so
    ignoring it would report a just-certified atom as never-verified and bury
    the real stale cells under noise.
    """
    out: dict[str, float] = {}
    for rel in (LEDGER_PATH, GATE_LEDGER_PATH):
        p = repo / rel
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue  # a malformed line loses its evidence, never the whole ledger
            atom, ts = rec.get("atom"), rec.get("ts")
            if isinstance(atom, str) and isinstance(ts, (int, float)):
                out[atom] = max(out.get(atom, 0.0), float(ts))
    return out


# ---------------------------------------------------------------------------
# The rows
# ---------------------------------------------------------------------------

def _scope_paths(atom: dict) -> list[str]:
    scope = atom.get("file_scope") or []
    if isinstance(scope, str):
        scope = [scope]
    return [str(s).strip().strip("'\"") for s in scope if str(s).strip()]


def _last_checked(asserted_at: float | None, verified_at: float | None) -> float:
    """The later of the two moments anybody looked. 0.0 means nobody ever did."""
    return max([t for t in (asserted_at, verified_at) if t is not None] or [0.0])


def _classify(*, level, scope: list[str], dir_claims: list[str], claims_the_map: bool,
              existing: list[str], dated: dict[str, float], last_checked: float) -> str:
    """One cell's status. The ladder is ordered by what can be KNOWN, worst first.

    Everything above the final branch is a cell that cannot be checked at all, and
    each is its own status rather than a quiet pass — a cell nobody can check must
    never read like a cell somebody checked.
    """
    if claims_the_map:
        return TAUTOLOGICAL  # dated against the file it asserts: the answer would be free
    if dir_claims:
        # A directory claim makes ownership unanswerable, so it cannot date a claim
        # either -- `docs/design` is claimed by 31 atoms and moves daily.
        return DIRECTORY_SCOPE
    if not scope:
        return NO_ARTEFACTS
    if isinstance(level, int) and level >= 2 and not existing:
        return MISSING_ARTEFACTS
    if not dated:
        # On disk but never committed, or named but never created. An L0 cell naming
        # files that do not exist yet is simply un-started, not a defect.
        return UNTRACKED_ARTEFACTS if existing else NO_ARTEFACTS

    moved_since = max(dated.values()) > last_checked
    # The DD shape: the cell says NOTHING IS BUILT, yet every artefact it names is
    # committed AND landed after the claim was last checked.
    #
    # The ordering is what makes this a defect rather than a normal atom. Most L0
    # cells name files that already exist because the work is to CHANGE them --
    # reading those as "already built" would report live, unstarted work as a
    # contradiction, which is the same weight of error as missing a real one. Four of
    # the nine cells the first run flagged were exactly that, and the artefact date
    # PRECEDED the assertion in every one of them.
    if level == 0 and len(dated) == len(scope) and moved_since:
        return CONTRADICTED
    return STALE if moved_since else CURRENT


def _map_atoms(repo: Path | None = None) -> list[dict]:
    """The map's cells. One reader, so a second caller cannot drift from build_rows."""
    import yaml  # local: the tool is importable for tests without a yaml at import time

    return yaml.safe_load(((repo or REPO) / MAP_PATH).read_text(encoding="utf-8"))


def build_rows(repo: Path | None = None, atoms: list[dict] | None = None) -> list[dict]:
    """One row per map cell, carrying its three clocks and a status."""
    import yaml  # local: the tool is importable for tests without a yaml at import time

    repo = repo or REPO
    map_file = repo / MAP_PATH
    map_text = map_file.read_text(encoding="utf-8")
    if atoms is None:
        atoms = yaml.safe_load(map_text)

    lines = assertion_lines(map_text)
    blame = blame_times(repo, MAP_PATH)
    commits = path_commit_times(repo)
    verified = verification_times(repo)
    tracked_dirs = {p.rsplit("/", 1)[0] for p in commits if "/" in p}

    # Who else claims each path. 48 files are claimed by more than one atom, so a
    # shared file moving says nothing about which claimant it moved for: H28's cell
    # lit up because H30 and W2 committed to a gate file three atoms claim. Reporting
    # that as evidence about H28 would be a confound presented as a finding.
    claimants: dict[str, int] = {}
    for atom in atoms:
        for s in _scope_paths(atom):
            claimants[s] = claimants.get(s, 0) + 1

    rows: list[dict] = []
    for atom in atoms:
        atom_id = atom.get("id")
        if not atom_id:
            continue
        level = atom.get("level_current")
        line_no = lines.get(atom_id)
        asserted_at, uncommitted = blame.get(line_no, (None, False)) if line_no else (None, False)
        verified_at = verified.get(atom_id)

        scope = _scope_paths(atom)
        # A directory claim makes ownership unanswerable, so it cannot date a
        # claim either -- `docs/design` is claimed by 31 atoms and moves daily.
        dir_claims = [s for s in scope if (repo / s).is_dir() or s.rstrip("/") in tracked_dirs]
        claims_the_map = any(s == MAP_PATH for s in scope)
        existing = [s for s in scope if (repo / s).exists()]
        dated = {s: commits[s] for s in scope if s in commits}
        artefacts_moved_at = max(dated.values()) if dated else None

        status = _classify(level=level, scope=scope, dir_claims=dir_claims,
                           claims_the_map=claims_the_map, existing=existing, dated=dated,
                           last_checked=_last_checked(asserted_at, verified_at))

        rows.append({
            "atom": atom_id,
            "lane": atom.get("lane"),
            "level_current": level,
            "status": status,
            "asserted_at": asserted_at,
            "asserted_uncommitted": uncommitted,
            "verified_at": verified_at,
            "artefacts_moved_at": artefacts_moved_at,
            "scope_count": len(scope),
            "dated_scope_count": len(dated),
            "scope_claims_map": claims_the_map,
            # False means some other atom's work can move this cell's clock, so the
            # status is a prompt to look rather than evidence about this cell.
            "scope_exclusive": bool(scope) and all(claimants.get(s, 0) == 1 for s in scope),
            "stale_days": (round((artefacts_moved_at - _last_checked(asserted_at, verified_at))
                                 / DAY, 1) if status == STALE else None),
        })
    return rows


def integrity_findings(rows: list[dict]) -> list[str]:
    """The checks that must be able to fail, or none of the above is evidence."""
    findings: list[str] = []
    if len(rows) < ATOM_FLOOR:
        findings.append("VACUITY: only %d cell(s) parsed, floor is %d -- the map parse has broken, "
                        "and a broken parse is not a clean map" % (len(rows), ATOM_FLOOR))
    if rows and not any(r["asserted_at"] for r in rows):
        findings.append("VACUITY: not one cell resolved an asserted_at -- the blame join is "
                        "broken, so every staleness answer below is unearned")
    if rows and not any(r["artefacts_moved_at"] for r in rows):
        findings.append("VACUITY: not one cell resolved an artefacts_moved_at -- the commit-time "
                        "pass is broken, so nothing can be found stale")
    # INDEPENDENCE: the two clocks must never come from the same file.
    leaked = [r["atom"] for r in rows
              if r["status"] not in (TAUTOLOGICAL,) and r.get("scope_claims_map")]
    if leaked:
        findings.append("INDEPENDENCE: %d cell(s) dated against the map they assert (%s) -- "
                        "tautology, the answer would be guaranteed not measured"
                        % (len(leaked), ", ".join(leaked[:3])))
    unknown = [r for r in rows if r["status"] in UNVERIFIABLE]
    if len(unknown) == len(rows) and rows:
        findings.append("VACUITY: every cell is unverifiable -- no comparison was actually made")
    return findings


def by_status(rows: list[dict], status: str) -> list[dict]:
    return [r for r in rows if r["status"] == status]


# ---------------------------------------------------------------------------
# THE HOLD RECORD'S OWN VALIDITY WINDOW  (H27 Expert Hour #22, atom D41)
# ---------------------------------------------------------------------------
# The three clocks above date an atom's LEVEL CLAIM against its artefacts. They
# say nothing about the record that answers the opposite question -- the one a
# self-refill draw actually asks: this atom is HELD below its target, why?
#
# That answer is written by hand, and this repo has now watched it go stale
# twice on the same atom. H27's own `level_hold_note` recorded the first
# instance as a finding ("the record that answers the only question a 2->3 draw
# asks was pointing at work already done") and closed it BY EDITING THE NOTE --
# a prose fix for a prose defect. Three Hours later it was three Hours behind
# again, and the promoter this tick read leads for Hours #19-#21 that had all
# already run. R3: a second false record on the same component means redesign
# the mechanism, not patch it again.
#
# THE NEAREST WORKING ANALOGUE (R4) is the other atom running Hours in this
# repo. H_GAP_fabric_belief_truth_gap has no separate hold note at all: each
# Hour's register entry carries its own verdict ("...SO THE LEVEL STAYS 2"), so
# the answer to the draw is written by the one act an Hour cannot skip -- if the
# Hour is recorded, its verdict is recorded. The diff is WHERE THE VERDICT
# LIVES, and a second copy kept by hand is the only shape that can fall behind.
#
# So the invariant is not "keep the note fresh" (an exhortation) but: THE LATEST
# RECORDED HOUR MUST ANSWER THE DRAW SOMEWHERE THE DRAW READS. Either shape
# satisfies it; neither is mandated.
#
# WHY A "LATEST HOUR MENTIONED" CHECK WOULD BE FAIL-OPEN, and is not what this
# does: every one of these hold records ends by naming the NEXT Hour ("the next
# promoter runs Hour #19"), so the highest number in the note is current by
# construction, one step ahead of the truth. At the first instance -- one Hour
# behind -- a mention check would have passed on the forward pointer alone,
# reading exactly green on the defect it was built for. Only ordinals in a
# sentence that also carries a HOLD VERDICT count; a forward pointer carries
# none. That mutation is pinned by name.

HOLD_STALE = "HOLD_STALE"            # a later Hour is recorded than any Hour answered
HOLD_UNANSWERED = "HOLD_UNANSWERED"  # Hours recorded, no verdict anywhere the draw reads

_ORDINAL_WORDS = {
    "FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4, "FIFTH": 5, "SIXTH": 6,
    "SEVENTH": 7, "EIGHTH": 8, "NINTH": 9, "TENTH": 10, "ELEVENTH": 11,
    "TWELFTH": 12, "THIRTEENTH": 13, "FOURTEENTH": 14, "FIFTEENTH": 15,
    "SIXTEENTH": 16, "SEVENTEENTH": 17, "EIGHTEENTH": 18, "NINETEENTH": 19,
    "TWENTIETH": 20, "THIRTIETH": 30, "FORTIETH": 40,
}
for _tens, _base in (("TWENTY", 20), ("THIRTY", 30)):
    for _unit, _n in list(_ORDINAL_WORDS.items())[:9]:
        _ORDINAL_WORDS["%s-%s" % (_tens, _unit)] = _base + _n

# The register writes "TWENTY-FIRST HOUR" / "THE FIFTEENTH EXPERT HOUR"; the
# notes write "EXPERT HOUR #16". Both forms, one population.
#
# AN ADJECTIVE BETWEEN THE ORDINAL AND THE NOUN MADE THE VERDICT UNREADABLE
# (H27 Expert Hour #25). The only sentence in which an Hour states its own
# outcome is "THE LEVEL STAYS 2 FOR THE TWENTY-FOURTH CONSECUTIVE HOUR", and
# `<ORDINAL> <WORD> HOUR` matched nothing, so the entry parsed as recording an
# Hour it never answered and `test_the_live_store_carries_no_stale_hold_record`
# went red at HEAD on a register that was in fact current. A short run of
# intervening words is allowed rather than the one word observed: closing this
# with `(?:CONSECUTIVE\s+)?` is the instance fix that returns the first time an
# Hour writes STRAIGHT or RUNNING.
#
# The ordinal is an ALTERNATION OF THE KNOWN WORDS, not `[A-Z]+`, and that is
# load-bearing now that words may sit in between: a wildcard first group lets
# "AND THE TWENTIETH HOUR" match with "AND" as the ordinal, and because the scan
# resumes past a discarded match, the real ordinal inside it is LOST. A parse
# that silently drops ordinals is the fail-open this check is built against.
_ORDINAL_ALTERNATION = "|".join(sorted(_ORDINAL_WORDS, key=len, reverse=True))
_ORDINAL_BEFORE_HOUR = re.compile(
    r"\b(" + _ORDINAL_ALTERNATION + r")\b(?:\s+[A-Z]+){0,2}\s+HOUR\b")
_HOUR_HASH = re.compile(r"\bHOUR\s*#\s*(\d+)", re.IGNORECASE)

# A HOLD VERDICT is a sentence saying the level did not move. Deliberately
# narrow: it must state the outcome, never merely mention an Hour.
_HOLD_VERDICT = re.compile(
    r"HELD\s+AT\s+L\d|LEVEL\s+STAYS|STAYS\s+AT\s+\d|LEVEL\s+STAY\b|"
    r"NOT\s+PROMOTED|NOT\s+TAKEN|STILL\s+L\d|REMAINS\s+AT\s+L\d",
    re.IGNORECASE,
)
_SENTENCE_SPLIT = re.compile(r"(?<=[.;])\s+")

# Vacuity floor: below this many Hours parsed across the whole store, the parse
# has stopped matching the convention the register is written in, and an empty
# population is a BROKEN CHECK, not a clean repo.
HOUR_PARSE_FLOOR = 1

# How far into an entry its own Hour may be named. Past this the entry is not
# self-identifying, so it contributes NO ordinal -- see `entry_hour` for why that
# is a None and not a raise.
ENTRY_SELF_ID_WINDOW = 120


def _hour_mentions(text: str) -> list[tuple[int, int]]:
    """[(position, ordinal)] for every Hour named in `text`, in either form."""
    out = []
    for match in _ORDINAL_BEFORE_HOUR.finditer(text or ""):
        word = match.group(1)
        if word in _ORDINAL_WORDS:
            out.append((match.start(), _ORDINAL_WORDS[word]))
    for match in _HOUR_HASH.finditer(text or ""):
        out.append((match.start(), int(match.group(1))))
    return sorted(out)


def hour_ordinals(text: str) -> set[int]:
    """Every Expert-Hour ordinal named in `text`, in either written form."""
    return {n for _, n in _hour_mentions(text)}


def entry_hour(text: str) -> int | None:
    """The Hour a register entry IS -- the first ordinal it names, never one it
    merely refers to.

    Both registers open by naming themselves ("TWENTY-FIRST HOUR (2026-08-12...",
    "2026-08-12 THE FIFTEENTH EXPERT HOUR RAN..."), and both then talk about
    OTHER Hours: the leads they took, and the Hour they hand on to. H_GAP's
    fifteenth entry ends "OPENER FOR THE SIXTEENTH HOUR", so a check that counted
    mentions would read a sixteenth Hour that has not run and report an atom
    whose record is perfectly current as one Hour behind -- the forward-pointer
    defect this check exists to catch, committed by the check itself. It cost a
    false finding on the first real run.

    THE STORE HOLDS MORE THAN HOUR ENTRIES, and that is why a late ordinal is a
    None rather than a raise. `hold_record_atoms` derives its register from
    `simplifications_store.for_atom`, which returns EVERY entry an atom has --
    including DISCOVER/FRAME notes ("2026-08-12 DISCOVER/FRAME ONLY, level stays
    0...") that are not Hour entries at all and merely mention an Hour in their
    body. This raise fired on exactly such a note and RED-WEDGED HEAD, blocking
    every commit in the repo, because it read "this entry does not self-identify"
    as "the convention has moved".

    Those are different facts and only one of them is an emergency, so they are
    now measured separately: an entry that does not self-identify contributes no
    ordinal, and the CONVENTION-MOVED alarm is `HOUR_PARSE_FLOOR` in
    `hold_record_findings` -- a population-level vacuity guard that raises when
    NOTHING parses anywhere. That guard is the right altitude for the claim: one
    unparsed entry is a non-Hour entry, a store where nothing parses is a broken
    check. Returning None here cannot make the check silently inert, because the
    floor is what decides inertness and it still raises.
    """
    mentions = _hour_mentions(text)
    if not mentions:
        return None
    position, ordinal = mentions[0]
    if position > ENTRY_SELF_ID_WINDOW:
        return None
    return ordinal


def answered_hours(text: str) -> set[int]:
    """Ordinals that appear in a sentence which also states a hold verdict.

    A forward pointer ("the next promoter runs Hour #19") states no verdict, so
    it answers nothing -- which is the whole point of reading verdicts rather
    than mentions.
    """
    answered: set[int] = set()
    for sentence in _SENTENCE_SPLIT.split(text or ""):
        if _HOLD_VERDICT.search(sentence):
            answered |= hour_ordinals(sentence)
    return answered


def hold_record_findings(atoms: list[dict]) -> list[str]:
    """Findings for every atom whose hold record is behind its own register.

    Each atom is a dict: `atom` (id), `level_current`, `level_target`,
    `register` (the Hour entries, newest last) and `hold_surfaces` (any further
    text the draw reads -- the hold note, where one is kept).

    RAISES rather than returning clean when no Hour is parsed anywhere: an
    unparseable register is an unavailable check, and an unavailable check is a
    FAILED check (R15).
    """
    parsed_any = 0
    findings: list[str] = []
    for atom in atoms:
        register = list(atom.get("register") or [])
        recorded = {h for h in (entry_hour(str(e)) for e in register) if h is not None}
        parsed_any += len(recorded)
        if not recorded:
            continue
        latest = max(recorded)
        surfaces = [str(e) for e in register] + [str(s) for s in atom.get("hold_surfaces") or []]
        answered = set()
        for surface in surfaces:
            answered |= answered_hours(surface)
        held = (atom.get("level_current") is not None
                and atom.get("level_target") is not None
                and atom["level_current"] < atom["level_target"])
        if not held:
            continue
        if not answered:
            findings.append(
                "%s: %s -- %d Hour(s) recorded, latest #%d, and no record the draw reads "
                "states what the level did. The draw asks why this is still L%s and nothing "
                "answers." % (HOLD_UNANSWERED, atom.get("atom"), len(recorded), latest,
                              atom.get("level_current")))
        elif max(answered) < latest:
            findings.append(
                "%s: %s -- register records Hour #%d, the latest Hour ANSWERED is #%d, so the "
                "record that answers a %s->%s draw is %d Hour(s) behind and hands the next "
                "promoter leads already taken."
                % (HOLD_STALE, atom.get("atom"), latest, max(answered),
                   atom.get("level_current"), atom.get("level_target"), latest - max(answered)))
    if parsed_any < HOUR_PARSE_FLOOR:
        raise ValueError(
            "VACUITY: not one Expert-Hour ordinal parsed across %d atom(s) -- the register's "
            "convention has moved and this check is unavailable, which is a FAILED check, not "
            "a clean one" % len(atoms))
    return findings


def hold_record_atoms(atoms: list[dict], store=None) -> list[dict]:
    """Build `hold_record_findings` input from the map cells and the record store.

    The population is DERIVED -- every atom the store holds Hour entries for --
    never a hand-typed list of the two atoms that run Hours today.
    """
    if store is None:
        from tools import simplifications_store as store  # local: CLI-only dependency
    rows = []
    for atom in atoms:
        aid = atom.get("id")
        if not aid:
            continue
        register = [str(e) for e in store.for_atom(aid)]
        records = store.records_for_atom(aid) or {}
        register += [str(e) for e in (records.get("expert_hour_findings") or [])]
        notes = store.notes_for_atom(aid) or {}
        surfaces = [str(v) for k, v in notes.items() if "hold" in k or "level" in k]
        rows.append({"atom": aid, "level_current": atom.get("level_current"),
                     "level_target": atom.get("level_target"),
                     "register": register, "hold_surfaces": surfaces})
    return rows


# ---------------------------------------------------------------------------
# THE LANDING ITSELF  (H27 Expert Hour #25, atom D42)
# ---------------------------------------------------------------------------
# D41 above asks whether the LATEST RECORDED HOUR IS ANSWERED in a record the
# draw reads. That is record against record. Two Hours running then hit the
# defect it cannot see: H27's Hour #22 wrote atom D38 -- 162 lines, every added
# docstring self-labelled "atom D38, H27 Expert Hour #22" -- and never committed
# it, and Hour #23 verified that work and did not commit either. Both times the
# committed tree was INTERNALLY CONSISTENT: register and note were current with
# each other, and both were silent about the code sitting in the working tree.
#
# THE QUEUED WORDING WOULD NOT HAVE CAUGHT EITHER INSTANCE, and this was measured
# before it was built rather than argued afterwards. Hours #23 and #24 both filed
# the lead as "a register claim of LANDED checked against what is COMMITTED".
# Run against the real history, a HEAD-only check reads clean at both moments:
# at `dfc233094` the register's newest entry (#22) claims a landing -- D41, in
# this file -- that IS committed, and says nothing at all about D38. Nothing in
# the committed tree carries the defect, so no reading of the committed tree can
# find it. THE ONLY WITNESS IS THE DIFFERENCE BETWEEN THE WORKING TREE AND HEAD.
#
# So the subject is the pair of trees, and the signal is the one thing this
# convention already puts in the work itself: an Hour labels its code with its
# own atom and ordinal. Two questions, both derived, neither hand-typed:
#
#   UNLANDED_HOUR_WORK    a tracked code file carries `<atom> Expert Hour #N` in
#                         the working tree and its HEAD version does not -- that
#                         Hour's landing is not landed.
#   UNLANDED_HOUR_RECORD  the atom's record file holds an Hour ENTRY the HEAD
#                         version does not -- the verdict itself is unlanded.
#
# WHY NOT "IS THE file_scope DIRTY", which the finding doc proposed: this tree
# carries 200+ dirty paths across concurrent lanes as its NORMAL state, so plain
# dirtiness is noise with no owner. A self-labelled Hour is not: it names the
# atom and the ordinal that claimed it, so the finding can say WHOSE work is
# unlanded and WHICH Hour to verify rather than rebuild.
#
# WHY A RECORD IS NOT A LANDING: `docs/` is the record store and the staged
# prose, and `site/data/` is their generated rendering. Every one of them repeats
# these labels verbatim, so counting them would report Hour #22 as landed at
# `dfc233094` on the strength of the register that was wrong about it -- record
# against record again, one level down. A landing is CODE.
#
# WHY THIS IS NOT IN THE SHARED `findings` LIST: its subject is the working
# tree, and the CLI's findings list is what a caller refuses to stand behind. A
# working-tree predicate wired into a repo-wide refusal wedges every lane the
# moment any Hour is mid-flight -- which is the state this check exists to
# REPORT, not to punish. It has its own flag and its own exit code.

UNLANDED_WORK = "UNLANDED_HOUR_WORK"      # self-labelled code in the tree, not at HEAD
UNLANDED_RECORD = "UNLANDED_HOUR_RECORD"  # an Hour entry in the tree, not at HEAD

# Path prefixes whose content is a RECORD of a landing rather than the landing.
RECORD_PREFIXES = ("docs/", "site/data/")

# Vacuity floor: below this many Hour labels parsed across both trees, the
# labelling convention has moved and this check is unavailable -- which is a
# FAILED check, never a clean one (R15).
HOUR_LABEL_FLOOR = 1

# The atom-qualified label the convention writes into the work itself. The
# qualifier is CAPTURED, never assumed, and the finding is keyed on the LABEL
# rather than on an atom guessed from it.
#
# WHY, and this was a defect in this check's own first run: two map cells begin
# `H27` (`H27_payment_belief_gap` and `H27_phone_act_channel`), so resolving a
# qualifier to "the atom whose id it prefixes" attributed one atom's unlanded
# work to a second atom that had never touched the file. Silently dropping an
# ambiguous qualifier instead would have been worse -- it would go inert on the
# exact atom the check was built for. So an ambiguous qualifier still FIRES, and
# names every candidate; the label is the subject, and attribution is a courtesy
# the finding offers rather than a fact it needs.
_QUALIFIED_HOUR_LABEL = re.compile(r"([A-Za-z0-9_]{2,})\s+EXPERT\s+HOUR\s*#\s*(\d+)",
                                   re.IGNORECASE)


def qualified_hour_labels(text: str) -> set[tuple[str, int]]:
    """{(QUALIFIER, ordinal)} for every atom-qualified Expert-Hour label.

    A bare "Expert Hour #3" belongs to nobody and is not collected: three atoms
    have run Hours in this repo, and an unqualified label would hand one atom's
    ordinals to another -- the wrong-subject shape R15 names.
    """
    return {(m.group(1).upper(), int(m.group(2)))
            for m in _QUALIFIED_HOUR_LABEL.finditer(text or "")}


def _candidates(qualifier: str, atom_ids) -> list[str]:
    """Map cells whose id this qualifier could name. May be 0, 1 or several."""
    return sorted(a for a in atom_ids if a.upper().startswith(qualifier))


def unlanded_hour_findings(rows: list[dict], atom_ids=()) -> list[str]:
    """Findings for Hour work that is in the working tree and not in HEAD.

    `rows` is a dict: `code` ([{path, head, worktree}] -- the file text on each
    side, `None` where that side does not carry the file) and `records`
    ([{path, atom, head_entries, worktree_entries}]). `atom_ids` is the map's own
    cell ids, used only to name who a label points at.

    RAISES rather than returning clean when no Hour label parses anywhere: an
    unparseable convention is an unavailable check, and an unavailable check is a
    FAILED check.
    """
    parsed_any = 0
    findings: list[str] = []
    for entry in rows.get("code") or []:
        head = qualified_hour_labels(entry.get("head") or "")
        tree = qualified_hour_labels(entry.get("worktree") or "")
        parsed_any += len(head | tree)
        unlanded = tree - head
        if not unlanded:
            continue
        for qualifier in sorted({q for q, _ in unlanded}):
            hours = sorted(n for q, n in unlanded if q == qualifier)
            owners = _candidates(qualifier, atom_ids)
            findings.append(
                "%s: %s Hour(s) %s -- %s carries them in the working tree and not at HEAD%s. "
                "That work is written and NOT landed: verify and land it, never rebuild it. "
                "(%s)"
                % (UNLANDED_WORK, qualifier, ", ".join("#%d" % h for h in hours),
                   entry.get("path"),
                   " (the file does not exist at HEAD at all)"
                   if entry.get("head") is None else "",
                   "map cell: %s" % owners[0] if len(owners) == 1
                   else ("AMBIGUOUS -- this qualifier names %d cells: %s"
                         % (len(owners), ", ".join(owners))) if owners
                   else "no map cell carries this id"))
    for record in rows.get("records") or []:
        head_hours = {h for h in (entry_hour(str(e)) for e in record.get("head_entries") or [])
                      if h is not None}
        tree_hours = {h for h in (entry_hour(str(e))
                                  for e in record.get("worktree_entries") or []) if h is not None}
        parsed_any += len(head_hours | tree_hours)
        unlanded_hours = tree_hours - head_hours
        if unlanded_hours:
            findings.append(
                "%s: %s -- %s records Hour(s) %s in the working tree and not at HEAD. The "
                "verdict for that Hour is written and NOT landed."
                % (UNLANDED_RECORD, record.get("atom"), record.get("path"),
                   ", ".join("#%d" % h for h in sorted(unlanded_hours))))
    if parsed_any < HOUR_LABEL_FLOOR:
        raise ValueError(
            "VACUITY: not one Expert-Hour label or entry parsed across %d code file(s) and %d "
            "record(s) on either tree -- the convention has moved and this check is unavailable, "
            "which is a FAILED check, not a clean one"
            % (len(rows.get("code") or []), len(rows.get("records") or [])))
    return findings


def _head_text(path: str, repo: Path) -> str | None:
    """The file's committed content, or None where HEAD does not carry it.

    A path git refuses to resolve for any OTHER reason propagates: "HEAD does not
    have this file" and "git could not answer" are opposite facts and only one of
    them is a None.
    """
    proc = subprocess.run(["git", "-C", str(repo), "show", "HEAD:%s" % path],
                          capture_output=True, text=True)
    if proc.returncode == 0:
        return proc.stdout
    stderr = proc.stderr.lower()
    if "does not exist" in stderr or "exists on disk, but not in" in stderr:
        return None
    raise RuntimeError("git show HEAD:%s failed: %s" % (path, proc.stderr.strip()[:200]))


def _register_entries(text: str | None) -> list[str]:
    """The Hour entries in one side's record file. Both sides parse identically:
    a head side read one way and a tree side read another would be measuring the
    parser, not the landing."""
    import yaml  # local: the tool is importable for tests without a yaml at import time

    if not text:
        return []
    try:
        doc = yaml.safe_load(text) or {}
    except Exception:
        return []
    if not isinstance(doc, dict):
        return []
    entries = [str(e) for e in (doc.get("simplifications") or [])]
    records = doc.get("map_records") or {}
    if isinstance(records, dict):
        entries += [str(e) for e in (records.get("expert_hour_findings") or [])]
    return entries


def _labelled_code_paths(repo: Path) -> list[str]:
    """Every tracked CODE file carrying an Expert-Hour label, in either tree.

    Derived from the repo both ways -- the working tree's tracked files and
    HEAD's -- so a file that only one side carries is still asked about, which is
    the whole direction the check is built for.
    """
    paths: set[str] = set()
    for args in (["grep", "-l", "-I", "-i", "-E", "Expert Hour #[0-9]"],
                 ["grep", "-l", "-I", "-i", "-E", "Expert Hour #[0-9]", "HEAD"]):
        proc = subprocess.run(["git", "-C", str(repo)] + args, capture_output=True, text=True)
        if proc.returncode not in (0, 1):  # 1 is "no matches", not a failure
            raise RuntimeError("git grep failed: %s" % proc.stderr.strip()[:200])
        for line in proc.stdout.splitlines():
            path = line.split(":", 1)[1] if line.startswith("HEAD:") else line
            if path and not path.startswith(RECORD_PREFIXES):
                paths.add(path)
    return sorted(paths)


def unlanded_hour_atoms(atoms: list[dict], repo: Path | None = None,
                        store_dir: Path | None = None) -> dict:
    """Build `unlanded_hour_findings` input from the two trees.

    The HEAD side comes from `git show` and the tree side from the filesystem:
    two independent readers, because one reader asked twice cannot see a
    difference between them.

    Both populations are DERIVED -- the code files are whatever carries a label
    in either tree, the records are whatever the map's own cells have a store
    file for -- so nothing here is a hand-typed list of the atoms running Hours.
    """
    repo = repo or REPO
    store = (store_dir if store_dir is not None
             else repo / "docs" / "design" / "simplifications")
    code = []
    for path in _labelled_code_paths(repo):
        disk = repo / path
        code.append({"path": path, "head": _head_text(path, repo),
                     "worktree": (disk.read_text(encoding="utf-8", errors="replace")
                                  if disk.exists() else None)})
    records = []
    for atom in atoms:
        aid = atom.get("id")
        if not aid:
            continue
        record_path = store / ("%s.yaml" % aid)
        rel = (record_path.relative_to(repo).as_posix()
               if record_path.is_relative_to(repo) else record_path.as_posix())
        head_text = _head_text(rel, repo)
        tree_text = record_path.read_text(encoding="utf-8") if record_path.exists() else None
        if head_text is None and tree_text is None:
            continue
        records.append({"atom": aid, "path": rel,
                        "head_entries": _register_entries(head_text),
                        "worktree_entries": _register_entries(tree_text)})
    return {"code": code, "records": records}


def record_verification(atom_id: str, note: str, repo: Path | None = None,
                        now: float | None = None) -> dict:
    """Append one verification to the ledger. Append-only, never rewritten."""
    repo = repo or REPO
    rec = {"atom": atom_id, "ts": float(now if now is not None else time.time()),
           "action": "MAP_ASSERTION_VERIFIED", "note": note}
    p = repo / LEDGER_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _fmt(ts: float | None) -> str:
    if not ts:
        return "     never"
    return time.strftime("%Y-%m-%d", time.gmtime(ts))


def _print_rows(rows: list[dict], limit: int | None = None) -> None:
    shown = rows if limit is None else rows[:limit]
    for r in shown:
        print("%-46s L%-4s %-20s asserted %s  verified %s  artefacts %s%s%s"
              % (r["atom"][:46], r["level_current"], r["status"],
                 _fmt(r["asserted_at"]), _fmt(r["verified_at"]), _fmt(r["artefacts_moved_at"]),
                 ("  (+%.0fd)" % r["stale_days"]) if r["stale_days"] else "",
                 # Only where a confound is actually possible: a cell with NO scope
                 # has nothing another atom could have moved, and printing the
                 # warning there would train the reader to ignore it.
                 "" if r["scope_exclusive"] or not r["scope_count"]
                 else "  [shared scope -- another atom may have moved it]"))
    if limit is not None and len(rows) > limit:
        print("... %d more (use --json for all)" % (len(rows) - limit))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stale", action="store_true",
                    help="cells whose artefacts moved after anyone last looked")
    ap.add_argument("--contradicted", action="store_true",
                    help="cells whose level is refuted by the artefacts on disk")
    ap.add_argument("--unverifiable", action="store_true",
                    help="cells nothing can check: no scope, directory scope, untracked")
    ap.add_argument("--atom", metavar="ID", help="the three clocks for one cell")
    ap.add_argument("--record", metavar="ID", help="append a verification for one cell")
    ap.add_argument("--note", default="", help="what was checked (with --record)")
    ap.add_argument("--json", action="store_true", help="emit every row as JSON")
    ap.add_argument("--check", action="store_true", help="integrity only, no rows")
    ap.add_argument("--unlanded", action="store_true",
                    help="Hour work written in the working tree and not committed (D42)")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args(argv)

    if args.record:
        if not args.note:
            print("--record needs --note: a verification with no statement of what was "
                  "checked is a timestamp, not evidence", file=sys.stderr)
            return 2
        rec = record_verification(args.record, args.note)
        print("recorded %s verified at %s" % (rec["atom"], _fmt(rec["ts"])))
        return 0

    if args.unlanded:
        # Its OWN exit code, deliberately: unlanded Hour work is a REPORT to the
        # next draw, not a repo-wide refusal. Folding a working-tree predicate
        # into the shared findings list would wedge every lane whenever any Hour
        # is mid-flight. 2 stays "could not run" -- an unavailable check is a
        # failed check, and it must not be mistaken for the finding itself.
        try:
            cells = _map_atoms()
            findings = unlanded_hour_findings(
                unlanded_hour_atoms(cells), [c.get("id") for c in cells if c.get("id")])
        except Exception as exc:
            print("UNLANDED HOUR WORK: COULD NOT RUN -- %s" % exc, file=sys.stderr)
            return 2
        if not findings:
            print("UNLANDED HOUR WORK: none -- every self-labelled Hour is committed")
            return 0
        print("UNLANDED HOUR WORK: %d finding(s) -- work exists that HEAD does not carry:"
              % len(findings), file=sys.stderr)
        for f in findings:
            print("  " + f, file=sys.stderr)
        return 3

    try:
        rows = build_rows()
        findings = integrity_findings(rows)
        # The hold record is a fourth clock, and it runs HERE rather than only in
        # the suite: D34's control was never wired into its CLI and nobody noticed
        # for two Hours. A stale hold record is an integrity finding about these
        # same cells, so it joins the list the caller already refuses to stand
        # behind. It raises rather than returning clean when unavailable, which
        # the same except below turns into COULD NOT RUN.
        findings = findings + hold_record_findings(hold_record_atoms(_map_atoms()))
    except Exception as exc:  # could not run is never a pass
        print("MAP ASSERTION PROVENANCE: COULD NOT RUN -- %s" % exc, file=sys.stderr)
        return 2

    if findings:
        print("MAP ASSERTION PROVENANCE: %d integrity finding(s) -- do NOT stand behind these "
              "dates:" % len(findings), file=sys.stderr)
        for f in findings:
            print("  " + f, file=sys.stderr)

    rc = _dispatch(args, rows, findings)
    return rc if rc else (1 if findings else 0)


def _dispatch(args, rows: list[dict], findings: list[str]) -> int:
    """Print whichever query was asked for. Returns non-zero only on a bad query."""
    if args.json:
        print(json.dumps({"rows": rows, "integrity_findings": findings,
                          "row_count": len(rows)}, indent=2))
    elif args.atom:
        hit = [r for r in rows if r["atom"] == args.atom]
        if not hit:
            print("no cell %r in the map" % args.atom, file=sys.stderr)
            return 2
        _print_rows(hit)
    elif args.stale:
        rest = by_status(rows, STALE)
        print("%d cell(s) STALE: the artefacts moved after the assertion was last checked"
              % len(rest))
        _print_rows(sorted(rest, key=lambda r: -(r["stale_days"] or 0)), args.limit)
    elif args.contradicted:
        rest = by_status(rows, CONTRADICTED) + by_status(rows, MISSING_ARTEFACTS)
        rest.sort(key=lambda r: not r["scope_exclusive"])  # the unconfounded ones first
        print("%d cell(s) CONTRADICTED by disk: the level and the artefacts disagree "
              "(%d on scope this atom alone claims)"
              % (len(rest), sum(1 for r in rest if r["scope_exclusive"])))
        _print_rows(rest, args.limit)
    elif args.unverifiable:
        rest = [r for r in rows if r["status"] in UNVERIFIABLE]
        print("%d cell(s) UNVERIFIABLE: nothing here can be checked against anything" % len(rest))
        _print_rows(rest, args.limit)
    elif not args.check:
        counts = {s: len(by_status(rows, s)) for s in STATUS_ORDER}
        print("MAP ASSERTION PROVENANCE: %d cells -- %s"
              % (len(rows), ", ".join("%d %s" % (counts[s], s) for s in STATUS_ORDER if counts[s])))
        print("query it: --stale | --contradicted | --unverifiable | --atom ID | --json")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
