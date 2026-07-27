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


def test_every_silent_entry_declares_a_rearm():
    """LAW A structural: every SILENT-biased live entry names its re-arm -- a numeric
    max_age_seconds (time-bound) and/or a non-empty rearm_trigger (independent counterpart)."""
    reg = _live_register()
    for e in reg["entries"]:
        if e.get("failure_direction") != "silent":
            continue
        mas = e.get("max_age_seconds")
        has_time_bound = isinstance(mas, (int, float)) and not isinstance(mas, bool) and mas > 0
        has_independent = bool((e.get("rearm_trigger") or "").strip())
        assert has_time_bound or has_independent, (
            f"{e.get('id')}: silent-biased but declares no re-arm (LAW A)"
        )


def test_silent_no_rearm_reds():
    """MUTATION (LAW A): a silent suppression with NEITHER a time-bound NOR an independent
    counterpart can silence a check forever -- the exact defect LAW A forbids -> must be flagged."""
    reg = copy.deepcopy(_live_register())
    reg["entries"].append({
        "id": "mutant_no_rearm",
        "mechanism": "a fold with no expiry and no independent counterpart",
        "failure_direction": "silent",
        "remediation": "law_b",          # remediated (so the older gate would pass it)...
        "status": "open",
        "what_still_pages": "a sibling lane, allegedly",   # ...and names a pager...
        # ...but declares NO max_age_seconds and NO rearm_trigger.
    })
    violations = sr.validate_suppression_register(reg)
    assert any("mutant_no_rearm" in v and "re-arm" in v for v in violations), (
        "gate must red on a silent suppression that declares no re-arm -- else LAW A is theatre"
    )


def test_law_a_token_without_time_bound_reds():
    """MUTATION: claiming remediation `law_a` while carrying no numeric max_age_seconds is
    claiming a remedy the register does not encode -> must be flagged."""
    reg = copy.deepcopy(_live_register())
    reg["entries"].append({
        "id": "mutant_law_a_no_bound",
        "mechanism": "claims a time-bound it does not encode",
        "failure_direction": "silent",
        "remediation": "law_a",
        "status": "landed",
        "what_still_pages": "a deadman cap, supposedly",
        "rearm_trigger": "some independent check",   # has an independent trigger...
        # ...but NO max_age_seconds, so the law_a time-bound claim is unbacked.
    })
    violations = sr.validate_suppression_register(reg)
    assert any("mutant_law_a_no_bound" in v and "law_a" in v for v in violations), (
        "a `law_a` remediation with no max_age_seconds must be flagged"
    )


def test_law_c_token_without_trigger_reds():
    """MUTATION: claiming remediation `law_c` while carrying no rearm_trigger is claiming an
    independent counterpart the register does not encode -> must be flagged."""
    reg = copy.deepcopy(_live_register())
    reg["entries"].append({
        "id": "mutant_law_c_no_trigger",
        "mechanism": "claims an independent counterpart it does not name",
        "failure_direction": "silent",
        "remediation": "law_c",
        "status": "landed",
        "what_still_pages": "an independent read, supposedly",
        "max_age_seconds": 3600,   # has a time-bound...
        # ...but NO rearm_trigger, so the law_c independent-counterpart claim is unbacked.
    })
    violations = sr.validate_suppression_register(reg)
    assert any("mutant_law_c_no_trigger" in v and "law_c" in v for v in violations), (
        "a `law_c` remediation with no rearm_trigger must be flagged"
    )


def test_compliant_does_not_exempt_silent_from_rearm():
    """LAW A "regardless of any self-declaration": a silent mechanism claiming status:compliant
    is STILL required to name its re-arm -- a compliant claim is not a re-arm."""
    reg = copy.deepcopy(_live_register())
    reg["entries"].append({
        "id": "mutant_compliant_no_rearm",
        "mechanism": "silent + self-declared compliant, but names no re-arm",
        "failure_direction": "silent",
        "remediation": "none",
        "status": "compliant",
        "what_still_pages": "trust me",
    })
    violations = sr.validate_suppression_register(reg)
    assert any("mutant_compliant_no_rearm" in v and "re-arm" in v for v in violations), (
        "status:compliant must NOT exempt a silent suppression from declaring its re-arm (LAW A)"
    )


def test_noisy_entry_needs_no_rearm():
    """A NOISY mechanism already fails toward a page -- it is exempt from the re-arm requirement
    (the gate must not false-positive on a legitimate noisy suppression)."""
    reg = copy.deepcopy(_live_register())
    reg["entries"].append({
        "id": "mutant_noisy_ok",
        "mechanism": "a throttle that re-attempts unless origin==HEAD -- fails toward noise",
        "failure_direction": "noisy",
        "remediation": "none",
        "status": "compliant",
        "what_still_pages": "it releases and re-attempts; never a silent success claim",
    })
    violations = sr.validate_suppression_register(reg)
    assert not any("mutant_noisy_ok" in v for v in violations), (
        f"a noisy suppression needs no re-arm; gate false-positived: {violations}"
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
