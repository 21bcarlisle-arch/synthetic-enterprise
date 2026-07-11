"""WALLED_INTERFACES reference-flow conversion (W4_1_typed_adapters, step 2).

Proves tools/meter_read_port.py is a transport-shape change to already-correct
data: the typed MeterReadMessage carries the existing generate_meter_read_log
dict losslessly, exposes a versioned schema, and respects the epistemic wall
(observable billed value vs SIM-internal ground truth). Mirrors the port-
conformance style of tests/tools/test_credit_bureau_adapter.py and
tests/tools/test_phase_pv_market_adapter.py.
"""
from simulation.meter_reads import generate_meter_read_log
from tools.meter_read_port import (
    SCHEMA_VERSION,
    MeterReadMessage,
    MeterReadPort,
)


def _sample_log() -> list[dict]:
    """A real meter-read log spanning both statuses, from the real generator."""
    bills = [
        {"customer_id": "C8", "period_end": f"2020-{m:02d}-28", "total_consumption_kwh": 300.0 + m}
        for m in range(1, 13)
    ]
    # Include a smart and a traditional customer so both status paths appear.
    bills += [
        {"customer_id": "C9", "period_end": f"2020-{m:02d}-28", "total_consumption_kwh": 500.0 + m}
        for m in range(1, 13)
    ]
    return generate_meter_read_log(bills, {"C8": "traditional", "C9": "smart"})


def test_round_trip_is_lossless_identity_on_existing_dict():
    log = _sample_log()
    assert log, "generator produced no reads -- fixture is not exercising anything"
    round_tripped = [MeterReadMessage.from_log_entry(e).to_log_entry() for e in log]
    # Default to_log_entry() must be byte-for-byte the pre-conversion entry so
    # every current downstream consumer of meter_read_log is unaffected.
    assert round_tripped == log


def test_schema_version_present_and_defaulted():
    log = _sample_log()
    msg = MeterReadMessage.from_log_entry(log[0])
    # Historical entries have no schema_version -- must default, not raise.
    assert "schema_version" not in log[0]
    assert msg.schema_version == SCHEMA_VERSION
    # Opt-in serialisation surfaces it on the versioned wire.
    assert msg.to_log_entry(include_schema_version=True)["schema_version"] == SCHEMA_VERSION
    assert "schema_version" not in msg.to_log_entry()


def test_from_log_entry_carries_every_field():
    entry = {
        "customer_id": "C8",
        "period_end": "2020-06-28",
        "meter_type": "traditional",
        "delay_days": 9,
        "status": "estimated",
        "estimated_consumption_kwh": 305.0,
        "true_consumption_kwh": 320.0,
        "consecutive_estimated_count": 2,
        "forced_catch_up": False,
    }
    msg = MeterReadMessage.from_log_entry(entry)
    assert msg.customer_id == "C8"
    assert msg.period_end == "2020-06-28"
    assert msg.meter_type == "traditional"
    assert msg.delay_days == 9
    assert msg.status == "estimated"
    assert msg.estimated_consumption_kwh == 305.0
    assert msg.true_consumption_kwh == 320.0
    assert msg.consecutive_estimated_count == 2
    assert msg.forced_catch_up is False


def test_billed_value_is_estimate_when_estimated_never_ground_truth():
    # Epistemic wall: for an estimated period the observable billed value is the
    # supplier's own estimate, NOT the SIM's true consumption.
    msg = MeterReadMessage.from_log_entry({
        "customer_id": "C8", "period_end": "2020-06-28", "meter_type": "traditional",
        "delay_days": 9, "status": "estimated",
        "estimated_consumption_kwh": 305.0, "true_consumption_kwh": 320.0,
        "consecutive_estimated_count": 1, "forced_catch_up": False,
    })
    assert msg.billed_consumption_kwh == 305.0
    assert msg.billed_consumption_kwh != msg.true_consumption_kwh


def test_billed_value_is_actual_read_when_actual():
    msg = MeterReadMessage.from_log_entry({
        "customer_id": "C9", "period_end": "2020-06-28", "meter_type": "smart",
        "delay_days": 1, "status": "actual",
        "estimated_consumption_kwh": None, "true_consumption_kwh": 500.0,
        "consecutive_estimated_count": 0, "forced_catch_up": False,
    })
    # An actual read IS the value a real supplier legitimately receives.
    assert msg.billed_consumption_kwh == 500.0


def test_port_is_runtime_checkable_protocol():
    class _SimMeterReadAdapter:
        def __init__(self, log):
            self._log = log

        def get_meter_reads(self):
            return [MeterReadMessage.from_log_entry(e) for e in self._log]

    adapter = _SimMeterReadAdapter(_sample_log())
    assert isinstance(adapter, MeterReadPort)
    reads = adapter.get_meter_reads()
    assert reads and all(isinstance(r, MeterReadMessage) for r in reads)

    class _NotAPort:
        pass

    assert not isinstance(_NotAPort(), MeterReadPort)
