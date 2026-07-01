"""Phase AP: Segment Capital Efficiency section tests."""
import pytest
from saas.reporting.annual_report import _section_segment_capital_efficiency


def _make_data(segments_by_year):
    years = {}
    for yr, segs in segments_by_year.items():
        ss = {}
        for seg, triple in segs.items():
            gross, cap, net = triple
            ss[seg] = {"gross_gbp": gross, "capital_gbp": cap, "net_gbp": net}
        years[yr] = {"segment_split": ss}
    return {"years": years}


def test_empty_years_returns_empty():
    assert _section_segment_capital_efficiency({}) == ""
    assert _section_segment_capital_efficiency({"years": {}}) == ""


def test_header_present():
    data = _make_data({"2024": {"I&C electricity": (1000.0, 100.0, 500.0)}})
    assert "Segment Capital Efficiency" in _section_segment_capital_efficiency(data)


def test_segment_row_shown():
    data = _make_data({"2024": {"resi electricity": (50000.0, 500.0, 4000.0)}})
    assert "resi electricity" in _section_segment_capital_efficiency(data)


def test_roc_computed():
    data = _make_data({"2024": {"I&C electricity": (10000.0, 100.0, 2000.0)}})
    assert "20.0x" in _section_segment_capital_efficiency(data)


def test_strong_signal():
    data = _make_data({"2024": {"I&C electricity": (100000.0, 1000.0, 20000.0)}})
    assert "Strong" in _section_segment_capital_efficiency(data)


def test_moderate_signal():
    data = _make_data({"2024": {"SME electricity": (10000.0, 1000.0, 7000.0)}})
    assert "Moderate" in _section_segment_capital_efficiency(data)


def test_low_return_signal():
    data = _make_data({"2024": {"resi electricity": (5000.0, 1000.0, 3000.0)}})
    assert "Low return" in _section_segment_capital_efficiency(data)


def test_capital_destroyer_signal():
    data = _make_data({"2024": {"I&C gas": (50000.0, 10000.0, -5000.0)}})
    assert "CAPITAL DESTROYER" in _section_segment_capital_efficiency(data)


def test_multi_year_aggregation():
    data = _make_data({
        "2023": {"I&C electricity": (50000.0, 100.0, 1000.0)},
        "2024": {"I&C electricity": (50000.0, 100.0, 1000.0)},
    })
    assert "10.0x" in _section_segment_capital_efficiency(data)


def test_gas_finding_shown_when_negative():
    data = _make_data({"2024": {
        "I&C electricity": (100000.0, 1000.0, 20000.0),
        "I&C gas": (50000.0, 10000.0, -5000.0),
    }})
    assert "Gas Segment Finding" in _section_segment_capital_efficiency(data)


def test_gas_finding_absent_when_positive():
    data = _make_data({"2024": {
        "I&C electricity": (100000.0, 1000.0, 20000.0),
        "I&C gas": (50000.0, 10000.0, 5000.0),
    }})
    assert "Gas Segment Finding" not in _section_segment_capital_efficiency(data)


def test_multiple_segments_all_shown():
    data = _make_data({"2024": {
        "I&C electricity": (1000.0, 50.0, 500.0),
        "resi electricity": (500.0, 20.0, 100.0),
        "I&C gas": (200.0, 30.0, -50.0),
    }})
    result = _section_segment_capital_efficiency(data)
    assert "I&C electricity" in result
    assert "resi electricity" in result
    assert "I&C gas" in result


def test_zero_capital_gives_low_return():
    from saas.reporting.annual_report import _section_segment_capital_efficiency
    data = _make_data({"2024": {"resi electricity": (5000.0, 0.0, 1000.0)}})
    result = _section_segment_capital_efficiency(data)
    assert "Low return" in result


def test_negative_net_appears_in_table():
    from saas.reporting.annual_report import _section_segment_capital_efficiency
    data = _make_data({"2024": {"I&C gas": (50000.0, 5000.0, -200.0)}})
    result = _section_segment_capital_efficiency(data)
    assert "I&C gas" in result


def test_no_gas_finding_when_gas_cap_is_zero():
    from saas.reporting.annual_report import _section_segment_capital_efficiency
    data = _make_data({"2024": {"I&C gas": (50000.0, 0.0, -100.0)}})
    result = _section_segment_capital_efficiency(data)
    assert "Gas Segment Finding" not in result
