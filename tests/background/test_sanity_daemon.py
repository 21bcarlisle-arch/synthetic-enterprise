"""Tests for background/sanity_daemon.py -- DOMAIN_SENSE_AND_COMPLIANCE.md Phase 5
(detective/sampling control, distinct from supervisor.py's turn-granting)."""
import json

import pytest

from background import sanity_daemon


def _reset_state():
    sanity_daemon._last_finding_signature = None


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(sanity_daemon, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(sanity_daemon, "RUN_OUTPUT_PATH", tmp_path / "run_output_latest.json")
    _reset_state()
    yield
    _reset_state()


def _write_run_output(path, bills=None, meter_read_log=None):
    path.write_text(json.dumps({
        "bills": bills or [],
        "meter_read_log": meter_read_log or [],
    }))


def test_run_cycle_skips_when_no_run_output(monkeypatch):
    calls = []
    monkeypatch.setattr(sanity_daemon, "send_ntfy", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    assert calls == []
    assert "No run_output_latest.json" in sanity_daemon.LOG_FILE.read_text()


def test_run_cycle_handles_malformed_json(monkeypatch):
    sanity_daemon.RUN_OUTPUT_PATH.write_text("not valid json")
    calls = []
    monkeypatch.setattr(sanity_daemon, "send_ntfy", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    assert calls == []
    assert "Could not read/parse" in sanity_daemon.LOG_FILE.read_text()


def test_run_cycle_clean_population_no_ntfy(monkeypatch):
    bills = [
        {"customer_id": "C1", "period_end": f"2024-{m:02d}-28", "segment": "resi",
         "commodity": "electricity", "total_consumption_kwh": 200.0,
         "commodity_amount_gbp": 200.0 * 150.0 / 1000}
        for m in range(1, 13)
    ]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bills, meter_read_log=[{"status": "actual"}] * 90 + [{"status": "estimated"}] * 10)
    calls = []
    monkeypatch.setattr(sanity_daemon, "send_ntfy", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    assert calls == []
    assert "Clean" in sanity_daemon.LOG_FILE.read_text()


def test_run_cycle_sends_one_ntfy_for_new_findings(monkeypatch):
    bills = [{"customer_id": "C6", "period_end": "2024-01-28", "segment": "resi",
              "commodity": "electricity", "total_consumption_kwh": 50000.0,
              "commodity_amount_gbp": 50000.0 * 150.0 / 1000}]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bills)
    calls = []
    monkeypatch.setattr(sanity_daemon, "send_ntfy", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    assert len(calls) == 1
    assert "population-level finding" in calls[0]


def test_run_cycle_does_not_repeat_ntfy_for_unchanged_findings(monkeypatch):
    bills = [{"customer_id": "C6", "period_end": "2024-01-28", "segment": "resi",
              "commodity": "electricity", "total_consumption_kwh": 50000.0,
              "commodity_amount_gbp": 50000.0 * 150.0 / 1000}]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bills)
    calls = []
    monkeypatch.setattr(sanity_daemon, "send_ntfy", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    sanity_daemon.run_cycle()
    sanity_daemon.run_cycle()
    assert len(calls) == 1  # R5: never repeat an unchanged status


def test_run_cycle_sends_new_ntfy_when_findings_change(monkeypatch):
    bills = [{"customer_id": "C6", "period_end": "2024-01-28", "segment": "resi",
              "commodity": "electricity", "total_consumption_kwh": 50000.0,
              "commodity_amount_gbp": 50000.0 * 150.0 / 1000}]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bills)
    calls = []
    monkeypatch.setattr(sanity_daemon, "send_ntfy", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()

    bills_changed = bills + [{"customer_id": "C9", "period_end": "2024-02-28", "segment": "resi",
                               "commodity": "gas", "total_consumption_kwh": 90000.0,
                               "commodity_amount_gbp": 90000.0 * 40.0 / 1000}]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bills_changed)
    sanity_daemon.run_cycle()
    assert len(calls) == 2


def test_run_cycle_transition_from_findings_back_to_clean_is_silent(monkeypatch):
    bad_bills = [{"customer_id": "C6", "period_end": "2024-01-28", "segment": "resi",
                  "commodity": "electricity", "total_consumption_kwh": 50000.0,
                  "commodity_amount_gbp": 50000.0 * 150.0 / 1000}]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bad_bills)
    calls = []
    monkeypatch.setattr(sanity_daemon, "send_ntfy", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    assert len(calls) == 1

    clean_bills = [
        {"customer_id": "C1", "period_end": f"2024-{m:02d}-28", "segment": "resi",
         "commodity": "electricity", "total_consumption_kwh": 200.0,
         "commodity_amount_gbp": 200.0 * 150.0 / 1000}
        for m in range(1, 13)
    ]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=clean_bills)
    sanity_daemon.run_cycle()
    assert len(calls) == 1  # clean transition doesn't NTFY, only logs
