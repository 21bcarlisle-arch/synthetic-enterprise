"""Tests for background/sanity_daemon.py -- DOMAIN_SENSE_AND_COMPLIANCE.md Phase 5
(detective/sampling control, distinct from supervisor.py's turn-granting)."""
import json

import pytest

from background import sanity_daemon
from company.compliance import sanity_adjudication


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(sanity_daemon, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(sanity_daemon, "RUN_OUTPUT_PATH", tmp_path / "run_output_latest.json")
    # Isolated from the real, committed site/state/billing_ledger.json --
    # defaults to a nonexistent tmp_path file (payment-channel-mix check
    # simply skipped, matching the daemon's own graceful-degradation
    # design), never the real repo file.
    monkeypatch.setattr(sanity_daemon, "BILLING_LEDGER_PATH", tmp_path / "billing_ledger.json")
    # Isolated from the real, committed sanity_adjudication_ledger.json --
    # every test starts with a genuinely empty ledger (2026-07-11 redesign).
    monkeypatch.setattr(sanity_adjudication, "LEDGER_PATH", tmp_path / "sanity_adjudication_ledger.json")
    # Isolated from the real daily-digest date marker.
    monkeypatch.setattr(sanity_daemon, "LAST_DIGEST_DATE_FILE", tmp_path / ".last_digest_date")
    # Isolated from the real, committed coupled_gap_ledger.json -- a test that
    # exercises the daily digest's coupled-triad gap line controls the ledger
    # content itself (defaults to a nonexistent tmp file, so the digest line
    # reads fail-closed "ledger MISSING" unless a test writes it).
    monkeypatch.setattr(sanity_daemon, "COUPLED_GAP_LEDGER_PATH", tmp_path / "coupled_gap_ledger.json")
    # Phase 6's internal audit calls a real local Ollama model by default --
    # never let a test hit that network service; default to "nothing
    # flagged" unless a test explicitly overrides this.
    monkeypatch.setattr(sanity_daemon, "run_internal_audit", lambda bills, n_samples=2: [])
    yield


# A realistic, non-degenerate population read log: ~10% estimated, well
# inside population_sanity._ESTIMATED_READ_RATE_SANITY_BAND. This is the
# DEFAULT so that a test exercising the audit/digest/channel-mix streams is
# not spuriously tripped by the R15 empty-read guard (KL-4, 2026-07-13):
# check_estimated_read_rate([]) now CORRECTLY FIRES -- a total absence of
# reads is the most-broken state, never a clean one. A real book always
# produces reads (the live run carries 1,588), so the degenerate empty log
# is not the state these tests mean to exercise. Tests that specifically
# assert the empty-read guard pass meter_read_log=[] explicitly.
_CLEAN_READS = [{"status": "actual"}] * 90 + [{"status": "estimated"}] * 10


def _write_run_output(path, bills=None, meter_read_log=None):
    path.write_text(json.dumps({
        "bills": bills or [],
        "meter_read_log": _CLEAN_READS if meter_read_log is None else meter_read_log,
    }))


def test_run_cycle_skips_when_no_run_output(monkeypatch):
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    assert calls == []
    assert "No run_output_latest.json" in sanity_daemon.LOG_FILE.read_text()


def test_run_cycle_handles_malformed_json(monkeypatch):
    sanity_daemon.RUN_OUTPUT_PATH.write_text("not valid json")
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    assert calls == []
    assert "Could not read/parse" in sanity_daemon.LOG_FILE.read_text()


def test_run_cycle_clean_population_no_ntfy(monkeypatch):
    bills = [
        {"customer_id": "C1", "period_end": f"2024-{m:02d}-28", "segment": "resi",
         "commodity": "electricity", "total_consumption_kwh": 200.0,
         "commodity_amount_gbp": 200.0 * 150.0 / 1000, "days_in_period": 30.44}
        for m in range(1, 13)
    ]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bills, meter_read_log=[{"status": "actual"}] * 90 + [{"status": "estimated"}] * 10)
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    assert calls == []
    assert "Clean" in sanity_daemon.LOG_FILE.read_text()


