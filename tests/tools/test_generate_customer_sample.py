"""Tests for tools/generate_customer_sample.py -- focused on the 2026-07-09
payment_channel/fuel_poverty fields added for Layer 2 dimensions 1-2
(CORE_FIDELITY_BEFORE_LOOPS Phase 2).

All tests pass explicit out_path/state_path (tmp_path-based) -- generate()
writes to the real site/data + site/state paths by default, and a first
version of this file that omitted these overrides clobbered the real,
committed customer_sample.json with test fixture data.
"""
import json

from tools.generate_customer_sample import generate


def _minimal_run(tmp_path, customers):
    run = {
        "per_customer_lifetime": customers,
        "by_billing_account": {},
        "customer_events": [],
        "basis_risk_by_billing_account": {},
        "churn_accuracy_by_billing_account": {},
        "per_customer_behavioral": {},
        "years": {},
        "feedback_survey_log": [],
        "reputation_events_log": [],
        "nudge_physics_log": [],
    }
    run_json = tmp_path / "run.json"
    run_json.write_text(json.dumps(run))
    return run_json


def _generate(tmp_path, customers):
    run_json = _minimal_run(tmp_path, customers)
    out_path = tmp_path / "customer_sample.json"
    state_path = tmp_path / "state_customer_sample.json"
    generate(str(run_json), out_path=str(out_path), state_path=str(state_path))
    return json.loads(out_path.read_text())


def test_resi_customer_gets_payment_channel_and_fuel_poverty_fields(tmp_path):
    customers = {
        "C1": {"segment": "resi", "commodity": "electricity", "acquisition_date": "2020-01-01",
               "revenue_gbp": 100.0, "gross_gbp": 50.0, "net_gbp": 20.0},
    }
    out = _generate(tmp_path, customers)
    c1 = out["customers"]["C1"]
    assert c1["payment_channel"] in ("direct_debit", "standard_credit")
    assert isinstance(c1["fuel_poverty"], bool)
    assert c1["tenure"] in ("owner_occupier", "private_renter", "social_renter")


def test_ic_customer_has_null_payment_channel_and_fuel_poverty(tmp_path):
    """Payment-channel/fuel-poverty/tenure archetypes are a resi-only concept
    (I&C/SME use bacs/chaps, not a household DD-vs-standard-credit split)."""
    customers = {
        "C_IC1": {"segment": "I&C", "commodity": "electricity", "acquisition_date": "2020-01-01",
                  "revenue_gbp": 100000.0, "gross_gbp": 5000.0, "net_gbp": 2000.0},
    }
    out = _generate(tmp_path, customers)
    ic = out["customers"]["C_IC1"]
    assert ic["payment_channel"] is None
    assert ic["fuel_poverty"] is None
    assert ic["tenure"] is None


def test_gas_twin_gets_same_tenure_as_electricity_leg(tmp_path):
    """Tenure is a household-level (not per-fuel) trait -- a dual-fuel
    household's gas leg must resolve to the SAME tenure as its electricity
    leg (both keyed on base_account_id), unlike payment_channel/fuel_poverty
    which are legitimately fuel-specific."""
    customers = {
        "C1": {"segment": "resi", "commodity": "electricity", "acquisition_date": "2020-01-01",
               "revenue_gbp": 100.0, "gross_gbp": 50.0, "net_gbp": 20.0},
        "C1g": {"segment": "resi", "commodity": "gas", "acquisition_date": "2020-01-01",
                "revenue_gbp": 50.0, "gross_gbp": 20.0, "net_gbp": 8.0},
    }
    out = _generate(tmp_path, customers)
    assert out["customers"]["C1"]["tenure"] == out["customers"]["C1g"]["tenure"]


def test_payment_channel_deterministic_across_regeneration(tmp_path):
    customers = {
        "C7": {"segment": "resi", "commodity": "electricity", "acquisition_date": "2019-06-01",
               "revenue_gbp": 200.0, "gross_gbp": 80.0, "net_gbp": 30.0},
    }
    out1 = _generate(tmp_path, customers)
    out2 = _generate(tmp_path, customers)
    assert out1["customers"]["C7"]["payment_channel"] == out2["customers"]["C7"]["payment_channel"]
    assert out1["customers"]["C7"]["fuel_poverty"] == out2["customers"]["C7"]["fuel_poverty"]
