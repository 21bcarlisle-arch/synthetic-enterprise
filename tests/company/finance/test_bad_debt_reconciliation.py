"""R15-both-ways tests for the bad-debt reconciliation bridge.

The variance control must be ABLE TO FAIL (R15): a control that always passes is
theatre. These prove it fires on its own named defects (realised zeroed;
estimate==outcome tautology; missing input) and clears on genuine data.

The pure reconciliation core (`company.finance.bad_debt_reconciliation`) is
wall-clean over primitives, so these tests need no SIM run. The collector
(`background.bad_debt_reconciliation_run`) is exercised on a tiny genuine fixture
to prove the end-to-end report + ledger append preserve other rows.
"""
import json

import pytest

from company.finance.bad_debt_reconciliation import (
    LEDGER_REL_ID,
    UNWIRED_METHODS,
    build_ledger_record,
    build_report,
    reconcile_by_year,
    variance_control,
)


# --- non-degenerate fixture: flat provision (billed) diverges from realised ---
_FLAT = {2021: 1000.0, 2022: 5000.0, 2023: 3000.0}
_REALISED = {2022: 400.0, 2023: 900.0}


def test_reconcile_by_year_covers_union_and_computes_variance():
    rows = {r.year: r for r in reconcile_by_year(_FLAT, _REALISED)}
    # 2021 has a provision but no realised loss -> a real row, not dropped.
    assert rows[2021].realised_written_off_gbp == 0.0
    assert rows[2021].variance_gbp == pytest.approx(1000.0)
    assert rows[2021].variance_ratio is None  # realised 0 -> undefined ratio
    assert rows[2022].variance_gbp == pytest.approx(4600.0)  # 5000 - 400
    assert rows[2022].variance_ratio == pytest.approx(12.5)
    assert rows[2022].provision_clock == "billed"
    assert rows[2022].realised_clock == "settled"


def test_report_carries_clocks_and_unwired_methods():
    report = build_report(_FLAT, _REALISED, generated_from="unit-fixture")
    assert report["provision_total_gbp"] == pytest.approx(9000.0)
    assert report["realised_total_gbp"] == pytest.approx(1300.0)
    assert report["provision_vs_realised_variance_gbp"] == pytest.approx(7700.0)
    # R14: every year row carries both clocks.
    for row in report["years"]:
        assert row["provision_clock"] == "billed"
        assert row["realised_clock"] == "settled"
    # steer D4: unwired methods reported, never fabricated.
    assert set(report["unwired_methods"]) == {"aging_matrix", "stage_recovery"}
    for entry in report["unwired_methods"].values():
        assert entry["status"].startswith("unwired")
        assert entry["needs"]  # names the input path each would require


# --------------------------------------------------------------------------
# R15 both ways -- the control must FAIL on its named defects and PASS on data.
# --------------------------------------------------------------------------

def test_control_passes_on_genuine_nondegenerate_data():
    result = variance_control(_FLAT, _REALISED)
    assert result.passed, result.reasons


def test_mutation1_zeroed_realised_trips_control():
    """MUTATION 1: a company that provisions while realising NO loss is a red
    flag (structurally-incapable-of-being-wrong), not a pass."""
    zeroed = {y: 0.0 for y in _REALISED}
    result = variance_control(_FLAT, zeroed)
    assert not result.passed
    assert any("realised written-off total is 0" in r for r in result.reasons)


def test_mutation2_tautology_provision_equals_realised_trips_control():
    """MUTATION 2: estimate := outcome. The variance is then not an independent
    measurement of the estimate's error (R15 tautology doctrine)."""
    tautological = dict(_REALISED)  # provision copied from the outcome
    result = variance_control(tautological, _REALISED)
    assert not result.passed
    assert any("tautology" in r or "independent measurement" in r for r in result.reasons)


def test_mutation2_near_tautology_within_epsilon_also_trips():
    """A copy perturbed by sub-penny noise is still not independent -- the
    control keys on max|variance| <= epsilon, not exact equality."""
    near = {y: v + 1e-9 for y, v in _REALISED.items()}
    result = variance_control(near, _REALISED)
    assert not result.passed


