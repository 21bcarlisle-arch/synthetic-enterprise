"""Tests for company/compliance/internal_audit.py -- DOMAIN_SENSE_AND_COMPLIANCE.md
Phases 6 (bill sampling) and 7 (phase-close artefact sampling)."""
import random

from company.compliance.internal_audit import (
    build_audit_prompt,
    parse_audit_response,
    sample_bills_risk_based,
    run_internal_audit,
    build_artefact_audit_prompt,
    audit_artefact,
    run_phase_close_audit,
)


def _bill(cid, segment="resi", **overrides):
    bill = {
        "customer_id": cid, "period_start": "2024-01-01", "period_end": "2024-01-31",
        "segment": segment, "commodity": "electricity", "total_consumption_kwh": 300.0,
        "commodity_amount_gbp": 44.55, "non_commodity_amount_gbp": 16.65,
        "standing_charge_gbp": 9.30, "vat_gbp": 3.53, "total_amount_gbp": 74.03,
    }
    bill.update(overrides)
    return bill


def test_parse_audit_response_clean():
    result = parse_audit_response("VERDICT: clean\nNOTE: Looks fine for a resi account.")
    assert result["verdict"] == "clean"
    assert "fine" in result["note"]


def test_parse_audit_response_flagged():
    result = parse_audit_response("VERDICT: flagged\nNOTE: Consumption is SME-scale for a resi account.")
    assert result["verdict"] == "flagged"
    assert "SME-scale" in result["note"]


def test_parse_audit_response_case_insensitive_verdict():
    result = parse_audit_response("VERDICT: FLAGGED\nNOTE: Something's off.")
    assert result["verdict"] == "flagged"


def test_parse_audit_response_empty_is_unavailable_not_clean():
    # F6 FAIL-SILENT FIX (CONTROLS_THAT_CANNOT_FAIL.md): an empty response means
    # the model was unreachable. That is NOT clean -- an unavailable check is a
    # FAILED check. It must never fabricate a per-bill finding either, so the
    # verdict is a distinct third state, "unavailable".
    result = parse_audit_response("")
    assert result["verdict"] == "unavailable"
    assert "unavailable" in result["note"].lower()


def test_parse_audit_response_malformed_is_unavailable_not_clean():
    # A response with no parseable VERDICT line is unusable output -- we cannot
    # assert clean from it, so it is unavailable (fail closed), not clean.
    result = parse_audit_response("some unrelated text with no VERDICT line")
    assert result["verdict"] == "unavailable"


def test_build_audit_prompt_includes_bill_fields():
    bill = _bill("C1")
    prompt = build_audit_prompt(bill)
    assert "resi" in prompt
    assert "300.0" in prompt
    assert "VERDICT: clean|flagged" in prompt


def test_sample_bills_risk_based_prefers_resi():
    bills = [_bill(f"C_IC{i}", segment="I&C") for i in range(20)] + [_bill(f"C{i}", segment="resi") for i in range(5)]
    rng = random.Random(42)
    sampled = sample_bills_risk_based(bills, 1000, rng)
    resi_count = sum(1 for b in sampled if b["segment"] == "resi")
    # resi is 5/25 of the population (20%) but weighted 3x -- should land
    # well above its raw population share in the sample.
    assert resi_count / len(sampled) > 0.30


def test_sample_bills_risk_based_empty_input():
    rng = random.Random(1)
    assert sample_bills_risk_based([], 5, rng) == []


def test_sample_bills_risk_based_zero_samples():
    rng = random.Random(1)
    assert sample_bills_risk_based([_bill("C1")], 0, rng) == []


def test_run_internal_audit_returns_only_flagged():
    bills = [_bill("C1"), _bill("C2"), _bill("C3")]

    def fake_qwen(prompt):
        return "VERDICT: clean\nNOTE: fine" if "C1" in prompt or True else ""

    # Deterministic fake: flag exactly the bill whose customer_id is embedded.
    def fake_qwen_flagging_c2(prompt):
        if "C2" in prompt:
            return "VERDICT: flagged\nNOTE: implausible"
        return "VERDICT: clean\nNOTE: fine"

    findings = run_internal_audit(bills, n_samples=3, seed=1, call_qwen_fn=fake_qwen_flagging_c2)
    assert all(f["customer_id"] == "C2" for f in findings)


def test_run_internal_audit_all_clean_returns_empty():
    bills = [_bill("C1"), _bill("C2")]
    findings = run_internal_audit(
        bills, n_samples=2, seed=1, call_qwen_fn=lambda p: "VERDICT: clean\nNOTE: ok"
    )
    assert findings == []


