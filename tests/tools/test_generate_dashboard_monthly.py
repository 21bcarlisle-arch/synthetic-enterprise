import pytest
from tools.generate_dashboard_data import extract_monthly_ops
import statistics


def _data(**overrides):
    base = {
        "years": {
            "2022": {
                "bill_shock_events": [
                    {"customer_id": "C1", "period_end": "2022-01-31", "bill_shock_pct": 0.8},
                    {"customer_id": "C2", "period_end": "2022-01-31", "bill_shock_pct": 0.6},
                    {"customer_id": "C3", "period_end": "2022-02-28", "bill_shock_pct": 1.1},
                ],
                "committee_wake_ups": [
                    {"settlement_date": "2022-01-15", "treasury_gbp": 3000000},
                    {"settlement_date": "2022-02-15", "treasury_gbp": 3100000},
                ],
            },
            "2020": {
                "bill_shock_events": [],
                "committee_wake_ups": [],
            },
        },
        "retention_log": [
            {"customer_id": "C1", "event_date": "2022-03-01", "outcome": "retained"},
            {"customer_id": "C2", "event_date": "2022-03-01", "outcome": "churned"},
        ],
    }
    base.update(overrides)
    return base


def test_monthly_key_present():
    r = extract_monthly_ops(_data())
    assert "monthly" in r


def test_months_counted():
    r = extract_monthly_ops(_data())
    months = [m["month"] for m in r["monthly"]]
    assert "2022-01" in months
    assert "2022-02" in months
    assert "2022-03" in months


def test_shock_count():
    r = extract_monthly_ops(_data())
    jan = next(m for m in r["monthly"] if m["month"] == "2022-01")
    assert jan["shock_count"] == 2


def test_avg_shock_pct():
    r = extract_monthly_ops(_data())
    jan = next(m for m in r["monthly"] if m["month"] == "2022-01")
    assert abs(jan["avg_shock_pct"] - 70.0) < 0.1


def test_max_shock_pct():
    r = extract_monthly_ops(_data())
    jan = next(m for m in r["monthly"] if m["month"] == "2022-01")
    assert abs(jan["max_shock_pct"] - 80.0) < 0.1


def test_committee_interventions():
    r = extract_monthly_ops(_data())
    jan = next(m for m in r["monthly"] if m["month"] == "2022-01")
    assert jan["committee_interventions"] == 1


def test_retention_offers_and_retained():
    r = extract_monthly_ops(_data())
    mar = next(m for m in r["monthly"] if m["month"] == "2022-03")
    assert mar["retention_offers"] == 2
    assert mar["retained"] == 1


def test_is_crisis_flag():
    r = extract_monthly_ops(_data())
    jan = next(m for m in r["monthly"] if m["month"] == "2022-01")
    assert jan["is_crisis"] is True


def test_no_crisis_in_2020():
    r = extract_monthly_ops(_data())
    months_2020 = [m for m in r["monthly"] if m["month"].startswith("2020")]
    for m in months_2020:
        assert m["is_crisis"] is False


def test_empty_data():
    r = extract_monthly_ops({})
    assert r == {"monthly": [], "demand_estimation_annual": []}


def test_shock_count_zero_when_no_shocks():
    r = extract_monthly_ops(_data())
    mar = next(m for m in r["monthly"] if m["month"] == "2022-03")
    assert mar["shock_count"] == 0
    assert mar["avg_shock_pct"] == 0.0


def test_monthly_is_list():
    r = extract_monthly_ops(_data())
    assert isinstance(r["monthly"], list)


def test_monthly_row_has_month_key():
    r = extract_monthly_ops(_data())
    for row in r["monthly"]:
        assert "month" in row


def test_shock_count_is_int():
    r = extract_monthly_ops(_data())
    jan = next(m for m in r["monthly"] if m["month"] == "2022-01")
    assert isinstance(jan["shock_count"], int)


# -- demand_estimation_annual (Operations tab KPI expansion, 2026-07-10) --

def test_demand_estimation_annual_empty_when_no_log():
    r = extract_monthly_ops(_data())
    assert r["demand_estimation_annual"] == []


def test_demand_estimation_annual_aggregates_by_year():
    data = _data(demand_estimation_log=[
        {"term_start": "2022-03-01", "error_pct": 5.0, "source": "prior_billing"},
        {"term_start": "2022-06-01", "error_pct": -15.0, "source": "prior_billing"},
        {"term_start": "2023-01-01", "error_pct": 2.0, "source": "oracle_fallback"},
    ])
    r = extract_monthly_ops(data)
    y2022 = next(y for y in r["demand_estimation_annual"] if y["year"] == 2022)
    assert y2022["renewal_count"] == 2
    assert y2022["mean_abs_error_pct"] == pytest.approx((5.0 + 15.0) / 2, abs=0.05)
    assert y2022["max_abs_error_pct"] == 15.0
    assert y2022["prior_billing_count"] == 2
    assert y2022["oracle_fallback_count"] == 0

    y2023 = next(y for y in r["demand_estimation_annual"] if y["year"] == 2023)
    assert y2023["renewal_count"] == 1
    assert y2023["oracle_fallback_count"] == 1
    assert y2023["prior_billing_count"] == 0


def test_demand_estimation_annual_sorted_by_year():
    data = _data(demand_estimation_log=[
        {"term_start": "2023-01-01", "error_pct": 1.0, "source": "prior_billing"},
        {"term_start": "2020-01-01", "error_pct": 1.0, "source": "prior_billing"},
    ])
    r = extract_monthly_ops(data)
    years = [y["year"] for y in r["demand_estimation_annual"]]
    assert years == sorted(years)


def test_demand_estimation_annual_ignores_entries_without_term_start():
    data = _data(demand_estimation_log=[{"error_pct": 1.0, "source": "prior_billing"}])
    r = extract_monthly_ops(data)
    assert r["demand_estimation_annual"] == []
