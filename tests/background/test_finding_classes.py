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


# --- rule 5: room exclusivity. Population is the ROOMS, not a class document's list ---
#
# The defect this rule was built for: `ADVISOR_FINDINGS_MONEY_CORE_CHARACTERIZATION_
# 2026-08-06.md` was dispositioned into `in_progress/` with its severity downgraded
# BLOCKING -> OPEN, and a stale root copy still reading `**Severity:** BLOCKING` was
# committed back by an auto-process sweep. The doorbell read the root copy and drew it at
# RUNG 1c -- the highest-priority draw in the machine -- ahead of every other lane, while
# `--check` printed PASS. It printed PASS because rule 3 only ever asks about names a
# class document already lists, and no class document has ever named an advisor findings
# note. WRONG POPULATION, not a missing rule.


def _rooms(tmp_path: Path) -> Path:
    root = _root(tmp_path)
    (root / fc.PARKED_DIRNAME).mkdir(parents=True, exist_ok=True)
    return root


def test_room_collisions_is_empty_on_documents_that_each_occupy_one_room(tmp_path):
    """The negative half. Three documents, three rooms, one each -- no collision. Without
    this the rule could be a constant `fail` and every positive test below would pass."""
    root = _rooms(tmp_path)
    _doc(root, "WORKER_FINDING_LIVE_2026-08-12.md", "live")
    _doc(root / fc.ARCHIVE_DIRNAME, "WORKER_FINDING_CONSUMED_2026-08-12.md", "done")
    _doc(root / fc.PARKED_DIRNAME, "WORKER_FINDING_PARKED_2026-08-12.md", "parked")
    assert fc.room_collisions(root) == []


def test_a_document_in_the_root_and_in_progress_is_named(tmp_path):
    """The shipped 2026-08-12 state, reproduced: the disposition parked it and a stale
    root copy came back. NOTE the name -- an ADVISOR document, which belongs to no class,
    so rule 3's listed-instance walk cannot reach it however carefully it is run."""
    root = _rooms(tmp_path)
    name = "ADVISOR_FINDINGS_MONEY_CORE_CHARACTERIZATION_2026-08-06.md"
    _doc(root, name, "the stale copy", severity="BLOCKING")
    _doc(root / fc.PARKED_DIRNAME, name, "the dispositioned copy", severity="OPEN")

    assert fc.room_collisions(root) == [(name, "in_progress", "root")]
    failures = fc.check(root).failures
    assert any(f.startswith(f"TWO ROOMS {name}") for f in failures), failures


def test_a_document_in_done_and_in_progress_is_named(tmp_path):
    """The pairing the 2026-08-12 hand census never looked at. That census ran root-vs-
    `done/` only, found zero, and reported the both-rooms class closed -- while three
    documents sat simultaneously archived as consumed and parked as open."""
    root = _rooms(tmp_path)
    name = "DIRECTOR_RULING_NIGHT_ENFORCEMENT_2026-07-23.md"
    _doc(root / fc.ARCHIVE_DIRNAME, name, "the archived text")
    _doc(root / fc.PARKED_DIRNAME, name, "the parked text with an open sub-item")

    assert fc.room_collisions(root) == [(name, "done", "in_progress")]
    assert any(f.startswith(f"TWO ROOMS {name}") for f in fc.check(root).failures)


def test_a_document_in_the_root_and_done_is_named(tmp_path):
    """The third pairing -- the only one anything checked before, and only for names a
    class document lists. Here the document is unlisted and it still fires."""
    root = _rooms(tmp_path)
    name = "WORKER_FINDING_AN_UNLISTED_ONE_2026-08-12.md"
    _doc(root, name, "root copy")
    _doc(root / fc.ARCHIVE_DIRNAME, name, "archived copy")

    assert fc.room_collisions(root) == [(name, "done", "root")]
    assert any(f.startswith(f"TWO ROOMS {name}") for f in fc.check(root).failures)


def test_the_rule_covers_every_pairing_of_the_three_rooms(tmp_path):
    """VACUITY GUARD on the pairing set. A rule that walks two of three rooms reads
    exactly like a clean sweep -- that is the defect, so the count of pairings the rule
    can produce is pinned rather than trusted. Three rooms, three pairs, one name in all
    three must produce all three."""
    root = _rooms(tmp_path)
    name = "WORKER_FINDING_IN_ALL_THREE_2026-08-12.md"
    for where in (root, root / fc.ARCHIVE_DIRNAME, root / fc.PARKED_DIRNAME):
        _doc(where, name, "a copy")

    assert fc.room_collisions(root) == [
        (name, "done", "in_progress"),
        (name, "done", "root"),
        (name, "in_progress", "root"),
    ]
    assert fc.PARKED_DIRNAME in fc.ROOM_DIRNAMES


