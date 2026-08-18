"""Tests for `background/finding_severity.py` — atom `OPS9_finding_severity_field`.

R15 governs the shape of this file. The module is the INPUT to two refusal mechanisms
(OPS11's lane-scoped level refusal, OPS12's blocker-first draw), so the only thing worth
proving is that it can FAIL. Two mutations are applied to a COPY of the module source and
each must kill a NAMED test:

  MUTATION A (fail-open) — the missing-header branch returns LATENT instead of
      UNCLASSIFIED. Kills `test_a_missing_header_reads_unclassified_never_latent`.
      This is the exact shape clause 2 forbids: a document becomes "not blocking" by
      nobody having classified it.
  MUTATION B (lane dropped) — the successful parse returns the severity without its lane.
      Kills `test_the_parse_returns_the_lane_beside_the_severity`. A lane-less severity
      cannot be acted on, because the refusal it feeds is lane-scoped.

The mutants are loaded from `tmp_path` under a unique module name, never by editing the
real file: editing a source file mid-pytest corrupts `inspect.getsource`, and a
same-length mutation can survive its own restoration through the `.pyc` cache (both are
filed findings in this project). A copy under a fresh name has neither failure mode.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from background import finding_severity as fs

REPO = Path(__file__).resolve().parents[2]
MODULE_SOURCE = REPO / "background" / "finding_severity.py"

CLEAN = """# [WORKER-FINDING] Something was measured wrong

**Severity:** LATENT · **Lane:** H_harness

## The claim
Body text.
"""


def _load_mutant(tmp_path: Path, old: str, new: str, name: str):
    """Import a copy of the module with `old` replaced by `new`. Asserts the mutation
    actually applied — a no-op mutation would make its test pass for the wrong reason,
    which is how a mutation proof becomes theatre."""
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


# --- the two properties the mutations attack, factored so one assertion serves both ---

def _assert_missing_header_reads_unclassified(module) -> None:
    result = module.parse_severity_text("# A finding with no header\n\nBody.\n")
    assert result.severity == module.UNCLASSIFIED
    assert result.severity != module.LATENT
    assert result.is_classified is False


def _assert_parse_returns_the_lane(module) -> None:
    result = module.parse_severity_text(CLEAN)
    assert result.severity == module.LATENT
    assert result.lane == "H_harness"


def test_a_missing_header_reads_unclassified_never_latent():
    """FAIL-CLOSED. The absent case is surfaced, never silently defaulted to LATENT."""
    _assert_missing_header_reads_unclassified(fs)


def test_mutation_a_defaulting_the_missing_header_to_latent_kills_a_named_test(tmp_path):
    mutant = _load_mutant(
        tmp_path,
        'return FindingSeverity(where, UNCLASSIFIED, None, "no severity header")',
        'return FindingSeverity(where, LATENT, None, "no severity header")',
        "finding_severity_mutant_fail_open",
    )
    _assert_parse_returns_the_lane(mutant)  # the clean input still passes under the mutation
    with pytest.raises(AssertionError):
        _assert_missing_header_reads_unclassified(mutant)


def test_the_parse_returns_the_lane_beside_the_severity():
    """Clause 2's refusal is lane-scoped, so the lane is half the answer, not metadata."""
    _assert_parse_returns_the_lane(fs)


def test_mutation_b_dropping_the_lane_from_the_parse_kills_a_named_test(tmp_path):
    mutant = _load_mutant(
        tmp_path,
        "return FindingSeverity(where, value, lane)",
        "return FindingSeverity(where, value, None)",
        "finding_severity_mutant_lane_dropped",
    )
    _assert_missing_header_reads_unclassified(mutant)  # the other property is untouched
    with pytest.raises(AssertionError):
        _assert_parse_returns_the_lane(mutant)


# --- the rest of the fail-closed surface ---

def test_the_clean_input_passes_and_reports_all_three_values():
    for value in fs.SEVERITIES:
        text = CLEAN.replace("LATENT", value)
        assert fs.parse_severity_text(text).severity == value


def test_a_severity_without_a_lane_is_unclassified_not_a_half_answer():
    result = fs.parse_severity_text("# T\n\n**Severity:** BLOCKING\n\n## Body\n")
    assert result.severity == fs.UNCLASSIFIED
    assert "lane missing" in result.reason


def test_an_unknown_lane_is_unclassified():
    result = fs.parse_severity_text("# T\n\n**Severity:** LATENT · **Lane:** Z_not_a_lane\n")
    assert result.severity == fs.UNCLASSIFIED
    assert "not a known lane" in result.reason


def test_a_prose_severity_sentence_does_not_classify_a_document():
    """Findings written before this atom used `**Severity:** this is the mechanism that...`
    as prose. That is unparseable, so it reads UNCLASSIFIED — and a well-formed header
    further down does NOT rescue it, because scanning past a malformed first occurrence is
    how the parser would fail open on the documents most likely to be mis-headered."""
    text = (
        "# T\n\n**Severity:** this is the mechanism that kept the wedge invisible\n"
        "**Severity:** LATENT · **Lane:** H_harness\n"
    )
    result = fs.parse_severity_text(text)
    assert result.severity == fs.UNCLASSIFIED


