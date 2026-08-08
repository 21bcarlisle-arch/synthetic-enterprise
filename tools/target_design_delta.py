#!/usr/bin/env python3
"""AO7 — the reported delta between `docs/design/TARGET_DESIGN.md` and the tree that exists.

WHY THIS EXISTS (director programme ARCHITECTED_OUT, §2)
--------------------------------------------------------
The target-design document's named failure mode, written into the atom before a line of it was
built, is that it becomes "an aspirational wish-list nobody measures against" — and the atom's
own `origin_note` names the remedy: "the REPORTED DELTA is the load-bearing half, not the target
prose". This module is that half. The document states INTENT; this measures the TREE; the delta
is printed.

THE STRUCTURAL GUARD: A WISH CANNOT BE WRITTEN INTO THE DOCUMENT
----------------------------------------------------------------
Every target block in the document must name a probe implemented here, and every probe here must
have a target block. Either orphan is rc 2. This is what makes the anti-wish-list property
STRUCTURAL rather than exhortative: to state a target you must first say how it is measured. A
paragraph of architectural aspiration with no probe does not degrade the report — it fails it.

WE GATE ON MEASURABILITY, NEVER ON THE NUMBER (R12, and this is the load-bearing choice)
----------------------------------------------------------------------------------------
A non-zero delta returns rc 0. It is a DIAGNOSTIC. If a large delta turned the build red, the
cheapest move available to any future turn would be to weaken the target or delete it from the
document, and the map would begin optimising itself toward the territory — the exact goal-seek
R12 forbids, with the added twist that here the metric can edit its own definition.

So the failing conditions are all about the MEASUREMENT, never the measurement's value:

    a target nobody measures        -> rc 2
    a probe nothing targets         -> rc 2
    a probe that cannot measure     -> rc 2   (unmeasurable is a FAILED check, never a pass)
    the document missing/unparseable-> rc 2
    a delta of any size whatsoever  -> rc 0   (reported in full, never hidden)

R15 — THE THREE KILLER PATTERNS, ANSWERED
------------------------------------------
TAUTOLOGY   — the actual is never read from the document. Every probe measures the filesystem,
              git's index, or an AST walk. The document is the sole authority on the TARGET and
              has no influence whatsoever on the ACTUAL, so a document edit can move a target but
              can never move a measurement. `--json` reports `target_source` and `actual_source`
              separately so the independence is auditable rather than promised.
FAIL-OPEN   — every probe declares a `scanned` count and a probe that scanned nothing RAISES
              (`ProbeUnavailable`). "0 monoliths found" and "0 files scanned" are the same number
              and opposite facts; this repo has already shipped a control that passed 1557/1557
              while the field it checked was absent. A probe raising is rc 2, never a silent pass.
FAIL-SILENT — an unavailable dependency (git, the size census, the capability index) is a FAILED
              check. Nothing here degrades to "assume fine". There is no skip disposition, and
              `--check` refuses to report success if any probe did not run.

BOUNDED PARSING
---------------
The block parser requires an explicit closing fence and rejects an unterminated block. An
unbounded field parser that swallows the rest of the document on a missing terminator is a
false-positive one way and a fail-open the other; this repo has been bitten by exactly that.
Unknown keys are rejected rather than ignored, so a typo'd `probe:` is an error and not a
silently unmeasured target.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOC_PATH = PROJECT_DIR / "docs" / "design" / "TARGET_DESIGN.md"

# The line at which a module has stopped being one capability (T1). Stated here, not in the
# document, because it is a measurement convention: the document says "no monolith", this says
# what the tool counts. SP3's NEW_FILE_LINE_CAP (600) governs NEW files and is a different,
# stricter question; 2000 is the destination for the existing tree.
MONOLITH_LINES = 2000

WORLD_ROOTS = ("sim", "simulation")
COMPANY_ROOT = "company"
# The company's legitimate windows onto the world. Imports through these are the seam working.
SEAM_MODULES = (
    "company.interfaces.sim_interface",
    "company.interfaces.recorded_sim_interface",
    "interface",
)
STATE_DIR_NAMES = ("state",)

VALID_DIRECTIONS = ("at_most", "at_least")
REQUIRED_KEYS = {"id", "probe", "direction", "target", "unit"}


class ProbeUnavailable(RuntimeError):
    """A probe could not measure. Always a failed check, never a pass."""


class DocumentDefect(RuntimeError):
    """The target document is missing, unparseable, or structurally wrong."""


@dataclass
class Target:
    id: str
    probe: str
    direction: str
    target: int
    unit: str
    line: int


@dataclass
class Measurement:
    target: Target
    actual: int
    scanned: int
    detail: list[str] = field(default_factory=list)

    @property
    def delta(self) -> int:
        if self.target.direction == "at_most":
            return self.actual - self.target.target
        return self.target.target - self.actual

    @property
    def met(self) -> bool:
        return self.delta <= 0


# --------------------------------------------------------------------------- the bounded parser
_FENCE = re.compile(r"^```target\s*$")
_CLOSE = re.compile(r"^```\s*$")


def parse_targets(text: str) -> list[Target]:
    """Parse ```target blocks. Bounded: an unterminated block is a defect, not a swallow."""
    targets: list[Target] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if not _FENCE.match(lines[i]):
            i += 1
            continue
        start = i + 1
        j = start
        while j < len(lines) and not _CLOSE.match(lines[j]):
            j += 1
        if j >= len(lines):
            raise DocumentDefect(
                f"unterminated ```target block opened at line {i + 1} -- a block with no closing "
                "fence would swallow the rest of the document"
            )
        targets.append(_parse_block(lines[start:j], start + 1))
        i = j + 1
    if not targets:
        raise DocumentDefect(
            "no ```target blocks found -- a target document with no measured targets is the "
            "wish-list this tool exists to make impossible"
        )
    return targets