def test_fail_closed_empty_provision():
    """Missing/empty input -> NOT a clean 'reconciled' (fail-open forbidden)."""
    result = variance_control({}, _REALISED)
    assert not result.passed
    assert any("fail-closed" in r for r in result.reasons)


def test_fail_closed_empty_realised():
    result = variance_control(_FLAT, {})
    assert not result.passed
    assert any("fail-closed" in r for r in result.reasons)


def test_report_reflects_control_failure_not_silently_reconciled():
    """An empty realised input must surface as control.passed=False in the
    report, never as a silently-reconciled artifact."""
    report = build_report(_FLAT, {}, generated_from="unit-fixture")
    assert report["control"]["passed"] is False
    assert report["control"]["reasons"]


# --------------------------------------------------------------------------
# Ledger record schema + fidelity ledger merge preserves other rows.
# --------------------------------------------------------------------------

def test_ledger_record_matches_schema_and_validates():
    from background.fidelity_evidence_ledger import _validate_record

    report = build_report(_FLAT, _REALISED, generated_from="unit-fixture")
    record = build_ledger_record(report)
    # Must not raise LedgerMalformed.
    _validate_record(record)
    assert record["rel_id"] == LEDGER_REL_ID
    assert record["relationship"]["provenance"] == "estimated_from_data"
    assert record["relationship"]["simplification_id"]  # honest-beyond-minimum


def test_append_preserves_existing_rows(tmp_path):
    from background.fidelity_evidence_ledger import append_record, load_ledger

    ledger_path = tmp_path / "ledger.json"
    # Seed with a pre-existing, unrelated row.
    prior = {
        "rel_id": "some_other_row",
        "atom_id": "W_other",
        "relationship": {
            "kind": "other", "provenance": "assumed", "simplification_id": None,
        },
    }
    append_record(prior, ledger_path=ledger_path)

    report = build_report(_FLAT, _REALISED, generated_from="unit-fixture")
    append_record(build_ledger_record(report), ledger_path=ledger_path)

    ledger = load_ledger(ledger_path)
    assert "some_other_row" in ledger  # prior row survived the merge
    assert LEDGER_REL_ID in ledger


# --------------------------------------------------------------------------
# Collector end-to-end on a tiny GENUINE fixture (a churned customer that
# fails payment -> a real written-off amount from the arrears engine).
# --------------------------------------------------------------------------

def _bill(cid, period_end, amount, segment="resi"):
    return {
        "customer_id": cid,
        "period_end": period_end,
        "total_amount_gbp": amount,
        "segment": segment,
        "commodity": "electricity",
    }


def test_collector_end_to_end_on_real_fixture(tmp_path):
    from background.bad_debt_reconciliation_run import (
        generate_report,
        register_ledger_row,
        write_report,
    )

    # 24 monthly bills for a HIGH-stress customer who churns -> genuine write-offs.
    bills = [
        _bill("C1", f"202{2 + i // 12}-{(i % 12) + 1:02d}-28", 200.0)
        for i in range(24)
    ]
    behavioral = {
        "C1": {"income_stress_trajectory": [
            {"year": 2022, "stress": "HIGH"},
            {"year": 2023, "stress": "HIGH"},
        ]}
    }
    run_data = {
        "bills": bills,
        "per_customer_behavioral": behavioral,
        "churned_billing_accounts": ["C1"],
    }

    report = generate_report(run_data, generated_from="test-fixture", seed=42)

    # Non-degenerate: some flat provision AND some realised write-off exist.
    assert report["provision_total_gbp"] > 0
    assert report["realised_total_gbp"] > 0
    assert report["control"]["passed"], report["control"]["reasons"]

    # Report writes to a scratch path (no published artifact touched).
    out = write_report(report, report_path=tmp_path / "recon.json")
    on_disk = json.loads(out.read_text())
    assert on_disk["provision_vs_realised_variance_gbp"] == (
        report["provision_vs_realised_variance_gbp"]
    )

    # Ledger append into a scratch ledger (never the real one in tests).
    ledger = register_ledger_row(report, ledger_path=tmp_path / "ledger.json")
    assert LEDGER_REL_ID in ledger