def test_a_header_below_the_header_block_does_not_classify():
    body = "# T\n\nIntro.\n\n## Section\n\n**Severity:** RECORDED · **Lane:** H_harness\n"
    assert fs.parse_severity_text(body).severity == fs.UNCLASSIFIED


def test_an_unreadable_file_is_unclassified_because_an_unavailable_check_is_a_failed_one(
    tmp_path,
):
    missing = tmp_path / "gone.md"
    result = fs.parse_severity_file(missing)
    assert result.severity == fs.UNCLASSIFIED
    assert "unreadable" in result.reason


def test_the_population_is_counted_from_the_filesystem(tmp_path):
    """Exit criterion 2: never a hand-kept list. A file dropped in is in the population."""
    (tmp_path / "a.md").write_text(CLEAN, encoding="utf-8")
    assert len(fs.scan_staging_root(tmp_path)) == 1
    (tmp_path / "b.md").write_text("# no header\n", encoding="utf-8")
    results = fs.scan_staging_root(tmp_path)
    assert len(results) == 2
    assert [r.path.name for r in fs.unclassified(results)] == ["b.md"]


def test_a_machine_doorbell_is_out_of_the_population_and_only_by_exact_prefix(tmp_path):
    """`run_complete_*` is written on every sim run and archived minutes later. It is not
    an authored finding. The exclusion is exact-prefix, so a finding cannot hide behind a
    lookalike name."""
    (tmp_path / "run_complete_20260812T085534Z.md").write_text("# doorbell\n", encoding="utf-8")
    (tmp_path / "WORKER_FINDING_run_complete_lookalike.md").write_text("# f\n", encoding="utf-8")
    names = [p.name for p in fs.classifiable_documents(tmp_path)]
    assert names == ["WORKER_FINDING_run_complete_lookalike.md"]
    assert len(fs.unclassified(fs.scan_staging_root(tmp_path))) == 1


def test_blocking_findings_group_by_lane(tmp_path):
    (tmp_path / "h.md").write_text(
        CLEAN.replace("LATENT", "BLOCKING"), encoding="utf-8")
    (tmp_path / "d.md").write_text(
        CLEAN.replace("LATENT", "BLOCKING").replace("H_harness", "D_billing_metering"),
        encoding="utf-8")
    (tmp_path / "l.md").write_text(CLEAN, encoding="utf-8")
    grouped = fs.blocking_by_lane(fs.scan_staging_root(tmp_path))
    assert sorted(grouped) == ["D_billing_metering", "H_harness"]
    assert [f.path.name for f in grouped["H_harness"]] == ["h.md"]


# --- exit criterion 4: the by-construction rule is checkable, not merely written ---

_SAYS_AN_INSTRUMENT_IS_WRONG = (
    "# T\n\n**Severity:** {value} · **Lane:** H_harness\n\n"
    "## The claim\nThe gate that certifies this lane is lying about its own subject.\n"
)


def test_a_document_saying_an_instrument_is_wrong_is_named_when_not_blocking(tmp_path):
    (tmp_path / "mis.md").write_text(
        _SAYS_AN_INSTRUMENT_IS_WRONG.format(value="LATENT"), encoding="utf-8")
    named = fs.by_construction_violations(tmp_path)
    assert [r.path.name for r, _ in named] == ["mis.md"]


def test_the_same_document_classified_blocking_is_not_named(tmp_path):
    (tmp_path / "ok.md").write_text(
        _SAYS_AN_INSTRUMENT_IS_WRONG.format(value="BLOCKING"), encoding="utf-8")
    assert fs.by_construction_violations(tmp_path) == []


def test_an_unclassified_document_saying_an_instrument_is_wrong_is_named(tmp_path):
    """The namer must reach UNCLASSIFIED too — otherwise the cheapest way to escape the
    by-construction rule would be to write no header at all."""
    (tmp_path / "bare.md").write_text(
        "# T\n\nA published figure on this page is wrong.\n", encoding="utf-8")
    assert [r.path.name for r, _ in fs.by_construction_violations(tmp_path)] == ["bare.md"]


# --- the escape hatch names its subject, or it is not an escape hatch
# (WORKER_FINDING_THE_BY_CONSTRUCTION_GATE_IS_SILENCED_BY_AN_ORDINARY_WORD_2026-08-12,
#  defect 1: a bare word match anywhere in the header took a whole document off the
#  census, so the census measured authorship convention rather than the corpus) ---

@pytest.mark.parametrize(
    "word", ["FIXED", "CLOSED", "REPAIRED", "repaired", "landed", "relieved",
             "CLEARED", "cleared", "DISCHARGED", "discharged", "accepted"])
