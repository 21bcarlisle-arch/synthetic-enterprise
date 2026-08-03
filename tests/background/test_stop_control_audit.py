"""R15 proof for `background/stop_control_audit.py` — the falsifier for STOP_CONTROL_GAP.md.

A control that cannot fail is worse than none. These tests mutate each claim class the audit
makes and assert it FIRES, then assert it PASSES on the real repo — both directions, per R15.

The three killer patterns, each addressed explicitly:
  TAUTOLOGY   — every check resolves against a source the registry does not control; the
                mutations below alter the ORACLE (a real file's contents, the manifest's
                declared state) as well as the claim, so a check that merely compared the
                registry to itself would not fire.
  FAIL-OPEN   — an empty registry, and a registry with no live control, are VIOLATIONS.
  FAIL-SILENT — a missing doc or manifest RAISES; it never returns a passing result.
"""
from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest
import yaml

from background import stop_control_audit as sca

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent


def _replace(control_id: int, **changes) -> tuple[sca.StopControl, ...]:
    """The real registry with one control mutated."""
    return tuple(
        dataclasses.replace(c, **changes) if c.id == control_id else c
        for c in sca.REGISTRY
    )


def _violations(result: sca.AuditResult) -> str:
    return "\n".join(result.violations)


# ─────────────────────────────────────────────────────────────────────────────
# The pass direction — the audit is green on the real repo, or it is worthless noise.
# ─────────────────────────────────────────────────────────────────────────────

def test_real_repo_passes_the_audit():
    result = sca.audit()
    assert result.ok, f"stop-control audit failed on the real repo:\n{_violations(result)}"


def test_real_repo_still_has_the_named_residual():
    """The atom's whole point: the residual is MEASURED, not asserted. If someone builds a
    window-reachable mid-flight stop, this test fails and the doc must be rewritten."""
    result = sca.audit()
    assert result.derived_verdict == "PARTIAL"
    assert len(result.residual) == 2
    assert any("window" in gap for gap in result.residual)
    assert any("in flight" in gap for gap in result.residual)


# ─────────────────────────────────────────────────────────────────────────────
# DEAD_TARGET — the defect this audit actually found in the 2026-07-28 inventory.
# ─────────────────────────────────────────────────────────────────────────────

def test_control_over_a_retired_process_is_a_dead_target():
    """Control #6 as the DISCOVER doc originally described it — a live director-only halt
    flag over the page-comment daemon. The manifest declares that daemon `retired`, so the
    claim is false. Restoring the original classification must make the audit fail."""
    mutated = _replace(
        6,
        classification="stop_control",
        cited_tests=("tests/background/test_stop_control_audit.py::test_real_repo_passes_the_audit",),
    )
    result = sca.audit(controls=mutated)
    assert not result.ok
    assert "DEAD_TARGET" in _violations(result)
    assert "director-comments" in _violations(result)


def test_dead_target_reads_the_manifest_not_the_registry(tmp_path):
    """Independence: flip the manifest's declared state and the SAME registry changes verdict.
    A tautological check (registry vs registry) could not do this."""
    manifest = yaml.safe_load(sca.PROCESS_MANIFEST_PATH.read_text(encoding="utf-8"))
    for proc in manifest["processes"]:
        if proc["session"] == "director-comments":
            proc["state"] = "enabled"
    revived = tmp_path / "process_manifest.yaml"
    revived.write_text(yaml.safe_dump(manifest), encoding="utf-8")

    mutated = _replace(
        6,
        classification="stop_control",
        cited_tests=("tests/background/test_stop_control_audit.py::test_real_repo_passes_the_audit",),
    )
    # Against the REAL manifest (retired) the same registry is a DEAD_TARGET...
    assert "DEAD_TARGET" in _violations(sca.audit(controls=mutated))
    # ...and against a manifest that declares it enabled, it is not.
    assert "DEAD_TARGET" not in _violations(sca.audit(controls=mutated, manifest_path=revived))


def test_process_absent_from_the_manifest_is_flagged():
    result = sca.audit(controls=_replace(2, halts_processes=("sim-runner", "no-such-daemon")))
    assert not result.ok
    assert "UNKNOWN_PROCESS" in _violations(result)


# ─────────────────────────────────────────────────────────────────────────────
# The claim-vs-source checks — each mutated so the ORACLE really differs.
# ─────────────────────────────────────────────────────────────────────────────

