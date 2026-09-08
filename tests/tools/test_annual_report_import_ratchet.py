#!/usr/bin/env python3
"""R15 proof for the annual-report import ratchet (director instruction, 2026-08-19).

The gate is deliberately ASYMMETRIC — production importers are frozen, test importers are only
counted — so both halves of that asymmetry are driven. A gate that quietly started enforcing the
test count would fail on every ordinary edit to a report test and be disabled within a week,
which is why "it does not enforce tests" is pinned as hard as "it does enforce production".

The fail-closed direction is toward RAISING: a scan that reads nothing finds no importers and
would otherwise report the clean layering it never looked at.
"""
from __future__ import annotations

import pytest

from tools import annual_report_import_ratchet as ar


def _tree(tmp_path, rel: str, body: str):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return tmp_path


IMPORTS = "from saas.reporting.annual_report import populate_compliance_scorecard\n"
PLAIN_IMPORT = "import saas.reporting.annual_report\n"


# ---------------------------------------------------------------------------
# Detection, both import shapes
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("body", [IMPORTS, PLAIN_IMPORT])
def test_MUTATION_a_production_importer_is_found(tmp_path, body):
    """Both `from X import y` and `import X` are real ways to read a report; a gate catching
    only the first is a gate you route around by accident."""
    root = _tree(tmp_path, "tools/x.py", body)
    assert ar.production_importers(root) == {"tools/x.py"}


def test_a_module_that_does_not_import_it_is_not_found(tmp_path):
    root = _tree(tmp_path, "tools/x.py", "import json\nfrom company.core import event_ledger\n")
    assert ar.production_importers(root) == set()


def test_the_report_importing_itself_is_not_a_violation(tmp_path):
    """The re-export shim left inside the renderer imports the extracted module, and the file
    is skipped by path so a self-reference can never read as a violation."""
    root = _tree(tmp_path, "saas/reporting/annual_report.py", PLAIN_IMPORT)
    _tree(tmp_path, "tools/other.py", "import json\n")
    assert ar.production_importers(root) == set()


# ---------------------------------------------------------------------------
# The asymmetry -- the instruction itself
# ---------------------------------------------------------------------------
def test_MUTATION_test_importers_are_COUNTED_and_NEVER_enforced(tmp_path, monkeypatch):
    """THE asymmetry, and the director's instruction verbatim: leave the test files alone,
    record the size. A test importer must raise the COUNT and not a violation."""
    monkeypatch.setattr(ar, "FROZEN", frozenset())  # isolate: the real freeze is absent here
    root = _tree(tmp_path, "tests/test_report.py", IMPORTS)
    _tree(tmp_path, "tools/clean.py", "import json\n")
    assert ar.test_importers(root) == {"tests/test_report.py"}
    assert ar.gate_violations(root) == [], "a test importer was enforced"


def test_MUTATION_a_new_production_importer_fails_the_commit(tmp_path, monkeypatch):
    monkeypatch.setattr(ar, "FROZEN", frozenset())  # isolate: a NEW importer, not a stale freeze
    root = _tree(tmp_path, "tools/new_reader.py", IMPORTS)
    problems = ar.gate_violations(root)
    assert len(problems) == 1
    assert problems[0].startswith("NEW PRODUCTION IMPORTER: tools/new_reader.py")
    assert "move the COMPUTATION into its own module" in problems[0], (
        "the refusal must name the repair, not just the rule"
    )


def test_MUTATION_a_frozen_entry_that_is_gone_ALSO_fails(tmp_path, monkeypatch):
    """The direction people forget. Without it the freeze becomes a permanent amnesty and the
    gate stops meaning anything."""
    monkeypatch.setattr(ar, "FROZEN", frozenset({"tools/departed.py"}))
    root = _tree(tmp_path, "tools/clean.py", "import json\n")
    problems = ar.gate_violations(root)
    assert len(problems) == 1 and problems[0].startswith("STALE FREEZE: tools/departed.py")


