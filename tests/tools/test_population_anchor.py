"""Tests for tools/population_anchor.py (Phase PR -- improved crisis churn direction + long-run comparison)."""
import json
from pathlib import Path

from tools.population_anchor import (
    generate, _churn_by_year, _bad_debt_check, _crisis_churn_direction,
    _multiplier_alignment, _long_run_comparison,
    OFGEM_SWITCHING_RATE, CALIBRATED_MULTIPLIER,
)


def _ev(cid, yr, et):
    return {"customer_id": cid, "event_date": "%s-06-30" % yr, "event_type": et}


def _cby(rates_and_counts):
    """Build churn_by_year dict from {year: (sim_churn_rate, renewals, churns)}."""
    result = {}
    for yr, (rate, r, c) in rates_and_counts.items():
        result[yr] = {
            "sim_churn_rate": rate,
            "renewals": r,
            "churns": c,
            "ofgem_benchmark": OFGEM_SWITCHING_RATE.get(yr),
            "calibrated_multiplier": CALIBRATED_MULTIPLIER.get(yr),
        }
    return result


def _make_run(events=None, years=None):
    return {
        "customer_events": events or [],
        "years": years or {},
    }


def test_churn_by_year_basic():
    events = [
        _ev("C1", 2021, "renewed"),
        _ev("C2", 2021, "churned"),
        _ev("C3", 2022, "renewed"),
    ]
    result = _churn_by_year(events)
    assert result[2021]["renewals"] == 1
    assert result[2021]["churns"] == 1
    assert abs(result[2021]["sim_churn_rate"] - 0.5) < 0.001
    assert result[2022]["churns"] == 0


def test_churn_by_year_empty():
    assert _churn_by_year([]) == {}


def test_churn_by_year_has_ofgem_benchmark():
    events = [_ev("C1", 2022, "renewed"), _ev("C2", 2022, "churned")]
    result = _churn_by_year(events)
    assert result[2022]["ofgem_benchmark"] == OFGEM_SWITCHING_RATE[2022]


def test_bad_debt_within_band_is_green():
    # WITHIN the plausible 0.5-2.5% band = realistic bad debt -> GREEN (the
    # World-door RAG is divergence magnitude, R12; zero divergence = green).
    years = {"2020": {"bad_debt_gbp": 5000, "revenue_gbp": 500000}}  # 1.0%
    findings = _bad_debt_check(years)
    assert findings[0]["rag"] == "GREEN"
    assert findings[0]["bad_debt_rate"] == 1.0


def test_bad_debt_below_floor_is_amber():
    # Implausibly LOW bad debt (below the 0.5% floor) is a FIDELITY divergence,
    # not a triumph -- no real supplier runs ~0% write-offs, so it must flag
    # AMBER, never read GREEN (director-caught on /world/, 2026-07-13).
    low = _bad_debt_check({"2020": {"bad_debt_gbp": 1000, "revenue_gbp": 500000}})  # 0.2%
    assert low[0]["rag"] == "AMBER"
    assert low[0]["bad_debt_rate"] == 0.2
    # the exact reported case: 0.0% bad debt (sim under-models write-offs)
    zero = _bad_debt_check({"2020": {"bad_debt_gbp": 0.0, "revenue_gbp": 500000}})
    assert zero[0]["rag"] == "AMBER"


def test_bad_debt_red_non_crisis():
    years = {"2020": {"bad_debt_gbp": 15000, "revenue_gbp": 500000}}
    findings = _bad_debt_check(years)
    assert findings[0]["rag"] == "RED"


def test_bad_debt_crisis_year_higher_threshold():
    years = {"2022": {"bad_debt_gbp": 15000, "revenue_gbp": 500000}}
    findings = _bad_debt_check(years)
    assert findings[0]["rag"] in ("AMBER", "GREEN")


def test_crisis_direction_no_divergence():
    churn = _cby({
        2019: (0.10, 5, 1), 2020: (0.08, 5, 0), 2021: (0.04, 5, 0),
        2022: (0.04, 5, 0), 2023: (0.03, 5, 0),
    })
    result = _crisis_churn_direction(churn)
    assert not result["crisis_divergence_flag"]


def test_crisis_direction_with_divergence():
    # Crisis window avg much higher than pre-crisis AND absolute 2022 >> 4x Ofgem
    churn = _cby({
        2019: (0.05, 5, 0), 2020: (0.05, 5, 0), 2021: (0.03, 5, 0),
        2022: (0.50, 5, 2), 2023: (0.40, 5, 2),
    })
    result = _crisis_churn_direction(churn)
    assert result["crisis_divergence_flag"]


def test_crisis_direction_insufficient_data():
    churn = _cby({
        2020: (0.10, 2, 0), 2021: (0.05, 2, 0),
        2022: (0.50, 2, 1), 2023: (0.40, 2, 1),
    })
    result = _crisis_churn_direction(churn)
    assert result["insufficient_data"] is True
    assert not result["crisis_divergence_flag"]


