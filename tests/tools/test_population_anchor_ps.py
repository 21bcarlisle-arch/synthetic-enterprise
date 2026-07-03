"""Phase PS -- Complaints & Arrears Population Anchoring tests."""
import json
from pathlib import Path

from tools.population_anchor import (
    _complaints_check, _arrears_check_by_year, generate,
    COMPLAINT_BENCHMARK_NORMAL_HI, COMPLAINT_BENCHMARK_CRISIS_HI,
    ARREARS_BENCHMARK_NORMAL_HI, ARREARS_BENCHMARK_CRISIS_HI,
)


def _yr(year, complaint_prob=0.05, active=None):
    return {str(year): {
        "avg_complaint_probability": complaint_prob,
        "active_customer_ids": active or ["C1", "C2", "C3", "C4"],
    }}


def _ledger(*arrears_list):
    customers = {}
    for cid, opened_date in arrears_list:
        customers.setdefault(cid, {"arrears_history": []})["arrears_history"].append(
            {"opened_date": opened_date}
        )
    return {"customers": customers}


def test_complaints_check_converts_probability():
    years = {"2020": {"avg_complaint_probability": 0.05}}
    findings = _complaints_check(years)
    assert abs(findings[0]["complaint_rate_pct"] - 5.0) < 0.01


def test_complaints_check_green_normal_year():
    years = {"2020": {"avg_complaint_probability": 0.05}}
    assert _complaints_check(years)[0]["rag"] == "GREEN"


def test_complaints_check_amber_normal_year():
    years = {"2020": {"avg_complaint_probability": 0.065}}
    assert _complaints_check(years)[0]["rag"] == "AMBER"


def test_complaints_check_green_crisis_year():
    years = {"2022": {"avg_complaint_probability": 0.058}}
    result = _complaints_check(years)
    assert result[0]["rag"] == "GREEN"
    assert result[0]["benchmark_green_hi"] == COMPLAINT_BENCHMARK_CRISIS_HI


def test_complaints_check_red_below_floor():
    years = {"2020": {"avg_complaint_probability": 0.005}}
    assert _complaints_check(years)[0]["rag"] == "RED"


def test_complaints_check_red_above_ceiling():
    years = {"2020": {"avg_complaint_probability": 0.15}}
    assert _complaints_check(years)[0]["rag"] == "RED"


def test_complaints_check_missing_probability_defaults_to_red():
    years = {"2020": {}}
    result = _complaints_check(years)
    assert result[0]["complaint_rate_pct"] == 0.0
    assert result[0]["rag"] == "RED"


def test_arrears_check_counts_unique_customers_per_year():
    ledger = _ledger(("C1", "2020-03-15"), ("C1", "2020-08-01"), ("C2", "2020-05-01"))
    years = {"2020": {"active_customer_ids": ["C1", "C2", "C3", "C4"]}}
    result = _arrears_check_by_year(ledger, years)
    assert result[0]["new_arrears_count"] == 2


def test_arrears_check_green_below_threshold():
    ledger = _ledger(("C1", "2020-01-01"))
    active = ["C%d" % i for i in range(1, 16)]
    years = {"2020": {"active_customer_ids": active}}
    result = _arrears_check_by_year(ledger, years)
    assert result[0]["new_arrears_rate_pct"] < 8.0
    assert result[0]["rag"] == "GREEN"


def test_arrears_check_amber_above_normal_threshold():
    active = ["C%d" % i for i in range(1, 101)]
    ledger = _ledger(*[("C%d" % i, "2020-01-01") for i in range(1, 10)])
    years = {"2020": {"active_customer_ids": active}}
    result = _arrears_check_by_year(ledger, years)
    assert result[0]["new_arrears_rate_pct"] == 9.0
    assert result[0]["rag"] == "AMBER"


def test_arrears_check_green_crisis_year_raised_ceiling():
    active = ["C%d" % i for i in range(1, 101)]
    ledger = _ledger(*[("C%d" % i, "2022-06-01") for i in range(1, 11)])
    years = {"2022": {"active_customer_ids": active}}
    result = _arrears_check_by_year(ledger, years)
    assert result[0]["new_arrears_rate_pct"] == 10.0
    assert result[0]["benchmark_green_hi"] == ARREARS_BENCHMARK_CRISIS_HI
    assert result[0]["rag"] == "GREEN"


def test_arrears_check_red_above_amber_threshold():
    active = ["C%d" % i for i in range(1, 101)]
    ledger = _ledger(*[("C%d" % i, "2020-01-01") for i in range(1, 17)])
    years = {"2020": {"active_customer_ids": active}}
    result = _arrears_check_by_year(ledger, years)
    assert result[0]["rag"] == "RED"


