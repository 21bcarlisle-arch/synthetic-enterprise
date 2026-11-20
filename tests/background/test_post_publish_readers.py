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


def _live(tmp_path, git_commit):
    """A provenance file serving `git_commit`'s book."""
    f = tmp_path / "publish_provenance.json"
    f.write_text('{"showing_run": {"git_commit": "%s"}}' % git_commit)
    return f


@pytest.fixture(autouse=True)
def _the_live_book_is_the_graded_one(tmp_path, monkeypatch):
    """Every test below grades `abc123def`; the site's real provenance names another book, and
    reading it would make every clause a staleness clause."""
    monkeypatch.setattr(ppr, "LIVE_PROVENANCE_PATH", _live(tmp_path, "abc123def0"))


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


def test_every_page_reader_exists_and_a_publish_runs_it(tmp_path, monkeypatch):
    """The named page readers are real files, and a run with the derived set includes them --
    a name that rotted, or a run that dropped them, would leave the 390 px check unrun."""
    root = ppr.PROJECT_DIR
    assert ppr.PAGE_READERS, "no page reader is named"
    for rel in ppr.PAGE_READERS:
        assert (root / rel).is_file(), f"{rel} is named as a page reader and does not exist"
    monkeypatch.setattr(ppr, "reader_tests", lambda *a, **k: ["tests/x/test_book.py"])
    seen = []
    runner = lambda argv, timeout: seen.append(argv) or SimpleNamespace(returncode=0, stdout=GREEN_OUT)  # noqa: E731
    ppr.run("abc", PARSE, runner=runner, path=tmp_path / "s.json")
    assert seen and all(rel in seen[0] for rel in ppr.PAGE_READERS), seen
    assert "tests/x/test_book.py" in seen[0]


def test_a_grade_of_a_book_the_site_no_longer_serves_reads_as_ungraded(tmp_path):
    """The 6fe7827ab2 book went live on 11 Nov by a salvage landing that never ran the readers,
    and the doorbell kept reporting the 3 Nov book's 7 reds as the live book's for three days.
    One control over the partition: stale-and-red, stale-and-clean, live-and-clean, live unknown."""
    p = tmp_path / "obs.json"
    red = ppr.run("0a6391d186", PARSE, runner=_runner(1, RED_OUT), files=["t.py"], path=p)
    clean = ppr.run("0a6391d186", PARSE, runner=_runner(0, GREEN_OUT), files=["t.py"], path=p)

    for old in (red, clean):
        line = ppr.doorbell_clause(old, live="6fe7827ab2")
        assert line and "UNGRADED" in line and "6fe7827ab2" in line and "0a6391d18" in line
    assert ppr.doorbell_clause(clean, live="0a6391d186") is None
    assert "1 red on publish" in ppr.doorbell_clause(red, live="0a6391d18")  # prefixes agree

    ppr.LIVE_PROVENANCE_PATH = tmp_path / "missing.json"  # restored by the autouse fixture
    assert ppr.live_run_git() is None and ppr.doorbell_clause(clean) is None
    ppr.LIVE_PROVENANCE_PATH = _live(tmp_path, "6fe7827ab2")
    assert "UNGRADED" in ppr.doorbell_clause(clean), "the default reads the site's provenance"


def test_an_unreadable_store_rings_and_an_absent_one_does_not(tmp_path):
    """`load` answers None for a missing store and a corrupt one alike, and the doorbell read that
    None as all-clear. Both priors are asserted reachable: absent stays silent, unreadable rings."""
    absent = tmp_path / "absent.json"
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text('{"outcome": "ran", "reds": ["FAILED t')
    assert ppr.doorbell_clause(path=absent, live="abc1234567") is None
    clause = ppr.doorbell_clause(path=corrupt, live="abc1234567")
    assert clause and "unreadable" in clause and "UNGRADED" in clause


def test_a_disposed_red_still_rings_and_the_next_publish_drops_the_disposition(tmp_path):
    """The 6af7fd0bfd book's contracted-tariff red was fixed in source two hours after that
    publish (c6695cd8db) and the doorbell redrew it every tick, each re-tracing it from scratch.
    A disposition says why it stands without silencing it; `run` rewrites the store whole, so the
    next publish drops it. The refusal partition: a red store takes one, a clean one does not.
    MUTATION: drop the disposition suffix from `doorbell_clause` and the reason never prints."""
    p = tmp_path / "obs.json"
    ppr.run("6af7fd0bfd", PARSE, runner=_runner(1, RED_OUT), files=["t.py"], path=p)
    reason = "fixed in source at c6695cd8db; re-ledgered book reads 0 disagree"
    assert ppr.dispose(reason, path=p) == reason
    line = ppr.doorbell_clause(path=p, live="6af7fd0bfd")
    assert "1 red on publish" in line and reason in line, line
    with pytest.raises(SystemExit):
        ppr.dispose("too short", path=p)

    ppr.run("6af7fd0bfd", PARSE, runner=_runner(0, GREEN_OUT), files=["t.py"], path=p)
    assert "disposition" not in ppr.load(p)
    with pytest.raises(SystemExit, match="no red"):
        ppr.dispose(reason, path=p)
