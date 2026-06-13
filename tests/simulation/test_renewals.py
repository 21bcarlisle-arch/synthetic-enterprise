from datetime import date, timedelta

from sim.weather_price_sensitivity import COLD_SPELL_PRICE_MULTIPLIER
from simulation.renewals import build_renewal_schedule


def _flat_price_records(start_date: str, end_date: str, price: float = 50.0) -> list[dict]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    records = []
    current = start
    while current <= end:
        records.append({"settlementDate": current.isoformat(), "systemSellPrice": price})
        current += timedelta(days=1)
    return records


def test_build_renewal_schedule_without_lookback_temps_fn_unchanged():
    records = _flat_price_records("2015-10-01", "2017-06-30")
    schedule = build_renewal_schedule("C1", "2016-01-01", "2016-01-01", records, 2800)
    assert len(schedule) == 1
    assert schedule[0]["forward_price_gbp_per_mwh"] > 0


def test_build_renewal_schedule_cold_spell_lookback_raises_forward_price():
    records = _flat_price_records("2015-10-01", "2017-06-30")

    no_weather = build_renewal_schedule("C1", "2016-01-01", "2016-01-01", records, 2800)

    def cold_lookback(term_start):
        return [0.0] * 90  # well above COLD_SPELL_HDD_THRESHOLD

    with_cold_weather = build_renewal_schedule(
        "C1", "2016-01-01", "2016-01-01", records, 2800, lookback_temps_fn=cold_lookback
    )

    ratio = (
        with_cold_weather[0]["forward_price_gbp_per_mwh"]
        / no_weather[0]["forward_price_gbp_per_mwh"]
    )
    assert ratio == COLD_SPELL_PRICE_MULTIPLIER


def test_build_renewal_schedule_mild_lookback_no_change():
    records = _flat_price_records("2015-10-01", "2017-06-30")

    no_weather = build_renewal_schedule("C1", "2016-01-01", "2016-01-01", records, 2800)

    def mild_lookback(term_start):
        return [10.0] * 90  # below COLD_SPELL_HDD_THRESHOLD

    with_mild_weather = build_renewal_schedule(
        "C1", "2016-01-01", "2016-01-01", records, 2800, lookback_temps_fn=mild_lookback
    )

    assert with_mild_weather[0]["forward_price_gbp_per_mwh"] == no_weather[0]["forward_price_gbp_per_mwh"]
