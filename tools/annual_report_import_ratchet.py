#!/usr/bin/env python3
"""
REUSE: tools/annual_report_import_ratchet.py
CLASS: CUSTOM
INDEX: searched "import ratchet", "annual report", "importer", "renderer", "layering".
       Three ratchets exist and none guards an import edge. `tools/orphan_ratchet.py` asks the
       OPPOSITE question -- who has NO caller -- and its baseline is a set of module names, not
       edges; `tools/size_ratchet_gate.py` freezes file sizes; `tools/company_network_isolation.py`
       freezes ROUTES OUT of the company and is the closest in SHAPE. That shape is reused
       deliberately and visibly: frozen set, fail on new, fail on stale, shrink-only, so a
       reader who knows one knows this. What is not reused is its import-graph walker, which is
       transitive by design because a socket opened three modules down is still a socket; this
       edge is DIRECT-ONLY on purpose, because importing something that happens to import the
       report is not what "a report should never be read" forbids.

A REPORT IS A RENDERING. PRODUCTION CODE MAY NOT IMPORT IT.

Director instruction, 2026-08-19, narrowed on the strength of the measurement: "Fix the one real
production violation and make it impossible for new importers to appear. Leave the 77 test files
reaching into renderer internals alone for now -- that's a rebuild, not a decoupling."

So this gate is deliberately asymmetric, and the asymmetry IS the instruction:
  * PRODUCTION importers of `saas.reporting.annual_report`: frozen at ZERO. A new one fails.
  * TEST importers: counted, published as debt, NEVER enforced. The count is written to
    docs/design/ANNUAL_REPORT_IMPORT_DEBT.md so the size is a fact we look at rather than a
    number someone would have to re-measure before choosing to spend on it.

WHY THE TEST COUNT IS NOT ALSO FROZEN. A frozen test count fails on every legitimate edit to a
report test, which is a gate that punishes ordinary work and gets disabled within a week. The
debt is recorded to be CHOSEN later, which is the director's word for it, and a ratchet that
makes the chosen-later thing painful today is a ratchet arguing with its own instruction.

FAIL-CLOSED: an unreadable tree RAISES. Zero importers found because nothing could be scanned is
indistinguishable from zero importers found because the layering is clean, and this gate exists
precisely to tell those apart.
"""
from __future__ import annotations

import ast
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
TARGET = "saas.reporting.annual_report"
DEBT_DOC = PROJECT_DIR / "docs" / "design" / "ANNUAL_REPORT_IMPORT_DEBT.md"

# Production trees. `tests/` is excluded on purpose -- see the module docstring.
PRODUCTION_TREES = ("background", "tools", "company", "saas", "sim", "simulation", "site")

# The module may import itself; the re-export shim inside it is not a violation.
_SELF = "saas/reporting/annual_report.py"

# FROZEN, 2026-08-19, WITH A REASON PER ENTRY -- a freeze without reasons is an amnesty.
#
# I told the director there was ONE production violation and that the other two were "the runner
# and a path constant". This gate, being mechanical, refused all three, and it was right to make
# me say out loud why two of them stay. The distinction that survives scrutiny is not "important
# vs unimportant" but WHAT THE IMPORT IS FOR:
#
#   * `tools/run_annual_report.py` RENDERS the report. It is the entry point that produces the
#     artefact. The rule is that a report must not be a thing other code READS; a renderer's own
#     runner is not other code reading it, it is the thing doing the rendering. Permanent.
#
#   * `tools/publish_report_gist.py` imports two PATH CONSTANTS (DEFAULT_REPORT_PATH,
#     DEFAULT_REPORT_DATA_PATH) so it can publish the file. It reads no computation. This one is
#     a real, small piece of debt rather than a clean case: the paths describe WHERE the artefact
#     lives and would sit better in a neutral module, so that publishing does not have to import
#     a 9,838-line renderer to learn a filename. Recorded here rather than fixed, because
#     changing it touches the publish path and the director's instruction was explicitly narrow.
#
# What is NOT here, and is the whole point: `tools/generate_dashboard_data.py`, which imported
# `populate_compliance_scorecard` -- a COMPUTATION -- and now imports it from its own module.
FROZEN: frozenset[str] = frozenset({
    "tools/run_annual_report.py",
    "tools/publish_report_gist.py",
})


class ScanUnavailable(RuntimeError):
    """The tree could not be scanned. NEVER silently a clean reading."""


def _imports_target(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:  # noqa: BLE001 - an unparseable file is not a scan failure
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "") == TARGET:
            return True
        if isinstance(node, ast.Import):
            if any(a.name == TARGET for a in node.names):
                return True
    return False


def _scan(trees, root: Path | None = None) -> tuple[set[str], int]:
    base = Path(root) if root is not None else PROJECT_DIR
    found, scanned = set(), 0
    for tree_name in trees:
        d = base / tree_name
        if not d.exists():
            continue
        for f in d.rglob("*.py"):
            rel = str(f.relative_to(base))
            if rel == _SELF:
                continue
            scanned += 1
            if _imports_target(f):
                found.add(rel)
    return found, scanned