def test_run_cycle_empty_meter_reads_fires_r15_guard(monkeypatch):
    """KL-4 / R15 (2026-07-13, CONTROLS_THAT_CANNOT_FAIL.md): a TOTAL absence
    of meter reads is the most-broken read-generation state, not a clean one.
    check_estimated_read_rate([]) must FIRE, and run_cycle must surface it as
    a NEW population-level NTFY -- an empty check can never be a passing check.
    This is the new correct contract; the old behaviour read clean (fail-silent)."""
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[], meter_read_log=[])
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    assert len(calls) == 1
    assert "No meter reads present at all" in calls[0]


def test_run_cycle_empty_meter_reads_guard_dedups_not_per_cycle_spam(monkeypatch):
    """The R15 empty-read guard must NOT re-NTFY every cycle -- it is a
    standing finding after its first sighting, deduped by the durable
    adjudication ledger exactly like every other finding (director's
    "an alarm that repeats unactionably kills the immune system"). Confirms
    the new correct control does not become a source of real-data spam."""
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[], meter_read_log=[])
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    sanity_daemon.run_cycle()
    sanity_daemon.run_cycle()
    assert len(calls) == 1  # fires once, then a standing known finding -- no repeat


def test_run_cycle_sends_one_ntfy_for_new_findings(monkeypatch):
    bills = [{"customer_id": "C6", "period_end": "2024-01-28", "segment": "resi",
              "commodity": "electricity", "total_consumption_kwh": 50000.0,
              "commodity_amount_gbp": 50000.0 * 150.0 / 1000, "days_in_period": 365}]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bills)
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    assert len(calls) == 1
    assert "population-level finding" in calls[0]


def test_run_cycle_does_not_repeat_ntfy_for_unchanged_findings(monkeypatch):
    bills = [{"customer_id": "C6", "period_end": "2024-01-28", "segment": "resi",
              "commodity": "electricity", "total_consumption_kwh": 50000.0,
              "commodity_amount_gbp": 50000.0 * 150.0 / 1000, "days_in_period": 365}]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bills)
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    sanity_daemon.run_cycle()
    sanity_daemon.run_cycle()
    assert len(calls) == 1  # R5: never repeat an unchanged status


def test_run_cycle_sends_new_ntfy_when_findings_change(monkeypatch):
    bills = [{"customer_id": "C6", "period_end": "2024-01-28", "segment": "resi",
              "commodity": "electricity", "total_consumption_kwh": 50000.0,
              "commodity_amount_gbp": 50000.0 * 150.0 / 1000, "days_in_period": 365}]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bills)
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()

    bills_changed = bills + [{"customer_id": "C9", "period_end": "2024-02-28", "segment": "resi",
                               "commodity": "gas", "total_consumption_kwh": 90000.0,
                               "commodity_amount_gbp": 90000.0 * 40.0 / 1000, "days_in_period": 365}]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bills_changed)
    sanity_daemon.run_cycle()
    assert len(calls) == 2


def test_run_cycle_transition_from_findings_back_to_clean_is_silent(monkeypatch):
    bad_bills = [{"customer_id": "C6", "period_end": "2024-01-28", "segment": "resi",
                  "commodity": "electricity", "total_consumption_kwh": 50000.0,
                  "commodity_amount_gbp": 50000.0 * 150.0 / 1000, "days_in_period": 365}]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bad_bills)
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
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


# --- Phase 6: internal audit (Qwen skeptic) sampling, mocked -- never a real Ollama call ---

def test_run_cycle_clean_audit_no_extra_ntfy(monkeypatch):
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[])
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    monkeypatch.setattr(sanity_daemon, "run_internal_audit", lambda bills, n_samples=2: [])
    sanity_daemon.run_cycle()
    assert calls == []
    assert "Internal audit: 0 flagged" in sanity_daemon.LOG_FILE.read_text()


