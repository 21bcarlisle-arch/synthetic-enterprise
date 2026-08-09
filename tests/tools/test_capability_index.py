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


# ---------------------------------------------------------------------------
# orphan disposition (KNIFE pass 4) — R15 on the ruling, not just on the index
#
# The register is a second fail-open surface stacked on the first. An index
# that under-reports looks like a small codebase; a REGISTER that under-reports
# looks like a tidy one — every orphan ruled, because the ones nobody ruled on
# were never counted. So each check below is mutated into firing on a real
# tree, and the healthy case is asserted too: a control that can only fail is
# worth as little as one that can only pass.
# ---------------------------------------------------------------------------

def write_register(root, body):
    """Put a register on disk where `disposition_findings` looks for it."""
    path = root / ci.DISPOSITION_REGISTER
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# register\n\n<!-- ORPHAN-DISPOSITIONS\n" + body + "\nORPHAN-DISPOSITIONS -->\n",
        encoding="utf-8",
    )
    return path


HEALTHY_ROW = ("company.billing.abandoned | unhooked | tools.runner | "
               "a register nothing imports; no importer")


def fires(findings, marker):
    return [f for f in findings if f.startswith(marker)]


def test_the_healthy_register_produces_no_findings(tree):
    """The control must be able to PASS on a correct tree, or every mutation
    below proves nothing but that it always fires."""
    write_register(tree, HEALTHY_ROW)
    assert ci.disposition_findings(ci.build_rows(tree), tree) == []


def test_an_orphan_with_no_ruling_fires(tree):
    """The exit criterion itself: `every orphan carries a disposition`."""
    write_register(tree, "# nothing ruled on")
    findings = ci.disposition_findings(ci.build_rows(tree), tree)
    assert fires(findings, "VACUOUS REGISTER")
    assert any("company.billing.abandoned" in f for f in fires(findings, "UNDISPOSITIONED"))


def test_a_new_orphan_appearing_later_fires(tree):
    """The 259th orphan. The register is complete today; a module that loses
    its caller tomorrow must break the check, which is the whole reason this
    is a mechanism and not a one-off audit."""
    write_register(tree, HEALTHY_ROW)
    assert ci.disposition_findings(ci.build_rows(tree), tree) == []
    (tree / "tools" / "runner.py").write_text(
        '"""Command that runs nothing in particular."""\n'
        'if __name__ == "__main__":\n    pass\n', encoding="utf-8")
    findings = ci.disposition_findings(ci.build_rows(tree), tree)
    assert any("company.billing.engine" in f for f in fires(findings, "UNDISPOSITIONED"))


def test_a_missing_register_is_a_failed_check_not_a_clean_one(tree):
    """FAIL-SILENT. An unavailable ruling must never read as 'no orphans
    outstanding' — that is the shape that lets the whole surface disappear."""
    findings = ci.disposition_findings(ci.build_rows(tree), tree)
    assert fires(findings, "DISPOSITION REGISTER UNAVAILABLE")
    assert "1 company-side orphan(s) are therefore unruled" in findings[0]


def test_a_ruling_that_outlives_its_subject_fires(tree):
    """STALE both ways: the module got wired, and the module went away."""
    write_register(tree, HEALTHY_ROW + "\ncompany.billing.working_days | unhooked | "
                                       "tools.runner | already wired")
    findings = ci.disposition_findings(ci.build_rows(tree), tree)
    assert any("is now wired" in f for f in fires(findings, "STALE DISPOSITION"))

    write_register(tree, HEALTHY_ROW + "\ncompany.billing.deleted_long_ago | unhooked | "
                                       "tools.runner | subject no longer exists")
    findings = ci.disposition_findings(ci.build_rows(tree), tree)
    assert any("no longer in the index" in f for f in fires(findings, "STALE DISPOSITION"))


def test_a_consumer_that_touches_the_package_nowhere_fires(tree):
    """DECORATIVE REFERENT — the guard that stops `unhooked` becoming a label.
    `company.billing.engine` is a real module, so the referent EXISTS; it just
    imports nothing from the orphan's package, which makes the nomination
    scenery rather than a claim."""
    write_register(tree, "company.billing.abandoned | unhooked | company.billing.engine | "
                         "nominates a sibling that drives nothing")
    findings = ci.disposition_findings(ci.build_rows(tree), tree)
    assert fires(findings, "DECORATIVE REFERENT")