def test_a_frozen_importer_does_not_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(ar, "FROZEN", frozenset({"tools/allowed.py"}))
    root = _tree(tmp_path, "tools/allowed.py", IMPORTS)
    assert ar.gate_violations(root) == []


# ---------------------------------------------------------------------------
# FAIL-CLOSED
# ---------------------------------------------------------------------------
def test_MUTATION_FAIL_CLOSED_a_scan_that_reads_nothing_raises(tmp_path):
    """No files scanned -> no importers found -> a serene clean layering, computed from a tree
    nobody looked at. That is the FAIL-OPEN killer pattern; it must raise."""
    with pytest.raises(ar.ScanUnavailable):
        ar.production_importers(tmp_path)


# ---------------------------------------------------------------------------
# The live tree
# ---------------------------------------------------------------------------
def test_the_live_tree_has_no_unfrozen_production_importer():
    assert ar.gate_violations() == []


def test_the_extracted_computation_is_shared_not_duplicated():
    """WHY the fix was an extraction rather than a copy. Two surfaces render this — the report's
    markdown table and the dashboard's Regulatory tab — and if they ever computed it separately
    they could disagree about whether an obligation is GREEN, which is a worse defect than the
    import was. One module, imported by both, is what makes disagreement impossible."""
    import inspect
    from saas.reporting import compliance_scorecard_population as pop
    from saas.reporting import annual_report

    assert callable(pop.populate_compliance_scorecard)
    # the report re-exports the SAME object, not a reimplementation
    assert annual_report.populate_compliance_scorecard is pop.populate_compliance_scorecard
    dash = inspect.getsource(
        __import__("tools.generate_dashboard_data", fromlist=["extract_regulatory"])
        .extract_regulatory)
    assert "compliance_scorecard_population" in dash, (
        "the dashboard no longer takes the computation from the extracted module"
    )
    assert "from saas.reporting.annual_report import" not in dash


def test_the_debt_record_states_its_own_size():
    """The director asked for the size recorded so it is chosen deliberately later. A debt doc
    without numbers is a note, not a measurement."""
    body = ar.DEBT_DOC.read_text(encoding="utf-8")
    assert "Test files importing the report" in body
    assert str(len(ar.test_importers())) in body


def _debt_tree(tmp_path, files):
    """A minimal tree `render_debt(root)` can be driven over: the renderer, plus test files."""
    (tmp_path / "saas" / "reporting").mkdir(parents=True)
    (tmp_path / "saas" / "reporting" / "annual_report.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    for name, body in files.items():
        (tmp_path / "tests" / name).write_text(body, encoding="utf-8")
    return tmp_path


def test_MUTATION_the_published_private_count_is_of_CALLS_not_of_MENTIONS(tmp_path):
    """THE PUBLISHED FIGURE (2026-09-08). `render_debt` reported 84 test files reaching into
    `_section_*` internals; two of them name a `_section_*` function only in a COMMENT and import
    none, so the debt the director asked us to size published itself 2 too large -- in the
    direction that makes the rebuild it defers look more necessary than it is.

    Driven over a planted tree rather than the live one: the figure is a COUNT, so a control keyed
    to today's answer goes red every time another lane adds a test, and one keyed to two named
    files goes red when either is renamed. Here the poison and the real reacher are both present,
    so the count can only be 1.
    """
    root = _debt_tree(tmp_path, {
        "test_mentions.py": ("from saas.reporting.annual_report import render\n"
                             "# explains why it does NOT call _section_policy_costs\n"),
        "test_reaches.py": ("from saas.reporting.annual_report import _section_policy_costs\n"
                            "def test_x():\n    assert _section_policy_costs({})\n"),
    })
    rendered = ar.render_debt(root)
    assert "| Test files importing the report | **2** |" in rendered, rendered
    assert "| ...of which reach into private `_section_*` functions | **1** |" in rendered, (
        "a COMMENT naming a private section counted as a file that reaches into one")