def test_run_cycle_audit_finding_sends_ntfy_labelled_advisory(monkeypatch):
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[])
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    monkeypatch.setattr(
        sanity_daemon, "run_internal_audit",
        lambda bills, n_samples=2: [{"customer_id": "C1", "period_end": "2024-01-31", "note": "looks off"}],
    )
    sanity_daemon.run_cycle()
    assert len(calls) == 1
    assert "advisory" in calls[0].lower()
    assert "verify before acting" in calls[0].lower()


def test_run_cycle_audit_does_not_repeat_ntfy_for_unchanged_finding(monkeypatch):
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[])
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    monkeypatch.setattr(
        sanity_daemon, "run_internal_audit",
        lambda bills, n_samples=2: [{"customer_id": "C1", "period_end": "2024-01-31", "note": "looks off"}],
    )
    sanity_daemon.run_cycle()
    sanity_daemon.run_cycle()
    assert len(calls) == 1


def test_run_cycle_audit_does_not_repeat_ntfy_for_same_category_different_sample(monkeypatch):
    """2026-07-10 regression: real run_internal_audit re-samples a different
    (customer_id, period_end) pair every cycle (unseeded random draw), so a
    signature keyed on that pair alone re-fires every cycle even when the
    finding's substantive category (e.g. the known gas-kWh false positive)
    is identical. This is the exact bug the director flagged as "repetitive
    findings" -- 49/49 cycles fired an NTFY overnight."""
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[])
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    samples = iter([
        [{"customer_id": "C1g", "period_end": "2020-07-31",
          "note": "Gas consumption is reported in kWh, which is typically used for electricity, not gas."}],
        [{"customer_id": "C4g", "period_end": "2021-03-31",
          "note": "Gas consumption is stated in kWh, which is typically used for electricity, not gas."}],
        [{"customer_id": "C2g", "period_end": "2023-01-31",
          "note": "Gas consumption is reported in kWh, suggesting a possible unit error."}],
    ])
    monkeypatch.setattr(
        sanity_daemon, "run_internal_audit",
        lambda bills, n_samples=2: next(samples),
    )
    sanity_daemon.run_cycle()
    sanity_daemon.run_cycle()
    sanity_daemon.run_cycle()
    assert len(calls) == 1


def test_run_cycle_audit_fires_again_for_genuinely_new_category(monkeypatch):
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[])
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    samples = iter([
        [{"customer_id": "C1g", "period_end": "2020-07-31",
          "note": "Gas consumption is reported in kWh, which is typically used for electricity, not gas."}],
        [{"customer_id": "C9", "period_end": "2022-05-31",
          "note": "The standing charge appears twice on this bill, once under each fuel."}],
    ])
    monkeypatch.setattr(
        sanity_daemon, "run_internal_audit",
        lambda bills, n_samples=2: next(samples),
    )
    sanity_daemon.run_cycle()
    sanity_daemon.run_cycle()
    assert len(calls) == 2


