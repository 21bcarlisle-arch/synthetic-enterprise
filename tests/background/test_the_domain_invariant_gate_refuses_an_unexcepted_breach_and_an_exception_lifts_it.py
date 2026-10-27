"""The publisher grades every run's book against the domain invariants (ruling of 26 Oct, step 4).

The defects these tests name:
  * a gate that refuses nothing: a planted breach, enforced, must refuse and name the invariant
    and its count (a guard that passes everything passes every other test here);
  * an exception that does not lift, or one that lifts without saying why, when, and what retires it;
  * an exception that hides a defect grown past the count it was filed for;
  * report-only mode that leaves no count on the surface;
  * an ungradable book read as a clean one while enforcing;
  * the refusal not wired ahead of the publish in the publisher's own run path.
"""
from __future__ import annotations

import ast
import inspect

import pytest

from background import process_run_complete as prc
from tests.tools.test_the_domain_invariant_runner_reads_only_the_raw_export_and_every_evaluator_can_fire import (  # noqa: E501
    INVARIANTS,
    _clean_book,
)
from tools import domain_invariant_runner as runner

EXCEPTION = {"invariant": "INV_FUEL_IDENTIFIER", "scope": "account E, March 2020",
             "reason": "planted", "filed": "2026-10-27", "retired_by": "the fix that unplants it"}


def _planted_breach():
    book = _clean_book()
    book["E"]["periods"][2]["mprn"] = "9"   # an electricity bill carrying a gas supply point
    return book


@pytest.fixture
def grade(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "log", lambda msg: None)
    monkeypatch.setattr(prc, "DOMAIN_INVARIANT_TABLE", tmp_path / "DOMAIN_INVARIANTS.md")
    monkeypatch.setattr(prc, "DOMAIN_INVARIANT_JSON", tmp_path / "domain_invariants.json")
    monkeypatch.setattr(runner, "load_invariants", lambda *a, **k: INVARIANTS)

    def _grade(book, register):
        monkeypatch.setattr(runner, "load_book", lambda *a, **k: book)
        reg = tmp_path / "exceptions.yaml"
        import yaml
        reg.write_text(yaml.safe_dump(register))
        ok, reason = prc._domain_invariant_gate_permits_publish(
            "abc", ledger_path=tmp_path / "unused.json", register_path=reg)
        return ok, reason, (tmp_path / "DOMAIN_INVARIANTS.md").read_text()
    return _grade


def test_the_whole_partition_is_reachable(grade):
    """Refuses, lifts, and permits a clean book: each leg can be taken."""
    refused = grade(_planted_breach(), {"enforce": True, "exceptions": []})
    lifted = grade(_planted_breach(), {"enforce": True, "exceptions": [EXCEPTION]})
    clean = grade(_clean_book(), {"enforce": True, "exceptions": []})
    assert not refused[0] and lifted[0] and clean[0], (refused[:2], lifted[:2], clean[:2])


def test_a_planted_breach_refuses_and_the_refusal_names_the_invariant_and_its_count(grade):
    ok, reason, table = grade(_planted_breach(), {"enforce": True, "exceptions": []})
    assert not ok
    assert "INV_FUEL_IDENTIFIER 1 (no exception)" in reason, reason
    assert "ENFORCED" in table and "INV_FUEL_IDENTIFIER" in table


def test_an_exception_lifts_only_when_it_says_scope_reason_date_and_retirement(grade):
    for field in runner.EXCEPTION_FIELDS:
        partial = {k: v for k, v in EXCEPTION.items() if k != field}
        ok, reason, table = grade(_planted_breach(), {"enforce": True, "exceptions": [partial]})
        assert not ok, "an exception without `{}` lifted the refusal".format(field)
        assert "lacks {}".format(field) in table
    ok, _, table = grade(_planted_breach(), {"enforce": True, "exceptions": [EXCEPTION]})
    assert ok and "excepted until the fix that unplants it" in table


def test_an_excepted_defect_that_grows_past_its_ceiling_refuses_again(grade):
    book = _planted_breach()
    book["E"]["periods"][3]["mprn"] = "9"
    capped = dict(EXCEPTION, max_breached=1)
    ok, reason, _ = grade(book, {"enforce": True, "exceptions": [capped]})
    assert not ok and "exceed the exception's max_breached 1" in reason, reason


def test_report_only_permits_and_still_puts_the_refusal_on_the_surface(grade):
    ok, reason, table = grade(_planted_breach(),
                              {"enforce": False, "report_only_because": "the grade has not landed",
                               "exceptions": []})
    assert ok and reason is None
    first = table.splitlines()[2]
    assert "1 unexcepted breach(es)" in first and "REPORT-ONLY" in first, first
    assert "the grade has not landed" in first


def test_an_ungradable_book_refuses_while_enforcing(grade, monkeypatch):
    def boom(*a, **k):
        raise ValueError("no ledger")
    monkeypatch.setattr(runner, "load_book", boom)
    ok, reason = prc._domain_invariant_gate_permits_publish(
        "abc", ledger_path=prc.DOMAIN_INVARIANT_JSON, register_path=prc.DOMAIN_INVARIANT_JSON)
    assert not ok and "could not grade" in reason, reason   # unreadable register enforces


def test_the_committed_register_is_well_formed():
    register = runner.load_exceptions()
    assert isinstance(register.get("enforce"), bool)
    assert register["enforce"] or register.get("report_only_because")
    ids = {i["id"] for i in runner.load_invariants()}
    for e in register.get("exceptions") or ():
        assert not [f for f in runner.EXCEPTION_FIELDS if not e.get(f)], e
        assert e["invariant"] in ids, e


def test_the_publisher_refuses_on_the_gate_before_its_suite_runs():
    """The refusal is wired: the gate's verdict is read and returns, ahead of run_fast_tests."""
    tree = ast.parse(inspect.getsource(prc))
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef):
            continue
        calls = {n.func.id: n.lineno for n in ast.walk(fn)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        if "run_fast_tests" in calls and "_domain_invariant_gate_permits_publish" in calls:
            break
    else:
        pytest.fail("no publisher function calls both the invariant gate and run_fast_tests")
    gate_line, suite_line = calls["_domain_invariant_gate_permits_publish"], calls["run_fast_tests"]
    assert gate_line < suite_line
    refusing = [n for n in ast.walk(fn) if isinstance(n, ast.If) and gate_line < n.lineno < suite_line
                and any(isinstance(b, ast.Return) for b in n.body)]
    assert refusing, "the gate's verdict is computed and nothing returns on it"