def test_missing_module_is_flagged():
    result = sca.audit(controls=_replace(1, module="background/deleted_governor.py"))
    assert not result.ok
    assert "MODULE_MISSING" in _violations(result)


def test_renamed_symbol_is_flagged():
    """A stop control whose implementing function was renamed out from under the doc."""
    result = sca.audit(controls=_replace(1, symbols=("kill_switch_enabled_RENAMED",)))
    assert not result.ok
    assert "SYMBOL_MISSING" in _violations(result)


def test_symbol_check_reads_real_source(tmp_path):
    """Independence proof for the symbol check: a project root whose governor no longer
    defines the symbol fails, with the registry untouched."""
    fake_root = tmp_path / "root"
    (fake_root / "background").mkdir(parents=True)
    (fake_root / "background" / "executor_governor.py").write_text(
        "# the kill switch was deleted\n", encoding="utf-8"
    )
    result = sca.audit(controls=(sca.REGISTRY[0],), project_dir=fake_root,
                       doc_path=sca.GAP_DOC_PATH)
    assert "SYMBOL_MISSING" in _violations(result)


def test_flag_no_longer_referenced_by_its_reader_is_flagged():
    """The flag file is only a stop control because something READS it. Point the claim at a
    module that does not, and the audit must fire."""
    result = sca.audit(controls=_replace(1, flag_readers=("background/deadmans_switch.py",)))
    assert not result.ok
    assert "FLAG_UNREFERENCED" in _violations(result)


def test_flag_with_no_declared_reader_is_flagged():
    result = sca.audit(controls=_replace(1, flag_readers=()))
    assert not result.ok
    assert "UNREAD_FLAG" in _violations(result)


def test_missing_reader_module_is_flagged():
    result = sca.audit(controls=_replace(1, flag_readers=("background/gone.py",)))
    assert not result.ok
    assert "READER_MISSING" in _violations(result)


def test_renamed_cited_test_is_flagged():
    """'Release tested?' is the inventory's strongest column. If the cited test is renamed or
    deleted, the column becomes a claim about nothing."""
    result = sca.audit(controls=_replace(
        2,
        cited_tests=("tests/background/test_sim_runner.py::test_check_hold_that_never_existed",),
    ))
    assert not result.ok
    assert "TEST_MISSING" in _violations(result)


def test_missing_test_file_is_flagged():
    result = sca.audit(controls=_replace(
        2, cited_tests=("tests/background/test_deleted.py::test_x",)))
    assert not result.ok
    assert "TEST_FILE_MISSING" in _violations(result)


def test_live_control_with_no_cited_test_is_flagged():
    result = sca.audit(controls=_replace(1, cited_tests=()))
    assert not result.ok
    assert "UNTESTED_CLAIM" in _violations(result)


def test_malformed_test_citation_is_flagged():
    result = sca.audit(controls=_replace(1, cited_tests=("tests/background/test_worker_tick.py",)))
    assert not result.ok
    assert "malformed test citation" in _violations(result)


def test_unknown_classification_and_reach_are_flagged():
    result = sca.audit(controls=_replace(3, classification="sort_of", reach="telepathy"))
    assert not result.ok
    assert "unknown classification" in _violations(result)
    assert "unknown reach" in _violations(result)


def test_duplicate_registry_id_is_flagged():
    result = sca.audit(controls=sca.REGISTRY + (dataclasses.replace(sca.REGISTRY[0]),))
    assert not result.ok
    assert "DUPLICATE id" in _violations(result)


# ─────────────────────────────────────────────────────────────────────────────
# FAIL-OPEN killers — vacuity.
# ─────────────────────────────────────────────────────────────────────────────

def test_empty_registry_is_vacuous_not_a_pass():
    result = sca.audit(controls=())
    assert not result.ok
    assert "VACUOUS" in _violations(result)


def test_registry_with_no_live_control_is_vacuous_not_a_pass():
    """Reclassifying every row to `not_a_stop_control` would silence every per-control check.
    The audit must call that what it is: an inventory claiming no stopping power at all."""
    all_inert = tuple(
        dataclasses.replace(c, classification="not_a_stop_control") for c in sca.REGISTRY
    )
    result = sca.audit(controls=all_inert)
    assert not result.ok
    assert "VACUOUS" in _violations(result)