def _parse_block(body: list[str], line_no: int) -> Target:
    fields: dict[str, str] = {}
    for offset, raw in enumerate(body):
        if not raw.strip():
            continue
        if ":" not in raw:
            raise DocumentDefect(f"line {line_no + offset}: not a key: value pair -- {raw!r}")
        key, _, value = raw.partition(":")
        key, value = key.strip(), value.strip()
        if key in fields:
            raise DocumentDefect(f"line {line_no + offset}: duplicate key {key!r}")
        fields[key] = value

    unknown = set(fields) - REQUIRED_KEYS
    if unknown:
        raise DocumentDefect(
            f"target block at line {line_no}: unknown key(s) {sorted(unknown)} -- a typo'd key "
            "would otherwise be a silently unmeasured target"
        )
    missing = REQUIRED_KEYS - set(fields)
    if missing:
        raise DocumentDefect(f"target block at line {line_no}: missing key(s) {sorted(missing)}")
    if fields["direction"] not in VALID_DIRECTIONS:
        raise DocumentDefect(
            f"target block at line {line_no}: direction must be one of {VALID_DIRECTIONS}"
        )
    try:
        target_value = int(fields["target"])
    except ValueError:
        raise DocumentDefect(
            f"target block at line {line_no}: target must be an integer, got {fields['target']!r}"
        ) from None
    return Target(
        id=fields["id"],
        probe=fields["probe"],
        direction=fields["direction"],
        target=target_value,
        unit=fields["unit"],
        line=line_no,
    )


# ---------------------------------------------------------------------------------- the probes
# Each returns (actual, scanned, detail). `scanned` is the vacuity guard: a probe that scanned
# nothing has not measured zero, it has failed, and every one of these raises rather than
# returning a comfortable 0.


def _tracked_files(project_dir: Path, *suffixes: str) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=project_dir, capture_output=True, text=True, check=True, timeout=60,
        ).stdout
    except (subprocess.SubprocessError, OSError) as exc:
        raise ProbeUnavailable(f"git ls-files unavailable: {exc}") from exc
    files = [p for p in out.split("\0") if p]
    if not files:
        raise ProbeUnavailable("git ls-files returned nothing -- an empty tree is a failed check")
    if suffixes:
        files = [p for p in files if p.endswith(suffixes)]
    return files


def _py_sources(project_dir: Path, roots: tuple[str, ...]) -> list[str]:
    files = [
        p for p in _tracked_files(project_dir, ".py")
        if p.startswith(tuple(r + "/" for r in roots))
        and "__pycache__" not in p
        and not p.startswith("tests/")
    ]
    if not files:
        raise ProbeUnavailable(
            f"no tracked python sources under {roots} -- a walker that stopped covering a root "
            "must fail, not report a clean tree"
        )
    return files


def _imports_of(project_dir: Path, rel: str) -> set[str]:
    try:
        text = (project_dir / rel).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ProbeUnavailable(f"cannot read {rel}: {exc}") from exc
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)
    return found


