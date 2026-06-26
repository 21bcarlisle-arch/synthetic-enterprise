import pytest
from company.risk.var_monitor import VaRMonitorBook, VaRBreachLevel, VaRObservation


def _book(amber=50_000, red=150_000):
    return VaRMonitorBook(amber_limit_gbp=amber, red_limit_gbp=red)


def test_record_observation():
    book = _book()
    obs = book.record_observation("2022-01-15", 60_000.0, 90_000.0, 3_000_000.0)
    assert obs.current_var_gbp == 60_000.0
    assert obs.observation_date == "2022-01-15"


def test_var_as_pct_treasury():
    obs = VaRObservation(
        observation_date="2022-01-15",
        current_var_gbp=300_000.0,
        stressed_var_gbp=400_000.0,
        treasury_gbp=3_000_000.0,
    )
    assert abs(obs.var_as_pct_treasury - 10.0) < 0.01


def test_stress_uplift_pct():
    obs = VaRObservation(
        observation_date="2022-01-15",
        current_var_gbp=100_000.0,
        stressed_var_gbp=150_000.0,
        treasury_gbp=3_000_000.0,
    )
    assert abs(obs.stress_uplift_pct - 50.0) < 0.01


def test_breach_level_within():
    book = _book()
    assert book.breach_level(30_000.0) == VaRBreachLevel.WITHIN_LIMIT


def test_breach_level_amber():
    book = _book()
    assert book.breach_level(80_000.0) == VaRBreachLevel.AMBER


def test_breach_level_red():
    book = _book()
    assert book.breach_level(200_000.0) == VaRBreachLevel.RED


def test_observations_for_year():
    book = _book()
    book.record_observation("2022-01-15", 60_000.0, 90_000.0, 3_000_000.0)
    book.record_observation("2022-06-15", 45_000.0, 70_000.0, 3_100_000.0)
    book.record_observation("2021-12-15", 30_000.0, 50_000.0, 2_900_000.0)
    assert len(book.observations_for_year(2022)) == 2


def test_breach_count():
    book = _book(amber=50_000, red=150_000)
    book.record_observation("2022-01-15", 60_000.0, 90_000.0, 3_000_000.0)
    book.record_observation("2022-06-15", 200_000.0, 300_000.0, 2_500_000.0)
    book.record_observation("2022-09-15", 30_000.0, 50_000.0, 3_000_000.0)
    assert book.breach_count(VaRBreachLevel.AMBER, 2022) == 1
    assert book.breach_count(VaRBreachLevel.RED, 2022) == 1


def test_peak_var():
    book = _book()
    book.record_observation("2022-01-15", 60_000.0, 90_000.0, 3_000_000.0)
    book.record_observation("2022-06-15", 200_000.0, 300_000.0, 2_500_000.0)
    pk = book.peak_var(2022)
    assert pk is not None
    assert pk.current_var_gbp == 200_000.0


def test_mean_var():
    book = _book()
    book.record_observation("2022-01-15", 60_000.0, 90_000.0, 3_000_000.0)
    book.record_observation("2022-06-15", 40_000.0, 70_000.0, 3_000_000.0)
    assert abs(book.mean_var_gbp(2022) - 50_000.0) < 0.01


def test_var_summary_keys():
    book = _book()
    book.record_observation("2022-01-15", 60_000.0, 90_000.0, 3_000_000.0)
    s = book.var_summary(2022)
    for k in ("observations", "mean_var_gbp", "peak_var_gbp", "peak_date",
               "amber_breaches", "red_breaches", "amber_limit_gbp", "red_limit_gbp"):
        assert k in s


def test_var_summary_empty():
    book = _book()
    s = book.var_summary(2022)
    assert s["observations"] == 0
    assert s["mean_var_gbp"] == 0.0


def test_var_trend_ordering():
    book = _book()
    book.record_observation("2022-06-15", 80_000.0, 120_000.0, 3_000_000.0)
    book.record_observation("2022-01-15", 40_000.0, 60_000.0, 3_000_000.0)
    trend = book.var_trend()
    assert trend[0]["date"] == "2022-01-15"
    assert trend[1]["date"] == "2022-06-15"
