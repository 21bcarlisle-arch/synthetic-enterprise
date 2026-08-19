#!/usr/bin/env python3
"""AO1 — the reuse surface: one DERIVED row per capability, over the code that exists.

WHY THIS EXISTS (director programme ARCHITECTED_OUT, step MAP)
--------------------------------------------------------------
The named cause of duplicate mechanisms, unwired modules and orphan
transitions is **write-time blindness**: each turn's cheapest move is to write
fresh, because discovering what exists costs more than creating it. Two DD
mandate registers, one with zero callers; a back-billing module found by
collision; a from-scratch working-day calculator built while `holidays` sits
in the ecosystem. None of those were laziness — they were the rational move
under a repo of ~840 production modules with no answer to "do we already have
this?" that costs less than a minute.

This tool is that answer. It is the FIRST half of the programme's economics
change; the write-time gate (AO2) is the half that spends it. An index nobody
consults is a demo, which the director named as the failure mode in advance.

DERIVED, NEVER HAND-MAINTAINED
------------------------------
Every field comes from source on disk at the moment of the query. There is no
committed index artefact to drift, no register to keep in sync, and nothing a
turn can forget to update. A hand-written index would itself be the
duplication this programme exists to kill: a second description of the code,
rotting from the day it is written.

Nothing here reads `docs/design/maturity_map.yaml`. That is deliberate and it
is this atom's answer to the edge-integrity addendum (A1, 2026-08-06): the
map's `file_scope` fields are reported unarbitrable — 48 files claimed by more
than one atom, whole directories claimed as scope, `depends_on` values holding
prose. An index derived from those fields would inherit exactly that
degradation and would report reuse candidates it could not stand behind. An
index that never reads them cannot. A1 is therefore satisfied by construction
rather than by a 185-atom field sweep, which the addendum's own risk section
names as the probable failure.

WHAT A ROW IS
-------------
One production Python module. Not a package, not an atom, not a concept: the
module is the unit a builder actually reuses (`from company.billing.x import
y`), the unit that exists on disk without ambiguity, and the only unit that
already carries an authored plain-words description — its docstring, written
once, next to the code, by the person who knew what it was for.

Per row, matching the proposal's four questions:

  plain words  -- the module docstring's first sentence. ABSENT IS A ROW, not
                  a skip: `plain_words: null` reads "unnamed capability", and
                  those rows are the ones worth the most (a capability nobody
                  could describe is one nobody will find, so it will be built
                  again).
  status       -- `wired` (some production module imports it), `entrypoint`
                  (nothing imports it but it runs as a command), or `orphan`
                  (neither). Derived from real import edges, never asserted.
                  `untracked` OVERRIDES all three: a file git does not track is
                  not something the repo has, whoever it imports (see check 5).
  evidence     -- the test files that import it. Nothing can be claimed here
                  that does not exist, because the list IS the grep.
  demo         -- how you would see it work: a site surface it writes, a test
                  run that exercises it, a command you can run.

R15 — WHY AN INDEX IS A TEXTBOOK FAIL-OPEN CONTROL
---------------------------------------------------
An index that under-reports does not look broken. It looks like a small
codebase. It passes silently, the builder reads "nothing to reuse", and the
index then CAUSES the duplicate build it exists to prevent — the failure is
worse than having no index, because the answer now carries authority.

So the integrity checks are the substance of this file, not its trim:

  1. VACUITY GUARD    -- an index resolving to zero or near-zero rows FAILS.
                         Zero rows is never "nothing to reuse" (the
                         1557/1557-passed-while-the-field-was-absent shape).
                         Any declared root yielding no rows fails too, so a
                         walker that silently stops covering `company/` is a
                         failure and not a quiet 400-row index.
  2. COVERAGE ORACLE  -- every tracked, non-test `.py` under a declared root
                         must have a row. The oracle is `git ls-files`, NOT
                         the same filesystem walk the rows come from. Checking
                         the walk against itself would pass by construction —
                         the tautology pattern — and would prove nothing.
  3. ROOT CLASSIFIER  -- every top-level directory holding tracked Python is
                         either a declared root or carries a written reason in
                         EXCLUDED_ROOTS. A new top-level package lands
                         UNINDEXED and INVISIBLE otherwise, which is the
                         silent-exclusion shape; here it fails instead.
  4. UNPARSED IS A ROW -- a file that will not parse still gets a row (status
                         `unparsed`) AND raises an integrity finding. It is
                         never dropped: a capability the index cannot read is
                         not a capability that does not exist.
  5. UNTRACKED IS NOT  -- the rows come from a filesystem WALK, so until this
     `wired`             check existed an untracked file was indistinguishable
                         from a committed one. Three composition roots really
                         did read `wired`, five callers each, while `git
                         ls-files` carried none of them
                         (WORKER_FINDING_THE_INDEX_READS_THE_WORKING_TREE
                         2026-08-09): the index was answering "do we already
                         have this?" about ONE WORKING TREE, and on the fresh
                         checkout the honest answer was no. Such a row is now
                         stated `untracked` and FAILS `--check`. The
                         trackedness verdict itself is fail-silent-proofed by
                         check 6: unresolved is a finding, never a pass.
  6. TRACKEDNESS RESOLVED -- rows built while the git oracle was unavailable
                         carry `tracked: null`, and that FAILS too. An
                         unavailable check is a FAILED check; without this,
                         check 5 would silently stop firing exactly when git
                         stopped answering.

Exit codes: 0 = index built and trustworthy, 1 = built but integrity findings
(do not stand behind it), 2 = could not run at all. rc 2 is distinct from rc 0
so "could not run" can never be read as "clean".

ORPHAN QUERY (addendum A3)
--------------------------
The write-time gate asks *do we already have this?*. It cannot ask *is this
still wired?* — every orphan to date passed write time cleanly and rotted
afterwards. `--orphans` is the standing read-time answer: modules no
production module imports and no command runs. Absence becomes a query rather
than a discovery, and per R15 it is mutation-proven: delete the only caller of
a real module and it must appear.

ORPHAN DISPOSITION (KNIFE pass 4)
---------------------------------
`--orphans` answers *what is unwired*. It cannot answer *and what did we decide
about it* — a standing list nobody has ruled on decays into wallpaper, which is
how the no-caller class produced 13 instances in 13 days, 8 of them found by
accident. `--dispositions` is the ruling half: every company-side orphan must
carry a row in `docs/design/ORPHAN_DISPOSITION_REGISTER.md` naming its class,
the referent that class requires, and a reason.

There is deliberately NO generator. A new orphan must be dispositioned by a
judgement, and this check FAILS until one exists; auto-stamping every new
orphan with a default class would be the fail-open that empties the ruling of
content. The check also fails on a STALE row — a module that stopped being an
orphan, or stopped existing — so the register cannot quietly outlive its
subject.

Usage:
    python3 tools/capability_index.py --find billing
    python3 tools/capability_index.py --orphans
    python3 tools/capability_index.py --dispositions
    python3 tools/capability_index.py --unnamed
    python3 tools/capability_index.py --json --out /tmp/index.json
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Directories holding code a builder could reuse. Each is a capability
#: habitat, not a filing convention.
DECLARED_ROOTS: tuple[str, ...] = (
    "background",
    "company",
    "interface",
    "saas",
    "sim",
    "simulation",
    "site",
    "tools",
)

#: Top-level directories that hold tracked Python which is deliberately NOT a
#: capability row, each with the reason. A directory absent from BOTH this map
#: and DECLARED_ROOTS is an integrity failure, never a silent skip — that is
#: how a new package would otherwise land invisible to the reuse surface.
EXCLUDED_ROOTS: dict[str, str] = {
    "tests": (
        "the evidence side of the index, not the capability side -- these files "
        "appear on rows as `evidence`, so indexing them as capabilities would "
        "double-count the suite as something to reuse"
    ),
    ".claude": (
        "harness hook scripts, invoked BY PATH by Claude Code and not importable "
        "as modules; their duplication risk is already governed by the single "
        "enumerated hook registry in .claude/settings.json"
    ),
    "docs": (
        "one-shot analysis scripts committed beside the research output they "
        "produced (docs/market_research/**); they are artefacts of a finding, "
        "not mechanisms anything imports"
    ),
}

#: Files that are EVIDENCE wherever they live, never capability rows. Applied
#: identically to the rows and to the coverage oracle, so the two stay
#: comparable.
def is_evidence_file(rel: str) -> bool:
    name = Path(rel).name
    return name.startswith("test_") or name == "conftest.py"


#: Vacuity floor. The repo holds ~840 production modules; a run returning
#: fewer than this many rows means the walk broke, not that the company shrank.
#: Deliberately far below the true count -- a floor that tracks reality would
#: be a generated value pinned in a control, and would fail every time real
#: code was retired.
ROW_FLOOR = 200


# ---------------------------------------------------------------------------
# enumeration
# ---------------------------------------------------------------------------

def tracked_python_files(root: Path | None = None) -> list[str]:
    """Every tracked `.py` path, from git — the INDEPENDENT coverage oracle.

    Deliberately not a filesystem walk: the rows come from a walk, and a walk
    checked against itself passes by construction. Raises rather than
    returning [] when git cannot answer — an unavailable check is a FAILED
    check, and an empty oracle would silently agree with an empty index.
    """
    base = root or ROOT
    try:
        out = subprocess.run(
            ["git", "ls-files", "*.py"],
            cwd=str(base), capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("capability_index: git ls-files failed (%s) -- the coverage "
                           "oracle is unavailable, which is a FAILED check" % exc) from exc
    if out.returncode != 0:
        raise RuntimeError("capability_index: git ls-files returned rc=%d -- the coverage "
                           "oracle is unavailable: %s" % (out.returncode, out.stderr.strip()))
    files = [line.strip() for line in out.stdout.splitlines() if line.strip()]
    if not files:
        raise RuntimeError("capability_index: git ls-files listed 0 Python files -- an empty "
                           "oracle cannot witness an empty index")
    return files


def tracked_paths(root: Path | None = None) -> set[str] | None:
    """The oracle as a SET for row-level lookup, or None when it cannot answer.

    Deliberately non-raising, unlike `tracked_python_files`: `build_rows` runs
    against trees that are not git repositories at all (the orphan ratchet
    builds an index of a scratch tree), and an index that refuses to derive
    there would be a worse failure than one that says "I could not tell".

    "Could not tell" is NOT allowed to read as "tracked", though — that is the
    fail-silent shape this whole check exists to close. None propagates to
    `tracked: null` on every row, and `integrity_findings` fails on it.
    """
    try:
        return set(tracked_python_files(root))
    except RuntimeError:
        return None


def source_files(root: Path | None = None) -> list[str]:
    """Repo-relative paths of every capability row candidate, by filesystem walk."""
    base = root or ROOT
    found: list[str] = []
    for name in DECLARED_ROOTS:
        d = base / name
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.py")):
            if "__pycache__" in p.parts or "node_modules" in p.parts:
                continue
            rel = p.relative_to(base).as_posix()
            if is_evidence_file(rel):
                continue
            found.append(rel)
    return found


def module_name(rel: str) -> str:
    """Dotted import name for a repo-relative path (`a/b/__init__.py` -> `a.b`)."""
    parts = rel[:-3].split("/") if rel.endswith(".py") else rel.split("/")
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


_SENTENCE_END = re.compile(r"(?<=[.!?])\s")


def plain_words(tree: ast.Module | None) -> str | None:
    """First sentence of the module docstring — the authored description.

    None means the module has no docstring: an UNNAMED CAPABILITY row. That is
    a finding worth surfacing, not a blank to be papered over with the
    filename, which would fabricate a description the author never wrote.
    """
    if tree is None:
        return None
    doc = ast.get_docstring(tree)
    if not doc or not doc.strip():
        return None
    first = _SENTENCE_END.split(doc.strip(), 1)[0]
    first = " ".join(first.split())
    return first[:240] if first else None


def imported_modules(tree: ast.Module, own_module: str, known: set[str]) -> set[str]:
    """Repo modules this source imports, resolved against the known module set."""
    hits: set[str] = set()
    own_parts = own_module.split(".")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                hit = _longest_known(alias.name, known)
                if hit:
                    hits.add(hit)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base_parts = own_parts[: max(0, len(own_parts) - node.level)]
                base = ".".join(base_parts + ([node.module] if node.module else []))
            else:
                base = node.module or ""
            if not base:
                continue
            for alias in node.names:
                hit = _longest_known(base + "." + alias.name, known) or _longest_known(base, known)
                if hit:
                    hits.add(hit)
    hits.discard(own_module)
    return hits


def _longest_known(dotted: str, known: set[str]) -> str | None:
    """Longest prefix of `dotted` that names a module in this repo, else None.

    `company.billing.engine.Bill` resolves to `company.billing.engine`; an
    import of `json` resolves to nothing, which is how third-party and stdlib
    imports drop out without a hardcoded exclusion list to maintain.
    """
    parts = dotted.split(".")
    for cut in range(len(parts), 0, -1):
        candidate = ".".join(parts[:cut])
        if candidate in known:
            return candidate
    return None


# ---------------------------------------------------------------------------
# derivation
# ---------------------------------------------------------------------------

def _parse(path: Path) -> tuple[ast.Module | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, "unreadable: %s" % exc
    try:
        return ast.parse(text), None
    except SyntaxError as exc:
        return None, "syntax error line %s: %s" % (exc.lineno, exc.msg)


def _is_entrypoint(tree: ast.Module | None) -> bool:
    if tree is None:
        return False
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if isinstance(test, ast.Compare) and isinstance(test.left, ast.Name) \
                and test.left.id == "__name__":
            return True
    return False


def test_files(root: Path | None = None) -> list[str]:
    """Every test source, wherever it lives — the evidence side."""
    base = root or ROOT
    found: list[str] = []
    for d in [base / "tests"] + [base / r for r in DECLARED_ROOTS]:
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.py")):
            if "__pycache__" in p.parts or "node_modules" in p.parts:
                continue
            rel = p.relative_to(base).as_posix()
            if is_evidence_file(rel):
                found.append(rel)
    return found


def _is_namespace_only(tree: ast.Module | None) -> bool:
    """An `__init__.py` holding nothing but (optionally) a docstring."""
    if tree is None:
        return False
    body = [n for n in tree.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                                         and isinstance(n.value.value, str))]
    return not body


#: A row's note when its file holds no code at all.
NAMESPACE_ONLY = "namespace only -- no code in this file"


def _seed_rows(rels: list[str]) -> tuple[dict[str, dict], dict[str, str], list[str]]:
    """One empty row per source file, keyed by module and by path."""
    by_module: dict[str, dict] = {}
    by_path: dict[str, str] = {}
    order: list[str] = []
    for rel in rels:
        mod = module_name(rel)
        if mod in by_module:  # two files claiming one dotted name; keep both visible
            mod = mod + " (" + rel + ")"
        by_module[mod] = {
            "module": mod, "path": rel, "plain_words": None, "status": "orphan",
            "callers": [], "evidence": [], "demo": [], "search_blob": "", "note": None,
            "tracked": None,
        }
        by_path[rel] = mod
        order.append(mod)
    return by_module, by_path, order


def _read_sources(base: Path, by_module: dict[str, dict], order: list[str]) -> tuple[dict, dict]:
    """Parse every row's file, filling the fields that come from the file alone."""
    trees: dict[str, ast.Module | None] = {}
    texts: dict[str, str] = {}
    for mod in order:
        row = by_module[mod]
        path = base / row["path"]
        try:
            texts[mod] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            texts[mod] = ""
        tree, err = _parse(path)
        trees[mod] = tree
        if err:
            row["status"] = "unparsed"
            row["note"] = err
            row["search_blob"] = _searchable(row["path"], None)
            continue
        row["plain_words"] = plain_words(tree)
        row["is_entrypoint"] = _is_entrypoint(tree)
        row["search_blob"] = _searchable(row["path"], ast.get_docstring(tree))
        if row["path"].endswith("__init__.py") and _is_namespace_only(tree):
            row["note"] = NAMESPACE_ONLY
    return trees, texts


