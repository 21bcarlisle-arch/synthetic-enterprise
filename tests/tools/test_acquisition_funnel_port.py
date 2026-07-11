"""WALLED_INTERFACES second reference-flow conversion (W4_1_typed_adapters,
step 3 "generalize the pattern").

Proves tools/acquisition_funnel_port.py is a transport-shape change to
already-correct data: the typed AcquisitionFunnelMessage / FunnelStageMessage
carry the existing `acquisition_funnel_log` dict (as simulation/run_phase2b.py
serialises it from a real run_acquisition_funnel result) losslessly, expose a
versioned schema, and respect the epistemic wall (observable bureau signal vs
SIM-internal ground truth). Mirrors the port-conformance style of
tests/tools/test_meter_read_port.py and tests/tools/test_credit_bureau_adapter.py.
"""
from tools.acquisition_funnel_port import (
    SCHEMA_VERSION,
    AcquisitionFunnelMessage,
    AcquisitionFunnelPort,
    FunnelStageMessage,
)
from tools.credit_bureau_port import CreditCheckResult
from simulation.acquisition_funnel import run_acquisition_funnel
from datetime import date


class _StubBureau:
    """Deterministic credit bureau exposing the CreditBureauPort shape, including
    the ground-truth field, so a real credit_check-reached result is produced."""

    def __init__(self, passed: bool, band: str, true_creditworthy: bool):
        self._r = CreditCheckResult(passed=passed, score_band=band, true_creditworthy=true_creditworthy)

    def check_credit(self, applicant_id: str, segment: str, seed: str) -> CreditCheckResult:
        return self._r


def _serialise_result(billing_account: str, result) -> dict:
    """Reproduce EXACTLY the acquisition_funnel_log dict shape that
    simulation/run_phase2b.py emits from a run_acquisition_funnel result (the
    real crossing projection). Kept in lockstep with run_phase2b.py so the
    lossless-identity test exercises the true seam shape, not a guessed one."""
    return {
        "billing_account": billing_account,
        "segment": result.segment,
        "term_start": result.term_start,
        "won": result.won,
        "stage_reached": result.stage_reached,
        "total_cost_gbp": result.total_cost_gbp,
        "credit_bureau_score_band": result.credit_bureau_score_band,
        "credit_bureau_passed": result.credit_bureau_passed,
        "credit_bureau_true_creditworthy": result.credit_bureau_true_creditworthy,
        "stages": [
            {"stage": s.stage, "passed": s.passed, "stage_date": s.stage_date}
            for s in result.stages
        ],
    }


def _sample_log() -> list[dict]:
    """A real acquisition_funnel_log from the real generator, spanning a
    credit-check-reached attempt (bureau fields populated) and an early-exit
    attempt (bureau fields None)."""
    ts = date(2023, 1, 1)
    bureau = _StubBureau(passed=True, band="prime", true_creditworthy=False)  # a false-accept
    entries = []
    for i in range(40):
        result = run_acquisition_funnel(
            "resi", f"seed_{i}", ts, bureau, total_amount_gbp=150.0
        )
        entries.append(_serialise_result(f"BA{i}", result))
    # Guarantee both a credit-check-reached and an early-exit attempt appear.
    assert any(e["credit_bureau_passed"] is not None for e in entries), "no credit_check reached"
    assert any(e["credit_bureau_passed"] is None for e in entries), "no early-exit attempt"
    return entries


def test_round_trip_is_lossless_identity_on_existing_dict():
    log = _sample_log()
    assert log, "generator produced no attempts -- fixture is not exercising anything"
    round_tripped = [AcquisitionFunnelMessage.from_log_entry(e).to_log_entry() for e in log]
    # Default to_log_entry() must be byte-for-byte the pre-conversion entry so
    # every current downstream consumer of acquisition_funnel_log is unaffected.
    assert round_tripped == log