def test_crisis_direction_has_3yr_rolling_fields():
    churn = _cby({
        2019: (0.10, 5, 1), 2020: (0.08, 5, 0),
        2021: (0.05, 5, 0), 2022: (0.22, 5, 2), 2023: (0.00, 5, 0),
    })
    result = _crisis_churn_direction(churn)
    assert "pre_crisis_avg_pct" in result
    assert "crisis_avg_pct" in result
    assert "2022_ratio_vs_ofgem" in result


def test_long_run_comparison_low_ratio_green():
    # SIM 6% vs Ofgem 13% avg -> ratio 0.47 -> GREEN
    churn = _cby({
        2016: (0.00, 5, 0), 2017: (0.00, 5, 0), 2018: (0.00, 5, 0),
        2019: (0.00, 5, 0), 2020: (0.20, 5, 2), 2021: (0.00, 5, 0),
        2022: (0.22, 5, 2), 2023: (0.00, 5, 0), 2024: (0.22, 5, 2), 2025: (0.00, 5, 0),
    })
    result = _long_run_comparison(churn)
    assert result["rag"] == "GREEN"
    assert result["ratio"] < 1.0


def test_long_run_comparison_high_ratio_red():
    # SIM 45% vs Ofgem 13% avg -> ratio ~3.3 -> AMBER or RED
    churn = _cby({
        2016: (0.50, 5, 2), 2017: (0.50, 5, 2), 2018: (0.40, 5, 2),
        2019: (0.40, 5, 2), 2020: (0.50, 5, 2), 2021: (0.40, 5, 2),
        2022: (0.45, 5, 2), 2023: (0.40, 5, 2), 2024: (0.40, 5, 2), 2025: (0.45, 5, 2),
    })
    result = _long_run_comparison(churn)
    assert result["rag"] in ("AMBER", "RED")


def test_long_run_has_note():
    churn = _cby({2020: (0.10, 5, 1), 2021: (0.05, 5, 0), 2022: (0.04, 5, 0)})
    result = _long_run_comparison(churn)
    assert "note" in result


def test_multiplier_alignment_all_tracking():
    churn = _cby({2021: (0.09, 5, 1), 2022: (0.04, 5, 0)})
    findings = _multiplier_alignment(churn)
    assert any(f["year_transition"] == "2021->2022" and f["rag"] == "GREEN" for f in findings)


def test_multiplier_alignment_diverges():
    churn = _cby({2021: (0.02, 5, 0), 2022: (0.30, 5, 2)})
    findings = _multiplier_alignment(churn)
    assert any(f["year_transition"] == "2021->2022" and f["rag"] == "AMBER" for f in findings)


def test_ofgem_switching_rates_have_crisis_collapse():
    assert OFGEM_SWITCHING_RATE[2022] < OFGEM_SWITCHING_RATE[2020]
    assert OFGEM_SWITCHING_RATE[2022] < 0.06


def test_calibrated_multiplier_crisis_year_low():
    assert CALIBRATED_MULTIPLIER[2022] < CALIBRATED_MULTIPLIER[2016] * 0.5


def test_generate_output_structure(tmp_path):
    events = [
        _ev("C1", 2020, "renewed"), _ev("C2", 2020, "churned"),
        _ev("C1", 2021, "renewed"), _ev("C2", 2021, "renewed"),
        _ev("C1", 2022, "renewed"), _ev("C2", 2022, "renewed"),
    ]
    years = {"2020": {"bad_debt_gbp": 1000, "revenue_gbp": 200000}}
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_make_run(events, years)))
    out = tmp_path / "anchor.json"
    result = generate(rj, out)
    assert "overall_rag" in result
    assert "crisis_churn_direction" in result
    assert "bad_debt_vs_benchmark" in result
    assert "multiplier_alignment" in result
    assert "churn_by_year" in result
    assert "long_run_comparison" in result


def test_generate_writes_file(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_make_run([_ev("C1", 2022, "renewed")])))
    out = tmp_path / "anchor.json"
    generate(rj, out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert "overall_rag" in data


def test_generate_empty_events(tmp_path):
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_make_run([])))
    out = tmp_path / "anchor.json"
    result = generate(rj, out)
    assert result["overall_rag"] in ("GREEN", "AMBER", "RED")


def test_crisis_note_in_result():
    churn = _cby({
        2019: (0.1, 5, 1), 2020: (0.08, 5, 0), 2021: (0.05, 5, 0),
        2022: (0.04, 5, 0), 2023: (0.03, 5, 0),
    })
    result = _crisis_churn_direction(churn)
    assert "note" in result


def test_churn_by_year_includes_ofgem_multiplier():
    events = [_ev("C1", 2016, "renewed"), _ev("C2", 2016, "churned")]
    result = _churn_by_year(events)
    assert result[2016]["calibrated_multiplier"] == CALIBRATED_MULTIPLIER[2016]
