#!/usr/bin/env python3
"""AO5 — the KNIFE pass ledger: measure the four named hotspots against the tree that exists.

WHY THIS EXISTS (director programme ARCHITECTED_OUT, §1 KNIFE)
--------------------------------------------------------------
The KNIFE step names four hotspots and rules four mitigations as WALLS: sequence position (after
NET), ONE hotspot per pass, behaviour-preserving moves only, byte-identical output checks where
they exist. The atom's own `origin_note` adds the fifth, and it is the one this module serves:

    "a shared file_scope across four high-risk refactors is exactly the concurrency hazard the
     three-lanes rule exists to prevent."

A pass plan written only in prose cannot honour that. Two passes can be drawn a week apart, each
believing its scope is its own, and cut the same seam — and nothing would say so. This module is
the half that makes the disjointness CHECKABLE: it measures each hotspot's real file set from the
tree, computes the real overlap between every pair, and refuses a plan whose declared overlaps do
not match the measured ones.

The targets themselves are NOT re-derived here. The director ruled them already-named, and the
`name:` field of the atom repeats them. What is derived is their CURRENT SIZE and their MUTUAL
OVERLAP, because those are facts about today's tree and July's analysis cannot know them. (It
did not: the reporting monolith it sized at ~9k lines is `saas/reporting/annual_report.py` at
9,378 lines inside an 11,094-line package, and the "~320 zero-import company modules" are 258.)

WE GATE ON THE PLAN'S HONESTY, NEVER ON THE NUMBERS (R12)
---------------------------------------------------------
The same choice `tools/target_design_delta.py` made, for the same reason. A hotspot that grew
returns rc 0 and is REPORTED. If growth turned the build red, the cheapest move for any future
turn would be to widen a baseline in the document, and the ledger would begin optimising itself.
Baselines here are DIAGNOSTIC: they say what the pass has to move, they never say the tree is
wrong. What fails is measurement dishonesty:

    a hotspot nobody measures                 -> rc 2
    a probe no hotspot declares               -> rc 2
    a probe that scanned nothing              -> rc 2   (unmeasurable is a FAILED check)
    an overlap declared that is not real      -> rc 2
    a real overlap left undeclared            -> rc 2   (the concurrency hazard itself)
    a pair omitted from the overlaps line     -> rc 2   (silence is not "zero")
    the document missing/unparseable          -> rc 2
    a baseline missed by any margin at all    -> rc 0   (reported in full, never hidden)

ENFORCEMENT LIVES NEXT DOOR, DELIBERATELY
------------------------------------------
`tests/architecture/test_epistemic_wall_ratchet.py` already ratchets the wall crossings: its
frozen lists may only shrink, and a new crossing reds the suite. This module does NOT duplicate
that. It reads the SAME walker (imported, not reimplemented — see below) and reports; the ratchet
gates. One definition of "a crossing", two consumers with different jobs.

WHY THE WALKER IS IMPORTED FROM A TEST MODULE
----------------------------------------------
`build_edges`/`company_reads_sim`/`sim_reads_company` live in the ratchet test. A tool importing
a test module is unusual, and the obviously tidier move is to lift the walker into a shared module
and have both import it. That move is deliberately NOT made here, and the reason is this atom's
own doctrine: the walker is part of the NET that protects the KNIFE passes, and KNIFE's first
wall is that the net is stable BEFORE the knife cuts. Moving the net while planning the cuts is
the error the sequence exists to prevent. The extraction is real work and it is owed — it is
recorded as the first step INSIDE pass 3, where it belongs, rather than done opportunistically
here. A second AST walk written to avoid the awkward import would be exactly the write-time
blindness the whole programme is about.

R15 — THE THREE KILLER PATTERNS, ANSWERED
------------------------------------------
TAUTOLOGY   — no measured value is ever read from the document. The document is the sole authority
              on what is DECLARED; the tree is the sole authority on what IS. A document edit can
              change a declaration but cannot move a measurement, so a mismatch can only be closed
              by making the declaration true. `--json` reports `declared_source` and
              `measured_source` separately so that independence is auditable, not promised.
FAIL-OPEN   — every probe returns a `scanned` count and a probe that scanned nothing RAISES.
              "0 crossings found" and "0 files walked" are the same number and opposite facts.
              A pair omitted from an `overlaps:` line is an ERROR, never an implied zero — an
              omission is precisely how a real overlap would hide.
FAIL-SILENT — an unavailable dependency (the walker, the capability index, the document) is a
              FAILED check. There is no skip disposition and nothing degrades to "assume fine".

BOUNDED PARSING
---------------
Blocks require an explicit terminator; an unterminated block is an error, not a block that
swallows the rest of the file. Unknown keys are rejected rather than ignored, so a typo'd
`overlaps:` is an error and not a silently undeclared pair.

R15 PROOF: `tests/tools/test_knife_hotspot_measure.py` — every guard has a source mutation
proving it fires alone, plus a vacuity guard (the suite passing while NO hotspot block is ever
parsed is the fail-open shape that would make this ledger theatre).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN_DOC = ROOT / "docs" / "design" / "KNIFE_HOTSPOT_PASSES.md"

BLOCK_OPEN = "<!-- KNIFE-HOTSPOT"
BLOCK_CLOSE = "KNIFE-HOTSPOT -->"

REQUIRED_KEYS = {"hotspot", "probe", "baseline_files", "overlaps"}
OPTIONAL_KEYS = {"baseline_edges", "baseline_lines"}


class ProbeUnavailable(RuntimeError):
    """A probe could not measure. Never degrades to a pass (R15 fail-silent)."""


class PlanError(RuntimeError):
    """The plan document is missing, unparseable, or dishonest about the tree."""


# --------------------------------------------------------------------------
# The measured side: populations read from the tree, never from the document.
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Population:
    """What one hotspot actually consists of, today.

    `files` is the governing set: file paths are the unit `file_scope` is written in and therefore
    the unit the three-lanes concurrency rule cares about. `edges` is reported alongside because
    for the three wall hotspots the edge is the thing a pass removes, and a pass that deleted
    files without removing edges would look like progress on `files` alone.
    """

    files: frozenset[str]
    edges: frozenset[tuple[str, str]] = frozenset()
    scanned: int = 0
    lines: int = 0
    notes: tuple[str, ...] = ()


def _wall_edges():
    """The live crossing edges, from the ratchet's walker (see module docstring)."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from tests.architecture.test_epistemic_wall_ratchet import (  # noqa: PLC0415
            REPO_ROOT,
            WALL_DIRS,
            build_edges,
            company_reads_sim,
            sim_reads_company,
        )
    except Exception as exc:  # pragma: no cover - exercised by the mutation test
        raise ProbeUnavailable(f"the wall walker is unavailable: {exc}") from exc
    raw = build_edges(REPO_ROOT, WALL_DIRS)
    if not raw:
        raise ProbeUnavailable("the wall walker returned no import edges at all")
    merged = {}
    merged.update(company_reads_sim(raw))
    merged.update(sim_reads_company(raw))
    return merged, len(raw)