def test_an_ordinary_word_in_the_header_does_not_stand_the_namer_down(tmp_path, word):
    """Each of the eleven words the old free-text escape released on. `landed`, `cleared`
    and `accepted` are ordinary finding prose ("the cut landed", "the queue cleared"), and
    none of them says THIS defect was repaired."""
    doc = tmp_path / f"{word.lower()}.md"
    doc.write_text(
        _SAYS_AN_INSTRUMENT_IS_WRONG.format(value="LATENT").replace(
            "**Lane:** H_harness", f"**Lane:** H_harness\n\nPrior work {word} separately."),
        encoding="utf-8")
    assert [r.path.name for r, _ in fs.by_construction_violations(tmp_path)] == [doc.name]


def test_only_a_valid_discharge_stands_the_namer_down(tmp_path):
    """The structured field, checked against the filesystem — the one release shape that
    names its own subject and carries a runnable falsifier."""
    repo, doc = _repo_with(
        tmp_path,
        "tests/test_real.py::test_it",
        {"tests/test_real.py": "def test_it():\n    pass\n"},
    )
    doc.write_text(
        doc.read_text().replace("**Severity:** BLOCKING", "**Severity:** LATENT")
        + "\nThe gate that certifies this lane is lying about its own subject.\n",
        encoding="utf-8")
    assert fs.by_construction_violations(doc.parent, repo) == []


def test_a_discharge_the_filesystem_refuses_does_not_stand_the_namer_down(tmp_path):
    """A release that does not release must not silence the namer either — otherwise the
    typo that voids the discharge also hides the finding it failed to close."""
    repo, doc = _repo_with(tmp_path, "tools/ghost.py")
    doc.write_text(
        doc.read_text().replace("**Severity:** BLOCKING", "**Severity:** LATENT")
        + "\nThe gate that certifies this lane is lying about its own subject.\n",
        encoding="utf-8")
    assert [r.path.name for r, _ in fs.by_construction_violations(doc.parent, repo)] == [doc.name]


def test_the_body_of_a_document_never_releases_it(tmp_path):
    """Scope rule, unchanged: a retrospective paragraph forty lines down saying a similar
    thing was fixed once is not this document's release."""
    (tmp_path / "body.md").write_text(
        _SAYS_AN_INSTRUMENT_IS_WRONG.format(value="LATENT")
        + "\n## Retro\nA similar defect was FIXED last week.\n", encoding="utf-8")
    assert [r.path.name for r, _ in fs.by_construction_violations(tmp_path)] == ["body.md"]


# --- defect 2: the phrase matched inside its own denial ---

def test_a_phrase_inside_its_own_denial_is_not_evidence():
    """The sentence that found this defect, verbatim from
    `WORKER_FINDING_A_MUTATION_THAT_PATCHES_BOTH_SIDES_OF_ITS_SEAM_2026-08-12.md`."""
    denial = ("Not a claim that any published figure is wrong: no gap value on the live "
              "record depends on either control.")
    assert fs.by_construction_evidence(denial) == []


def test_the_denial_releases_only_its_own_sentence():
    """A denial is not a blanket. The next sentence is read on its own terms — erring
    toward NAMING, because a missed name is the fail-open direction here."""
    text = ("This does not claim the gate is broken. But the published figure is wrong, "
            "and the door still serves it.\n")
    assert fs.by_construction_evidence(text) == ["published figure is wrong"]


def test_an_ordinary_negation_does_not_read_as_a_denial_of_the_claim():
    """The guard is scoped to the explicit denial-of-a-claim shape. A sentence merely
    containing "not" still names — widening this is how a negation guard becomes the
    fail-open hole it was built to close."""
    text = "This is not a small thing: the report says the published figure is wrong.\n"
    assert fs.by_construction_evidence(text) == ["published figure is wrong"]


def test_mutation_f_restoring_the_free_text_escape_kills_a_named_test(tmp_path):
    """MUTATION F — the escape hatch goes back to matching a bare word in the header."""
    mutant = _load_mutant(
        tmp_path,
        "        discharge = parse_discharge(text, repo_root)\n"
        "        if discharge is not None and discharge.released:\n            continue",
        "        if re.search(r'\\b(?:landed|cleared|accepted|FIXED)\\b', header_block(text)):\n"
        "            continue",
        "finding_severity_mutant_free_text_escape",
    )
    doc = tmp_path / "f_mut"
    doc.mkdir()
    (doc / "mis.md").write_text(
        _SAYS_AN_INSTRUMENT_IS_WRONG.format(value="LATENT").replace(
            "**Lane:** H_harness", "**Lane:** H_harness\n\nPrior work landed separately."),
        encoding="utf-8")
    assert [r.path.name for r, _ in fs.by_construction_violations(doc)] == ["mis.md"]
    assert mutant.by_construction_violations(doc) == []  # the defect, reproduced


def test_mutation_g_dropping_the_denial_guard_kills_a_named_test(tmp_path):
    """MUTATION G — evidence is collected without asking whether the phrase was denied."""
    mutant = _load_mutant(
        tmp_path,
        "            if not _is_denied(text, m.start())",
        "            if True",
        "finding_severity_mutant_no_denial_guard",
    )
    denial = "Not a claim that any published figure is wrong: no gap value depends on it."
    assert fs.by_construction_evidence(denial) == []
    assert mutant.by_construction_evidence(denial) != []  # the defect, reproduced


