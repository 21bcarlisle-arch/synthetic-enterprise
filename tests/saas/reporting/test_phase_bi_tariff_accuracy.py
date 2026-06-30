"""Phase BI: Tariff Estimation Accuracy section tests."""
import pytest
from saas.reporting.annual_report import _section_tariff_estimation_accuracy


def _data(by_year: dict) -> dict:
    return {"company_divergence": {"tariff_error_by_year": by_year}}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_tariff_estimation_accuracy({}) == ""
    assert _section_tariff_estimation_accuracy({"company_divergence": {}}) == ""
    assert _section_tariff_estimation_accuracy({"company_divergence": {"tariff_error_by_year": {}}}) == ""


# 2. Header present with data
def test_header_present():
    d = _data({"2022": {"n": 10, "mean_abs_error_pct": 0.12, "max_abs_error_pct": 0.30}})
    assert "Tariff Estimation Accuracy" in _section_tariff_estimation_accuracy(d)


# 3. GOOD flag when mean < 10%
def test_good_accuracy_flag():
    d = _data({"2022": {"n": 10, "mean_abs_error_pct": 0.09, "max_abs_error_pct": 0.20}})
    assert "GOOD" in _section_tariff_estimation_accuracy(d)


# 4. MODERATE flag when 10-15%
def test_moderate_accuracy_flag():
    d = _data({"2022": {"n": 10, "mean_abs_error_pct": 0.12, "max_abs_error_pct": 0.25}})
    assert "MODERATE" in _section_tariff_estimation_accuracy(d)


# 5. POOR flag when >= 15%
def test_poor_accuracy_flag():
    d = _data({"2022": {"n": 10, "mean_abs_error_pct": 0.18, "max_abs_error_pct": 0.40}})
    assert "POOR" in _section_tariff_estimation_accuracy(d)


# 6. Best accuracy year shown
def test_best_accuracy_year():
    d = _data({
        "2021": {"n": 10, "mean_abs_error_pct": 0.15, "max_abs_error_pct": 0.35},
        "2022": {"n": 10, "mean_abs_error_pct": 0.09, "max_abs_error_pct": 0.20},
        "2023": {"n": 10, "mean_abs_error_pct": 0.20, "max_abs_error_pct": 0.45},
    })
    result = _section_tariff_estimation_accuracy(d)
    assert "Best accuracy year" in result
    assert "2022" in result


# 7. Worst accuracy year shown
def test_worst_accuracy_year():
    d = _data({
        "2021": {"n": 10, "mean_abs_error_pct": 0.15, "max_abs_error_pct": 0.35},
        "2022": {"n": 10, "mean_abs_error_pct": 0.09, "max_abs_error_pct": 0.20},
        "2023": {"n": 10, "mean_abs_error_pct": 0.20, "max_abs_error_pct": 0.45},
    })
    result = _section_tariff_estimation_accuracy(d)
    assert "Worst accuracy year" in result
    assert "2023" in result


# 8. n<5 rows excluded from best/worst
def test_small_n_excluded_from_summary():
    d = _data({
        "2024": {"n": 3, "mean_abs_error_pct": 0.02, "max_abs_error_pct": 0.05},  # n=3 excluded
        "2023": {"n": 10, "mean_abs_error_pct": 0.15, "max_abs_error_pct": 0.35},
        "2022": {"n": 10, "mean_abs_error_pct": 0.20, "max_abs_error_pct": 0.45},
    })
    result = _section_tariff_estimation_accuracy(d)
    # Best should be 2023 (2024 excluded due to n<5)
    assert "Best accuracy year (n≥5): 2023" in result


# 9. Error pct formatted as percentage
def test_percentage_format():
    d = _data({"2022": {"n": 10, "mean_abs_error_pct": 0.1216, "max_abs_error_pct": 0.2742}})
    result = _section_tariff_estimation_accuracy(d)
    assert "12.2%" in result
    assert "27.4%" in result


# 10. Epistemic blindfold note present
def test_epistemic_note():
    d = _data({"2022": {"n": 10, "mean_abs_error_pct": 0.12, "max_abs_error_pct": 0.30}})
    result = _section_tariff_estimation_accuracy(d)
    assert "epistemic" in result.lower() or "information gap" in result.lower()


# 11. Observation count in table
def test_observation_count():
    d = _data({"2022": {"n": 17, "mean_abs_error_pct": 0.10, "max_abs_error_pct": 0.23}})
    result = _section_tariff_estimation_accuracy(d)
    assert "| 17 |" in result


# 12. Multiple years sorted by year
def test_sorted_years():
    d = _data({
        "2023": {"n": 10, "mean_abs_error_pct": 0.15, "max_abs_error_pct": 0.30},
        "2021": {"n": 10, "mean_abs_error_pct": 0.12, "max_abs_error_pct": 0.25},
        "2022": {"n": 10, "mean_abs_error_pct": 0.10, "max_abs_error_pct": 0.20},
    })
    result = _section_tariff_estimation_accuracy(d)
    pos_2021 = result.find("| 2021 |")
    pos_2022 = result.find("| 2022 |")
    pos_2023 = result.find("| 2023 |")
    assert pos_2021 < pos_2022 < pos_2023
