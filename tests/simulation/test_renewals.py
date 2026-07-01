from datetime import date, timedelta

import pytest
from sim.weather_price_sensitivity import COLD_SPELL_PRICE_MULTIPLIER
from simulation.renewals import NOTICE_DAYS, build_renewal_schedule


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


# Phase 34a: 42-day notice period tests


def test_notice_date_present_in_term_dict():
    records = _flat_price_records("2015-10-01", "2017-06-30")
    schedule = build_renewal_schedule("C1", "2016-01-01", "2016-01-01", records, 2800)
    assert "notice_date" in schedule[0]


def test_notice_date_is_42_days_before_term_start():
    records = _flat_price_records("2015-10-01", "2017-06-30")
    schedule = build_renewal_schedule("C1", "2016-06-01", "2016-06-01", records, 2800)
    term_start = date.fromisoformat(schedule[0]["acquisition_date"])
    notice_date = date.fromisoformat(schedule[0]["notice_date"])
    assert (term_start - notice_date).days == NOTICE_DAYS


def test_company_fwd_uses_prices_at_notice_date_not_term_start():
    """When price spikes sharply 21 days before term start, company_fwd should NOT reflect the spike."""
    low_price = 50.0
    spike_price = 200.0
    # Low price covers the notice window; spike only in final 41 days before term start.
    base_records = _flat_price_records("2015-10-01", "2016-11-19", low_price)
    spike_records = _flat_price_records("2016-11-20", "2017-06-30", spike_price)
    records = base_records + spike_records

    # Term start 2017-01-01; notice_date = 2016-11-20 — right at spike boundary.
    schedule = build_renewal_schedule("C1", "2017-01-01", "2017-01-01", records, 2800)
    company_fwd = schedule[0]["company_forward_price_gbp_per_mwh"]
    sim_fwd = schedule[0]["forward_price_gbp_per_mwh"]

    # sim_fwd should be spike_price (knows full market); company_fwd should be low_price.
    assert sim_fwd > low_price * 1.5, f"sim_fwd={sim_fwd} expected to reflect spike"
    assert company_fwd < spike_price * 0.9, f"company_fwd={company_fwd} should not fully reflect spike"


def test_notice_constant_is_42():
    assert NOTICE_DAYS == 42


def test_multiple_terms_all_have_notice_date():
    records = _flat_price_records("2015-01-01", "2020-12-31")
    schedule = build_renewal_schedule("C1", "2016-01-01", "2018-01-01", records, 2800)
    assert len(schedule) >= 2
    for term in schedule:
        assert "notice_date" in term
        assert (
            date.fromisoformat(term["acquisition_date"]) - date.fromisoformat(term["notice_date"])
        ).days == NOTICE_DAYS


def test_deemed_premium_constant():
    from simulation.renewals import DEEMED_PREMIUM
    assert DEEMED_PREMIUM == 0.20


def test_flex_markup_constant():
    from simulation.renewals import FLEX_MARKUP_PER_MWH
    assert FLEX_MARKUP_PER_MWH == 2.0


def test_first_term_starts_on_supply_start():
    records = _flat_price_records("2015-10-01", "2017-06-30")
    schedule = build_renewal_schedule("C1", "2016-03-01", "2016-03-01", records, 2800)
    assert schedule[0]["acquisition_date"] == "2016-03-01"


def test_all_term_keys_present():
    records = _flat_price_records("2015-10-01", "2017-06-30")
    schedule = build_renewal_schedule("C1", "2016-01-01", "2016-01-01", records, 2800)
    r = schedule[0]
    for key in ("acquisition_date", "term_end", "forward_price_gbp_per_mwh",
                "company_forward_price_gbp_per_mwh", "unit_rate_gbp_per_mwh",
                "notice_date"):
        assert key in r, f"missing key {key!r}"


def test_company_forward_price_is_positive():
    records = _flat_price_records("2015-10-01", "2017-06-30")
    schedule = build_renewal_schedule("C1", "2016-01-01", "2016-01-01", records, 2800)
    assert schedule[0]["company_forward_price_gbp_per_mwh"] > 0


def test_tariff_rate_exceeds_forward_price():
    records = _flat_price_records("2015-10-01", "2017-06-30")
    schedule = build_renewal_schedule("C1", "2016-01-01", "2016-01-01", records, 2800)
    r = schedule[0]
    assert r["unit_rate_gbp_per_mwh"] > r["forward_price_gbp_per_mwh"]