# --- the live population, and the vocabulary it is classified against ---

def test_the_lane_vocabulary_matches_the_maturity_map():
    """LANES is hard-coded so an importer never dies on a mid-write map. The drift check
    belongs HERE, where a disagreement is visible instead of fatal."""
    atoms = yaml.safe_load((REPO / "docs" / "design" / "maturity_map.yaml").read_text())
    rows = atoms["atoms"] if isinstance(atoms, dict) else atoms
    in_map = {a["lane"] for a in rows if isinstance(a, dict) and a.get("lane")}
    assert in_map <= set(fs.LANES), f"lanes in the map but not in LANES: {in_map - set(fs.LANES)}"


def test_the_staging_root_has_zero_unclassified_documents():
    """Exit criterion 2 — the OPS9 pass, held. If this fails you staged a finding without
    its header; add ONE line under the title and it goes green:

        **Severity:** LATENT · **Lane:** H_harness

    BLOCKING if a control/instrument in that lane is untrustworthy or a published figure
    may be wrong; LATENT if it is a real defect that invalidates nothing published;
    RECORDED if it is an accepted limitation with no work owed."""
    open_ = fs.unclassified(fs.scan_staging_root())
    assert not open_, "unclassified staging documents:\n" + "\n".join(
        f"  {r.path.name}: {r.reason}" for r in open_
    )


# --- THE DISCHARGE FIELD (2026-08-12, the rung-1c draw on 14 live H_harness blockers) ---
#
# R15 governs this block the same way it governs the two mutations above. This field is a
# RELEASE — the only thing in the module that turns a BLOCKING document into a
# non-blocking one — so the property worth proving is that it REFUSES. Three more
# mutations, each killing a named test:
#
#   MUTATION C (release without a falsifier) — the "no test node" branch releases anyway.
#       Kills `test_a_discharge_naming_no_test_node_does_not_release`. This is the vacuity
#       shape: typing a source path would close a blocker.
#   MUTATION D (release on a missing artefact) — the existence check is dropped.
#       Kills `test_a_discharge_naming_an_artefact_that_does_not_exist_does_not_release`.
#       Fail-open on a typo, which is how a lane goes clean by accident.
#   MUTATION E (invalid claim releases silently) — an unreleased discharge still reads the
#       severity down. Kills `test_an_invalid_discharge_leaves_the_severity_where_it_was`.

_DISCHARGE_DOC = """# A finding whose repair landed

**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `{artefacts}` — the instrument was repaired in the same tick

## Body
Text.
"""


def _repo_with(
    tmp_path: Path,
    artefacts: str,
    files: dict[str, str] | None = None,
    *,
    staged: bool = True,
) -> tuple[Path, Path]:
    """A tmp GIT repo root + staging root holding one document that claims `artefacts`.

    A REAL repository, not a bare directory: since 2026-08-18 the discharge's evidence is
    read from the INDEX, so a fixture that is not a work tree can only ever exercise the
    unavailable-index refusal. `staged=False` writes the artefacts to disk and leaves them
    OUT of the index — the shipped defect's own shape, and the reason `README.md` is always
    staged (an empty index is "cannot answer", which is a different refusal).
    """
    tmp_path.mkdir(parents=True, exist_ok=True)
    _git(tmp_path, "init", "-q")
    (tmp_path / "README.md").write_text("a repository\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")

    staging = tmp_path / "docs" / "staging"
    staging.mkdir(parents=True)
    for relative, content in (files or {}).items():
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        if staged:
            _git(tmp_path, "add", relative)
    doc = staging / "WORKER_FINDING_X.md"
    doc.write_text(_DISCHARGE_DOC.format(artefacts=artefacts), encoding="utf-8")
    return tmp_path, doc


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def _assert_no_test_node_does_not_release(module, tmp_path: Path) -> None:
    repo, doc = _repo_with(tmp_path, "tools/real.py", {"tools/real.py": "x = 1\n"})
    discharge = module.parse_discharge(doc.read_text(), repo)
    assert discharge.released is False
    assert "falsifier" in discharge.reason


def _assert_missing_artefact_does_not_release(module, tmp_path: Path) -> None:
    repo, doc = _repo_with(
        tmp_path,
        "tests/test_real.py::test_it",
        {"tests/test_real.py": "def test_it():\n    pass\n"},
    )
    doc.write_text(
        doc.read_text().replace("tests/test_real.py::test_it", "tests/test_ghost.py::test_it"),
        encoding="utf-8",
    )
    discharge = module.parse_discharge(doc.read_text(), repo)
    assert discharge.released is False
    assert "does not exist" in discharge.reason


def _assert_a_real_falsifier_does_release(module, tmp_path: Path) -> None:
    repo, doc = _repo_with(
        tmp_path,
        "tests/test_real.py::test_it",
        {"tests/test_real.py": "def test_it():\n    pass\n"},
    )
    discharge = module.parse_discharge(doc.read_text(), repo)
    assert discharge.released is True
    assert module.parse_severity_file(doc, repo).severity == module.RECORDED