def test_mutation_e_narrowing_the_population_to_listed_instances_kills_those_tests(tmp_path):
    """MUTATION E — the population defect itself, reintroduced. Restrict the rooms walked
    to `done/` (i.e. drop `in_progress/`, which is what rule 3 knew about) and the two
    collisions involving a parked copy vanish while the checker still reports PASS. This
    is the state that shipped and drew at rung 1c."""
    mutant = _load_mutant(
        tmp_path,
        'ROOM_DIRNAMES = (ARCHIVE_DIRNAME, PARKED_DIRNAME)',
        'ROOM_DIRNAMES = (ARCHIVE_DIRNAME,)',
        "fc_mutant_e",
    )
    root = _rooms(tmp_path)
    name = "ADVISOR_FINDINGS_MONEY_CORE_CHARACTERIZATION_2026-08-06.md"
    _doc(root, name, "the stale copy", severity="BLOCKING")
    _doc(root / fc.PARKED_DIRNAME, name, "the dispositioned copy", severity="OPEN")

    assert fc.room_collisions(root), "the real module must see this collision"
    assert mutant.room_collisions(root) == [], "mutant should be blind to the parked room"
    assert not any(f.startswith("TWO ROOMS") for f in mutant.check(root).failures)


# --- rule 6: the printed severity is re-derived, so a discharge can RELEASE a class ---
#
# The release valve. Rules 1-5 can each only ADD an obligation; without this one a class
# document's severity is written once at render and never re-read, so discharging every
# blocking member leaves the header printing BLOCKING, `check()` passing, and
# `_blocking_lane_draw` freezing the lane off a claim no control still stands behind.

#: A real, stable test node used as discharge evidence. OPS9's discharge is checked
#: against the filesystem relative to the REPO root (not tmp_path), so a fixture cannot
#: invent one. Asserted below rather than assumed: a discharge naming a node that stopped
#: existing would be REFUSED, the member would stay BLOCKING, and these tests would fail
#: for a reason that has nothing to do with what they are about.
_REAL_NODE = "tests/background/test_finding_classes.py::test_check_passes_on_a_completed_consolidation"


def _discharge(path: Path) -> None:
    """Write a VALID `**Discharged:**` header onto an already-archived member."""
    text = path.read_text(encoding="utf-8")
    assert "## Observed" in text
    path.write_text(
        text.replace(
            "## Observed",
            f"**Discharged:** `{_REAL_NODE}` — repaired, falsifier named.\n\n## Observed",
        ),
        encoding="utf-8",
    )


def _consolidated_wedge_class(tmp_path: Path) -> tuple[Path, Path]:
    """A completed consolidation of one BLOCKING and one LATENT wedge finding.

    Returns (root, archived path of the BLOCKING member).
    """
    root = _root(tmp_path)
    _doc(root, "WORKER_FINDING_THE_WEDGE_GATE_IS_RED_2026-08-12.md",
         "the publish gate wedge", severity="BLOCKING")
    _doc(root, "WORKER_FINDING_ANOTHER_WEDGE_PUBLISH_GATE_2026-08-12.md",
         "another publish gate wedge", severity="LATENT")
    _consolidate(root)
    blocker = (root / fc.ARCHIVE_DIRNAME
               / "WORKER_FINDING_THE_WEDGE_GATE_IS_RED_2026-08-12.md")
    assert blocker.exists(), "fixture did not archive the blocking member"
    return root, blocker


def test_the_discharge_evidence_this_fixture_relies_on_actually_exists():
    """Guards the fixture, not the module: an unchecked discharge is refused, which would
    make the tests below fail for an unrelated reason."""
    rel, _, node = _REAL_NODE.partition("::")
    source = (REPO / rel)
    assert source.exists(), f"{rel} no longer exists"
    assert f"def {node}(" in source.read_text(encoding="utf-8"), f"{node} no longer defined"


def test_a_consolidated_class_starts_green_and_prints_its_members_severity(tmp_path):
    """NOT-ALWAYS-RED. A completed consolidation passes rule 6, and the header it prints
    is the maximum over its members — so the red cases below mean something."""
    root, _blocker = _consolidated_wedge_class(tmp_path)
    doc = root / "CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md"

    assert fc.parse_severity_file(doc).severity == fc.BLOCKING
    result = fc.check(root)
    assert result.ok, result.failures


def test_an_empty_class_document_is_a_stub_not_a_stale_severity(tmp_path):
    """A class nobody has filed against has no severity to derive. Rendering writes a
    document for every declared class, so treating an empty one as unbacked would fail
    the live tree on four stubs."""
    root, _blocker = _consolidated_wedge_class(tmp_path)
    empty = [c for c in fc.CLASSES if c.id != "publish_gate_and_wedge"]
    assert empty, "fixture assumes more than one declared class"
    for finding_class in empty:
        doc = root / finding_class.document_name
        assert doc.exists(), f"{finding_class.document_name} was not rendered"
        assert fc._INSTANCE_LINE_RE.findall(doc.read_text(encoding="utf-8")) == []

    assert fc.check(root).ok


