#!/usr/bin/env python3
"""A running total may only be read in the order it was accumulated.

THE DEFECT THIS IS THE CLASS FIX FOR (R10), 2026-08-24 --
`docs/staging/WORKER_FINDING_THE_TREASURY_DRAWDOWN_FIGURE_IS_AN_ARTEFACT_OF_SORTING_A_BALANCE_THAT_WAS_NEVER_A_SERIES_2026-08-24.md`:

    `simulation/run_phase2b.py` settles one customer's whole contract term, appends it to
    `all_records`, then moves to the next customer. `treasury_cash_balance_gbp` is a
    PORTFOLIO-level running total stamped onto each record as it is produced, so it is
    meaningful in ACCUMULATION order and in no other. `saas/reporting/annual_report.py`
    then sorts by `(settlement_date, settlement_period)` before walking it into
    `_drawdown_events`, interleaving balances produced at completely different points in
    the term loop. On a real end-2017 run that turns 0 genuine drawdowns into 6,747
    reported ones -- thousands of copies of one swing, each a penny apart -- on a published
    risk figure with a RAG rating computed from it.

That finding was closed for its INSTANCE by a register that folds the drawdown during the
run (`simulation/settlement_daily.py::TreasuryDrawdown`). What it explicitly left open, and
what this module is, is the CLASS:

    "nothing checks that a balance stamped in accumulation order is only ever read in
     accumulation order. The same shape is available to any future consumer that sorts
     `all_records` and reads a running total off it, and there are other running totals on
     those records (`gross_margin_ytd_gbp`, `net_margin_ytd_gbp`, `capital_costs_ytd_gbp`).
     Those have not been checked."

They have now. The scan found the named instance and TWO MORE the finding did not know about,
both `treasury_end`, a published balance-sheet figure. Those two are REPAIRED (2026-08-24,
read in accumulation order, movement measured -- see the note under `KNOWN_READS`); the named
instance remains, because its repair is the drawdown register and that is blocked on the daily
fold's one undiagnosed ~£14 ledger movement.

WHY A STATIC CONTROL RATHER THAN A RUNTIME GUARD. The runtime alternative is to stamp an
accumulation index on every record and have a checked reader refuse an out-of-order walk.
That costs a field on ~1.9M records in the very run whose memory footprint is being cut from
3,003 MB to 486 MB, to catch at run time a mistake that is fully visible in the source. The
order a list was built in is a property of the CODE, so the code is where it is checkable.

WHAT COUNTS AS A RE-SORTED READ. Three shapes, each a real way to write the defect:

  * `comprehension-over-reordering` -- `[r[FIELD] for r in sorted(recs, key=...)]`.
    The named instance (still live), and `segment_report`'s `treasury_end` copy of it
    (repaired 2026-08-24).
  * `subscript-of-reordering`      -- `max(recs, key=...)[FIELD]`.
    `annual_report`'s `treasury_end`: the balance of whichever record has the latest
    (date, period), which is not the balance the year actually closed at. The run's own
    printout uses `yr[-1]` -- accumulation order -- so these two disagreed by construction,
    which is how the repair was checked. Repaired 2026-08-24; zero instances today.
  * `read-of-reordered-binding`    -- `s = sorted(recs, ...)` ... `s[-1][FIELD]`.
    Zero instances today. It is here because it is the obvious way to walk around the first
    two without meaning to, and a control that only catches the shapes already committed is
    a control that can only ever be green.

WHAT IS DELIBERATELY NOT FLAGGED. `yr[-1][FIELD]` where `yr` is a filter or a bucket of
`all_records` is CORRECT -- filtering preserves accumulation order, and that is how
`run_phase2b` prints its own treasury. Reordering is the defect; slicing is not.

RATCHET, NOT A FREEZE -- same shape as `tools/company_network_isolation.py` and the orphan
ratchet. The three reads that exist today are frozen WITH THEIR COUNTS so the debt can only
shrink: a NEW read fails, a SECOND read of an already-frozen (module, shape, field) fails,
and a frozen entry that is no longer real ALSO fails, because a baseline that keeps
discharged entries stops being countable. Every entry names its repair, so removing one is a
checkable claim rather than a tidy-up.

THE FROZEN READS ARE REAL AND STILL WRONG TODAY. `--gate` ignores them so the tree is not
held hostage; the default mode reports them, and is the standing red. Their repair moves a
published figure and so is a measured landing of its own (R14), not a drive-by edit here.
"""
from __future__ import annotations

