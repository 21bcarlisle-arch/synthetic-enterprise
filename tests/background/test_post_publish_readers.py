"""After a publish, the tests that read what it published are run, and a red reaches the doorbell.

The defect (2248e3baf, 2026-10-13): a publish turned three real-book controls red and nothing saw it
for three days, because the gate grades HEAD before the new artefacts exist and both whole-suite
runs after it never finish.
"""
from __future__ import annotations

import subprocess
from types import SimpleNamespace

import pytest

from background import post_publish_readers as ppr
from background.process_run_complete import _parse_failed_node_ids as PARSE

RED_OUT = (
    "F.\n"
    "=========================== short test summary info ============================\n"
    "FAILED tests/x/test_book.py::test_closes - AssertionError: 12 accounts\n"
    "1 failed, 1 passed in 2.0s\n"
)
GREEN_OUT = "..\n2 passed in 1.0s\n"


def _runner(rc, out):
    return lambda argv, timeout: SimpleNamespace(returncode=rc, stdout=out)


def test_the_derived_set_holds_both_controls_the_2248e3baf_publish_turned_red():
    """Keyed to the property -- the two named readers are found -- not to today's count. The
    statement control is the one hop 2 exists for: it never spells the ledger's path, only
    `sx.LEDGER_PATH`, and a literal-only grep missed it."""
    found = set(ppr.reader_tests())
    assert "tests/tools/test_the_ledger_and_the_pnl_write_off_agree_on_the_real_book.py" in found
    assert "tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py" in found


def test_each_hop_admits_its_own_reader_and_neither_admits_a_bystander(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "ledger_mod.py").write_text(
        'LEDGER_PATH = PROJECT / "docs" / "state" / "billing_ledger.json"\nOTHER = 1\n')
    t = tmp_path / "tests"
    t.mkdir()
    (t / "test_literal.py").write_text('P = "docs/state/billing_ledger.json"\n')
    (t / "test_joined.py").write_text('P = ROOT / "state" / "billing_ledger.json"\n')
    (t / "test_hop2.py").write_text("from tools import ledger_mod as lm\nx = lm.LEDGER_PATH\n")
    (t / "test_other_const.py").write_text("from tools import ledger_mod\nx = ledger_mod.OTHER\n")
    (t / "test_bystander.py").write_text("x = 1\n")
    (t / "test_prose.py").write_text(
        '"""Once read docs/state/billing_ledger.json."""\n# docs/state/billing_ledger.json\n')
    (tmp_path / "tools" / "rel_mod.py").write_text(
        'LEDGER_REL = "docs/state/billing_ledger.json"\n')
    (t / "test_rel_const.py").write_text("from tools import rel_mod\nx = rel_mod.LEDGER_REL\n")
    found = ppr.reader_tests(artefacts=("docs/state/billing_ledger.json",), root=tmp_path)
    assert found == ["tests/test_hop2.py", "tests/test_joined.py", "tests/test_literal.py"]


def test_every_outcome_is_reachable_and_only_a_clean_run_is_silent(tmp_path):
    """One control over the whole partition: red, clean, unreadable, timed out, nothing derived."""
    p = tmp_path / "obs.json"
    red = ppr.run("abc123def", PARSE, runner=_runner(1, RED_OUT), files=["t.py"], path=p)
    clean = ppr.run("abc123def", PARSE, runner=_runner(0, GREEN_OUT), files=["t.py"], path=p)
    unreadable = ppr.run("abc123def", PARSE, runner=_runner(137, ""), files=["t.py"], path=p)

    def _hang(argv, timeout):
        raise subprocess.TimeoutExpired(argv, timeout)
    timed_out = ppr.run("abc123def", PARSE, runner=_hang, files=["t.py"], path=p)
    empty = ppr.run("abc123def", PARSE, runner=_runner(0, GREEN_OUT), files=[], path=p)

    assert red["reds"] and not clean["reds"] and unreadable["reds"][0].startswith("UNREADABLE")
    assert (timed_out["outcome"], empty["outcome"]) == (ppr.TIMED_OUT, ppr.UNAVAILABLE)

    assert "test_book.py::test_closes" in ppr.doorbell_clause(red)
    assert ppr.doorbell_clause(clean) is None
    assert "UNREADABLE" in ppr.doorbell_clause(unreadable)
    assert "UNGRADED" in ppr.doorbell_clause(timed_out)
    assert "UNGRADED" in ppr.doorbell_clause(empty)
    assert ppr.load(p)["outcome"] == ppr.UNAVAILABLE, "the last run is what the store holds"


def test_the_store_is_not_the_census_store():
    """Folding a partial run into the census observation reads every unreached red as fixed."""
    from background import head_red_register
    assert ppr.OBSERVED_PATH != head_red_register.OBSERVED_PATH


def test_the_publish_step_runs_the_readers_and_cannot_raise(tmp_path, monkeypatch):
    from background import process_run_complete as prc
    monkeypatch.setattr(ppr, "OBSERVED_PATH", tmp_path / "obs.json")
    monkeypatch.setattr(ppr, "reader_tests", lambda *a, **k: ["t.py"])
    monkeypatch.setattr(prc, "remainder_budget_seconds", lambda *a, **k: 600)
    state = prc.run_post_publish_readers_step("abc123def", runner=_runner(1, RED_OUT))
    assert state["reds"] and ppr.load()["git_hash"] == "abc123def"

    monkeypatch.setattr(prc, "remainder_budget_seconds", lambda *a, **k: 0)
    assert prc.run_post_publish_readers_step("abc123def", runner=_runner(1, RED_OUT)) is None

    def _boom(*a, **k):
        raise RuntimeError("x")
    monkeypatch.setattr(prc, "remainder_budget_seconds", _boom)
    assert prc.run_post_publish_readers_step("abc123def") is None


def test_a_red_reader_run_reaches_the_supervisors_doorbell(tmp_path, monkeypatch):
    from background import supervisor
    p = tmp_path / "obs.json"
    ppr.run("abc123def", PARSE, runner=_runner(1, RED_OUT), files=["t.py"], path=p)
    monkeypatch.setattr(ppr, "OBSERVED_PATH", p)
    line = supervisor._differentiated_staging(["SOME_FINDING.md"])
    assert "POST-PUBLISH READERS: 1 red" in line and "SOME_FINDING.md" in line

    ppr.run("abc123def", PARSE, runner=_runner(0, GREEN_OUT), files=["t.py"], path=p)
    assert "POST-PUBLISH" not in supervisor._differentiated_staging(["SOME_FINDING.md"])


@pytest.mark.parametrize("bad", [None, {}])
def test_no_store_is_silent(bad):
    assert ppr.doorbell_clause(bad or None, path=ppr.PROJECT_DIR / "nonexistent.json") is None