def test_a_valid_discharge_reads_a_blocking_document_down_to_recorded(tmp_path):
    """Clause 2's own release ("until it is repaired"), made machine-readable — the thing
    whose absence let a lane's blocker set only ever grow."""
    _assert_a_real_falsifier_does_release(fs, tmp_path)


def test_a_discharge_naming_no_test_node_does_not_release(tmp_path):
    """A release needs a NAMED FALSIFIER. A source path proves the author typed a path."""
    _assert_no_test_node_does_not_release(fs, tmp_path)


def test_a_discharge_naming_an_artefact_that_does_not_exist_does_not_release(tmp_path):
    _assert_missing_artefact_does_not_release(fs, tmp_path)


def test_a_discharge_whose_file_does_not_define_the_node_does_not_release(tmp_path):
    """The file existing is not the claim; the file DEFINING the falsifier is."""
    repo, doc = _repo_with(
        tmp_path,
        "tests/test_real.py::test_something_else",
        {"tests/test_real.py": "def test_it():\n    pass\n"},
    )
    discharge = fs.parse_discharge(doc.read_text(), repo)
    assert discharge.released is False
    assert "does not define the node" in discharge.reason


def test_an_invalid_discharge_leaves_the_severity_where_it_was(tmp_path):
    """The anti-loophole: a malformed release that released would be worse than none."""
    repo, doc = _repo_with(tmp_path, "tools/real.py", {"tools/real.py": "x = 1\n"})
    assert fs.parse_severity_file(doc, repo).severity == fs.BLOCKING


def test_an_invalid_discharge_is_surfaced_not_silent(tmp_path):
    """The author believes the finding is closed and will not look again, so the refusal
    has to be LOUD."""
    repo, doc = _repo_with(tmp_path, "tools/real.py", {"tools/real.py": "x = 1\n"})
    refused = fs.false_discharges(doc.parent, repo)
    assert [p.name for p, _ in refused] == ["WORKER_FINDING_X.md"]


def test_a_document_with_no_discharge_field_is_untouched(tmp_path):
    assert fs.parse_discharge(CLEAN) is None
    assert fs.parse_severity_text(CLEAN).severity == fs.LATENT


def test_a_discharge_below_the_header_block_does_not_release(tmp_path):
    """Same scope rule as every other field here: a release the next reader never meets
    is not a release."""
    repo, doc = _repo_with(
        tmp_path,
        "tests/test_real.py::test_it",
        {"tests/test_real.py": "def test_it():\n    pass\n"},
    )
    text = doc.read_text()
    header, _, body = text.partition("## Body")
    doc.write_text(
        header.replace("**Discharged:**", "Once said, in prose:") + "## Body" + body
        + "\n**Discharged:** `tests/test_real.py::test_it` — too late to count\n",
        encoding="utf-8",
    )
    assert fs.parse_severity_file(doc, repo).severity == fs.BLOCKING


def test_mutation_c_releasing_without_a_falsifier_kills_a_named_test(tmp_path):
    mutant = _load_mutant(
        tmp_path,
        "    if not nodes_ok:\n        return Discharge(",
        "    if False:\n        return Discharge(",
        "finding_severity_mutant_no_falsifier",
    )
    _assert_missing_artefact_does_not_release(mutant, tmp_path / "d_ok")  # untouched property
    with pytest.raises(AssertionError):
        _assert_no_test_node_does_not_release(mutant, tmp_path / "c_mut")


def test_mutation_d_dropping_the_existence_check_kills_a_named_test(tmp_path):
    mutant = _load_mutant(
        tmp_path,
        "        if file_part not in tracked:\n"
        "            (unstaged if (root / file_part).exists() else missing).append(artefact)\n"
        "            continue",
        "        if file_part not in tracked:\n            continue",
        "finding_severity_mutant_no_existence",
    )
    with pytest.raises(AssertionError):
        _assert_missing_artefact_does_not_release(mutant, tmp_path / "d_mut")


def test_mutation_e_letting_an_invalid_discharge_release_kills_a_named_test(tmp_path):
    mutant = _load_mutant(
        tmp_path,
        "    if discharge is None or not discharge.released:\n        return parsed",
        "    if discharge is None:\n        return parsed",
        "finding_severity_mutant_invalid_releases",
    )
    _assert_a_real_falsifier_does_release(mutant, tmp_path / "e_ok")  # the valid path still works
    repo, doc = _repo_with(tmp_path / "e_mut", "tools/real.py", {"tools/real.py": "x = 1\n"})
    assert mutant.parse_severity_file(doc, repo).severity == mutant.RECORDED  # the defect


# ── WHICH TREE THE EVIDENCE IS READ FROM (2026-08-18, rung-1c BLOCKING draw, H_harness) ──
#
# WORKER_FINDING_THE_DISCHARGE_RELEASE_READS_THE_NODE_FROM_THE_WORKING_TREE_AND_ITS_CONTROL_
# READS_ONLY_THE_FILE_2026-08-18 measured the hole: the release resolved the cited NODE
# against `repo_root` on disk, and the `tests/architecture/` control that was supposed to
# keep it honest checked only the FILE, against the index. Nothing checked the node against
# the index, so a discharge citing a long-committed test file and a node that existed only
# in the author's editor released the document AND passed the control — 10 such citations,
# in 2 committed records, both already archived.
#
# The three tests below are the falsifiers for that repair, and MUTATION H is the R15 proof:
# it puts the working-tree read back and the first of them must die.