def _py_files(rel_dir: str) -> list[str]:
    base = ROOT / rel_dir
    if not base.is_dir():
        raise ProbeUnavailable(f"{rel_dir}/ does not exist")
    out = [
        os.path.relpath(os.path.join(dp, fn), ROOT)
        for dp, _dn, fns in os.walk(base)
        for fn in fns
        if fn.endswith(".py")
    ]
    if not out:
        raise ProbeUnavailable(f"{rel_dir}/ holds no python files")
    return sorted(out)


def _count_lines(paths) -> int:
    total = 0
    for p in paths:
        try:
            with open(ROOT / p, encoding="utf-8", errors="replace") as fh:
                total += sum(1 for _ in fh)
        except OSError as exc:
            raise ProbeUnavailable(f"cannot read {p}: {exc}") from exc
    return total


def probe_reporting_monolith() -> Population:
    """Hotspot 1 — the reporting package and its mutual-import cycle with the main run.

    Files are the package itself PLUS the far end of every edge it participates in: a cycle is
    not owned by one side of it, and a pass that edits only `saas/reporting/` cannot break one.
    """
    pkg = _py_files("saas/reporting")
    merged, scanned = _wall_edges()
    if scanned <= 0:
        raise ProbeUnavailable("the wall walker scanned nothing")
    edges = {k for k in merged if k[0].startswith("saas.reporting") or k[1].startswith("saas.reporting")}
    files = set(pkg) | {merged[k].path for k in edges}
    return Population(
        files=frozenset(files),
        edges=frozenset(edges),
        scanned=scanned + len(pkg),
        lines=_count_lines(pkg),
        notes=(f"largest single file: {_largest(pkg)}",),
    )


