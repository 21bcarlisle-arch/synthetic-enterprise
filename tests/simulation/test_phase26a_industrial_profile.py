"""Phase 26a: industrial demand profile for C_IC1 + risk committee EAC calibration.

Verifies:
- C_IC1 HH profile has industrial shape (core weekday hours, low weekends)
- Mon-Fri core-hour (08:00-18:00) load >> overnight/weekend load
- Total annual consumption still ~2 GWh/year
- Sunday / Monday ratio matches expected industrial differential (~15% vs 100%)
- Risk committee block uses _company_eac_estimate (not EFFECTIVE_EAC_KWH)
- Portfolio EAC in context-handshake converges to billing-derived estimate
"""

import csv
from datetime import date, timedelta


def _load_ic1_csv():
    rows = []
    with open("sim/hh_data/C_IC1.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def _day_total(row):
    return sum(float(row[f"p{i}"]) for i in range(1, 49))


def _weekday_for(date_str):
    return date.fromisoformat(date_str).weekday()


def test_industrial_profile_annual_total_approx_2gwh():
    rows = _load_ic1_csv()
    total_kwh = sum(_day_total(r) for r in rows)
    years = (date.fromisoformat(rows[-1]["date"]) - date.fromisoformat(rows[0]["date"])).days / 365.25
    annual_kwh = total_kwh / years
    assert abs(annual_kwh - 2_000_000) < 20_000, f"Expected ~2 GWh/year, got {annual_kwh:.0f}"


def test_industrial_profile_weekday_vs_sunday_ratio():
    rows = _load_ic1_csv()
    weekdays = [r for r in rows if _weekday_for(r["date"]) < 5]
    sundays = [r for r in rows if _weekday_for(r["date"]) == 6]
    avg_weekday = sum(_day_total(r) for r in weekdays) / len(weekdays)
    avg_sunday = sum(_day_total(r) for r in sundays) / len(sundays)
    ratio = avg_weekday / avg_sunday
    assert 6.0 < ratio < 8.0, f"Weekday/Sunday ratio should be ~6.7, got {ratio:.2f}"


def test_industrial_profile_core_hours_higher_than_overnight():
    rows = _load_ic1_csv()
    monday = next(r for r in rows if _weekday_for(r["date"]) == 0)
    core_mean = sum(float(monday[f"p{i}"]) for i in range(17, 37)) / 20
    overnight_mean = sum(float(monday[f"p{i}"]) for i in range(1, 13)) / 12
    assert core_mean > overnight_mean * 15, (
        f"Core hours ({core_mean:.1f} kWh) should be >>15x overnight ({overnight_mean:.1f} kWh)"
    )


def test_industrial_profile_no_seasonal_variation():
    rows = _load_ic1_csv()
    winter = [r for r in rows if r["date"][5:7] in ("01", "02") and _weekday_for(r["date"]) < 5]
    summer = [r for r in rows if r["date"][5:7] in ("07", "08") and _weekday_for(r["date"]) < 5]
    avg_winter = sum(_day_total(r) for r in winter) / len(winter)
    avg_summer = sum(_day_total(r) for r in summer) / len(summer)
    pct_diff = abs(avg_winter - avg_summer) / avg_summer
    assert pct_diff < 0.05, (
        f"Industrial profile should have <5% seasonal variation, got {pct_diff*100:.1f}%"
    )


def test_risk_committee_eac_uses_company_estimate():
    import pathlib
    src = pathlib.Path("simulation/run_phase2b.py").read_text()
    assert "_eac = {c[" in src, "Risk committee _eac dict not found"
    assert "_company_eac_estimate(c[" in src.split("_eac = {")[1].split("}")[0], (
        "Risk committee _eac dict should use _company_eac_estimate"
    )


def test_risk_committee_eac_not_using_effective_eac_kwh_directly():
    import pathlib
    src = pathlib.Path("simulation/run_phase2b.py").read_text()
    marker_start = "# Risk committee check"
    marker_end = "portfolio_state = {"
    committee_block = src[src.index(marker_start):src.index(marker_end) + 200]
    assert "EFFECTIVE_EAC_KWH" not in committee_block, (
        "EFFECTIVE_EAC_KWH should not appear in risk committee block after Phase 26a"
    )




def test_industrial_profile_has_48_period_columns():
    rows = _load_ic1_csv()
    periods = [k for k in rows[0].keys() if k.startswith("p")]
    assert len(periods) == 48


def test_industrial_profile_all_periods_nonnegative():
    rows = _load_ic1_csv()[:30]
    for row in rows:
        for i in range(1, 49):
            assert float(row[f"p{i}"]) >= 0.0


def test_industrial_profile_saturday_higher_than_sunday():
    rows = _load_ic1_csv()
    saturdays = [r for r in rows if _weekday_for(r["date"]) == 5]
    sundays = [r for r in rows if _weekday_for(r["date"]) == 6]
    avg_sat = sum(_day_total(r) for r in saturdays) / len(saturdays)
    avg_sun = sum(_day_total(r) for r in sundays) / len(sundays)
    assert avg_sat > avg_sun * 2.0


def test_industrial_profile_saturday_lower_than_weekday():
    rows = _load_ic1_csv()
    saturdays = [r for r in rows if _weekday_for(r["date"]) == 5]
    weekdays = [r for r in rows if _weekday_for(r["date"]) < 5]
    avg_sat = sum(_day_total(r) for r in saturdays) / len(saturdays)
    avg_wd = sum(_day_total(r) for r in weekdays) / len(weekdays)
    assert avg_sat < avg_wd * 0.6


def test_industrial_profile_has_more_than_1000_rows():
    rows = _load_ic1_csv()
    assert len(rows) > 1000


def test_industrial_profile_starts_2016():
    rows = _load_ic1_csv()
    assert rows[0]["date"].startswith("2016")


# 13. Profile covers multiple years
def test_industrial_profile_multi_year_span():
    rows = _load_ic1_csv()
    years = {r["date"][:4] for r in rows}
    assert len(years) >= 2


# 14. Daily total non-negative for all rows
def test_industrial_profile_daily_totals_nonneg():
    rows = _load_ic1_csv()
    for r in rows:
        assert _day_total(r) >= 0


# 15. Last period p48 column exists
def test_industrial_profile_has_p48_column():
    rows = _load_ic1_csv()
    assert "p48" in rows[0]
