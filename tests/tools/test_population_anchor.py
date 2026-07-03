"""Tests for tools/population_anchor.py (Phase PQ)."""
import json
from pathlib import Path

from tools.population_anchor import (
    generate, _churn_by_year, _bad_debt_check, _crisis_churn_direction,
    _multiplier_alignment, OFGEM_SWITCHING_RATE, CALIBRATED_MULTIPLIER
)


def _ev(cid, yr, et):
    return {"customer_id": cid, "event_date": "%s-06-30" % yr, "event_type": et}


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


def test_bad_debt_green():
    years = {"2020": {"bad_debt_gbp": 1000, "revenue_gbp": 500000}}
    findings = _bad_debt_check(years)
    assert findings[0]["rag"] == "GREEN"
    assert findings[0]["bad_debt_rate"] == 0.2


def test_bad_debt_amber():
    years = {"2020": {"bad_debt_gbp": 5000, "revenue_gbp": 500000}}
    findings = _bad_debt_check(years)
    assert findings[0]["rag"] == "AMBER"


def test_bad_debt_red_non_crisis():
    years = {"2020": {"bad_debt_gbp": 15000, "revenue_gbp": 500000}}
    findings = _bad_debt_check(years)
    assert findings[0]["rag"] == "RED"


def test_bad_debt_crisis_year_higher_threshold():
    # 3% bad debt in 2022 crisis -- within 4% crisis ceiling, should be AMBER not RED
    years = {"2022": {"bad_debt_gbp": 15000, "revenue_gbp": 500000}}
    findings = _bad_debt_check(years)
    assert findings[0]["rag"] in ("AMBER", "GREEN")


def test_crisis_direction_no_divergence():
    churn = {
        2020: {"sim_churn_rate": 0.10},
        2021: {"sim_churn_rate": 0.05},
        2022: {"sim_churn_rate": 0.04},
    }
    result = _crisis_churn_direction(churn)
    assert not result["crisis_divergence_flag"]


def test_crisis_direction_with_divergence():
    # 2022 churn = 0.50, 2020 = 0.10: normalised 2022 propensity is very high
    churn = {
        2020: {"sim_churn_rate": 0.10},
        2021: {"sim_churn_rate": 0.02},
        2022: {"sim_churn_rate": 0.50},
    }
    result = _crisis_churn_direction(churn)
    assert result["crisis_divergence_flag"]


def test_multiplier_alignment_all_tracking():
    # Both Ofgem and SIM going down 2021->2022: GREEN
    churn = {
        2021: {"sim_churn_rate": 0.09},
        2022: {"sim_churn_rate": 0.04},
    }
    findings = _multiplier_alignment(churn)
    assert any(f["year_transition"] == "2021->2022" and f["rag"] == "GREEN" for f in findings)


def test_multiplier_alignment_diverges():
    # Ofgem going down but SIM going up: AMBER
    churn = {
        2021: {"sim_churn_rate": 0.02},
        2022: {"sim_churn_rate": 0.30},
    }
    findings = _multiplier_alignment(churn)
    assert any(f["year_transition"] == "2021->2022" and f["rag"] == "AMBER" for f in findings)


def test_ofgem_switching_rates_have_crisis_collapse():
    # Ofgem 2022 switching rate should be much lower than 2020
    assert OFGEM_SWITCHING_RATE[2022] < OFGEM_SWITCHING_RATE[2020]
    assert OFGEM_SWITCHING_RATE[2022] < 0.06  # 6% ceiling


def test_calibrated_multiplier_crisis_year_low():
    # 2022 multiplier should be much lower than 2016
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
    churn = {2020: {"sim_churn_rate": 0.1}, 2021: {"sim_churn_rate": 0.0}, 2022: {"sim_churn_rate": 0.05}}
    result = _crisis_churn_direction(churn)
    assert "note" in result


def test_churn_by_year_includes_ofgem_multiplier():
    events = [_ev("C1", 2016, "renewed"), _ev("C2", 2016, "churned")]
    result = _churn_by_year(events)
    assert result[2016]["calibrated_multiplier"] == CALIBRATED_MULTIPLIER[2016]