def test_run_cycle_audit_does_not_repeat_for_varying_mixed_subsets_of_known_categories(monkeypatch):
    """The actual 2026-07-11 root cause (docs/design/SANITY_TRIAGE_2026_07_11.md):
    category normalisation alone was only a PARTIAL fix. A small per-cycle
    sample (n_samples=2) draws a DIFFERENT combination of the same 3 known
    categories each cycle -- the prior test above only ever samples ONE
    category per cycle and so never actually reproduces this. Real symptom:
    ~70 NTFYs fired over ~70 cycles, confirmed via docs/observability/
    sanity-daemon-log.md, because a signature built from {gas-kwh-unit} one
    cycle and {vat-mismatch, high-consumption} the next always looks "new"
    to a naive set-comparison, even though every individual category in it
    had already been seen before. The ledger-backed fix must not re-alert
    for any of these, since gas-kwh-unit/vat-mismatch/high-consumption all
    become known after their first appearance regardless of which subset
    a later cycle happens to draw."""
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[])
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    samples = iter([
        [{"customer_id": "C1g", "period_end": "2020-07-31",
          "note": "Gas consumption is reported in kWh, which is typically used for electricity, not gas."}],
        [{"customer_id": "C2", "period_end": "2022-07-31",
          "note": "The VAT amount does not align with the expected 20% VAT rate."},
         {"customer_id": "C8", "period_end": "2018-08-31",
          "note": "This consumption looks extremely high for a residential customer."}],
        [{"customer_id": "C4g", "period_end": "2021-03-31",
          "note": "Gas consumption is stated in kWh, which is typically used for electricity, not gas."},
         {"customer_id": "C9", "period_end": "2023-09-30",
          "note": "The VAT amount does not align with the expected 20% VAT rate."}],
        [{"customer_id": "C_IC3", "period_end": "2021-04-30",
          "note": "This consumption looks extremely high for an I&C customer."}],
    ])
    monkeypatch.setattr(
        sanity_daemon, "run_internal_audit",
        lambda bills, n_samples=2: next(samples),
    )
    sanity_daemon.run_cycle()
    assert len(calls) == 1  # cycle 1: gas-kwh-unit is genuinely new

    sanity_daemon.run_cycle()
    assert len(calls) == 2  # cycle 2: vat-mismatch AND high-consumption are both new

    sanity_daemon.run_cycle()
    assert len(calls) == 2  # cycle 3: gas-kwh-unit + vat-mismatch -- both ALREADY known, silent

    sanity_daemon.run_cycle()
    assert len(calls) == 2  # cycle 4: high-consumption again -- already known, silent


def test_audit_ledger_persists_across_a_simulated_daemon_restart(monkeypatch):
    """The other root-cause fix: the ledger is disk-persisted, not an
    in-memory module global -- a daemon restart must not forget a category
    was already seen and re-alert on it."""
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[])
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    monkeypatch.setattr(
        sanity_daemon, "run_internal_audit",
        lambda bills, n_samples=2: [{"customer_id": "C1g", "period_end": "2020-07-31",
                                      "note": "Gas consumption is reported in kWh, not gas."}],
    )
    sanity_daemon.run_cycle()
    assert len(calls) == 1

    # Simulate a process restart: nothing in-memory survives -- but this
    # module never held any relevant state in memory any more (only the
    # disk-persisted ledger), so a fresh call must still see it as known.
    sanity_daemon.run_cycle()
    assert len(calls) == 1


def test_daily_digest_fires_once_for_standing_open_findings_on_a_new_day(monkeypatch):
    """A standing open finding surfaces as ONE digest line on a later day
    that has no fresh alert of its own -- not silence forever."""
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[])
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    monkeypatch.setattr(
        sanity_daemon, "run_internal_audit",
        lambda bills, n_samples=2: [{"customer_id": "C1g", "period_end": "2020-07-31",
                                      "note": "Gas consumption is reported in kWh, not gas."}],
    )
    sanity_daemon.run_cycle()
    assert len(calls) == 1  # fresh alert, digest skipped same day

    # Simulate the next UTC calendar day by clearing the digest-date marker
    # (equivalent to real wall-clock time actually advancing a day).
    sanity_daemon.LAST_DIGEST_DATE_FILE.unlink()
    sanity_daemon.run_cycle()
    assert len(calls) == 2
    assert "daily digest" in calls[1].lower()
    assert "gas-kwh-unit" not in calls[1] or "audit:gas-kwh-unit" in calls[1]


def test_daily_digest_does_not_repeat_same_day(monkeypatch):
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[])
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    monkeypatch.setattr(
        sanity_daemon, "run_internal_audit",
        lambda bills, n_samples=2: [{"customer_id": "C1g", "period_end": "2020-07-31",
                                      "note": "Gas consumption is reported in kWh, not gas."}],
    )
    sanity_daemon.run_cycle()
    sanity_daemon.LAST_DIGEST_DATE_FILE.unlink()
    sanity_daemon.run_cycle()
    assert len(calls) == 2

    sanity_daemon.run_cycle()  # same day, digest already sent -- silent
    assert len(calls) == 2


