import json
import pathlib
import pytest
from tools.generate_sim_data import _bm_monthly_aggregation


def _make_recs(months_data):
    records = []
    for (month, ssp, sbp, niv_vals) in months_data:
        for i, niv in enumerate(niv_vals):
            records.append({
                "settlementDate": month + "-01",
                "settlementPeriod": i + 1,
                "systemSellPrice": ssp,
                "systemBuyPrice": sbp,
                "netImbalanceVolume": niv,
            })
    return records


def test_bm_monthly_keys():
    recs = _make_recs([("2022-01", 200.0, 200.0, [-100.0, 50.0, -200.0, 80.0])])
    result = _bm_monthly_aggregation(recs)
    assert len(result) == 1
    row = result[0]
    for k in ("month", "mean_ssp", "mean_sbp", "spread_sbp_ssp", "max_ssp",
              "mean_niv_mwh", "short_pct", "is_crisis"):
        assert k in row, f"missing key: {k}"


def test_bm_short_pct_calculation():
    niv_vals = [-10.0, -20.0, 30.0, -5.0]
    recs = _make_recs([("2022-06", 100.0, 100.0, niv_vals)])
    result = _bm_monthly_aggregation(recs)
    assert result[0]["short_pct"] == 75.0


def test_bm_crisis_flag():
    recs = _make_recs([("2022-01", 200.0, 200.0, [0.0]),("2019-06", 40.0, 40.0, [0.0])])
    result = _bm_monthly_aggregation(recs)
    crisis_months = [r for r in result if r["is_crisis"]]
    non_crisis = [r for r in result if not r["is_crisis"]]
    assert len(crisis_months) == 1
    assert len(non_crisis) == 1


def test_bm_filters_out_of_range():
    recs = _make_recs([("2015-12", 30.0, 30.0, [0.0]), ("2016-01", 35.0, 35.0, [0.0])])
    result = _bm_monthly_aggregation(recs)
    months = [r["month"] for r in result]
    assert "2015-12" not in months
    assert "2016-01" in months


def test_bm_100pct_short():
    recs = _make_recs([("2022-01", 400.0, 400.0, [-100.0, -200.0, -50.0])])
    result = _bm_monthly_aggregation(recs)
    assert result[0]["short_pct"] == 100.0


def test_bm_0pct_short():
    recs = _make_recs([("2020-01", 50.0, 50.0, [10.0, 20.0, 30.0])])
    result = _bm_monthly_aggregation(recs)
    assert result[0]["short_pct"] == 0.0


def test_bm_mean_ssp():
    recs = _make_recs([("2022-03", 100.0, 100.0, [0.0]),("2022-03", 200.0, 200.0, [0.0])])
    result = _bm_monthly_aggregation(recs)
    assert result[0]["mean_ssp"] == 150.0


def test_bm_multi_month_ordering():
    recs = _make_recs([
        ("2020-03", 40.0, 40.0, [5.0]),
        ("2020-01", 35.0, 35.0, [-5.0]),
        ("2020-02", 38.0, 38.0, [0.0]),
    ])
    result = _bm_monthly_aggregation(recs)
    months = [r["month"] for r in result]
    assert months == sorted(months)


def test_bm_full_data_produces_114_months():
    ssp_path = pathlib.Path("sim/cache/elexon_ssp_full.json")
    if not ssp_path.exists():
        pytest.skip("SSP cache not present")
    import json
    recs = json.loads(ssp_path.read_text())
    result = _bm_monthly_aggregation(recs)
    assert len(result) == 114


def test_bm_2022_high_short_pct():
    ssp_path = pathlib.Path("sim/cache/elexon_ssp_full.json")
    if not ssp_path.exists():
        pytest.skip("SSP cache not present")
    import json
    recs = json.loads(ssp_path.read_text())
    result = _bm_monthly_aggregation(recs)
    months_2022 = [r for r in result if r["month"].startswith("2022")]
    avg_short_2022 = sum(m["short_pct"] for m in months_2022) / len(months_2022)
    months_2018 = [r for r in result if r["month"].startswith("2018")]
    avg_short_2018 = sum(m["short_pct"] for m in months_2018) / len(months_2018)
    assert avg_short_2022 > avg_short_2018 or avg_short_2022 > 40


def test_bm_spread_is_sbp_minus_ssp():
    recs = _make_recs([("2020-01", 50.0, 60.0, [0.0])])
    result = _bm_monthly_aggregation(recs)
    assert abs(result[0]["spread_sbp_ssp"] - 10.0) < 0.01


def test_bm_empty_returns_empty_list():
    result = _bm_monthly_aggregation([])
    assert result == []


def test_bm_max_ssp_is_correct():
    recs = _make_recs([("2022-06", 100.0, 100.0, [0.0]),("2022-06", 300.0, 300.0, [0.0])])
    result = _bm_monthly_aggregation(recs)
    assert result[0]["max_ssp"] == 300.0
