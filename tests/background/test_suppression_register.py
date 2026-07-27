"""R15 both-ways proof of the R10 SUPPRESSION-SWEEP standing gate
(DIRECTOR_RULING_FAILURE_BIAS_LAWS 2026-07-27, standing consequence).

The gate: every registered suppression must declare `what_still_pages` -- the independent
check that fires if the underlying condition is real. This is the mechanised half of the
director's standing consequence ("a suppression proposed without that answer is rejected").

Both ways (R15):
  * test_live_register_passes           -- the real committed register is clean (the control
                                           does not false-positive on legitimate input).
  * test_empty_what_still_pages_reds     -- MUTATION: inject a suppression with an empty
                                           `what_still_pages` and prove the gate REPORTS it.
                                           If this passed silently, the gate is theatre.
  * test_silent_unremediated_reds        -- MUTATION: a silent-biased suppression claiming
                                           remediation 'none' and status != compliant is the
                                           exact defect the law forbids -> must be flagged.
  * test_missing_register_raises         -- an UNAVAILABLE gate is a FAILED gate (R15
                                           FAIL-SILENT killer): a missing register raises,
                                           never silently passes.
  * test_malformed_register_raises       -- a register with no 'entries' list raises.
"""
from __future__ import annotations

import copy
import json

import pytest

import background.suppression_register as sr


def _live_register() -> dict:
    return sr.load_register()


def test_live_register_passes():
    """The committed register is clean -- no false positive on legitimate input."""
    violations = sr.validate_suppression_register(_live_register())
    assert violations == [], f"live register should be clean, got: {violations}"
    assert sr.register_is_clean() is True


def test_every_entry_has_the_required_fields():
    """Structural: every entry carries id + a non-empty what_still_pages."""
    reg = _live_register()
    assert reg["entries"], "register must enumerate at least one suppression"
    for e in reg["entries"]:
        assert e.get("id"), f"entry missing id: {e}"
        assert (e.get("what_still_pages") or "").strip(), f"{e.get('id')}: empty what_still_pages"


def test_empty_what_still_pages_reds():
    """MUTATION: a suppression with an empty what_still_pages must be flagged."""
    reg = copy.deepcopy(_live_register())
    reg["entries"].append({
        "id": "mutant_no_pager",
        "mechanism": "a fold that silences a check and names no pager",
        "failure_direction": "silent",
        "remediation": "law_a",
        "status": "open",
        "what_still_pages": "",
    })
    violations = sr.validate_suppression_register(reg)
    assert any("mutant_no_pager" in v for v in violations), (
        "gate must red on an empty what_still_pages -- otherwise it is theatre"
    )


def test_silent_unremediated_reds():
    """MUTATION: silent-biased + remediation 'none' + not compliant == the forbidden defect."""
    reg = copy.deepcopy(_live_register())
    reg["entries"].append({
        "id": "mutant_silent_unremediated",
        "mechanism": "silences a page with no time-bound and no independent counterpart",
        "failure_direction": "silent",
        "remediation": "none",
        "status": "open",
        "what_still_pages": "nothing, honestly",
    })
    violations = sr.validate_suppression_register(reg)
    assert any("mutant_silent_unremediated" in v for v in violations), (
        "a silence-failing suppression with no remediation must be flagged"
    )


def test_missing_register_raises(tmp_path):
    """An UNAVAILABLE gate is a FAILED gate -- must raise, never silently pass."""
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        sr.load_register(missing)
    with pytest.raises(FileNotFoundError):
        sr.register_is_clean(path=missing)


def test_malformed_register_raises(tmp_path):
    """A register with no 'entries' list is malformed -> raise (R15 fail-silent killer)."""
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"nonsense": True}), encoding="utf-8")
    with pytest.raises(ValueError):
        sr.load_register(bad)