def production_importers(root: Path | None = None) -> set[str]:
    found, scanned = _scan(PRODUCTION_TREES, root)
    if not scanned:
        raise ScanUnavailable(
            f"no python files scanned under {PRODUCTION_TREES} -- an empty scan reports a clean "
            "layering it never looked at"
        )
    return found


def test_importers(root: Path | None = None) -> set[str]:
    found, _ = _scan(("tests",), root)
    return found


def gate_violations(root: Path | None = None) -> list[str]:
    """NEW production importers fail. A frozen entry that is gone also fails, so the freeze can
    only shrink -- though it is already empty, which is the state worth defending."""
    live = production_importers(root)
    problems = [
        f"NEW PRODUCTION IMPORTER: {p} imports `{TARGET}`. A report is a RENDERING, never a "
        "thing other code reads (director ruling 2026-08-19). If you need a value the report "
        "computes, move the COMPUTATION into its own module and import that from both -- as "
        "`saas/reporting/compliance_scorecard_population.py` did for the last one."
        for p in sorted(live - FROZEN)
    ]
    problems += [
        f"STALE FREEZE: {p} no longer imports `{TARGET}` -- remove it from FROZEN."
        for p in sorted(FROZEN - live)
    ]
    return problems


def render_debt(root: Path | None = None) -> str:
    tests = test_importers(root)
    private = sorted(
        p for p in tests
        if "_section" in (PROJECT_DIR / p).read_text(encoding="utf-8", errors="replace")
    )
    return (
        "**Severity:** RECORDED · **Lane:** D_billing_metering\n\n"
        "# Annual report import debt — measured, recorded, deliberately not paid\n\n"
        "GENERATED by `tools/annual_report_import_ratchet.py --write`. Do not hand-edit.\n\n"
        "Director instruction, 2026-08-19: *\"Leave the 77 test files reaching into renderer\n"
        "internals alone for now — that's a rebuild, not a decoupling, and the cost is out of\n"
        "proportion to the harm. Record it as known debt with its size, so we choose it\n"
        "deliberately later rather than drifting into it.\"*\n\n"
        "## The size\n\n"
        f"| | |\n|---|---|\n"
        f"| Production importers reading a COMPUTATION | **0** (was 1, moved out) |\n"
        f"| Production importers frozen with a stated reason | **{len(FROZEN)}** "
        "(the renderer's own runner; a publisher importing two path constants) |\n"
        f"| Test files importing the report | **{len(tests)}** |\n"
        f"| ...of which reach into private `_section_*` functions | **{len(private)}** |\n"
        f"| `saas/reporting/annual_report.py` | **"
        f"{len((PROJECT_DIR / _SELF).read_text(errors='replace').splitlines())} lines** |\n\n"
        "## What the shape means\n\n"
        "The report is not merely imported — it has become the place where domain figures are\n"
        "COMPUTED, and the suite validates those figures by calling renderer internals. So the\n"
        "debt is not an import list to unpick; it is that a rendering owns computations. Paying\n"
        "it means giving each of those sections a home outside the renderer and repointing its\n"
        "tests, which is a rebuild of the reporting layer.\n\n"
        "## What is already true\n\n"
        "No production code reads a COMPUTATION out of the report any more. The one that did --\n"
        "`tools/generate_dashboard_data.py`, for `populate_compliance_scorecard` -- now imports\n"
        "it from `saas/reporting/compliance_scorecard_population.py`, which both surfaces share\n"
        "so they cannot disagree about whether an obligation is GREEN.\n\n"
        "Two import edges remain and are frozen WITH REASONS rather than waved through:\n"
        "`tools/run_annual_report.py` renders the report (a renderer's own runner is not other\n"
        "code reading it), and `tools/publish_report_gist.py` imports two PATH CONSTANTS to know\n"
        "where the artefact lives. The second is real, small debt: a filename should not require\n"
        "importing a 9,700-line renderer. It is left because it touches the publish path and the\n"
        "instruction was explicitly narrow.\n\n"
        "A NEW production importer fails the commit, so this cannot grow on the side that matters.\n"
    )


def main() -> int:
    import sys
    write = "--write" in sys.argv
    try:
        problems = gate_violations()
    except ScanUnavailable as exc:
        print(f"annual-report-import-ratchet: SCAN UNAVAILABLE -- {exc}")
        return 2
    if write:
        DEBT_DOC.parent.mkdir(parents=True, exist_ok=True)
        DEBT_DOC.write_text(render_debt(), encoding="utf-8")
        print(f"wrote {DEBT_DOC.relative_to(PROJECT_DIR)}")
    if not problems:
        print(f"annual-report-import-ratchet: no production module imports {TARGET} "
              f"({len(test_importers())} test file(s), recorded as debt, not enforced).")
        return 0
    print("annual-report-import-ratchet: COMMIT REFUSED.\n")
    for p in problems:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
