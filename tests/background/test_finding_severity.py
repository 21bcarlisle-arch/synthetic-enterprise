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


def test_a_repaired_document_stands_the_namer_down_only_from_its_header_block(tmp_path):
    header_says_fixed = (
        "# T\n\n**Severity:** LATENT · **Lane:** H_harness · **Status:** FIXED\n\n"
        "## The claim\nThe gate that certifies this lane is lying about its own subject.\n"
    )
    (tmp_path / "fixed.md").write_text(header_says_fixed, encoding="utf-8")
    assert fs.by_construction_violations(tmp_path) == []

    body_says_fixed = _SAYS_AN_INSTRUMENT_IS_WRONG.format(value="LATENT") + (
        "\n## Retro\nA similar defect was FIXED last week.\n")
    (tmp_path / "body.md").write_text(body_says_fixed, encoding="utf-8")
    assert [r.path.name for r, _ in fs.by_construction_violations(tmp_path)] == ["body.md"]


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