def test_categorize_audit_note_buckets_known_false_positive_shapes():
    assert sanity_daemon._categorize_audit_note(
        "Gas consumption is reported in kWh, not gas."
    ) == "gas-kwh-unit"
    assert sanity_daemon._categorize_audit_note(
        "The VAT amount does not align with the expected rate."
    ) == "vat-mismatch"
    assert sanity_daemon._categorize_audit_note(
        "This consumption looks extremely high for a residential customer."
    ) == "high-consumption"
    assert sanity_daemon._categorize_audit_note(
        "Something entirely novel and unrelated to any known shape."
    ).startswith("other:")


# --- COUPLED-TRIAD gap surfacing in the daily digest (A6_gap_digest_surfacing) ---


def _write_gap_ledger(path, entries):
    """entries: {world_id: (twin_id, gap)}."""
    path.write_text(json.dumps({
        wid: {"twin_atom_id": twin, "gap": gap, "metric": "belief",
              "measured_at": "2026-07-13T00:00:00+00:00"}
        for wid, (twin, gap) in entries.items()
    }))


def test_coupled_gap_digest_line_reflects_ledger_values():
    """R11 / independence: the digest line reports the EXACT gap the ledger
    holds (formatted to 3dp, the same precision the Proof panel renders), for
    each coupled pair -- it never recomputes a gap."""
    _write_gap_ledger(sanity_daemon.COUPLED_GAP_LEDGER_PATH, {
        "W2_4_household_budget": ("C6_affordability_inference", 0.6065128900949797),
        "W2_7_willingness_classification": ("C9_cantpay_wontpay_classifier", 0.12781897212989005),
    })
    line = sanity_daemon._coupled_gap_digest_line()
    # The rendered value equals the ledger value at 3dp (the pixel == the number).
    assert "W2_4<->C6: 0.607" in line
    assert "W2_7<->C9: 0.128" in line
    assert "2 pairs" in line
    assert "unmeasured=0" in line and "wall-leak=0" in line and "worse-than-blind=0" in line


def test_coupled_gap_digest_line_counts_unmeasured_leak_and_worse_than_blind():
    """The anti-decay counts (unmeasured / wall-leak / worse-than-blind) mirror
    the Proof panel's classification exactly: null gap -> unmeasured; gap<=0 ->
    wall-leak (observable leaked the hidden truth); gap>1 -> worse than blind."""
    _write_gap_ledger(sanity_daemon.COUPLED_GAP_LEDGER_PATH, {
        "W2_4_household_budget": ("C6_affordability_inference", 0.42),   # learning
        "W2_5_life_event_stream": ("C7_life_event_detection", None),     # unmeasured
        "W2_6_sme_distress_twin": ("C8_sme_credit_risk", 0.0),           # wall-leak
        "W2_7_willingness_classification": ("C9_cantpay_wontpay_classifier", 1.4),  # worse
    })
    line = sanity_daemon._coupled_gap_digest_line()
    assert "unmeasured=1" in line
    assert "wall-leak=1" in line
    assert "worse-than-blind=1" in line
    assert "untested" in line  # the null-gap pair renders as untested


def test_coupled_gap_digest_line_fail_closed_when_ledger_missing():
    """R15 fail-closed: a missing ledger is announced explicitly, never a
    silent omission."""
    assert not sanity_daemon.COUPLED_GAP_LEDGER_PATH.exists()
    line = sanity_daemon._coupled_gap_digest_line()
    assert "MISSING" in line and "fail-closed" in line


def test_coupled_gap_digest_line_fail_closed_when_ledger_empty():
    sanity_daemon.COUPLED_GAP_LEDGER_PATH.write_text("{}")
    line = sanity_daemon._coupled_gap_digest_line()
    assert "EMPTY" in line and "fail-closed" in line