def test_discharging_the_last_blocking_member_makes_the_printed_severity_stale(tmp_path):
    """THE FALSIFIER. Discharge the only BLOCKING member of a consolidated class and the
    class document goes on printing BLOCKING while its instances now derive LATENT. Before
    rule 6 this state passed `check()` with zero failures, and the lane stayed frozen."""
    root, blocker = _consolidated_wedge_class(tmp_path)
    doc = root / "CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md"
    _discharge(blocker)

    assert fc.parse_severity_file(blocker).severity == fc.RECORDED, (
        "the discharge was refused — the fixture's evidence is not valid"
    )
    instances = fc.derive_memberships(root)["publish_gate_and_wedge"].instance_paths(root)
    assert fc.class_severity(instances)[0] == fc.LATENT
    assert fc.parse_severity_file(doc).severity == fc.BLOCKING, "header should still be stale"

    failures = fc.check(root).failures
    assert any(f.startswith("STALE SEVERITY") for f in failures), failures
    assert any("prints BLOCKING" in f and "derive LATENT" in f for f in failures), failures


def test_re_rendering_releases_the_class_document_and_the_lane(tmp_path):
    """R11, no orphan transitions: the release must have a tested EFFECT. After the
    discharge and a re-render the class document prints LATENT, `check()` is green, and
    `blocking_by_lane` no longer holds the class document against H_harness."""
    from background.finding_severity import blocking_by_lane, scan_staging_root

    root, blocker = _consolidated_wedge_class(tmp_path)
    doc = root / "CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md"
    assert doc.name in {
        p.path.name for p in blocking_by_lane(scan_staging_root(root)).get("H_harness", [])
    }, "the class document should start out blocking its lane"

    _discharge(blocker)
    fc._write_class_documents(root)

    assert fc.parse_severity_file(doc).severity == fc.LATENT
    assert fc.check(root).ok, fc.check(root).failures
    assert doc.name not in {
        p.path.name for p in blocking_by_lane(scan_staging_root(root)).get("H_harness", [])
    }, "a released class document must stop blocking its lane"


def test_mutation_f_dropping_the_severity_comparison_kills_that_test(tmp_path):
    """MUTATION F — SILENT REMOVAL. The shipped state: nothing re-derives the header."""
    mutant = _load_mutant(
        tmp_path,
        "if printed_severity != derived:",
        "if False:",
        "fc_mutant_f",
    )
    root, blocker = _consolidated_wedge_class(tmp_path)
    _discharge(blocker)

    assert any(f.startswith("STALE SEVERITY") for f in fc.check(root).failures)
    assert not any(f.startswith("STALE SEVERITY") for f in mutant.check(root).failures)
    assert mutant.check(root).ok, "the mutant reproduces the defect: stale header, PASS"


def test_mutation_g_comparing_only_upward_kills_that_test(tmp_path):
    """MUTATION G — FAIL-OPEN, and the subtle one. Fire only when the instances derive a
    HIGHER severity than the header prints. Escalation still works, so the rule looks
    alive and its other tests stay green; but a RELEASE is silently dropped, which is the
    exact 'a lane's blocker set can only grow' defect one layer up."""
    mutant = _load_mutant(
        tmp_path,
        "if printed_severity != derived:",
        "if _SEVERITY_RANK.get(derived, 2) > _SEVERITY_RANK.get(printed_severity, 2):",
        "fc_mutant_g",
    )
    root, blocker = _consolidated_wedge_class(tmp_path)
    _discharge(blocker)

    assert any(f.startswith("STALE SEVERITY") for f in fc.check(root).failures)
    assert not any(f.startswith("STALE SEVERITY") for f in mutant.check(root).failures)
    assert mutant.check(root).ok, "the mutant lets a release rot while escalation works"


def test_mutation_h_deriving_the_printed_severity_kills_that_test(tmp_path):
    """MUTATION H — TAUTOLOGY. Read the 'printed' severity from the instances instead of
    from the rendered document. The comparison then holds both sides from one source and
    can never fail, which is R15's first killer pattern."""
    mutant = _load_mutant(
        tmp_path,
        "printed_severity = parse_severity_file(doc).severity",
        "printed_severity = class_severity(instances)[0]",
        "fc_mutant_h",
    )
    root, blocker = _consolidated_wedge_class(tmp_path)
    _discharge(blocker)

    assert any(f.startswith("STALE SEVERITY") for f in fc.check(root).failures)
    assert not any(f.startswith("STALE SEVERITY") for f in mutant.check(root).failures)
    assert mutant.check(root).ok, "a tautological comparison cannot fail"