def probe_modules_over_line_cap(project_dir: Path) -> tuple[int, int, list[str]]:
    """Count modules past MONOLITH_LINES, using SP3's census so line counting cannot diverge."""
    try:
        sys.path.insert(0, str(project_dir))
        from tools.size_ratchet import census_at
    except ImportError as exc:
        raise ProbeUnavailable(f"SP3 size census unavailable: {exc}") from exc
    try:
        census = census_at(None, project_dir=project_dir)
    except Exception as exc:  # RatchetUnavailable and anything git throws underneath it
        raise ProbeUnavailable(f"SP3 census could not measure: {exc}") from exc
    if not census.files_scanned:
        raise ProbeUnavailable("SP3 census scanned 0 files")
    over = sorted(
        (p for p, n in census.lines.items() if n > MONOLITH_LINES),
        key=lambda p: -census.lines[p],
    )
    detail = [f"{p} ({census.lines[p]} lines)" for p in over]
    return len(over), census.files_scanned, detail


def probe_import_cycles(project_dir: Path) -> tuple[int, int, list[str]]:
    """Count strongly-connected components larger than one module."""
    roots = ("company", "sim", "saas", "simulation", "interface", "tools", "background")
    files = _py_sources(project_dir, roots)
    known: dict[str, str] = {}
    for rel in files:
        mod = rel[:-3].replace("/", ".")
        if mod.endswith(".__init__"):
            mod = mod[: -len(".__init__")]
        known[mod] = rel

    def resolve(dotted: str) -> str | None:
        parts = dotted.split(".")
        for i in range(len(parts), 0, -1):
            candidate = ".".join(parts[:i])
            if candidate in known:
                return candidate
        return None

    graph = {
        mod: {r for r in (resolve(t) for t in _imports_of(project_dir, rel)) if r and r != mod}
        for mod, rel in known.items()
    }
    sccs = _strongly_connected(graph)
    cycles = [c for c in sccs if len(c) > 1]
    detail = [" <-> ".join(sorted(c)) for c in cycles]
    return len(cycles), len(known), detail


def _strongly_connected(graph: dict[str, set[str]]) -> list[list[str]]:
    """Tarjan, iterative — the recursive form overflows on a graph this size."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: dict[str, bool] = {}
    stack: list[str] = []
    counter = 0
    out: list[list[str]] = []

    for root in graph:
        if root in index:
            continue
        work: list[tuple[str, list[str]]] = [(root, sorted(graph.get(root, ())))]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack[root] = True
        while work:
            node, pending = work[-1]
            advanced = False
            while pending:
                nxt = pending.pop(0)
                if nxt not in index:
                    index[nxt] = low[nxt] = counter
                    counter += 1
                    stack.append(nxt)
                    on_stack[nxt] = True
                    work.append((nxt, sorted(graph.get(nxt, ()))))
                    advanced = True
                    break
                if on_stack.get(nxt):
                    low[node] = min(low[node], index[nxt])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[node])
            if low[node] == index[node]:
                component = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    component.append(w)
                    if w == node:
                        break
                out.append(component)
    return out


def probe_world_files_importing_company_directly(project_dir: Path) -> tuple[int, int, list[str]]:
    """World modules binding themselves to the company's internal layout (architectural debt)."""
    files = _py_sources(project_dir, WORLD_ROOTS)
    offenders = []
    for rel in files:
        hits = sorted(
            m for m in _imports_of(project_dir, rel)
            if (m == COMPANY_ROOT or m.startswith(COMPANY_ROOT + "."))
            and not m.startswith(SEAM_MODULES)
        )
        if hits:
            offenders.append(f"{rel} -> {', '.join(hits[:3])}{' ...' if len(hits) > 3 else ''}")
    return len(offenders), len(files), offenders


def probe_company_files_importing_world_internals(project_dir: Path) -> tuple[int, int, list[str]]:
    """THE EPISTEMIC WALL. Company modules reading world internals outside the seam."""
    files = _py_sources(project_dir, (COMPANY_ROOT,))
    offenders = []
    for rel in files:
        mod = rel[:-3].replace("/", ".")
        if mod.startswith(SEAM_MODULES):
            continue  # the seam is allowed to see both sides; that is what it is for
        hits = sorted(
            m for m in _imports_of(project_dir, rel)
            if m.split(".")[0] in WORLD_ROOTS
        )
        if hits:
            offenders.append(f"{rel} -> {', '.join(hits[:3])}{' ...' if len(hits) > 3 else ''}")
    return len(offenders), len(files), offenders