def test_a_node_that_exists_only_in_the_working_tree_does_not_release(tmp_path):
    """THE SHIPPED DEFECT, reproduced: file committed, node not.

    This is the shape a whole-file check cannot see and a working-tree read cannot refuse —
    the file is in the index, so "does the repository have the falsifier" says yes, while
    the falsifier itself is on exactly one machine.
    """
    repo, doc = _repo_with(
        tmp_path,
        "tests/test_real.py::test_added_but_not_staged",
        {"tests/test_real.py": "def test_it():\n    pass\n"},
    )
    (repo / "tests" / "test_real.py").write_text(
        "def test_it():\n    pass\n\n\ndef test_added_but_not_staged():\n    pass\n",
        encoding="utf-8",
    )
    discharge = fs.parse_discharge(doc.read_text(), repo)
    assert discharge.released is False, (
        "a node present only in the working tree released the finding — that is the defect"
    )
    assert "does not define the node" in discharge.reason


def test_an_artefact_on_disk_but_not_in_the_index_does_not_release(tmp_path):
    """The file half, at the same standard: on this disk only is not a landed falsifier."""
    repo, doc = _repo_with(
        tmp_path,
        "tests/test_real.py::test_it",
        {"tests/test_real.py": "def test_it():\n    pass\n"},
        staged=False,
    )
    discharge = fs.parse_discharge(doc.read_text(), repo)
    assert discharge.released is False
    assert "does not exist in the index" in discharge.reason


def test_an_unreadable_index_refuses_rather_than_releasing(tmp_path, monkeypatch):
    """R15 FAIL-SILENT: git missing or the root not a work tree is a FAILED check.

    Both doors, because they fail through different code: a root with no repository at all,
    and `git` itself unavailable on a root that has one.
    """
    bare = tmp_path / "not_a_repo"
    (bare / "docs" / "staging").mkdir(parents=True)
    (bare / "tests").mkdir()
    (bare / "tests" / "test_real.py").write_text("def test_it():\n    pass\n", encoding="utf-8")
    doc = bare / "docs" / "staging" / "WORKER_FINDING_X.md"
    doc.write_text(
        _DISCHARGE_DOC.format(artefacts="tests/test_real.py::test_it"), encoding="utf-8")
    refused = fs.parse_discharge(doc.read_text(), bare)
    assert refused.released is False
    assert "unavailable check is a FAILED check" in refused.reason

    repo, real_doc = _repo_with(
        tmp_path / "real", "tests/test_real.py::test_it",
        {"tests/test_real.py": "def test_it():\n    pass\n"},
    )
    assert fs.parse_discharge(real_doc.read_text(), repo).released is True  # precondition

    def _boom(*_a, **_k):
        raise OSError("git not on PATH")

    monkeypatch.setattr(fs.subprocess, "run", _boom)
    fs._INDEX_FILES_CACHE.clear()
    fs._INDEX_BLOB_CACHE.clear()
    blinded = fs.parse_discharge(real_doc.read_text(), repo)
    assert blinded.released is False, "an unavailable check must never read as a release"
    assert "unavailable check is a FAILED check" in blinded.reason


def test_mutation_h_reading_the_node_from_the_working_tree_kills_a_named_test(tmp_path):
    """MUTATION H — the shipped defect, put back. R15 TAUTOLOGY: the check asks the one
    tree guaranteed to contain the work whose absence it is about."""
    mutant = _load_mutant(
        tmp_path,
        "        blob = _index_blob(root, file_part)",
        "        blob = (root / file_part).read_text(encoding='utf-8', errors='replace')",
        "finding_severity_mutant_worktree_node",
    )
    _assert_a_real_falsifier_does_release(mutant, tmp_path / "h_ok")  # untouched property

    repo, doc = _repo_with(
        tmp_path / "h_mut",
        "tests/test_real.py::test_added_but_not_staged",
        {"tests/test_real.py": "def test_it():\n    pass\n"},
    )
    (repo / "tests" / "test_real.py").write_text(
        "def test_it():\n    pass\n\n\ndef test_added_but_not_staged():\n    pass\n",
        encoding="utf-8",
    )
    assert mutant.parse_discharge(doc.read_text(), repo).released is True  # the defect


# ── THE MULTI-LINE CLAIM (§4 of the same finding) ──


_SIX_LINE_DISCHARGE = """# A finding whose repair landed

**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/test_real.py::test_one`,
`tests/test_real.py::test_two`,
`{third}`
— 2026-08-18 worker tick, all three taken.

## Body
Text.
"""