def _wire_edges(base: Path, by_module: dict[str, dict], by_path: dict[str, str],
                order: list[str], trees: dict, texts: dict) -> None:
    """Caller and evidence edges: real imports, PLUS references by path.

    A module launched as `subprocess.run(["python3", "tools/x.py"])` or exec'd
    from a path string has a genuine caller that no import graph can see, and
    calling it an orphan is the false-orphan reading that would get a live
    mechanism retired.
    """
    known = set(by_module)
    for mod in order:
        tree = trees.get(mod)
        if tree is not None:
            for target in imported_modules(tree, mod, known):
                by_module[target]["callers"].append(mod)
        for target in _path_references(texts.get(mod, ""), by_path, mod):
            by_module[target]["callers"].append(mod + " (by path)")

    for rel in test_files(base):
        tree, _err = _parse(base / rel)
        if tree is not None:
            for target in imported_modules(tree, module_name(rel), known):
                by_module[target]["evidence"].append(rel)
        try:
            text = (base / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for target in _path_references(text, by_path, None):
            by_module[target]["evidence"].append(rel)


def _finalise(by_module: dict[str, dict], order: list[str], texts: dict) -> None:
    """Derive status and demo channels once every edge is known."""
    for mod in order:
        row = by_module[mod]
        row["callers"] = sorted(set(row["callers"]))
        row["evidence"] = sorted(set(row["evidence"]))
        if row["status"] == "unparsed":
            continue
        if row["callers"]:
            row["status"] = "wired"
        elif row.get("is_entrypoint"):
            row["status"] = "entrypoint"
        elif row["note"] == NAMESPACE_ONLY:
            row["status"] = "package"
        else:
            row["status"] = "orphan"
        row["demo"] = _demo_channels(texts.get(mod, ""), row)


def _mark_trackedness(by_module: dict[str, dict], order: list[str],
                      tracked: set[str] | None) -> None:
    """Stamp each row with git's verdict on its path, and restate the status.

    Runs AFTER `_finalise`, because it overrides what the import edges said:
    callers make a file `wired` in this working tree, but a file the repo does
    not carry is not a capability the repo has, however many local modules
    import it. `unparsed` is left standing (its own finding is about a file
    that cannot be read, which is still true) — check 5 keys off the `tracked`
    field rather than the status precisely so the two never mask each other.
    """
    for mod in order:
        row = by_module[mod]
        if tracked is None:
            row["tracked"] = None
            continue
        row["tracked"] = row["path"] in tracked
        if not row["tracked"] and row["status"] != "unparsed":
            row["status"] = "untracked"


def build_rows(root: Path | None = None) -> list[dict]:
    """The index: one row per production module, every field derived from source."""
    base = root or ROOT
    by_module, by_path, order = _seed_rows(source_files(base))
    trees, texts = _read_sources(base, by_module, order)
    _wire_edges(base, by_module, by_path, order, trees, texts)
    _finalise(by_module, order, texts)
    _mark_trackedness(by_module, order, tracked_paths(base))
    return [by_module[m] for m in order]


def _searchable(rel: str, doc: str | None) -> str:
    """Lowercased match text: the path with separators opened up, plus the docstring.

    Separators become spaces on BOTH sides of a query, because the search that
    matters is a builder typing "working day" at a module called `working_days`.
    That exact miss was real: the first run of this index answered "0 rows" for
    a capability sitting in `company/compliance/working_days.py`, which is the
    fail-open that CAUSES the duplicate build rather than preventing it.
    """
    opened = re.sub(r"[/_\-.]+", " ", rel[:-3] if rel.endswith(".py") else rel)
    return " ".join((rel + " " + opened + " " + (doc or "")[:2000]).lower().split())


_PATH_TOKEN = re.compile(
    r"\b(?:" + "|".join(DECLARED_ROOTS) + r")/[\w./\-]+\.py\b"
)


def _path_references(text: str, by_path: dict[str, str], own: str | None) -> set[str]:
    """Modules this source names by repo-relative PATH (subprocess, exec, config)."""
    hits: set[str] = set()
    for token in _PATH_TOKEN.findall(text):
        mod = by_path.get(token)
        if mod and mod != own:
            hits.add(mod)
    return hits


def _demo_channels(text: str, row: dict) -> list[str]:
    """How you would SEE this capability work — derived, never claimed."""
    channels: list[str] = []
    if "site/data" in text or 'site" / "data' in text:
        channels.append("site surface")
    if row["evidence"]:
        channels.append("test run")
    if row.get("is_entrypoint"):
        channels.append("command")
    return channels


# ---------------------------------------------------------------------------
# integrity (R15)
# ---------------------------------------------------------------------------

def integrity_findings(rows: list[dict], root: Path | None = None) -> list[str]:
    """Every way this index could be quietly wrong. Empty means stand behind it."""
    base = root or ROOT
    findings: list[str] = []

    # 1. vacuity — an empty or near-empty index is never "nothing to reuse"
    if len(rows) < ROW_FLOOR:
        findings.append(
            "VACUITY: %d rows is below the floor of %d -- an index this small means the "
            "derivation broke, and reporting 'nothing to reuse' is the fail-open that "
            "CAUSES a duplicate build" % (len(rows), ROW_FLOOR)
        )
    by_root: dict[str, int] = {}
    for row in rows:
        by_root[row["path"].split("/")[0]] = by_root.get(row["path"].split("/")[0], 0) + 1
    for name in DECLARED_ROOTS:
        if (base / name).is_dir() and not by_root.get(name):
            findings.append(
                "VACUITY: declared root %s/ exists on disk but produced 0 rows -- the walk "
                "stopped covering it" % name
            )

    # 2/3. coverage against the independent git oracle
    tracked = tracked_python_files(base)
    indexed = {row["path"] for row in rows}
    unclassified: dict[str, int] = {}
    holes: list[str] = []
    for rel in tracked:
        top = rel.split("/")[0] if "/" in rel else ""
        if top in EXCLUDED_ROOTS:
            continue
        if top not in DECLARED_ROOTS:
            unclassified[top or rel] = unclassified.get(top or rel, 0) + 1
            continue
        if is_evidence_file(rel):
            continue
        if rel not in indexed:
            holes.append(rel)
    for top, count in sorted(unclassified.items()):
        findings.append(
            "UNCLASSIFIED ROOT: %s holds %d tracked Python file(s) but is neither a declared "
            "root nor an EXCLUDED_ROOTS entry with a reason -- it would be invisible to the "
            "reuse surface" % (top, count)
        )
    if holes:
        findings.append(
            "COVERAGE HOLE: %d tracked file(s) under a declared root have no row: %s"
            % (len(holes), ", ".join(sorted(holes)[:10]) + (" ..." if len(holes) > 10 else ""))
        )

    # 4. unparsed rows are visible, but they are still a failure to read the code
    unparsed = [r for r in rows if r["status"] == "unparsed"]
    if unparsed:
        findings.append(
            "UNPARSED: %d file(s) could not be read, so their capability is unknown: %s"
            % (len(unparsed), ", ".join(r["path"] for r in unparsed[:10]))
        )

    # 5. a row git does not track is a claim the index cannot support
    untracked = [r for r in rows if r.get("tracked") is False]
    if untracked:
        findings.append(
            "UNTRACKED ROW: %d row(s) have no committed file behind them, so a fresh "
            "checkout does not have them and the index is answering for one working "
            "tree: %s" % (len(untracked), ", ".join(sorted(r["path"] for r in untracked)[:10])
                          + (" ..." if len(untracked) > 10 else ""))
        )

    # 6. and a trackedness verdict that never resolved is not a clean one
    unresolved = [r for r in rows if r.get("tracked") is None]
    if unresolved:
        findings.append(
            "TRACKEDNESS UNRESOLVED: %d row(s) were built while the git oracle could not "
            "answer, so `untracked` could not be told from `wired` -- an unavailable check "
            "is a FAILED check, not a quiet pass: %s"
            % (len(unresolved), ", ".join(sorted(r["path"] for r in unresolved)[:10])
               + (" ..." if len(unresolved) > 10 else ""))
        )
    return findings


def orphans(rows: list[dict]) -> list[dict]:
    """Modules no production module imports and no command runs (addendum A3)."""
    return [r for r in rows if r["status"] == "orphan"]


# ---------------------------------------------------------------------------
# disposition (KNIFE pass 4) — the ruling on every orphan
# ---------------------------------------------------------------------------

#: The register this check reads. The index is the SOURCE (what is an orphan);
#: the register is the RULING (what we decided about it). Two files because a
#: judgement stored in the thing that derives the fact would be re-derived away
#: on the next run.
DISPOSITION_REGISTER = "docs/design/ORPHAN_DISPOSITION_REGISTER.md"

#: Which orphans must carry a ruling. The register is a company-layer artefact;
#: `background/`, `tools/` and `sim/` orphans are governed elsewhere and are not
#: silently swept in here.
DISPOSITION_PREFIXES: tuple[str, ...] = ("company.", "saas.")

#: Each disposition class and the referent it MUST name to be non-vacuous. A
#: class with no required referent would be a label, and a label cannot be
#: wrong -- which is the whole failure mode this register exists to avoid.
DISPOSITION_CLASSES: dict[str, str] = {
    # a caller existed and was missing; the referent is that caller, and it
    # must now genuinely import the module (so the row self-destructs by
    # becoming stale the moment it is true)
    "wired": "caller",
    # archived because something replaced it; the referent NAMES the superseder
    "retired": "superseder",
    # the index cannot see its real caller: an index DEFECT, logged as one
    "explained": "caller",
    # a real, tested capability with no consumer because the consumer was never
    # built; the referent nominates who would drive it
    "unhooked": "consumer",
}

_REGISTER_OPEN = "<!-- ORPHAN-DISPOSITIONS"
_REGISTER_CLOSE = "ORPHAN-DISPOSITIONS -->"

#: Referent form for an orphan whose whole PACKAGE has no external consumer --
#: there is no module to nominate, and inventing one would be decoration. It is
#: a claim about the tree, not an escape hatch: the check verifies the package
#: really has zero external consumers and fires when one appears.
_NO_CONSUMER = "none:"

#: Referent form for an orphan whose package DOES have an external consumer.
#: The counterpart of `_NO_CONSUMER`, and the reason the `unhooked` referent is
#: DERIVED rather than declared (2026-08-19, repairing the 707-commit wedge in
#: `WORKER_FINDING_A_SEAM_CUT_HOLLOWED_OUT_82_ORPHAN_RULINGS_...`).
#:
#: The column used to hand-name one consumer per row. Measured, that was never
#: a per-module judgement: all 258 rows carried exactly ONE distinct nominee per
#: package, copied down the file. And the check could only ever verify it at
#: PACKAGE granularity -- whether the nominee imports *anything* from the
#: package -- so the row asserted "this module would drive THIS orphan" while
#: the control tested something much weaker. A seam cut then moved every
#: crossing behind `company/interfaces/` and hollowed out 82 rows in one stroke,
#: with no repair short of 82 fresh judgements, which wedged the register shut.
#:
#: So the column now states exactly the fact the checker can compute: whether
#: this package has an external consumer at all. The JUDGEMENT -- the class and
#: the reason -- stays hand-authored and stays checked. The same seam cut now
#: shows up as a re-render, not as a wedge found 707 commits later.
_HAS_CONSUMER = "consumers:"

#: Both derived forms. A row of any other class using one is claiming a
#: computed answer to a question its class asks a human to answer.
_DERIVED_REFERENTS: tuple[str, ...] = (_NO_CONSUMER, _HAS_CONSUMER)

#: How many re-rendered rows the CLI names before summarising. The full set is
#: the diff; this is orientation, not the record.
_RENDER_REPORT_LIMIT = 20


def derive_referent(module: str, consumers: dict[str, set[str]]) -> str:
    """The `unhooked` referent COMPUTED from the tree, never declared.

    A column the checker can compute is a column the register must not be
    hand-authoring: a hand-written referent goes stale silently, a rendered one
    cannot.
    """
    pkg = module.rpartition(".")[0]
    prefix = _HAS_CONSUMER if consumers.get(pkg) else _NO_CONSUMER
    return prefix + pkg


def parse_dispositions(text: str) -> tuple[list[dict], list[str]]:
    """Rows of the register, plus every line that would not parse.

    Malformed lines are RETURNED, never skipped: a row the parser cannot read
    is a ruling nobody is enforcing, and dropping it silently would let a typo
    un-disposition a module while the count still looked complete.
    """
    rows: list[dict] = []
    errors: list[str] = []
    inside = False
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not inside:
            if line.startswith(_REGISTER_OPEN):
                inside = True
            continue
        if line.startswith(_REGISTER_CLOSE):
            inside = False
            continue
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 4 or not all(parts[:3]):
            errors.append("line %d is not `module | class | referent | reason`: %s"
                          % (lineno, line[:90]))
            continue
        rows.append({"module": parts[0], "class": parts[1],
                     "referent": parts[2], "reason": parts[3], "line": lineno})
    if inside:
        errors.append("the disposition block was opened and never closed -- every row after "
                      "the last readable one is unenforced")
    return rows, errors


def _package_consumers(rows: list[dict]) -> dict[str, set[str]]:
    """Per package, the modules OUTSIDE it that import one of its wired modules."""
    out: dict[str, set[str]] = {}
    for row in rows:
        pkg = row["module"].rpartition(".")[0]
        if not pkg:
            continue
        bucket = out.setdefault(pkg, set())
        if row["status"] != "wired":
            continue
        for caller in row["callers"]:
            name = caller.replace(" (by path)", "")
            if name == pkg or name.startswith(pkg + "."):
                continue  # a sibling is not a driver of the package
            bucket.add(name)
    return out


def _referent_findings(mod: str, cls: str, ref: str, where: str,
                       consumers: dict[str, set[str]], known: set[str]) -> list[str]:
    """Whether the referent this class REQUIRES is a claim or decoration."""
    if cls == "unhooked":
        # DERIVED column: the only correct value is the one the tree computes,
        # so this fires on a register that has not been re-rendered since the
        # import graph moved -- and the repair is `--render-dispositions`, one
        # command, rather than one fresh judgement per stale row.
        want = derive_referent(mod, consumers)
        if ref == want:
            return []
        return ["STALE RENDER: %s carries referent %r, but the tree derives %r -- the "
                "`unhooked` consumer column is computed, not declared; re-render with "
                "`python3 tools/capability_index.py --render-dispositions`"
                % (where, ref, want)]
    if ref.startswith(_DERIVED_REFERENTS):
        return ["REFERENT MISUSE: %s is class %r and uses a DERIVED referent (`%s`/`%s`), "
                "which only a class `unhooked` row carries -- this class must NAME its %s"
                % (where, cls, _NO_CONSUMER, _HAS_CONSUMER, DISPOSITION_CLASSES[cls])]
    if ref not in known:
        return ["ABSENT REFERENT: %s names %s as its %s, and no such module exists"
                % (where, ref, DISPOSITION_CLASSES[cls])]
    if cls == "wired":
        return ["SELF-REFUTING ROW: %s is classed `wired` but the index still calls it an "
                "orphan -- if %s really imports it the status would say so" % (where, ref)]
    return []


def render_dispositions(text: str, consumers: dict[str, set[str]]) -> tuple[str, list[str]]:
    """Rewrite the DERIVED referent column of every `unhooked` row in place.

    It rewrites that ONE column and nothing else. It never adds a row and never
    removes one: a new orphan must still be ruled on by a judgement, and a
    ruling whose subject left the population must still be retired by one.
    Auto-filling either would leave the count complete while emptying the
    ruling of content -- the exact fail-open §0 of the register forbids, and the
    reason there is deliberately no generator.

    It also never silently repairs a malformed row or one of another class:
    those are the checker's findings to report, and a renderer that tidied them
    away would be deleting the evidence a human has to see.
    """
    out: list[str] = []
    changes: list[str] = []
    inside = False
    for raw in text.splitlines():
        line = raw.strip()
        if not inside:
            out.append(raw)
            if line.startswith(_REGISTER_OPEN):
                inside = True
            continue
        if line.startswith(_REGISTER_CLOSE):
            inside = False
            out.append(raw)
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 4 or not all(parts[:3]) or parts[1] != "unhooked":
            out.append(raw)
            continue
        want = derive_referent(parts[0], consumers)
        if parts[2] != want:
            changes.append("%s | %s -> %s" % (parts[0], parts[2], want))
        out.append("%s | %s | %s | %s" % (parts[0], parts[1], want, parts[3]))
    rendered = "\n".join(out)
    if text.endswith("\n"):
        rendered += "\n"
    return rendered, changes


def _row_findings(row: dict, subjects: dict[str, dict], consumers: dict[str, set[str]],
                  known: set[str]) -> list[str]:
    """Everything one ruling can be wrong about: subject, class, reason, referent."""
    mod, cls, ref = row["module"], row["class"], row["referent"]
    where = "%s (line %d)" % (mod, row["line"])

    if mod not in subjects:
        return ["STALE DISPOSITION: %s names a module that is no longer in the index -- "
                "the register is outliving its subject" % where]
    if subjects[mod]["status"] != "orphan":
        return ["STALE DISPOSITION: %s is now %s, not an orphan -- delete the row; a ruling "
                "kept past its subject is how the count stops meaning anything"
                % (where, subjects[mod]["status"])]
    if cls not in DISPOSITION_CLASSES:
        return ["UNKNOWN CLASS: %s is classed %r, which is not one of %s"
                % (where, cls, ", ".join(sorted(DISPOSITION_CLASSES)))]

    findings: list[str] = []
    if not row["reason"]:
        findings.append("EMPTY REASON: %s carries a class but no reason -- a class without "
                        "a reason is a label" % where)
    findings.extend(_referent_findings(mod, cls, ref, where, consumers, known))
    return findings


def disposition_findings(rows: list[dict], root: Path | None = None) -> list[str]:
    """Every way the orphan ruling could be quietly absent, stale or vacuous.

    Reads the register from disk rather than taking it as an argument, because
    the failure this guards is the register being MISSING -- and a check that
    can only run once someone hands it a register cannot witness that.
    """
    base = root or ROOT
    path = base / DISPOSITION_REGISTER
    findings: list[str] = []

    subjects = {r["module"]: r for r in rows
                if r["module"].startswith(DISPOSITION_PREFIXES)}
    outstanding = {m for m, r in subjects.items() if r["status"] == "orphan"}

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        # FAIL-SILENT guard: an unavailable register is a FAILED ruling, and
        # must never read as "no orphans outstanding".
        return ["DISPOSITION REGISTER UNAVAILABLE: %s could not be read (%s) -- %d "
                "company-side orphan(s) are therefore unruled, which is a FAILED check, "
                "not a clean one" % (DISPOSITION_REGISTER, exc, len(outstanding))]

    declared, errors = parse_dispositions(text)
    findings.extend("MALFORMED DISPOSITION: %s" % e for e in errors)

    if outstanding and not declared:
        findings.append(
            "VACUOUS REGISTER: %d company-side orphan(s) outstanding and the register "
            "declares 0 dispositions -- an empty ruling is not a clean tree"
            % len(outstanding)
        )

    consumers = _package_consumers(rows)
    known = {r["module"] for r in rows}
    seen: set[str] = set()
    for row in declared:
        if row["module"] in seen:
            findings.append("DUPLICATE DISPOSITION: %s (line %d) is ruled on twice -- two "
                            "rulings means neither is the ruling"
                            % (row["module"], row["line"]))
            continue
        seen.add(row["module"])
        findings.extend(_row_findings(row, subjects, consumers, known))

    missing = sorted(outstanding - seen)
    if missing:
        findings.append(
            "UNDISPOSITIONED: %d company-side orphan(s) carry no ruling: %s"
            % (len(missing), ", ".join(missing[:10]) + (" ..." if len(missing) > 10 else "")))
    return findings


def unnamed(rows: list[dict]) -> list[dict]:
    """The empty rows: code with no plain-words description of what it is for.

    Namespace-only `__init__.py` files are not counted. They hold no code, so
    there is no capability to describe and no duplicate anyone could build —
    counting ~100 of them would bury the rows that matter under filing.
    """
    return [
        r for r in rows
        if r["status"] not in ("unparsed", "package") and not r["plain_words"]
    ]


def find(rows: list[dict], term: str) -> list[dict]:
    """Rows matching `term` — the builder's query, and the whole point of the tool.

    Matched against the path with separators opened up AND the full docstring,
    not just the module name: the query is typed in words ("working day",
    "direct debit"), while the code is named in identifiers (`working_days`,
    `dd_mandate`). A matcher that only saw identifiers would answer "nothing to
    reuse" to the exact questions the index exists to answer.
    """
    needle = " ".join(re.sub(r"[/_\-.]+", " ", term).lower().split())
    if not needle:
        return []
    hits = [r for r in rows if needle in r.get("search_blob", "")]
    # A match in the NAME beats a match buried in prose, and a module with real
    # callers is a better reuse candidate than one with none. Without this the
    # answer is alphabetical, and the row the builder needed sits at number 5
    # where a hurried turn will not read it -- which is the same miss as not
    # finding it at all.
    def rank(r: dict) -> tuple:
        opened = " ".join(re.sub(r"[/_\-.]+", " ", r["path"][:-3]).lower().split())
        return (0 if needle in opened else 1, -len(r["callers"]), r["module"])
    return sorted(hits, key=rank)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_rows(rows: list[dict], limit: int | None = None) -> None:
    shown = rows if limit is None else rows[:limit]
    for r in shown:
        words = r["plain_words"] or "(unnamed capability -- no module docstring)"
        print("%-58s %-10s %s" % (r["module"][:58], r["status"], words[:100]))
        detail = []
        if r["evidence"]:
            detail.append("%d test file(s), e.g. %s" % (len(r["evidence"]), r["evidence"][0]))
        else:
            detail.append("NO TEST EVIDENCE")
        if r["callers"]:
            detail.append("%d caller(s)" % len(r["callers"]))
        if r["demo"]:
            detail.append("see it: " + ", ".join(r["demo"]))
        print("    " + " | ".join(detail))
    if limit is not None and len(rows) > limit:
        print("... %d more (use --json for all)" % (len(rows) - limit))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--find", metavar="TERM", help="rows whose name or description mentions TERM")
    ap.add_argument("--orphans", action="store_true", help="modules nothing imports and no command runs")
    ap.add_argument("--dispositions", action="store_true",
                    help="check every company-side orphan carries a ruling in the register")
    ap.add_argument("--render-dispositions", action="store_true",
                    dest="render_dispositions",
                    help="rewrite the DERIVED consumer column of the register's `unhooked` "
                         "rows from the tree (adds no row, removes no row)")
    ap.add_argument("--unnamed", action="store_true", help="rows with no plain-words description")
    ap.add_argument("--json", action="store_true", help="emit the whole index as JSON")
    ap.add_argument("--out", metavar="PATH", help="write the JSON index to PATH")
    ap.add_argument("--check", action="store_true", help="integrity only, no rows")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args(argv)

    try:
        rows = build_rows()
        findings = integrity_findings(rows)
    except Exception as exc:  # could not run is never a pass
        print("CAPABILITY INDEX: COULD NOT RUN -- %s" % exc, file=sys.stderr)
        return 2

    if findings:
        print("CAPABILITY INDEX: %d integrity finding(s) -- do NOT stand behind this index:"
              % len(findings), file=sys.stderr)
        for f in findings:
            print("  " + f, file=sys.stderr)

    payload = None
    if args.json or args.out:
        payload = {"rows": rows, "integrity_findings": findings, "row_count": len(rows)}
    if args.out:
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print("wrote %d rows to %s" % (len(rows), args.out))
    elif args.json:
        print(json.dumps(payload, indent=2))
    elif args.find:
        hits = find(rows, args.find)
        print("%d row(s) match %r -- extend one of these, or record in the commit why not:"
              % (len(hits), args.find))
        _print_rows(hits, args.limit)
    elif args.orphans:
        rest = orphans(rows)
        print("%d orphan row(s): nothing imports them and no command runs them" % len(rest))
        _print_rows(rest, args.limit)
    elif args.render_dispositions:
        path = ROOT / DISPOSITION_REGISTER
        before = path.read_text(encoding="utf-8")
        after, changes = render_dispositions(before, _package_consumers(rows))
        if after == before:
            print("ORPHAN DISPOSITIONS: consumer column already matches the tree -- "
                  "nothing to render")
            return 0
        path.write_text(after, encoding="utf-8")
        print("ORPHAN DISPOSITIONS: re-rendered %d consumer column(s) in %s"
              % (len(changes), DISPOSITION_REGISTER))
        for c in changes[:_RENDER_REPORT_LIMIT]:
            print("  " + c)
        if len(changes) > _RENDER_REPORT_LIMIT:
            print("  ... and %d more" % (len(changes) - _RENDER_REPORT_LIMIT))
        return 0
    elif args.dispositions:
        try:
            ruling = disposition_findings(rows)
        except Exception as exc:
            print("ORPHAN DISPOSITIONS: COULD NOT RUN -- %s" % exc, file=sys.stderr)
            return 2
        subject = [r for r in orphans(rows) if r["module"].startswith(DISPOSITION_PREFIXES)]
        declared, _ = parse_dispositions(
            (ROOT / DISPOSITION_REGISTER).read_text(encoding="utf-8")
            if (ROOT / DISPOSITION_REGISTER).exists() else "")
        counts: dict[str, int] = {}
        for row in declared:
            counts[row["class"]] = counts.get(row["class"], 0) + 1
        print("ORPHAN DISPOSITIONS: %d company-side orphan(s), %d ruled -- %s"
              % (len(subject), len(declared),
                 ", ".join("%s %d" % (k, counts[k]) for k in sorted(counts)) or "none"))
        if ruling:
            print("%d disposition finding(s):" % len(ruling), file=sys.stderr)
            for f in ruling:
                print("  " + f, file=sys.stderr)
            return 1
        print("every company-side orphan carries a ruling with a referent that holds")
        return 1 if findings else 0
    elif args.unnamed:
        rest = unnamed(rows)
        print("%d unnamed capability row(s): code with no docstring to describe it" % len(rest))
        _print_rows(rest, args.limit)
    elif not args.check:
        wired = sum(1 for r in rows if r["status"] == "wired")
        entry = sum(1 for r in rows if r["status"] == "entrypoint")
        untracked = sum(1 for r in rows if r.get("tracked") is False)
        print("CAPABILITY INDEX: %d rows -- %d wired, %d entrypoint, %d orphan, %d untracked, "
              "%d unnamed, %d with no test evidence"
              % (len(rows), wired, entry, len(orphans(rows)), untracked, len(unnamed(rows)),
                 sum(1 for r in rows if not r["evidence"])))
        print("query it: --find TERM | --orphans | --unnamed | --json")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
