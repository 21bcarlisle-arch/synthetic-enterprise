"""R15 both-ways mutation tests for the cohort-coverage PUBLISH GATE
(``_cohort_coverage_gate_permits_publish`` in background/process_run_complete.py).

Director condition #3 of the generator population activation
(POPULATION_ACTIVATION_AND_RUN_LEDGER 2026-07-25 §1.3; POOL_VS_BOOK_LAMBDA_STANDS
2026-07-27): once the R13 draw is ACTIVE (``SE_DRAW_POPULATION=1``) no derived
figure may reach a surface until the realised-cohort coverage report is emitted
and passes the redundancy floor. Thin cells are reported, never smoothed.

These prove the control CAN FAIL on its own named defect (R15):
  * INERT WHEN OFF: flag unset -> permits publish WITHOUT drawing (mutation:
    a gate that always drew would break the byte-identical static-book path).
  * BLOCKS WHEN ON + THIN: flag on + gate_ok False -> blocks (mutation: a gate
    that always returned True — i.e. no gate — would let a thin draw publish).
  * PERMITS WHEN ON + FULL: flag on + gate_ok True -> permits.
  * FAIL-CLOSED: flag on + report build raises -> blocks (R15 fail-silent: an
    unavailable check is a FAILED check, never a pass-through).
"""
import pytest

import background.process_run_complete as prc


@pytest.fixture(autouse=True)
def _quiet_log(monkeypatch):
    # keep the gate's log() calls off disk during the test
    monkeypatch.setattr(prc, "log", lambda *a, **k: None)


def _patch_artifact(monkeypatch, *, gate_ok=None, raises=False, thin_cells=None):
    """Patch the coverage-report builder the gate imports locally."""
    calls = {"build": 0, "write": 0}

    def fake_build():
        calls["build"] += 1
        if raises:
            raise RuntimeError("coverage machinery unavailable")
        return {"gate_ok": gate_ok, "coverage": {"thin_cells": thin_cells or []}}

    def fake_write(artifact, *a, **k):
        calls["write"] += 1
        return None

    monkeypatch.setattr("tools.generate_cohort_coverage.build_artifact", fake_build)
    monkeypatch.setattr("tools.generate_cohort_coverage.write_artifact", fake_write)
    return calls


def test_inert_when_flag_off(monkeypatch):
    """Flag off -> permits publish and NEVER draws (byte-identical static path)."""
    monkeypatch.delenv("SE_DRAW_POPULATION", raising=False)

    def _boom():
        raise AssertionError("build_artifact must NOT be called when flag is off")

    monkeypatch.setattr("tools.generate_cohort_coverage.build_artifact", _boom)
    assert prc._cohort_coverage_gate_permits_publish() is True


def test_inert_when_flag_not_exactly_one(monkeypatch):
    """Only the exact "1" activates — any other value stays inert."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "0")
    calls = _patch_artifact(monkeypatch, gate_ok=False)  # would block IF it ran
    assert prc._cohort_coverage_gate_permits_publish() is True
    assert calls["build"] == 0


def test_permits_when_on_and_coverage_passes(monkeypatch):
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    calls = _patch_artifact(monkeypatch, gate_ok=True)
    assert prc._cohort_coverage_gate_permits_publish() is True
    # report must be EMITTED before any derived figure (write happened)
    assert calls["build"] == 1 and calls["write"] == 1


def test_blocks_when_on_and_coverage_thin(monkeypatch):
    """The core mutation: a thin realised draw MUST NOT publish."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    _patch_artifact(monkeypatch, gate_ok=False,
                    thin_cells=[{"axis": "heating_fuel", "category": "lpg_bottled", "count": 1}])
    assert prc._cohort_coverage_gate_permits_publish() is False


def test_fail_closed_when_report_build_raises(monkeypatch):
    """R15 fail-silent: an unavailable coverage build is a FAILED gate -> block."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    _patch_artifact(monkeypatch, raises=True)
    assert prc._cohort_coverage_gate_permits_publish() is False