def _six_line_repo(tmp_path: Path, third: str) -> tuple[Path, Path]:
    repo, doc = _repo_with(
        tmp_path,
        "unused",
        {"tests/test_real.py": "def test_one():\n    pass\n\n\ndef test_two():\n    pass\n"},
    )
    doc.write_text(_SIX_LINE_DISCHARGE.format(third=third), encoding="utf-8")
    return repo, doc


def test_a_discharge_spread_over_several_lines_claims_every_artefact_on_them(tmp_path):
    """A list continued across lines is ONE claim. Reading its first line only meant five
    sixths of a real discharge — including any artefact that did not exist — sat outside the
    checked claim while the release fired on the first."""
    repo, doc = _six_line_repo(tmp_path, "tests/test_real.py::test_one")
    discharge = fs.parse_discharge(doc.read_text(), repo)
    assert len(discharge.artefacts) == 3, discharge.artefacts
    assert discharge.released is True


def test_a_bad_artefact_on_a_continuation_line_voids_the_whole_discharge(tmp_path):
    """The property that makes the line above worth having: the third line is checked."""
    repo, doc = _six_line_repo(tmp_path, "tests/test_ghost.py::test_three")
    discharge = fs.parse_discharge(doc.read_text(), repo)
    assert discharge.released is False
    assert "does not exist" in discharge.reason


def test_the_authors_reason_line_is_not_read_as_artefacts(tmp_path):
    """The continuation rule is 'the line so far ends in a comma', not 'swallow to the
    blank line' — otherwise every backticked symbol in the reason becomes a claimed path."""
    repo, doc = _six_line_repo(tmp_path, "tests/test_real.py::test_two")
    doc.write_text(
        doc.read_text().replace(
            "— 2026-08-18 worker tick, all three taken.",
            "— 2026-08-18 worker tick; `tools/ghost.py` is discussed, not claimed.",
        ),
        encoding="utf-8",
    )
    discharge = fs.parse_discharge(doc.read_text(), repo)
    assert "tools/ghost.py" not in discharge.artefacts
    assert discharge.released is True


def test_mutation_i_reading_only_the_first_line_kills_a_named_test(tmp_path):
    """MUTATION I — the one-line regex, put back: the third artefact stops being claimed."""
    mutant = _load_mutant(
        tmp_path,
        "        if not value[-1].rstrip().endswith(_CONTINUES):\n            break",
        "        if True:\n            break",
        "finding_severity_mutant_one_line_discharge",
    )
    repo, doc = _six_line_repo(tmp_path, "tests/test_ghost.py::test_three")
    assert fs.parse_discharge(doc.read_text(), repo).released is False  # the control
    assert mutant.parse_discharge(doc.read_text(), repo).released is True  # the defect


def test_the_staging_root_has_no_false_discharges():
    """A discharge the filesystem refuses is a blocker its author has stopped watching."""
    refused = fs.false_discharges()
    assert not refused, "discharge claims the filesystem refuses:\n" + "\n".join(
        f"  {p.name}: {d.reason}" for p, d in refused
    )


# ── THE EXONERATION FIELD (2026-08-12, RUNG-1c BLOCKING draw on lane H_harness) ──
#
# WHY: `process_run_complete.linked_findings` links a staged finding to a publish wedge by
# LEXICAL CO-OCCURRENCE with the red's blame trail. An accusation and a REFUTATION are the
# same tokens, so answering a RUNG-1 draw as instructed ("re-freeze with provenance" — which
# must NAME the cause in order to deny it) raised one document's suspect score from 2 to 7
# and got it re-cited to the next priority-zero draw. Of the two dispositions the draw offers,
# the citation could observe exactly one: fix-and-archive clears it, re-freeze never can.
# That is R11's orphan transition — a release whose effect is nothing.
#
# The field gives the citation the one thing it could not read: the finding's OWN ANSWER.
# Two properties keep it from becoming a blanket opt-out of ever being cited:
#   * it must name a TEST FILE, and it must name EVERY blocking test file of the current
#     red — exonerating yourself for test A does nothing when the red is test B;
#   * it lives in the parsed HEADER BLOCK and every path it names must EXIST, so a claim
#     buried in prose, or a typo, does not silently suppress a real suspect.

EXONERATED = """# [WORKER-FINDING] Something else entirely

**Severity:** LATENT · **Lane:** H_harness
**Not-a-suspect-for:** `tests/background/test_thing.py` — checked against the 19th wedge, not its cause

## The claim
Body text naming tests/background/test_thing.py all over the place.
"""


def _repo_with_test_file(root: Path, rel: str = "tests/background/test_thing.py") -> Path:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("def test_thing():\n    pass\n", encoding="utf-8")
    return root


# --- the properties, factored so the mutations below can attack them by name ---

def _assert_a_named_test_exonerates(module, root: Path) -> None:
    _repo_with_test_file(root)
    ex = module.parse_exoneration(EXONERATED, root)
    assert ex is not None and ex.valid, ex.reason if ex else "no exoneration parsed"
    assert ex.covers(["tests/background/test_thing.py"]) is True