def test_a_referent_that_does_not_exist_fires(tree):
    write_register(tree, "company.billing.abandoned | unhooked | tools.imaginary | "
                         "nominates a module nobody wrote")
    assert fires(ci.disposition_findings(ci.build_rows(tree), tree), "ABSENT REFERENT")


def test_a_no_consumer_claim_is_refuted_when_a_consumer_exists(tree):
    """REFUTED REFERENT. `none:<package>` is a claim about the tree, not an
    exemption from making one."""
    write_register(tree, "company.billing.abandoned | unhooked | none:company.billing | "
                         "claims the package has no door")
    assert fires(ci.disposition_findings(ci.build_rows(tree), tree), "REFUTED REFERENT")


def test_a_no_consumer_claim_holds_when_the_package_really_has_no_door(tree):
    """...and it must be able to be TRUE, or the five real `none:` rows in the
    live register could never pass."""
    (tree / "company" / "carbon").mkdir()
    (tree / "company" / "carbon" / "__init__.py").write_text("", encoding="utf-8")
    (tree / "company" / "carbon" / "ledger.py").write_text(
        '"""Carbon ledger nothing drives."""\nVALUE = 1\n', encoding="utf-8")
    write_register(tree, HEALTHY_ROW + "\ncompany.carbon.ledger | unhooked | "
                                       "none:company.carbon | no consumer exists")
    assert ci.disposition_findings(ci.build_rows(tree), tree) == []


def test_a_class_outside_the_declared_set_fires(tree):
    write_register(tree, "company.billing.abandoned | probably_fine | tools.runner | "
                         "invents its own class")
    assert fires(ci.disposition_findings(ci.build_rows(tree), tree), "UNKNOWN CLASS")


def test_a_wired_ruling_on_a_still_orphaned_module_refutes_itself(tree):
    """`wired` says a caller was missing and now is not. The index disagreeing
    is the row refuting itself, and it must say so rather than be believed."""
    write_register(tree, "company.billing.abandoned | wired | tools.runner | claims a caller")
    assert fires(ci.disposition_findings(ci.build_rows(tree), tree), "SELF-REFUTING ROW")


def test_a_malformed_row_is_reported_never_skipped(tree):
    """A row the parser cannot read is a ruling nobody is enforcing. Dropping
    it silently would un-disposition a module while the count still looked
    complete — the tidy-register fail-open in its purest form."""
    write_register(tree, "company.billing.abandoned | unhooked | tools.runner")
    findings = ci.disposition_findings(ci.build_rows(tree), tree)
    assert fires(findings, "MALFORMED DISPOSITION")
    assert fires(findings, "UNDISPOSITIONED")


def test_an_unclosed_block_does_not_swallow_the_rest_of_the_file(tree):
    path = tree / ci.DISPOSITION_REGISTER
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("<!-- ORPHAN-DISPOSITIONS\n" + HEALTHY_ROW + "\n", encoding="utf-8")
    assert fires(ci.disposition_findings(ci.build_rows(tree), tree),
                 "MALFORMED DISPOSITION")


def test_two_rulings_on_one_module_fire(tree):
    write_register(tree, HEALTHY_ROW + "\n" + HEALTHY_ROW)
    assert fires(ci.disposition_findings(ci.build_rows(tree), tree), "DUPLICATE DISPOSITION")


def test_a_class_with_no_reason_is_a_label(tree):
    write_register(tree, "company.billing.abandoned | unhooked | tools.runner |")
    assert fires(ci.disposition_findings(ci.build_rows(tree), tree), "EMPTY REASON")


def test_only_company_side_orphans_are_swept_in(tree):
    """`background/` and `tools/` orphans are governed elsewhere. Sweeping them
    in silently would make this register the owner of a population it never
    measured."""
    (tree / "tools" / "stray.py").write_text(
        '"""A tools-side orphan."""\nVALUE = 1\n', encoding="utf-8")
    write_register(tree, HEALTHY_ROW)
    assert ci.disposition_findings(ci.build_rows(tree), tree) == []


def test_the_live_register_rules_on_every_live_orphan():
    """The pass's own exit criterion, asserted against the real tree."""
    rows = ci.build_rows(REPO)
    assert ci.disposition_findings(rows, REPO) == []
    subjects = [r for r in ci.orphans(rows)
                if r["module"].startswith(ci.DISPOSITION_PREFIXES)]
    declared, errors = ci.parse_dispositions(
        (REPO / ci.DISPOSITION_REGISTER).read_text(encoding="utf-8"))
    assert errors == []
    assert len(declared) == len(subjects) > 200
    assert {r["class"] for r in declared} <= set(ci.DISPOSITION_CLASSES)