import argparse
import ast
import os
import sys
from pathlib import Path

REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

#: Fields stamped onto a settlement record as a PORTFOLIO-level running total during the term
#: loop. Each is meaningful only in the order it was accumulated. Sourced from the producers
#: themselves (`run_phase2b`, `run_phase2a_repriced`, `tools/run_segments`), not invented here.
RUNNING_TOTAL_FIELDS: frozenset[str] = frozenset({
    "treasury_cash_balance_gbp",
    "gross_margin_ytd_gbp",
    "net_margin_ytd_gbp",
    "capital_costs_ytd_gbp",
})

#: Builtins that produce a NEW order. `reversed` is included because reversing a running
#: total and walking it is as wrong as sorting it, and costs nothing to name.
REORDERING_BUILTINS: frozenset[str] = frozenset({"sorted", "max", "min", "reversed"})

#: Where a settlement record can be read. `company/` and `sim/` carry no producer today and
#: are scanned anyway -- the point of a class control is the consumer that does not exist yet.
SCAN_DIRS: tuple[str, ...] = ("simulation", "saas", "company", "sim", "tools", "background")

#: This module and its test necessarily name the fields and the shapes; scanning them would
#: be the control reporting itself.
SELF_EXEMPT: frozenset[str] = frozenset({
    "tools/running_total_order.py",
    "tests/tools/test_running_total_order.py",
})

#: THE THREE READS THAT EXIST TODAY, frozen with their counts. Shrink-only: see the module
#: docstring. Key is `module::shape::field`; `count` is what makes a SECOND read of the same
#: (module, shape, field) a failure rather than a silent restatement of the first.
#: EMPTY, AND THAT IS THE POINT: the baseline is paid off, not abandoned. Every entry that was
#: ever in it is recorded below with its movement measured. An empty baseline means `--gate` and
#: the default report now agree, so the standing red this module used to carry is gone.
KNOWN_READS: dict[str, dict] = {}

#: REPAIRED AND REMOVED FROM THE BASELINE -- kept here as prose because a ratchet entry that
#: simply vanishes leaves no record that the debt was PAID rather than hidden. Both were
#: `treasury_end`, both a published balance-sheet figure, both repaired to `yr_records[-1]`
#: (accumulation order) on 2026-08-24 with their movement measured on a real end-2017 run:
#:
#:   saas/reporting/annual_report.py   subscript-of-reordering
#:       was `max(yr_records, key=(settlement_date, settlement_period))`
#:   saas/reporting/segment_report.py  comprehension-over-reordering
#:       was `sorted(...)` built into a series, then `[-1]`
#:
#:   year  published BEFORE   published AFTER    move
#:   2016  £250,807.39        £252,386.55        +£1,579.16
#:   2017  £281,285.30        £283,078.93        +£1,793.63
#:
#: The AFTER figures agree to the penny with what `run_phase2b` prints for the same years in
#: its own "Portfolio P&L by calendar year" table -- an independent check, since that print
#: never went near a re-sort. The BEFORE figures agreed with nothing.
#:
#: THE THIRD AND LAST ENTRY, PAID 2026-08-24 -- the named instance, the drawdown count itself:
#:
#:   saas/reporting/annual_report.py   comprehension-over-reordering
#:       was `sorted(yr_records, key=(settlement_date, settlement_period))` walked by
#:       `_drawdown_events`. REPAIRED by wiring `simulation/settlement_daily.py::
#:       TreasuryDrawdown` into `run_phase2b` (fed at the same single point the settlement fold
#:       is, emitted as `treasury_drawdown_points`) and reading it. The remaining no-register
#:       path reads the book in ACCUMULATION order, which is a second CORRECT read rather than
#:       the old one kept alive: an absent register must not silently become "no drawdowns".
#:
#:   The published figure this moves, on a real `run_phase2b.main(report_end="2017-12-31")`
#:   (199,522 records in 2016, 330,366 in 2017):
#:
#:   year  drawdown events BEFORE   AFTER   deepest BEFORE
#:   2016  0                        0       --
#:   2017  6,747                    0       11.0%
#:
#:   Not "too high" -- the phenomenon did not happen. The RAG rating beside it
#:   (GREEN <25% | AMBER 25-50% | RED >50%) was computed from the same artefact, and the
#:   rendered line was 202,048 characters of near-duplicate events in the end-2019 report.
#:   The register the run emitted was checked equal to one folded independently over the run's
#:   own book, and its events equal to the accumulation-order walk of that book, both years.


