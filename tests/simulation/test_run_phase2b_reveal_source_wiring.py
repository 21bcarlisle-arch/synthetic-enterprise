"""Source-wiring guard for W1_reveal_over_time -- the point-in-time blindfold
AT THE SOURCE, not just in company/ code.

Every existing reveal-boundary test lives in company/interfaces/ (the
PointInTimeView / BitemporalEventLog mechanism) or RE-IMPLEMENTS the wiring in
its own helper (tests/simulation/test_run_phase2b.py::_piv_at builds its own
`decision_time`). None of them exercises the ACTUAL construction inside
simulation/run_phase2b.py, so a regression there -- the two hedge-decision call
sites constructing `PointInTimeView(decision_time=...)` -- would leak foresight
into the hedge decision and NO test would fail:

  * `time.min` -> `time.max`  : a decision "at term_start" would see the whole
    of term_start's own settlement day, incl. date-D's own daily-mean spot
    price (the exact same-day leak the 2026-07-13 expert-hour fix closed at the
    log level, re-opened here at the wiring level).
  * `term_start_str` -> `term_end_str` : the decision would be dated at the END
    of the term, seeing the entire term's realised prices before deciding how
    to hedge it -- gross look-ahead.

This is the atom's own stated boundary ("at the source"), and it is where the
class-level mutation tests do not reach. The guard below parses run_phase2b.py's
AST, resolves each `PointInTimeView(decision_time=X)` back to X's assignment,
and asserts the reveal boundary is set at START-OF-DAY on a *term_start*
variable. R15: proven to FIRE on both named defects by re-running the same
analyzer over a mutated copy of the live source.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

_SOURCE_PATH = Path(__file__).resolve().parents[2] / "simulation" / "run_phase2b.py"


def _analyze(source: str) -> list[dict]:
    """Find every `PointInTimeView(decision_time=<Name>)` construction and
    resolve <Name> back to its `datetime.combine(date.fromisoformat(<X>), <T>)`
    assignment, reporting the reveal-boundary properties actually wired in.

    Independent of the mechanism under test: it reads the SOURCE's own wiring
    expression, never PointInTimeView's behaviour, so it cannot pass by the
    same bug it checks (R15 tautology guard)."""
    tree = ast.parse(source)

    # Map simple `name = <Call>` assignments -> the RHS Call node.
    assigns: dict[str, ast.AST] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            tgt = node.targets[0]
            if isinstance(tgt, ast.Name):
                assigns[tgt.id] = node.value

    def _attr_name(n: ast.AST) -> str | None:
        return n.attr if isinstance(n, ast.Attribute) else None

    findings: list[dict] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and _attr_or_id(node.func) == "PointInTimeView"):
            continue
        dt_kw = next((k for k in node.keywords if k.arg == "decision_time"), None)
        f: dict = {"has_decision_time": dt_kw is not None,
                   "uses_start_of_day": False, "bound_to_term_start": False,
                   "resolved": False}
        findings.append(f)
        if dt_kw is None or not isinstance(dt_kw.value, ast.Name):
            continue
        rhs = assigns.get(dt_kw.value.id)
        # Must be datetime.combine(<date_expr>, <time_expr>)
        if not (isinstance(rhs, ast.Call) and _attr_name(rhs.func) == "combine"
                and len(rhs.args) == 2):
            continue
        f["resolved"] = True
        date_expr, time_expr = rhs.args
        # Reveal instant must be START of the day (time.min), never time.max.
        f["uses_start_of_day"] = _attr_name(time_expr) == "min"
        # Date source must be a *term_start* variable (via date.fromisoformat).
        if (isinstance(date_expr, ast.Call) and _attr_name(date_expr.func) == "fromisoformat"
                and date_expr.args and isinstance(date_expr.args[0], ast.Name)):
            f["bound_to_term_start"] = "term_start" in date_expr.args[0].id
    return findings


def _attr_or_id(n: ast.AST) -> str | None:
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.Attribute):
        return n.attr
    return None


@pytest.fixture(scope="module")
def live_findings() -> list[dict]:
    return _analyze(_SOURCE_PATH.read_text())


def test_source_constructs_at_least_the_two_hedge_pit_views(live_findings):
    """The elec and gas VaR-hedge decision paths each construct a PIV."""
    assert len(live_findings) >= 2, (
        "expected at least the electricity+gas hedge-decision PointInTimeView "
        f"constructions in run_phase2b.py, found {len(live_findings)}"
    )


def test_every_pit_decision_time_is_resolvable(live_findings):
    for f in live_findings:
        assert f["has_decision_time"], "a PointInTimeView is built without decision_time"
        assert f["resolved"], (
            "a PointInTimeView.decision_time could not be traced to a "
            "datetime.combine(date.fromisoformat(...), ...) assignment -- the "
            "guard can no longer see the reveal boundary; re-check the wiring"
        )


def test_reveal_boundary_is_start_of_term_start_day(live_findings):
    """The core source-wiring invariant: every hedge decision reads history as
    of START-OF-DAY on its TERM_START -- never term_end, never end-of-day."""
    for f in live_findings:
        assert f["uses_start_of_day"], (
            "a hedge-decision PointInTimeView is dated at end-of-day (time.max) "
            "not start-of-day (time.min) -- term_start's own settlement day "
            "would leak into the decision (same-day look-ahead)"
        )
        assert f["bound_to_term_start"], (
            "a hedge-decision PointInTimeView is NOT bound to a term_start "
            "variable -- the reveal boundary has drifted off term start "
            "(look-ahead risk)"
        )


# --- R15: the guard must FIRE on each named defect (mutation both ways) ---

def test_MUTATION_end_of_day_leak_is_caught():
    """time.min -> time.max in the decision_time construction re-opens the
    same-day leak; the guard must flag it (else it proves nothing)."""
    mutant = _SOURCE_PATH.read_text().replace(
        "datetime.combine(date.fromisoformat(term_start_str), time.min)",
        "datetime.combine(date.fromisoformat(term_start_str), time.max)",
    )
    assert mutant != _SOURCE_PATH.read_text(), (
        "mutation was a no-op -- the exact decision_time expression the guard "
        "targets is no longer present verbatim; update this mutation string"
    )
    findings = _analyze(mutant)
    assert findings, "mutant produced no PIT findings -- guard blind"
    assert any(not f["uses_start_of_day"] for f in findings), (
        "the end-of-day mutant slipped past test_reveal_boundary_is_start_of_"
        "term_start_day -- the start-of-day control does not actually fire"
    )


def test_MUTATION_term_end_dating_leak_is_caught():
    """term_start_str -> term_end_str dates the decision at the END of the term,
    letting the whole term's realised prices leak in; the guard must flag it."""
    mutant = _SOURCE_PATH.read_text().replace(
        "datetime.combine(date.fromisoformat(term_start_str), time.min)",
        "datetime.combine(date.fromisoformat(term_end_str), time.min)",
    )
    assert mutant != _SOURCE_PATH.read_text(), "term_start mutation was a no-op"
    findings = _analyze(mutant)
    assert findings, "mutant produced no PIT findings -- guard blind"
    assert any(not f["bound_to_term_start"] for f in findings), (
        "the term_end mutant slipped past the bound_to_term_start control -- "
        "the reveal boundary is not actually pinned to term start"
    )
