"""Tests for tools/capability_index.py — AO1, the derived reuse surface.

The derivation is the easy half. An index is a textbook FAIL-OPEN control: one
that under-reports does not look broken, it looks like a small codebase, and
the builder who reads "nothing to reuse" then writes the duplicate the index
existed to prevent. So most of what follows is R15 work — proving each
integrity check FIRES on its own named defect, by mutating a real tree rather
than by asserting that it would.

Three killer patterns, each answered here:

  TAUTOLOGY   -- the coverage check must not be the row walk compared with
                 itself. `test_coverage_oracle_is_independent_of_the_row_walk`
                 breaks the walk while leaving git's view intact, and the
                 check must still fire.
  FAIL-OPEN   -- `test_vacuity_*` and `test_coverage_hole_*`: an index that
                 silently shrinks to nothing must FAIL, not report calm.
  FAIL-SILENT -- `test_missing_oracle_is_a_failure_not_a_pass`: when git
                 cannot answer, the tool returns rc 2, never rc 0.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools import capability_index as ci

REPO = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# a small real repo to mutate — a fixture, so the mutations below are genuine
# code changes and not monkeypatched return values
# ---------------------------------------------------------------------------

@pytest.fixture
def tree(tmp_path):
    """A miniature repo with a wired module, an orphan, an entrypoint, a test."""
    (tmp_path / "company" / "billing").mkdir(parents=True)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "company" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "company" / "billing" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "company" / "billing" / "working_days.py").write_text(
        '"""Canonical UK working-day arithmetic. Bank holidays and settlement offsets."""\n'
        "def add_working_days(d, n):\n    return d\n",
        encoding="utf-8",
    )
    (tmp_path / "company" / "billing" / "engine.py").write_text(
        '"""Bill calculation from meter reads."""\n'
        "from company.billing.working_days import add_working_days\n",
        encoding="utf-8",
    )
    (tmp_path / "company" / "billing" / "abandoned.py").write_text(
        '"""A register nothing imports any more."""\nVALUE = 1\n',
        encoding="utf-8",
    )
    (tmp_path / "tools" / "runner.py").write_text(
        '"""Command that runs the billing engine."""\n'
        "import company.billing.engine\n"
        'if __name__ == "__main__":\n    pass\n',
        encoding="utf-8",
    )
    (tmp_path / "tests" / "test_engine.py").write_text(
        "from company.billing.engine import *\n", encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    return tmp_path


def rows_by_module(rows):
    return {r["module"]: r for r in rows}


# ---------------------------------------------------------------------------
# derivation: the four questions a row answers
# ---------------------------------------------------------------------------

def test_row_carries_plain_words_from_the_docstring(tree):
    rows = rows_by_module(ci.build_rows(tree))
    assert rows["company.billing.working_days"]["plain_words"] == (
        "Canonical UK working-day arithmetic."
    )


def test_module_without_docstring_is_a_visible_row_not_a_skip(tree):
    (tree / "company" / "billing" / "silent.py").write_text("X = 1\n", encoding="utf-8")
    rows = rows_by_module(ci.build_rows(tree))
    assert "company.billing.silent" in rows, "an undescribed capability must still get a row"
    assert rows["company.billing.silent"]["plain_words"] is None
    assert rows["company.billing.silent"] in ci.unnamed(ci.build_rows(tree))


def test_status_is_derived_from_real_import_edges(tree):
    rows = rows_by_module(ci.build_rows(tree))
    assert rows["company.billing.working_days"]["status"] == "wired"
    assert rows["company.billing.working_days"]["callers"] == ["company.billing.engine"]
    assert rows["company.billing.abandoned"]["status"] == "orphan"
    assert rows["tools.runner"]["status"] == "entrypoint"


def test_evidence_lists_the_tests_that_actually_import_it(tree):
    rows = rows_by_module(ci.build_rows(tree))
    assert rows["company.billing.engine"]["evidence"] == ["tests/test_engine.py"]
    assert rows["company.billing.abandoned"]["evidence"] == []


def test_namespace_only_package_is_not_reported_as_an_orphan(tree):
    rows = rows_by_module(ci.build_rows(tree))
    assert rows["company"]["status"] == "package"
    assert rows["company"] not in ci.unnamed(ci.build_rows(tree))


def test_a_module_invoked_by_path_is_not_an_orphan(tree):
    """The false-orphan reading that would retire a live mechanism.

    `background_worker.py` runs `run_queued_tasks.py` with `exec(open(...))`.
    No import graph can see that edge, and the first run of this index called
    that live dispatcher an orphan.
    """
    (tree / "tools" / "launcher.py").write_text(
        '"""Launches the abandoned register as a subprocess."""\n'
        'import subprocess\n'
        'subprocess.run(["python3", "company/billing/abandoned.py"])\n',
        encoding="utf-8",
    )
    rows = rows_by_module(ci.build_rows(tree))
    assert rows["company.billing.abandoned"]["status"] == "wired"
    assert rows["company.billing.abandoned"]["callers"] == ["tools.launcher (by path)"]


# ---------------------------------------------------------------------------
# the query: the fail-open that matters most
# ---------------------------------------------------------------------------

def test_find_matches_words_against_identifier_names(tree):
    """The real miss: "working day" typed at a module called `working_days`.

    The first run of this tool answered 0 rows for a capability that exists in
    the repo. An index that answers "nothing to reuse" to the question it was
    built for does not merely fail to help — it authorises the duplicate.
    """
    rows = ci.build_rows(tree)
    hits = ci.find(rows, "working day")
    assert [r["module"] for r in hits][:1] == ["company.billing.working_days"]


def test_find_matches_the_docstring_not_only_the_name(tree):
    rows = ci.build_rows(tree)
    assert [r["module"] for r in ci.find(rows, "bank holidays")] == [
        "company.billing.working_days"
    ]


def test_find_ranks_name_matches_above_prose_matches(tree):
    (tree / "company" / "billing" / "invoice.py").write_text(
        '"""Invoices, which are produced on working days."""\n', encoding="utf-8",
    )
    hits = ci.find(ci.build_rows(tree), "working_days")
    assert hits[0]["module"] == "company.billing.working_days"


def test_find_on_absent_capability_returns_nothing(tree):
    """The index must be able to say NO — a matcher that hits everything is
    the mirror defect of one that hits nothing, and equally useless."""
    assert ci.find(ci.build_rows(tree), "carbon certificate auction") == []


# ---------------------------------------------------------------------------
# R15 — vacuity
# ---------------------------------------------------------------------------

def test_vacuity_guard_fires_on_an_empty_index(tree, monkeypatch):
    monkeypatch.setattr(ci, "ROW_FLOOR", 3)
    findings = ci.integrity_findings([], tree)
    assert any("below the floor" in f for f in findings), (
        "zero rows must FAIL -- 'nothing to reuse' is the fail-open that causes "
        "the duplicate build"
    )


def test_vacuity_floor_fires_on_a_shrunken_index_that_still_covers_every_root(tree,
                                                                              monkeypatch):
    """The floor must be witnessed ALONE, not through the per-root check.

    Both guards emit findings tagged VACUITY, so a test asserting only that tag
    passes on either one. Deleting the floor outright left this file green
    until this test existed -- the union-metric blindness, reappearing inside
    an R15 test. Here every declared root still has rows and coverage is whole,
    so the floor is the only guard that can speak.
    """
    rows = ci.build_rows(tree)
    monkeypatch.setattr(ci, "ROW_FLOOR", len(rows) + 1)
    findings = ci.integrity_findings(rows, tree)
    assert [f for f in findings if "below the floor" in f], findings
    assert not [f for f in findings if "declared root" in f]


def test_vacuity_guard_fires_when_one_declared_root_stops_being_covered(tree, monkeypatch):
    monkeypatch.setattr(ci, "ROW_FLOOR", 1)
    rows = [r for r in ci.build_rows(tree) if not r["path"].startswith("tools/")]
    findings = ci.integrity_findings(rows, tree)
    assert any("declared root tools/" in f for f in findings)


def test_healthy_index_reports_no_findings(tree, monkeypatch):
    """The control must be able to PASS on a good tree, or it is a wedge, not a check."""
    monkeypatch.setattr(ci, "ROW_FLOOR", 3)
    assert ci.integrity_findings(ci.build_rows(tree), tree) == []


# ---------------------------------------------------------------------------
# R15 — coverage, and its independence
# ---------------------------------------------------------------------------

def test_coverage_hole_fires_when_a_known_capability_goes_missing(tree, monkeypatch):
    """The atom's own named mutation: a KNOWN-EXISTING capability disappears."""
    monkeypatch.setattr(ci, "ROW_FLOOR", 1)
    rows = [r for r in ci.build_rows(tree) if r["module"] != "company.billing.working_days"]
    findings = ci.integrity_findings(rows, tree)
    assert any("COVERAGE HOLE" in f and "working_days" in f for f in findings)


