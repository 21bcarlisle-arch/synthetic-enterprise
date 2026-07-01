"""Tests for Phase 38a scenario comparison runner — unit-testable helpers only."""
from simulation.scenario_comparison import extract_scenario_kpis, format_comparison_table


def _make_run_result(
    scenario_name: str = "central_2027",
    years: dict | None = None,
    churn_count: int = 2,
    retention_count: int = 1,
) -> dict:
    if years is None:
        years = {
            "2026": {"net_margin_gbp": 500.0, "treasury_end_gbp": 10000.0, "active_customer_ids": ["C1", "C2"]},
            "2027": {"net_margin_gbp": -200.0, "treasury_end_gbp": 9800.0, "active_customer_ids": ["C1"]},
        }
    events = [{"event_type": "churned"}] * churn_count + [{"event_type": "renewed"}]
    retention_log = [{"foo": "bar"}] * retention_count
    return {
        "scenario_name": scenario_name,
        "years": years,
        "customer_events": events,
        "retention_log": retention_log,
    }


def test_extract_kpis_scenario_name():
    result = _make_run_result("central_2027")
    kpis = extract_scenario_kpis(result, "central_2027")
    assert kpis["scenario_name"] == "central_2027"


def test_extract_kpis_total_net_margin():
    result = _make_run_result(years={
        "2026": {"net_margin_gbp": 500.0, "active_customer_ids": ["C1"]},
        "2027": {"net_margin_gbp": -200.0, "active_customer_ids": []},
    })
    kpis = extract_scenario_kpis(result, "central_2027")
    assert abs(kpis["total_net_margin_gbp"] - 300.0) < 0.01


def test_extract_kpis_churn_count():
    result = _make_run_result(churn_count=3)
    kpis = extract_scenario_kpis(result, "central_2027")
    assert kpis["total_churn"] == 3


def test_extract_kpis_retention_events():
    result = _make_run_result(retention_count=5)
    kpis = extract_scenario_kpis(result, "central_2027")
    assert kpis["retention_events"] == 5


def test_extract_kpis_years_summary_keys():
    result = _make_run_result()
    kpis = extract_scenario_kpis(result, "central_2027")
    assert "2026" in kpis["years_summary"]
    assert "2027" in kpis["years_summary"]


def test_extract_kpis_final_treasury():
    result = _make_run_result(years={
        "2026": {"net_margin_gbp": 100.0, "treasury_end_gbp": 9000.0, "active_customer_ids": []},
        "2027": {"net_margin_gbp": 200.0, "treasury_end_gbp": 12345.0, "active_customer_ids": []},
    })
    kpis = extract_scenario_kpis(result, "s")
    assert kpis["final_treasury_gbp"] == 12345.0


def test_extract_kpis_empty_result():
    kpis = extract_scenario_kpis({}, "empty")
    assert kpis["total_net_margin_gbp"] == 0.0
    assert kpis["total_churn"] == 0
    assert kpis["retention_events"] == 0


def test_format_comparison_table_empty():
    assert format_comparison_table([]) == ""


def test_format_comparison_table_has_scenario_names():
    r1 = _make_run_result("central_2027")
    r2 = _make_run_result("baseline_2025")
    comp = [extract_scenario_kpis(r1, "central_2027"), extract_scenario_kpis(r2, "baseline_2025")]
    table = format_comparison_table(comp)
    assert "central_2027" in table
    assert "baseline_2025" in table


def test_format_comparison_table_has_year_rows():
    r1 = _make_run_result("central_2027")
    comp = [extract_scenario_kpis(r1, "central_2027")]
    table = format_comparison_table(comp)
    assert "2026" in table
    assert "2027" in table


def test_format_comparison_table_markdown_headers():
    r1 = _make_run_result("scenario_a")
    comp = [extract_scenario_kpis(r1, "scenario_a")]
    table = format_comparison_table(comp)
    assert "| Scenario |" in table or "| Year |" in table


def test_format_comparison_table_net_margin_sign():
    r1 = _make_run_result("pos_scenario", years={
        "2026": {"net_margin_gbp": 1234.0, "active_customer_ids": []},
    })
    r2 = _make_run_result("neg_scenario", years={
        "2026": {"net_margin_gbp": -567.0, "active_customer_ids": []},
    })
    comp = [extract_scenario_kpis(r1, "pos_scenario"), extract_scenario_kpis(r2, "neg_scenario")]
    table = format_comparison_table(comp)
    assert "£+1,234" in table or "£1,234" in table
    assert "£-567" in table


def test_extract_kpis_final_treasury_none_no_years():
    result = {"scenario_name": "x", "years": {}, "customer_events": [], "retention_log": []}
    kpis = extract_scenario_kpis(result, "x")
    assert kpis["final_treasury_gbp"] is None


def test_format_comparison_table_mentions_margin():
    r1 = _make_run_result("test_scenario")
    comp = [extract_scenario_kpis(r1, "test_scenario")]
    table = format_comparison_table(comp)
    assert "net" in table.lower() or "margin" in table.lower()


def test_extract_kpis_years_summary_active_customer_count():
    result = _make_run_result(years={
        "2026": {"net_margin_gbp": 100.0, "active_customer_ids": ["C1", "C2"]},
    })
    kpis = extract_scenario_kpis(result, "x")
    assert kpis["years_summary"]["2026"]["active_customers"] == 2