def probe_orphan_capabilities(project_dir: Path) -> tuple[int, int, list[str]]:
    """Modules nothing imports and no command runs, via AO1's derived index."""
    try:
        sys.path.insert(0, str(project_dir))
        from tools import capability_index
    except ImportError as exc:
        raise ProbeUnavailable(f"AO1 capability index unavailable: {exc}") from exc
    try:
        rows = capability_index.build_rows(project_dir)
    except Exception as exc:
        raise ProbeUnavailable(f"AO1 index could not build rows: {exc}") from exc
    if not rows:
        raise ProbeUnavailable("AO1 index produced 0 rows -- an empty index is a failed check")
    orphans = capability_index.orphans(rows)
    detail = [str(r.get("module") or r.get("name") or r) for r in orphans[:12]]
    if len(orphans) > 12:
        detail.append(f"... and {len(orphans) - 12} more (tools/capability_index.py --orphans)")
    return len(orphans), len(rows), detail


def probe_duplicated_state_files(project_dir: Path) -> tuple[int, int, list[str]]:
    """State payloads tracked at more than one path -- a source and a committed copy."""
    tracked = _tracked_files(project_dir, ".json")
    by_name: dict[str, list[str]] = defaultdict(list)
    scanned = 0
    for rel in tracked:
        parts = Path(rel).parts
        if not any(p in STATE_DIR_NAMES for p in parts):
            continue
        scanned += 1
        by_name[Path(rel).name].append(rel)
    if not scanned:
        raise ProbeUnavailable(
            f"no tracked json under any {STATE_DIR_NAMES} directory -- if the state layout moved, "
            "this probe must fail rather than report zero duplicates"
        )
    dupes = {n: ps for n, ps in by_name.items() if len(ps) > 1}
    detail = [f"{n}: {', '.join(sorted(ps))}" for n, ps in sorted(dupes.items())]
    return len(dupes), scanned, detail


def probe_company_modules_without_tests(project_dir: Path) -> tuple[int, int, list[str]]:
    """Company production modules that no test file imports."""
    company_files = _py_sources(project_dir, (COMPANY_ROOT,))
    modules = {}
    for rel in company_files:
        mod = rel[:-3].replace("/", ".")
        if mod.endswith(".__init__"):
            continue
        modules[mod] = rel

    test_files = [
        p for p in _tracked_files(project_dir, ".py")
        if (p.startswith("tests/") or Path(p).name.startswith("test_"))
        and "__pycache__" not in p
    ]
    if not test_files:
        raise ProbeUnavailable("no tracked test files found -- a vanished test tree is a failure")

    imported: set[str] = set()
    for rel in test_files:
        for dotted in _imports_of(project_dir, rel):
            parts = dotted.split(".")
            for i in range(len(parts), 0, -1):
                candidate = ".".join(parts[:i])
                if candidate in modules:
                    imported.add(candidate)
                    break
    untested = sorted(set(modules) - imported)
    detail = untested[:12]
    if len(untested) > 12:
        detail.append(f"... and {len(untested) - 12} more")
    return len(untested), len(modules), detail


PROBES: dict[str, Callable[[Path], tuple[int, int, list[str]]]] = {
    "modules_over_line_cap": probe_modules_over_line_cap,
    "import_cycles": probe_import_cycles,
    "world_files_importing_company_directly": probe_world_files_importing_company_directly,
    "company_files_importing_world_internals": probe_company_files_importing_world_internals,
    "orphan_capabilities": probe_orphan_capabilities,
    "duplicated_state_files": probe_duplicated_state_files,
    "company_modules_without_tests": probe_company_modules_without_tests,
}


# ------------------------------------------------------------------------------- reconciliation
def reconcile(targets: list[Target]) -> list[str]:
    """The anti-wish-list guard, both directions. Either orphan is a defect."""
    findings = []
    seen: dict[str, Target] = {}
    for t in targets:
        if t.id in seen:
            findings.append(f"duplicate target id {t.id!r} (lines {seen[t.id].line}, {t.line})")
        seen[t.id] = t
        if t.probe not in PROBES:
            findings.append(
                f"target {t.id!r} (line {t.line}) names probe {t.probe!r}, which is not "
                "implemented -- a target nobody measures is the wish-list this tool forbids"
            )
    targeted = {t.probe for t in targets}
    for name in sorted(set(PROBES) - targeted):
        findings.append(
            f"probe {name!r} is implemented but no target block claims it -- an unclaimed probe "
            "means the document stopped describing what is measured"
        )
    return findings


