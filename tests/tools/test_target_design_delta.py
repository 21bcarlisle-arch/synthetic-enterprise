"""Tests for tools/target_design_delta.py — AO7, the reported delta.

The delta arithmetic is the easy half. The thing that can rot is the CONTROL: a target document
whose targets quietly stop being measured reads exactly like one whose targets are all met — in
both cases nothing complains. That is the failure the atom's own `origin_note` names in advance
("an aspirational wish-list nobody measures against"), so most of what follows is R15 work,
proving each guard FIRES on its own named defect by mutating a real tree or a real document
rather than by asserting that it would.

Three killer patterns, each answered here:

  TAUTOLOGY   -- the ACTUAL must never be derived from the document that states the TARGET.
                 `test_actual_is_independent_of_the_document` moves a target in the document and
                 proves every measured actual is byte-identical, so a document edit can never
                 move a measurement.
  FAIL-OPEN   -- `test_probe_that_scanned_nothing_fails` and the per-probe vacuity tests: a probe
                 that looked at no files must FAIL, not report a comfortable zero. "0 monoliths
                 found" and "0 files scanned" are the same number and opposite facts.
  FAIL-SILENT -- `test_unavailable_probe_is_rc2_not_rc0`: when a delegated measurement (SP3's
                 census, AO1's index, git) cannot answer, the tool returns 2. An unavailable
                 check is a FAILED check.

Plus the one inversion that makes this document different from every other control in the repo:
`test_a_large_delta_does_not_fail` pins R12. A non-zero delta must return rc 0. If a big delta
turned the build red, the cheapest available fix would be to delete the target from the document,
and the map would start optimising itself toward the territory.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools import target_design_delta as tdd

REPO = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# a real miniature repo, git-initialised, so every mutation below is a genuine
# code change measured through git — not a monkeypatched return value
# ---------------------------------------------------------------------------

def _write(base: Path, rel: str, text: str) -> Path:
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _git(base: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=base, check=True, capture_output=True)


@pytest.fixture
def tree(tmp_path):
    """A clean miniature repo: no cycles, no orphans, no seam bypass, no duplicate state."""
    base = tmp_path / "repo"
    base.mkdir()
    _write(base, "company/__init__.py", "")
    _write(base, "company/billing/__init__.py", "")
    _write(base, "company/billing/engine.py", '"""Bill calculation."""\nVALUE = 1\n')
    _write(base, "company/interfaces/__init__.py", "")
    _write(
        base, "company/interfaces/sim_interface.py",
        '"""The seam. Observables only."""\nfrom sim.prices import CURVE\n',
    )
    _write(base, "sim/__init__.py", "")
    _write(base, "sim/prices.py", '"""Wholesale curve."""\nCURVE = []\n')
    _write(base, "simulation/__init__.py", "")
    _write(base, "simulation/run.py", '"""The run."""\nVALUE = 2\n')
    _write(base, "docs/state/ledger.json", '{"a": 1}')
    _write(
        base, "tests/test_engine.py",
        "from company.billing.engine import VALUE\n"
        "from company.interfaces.sim_interface import CURVE\n",
    )
    _git(base, "init", "-q")
    _git(base, "add", "-A")
    return base


def _measure(base: Path, probe_name: str):
    return tdd.PROBES[probe_name](base)


# ---------------------------------------------------------------------------
# R15 -- each probe FIRES on its own named defect. Clean tree first (so the
# fixture asserts its own premise and a probe that always fires is caught),
# then the mutation.
# ---------------------------------------------------------------------------

def test_import_cycle_probe_fires_on_a_real_cycle(tree):
    clean, scanned, _ = _measure(tree, "import_cycles")
    assert clean == 0, "premise: the fixture starts acyclic"
    assert scanned > 0

    # MUTATION: make two modules import each other.
    _write(tree, "company/billing/engine.py",
           '"""Bill calculation."""\nfrom company.billing.rates import RATE\nVALUE = 1\n')
    _write(tree, "company/billing/rates.py",
           '"""Rates."""\nfrom company.billing.engine import VALUE\nRATE = 2\n')
    _git(tree, "add", "-A")

    dirty, _, detail = _measure(tree, "import_cycles")
    assert dirty == 1, "a genuine mutual import must be reported"
    assert "company.billing.engine" in detail[0]


def test_world_to_company_probe_fires_and_ignores_the_seam(tree):
    clean, scanned, _ = _measure(tree, "world_files_importing_company_directly")
    assert clean == 0, "premise: the fixture's world does not reach into the company"
    assert scanned > 0

    # MUTATION: the world binds itself to a company internal.
    _write(tree, "simulation/run.py",
           '"""The run."""\nfrom company.billing.engine import VALUE\n')
    _git(tree, "add", "-A")

    dirty, _, detail = _measure(tree, "world_files_importing_company_directly")
    assert dirty == 1
    assert "simulation/run.py" in detail[0]


def test_epistemic_wall_probe_fires_on_a_real_breach(tree):
    """T3b is the WALL. It must fire when a company module reads a world internal..."""
    clean, scanned, _ = _measure(tree, "company_files_importing_world_internals")
    assert clean == 0, "premise: only the seam sees the world"
    assert scanned > 0

    # MUTATION: a company module reads simulation internals directly.
    _write(tree, "company/billing/engine.py",
           '"""Bill calculation."""\nfrom simulation.run import VALUE\n')
    _git(tree, "add", "-A")

    dirty, _, detail = _measure(tree, "company_files_importing_world_internals")
    assert dirty == 1
    assert "company/billing/engine.py" in detail[0]


def test_epistemic_wall_probe_does_not_fire_on_the_seam_itself(tree):
    """...and must NOT fire on the seam, whose whole job is to see both sides.

    A wall control that reds on its own designated door is a false-positive that jams the
    pipeline, and the fix under time pressure is always to disable the control.
    """
    actual, _, detail = _measure(tree, "company_files_importing_world_internals")
    assert actual == 0, f"the seam must not count as a breach, got {detail}"
    # and the seam really does import the world, so this is not a vacuous pass
    assert "from sim.prices import" in (
        tree / "company/interfaces/sim_interface.py").read_text(encoding="utf-8")


def test_duplicate_state_probe_fires_on_a_second_copy(tree):
    clean, scanned, _ = _measure(tree, "duplicated_state_files")
    assert clean == 0, "premise: one ledger, one path"
    assert scanned > 0

    # MUTATION: commit a second copy of the same state payload elsewhere.
    _write(tree, "site/state/ledger.json", '{"a": 1}')
    _git(tree, "add", "-A")

    dirty, _, detail = _measure(tree, "duplicated_state_files")
    assert dirty == 1
    assert "ledger.json" in detail[0]


def test_untested_module_probe_fires_when_a_test_stops_importing(tree):
    clean, scanned, _ = _measure(tree, "company_modules_without_tests")
    assert clean == 0, "premise: every company module is exercised"
    assert scanned > 0

    # MUTATION: the test stops importing the engine.
    _write(tree, "tests/test_engine.py",
           "from company.interfaces.sim_interface import CURVE\n")
    _git(tree, "add", "-A")

    dirty, _, detail = _measure(tree, "company_modules_without_tests")
    assert dirty == 1
    assert "company.billing.engine" in detail


# ---------------------------------------------------------------------------
# FAIL-OPEN -- the vacuity guards. A probe that scanned nothing must raise.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("probe_name", [
    "import_cycles",
    "world_files_importing_company_directly",
    "company_files_importing_world_internals",
    "duplicated_state_files",
    "company_modules_without_tests",
])
def test_probe_on_an_empty_tree_raises_rather_than_reporting_zero(tmp_path, probe_name):
    """An empty scan is a FAILED check, not a clean tree.

    This is the 1557/1557-passed-while-the-field-was-absent shape: every one of these probes
    would otherwise return a perfectly plausible 0 for a tree it never looked at.
    """
    base = tmp_path / "empty"
    base.mkdir()
    _git(base, "init", "-q")
    with pytest.raises(tdd.ProbeUnavailable):
        tdd.PROBES[probe_name](base)


@pytest.mark.parametrize("probe_name,roots", [
    ("import_cycles", ("company", "sim", "saas", "simulation", "interface", "tools", "background")),
    ("world_files_importing_company_directly", tdd.WORLD_ROOTS),
    ("company_files_importing_world_internals", (tdd.COMPANY_ROOT,)),
    ("company_modules_without_tests", (tdd.COMPANY_ROOT,)),
])
def test_probe_whose_declared_root_went_missing_raises(tmp_path, probe_name, roots):
    """A POPULATED repo in which the probe's own root covers nothing must FAIL, not report zero.

    This is the case the empty-tree test above does NOT reach, and the mutation pass proved it:
    deleting the root-level vacuity guard left the whole suite green, because an empty repo trips
    the `git ls-files` guard first and the root guard was never exercised. The realistic failure
    is not an empty repo -- it is a rename or a prefix change that silently drops `company/` from
    the walk, leaving a tool that reports a beautifully clean architecture for a tree it stopped
    looking at. Under-reporting does not look broken; it looks like success.
    """
    base = tmp_path / "populated"
    base.mkdir()
    # plenty of tracked python, none of it under the probe's declared roots
    _write(base, "elsewhere/thing.py", '"""Something."""\nVALUE = 1\n')
    _write(base, "other/place.py", '"""Another."""\nfrom elsewhere.thing import VALUE\n')
    _git(base, "init", "-q")
    _git(base, "add", "-A")

    # premise: the repo is genuinely non-empty, so `git ls-files` cannot be what fires
    assert tdd._tracked_files(base, ".py"), "premise: the fixture repo has tracked python"

    with pytest.raises(tdd.ProbeUnavailable, match="no tracked python sources"):
        tdd.PROBES[probe_name](base)


def test_tracked_files_empty_result_raises_directly(tmp_path):
    """The `git ls-files returned nothing` guard, pinned at its own level.

    The mutation pass caught this one surviving: every probe that goes through `_tracked_files`
    has a second, narrower vacuity guard downstream, so deleting this one left the suite green.
    A guard whose only evidence is another guard's test is not evidence -- it is a line of code
    nobody has ever seen fire. Tested here directly so it has its own falsifier.
    """
    base = tmp_path / "emptyrepo"
    base.mkdir()
    _git(base, "init", "-q")
    with pytest.raises(tdd.ProbeUnavailable, match="returned nothing"):
        tdd._tracked_files(base)


def test_probe_where_git_is_unavailable_raises(tmp_path):
    """FAIL-SILENT: no git means the check could not run, which is a failure."""
    base = tmp_path / "notarepo"
    base.mkdir()
    (base / "company").mkdir()
    (base / "company" / "x.py").write_text('"""x."""\n', encoding="utf-8")
    with pytest.raises(tdd.ProbeUnavailable):
        tdd.PROBES["import_cycles"](base)


def test_scanned_zero_is_reported_as_a_failure_not_a_measurement(monkeypatch):
    """Belt and braces: even if a probe returned (0, 0, []) instead of raising, measure()
    must treat it as a failure. The guard does not depend on every probe remembering."""
    target = tdd.Target(id="T", probe="p", direction="at_most", target=0, unit="u", line=1)
    monkeypatch.setitem(tdd.PROBES, "p", lambda _: (0, 0, []))
    results, failures = tdd.measure([target], REPO)
    assert results == []
    assert failures and "scanned 0 units" in failures[0]


def test_unavailable_probe_is_rc2_not_rc0(monkeypatch, tmp_path):
    """A delegated measurement that cannot answer must fail the run, never pass it quietly."""
    def dead(_):
        raise tdd.ProbeUnavailable("SP3 census could not measure")

    monkeypatch.setitem(tdd.PROBES, "modules_over_line_cap", dead)
    doc = tmp_path / "doc.md"
    doc.write_text(_doc_with(["modules_over_line_cap"]), encoding="utf-8")
    monkeypatch.setattr(tdd, "PROBES", {"modules_over_line_cap": dead})
    assert tdd.main(["--check", "--doc", str(doc)]) == 2


# ---------------------------------------------------------------------------
# THE ANTI-WISH-LIST GUARD -- the reason this atom exists. Both directions.
# ---------------------------------------------------------------------------

def _doc_with(probe_names: list[str]) -> str:
    blocks = "\n\n".join(
        "```target\n"
        f"id: T{i}\n"
        f"probe: {name}\n"
        "direction: at_most\n"
        "target: 0\n"
        "unit: things\n"
        "```"
        for i, name in enumerate(probe_names)
    )
    return f"# A target document\n\nSome prose.\n\n{blocks}\n"


def test_a_target_with_no_probe_fails(tmp_path, monkeypatch):
    """THE named failure mode: aspirational prose that nothing measures.

    This is the test that makes the anti-wish-list property structural rather than exhortative.
    """
    monkeypatch.setattr(tdd, "PROBES", {"real_probe": lambda _: (1, 5, [])})
    doc = tmp_path / "doc.md"
    doc.write_text(_doc_with(["real_probe", "a_beautiful_idea_nobody_measures"]), encoding="utf-8")

    assert tdd.main(["--check", "--doc", str(doc)]) == 2

    findings = tdd.reconcile(tdd.parse_targets(doc.read_text(encoding="utf-8")))
    assert any("not implemented" in f for f in findings)


def test_a_probe_with_no_target_fails(tmp_path, monkeypatch):
    """The other direction: the document stopped describing what is measured."""
    monkeypatch.setattr(tdd, "PROBES", {
        "claimed": lambda _: (1, 5, []),
        "orphaned": lambda _: (1, 5, []),
    })
    doc = tmp_path / "doc.md"
    doc.write_text(_doc_with(["claimed"]), encoding="utf-8")

    assert tdd.main(["--check", "--doc", str(doc)]) == 2
    findings = tdd.reconcile(tdd.parse_targets(doc.read_text(encoding="utf-8")))
    assert any("no target block claims it" in f for f in findings)


def test_a_document_of_pure_prose_fails(tmp_path):
    """A target document with no measured targets is exactly the wish-list."""
    doc = tmp_path / "doc.md"
    doc.write_text("# Our beautiful architecture\n\nWe will have clean seams.\n", encoding="utf-8")
    assert tdd.main(["--check", "--doc", str(doc)]) == 2


def test_missing_document_is_rc2(tmp_path):
    assert tdd.main(["--check", "--doc", str(tmp_path / "nope.md")]) == 2


# ---------------------------------------------------------------------------
# THE BOUNDED PARSER -- an unterminated block must not swallow the document
# ---------------------------------------------------------------------------

def test_unterminated_block_is_a_defect_not_a_swallow():
    """The last-field-with-no-terminator class: false-positive one way, fail-OPEN the other."""
    text = (
        "# doc\n```target\nid: T1\nprobe: p\ndirection: at_most\ntarget: 0\nunit: u\n```\n"
        "```target\nid: T2\nprobe: p2\ndirection: at_most\ntarget: 0\nunit: u\n"
    )
    with pytest.raises(tdd.DocumentDefect, match="unterminated"):
        tdd.parse_targets(text)


def test_typoed_key_is_rejected_rather_than_silently_unmeasured():
    """`prboe:` must be an error. Ignoring unknown keys would make it an unmeasured target."""
    text = ("```target\nid: T1\nprboe: p\ndirection: at_most\ntarget: 0\nunit: u\n```\n")
    with pytest.raises(tdd.DocumentDefect, match="unknown key"):
        tdd.parse_targets(text)


def test_missing_key_is_rejected():
    text = "```target\nid: T1\ndirection: at_most\ntarget: 0\nunit: u\n```\n"
    with pytest.raises(tdd.DocumentDefect, match="missing key"):
        tdd.parse_targets(text)


def test_duplicate_target_id_is_rejected(monkeypatch):
    monkeypatch.setattr(tdd, "PROBES", {"p": lambda _: (0, 1, [])})
    text = (
        "```target\nid: T1\nprobe: p\ndirection: at_most\ntarget: 0\nunit: u\n```\n"
        "```target\nid: T1\nprobe: p\ndirection: at_most\ntarget: 0\nunit: u\n```\n"
    )
    findings = tdd.reconcile(tdd.parse_targets(text))
    assert any("duplicate target id" in f for f in findings)


def test_non_integer_target_is_rejected():
    text = "```target\nid: T1\nprobe: p\ndirection: at_most\ntarget: soon\nunit: u\n```\n"
    with pytest.raises(tdd.DocumentDefect, match="must be an integer"):
        tdd.parse_targets(text)


def test_bad_direction_is_rejected():
    text = "```target\nid: T1\nprobe: p\ndirection: roughly\ntarget: 0\nunit: u\n```\n"
    with pytest.raises(tdd.DocumentDefect, match="direction"):
        tdd.parse_targets(text)


# ---------------------------------------------------------------------------
# TAUTOLOGY -- the actual must not come from the document
# ---------------------------------------------------------------------------

def test_actual_is_independent_of_the_document(tmp_path, monkeypatch):
    """Move the TARGET in the document; every ACTUAL must be byte-identical.

    If the actual could be influenced by the document, the delta would be a number the document
    computes about itself, and the whole report would prove nothing.
    """
    monkeypatch.setattr(tdd, "PROBES", {"p": lambda _: (7, 10, [])})

    def actuals(target_value: int):
        doc = tmp_path / f"doc{target_value}.md"
        doc.write_text(
            f"```target\nid: T1\nprobe: p\ndirection: at_most\ntarget: {target_value}\n"
            "unit: u\n```\n", encoding="utf-8")
        results, failures = tdd.measure(tdd.parse_targets(doc.read_text(encoding="utf-8")), REPO)
        assert not failures
        return [m.actual for m in results]

    assert actuals(0) == actuals(999) == [7]


def test_delta_arithmetic_both_directions():
    at_most = tdd.Target(id="a", probe="p", direction="at_most", target=0, unit="u", line=1)
    at_least = tdd.Target(id="b", probe="p", direction="at_least", target=10, unit="u", line=1)
    assert tdd.Measurement(target=at_most, actual=5, scanned=1).delta == 5
    assert tdd.Measurement(target=at_most, actual=0, scanned=1).met is True
    assert tdd.Measurement(target=at_least, actual=4, scanned=1).delta == 6
    assert tdd.Measurement(target=at_least, actual=12, scanned=1).met is True


# ---------------------------------------------------------------------------
# R12 -- the inversion. The delta is a diagnostic and must NOT gate.
# ---------------------------------------------------------------------------

def test_a_large_delta_does_not_fail(tmp_path, monkeypatch):
    """R12, and the load-bearing design choice of this atom.

    If a large delta returned non-zero, the cheapest fix available to any future turn would be to
    weaken the target or delete it from the document -- the map optimising itself toward the
    territory. What fails is a target that stopped being measured; never the number.
    """
    monkeypatch.setattr(tdd, "PROBES", {"p": lambda _: (99999, 10, [])})
    doc = tmp_path / "doc.md"
    doc.write_text(_doc_with(["p"]), encoding="utf-8")
    assert tdd.main(["--check", "--doc", str(doc)]) == 0


# ---------------------------------------------------------------------------
# the real document, and the real tree
# ---------------------------------------------------------------------------

def test_the_committed_document_passes_its_own_integrity_check():
    assert tdd.main(["--check"]) == 0


def test_the_committed_document_measures_every_implemented_probe():
    targets = tdd.parse_targets(tdd.DOC_PATH.read_text(encoding="utf-8"))
    assert {t.probe for t in targets} == set(tdd.PROBES)
    assert tdd.reconcile(targets) == []


def test_json_output_names_its_two_sources_separately():
    """The independence claim must be auditable in the artefact AO6 consumes, not just asserted
    in a docstring."""
    out = subprocess.run(
        [sys.executable, "tools/target_design_delta.py", "--json"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert out.returncode == 0, out.stderr
    payload = json.loads(out.stdout)
    assert payload["target_source"] != payload["actual_source"]
    assert payload["integrity_findings"] == []
    assert payload["targets_measured"] == len(tdd.PROBES)
    for row in payload["results"]:
        assert row["scanned"] > 0, f"{row['id']} measured nothing"


def test_the_epistemic_wall_is_currently_intact():
    """T3b is the one target that is a WALL rather than debt: a regression is fixed on sight.

    Pinned as a test so the day it stops being zero, the suite says so and not only the report.
    """
    actual, scanned, detail = tdd.PROBES["company_files_importing_world_internals"](REPO)
    assert scanned > 100, "premise: the company tree was really walked"
    assert actual == 0, f"epistemic wall breached by: {detail}"