# ─────────────────────────────────────────────────────────────────────────────
# Doc/registry drift + the headline verdict.
# ─────────────────────────────────────────────────────────────────────────────

def test_doc_row_the_audit_does_not_check_is_flagged():
    """Someone adds a 9th control to the doc's table and never registers it. The doc would
    read as a complete inventory; the audit says otherwise."""
    result = sca.audit(controls=tuple(c for c in sca.REGISTRY if c.id != 8))
    assert not result.ok
    assert "DOC_ROW_UNCHECKED" in _violations(result)


def test_registry_row_absent_from_the_doc_is_flagged():
    extra = dataclasses.replace(sca.REGISTRY[7], id=99)
    result = sca.audit(controls=sca.REGISTRY + (extra,))
    assert not result.ok
    assert "REGISTRY_ROW_UNDOCUMENTED" in _violations(result)


def test_verdict_goes_stale_when_a_window_reachable_midflight_stop_appears():
    """The release side (R11 / no orphan transition): if the residual is ever CLOSED, the
    doc's 'PARTIAL' headline becomes a lie and this audit is what catches it."""
    built = sca.REGISTRY + (
        sca.StopControl(
            id=9,
            name="hypothetical director-window stop",
            classification="stop_control",
            reach="window",
            mid_flight=True,
            module="background/executor_governor.py",
            symbols=("kill_switch_enabled",),
            cited_tests=(
                "tests/background/test_executor_governor.py::test_governor_never_writes_the_enable_flag",
            ),
        ),
    )
    result = sca.audit(controls=built)
    assert not result.ok
    assert "VERDICT_STALE" in _violations(result)
    assert result.derived_verdict == "MET"


def test_verdict_derivation_is_from_reach_and_midflight_not_from_prose():
    assert sca._derive_verdict(())[0] == "NONE"
    live_console = (dataclasses.replace(sca.REGISTRY[0]),)
    assert sca._derive_verdict(live_console)[0] == "PARTIAL"


# ─────────────────────────────────────────────────────────────────────────────
# FAIL-SILENT killers — an unavailable check is a FAILED check.
# ─────────────────────────────────────────────────────────────────────────────

def test_missing_doc_raises_rather_than_passing(tmp_path):
    with pytest.raises(sca.StopControlAuditError, match="required file missing"):
        sca.audit(doc_path=tmp_path / "no_such_doc.md")


def test_missing_manifest_raises_rather_than_passing(tmp_path):
    with pytest.raises(sca.StopControlAuditError, match="required file missing"):
        sca.audit(manifest_path=tmp_path / "no_such_manifest.yaml")


def test_malformed_manifest_raises_rather_than_passing(tmp_path):
    bad = tmp_path / "process_manifest.yaml"
    bad.write_text("processes: not-a-list\n", encoding="utf-8")
    with pytest.raises(sca.StopControlAuditError, match="malformed"):
        sca.audit(manifest_path=bad)


def test_manifest_declaring_no_processes_raises(tmp_path):
    empty = tmp_path / "process_manifest.yaml"
    empty.write_text("processes: []\n", encoding="utf-8")
    with pytest.raises(sca.StopControlAuditError, match="declares no processes"):
        sca.audit(manifest_path=empty)


def test_doc_without_a_coverage_verdict_raises(tmp_path):
    """The doc's headline conclusion is the thing most likely to go stale. A doc that states
    no checkable verdict must fail the audit, not skip that check."""
    stripped = sca.GAP_DOC_PATH.read_text(encoding="utf-8").replace("Coverage verdict", "Coverage view")
    doc = tmp_path / "STOP_CONTROL_GAP.md"
    doc.write_text(stripped, encoding="utf-8")
    with pytest.raises(sca.StopControlAuditError, match="no 'Coverage verdict"):
        sca.audit(doc_path=doc)


def test_main_returns_nonzero_when_the_audit_is_unavailable(monkeypatch, capsys):
    def boom(*_a, **_k):
        raise sca.StopControlAuditError("manifest gone")

    monkeypatch.setattr(sca, "audit", boom)
    assert sca.main([]) == 2
    assert "UNAVAILABLE (= FAILED)" in capsys.readouterr().err


def test_main_passes_on_the_real_repo(capsys):
    assert sca.main([]) == 0
    assert "PASS" in capsys.readouterr().out