class OrderCheckUnavailable(RuntimeError):
    """The check could not be performed. NOT a pass."""


def _is_reordering(node: ast.AST) -> bool:
    return (isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in REORDERING_BUILTINS)


def _fields_read(node: ast.AST, fields: frozenset[str]) -> set[str]:
    """Running-total field names appearing as string constants anywhere under `node`."""
    return {
        child.value for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
        and child.value in fields
    }


def _root_name(node: ast.AST) -> str | None:
    """The base name of a `a[...][...]`/`a.b[...]` chain, if it roots at a plain name."""
    while isinstance(node, (ast.Subscript, ast.Attribute)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _reordered_bindings(tree: ast.AST) -> set[str]:
    """Names bound directly to a reordering, or to a comprehension over one."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        value = node.value
        produced_new_order = _is_reordering(value) or (
            isinstance(value, (ast.ListComp, ast.GeneratorExp, ast.SetComp))
            and any(_is_reordering(gen.iter) for gen in value.generators)
        )
        if produced_new_order:
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
    return names


def scan_source(source: str, path: str,
                fields: frozenset[str] = RUNNING_TOTAL_FIELDS) -> list[dict]:
    """Every re-sorted read of a running total in one file. The unit the tests drive."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    found: list[dict] = []
    bound = _reordered_bindings(tree)

    for node in ast.walk(tree):
        # `[r[FIELD] for r in sorted(recs, key=...)]`
        if isinstance(node, (ast.ListComp, ast.GeneratorExp, ast.SetComp)):
            if any(_is_reordering(gen.iter) for gen in node.generators):
                for field in _fields_read(node.elt, fields):
                    found.append({"path": path, "line": node.lineno,
                                  "shape": "comprehension-over-reordering", "field": field})
        # `max(recs, key=...)[FIELD]`
        if isinstance(node, ast.Subscript):
            if _is_reordering(node.value):
                for field in _fields_read(node.slice, fields):
                    found.append({"path": path, "line": node.lineno,
                                  "shape": "subscript-of-reordering", "field": field})
            # `s = sorted(recs, ...)` ... `s[-1][FIELD]`
            elif (isinstance(node.slice, ast.Constant)
                  and node.slice.value in fields
                  and _root_name(node.value) in bound):
                found.append({"path": path, "line": node.lineno,
                              "shape": "read-of-reordered-binding", "field": node.slice.value})
    return found


def scan_tree(root: str = REPO_ROOT, dirs: tuple[str, ...] = SCAN_DIRS,
              fields: frozenset[str] = RUNNING_TOTAL_FIELDS,
              require_producer: bool = True) -> list[dict]:
    """Every re-sorted read under `root`, sorted for a stable report.

    FAIL-SILENT GUARD (R15): if not one running-total field is mentioned anywhere in the
    scanned tree, the scan is looking in the wrong place and says so. An unavailable check
    is a FAILED check, never a green one.
    """
    found: list[dict] = []
    mentions_a_field = False
    for d in dirs:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            if "__pycache__" in dirpath:
                continue
            for fn in sorted(filenames):
                if not fn.endswith(".py"):
                    continue
                abs_path = os.path.join(dirpath, fn)
                rel = os.path.relpath(abs_path, root).replace(os.sep, "/")
                if rel in SELF_EXEMPT:
                    continue
                try:
                    source = Path(abs_path).read_text(encoding="utf-8")
                except OSError:
                    continue
                if any(f in source for f in fields):
                    mentions_a_field = True
                found.extend(scan_source(source, rel, fields))
    if require_producer and not mentions_a_field:
        raise OrderCheckUnavailable(
            "no file in the scanned tree mentions a running-total field -- the scan is "
            "looking in the wrong place, not proving the tree is clean"
        )
    return sorted(found, key=lambda v: (v["path"], v["line"], v["shape"], v["field"]))


def _key(violation: dict) -> str:
    return f"{violation['path']}::{violation['shape']}::{violation['field']}"


def counts_by_key(violations: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for v in violations:
        counts[_key(v)] = counts.get(_key(v), 0) + 1
    return counts


def gate_problems(root: str = REPO_ROOT, dirs: tuple[str, ...] = SCAN_DIRS,
                  known: dict[str, dict] | None = None,
                  fields: frozenset[str] = RUNNING_TOTAL_FIELDS,
                  require_producer: bool = True) -> list[str]:
    """What a commit must fail on: a NEW read, one MORE of a frozen read, or a stale entry."""
    known = KNOWN_READS if known is None else known
    found = counts_by_key(scan_tree(root, dirs, fields, require_producer))
    problems: list[str] = []

    for key in sorted(set(found) - set(known)):
        path, shape, field = key.split("::")
        problems.append(
            f"RE-SORTED READ OF A RUNNING TOTAL: {path} reads `{field}` via {shape}. "
            f"`{field}` is a portfolio running total stamped in ACCUMULATION order; a "
            f"re-ordered walk of it reports events that did not happen (2026-08-24: 0 real "
            f"treasury drawdowns became 6,747 published ones). Read it in the order it was "
            f"accumulated, or fold the figure during the run as "
            f"`simulation/settlement_daily.py::TreasuryDrawdown` does."
        )
    for key in sorted(set(known) & set(found)):
        if found[key] > known[key]["count"]:
            path, shape, field = key.split("::")
            problems.append(
                f"ANOTHER RE-SORTED READ: {path} now has {found[key]} `{shape}` reads of "
                f"`{field}`, up from the frozen {known[key]['count']}. The debt is "
                f"shrink-only -- repair the existing read rather than adding one beside it."
            )
    for key in sorted(set(known) - set(found)):
        problems.append(
            f"STALE BASELINE: {key} is frozen as a known re-sorted read but no longer "
            f"exists. Remove it from KNOWN_READS -- a baseline that keeps discharged "
            f"entries stops being countable."
        )
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A running total may only be read in accumulation order.")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--gate", action="store_true",
                    help="commit gate: fail only on a NEW read, an extra read, or a stale entry")
    args = ap.parse_args(argv)

    if args.gate:
        problems = gate_problems()
        if problems:
            print("running-total-order: COMMIT REFUSED.")
            for p_ in problems:
                print(f"  - {p_}")
            return 1
        print(f"running-total-order: no new re-sorted read of a running total "
              f"({len(KNOWN_READS)} known, frozen, shrink-only).")
        return 0

    found = scan_tree()
    if args.json:
        import json
        print(json.dumps({"violations": found, "count": len(found)}, indent=2))
        return 1 if found else 0
    if not found:
        print("running-total-order: every running total is read in accumulation order.")
        return 0
    print(f"running-total-order: {len(found)} re-sorted read(s) of a running total.\n")
    for v in found:
        entry = KNOWN_READS.get(_key(v))
        print(f"  {v['path']}:{v['line']}  {v['field']}  [{v['shape']}]")
        if entry:
            print(f"      frozen: {entry['why']}")
    print("\nA running total is meaningful in the order it was accumulated and in no other.")
    print("Re-ordering one and walking it reports events that did not happen -- on 2026-08-24")
    print("that was 0 real treasury drawdowns published as 6,747, with a RAG rating beside it.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
