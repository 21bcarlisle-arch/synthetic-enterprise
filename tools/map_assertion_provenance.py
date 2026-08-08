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

        if claims_the_map:
            status = TAUTOLOGICAL
        elif dir_claims:
            status = DIRECTORY_SCOPE
        elif not scope:
            status = NO_ARTEFACTS
        elif isinstance(level, int) and level >= 2 and not existing:
            status = MISSING_ARTEFACTS
        elif not dated:
            # On disk but never committed, or named but never created. An L0 cell
            # naming files that do not exist yet is simply un-started, not a defect.
            status = UNTRACKED_ARTEFACTS if existing else NO_ARTEFACTS
        else:
            last_checked = max([t for t in (asserted_at, verified_at) if t is not None] or [0.0])
            moved_since = artefacts_moved_at > last_checked
            # The DD shape: the cell says NOTHING IS BUILT, yet every artefact it
            # names is committed AND landed after the claim was last checked.
            #
            # The ordering is what makes this a defect rather than a normal atom.
            # Most L0 cells name files that already exist because the work is to
            # CHANGE them -- reading those as "already built" would report live,
            # unstarted work as a contradiction, which is the same weight of error
            # as missing a real one. Four of the nine cells the first run flagged
            # were exactly that, and the artefact date PRECEDED the assertion in
            # every one of them.
            if level == 0 and len(dated) == len(scope) and moved_since:
                status = CONTRADICTED
            else:
                status = STALE if moved_since else CURRENT

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
            "stale_days": (round((artefacts_moved_at - max(
                [t for t in (asserted_at, verified_at) if t is not None] or [0.0])) / DAY, 1)
                if status == STALE else None),
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
                 "" if r["scope_exclusive"] else "  [shared scope -- another atom may have moved it]"))
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

    try:
        rows = build_rows()
        findings = integrity_findings(rows)
    except Exception as exc:  # could not run is never a pass
        print("MAP ASSERTION PROVENANCE: COULD NOT RUN -- %s" % exc, file=sys.stderr)
        return 2

    if findings:
        print("MAP ASSERTION PROVENANCE: %d integrity finding(s) -- do NOT stand behind these "
              "dates:" % len(findings), file=sys.stderr)
        for f in findings:
            print("  " + f, file=sys.stderr)

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

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