def test_coverage_oracle_is_independent_of_the_row_walk(tree, monkeypatch):
    """TAUTOLOGY killer: break the walk, leave git intact, the check must fire.

    If coverage were `walk == walk` it would pass by construction and prove
    nothing. Here the walk is made to skip a whole root while git still lists
    its files, and the finding must appear.
    """
    monkeypatch.setattr(ci, "ROW_FLOOR", 1)
    monkeypatch.setattr(ci, "DECLARED_ROOTS", ("company",))
    rows = ci.build_rows(tree)
    assert all(not r["path"].startswith("tools/") for r in rows)
    findings = ci.integrity_findings(rows, tree)
    assert any("UNCLASSIFIED ROOT" in f and "tools" in f for f in findings), (
        "git still lists tools/runner.py; a coverage check derived from the same "
        "walk as the rows would have agreed with the walk and stayed silent"
    )


def test_untracked_new_top_level_package_is_not_silently_unindexed(tree):
    """A new package must not be able to land invisible to the reuse surface."""
    (tree / "trading").mkdir()
    (tree / "trading" / "book.py").write_text('"""Trade book."""\n', encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tree, check=True)
    findings = ci.integrity_findings(ci.build_rows(tree), tree)
    assert any("UNCLASSIFIED ROOT" in f and "trading" in f for f in findings)