def test_arrears_check_handles_empty_arrears_history():
    ledger = {"customers": {"C1": {"arrears_history": []}, "C2": {}}}
    years = {"2020": {"active_customer_ids": ["C1", "C2"]}}
    result = _arrears_check_by_year(ledger, years)
    assert result[0]["new_arrears_count"] == 0
    assert result[0]["rag"] == "GREEN"


def test_arrears_check_denominator_uses_active_customer_ids():
    ledger = _ledger(("C1", "2020-05-01"), ("C2", "2020-06-01"))
    active = ["C%d" % i for i in range(1, 11)]
    years = {"2020": {"active_customer_ids": active}}
    result = _arrears_check_by_year(ledger, years)
    assert result[0]["active_customers"] == 10
    assert result[0]["new_arrears_rate_pct"] == 20.0


def test_generate_includes_complaints_vs_benchmark(tmp_path):
    run = {"customer_events": [], "years": {
        "2020": {"avg_complaint_probability": 0.05, "bad_debt_gbp": 100,
                 "revenue_gbp": 100000, "active_customer_ids": ["C1"]},
    }}
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(run))
    lp = tmp_path / "billing_ledger.json"
    lp.write_text(json.dumps({"customers": {}}))
    out = tmp_path / "anchor.json"
    result = generate(rj, out, billing_ledger_path=lp)
    assert "complaints_vs_benchmark" in result
    assert len(result["complaints_vs_benchmark"]) == 1


def test_generate_includes_arrears_vs_benchmark(tmp_path):
    run = {"customer_events": [], "years": {
        "2020": {"avg_complaint_probability": 0.05, "bad_debt_gbp": 100,
                 "revenue_gbp": 100000, "active_customer_ids": ["C1", "C2"]},
    }}
    ledger = {"customers": {"C1": {"arrears_history": [{"opened_date": "2020-03-01"}]}}}
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(run))
    lp = tmp_path / "billing_ledger.json"
    lp.write_text(json.dumps(ledger))
    out = tmp_path / "anchor.json"
    result = generate(rj, out, billing_ledger_path=lp)
    assert "arrears_vs_benchmark" in result
    assert result["arrears_vs_benchmark"][0]["new_arrears_count"] == 1


def test_generate_handles_missing_billing_ledger(tmp_path):
    run = {"customer_events": [], "years": {
        "2020": {"avg_complaint_probability": 0.05, "bad_debt_gbp": 0,
                 "revenue_gbp": 100000, "active_customer_ids": ["C1"]},
    }}
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(run))
    out = tmp_path / "anchor.json"
    nonexistent = tmp_path / "no_ledger.json"
    result = generate(rj, out, billing_ledger_path=nonexistent)
    assert "arrears_vs_benchmark" in result
    assert result["arrears_vs_benchmark"][0]["new_arrears_count"] == 0
    assert result["arrears_vs_benchmark"][0]["rag"] == "GREEN"


def test_section_population_anchoring_renders_table():
    from saas.reporting.annual_report import _section_population_anchoring
    data = {"years": {"2020": {"avg_complaint_probability": 0.05,
                               "active_customer_ids": ["C1", "C2"]}}}
    out = _section_population_anchoring(data)
    assert "Population Anchoring" in out
    assert "2020" in out


def test_section_population_anchoring_green_row():
    from saas.reporting.annual_report import _section_population_anchoring
    data = {"years": {"2020": {"avg_complaint_probability": 0.04,
                               "active_customer_ids": ["C1", "C2"]}}}
    out = _section_population_anchoring(data)
    assert "OK" in out


def test_section_population_anchoring_summary_line():
    from saas.reporting.annual_report import _section_population_anchoring
    data = {"years": {
        "2019": {"avg_complaint_probability": 0.04, "active_customer_ids": ["C1"]},
        "2020": {"avg_complaint_probability": 0.04, "active_customer_ids": ["C1"]},
    }}
    out = _section_population_anchoring(data)
    assert "2 of 2 years GREEN" in out


def test_section_population_anchoring_empty_data():
    from saas.reporting.annual_report import _section_population_anchoring
    assert _section_population_anchoring({}) == ""
    assert _section_population_anchoring({"years": {}}) == ""


def test_licence_health_uses_actual_complaint_rate():
    from saas.reporting.annual_report import _section_licence_health
    data = {
        "years": {"2020": {
            "avg_complaint_probability": 0.05,
            "active_customer_ids": ["C1", "C2", "C3", "C4", "C5"],
            "revenue_gbp": 200000.0,
            "bad_debt_gbp": 500.0,
            "treasury_end_gbp": 100000.0,
            "gross_gbp": 180000.0,
        }},
        "management_accounts": {},
    }
    out = _section_licence_health(data)
    assert "0.0/100 customers assumed" not in out
    assert "contact model" in out
