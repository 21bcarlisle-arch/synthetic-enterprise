"""The defect: `date.replace(year=d.year +/- n)` raises on 29 February whenever the target year is not a
leap year. The class was fixed instance by instance -- `simulation.customer_events`,
`simulation.arrears_engine`, `run_phase2b`, `company/billing/fit_legacy_register` -- and still crashed a
whole run on 2026-10-02 in `company/pricing/value_based_renewal`, the first time a book drew a term
starting 29 February 2020. Fixed there and in `company/billing/meter_assets`, and made a class here.

The rule, over every module the run executes: a `.replace(year=<arithmetic>)` that keeps the original
day must sit inside a `try` that catches ValueError (or a bare `except`). Two conventions exist for the fallback -- 1 March
(customer_events, fit_legacy_register, the two new sites) and 28 February (arrears_engine) -- and
unifying them is a separate, world-changing decision; this control only forbids the crash.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCOPES = ("company", "saas", "simulation", "sim")


def _catches_value_error(handler: ast.ExceptHandler) -> bool:
    if handler.type is None:
        return True
    names = [handler.type] if not isinstance(handler.type, ast.Tuple) else list(handler.type.elts)
    return any(isinstance(n, ast.Name) and n.id in ("ValueError", "Exception") for n in names)


def _unguarded(path: Path) -> list[int]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    guarded: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try) and any(_catches_value_error(h) for h in node.handlers):
            for stmt in node.body:
                for sub in ast.walk(stmt):
                    guarded.add(id(sub))
    bad = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "replace"
                and any(k.arg == "year" and isinstance(k.value, ast.BinOp) for k in node.keywords)
                # THE CRASH SHAPE KEEPS THE ORIGINAL DAY. A call that sets `day=` explicitly (the
                # 1 March / 28 February fallbacks, a direct-debit day in January) cannot land on a
                # 29 February that does not exist, so it is not this defect.
                and not any(k.arg == "day" for k in node.keywords)
                and id(node) not in guarded):
            bad.append(node.lineno)
    return bad


def _year_replaces(path: Path) -> bool:
    """True if the module makes any `.replace(year=...)` call, read from its syntax tree."""
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "replace"
               and any(k.arg == "year" for k in n.keywords)
               for n in ast.walk(ast.parse(path.read_text(encoding="utf-8"))))


def test_the_census_sees_the_sites_it_governs():
    """Not vacuous: the guarded sites this was written from are found as year arithmetic at all."""
    seen = {p.relative_to(ROOT).as_posix() for s in SCOPES for p in (ROOT / s).rglob("*.py")
            if _year_replaces(p)}
    assert {"company/pricing/value_based_renewal.py", "simulation/arrears_engine.py"} <= seen, seen


def test_no_year_arithmetic_is_outside_a_value_error_guard():
    offenders = {}
    for s in SCOPES:
        for p in (ROOT / s).rglob("*.py"):
            lines = _unguarded(p)
            if lines:
                offenders[p.relative_to(ROOT).as_posix()] = lines
    assert not offenders, f"date.replace(year=...) arithmetic that raises on 29 February: {offenders}"
