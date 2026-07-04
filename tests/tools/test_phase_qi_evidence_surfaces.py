"""Tests for the EVIDENCE_IN_BUSINESS_SURFACES.md retrofit (Phase QI): the
QD bad-debt/arrears cascade and the C7 income-stress/life-event case study
must appear on the Sim/Customers/Supplier shadow pages as real, generated
evidence -- not just described in a spec. Covers the three new generators
in tools/generate_shadow_html.py: the behavioral signal/correlation panel
(Sim), the named customer case study + divergence (Customers), and the
collections/dunning process aggregate (Supplier)."""
from tools.generate_shadow_html import (
    _behavioral_case_study,
    _behavioral_signal_correlation,
    _collections_process,
    build_customers,
    build_sim,
    build_supplier,
)


def _sample_with(cid, life_events, stress_traj, pay_score="FAIR", metrics=None):
    return {
        "customers": {
            cid: {
                "life_event_history": life_events,
                "income_stress_trajectory": stress_traj,
                "payment_behaviour_analytics": {
                    "score": pay_score,
                    "metrics": metrics or {"on_time_rate": 0.75, "late_rate": 0.16, "dd_fail_rate": 0.1},
                },
            }
        }
    }


def _ledger_with(cid, arrears_history):
    return {"customers": {cid: {"arrears_history": arrears_history}}}


def test_case_study_names_the_transition_year_not_the_last_year():
    sample = _sample_with(
        "C7",
        life_events=[{"date": "2023-12-23", "event_type": "new_baby"}],
        stress_traj=[
            {"year": 2021, "stress": "low"},
            {"year": 2022, "stress": "low"},
            {"year": 2023, "stress": "moderate"},
            {"year": 2024, "stress": "moderate"},
            {"year": 2025, "stress": "moderate"},
        ],
    )
    ledger = _ledger_with("C7", [
        {"case_id": "ARR-1", "opened_date": "2023-06-14", "arrears_gbp": 354.44,
         "stages": [{"stage": "DD_FAILED", "date": "2023-06-14"}, {"stage": "RESOLVED", "date": "2023-07-29"}]},
    ])
    html = _behavioral_case_study(sample, ledger, "C7")
    assert "from 2023 onward" in html
    assert "from 2025 onward" not in html
    assert "new baby" in html
    assert "FAIR" in html


def test_case_study_shows_both_sides_of_the_wall():
    sample = _sample_with("C7", [{"date": "2023-12-23", "event_type": "new_baby"}],
                           [{"year": 2023, "stress": "moderate"}])
    ledger = _ledger_with("C7", [])
    html = _behavioral_case_study(sample, ledger, "C7")
    assert "not observable to the company" in html
    assert "Company-Observable" in html
    assert "basis risk" in html


def test_case_study_missing_customer_returns_empty_not_crash():
    assert _behavioral_case_study({"customers": {}}, {"customers": {}}, "C99") == ""
    assert _behavioral_case_study({}, {}, "C7") == ""


def test_signal_correlation_counts_stress_levels_per_year():
    sample = {
        "customers": {
            "C1": {"income_stress_trajectory": [{"year": 2022, "stress": "low"}, {"year": 2023, "stress": "moderate"}]},
            "C2": {"income_stress_trajectory": [{"year": 2022, "stress": "high"}, {"year": 2023, "stress": "moderate"}]},
            "C2g": {"income_stress_trajectory": [{"year": 2022, "stress": "high"}]},
        }
    }
    ledger = _ledger_with("C1", [{"opened_date": "2023-03-01", "arrears_gbp": 100}])
    html = _behavioral_signal_correlation(sample, ledger, [{"year": 2023, "bad_debt_gbp": 50.0}])
    assert "<td>2022</td><td>1</td><td>0</td><td>1</td>" in html
    assert "<td>2023</td><td>0</td><td>2</td><td>0</td><td>1</td>" in html
    assert "&pound;50" in html


def test_signal_correlation_missing_data_returns_empty():
    assert _behavioral_signal_correlation({}, {}, []) == ""
    assert _behavioral_signal_correlation({"customers": {}}, {}, []) == ""


def test_collections_process_separates_written_off_from_resolved_value():
    ledger = {
        "customers": {
            "C1": {"arrears_history": [
                {"arrears_gbp": 100.0, "stages": [{"stage": "DD_FAILED"}, {"stage": "RESOLVED"}]},
                {"arrears_gbp": 250.0, "stages": [{"stage": "DD_FAILED"}, {"stage": "WRITTEN_OFF"}]},
            ]},
            "C2": {"arrears_history": [
                {"arrears_gbp": 40.0, "stages": [{"stage": "DD_FAILED"}]},
            ]},
        }
    }
    html = _collections_process(ledger)
    assert "3 arrears cases opened" in html
    assert "&pound;390 total arrears value" in html
    assert "1 resolved via payment plan" in html
    assert "&pound;250 -- feeds the emergent bad debt" in html
    assert "1 still open" in html


def test_collections_process_missing_ledger_returns_empty():
    assert _collections_process(None) == ""
    assert _collections_process({}) == ""


def test_build_customers_includes_case_study_when_ledger_present():
    dash = {"meta": {}, "build": {}, "customers": {"lifetime": {}, "events": [], "retention": []}}
    sample = _sample_with("C7", [{"date": "2023-12-23", "event_type": "new_baby"}],
                           [{"year": 2023, "stress": "moderate"}])
    ledger = _ledger_with("C7", [{"case_id": "ARR-1", "opened_date": "2023-06-14",
                                   "arrears_gbp": 100, "stages": [{"stage": "RESOLVED", "date": "2023-07-01"}]}])
    html = build_customers(dash, sample, "ts", ledger)
    assert "Behavioral Case Study: C7" in html


def test_build_sim_includes_correlation_panel_when_data_present():
    sim_data = {"annual": [], "monthly": [], "peak_records": [], "metadata": {}}
    sample = {"customers": {"C1": {"income_stress_trajectory": [{"year": 2022, "stress": "low"}]}}}
    ledger = _ledger_with("C1", [])
    html = build_sim(sim_data, "ts", "abc1234", "QI", sample, ledger, [])
    assert "Customer Behavioral Signal" in html


def test_build_supplier_includes_collections_process_when_ledger_present():
    dash = {
        "meta": {}, "build": {},
        "financial": {"annual": [], "ledger": {}, "segment_annual": []},
    }
    ledger = {"customers": {"C1": {"arrears_history": [
        {"arrears_gbp": 10.0, "stages": [{"stage": "DD_FAILED"}, {"stage": "RESOLVED"}]},
    ]}}}
    html = build_supplier(dash, "ts", ledger)
    assert "Collections &amp; Dunning Process" in html


def test_build_functions_degrade_gracefully_without_ledger():
    dash = {"meta": {}, "build": {}, "customers": {"lifetime": {}, "events": [], "retention": []},
            "financial": {"annual": [], "ledger": {}, "segment_annual": []}}
    assert "Behavioral Case Study" not in build_customers(dash, {"customers": {}}, "ts")
    assert "Collections &amp; Dunning Process" not in build_supplier(dash, "ts")