def _largest(paths) -> str:
    best, best_n = "", -1
    for p in paths:
        n = _count_lines([p])
        if n > best_n:
            best, best_n = p, n
    return f"{best} ({best_n} lines)"


def probe_customer_straddle() -> Population:
    """Hotspot 2 — the customer module straddling the wall.

    `saas/customers.py` is company-side code the SIM imports directly. Its files are the module
    and every SIM module that reaches into it: the straddle is the set of reachers, not the file.
    """
    target = ROOT / "saas" / "customers.py"
    if not target.is_file():
        raise ProbeUnavailable("saas/customers.py does not exist")
    merged, scanned = _wall_edges()
    if scanned <= 0:
        raise ProbeUnavailable("the wall walker scanned nothing")
    edges = {k for k in merged if k[1] == "saas.customers"}
    files = {"saas/customers.py"} | {merged[k].path for k in edges}
    return Population(
        files=frozenset(files),
        edges=frozenset(edges),
        scanned=scanned + 1,
        lines=_count_lines(["saas/customers.py"]),
    )


def probe_wall_crossings() -> Population:
    """Hotspot 3 — every SIM<->company crossing that bypasses the seam.

    Note what is and is NOT an availability failure here. `scanned == 0` (the walker read no
    files) is FAIL-OPEN and raises. Zero CROSSINGS found while thousands of imports were scanned
    is the goal state of pass 3, and a control that could only pass while the defect existed
    would wedge the moment the work succeeded.
    """
    merged, scanned = _wall_edges()
    if scanned <= 0:
        raise ProbeUnavailable("the wall walker scanned nothing")
    files = {e.path for e in merged.values()}
    return Population(
        files=frozenset(files),
        edges=frozenset(merged),
        scanned=scanned,
        notes=(f"seam: company/interfaces/sim_interface.py ({_count_lines(['company/interfaces/sim_interface.py'])} lines)",),
    )


def probe_company_orphans() -> Population:
    """Hotspot 4 — company-side modules nothing imports and no command runs.

    Read from the capability index (AO1), which is the repo's single definition of "orphan".
    Re-deriving it here would be a second answer to a question that already has one.
    """
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "capability_index.py"), "--json"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=600,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProbeUnavailable(f"the capability index would not run: {exc}") from exc
    if proc.returncode != 0:
        raise ProbeUnavailable(f"the capability index exited {proc.returncode}")
    try:
        rows = json.loads(proc.stdout)["rows"]
    except (ValueError, KeyError, TypeError) as exc:
        raise ProbeUnavailable(f"the capability index emitted no usable rows: {exc}") from exc
    if not rows:
        raise ProbeUnavailable("the capability index returned zero rows")
    orphans = [
        r for r in rows
        if r.get("status") == "orphan" and str(r.get("module", "")).startswith(("company.", "saas."))
    ]
    tested = sum(1 for r in orphans if r.get("evidence"))
    return Population(
        files=frozenset(r["path"] for r in orphans),
        scanned=len(rows),
        notes=(
            f"{tested}/{len(orphans)} carry test evidence — no-caller is NOT dead-code; "
            "retirement may never be inferred from orphan status alone",
        ),
    )