def test_coupled_gap_digest_line_fail_closed_when_ledger_malformed():
    sanity_daemon.COUPLED_GAP_LEDGER_PATH.write_text("not json {")
    line = sanity_daemon._coupled_gap_digest_line()
    assert "UNREADABLE" in line and "fail-closed" in line


def test_daily_digest_carries_live_coupled_gap_line(monkeypatch):
    """End-to-end (R11): when the daily digest fires, the NTFY it sends carries
    the per-coupled-pair gap line whose values EQUAL the live ledger's values.
    Proves the wiring, not just the helper."""
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[])
    _write_gap_ledger(sanity_daemon.COUPLED_GAP_LEDGER_PATH, {
        "W2_4_household_budget": ("C6_affordability_inference", 0.6065128900949797),
    })
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    monkeypatch.setattr(
        sanity_daemon, "run_internal_audit",
        lambda bills, n_samples=2: [{"customer_id": "C1g", "period_end": "2020-07-31",
                                      "note": "Gas consumption is reported in kWh, not gas."}],
    )
    sanity_daemon.run_cycle()  # cycle 1: fresh audit alert, digest skipped same day
    assert len(calls) == 1

    sanity_daemon.LAST_DIGEST_DATE_FILE.unlink()  # simulate a new UTC day
    sanity_daemon.run_cycle()  # cycle 2: standing finding -> digest fires
    assert len(calls) == 2
    digest = calls[1]
    assert "daily digest" in digest.lower()
    assert "COUPLED-TRIAD gap" in digest
    # The digest value equals the ledger value (0.6065... -> 0.607 at 3dp).
    assert "W2_4<->C6: 0.607" in digest


def test_run_cycle_population_and_audit_ntfys_are_independent(monkeypatch):
    bills = [{"customer_id": "C6", "period_end": "2024-01-28", "segment": "resi",
              "commodity": "electricity", "total_consumption_kwh": 50000.0,
              "commodity_amount_gbp": 50000.0 * 150.0 / 1000, "days_in_period": 365}]
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=bills)
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    monkeypatch.setattr(
        sanity_daemon, "run_internal_audit",
        lambda bills, n_samples=2: [{"customer_id": "C6", "period_end": "2024-01-28", "note": "SME-scale"}],
    )
    sanity_daemon.run_cycle()
    assert len(calls) == 2  # one population NTFY, one audit NTFY -- distinct signals


# --- Layer 2 dimension 2: payment-channel-mix population check wiring (2026-07-09) ---


def test_run_cycle_reads_billing_ledger_payments_for_channel_mix(monkeypatch):
    """When site/state/billing_ledger.json (isolated to tmp_path) exists with
    a lopsided all-direct_debit resi population, run_cycle() must surface the
    payment_channel_mix_vs_desnz_anchor finding -- proving the daemon actually
    reads and passes the payments through, not just a dead code path."""
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[])
    sanity_daemon.BILLING_LEDGER_PATH.write_text(json.dumps({
        "customers": {
            "C1": {"segment": "resi", "payments": [{"method": "direct_debit"}] * 50},
        }
    }))
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    assert len(calls) == 1
    assert "Direct Debit share" in sanity_daemon.LOG_FILE.read_text()


def test_run_cycle_missing_billing_ledger_skips_channel_mix_check_gracefully(monkeypatch):
    """No billing_ledger.json at all (e.g. a run predating it) must not
    crash the cycle -- the check is simply skipped, matching the rest of
    this daemon's graceful-degradation design."""
    _write_run_output(sanity_daemon.RUN_OUTPUT_PATH, bills=[])
    assert not sanity_daemon.BILLING_LEDGER_PATH.exists()
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    sanity_daemon.run_cycle()
    assert calls == []
    assert "Clean" in sanity_daemon.LOG_FILE.read_text()