def test_run_internal_audit_model_unavailable_alarms_not_silent():
    # F6 FAIL-SILENT FIX: when the model is unreachable the audit did NOT run --
    # it must ALARM (a checker_unavailable finding), not return an empty (=clean)
    # list. It still fabricates no finding against any specific bill.
    bills = [_bill("C1"), _bill("C2")]
    findings = run_internal_audit(bills, n_samples=2, seed=1, call_qwen_fn=lambda p: "")
    assert len(findings) == 1
    assert findings[0]["kind"] == "checker_unavailable"
    assert findings[0]["customer_id"] is None
    assert "did NOT run" in findings[0]["note"]


def test_run_internal_audit_partial_unavailability_still_alarms():
    # Even one unreachable sample among otherwise-clean ones must alarm.
    bills = [_bill("C1"), _bill("C2")]

    def flaky_qwen(prompt):
        return "VERDICT: clean\nNOTE: fine" if "C1" in prompt else ""

    findings = run_internal_audit(bills, n_samples=2, seed=1, call_qwen_fn=flaky_qwen)
    assert any(f.get("kind") == "checker_unavailable" for f in findings)


def test_run_internal_audit_no_bills():
    assert run_internal_audit([], n_samples=5) == []


def test_run_internal_audit_finding_includes_customer_and_note():
    bills = [_bill("C6")]
    findings = run_internal_audit(
        bills, n_samples=1, seed=1,
        call_qwen_fn=lambda p: "VERDICT: flagged\nNOTE: SME-scale consumption on a resi record.",
    )
    assert len(findings) == 1
    assert findings[0]["customer_id"] == "C6"
    assert findings[0]["period_end"] == "2024-01-31"
    assert "SME-scale" in findings[0]["note"]


# --- Phase 7: Qwen skeptic phase-close pass (arbitrary rendered artefacts) ---

def test_build_artefact_audit_prompt_includes_name_and_content():
    prompt = build_artefact_audit_prompt("site/customers/index.html#C1", "Household bill total: GBP 100")
    assert "site/customers/index.html#C1" in prompt
    assert "Household bill total" in prompt


def test_build_artefact_audit_prompt_truncates_long_content():
    long_text = "x" * 5000
    prompt = build_artefact_audit_prompt("some_page", long_text)
    assert len(prompt) < 3000  # excerpt capped, not the full 5000 chars


def test_audit_artefact_clean():
    result = audit_artefact("page1", "all fine", call_qwen_fn=lambda p: "VERDICT: clean\nNOTE: nothing wrong")
    assert result["verdict"] == "clean"
    assert result["artefact_name"] == "page1"


def test_audit_artefact_flagged():
    result = audit_artefact("page1", "SME billed as household", call_qwen_fn=lambda p: "VERDICT: flagged\nNOTE: segment mismatch")
    assert result["verdict"] == "flagged"
    assert "segment mismatch" in result["note"]


def test_run_phase_close_audit_returns_only_flagged():
    artefacts = {"page_a": "content a", "page_b": "content b", "page_c": "content c"}

    def fake_qwen(prompt):
        if "content b" in prompt:
            return "VERDICT: flagged\nNOTE: something off"
        return "VERDICT: clean\nNOTE: fine"

    findings = run_phase_close_audit(artefacts, n_samples=3, seed=1, call_qwen_fn=fake_qwen)
    assert len(findings) == 1
    assert findings[0]["artefact_name"] == "page_b"


def test_run_phase_close_audit_samples_at_most_n_artefacts(monkeypatch):
    artefacts = {f"page_{i}": f"content {i}" for i in range(10)}
    calls = []

    def counting_qwen(prompt):
        calls.append(prompt)
        return "VERDICT: clean\nNOTE: fine"

    run_phase_close_audit(artefacts, n_samples=3, seed=1, call_qwen_fn=counting_qwen)
    assert len(calls) == 3


def test_run_phase_close_audit_empty_artefacts():
    assert run_phase_close_audit({}, n_samples=3) == []


def test_run_phase_close_audit_all_clean_returns_empty():
    artefacts = {"page_a": "content a", "page_b": "content b"}
    findings = run_phase_close_audit(
        artefacts, n_samples=2, seed=1, call_qwen_fn=lambda p: "VERDICT: clean\nNOTE: fine"
    )
    assert findings == []