def test_schema_version_present_and_defaulted():
    log = _sample_log()
    msg = AcquisitionFunnelMessage.from_log_entry(log[0])
    # Historical entries have no schema_version -- must default, not raise.
    assert "schema_version" not in log[0]
    assert msg.schema_version == SCHEMA_VERSION
    # Opt-in serialisation surfaces it on the versioned wire.
    assert msg.to_log_entry(include_schema_version=True)["schema_version"] == SCHEMA_VERSION
    assert "schema_version" not in msg.to_log_entry()


def test_from_log_entry_carries_every_field():
    entry = {
        "billing_account": "BA7",
        "segment": "SME",
        "term_start": "2023-03-01",
        "won": True,
        "stage_reached": "cooling_off",
        "total_cost_gbp": 400.0,
        "credit_bureau_score_band": "near_prime",
        "credit_bureau_passed": True,
        "credit_bureau_true_creditworthy": True,
        "stages": [
            {"stage": "quote", "passed": True, "stage_date": "2023-03-01"},
            {"stage": "application", "passed": True, "stage_date": "2023-03-05"},
        ],
    }
    msg = AcquisitionFunnelMessage.from_log_entry(entry)
    assert msg.billing_account == "BA7"
    assert msg.segment == "SME"
    assert msg.term_start == "2023-03-01"
    assert msg.won is True
    assert msg.stage_reached == "cooling_off"
    assert msg.total_cost_gbp == 400.0
    assert msg.credit_bureau_score_band == "near_prime"
    assert msg.credit_bureau_passed is True
    assert msg.credit_bureau_true_creditworthy is True
    assert msg.stages == (
        FunnelStageMessage(stage="quote", passed=True, stage_date="2023-03-01"),
        FunnelStageMessage(stage="application", passed=True, stage_date="2023-03-05"),
    )


def test_stage_message_round_trip_drops_no_seam_field():
    stage_dict = {"stage": "onboarding", "passed": False, "stage_date": "2023-03-10"}
    assert FunnelStageMessage.from_log_entry(stage_dict).to_log_entry() == stage_dict


def test_bureau_divergence_is_evidence_accessor_never_none_when_ground_truth_present():
    # Epistemic wall: the observable decision is `credit_bureau_passed`; the
    # divergence accessor reads ground truth for the evidence surface only.
    msg = AcquisitionFunnelMessage.from_log_entry({
        "billing_account": "BA1", "segment": "resi", "term_start": "2023-01-01",
        "won": True, "stage_reached": "cooling_off", "total_cost_gbp": 150.0,
        "credit_bureau_score_band": "prime", "credit_bureau_passed": True,
        "credit_bureau_true_creditworthy": False,  # a false-accept
        "stages": [],
    })
    assert msg.bureau_divergence is True  # passed but not truly creditworthy
    assert msg.credit_bureau_passed is True  # the observable decision is unchanged


def test_bureau_divergence_none_when_credit_check_never_reached():
    msg = AcquisitionFunnelMessage.from_log_entry({
        "billing_account": "BA2", "segment": "resi", "term_start": "2023-01-01",
        "won": False, "stage_reached": "application", "total_cost_gbp": 112.5,
        "credit_bureau_score_band": None, "credit_bureau_passed": None,
        "credit_bureau_true_creditworthy": None, "stages": [],
    })
    assert msg.bureau_divergence is None


def test_port_is_runtime_checkable_protocol():
    class _SimAcquisitionFunnelAdapter:
        def __init__(self, log):
            self._log = log

        def get_acquisition_funnel(self):
            return [AcquisitionFunnelMessage.from_log_entry(e) for e in self._log]

    adapter = _SimAcquisitionFunnelAdapter(_sample_log())
    assert isinstance(adapter, AcquisitionFunnelPort)
    attempts = adapter.get_acquisition_funnel()
    assert attempts and all(isinstance(a, AcquisitionFunnelMessage) for a in attempts)

    class _NotAPort:
        pass

    assert not isinstance(_NotAPort(), AcquisitionFunnelPort)