PROBES = {
    "reporting_monolith": probe_reporting_monolith,
    "customer_straddle": probe_customer_straddle,
    "wall_crossings": probe_wall_crossings,
    "company_orphans": probe_company_orphans,
}


# --------------------------------------------------------------------------
# The declared side: the plan document, sole authority on intent.
# --------------------------------------------------------------------------

@dataclass
class Declaration:
    hotspot: str
    probe: str
    baseline_files: int
    overlaps: dict[str, int]
    baseline_edges: int | None = None
    baseline_lines: int | None = None
    errors: list[str] = field(default_factory=list)


def _parse_overlaps(raw: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for part in [p.strip() for p in raw.split(",") if p.strip()]:
        m = re.fullmatch(r"([A-Za-z0-9_]+)\s*=\s*(\d+)", part)
        if not m:
            raise PlanError(f"overlaps entry {part!r} is not `<hotspot>=<count>`")
        if m.group(1) in out:
            raise PlanError(f"overlaps names {m.group(1)!r} twice")
        out[m.group(1)] = int(m.group(2))
    return out


def parse_plan(text: str) -> list[Declaration]:
    """Parse every hotspot block. Bounded: an unterminated block is an error."""
    decls: list[Declaration] = []
    pos = 0
    while True:
        start = text.find(BLOCK_OPEN, pos)
        if start == -1:
            break
        end = text.find(BLOCK_CLOSE, start)
        if end == -1:
            raise PlanError("a KNIFE-HOTSPOT block is never terminated")
        body = text[start + len(BLOCK_OPEN):end]
        pos = end + len(BLOCK_CLOSE)
        fields: dict[str, str] = {}
        for line in body.splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" not in line:
                raise PlanError(f"line {line!r} in a hotspot block is not `key: value`")
            k, v = line.split(":", 1)
            k = k.strip()
            if k in fields:
                raise PlanError(f"key {k!r} appears twice in one hotspot block")
            if k not in REQUIRED_KEYS | OPTIONAL_KEYS:
                raise PlanError(f"unknown key {k!r} in a hotspot block")
            fields[k] = v.strip()
        missing = REQUIRED_KEYS - set(fields)
        if missing:
            raise PlanError(f"hotspot block missing required key(s): {sorted(missing)}")
        try:
            decls.append(Declaration(
                hotspot=fields["hotspot"],
                probe=fields["probe"],
                baseline_files=int(fields["baseline_files"]),
                baseline_edges=int(fields["baseline_edges"]) if "baseline_edges" in fields else None,
                baseline_lines=int(fields["baseline_lines"]) if "baseline_lines" in fields else None,
                overlaps=_parse_overlaps(fields["overlaps"]),
            ))
        except ValueError as exc:
            raise PlanError(f"a baseline is not an integer: {exc}") from exc
    return decls


def load_plan(path: Path = PLAN_DOC) -> list[Declaration]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PlanError(f"the plan document is unreadable: {exc}") from exc
    decls = parse_plan(text)
    if not decls:
        raise PlanError("the plan document declares no hotspots at all")
    names = [d.hotspot for d in decls]
    if len(set(names)) != len(names):
        raise PlanError("the plan document declares the same hotspot twice")
    return decls


# --------------------------------------------------------------------------
# Reconciliation.
# --------------------------------------------------------------------------

def reconcile(decls: list[Declaration], doc: Path = PLAN_DOC) -> tuple[list[str], dict]:
    """Return (findings, report). A finding is a measurement dishonesty -> rc 2."""
    findings: list[str] = []
    declared = {d.hotspot: d for d in decls}

    for name in sorted(set(PROBES) - set(declared)):
        findings.append(f"probe {name!r} exists but no hotspot block declares it")

    pops: dict[str, Population] = {}
    for d in decls:
        if d.probe not in PROBES:
            findings.append(f"hotspot {d.hotspot!r} names probe {d.probe!r}, which does not exist")
            continue
        try:
            pops[d.hotspot] = PROBES[d.probe]()
        except ProbeUnavailable as exc:
            findings.append(f"hotspot {d.hotspot!r} could not be measured: {exc}")

    # Overlaps: the concurrency guard. Every OTHER hotspot must be named, including at zero.
    for d in decls:
        if d.hotspot not in pops:
            continue
        others = {o.hotspot for o in decls if o.hotspot != d.hotspot}
        omitted = others - set(d.overlaps)
        if omitted:
            findings.append(
                f"hotspot {d.hotspot!r} omits {sorted(omitted)} from its overlaps line — "
                "an omission is not an implied zero"
            )
        for other in sorted(set(d.overlaps) - others):
            findings.append(f"hotspot {d.hotspot!r} declares an overlap with unknown hotspot {other!r}")
        for other in sorted(set(d.overlaps) & others):
            if other not in pops:
                continue
            real = len(pops[d.hotspot].files & pops[other].files)
            if real != d.overlaps[other]:
                findings.append(
                    f"hotspot {d.hotspot!r} declares {d.overlaps[other]} shared file(s) with "
                    f"{other!r}; the tree has {real}"
                    + (" — a real overlap is undeclared, which is the concurrency hazard itself"
                       if real > d.overlaps[other] else " — the declaration claims a tangle that is not there")
                )

    report = {
        "declared_source": str(doc),
        "measured_source": "static AST walk of the tree + tools/capability_index.py",
        "hotspots": [],
    }
    for d in decls:
        p = pops.get(d.hotspot)
        report["hotspots"].append({
            "hotspot": d.hotspot,
            "probe": d.probe,
            "measured": None if p is None else {
                "files": len(p.files),
                "edges": len(p.edges),
                "lines": p.lines,
                "scanned": p.scanned,
                "notes": list(p.notes),
            },
            "baseline_files": d.baseline_files,
            "baseline_edges": d.baseline_edges,
            "baseline_lines": d.baseline_lines,
            "delta_files": None if p is None else len(p.files) - d.baseline_files,
            "declared_overlaps": d.overlaps,
            "measured_overlaps": None if p is None else {
                o: len(p.files & pops[o].files) for o in sorted(pops) if o != d.hotspot
            },
        })
    return findings, report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="emit the whole report as JSON")
    ap.add_argument("--check", action="store_true", help="reconciliation only, no report body")
    ap.add_argument("--doc", default=str(PLAN_DOC), help="plan document to read")
    args = ap.parse_args(argv)

    doc = Path(args.doc)  # --doc is how the mutation fixtures point at a tmp plan

    try:
        decls = load_plan(doc)
    except PlanError as exc:
        print(f"KNIFE LEDGER: FAIL — {exc}", file=sys.stderr)
        return 2

    findings, report = reconcile(decls, doc)

    if args.json:
        report["findings"] = findings
        print(json.dumps(report, indent=2))
    elif not args.check:
        for h in report["hotspots"]:
            m = h["measured"]
            if m is None:
                print(f"{h['hotspot']:<22} UNMEASURED")
                continue
            delta = h["delta_files"]
            sign = f"{delta:+d}" if delta else "="
            print(f"{h['hotspot']:<22} {m['files']:>4} files ({sign} vs baseline)  "
                  f"{m['edges']:>4} edges  {m['lines'] or '-':>6} lines")
            for note in m["notes"]:
                print(f"{'':<22}   {note}")

    if findings:
        print(f"\nKNIFE LEDGER: FAIL — {len(findings)} measurement finding(s):", file=sys.stderr)
        for f in findings:
            print(f"  * {f}", file=sys.stderr)
        return 2
    if not args.json:
        print("\nKNIFE LEDGER: OK — every hotspot measured; every declared overlap matches the tree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
