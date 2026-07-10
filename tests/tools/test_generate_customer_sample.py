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
    assert c1["occupancy"] in ("one_person", "two_person", "three_to_four_person", "five_plus_person")


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
    assert ic["occupancy"] is None


def test_resi_customer_gets_engagement_level(tmp_path):
    """2026-07-10, C1_segment_layers self-refill draw: engagement_level
    (simulation/household_segments.py, drives active/passive renewal for
    EVERY segment in run_phase2b.py) was computed but never surfaced
    anywhere on the SIM tab -- a real gap, now fixed."""
    customers = {
        "C1": {"segment": "resi", "commodity": "electricity", "acquisition_date": "2020-01-01",
               "revenue_gbp": 100.0, "gross_gbp": 50.0, "net_gbp": 20.0},
    }
    out = _generate(tmp_path, customers)
    assert out["customers"]["C1"]["engagement_level"] in ("active", "passive", "disengaged")


def test_ic_customer_also_gets_engagement_level(tmp_path):
    """Unlike payment_channel/fuel_poverty/tenure/occupancy, engagement_level
    is NOT resi-gated -- run_phase2b.py looks it up unconditionally for
    every billing_account regardless of segment."""
    customers = {
        "C_IC1": {"segment": "I&C", "commodity": "electricity", "acquisition_date": "2020-01-01",
                  "revenue_gbp": 100000.0, "gross_gbp": 5000.0, "net_gbp": 2000.0},
    }
    out = _generate(tmp_path, customers)
    assert out["customers"]["C_IC1"]["engagement_level"] in ("active", "passive", "disengaged")


def test_engagement_level_deterministic_and_shared_across_dual_fuel_legs(tmp_path):
    """engagement_level_for_customer() is keyed on the household base_id
    (billing_account), matching run_phase2b.py's own lookup -- a dual-fuel
    household's gas leg must resolve to the SAME engagement level as its
    electricity leg."""
    customers = {
        "C1": {"segment": "resi", "commodity": "electricity", "acquisition_date": "2020-01-01",
               "revenue_gbp": 100.0, "gross_gbp": 50.0, "net_gbp": 20.0},
        "C1g": {"segment": "resi", "commodity": "gas", "acquisition_date": "2020-01-01",
                "revenue_gbp": 50.0, "gross_gbp": 20.0, "net_gbp": 10.0},
    }
    out = _generate(tmp_path, customers)
    assert out["customers"]["C1"]["engagement_level"] == out["customers"]["C1g"]["engagement_level"]


def test_gas_twin_gets_same_tenure_and_occupancy_as_electricity_leg(tmp_path):
    """Tenure/occupancy are household-level (not per-fuel) traits -- a
    dual-fuel household's gas leg must resolve to the SAME tenure/occupancy
    as its electricity leg (both keyed on base_account_id), unlike
    payment_channel/fuel_poverty which are legitimately fuel-specific."""
    customers = {
        "C1": {"segment": "resi", "commodity": "electricity", "acquisition_date": "2020-01-01",
               "revenue_gbp": 100.0, "gross_gbp": 50.0, "net_gbp": 20.0},
        "C1g": {"segment": "resi", "commodity": "gas", "acquisition_date": "2020-01-01",
                "revenue_gbp": 50.0, "gross_gbp": 20.0, "net_gbp": 8.0},
    }
    out = _generate(tmp_path, customers)
    assert out["customers"]["C1"]["tenure"] == out["customers"]["C1g"]["tenure"]
    assert out["customers"]["C1"]["occupancy"] == out["customers"]["C1g"]["occupancy"]


def test_payment_channel_deterministic_across_regeneration(tmp_path):
    customers = {
        "C7": {"segment": "resi", "commodity": "electricity", "acquisition_date": "2019-06-01",
               "revenue_gbp": 200.0, "gross_gbp": 80.0, "net_gbp": 30.0},
    }
    out1 = _generate(tmp_path, customers)
    out2 = _generate(tmp_path, customers)
    assert out1["customers"]["C7"]["payment_channel"] == out2["customers"]["C7"]["payment_channel"]
    assert out1["customers"]["C7"]["fuel_poverty"] == out2["customers"]["C7"]["fuel_poverty"]


# --- smart_meter / home_type / dual_fuel (2026-07-10, director page comment
# on /sim/: "No info on smart meters. Duel fuel. House type. Business type
# consumption") -- sourced from saas/customers.py, real per-customer_id data ---

def test_home_type_and_smart_meter_sourced_from_raw_customer_record(tmp_path):
    customers = {
        "C1": {"segment": "resi", "commodity": "electricity", "acquisition_date": "2016-01-01",
               "revenue_gbp": 100.0, "gross_gbp": 50.0, "net_gbp": 20.0},
    }
    out = _generate(tmp_path, customers)
    c1 = out["customers"]["C1"]
    assert c1["home_type"] == "urban_flat"
    assert c1["smart_meter"] is True


def test_business_customer_home_type_is_the_business_premises_type(tmp_path):
    """home_type doubles as the "business type" signal for I&C/SME accounts
    (no separate field exists in saas/customers.py -- same key, segment-aware
    label on the rendering side)."""
    customers = {
        "C_IC1": {"segment": "I&C", "commodity": "electricity", "acquisition_date": "2016-01-01",
                  "revenue_gbp": 100000.0, "gross_gbp": 5000.0, "net_gbp": 2000.0},
    }
    out = _generate(tmp_path, customers)
    assert out["customers"]["C_IC1"]["home_type"] == "warehouse_unit"


def test_dual_fuel_true_when_both_legs_present(tmp_path):
    customers = {
        "C1": {"segment": "resi", "commodity": "electricity", "acquisition_date": "2016-01-01",
               "revenue_gbp": 100.0, "gross_gbp": 50.0, "net_gbp": 20.0},
        "C1g": {"segment": "resi", "commodity": "gas", "acquisition_date": "2016-01-01",
                "revenue_gbp": 50.0, "gross_gbp": 20.0, "net_gbp": 8.0},
    }
    out = _generate(tmp_path, customers)
    assert out["customers"]["C1"]["dual_fuel"] is True
    assert out["customers"]["C1g"]["dual_fuel"] is True


def test_dual_fuel_false_when_only_one_leg_present(tmp_path):
    customers = {
        "C7": {"segment": "resi", "commodity": "electricity", "acquisition_date": "2019-06-01",
               "revenue_gbp": 200.0, "gross_gbp": 80.0, "net_gbp": 30.0},
    }
    out = _generate(tmp_path, customers)
    assert out["customers"]["C7"]["dual_fuel"] is False
