"""Tests for `background/finding_classes.py` — atom `OPS10_finding_class_consolidation`.

R15 governs the shape of this file. Consolidation ARCHIVES documents: it takes twenty-two
live findings out of the staging root and replaces them with one. Every way that can go
wrong is a way to lose a finding silently, so what is proven here is that the module's
four load-bearing refusals can FAIL. Four mutations, each on a COPY of the module source,
each killing a NAMED test:

  MUTATION A (lane guard removed) — a member in another lane is consolidated anyway.
      Kills `test_a_member_in_another_lane_is_refused_consolidation`. This is the
      severity-laundering shape: archive a BLOCKING `D_billing_metering` finding under an
      `H_harness` class document and the D lane silently has no blocker.
  MUTATION B (the printed count comes from the ruling's estimate, not the list) — kills
      `test_the_printed_count_equals_the_instance_list_length`. The one-name-one-number
      class, already filed once against this project's own registers.
  MUTATION C (cost context requirement dropped) — every number becomes damage. Kills
      `test_a_number_with_no_cost_word_near_it_is_not_a_cost`. An estimate wearing a
      measurement's clothes is exactly what exit criterion 4 forbids.
  MUTATION D (`check()` stops reporting UNCONSOLIDATED) — kills
      `test_check_names_a_live_finding_that_belongs_to_a_class_and_is_not_listed`. Without
      it the consolidation decays the day after it lands and says nothing.

The mutants load from `tmp_path` under a unique module name, never by editing the real
file: editing a source file mid-pytest corrupts `inspect.getsource`, and a same-length
mutation can survive its own restoration through the `.pyc` cache (both filed findings
here). Every test builds its own staging root under `tmp_path` — the live root is read by
exactly one test, which is marked as such and asserts only what must be true of it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from background import finding_classes as fc

REPO = Path(__file__).resolve().parents[2]
MODULE_SOURCE = REPO / "background" / "finding_classes.py"


def _load_mutant(tmp_path: Path, old: str, new: str, name: str):
    """Import a copy of the module with `old` replaced by `new`. Asserts the anchor is
    unique — a no-op mutation would make its test pass for the wrong reason, which is how
    a mutation proof becomes theatre."""
    source = MODULE_SOURCE.read_text(encoding="utf-8")
    assert source.count(old) == 1, f"mutation anchor is not unique: {old!r}"
    path = tmp_path / f"{name}.py"
    path.write_text(source.replace(old, new), encoding="utf-8")

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


def _doc(root: Path, name: str, body: str, severity: str = "LATENT",
         lane: str = "H_harness") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
    path.write_text(
        f"# [WORKER-FINDING] {name.replace('_', ' ')}\n\n"
        f"**Severity:** {severity} · **Lane:** {lane}\n\n## Observed\n\n{body}\n",
        encoding="utf-8",
    )
    return path


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "staging"
    (root / fc.ARCHIVE_DIRNAME).mkdir(parents=True, exist_ok=True)
    return root


def _consolidate(root: Path) -> None:
    """Render the class documents, then archive every listed instance — the whole move,
    performed the way the tool performs it, so the checks below see a real end state."""
    for membership in fc.derive_memberships(root).values():
        doc = root / membership.finding_class.document_name
        doc.write_text(fc.render_class_document(membership, root), encoding="utf-8")
        for member in membership.members:
            member.rename(root / fc.ARCHIVE_DIRNAME / member.name)


# --- properties the mutations attack, factored so one assertion serves test and mutant ---

def _assert_out_of_lane_is_refused(module, root: Path) -> None:
    memberships = module.derive_memberships(root)
    gate = memberships["publish_gate_and_wedge"]
    names = [p.name for p in gate.members]
    assert "WORKER_FINDING_THE_WEDGE_ALARM_IS_WRONG_2026-08-12.md" in names
    assert "WORKER_FINDING_A_BILLING_WEDGE_2026-08-12.md" not in names, (
        "a D_billing_metering finding was consolidated into an H_harness class"
    )
    refused = [p.name for p, _lane in gate.refused_out_of_lane]
    assert "WORKER_FINDING_A_BILLING_WEDGE_2026-08-12.md" in refused


def _assert_printed_count_equals_list_length(module, root: Path) -> None:
    membership = module.derive_memberships(root)["publish_gate_and_wedge"]
    text = module.render_class_document(membership, root)
    printed = module._PRINTED_COUNT_RE.search(text)
    listed = module._INSTANCE_LINE_RE.findall(text)
    assert printed is not None
    assert int(printed.group(1)) == len(listed) == membership.count


def _assert_bare_number_is_not_a_cost(module) -> None:
    items = module.cost_evidence(
        "Any document untouched for 72 hours is named in the digest.", "d.md"
    )
    assert [i for i in items if i.unit == "hours"] == []


def _assert_unconsolidated_is_named(module, root: Path) -> None:
    failures = module.check(root).failures
    assert any(f.startswith("UNCONSOLIDATED") and "SIXTEENTH" in f for f in failures), failures


# --- classification: at most one class, precedence declared, unmatched stays unclassed ---

def test_a_document_lands_in_at_most_one_class(tmp_path):
    """Exit criterion 3. Overlapping families are real; two memberships are not."""
    root = _root(tmp_path)
    path = _doc(root, "WORKER_FINDING_THE_WEDGE_ALARM_IS_UNREACHABLE_2026-08-12.md", "x")
    result = fc.classify_file(path)
    assert result.class_id == "publish_gate_and_wedge"
    assert isinstance(result.class_id, str)


def test_the_losing_match_is_recorded_not_discarded(tmp_path):
    """A contested document is VISIBLE. Precedence decides; it does not erase."""
    root = _root(tmp_path)
    path = _doc(root, "WORKER_FINDING_THE_WEDGE_ALARM_IS_UNREACHABLE_2026-08-12.md", "x")
    result = fc.classify_file(path)
    assert "no_caller_and_never_runs" in result.also_matched
    assert result.is_contested


def test_an_unmatched_document_is_unclassed_never_forced_into_a_class(tmp_path):
    root = _root(tmp_path)
    path = _doc(root, "WORKER_FINDING_THE_TARIFF_LADDER_IS_UPSIDE_DOWN_2026-08-12.md", "x")
    result = fc.classify_file(path)
    assert result.class_id is None
    assert result.is_classed is False


def test_a_class_document_is_not_a_member_of_its_own_class(tmp_path):
    """Without the prefix exclusion, each class document matches its own patterns and
    becomes its own first instance — a register counting itself."""
    root = _root(tmp_path)
    (root / f"{fc.CLASS_DOC_PREFIX}PUBLISH_GATE_AND_WEDGE_2026-08-12.md").write_text(
        "# [CLASS] wedge\n\n**Severity:** LATENT · **Lane:** H_harness\n", encoding="utf-8"
    )
    assert [p.name for p in fc.classifiable_documents(root)] == []


def test_a_recorded_document_is_out_of_population(tmp_path):
    """A landed record has no repair to argue and no cost to add. Read from OPS9's parse,
    never from a second hand-kept list that could disagree with it."""
    root = _root(tmp_path)
    _doc(root, "WORKER_REPORT_THE_WEDGE_WAS_CLEARED_2026-08-12.md", "x", severity="RECORDED")
    assert fc.derive_memberships(root)["publish_gate_and_wedge"].members == []


def test_an_externally_authored_document_is_never_consolidated(tmp_path):
    """Clause 5 of the same ruling exists because advisor documents sat unopened. Filing
    one into a class and archiving it would be that silence with a mechanism behind it."""
    root = _root(tmp_path)
    _doc(root, "ADVISOR_FINDINGS_THE_WEDGE_ALARM_IS_INERT_2026-08-09.md", "x")
    memberships = fc.derive_memberships(root)
    assert all(m.members == [] for m in memberships.values())


# --- the lane guard: consolidation must not launder a blocker into another lane ---

def test_a_member_in_another_lane_is_refused_consolidation(tmp_path):
    """MUTATION A kills this test."""
    root = _root(tmp_path)
    _doc(root, "WORKER_FINDING_THE_WEDGE_ALARM_IS_WRONG_2026-08-12.md", "x")
    _doc(root, "WORKER_FINDING_A_BILLING_WEDGE_2026-08-12.md", "x",
         severity="BLOCKING", lane="D_billing_metering")
    _assert_out_of_lane_is_refused(fc, root)


def test_mutation_a_removing_the_lane_guard_kills_that_test(tmp_path):
    root = _root(tmp_path)
    _doc(root, "WORKER_FINDING_THE_WEDGE_ALARM_IS_WRONG_2026-08-12.md", "x")
    _doc(root, "WORKER_FINDING_A_BILLING_WEDGE_2026-08-12.md", "x",
         severity="BLOCKING", lane="D_billing_metering")
    mutant = _load_mutant(
        tmp_path,
        "        if severity.lane != membership.finding_class.lane:",
        "        if False:",
        "mutant_lane_guard",
    )
    try:
        _assert_out_of_lane_is_refused(mutant, root)
    except AssertionError:
        return
    raise AssertionError("MUTATION A survived: the lane guard is not load-bearing")


def test_a_member_with_no_readable_lane_is_refused_consolidation(tmp_path):
    """FAIL-CLOSED. A document that cannot be SHOWN to be in this lane is not archived
    into it — an unavailable check is a FAILED check, not a pass."""
    root = _root(tmp_path)
    path = root / "WORKER_FINDING_A_WEDGE_WITH_NO_HEADER_2026-08-12.md"
    path.write_text("# [WORKER-FINDING] a wedge with no header\n\nBody.\n", encoding="utf-8")
    gate = fc.derive_memberships(root)["publish_gate_and_wedge"]
    assert gate.members == []
    assert [p.name for p, _ in gate.refused_out_of_lane] == [path.name]


def test_the_class_severity_is_the_maximum_over_its_members(tmp_path):
    """A class that supersedes a blocker is itself blocking, or consolidation is a way to
    launder one into a housekeeping note."""
    root = _root(tmp_path)
    latent = _doc(root, "WORKER_FINDING_A_WEDGE_ONE_2026-08-12.md", "x")
    blocking = _doc(root, "WORKER_FINDING_A_WEDGE_TWO_2026-08-12.md", "x", severity="BLOCKING")
    severity, _parsed = fc.class_severity([latent, blocking])
    assert severity == fc.BLOCKING
    assert fc.class_severity([latent])[0] == fc.LATENT


def test_an_unreadable_member_makes_the_class_blocking(tmp_path):
    root = _root(tmp_path)
    missing = root / "WORKER_FINDING_A_WEDGE_THAT_VANISHED_2026-08-12.md"
    assert fc.class_severity([missing])[0] == fc.BLOCKING


# --- cost: measured from artefacts, one figure per document, never from a log paste ---

def test_a_number_with_no_cost_word_near_it_is_not_a_cost():
    """MUTATION C kills this test. The ruling's own 72-hour ageing threshold is not
    damage, and a classifier that bills it is estimating, not measuring."""
    _assert_bare_number_is_not_a_cost(fc)


def test_mutation_c_dropping_the_cost_context_requirement_kills_that_test(tmp_path):
    mutant = _load_mutant(
        tmp_path,
        "            if not _COST_CONTEXT_RE.search(window):",
        "            if False:",
        "mutant_cost_context",
    )
    try:
        _assert_bare_number_is_not_a_cost(mutant)
    except AssertionError:
        return
    raise AssertionError("MUTATION C survived: the cost-context requirement does nothing")


def test_a_duration_inside_a_code_fence_is_not_a_cost():
    """Quoted evidence is not a claim about what the defect cost. The first draft of this
    extractor billed a pasted pytest line to a class."""
    text = (
        "The wedge is described below.\n\n```\nE assert '-1 day(s) old' after 3h of red\n```\n"
    )
    assert [i for i in fc.cost_evidence(text, "d.md") if i.unit == "hours"] == []


def test_one_document_contributes_one_figure_its_largest():
    """A finding states its episode more than once; summing inside one document invents
    time nobody lost."""
    costs = [
        fc.CostItem("a.md", 31.0, "hours", "the 31h wedge"),
        fc.CostItem("a.md", 25.0, "hours", "the 25h window inside it"),
        fc.CostItem("b.md", 7.0, "hours", "a 7h stall"),
    ]
    worst = sorted(fc.worst_per_instance(costs), key=lambda c: c.source)
    assert [(c.source, c.amount) for c in worst] == [("a.md", 31.0), ("b.md", 7.0)]


def test_a_traced_cost_carries_the_sentence_it_came_from(tmp_path):
    """Exit criterion 4: a cost that cannot be traced is the mirror class this
    consolidation lists."""
    items = fc.cost_evidence("The gate wedged publishing for 60h before anyone looked.", "d.md")
    assert items and items[0].amount == 60.0
    assert "wedged publishing" in items[0].phrase


# --- the rendered document, and the check that it stays true ---

def test_the_printed_count_equals_the_instance_list_length(tmp_path):
    """MUTATION B kills this test. Exit criterion 5."""
    root = _root(tmp_path)
    for index in range(3):
        _doc(root, f"WORKER_FINDING_A_WEDGE_{index}_2026-08-12.md", "x")
    _assert_printed_count_equals_list_length(fc, root)


def test_mutation_b_printing_the_rulings_estimate_as_the_count_kills_that_test(tmp_path):
    root = _root(tmp_path)
    for index in range(3):
        _doc(root, f"WORKER_FINDING_A_WEDGE_{index}_2026-08-12.md", "x")
    mutant = _load_mutant(
        tmp_path,
        'f"**Instances:** {membership.count} · **Class:** `{finding_class.id}` · "',
        'f"**Instances:** {finding_class.ruling_count} · **Class:** `{finding_class.id}` · "',
        "mutant_printed_count",
    )
    try:
        _assert_printed_count_equals_list_length(mutant, root)
    except AssertionError:
        return
    raise AssertionError("MUTATION B survived: the printed count is not tied to the list")


def test_check_passes_on_a_completed_consolidation(tmp_path):
    """The RELEASE half (R11, no orphan transitions): a consolidation done properly must
    actually pass its own check, or the check is only ever red and nobody reads it."""
    root = _root(tmp_path)
    _doc(root, "WORKER_FINDING_A_WEDGE_ALARM_2026-08-12.md", "x")
    _doc(root, "WORKER_FINDING_A_FAIL_OPEN_GUARD_2026-08-12.md", "x")
    _consolidate(root)
    result = fc.check(root)
    assert result.ok, result.failures


def test_check_names_a_live_finding_that_belongs_to_a_class_and_is_not_listed(tmp_path):
    """MUTATION D kills this test. The sixteenth-instance detector: a family that grows
    must not silently stop being consolidated."""
    root = _root(tmp_path)
    _doc(root, "WORKER_FINDING_A_WEDGE_ALARM_2026-08-12.md", "x")
    _consolidate(root)
    _doc(root, "WORKER_FINDING_A_SIXTEENTH_WEDGE_2026-08-12.md", "x")
    _assert_unconsolidated_is_named(fc, root)


def test_mutation_d_silencing_the_unconsolidated_report_kills_that_test(tmp_path):
    root = _root(tmp_path)
    _doc(root, "WORKER_FINDING_A_WEDGE_ALARM_2026-08-12.md", "x")
    _consolidate(root)
    _doc(root, "WORKER_FINDING_A_SIXTEENTH_WEDGE_2026-08-12.md", "x")
    mutant = _load_mutant(
        tmp_path,
        "            if name not in listed:",
        "            if False:",
        "mutant_unconsolidated",
    )
    try:
        _assert_unconsolidated_is_named(mutant, root)
    except AssertionError:
        return
    raise AssertionError("MUTATION D survived: membership drift is not detected")


def test_check_fails_when_a_listed_instance_is_missing_from_the_archive(tmp_path):
    """ARCHIVED, NEVER DELETED — the ruling's own word. A class document whose instances
    are gone is a deletion with a citation."""
    root = _root(tmp_path)
    _doc(root, "WORKER_FINDING_A_WEDGE_ALARM_2026-08-12.md", "x")
    _consolidate(root)
    (root / fc.ARCHIVE_DIRNAME / "WORKER_FINDING_A_WEDGE_ALARM_2026-08-12.md").unlink()
    failures = fc.check(root).failures
    assert any(f.startswith("ARCHIVE MISSING") for f in failures), failures


def test_check_fails_when_a_superseded_instance_is_back_in_the_root(tmp_path):
    """The resurrection class — `WORKER_FINDING_ARCHIVED_STAGING_PATHS_ARE_RESURRECTED_ON_
    THE_SHARED_TREE_2026-08-10` — is this exact move's known failure mode on this tree."""
    root = _root(tmp_path)
    _doc(root, "WORKER_FINDING_A_WEDGE_ALARM_2026-08-12.md", "x")
    _consolidate(root)
    _doc(root, "WORKER_FINDING_A_WEDGE_ALARM_2026-08-12.md", "x")
    failures = fc.check(root).failures
    assert any(f.startswith("RESURRECTED") for f in failures), failures


def test_a_missing_class_document_fails_the_check(tmp_path):
    """FAIL-CLOSED: an absent class document is a failure, never a vacuous pass."""
    root = _root(tmp_path)
    failures = fc.check(root).failures
    assert len(failures) == len(fc.CLASSES)
    assert all(f.startswith("MISSING CLASS DOC") for f in failures)


def test_the_five_classes_are_the_five_the_ruling_named():
    """The families are the DIRECTOR'S measurement, not re-derived here. A sixth class
    appearing in this module means someone re-clustered the pile without a ruling."""
    assert [c.id for c in fc.CLASSES] == [
        "publish_gate_and_wedge",
        "controls_that_cannot_fail",
        "measurements_that_mirror",
        "uncommitted_and_orphaned_work",
        "no_caller_and_never_runs",
    ]
    assert [c.ruling_count for c in fc.CLASSES] == [18, 9, 7, 7, 5]


def test_the_live_staging_root_consolidation_holds():
    """The one test that reads the REAL root. It asserts the state this atom landed:
    five class documents present, every instance they name archived and not resurrected,
    every printed count equal to its list, and no live finding left unconsolidated."""
    result = fc.check()
    assert result.ok, "\n".join(result.failures)