# ---------------------------------------------------------------------------
# R15 — fail-silent
# ---------------------------------------------------------------------------

def test_missing_oracle_is_a_failure_not_a_pass(tmp_path):
    """An unavailable check is a FAILED check: no git, no clean verdict."""
    (tmp_path / "company").mkdir()
    with pytest.raises(RuntimeError):
        ci.tracked_python_files(tmp_path)


def test_empty_oracle_cannot_witness_an_empty_index(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    with pytest.raises(RuntimeError, match="0 Python files"):
        ci.tracked_python_files(tmp_path)


def test_unparseable_file_is_a_row_and_a_finding_never_a_silent_skip(tree, monkeypatch):
    monkeypatch.setattr(ci, "ROW_FLOOR", 1)
    (tree / "company" / "billing" / "broken.py").write_text(
        "def oops(:\n", encoding="utf-8",
    )
    subprocess.run(["git", "add", "-A"], cwd=tree, check=True)
    rows = ci.build_rows(tree)
    row = rows_by_module(rows)["company.billing.broken"]
    assert row["status"] == "unparsed" and row["note"]
    findings = ci.integrity_findings(rows, tree)
    assert any("UNPARSED" in f for f in findings)


# ---------------------------------------------------------------------------
# the live repo, and the CLI contract
# ---------------------------------------------------------------------------

def test_live_repo_index_is_healthy_and_substantial():
    rows = ci.build_rows(REPO)
    assert len(rows) > ci.ROW_FLOOR
    assert ci.integrity_findings(rows, REPO) == []


def test_live_repo_finds_the_named_duplication_evidence():
    """The director's own evidence class: a from-scratch working-day calculator
    was written while `company/compliance/working_days.py` already existed."""
    hits = ci.find(ci.build_rows(REPO), "working day")
    assert "company.compliance.working_days" in {r["module"] for r in hits}


def test_cli_exit_codes_distinguish_clean_from_could_not_run(tmp_path):
    clean = subprocess.run(
        [sys.executable, "tools/capability_index.py", "--check"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert clean.returncode == 0, clean.stderr

    out = tmp_path / "index.json"
    dumped = subprocess.run(
        [sys.executable, "tools/capability_index.py", "--out", str(out)],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert dumped.returncode == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["row_count"] == len(payload["rows"]) > ci.ROW_FLOOR
    assert payload["integrity_findings"] == []
    assert {"module", "path", "plain_words", "status", "evidence", "demo"} <= set(
        payload["rows"][0]
    )


def test_cli_returns_two_when_it_cannot_run(tmp_path, monkeypatch):
    """rc 2 must be reachable and distinct from rc 0, or 'could not run' reads
    as 'clean' the first time the oracle is unavailable."""
    monkeypatch.setattr(ci, "build_rows", lambda *a, **k: (_ for _ in ()).throw(
        RuntimeError("oracle unavailable")))
    assert ci.main(["--check"]) == 2