def _assert_a_different_red_is_not_covered(module, root: Path) -> None:
    _repo_with_test_file(root)
    ex = module.parse_exoneration(EXONERATED, root)
    assert ex is not None and ex.valid
    assert ex.covers(["tests/background/test_other.py"]) is False, (
        "exonerating for test A must not exonerate for test B"
    )


def _assert_a_missing_path_does_not_exonerate(module, root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)  # the named test file is deliberately absent
    ex = module.parse_exoneration(EXONERATED, root)
    assert ex is not None
    assert ex.valid is False, "an exoneration naming a path that does not exist must be REFUSED"
    assert ex.covers(["tests/background/test_thing.py"]) is False


def _assert_a_non_test_artefact_does_not_exonerate(module, root: Path) -> None:
    (root / "background").mkdir(parents=True, exist_ok=True)
    (root / "background" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    text = EXONERATED.replace("`tests/background/test_thing.py`", "`background/thing.py`")
    ex = module.parse_exoneration(text, root)
    assert ex is not None and ex.valid is False, (
        "the field exonerates against the RED's blocking TEST; a module path is a wider claim"
    )


def test_a_named_test_exonerates_the_document_for_that_red(tmp_path):
    _assert_a_named_test_exonerates(fs, tmp_path / "ok")


def test_exonerating_for_one_test_does_not_exonerate_for_another(tmp_path):
    """The blanket-opt-out guard. Without this the field is 'never cite me again'."""
    _assert_a_different_red_is_not_covered(fs, tmp_path / "other")


def test_an_exoneration_naming_a_path_that_does_not_exist_is_refused(tmp_path):
    """FAIL-CLOSED: an unverifiable release leaves the document a suspect (R15 pattern 2)."""
    _assert_a_missing_path_does_not_exonerate(fs, tmp_path / "missing")


def test_an_exoneration_must_name_a_test_file_not_a_module(tmp_path):
    _assert_a_non_test_artefact_does_not_exonerate(fs, tmp_path / "module")


def test_a_document_with_no_field_makes_no_claim(tmp_path):
    assert fs.parse_exoneration(CLEAN, tmp_path) is None


def test_the_claim_must_sit_in_the_header_block_not_in_prose(tmp_path):
    """A `**Not-a-suspect-for:**` line written down in §4 is prose, not a header — the same
    rule the severity and discharge fields already hold to."""
    _repo_with_test_file(tmp_path)
    buried = CLEAN + "\n" * 45 + "**Not-a-suspect-for:** `tests/background/test_thing.py`\n"
    assert fs.parse_exoneration(buried, tmp_path) is None


def test_an_exoneration_covers_nothing_when_the_red_names_no_test(tmp_path):
    """A red with no recorded blocking TEST cannot be answered by this field — covering an
    empty set would exonerate every document against every trail."""
    _repo_with_test_file(tmp_path)
    ex = fs.parse_exoneration(EXONERATED, tmp_path)
    assert ex.covers([]) is False
    assert ex.covers(None) is False


def test_mutation_f_covering_the_empty_trail_kills_a_named_test(tmp_path):
    mutant = _load_mutant(
        tmp_path,
        "        if not wanted:\n            return False",
        "        if not wanted:\n            return True",
        "finding_severity_mutant_empty_trail_covers",
    )
    _assert_a_named_test_exonerates(mutant, tmp_path / "f_ok")  # the valid path still works
    _repo_with_test_file(tmp_path / "f_mut")
    assert mutant.parse_exoneration(EXONERATED, tmp_path / "f_mut").covers([]) is True  # defect


def test_mutation_g_subset_becomes_intersection_kills_a_named_test(tmp_path):
    """The mutation that turns 'names EVERY blocking test' into 'names ANY of them'."""
    mutant = _load_mutant(
        tmp_path,
        "        return wanted <= named",
        "        return bool(wanted & named)",
        "finding_severity_mutant_any_not_all",
    )
    _assert_a_named_test_exonerates(mutant, tmp_path / "g_ok")
    _repo_with_test_file(tmp_path / "g_mut")
    ex = mutant.parse_exoneration(EXONERATED, tmp_path / "g_mut")
    assert ex.covers(["tests/background/test_thing.py", "tests/background/test_other.py"]) is True


def test_mutation_h_dropping_the_existence_check_kills_a_named_test(tmp_path):
    mutant = _load_mutant(
        tmp_path,
        "    missing = [a for a in artefacts if not (root / a.partition('::')[0]).is_file()]",
        "    missing = []",
        "finding_severity_mutant_exoneration_no_existence",
    )
    with pytest.raises(AssertionError):
        _assert_a_missing_path_does_not_exonerate(mutant, tmp_path / "h_mut")


def test_mutation_i_accepting_a_module_path_kills_a_named_test(tmp_path):
    mutant = _load_mutant(
        tmp_path,
        "    non_tests = [a for a in artefacts if not _is_test_file(a)]",
        "    non_tests = []",
        "finding_severity_mutant_exoneration_any_path",
    )
    with pytest.raises(AssertionError):
        _assert_a_non_test_artefact_does_not_exonerate(mutant, tmp_path / "i_mut")
