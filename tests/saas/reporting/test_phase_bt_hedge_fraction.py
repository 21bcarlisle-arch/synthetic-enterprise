"""Phase BT: Portfolio Hedge Fraction Evolution section tests."""
import pytest
from saas.reporting.annual_report import _section_hedge_fraction_evolution


def _yr(hf_entries):
    return {"hedge_fractions": {cid: {"start_hf": v, "avg_hf": v} for cid, v in hf_entries.items()}}


def _data(year_hf):
    return {"years": {yr: _yr(hf) for yr, hf in year_hf.items()}}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_hedge_fraction_evolution({}) == ""
    assert _section_hedge_fraction_evolution({"years": {}}) == ""


# 2. No hedge_fractions in year → empty
def test_no_hf_data_empty():
    d = {"years": {"2022": {"hedge_fractions": {}}}}
    assert _section_hedge_fraction_evolution(d) == ""


# 3. Header present
def test_header_present():
    d = _data({"2022": {"C1": 0.95, "C2": 0.90}})
    assert "Portfolio Hedge Fraction Evolution" in _section_hedge_fraction_evolution(d)


# 4. Year row present
def test_year_row():
    d = _data({"2022": {"C1": 0.95, "C2": 0.90}})
    result = _section_hedge_fraction_evolution(d)
    assert "| 2022 |" in result


# 5. Portfolio avg correct (95% + 90%) / 2 = 92.5%
def test_portfolio_avg():
    d = _data({"2022": {"C1": 0.95, "C2": 0.90}})
    result = _section_hedge_fraction_evolution(d)
    assert "92.5%" in result


# 6. Naked count correct (hf < 5%)
def test_naked_count():
    d = _data({"2022": {"C1": 0.95, "C2": 0.00}})
    result = _section_hedge_fraction_evolution(d)
    # naked_count = 1
    assert "| 2022 |" in result
    row = [l for l in result.split("\n") if "| 2022 |" in l][0]
    assert "| 1 |" in row


# 7. No naked shows dash
def test_no_naked_dash():
    d = _data({"2022": {"C1": 0.95, "C2": 0.90}})
    result = _section_hedge_fraction_evolution(d)
    row = [l for l in result.split("\n") if "| 2022 |" in l][0]
    assert "—" in row


# 8. Lowest hedge fraction year flagged
def test_lowest_avg_year():
    d = _data({
        "2016": {"C1": 0.90, "C2": 0.88},
        "2024": {"C1": 0.80, "C2": 0.77},
    })
    result = _section_hedge_fraction_evolution(d)
    assert "Lowest portfolio hedge fraction: 2024" in result


# 9. First naked year flagged
def test_first_naked_year():
    d = _data({
        "2019": {"C1": 0.95, "C2": 0.00},
        "2016": {"C1": 0.90, "C2": 0.88},
    })
    result = _section_hedge_fraction_evolution(d)
    # 2016 has no naked accounts; 2019 has C2=0.00 naked => first naked in 2019
    assert "Naked positions first appear in 2019" in result


# 10. Regime-change blindness note present
def test_regime_change_note():
    d = _data({"2022": {"C1": 0.95}})
    result = _section_hedge_fraction_evolution(d)
    assert "regime-change blindness" in result.lower() or "Regime-change" in result


# 11. Min and Max HF correct
def test_min_max_hf():
    d = _data({"2022": {"C1": 0.97, "C2": 0.85, "C3": 0.00}})
    result = _section_hedge_fraction_evolution(d)
    assert "0.0%" in result  # min
    assert "97.0%" in result  # max


# 12. Multiple years sorted
def test_years_sorted():
    d = _data({
        "2018": {"C1": 0.90},
        "2016": {"C1": 0.92},
    })
    result = _section_hedge_fraction_evolution(d)
    pos_2016 = result.find("| 2016 |")
    pos_2018 = result.find("| 2018 |")
    assert pos_2016 < pos_2018


# 13. Lowest hedge fraction year noted
def test_lowest_hf_year_noted():
    d = {"years": {
        "2020": {"hedge_fractions": {"C1": {"avg_hf": 0.8}, "C2": {"avg_hf": 0.7}}},
        "2021": {"hedge_fractions": {"C1": {"avg_hf": 0.1}, "C2": {"avg_hf": 0.05}}},
    }}
    result = _section_hedge_fraction_evolution(d)
    assert "Lowest portfolio hedge fraction: 2021" in result


# 14. Naked positions label shown when avg_hf < 5%
def test_naked_positions_label():
    d = {"years": {"2022": {"hedge_fractions": {
        "C1": {"avg_hf": 0.02}, "C2": {"avg_hf": 0.01}
    }}}}
    result = _section_hedge_fraction_evolution(d)
    assert "Naked positions" in result or "Naked" in result


# 15. Regime-change blindness note in output
def test_regime_change_blindness_note():
    d = {"years": {"2022": {"hedge_fractions": {"C1": {"avg_hf": 0.4}}}}}
    result = _section_hedge_fraction_evolution(d)
    assert "Regime-change blindness" in result or "regime-change" in result.lower()