def measure(targets: list[Target], project_dir: Path) -> tuple[list[Measurement], list[str]]:
    results, failures = [], []
    for t in targets:
        probe = PROBES.get(t.probe)
        if probe is None:
            continue  # already reported by reconcile()
        try:
            actual, scanned, detail = probe(project_dir)
        except ProbeUnavailable as exc:
            failures.append(f"target {t.id!r}: UNMEASURABLE -- {exc}")
            continue
        except Exception as exc:  # an unexpected probe error is still a failed check
            failures.append(f"target {t.id!r}: probe raised {type(exc).__name__} -- {exc}")
            continue
        if scanned <= 0:
            failures.append(
                f"target {t.id!r}: probe scanned 0 units -- 'nothing found' and 'nothing "
                "looked at' are the same number and opposite facts"
            )
            continue
        results.append(Measurement(target=t, actual=actual, scanned=scanned, detail=detail))
    return results, failures


# ---------------------------------------------------------------------------------------- CLI
def _render(results: list[Measurement], verbose: bool) -> str:
    lines = ["", "TARGET DESIGN -- delta between the architecture we would build and the tree", ""]
    lines.append(f"  {'target':<48} {'want':>7} {'actual':>8} {'delta':>7}   scanned")
    lines.append("  " + "-" * 86)
    for m in sorted(results, key=lambda r: -r.delta):
        mark = "OK " if m.met else "   "
        want = ("<=" if m.target.direction == "at_most" else ">=") + str(m.target.target)
        lines.append(
            f"{mark} {m.target.id:<48} {want:>7} {m.actual:>8} {m.delta:>+7}   {m.scanned}"
        )
        if verbose and m.detail:
            for d in m.detail:
                lines.append(f"      - {d}")
    met = sum(1 for m in results if m.met)
    lines.append("")
    lines.append(f"  {met}/{len(results)} targets met. Delta is a DIAGNOSTIC, never a target (R12):")
    lines.append("  a non-zero delta is the honest state of the tree and does not fail this check.")
    lines.append("  What fails is a target that stopped being measured.")
    lines.append("")
    return "\n".join(lines)


def _payload(results: list[Measurement], findings: list[str], doc_path: Path,
             project_dir: Path) -> dict:
    """The JSON artefact AO6's consolidation rhythm consumes.

    `target_source` and `actual_source` are reported separately so the R15 independence claim is
    auditable in the artefact rather than only promised in a docstring.
    """
    return {
        "doc": str(doc_path.relative_to(project_dir) if doc_path.is_relative_to(project_dir)
                   else doc_path),
        "target_source": "docs/design/TARGET_DESIGN.md (authored intent)",
        "actual_source": "git index + AST walk + SP3 census + AO1 index (measured tree)",
        "integrity_findings": findings,
        "targets_met": sum(1 for m in results if m.met),
        "targets_measured": len(results),
        "results": [
            {
                "id": m.target.id, "probe": m.target.probe, "unit": m.target.unit,
                "direction": m.target.direction, "target": m.target.target,
                "actual": m.actual, "delta": m.delta, "met": m.met,
                "scanned": m.scanned, "detail": m.detail,
            }
            for m in sorted(results, key=lambda r: -r.delta)
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="AO7 -- the reported delta between TARGET_DESIGN.md and the tree that exists."
    )
    parser.add_argument("--json", action="store_true", help="emit the delta as JSON (for AO6)")
    parser.add_argument("--check", action="store_true", help="structural integrity only, no table")
    parser.add_argument("--verbose", "-v", action="store_true", help="list what each probe found")
    parser.add_argument("--doc", default=None, help="path to the target document")
    args = parser.parse_args(argv)

    project_dir = PROJECT_DIR
    doc_path = Path(args.doc) if args.doc else DOC_PATH

    try:
        text = doc_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"FAIL: target document unreadable -- {exc}", file=sys.stderr)
        return 2
    try:
        targets = parse_targets(text)
    except DocumentDefect as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    findings = reconcile(targets)
    results, failures = measure(targets, project_dir)
    findings.extend(failures)

    if args.json:
        print(json.dumps(_payload(results, findings, doc_path, project_dir), indent=2))
    elif not args.check:
        print(_render(results, args.verbose))

    if findings:
        print(f"FAIL: {len(findings)} integrity finding(s):", file=sys.stderr)
        for f in findings:
            print(f"  - {f}", file=sys.stderr)
        return 2
    if len(results) != len(targets):
        print("FAIL: not every target produced a measurement", file=sys.stderr)
        return 2
    if args.check:
        print(f"OK: {len(results)} targets, each measured by an implemented probe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
