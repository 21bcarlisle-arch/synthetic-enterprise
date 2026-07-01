"""Tests for simulation/life_events.py internal helpers and LifeEvent dataclass."""

import random
from datetime import date

import pytest

from simulation.life_events import LifeEvent, _annual_prob, _random_date_in_year


_TABLE = {2016: 0.10, 2019: 0.25, 2024: 0.40}


def test_annual_prob_exact_year():
    assert _annual_prob(_TABLE, 2019) == pytest.approx(0.25)


def test_annual_prob_clamps_below_min():
    assert _annual_prob(_TABLE, 2010) == pytest.approx(0.10)


def test_annual_prob_clamps_above_max():
    assert _annual_prob(_TABLE, 2030) == pytest.approx(0.40)


def test_annual_prob_at_min_boundary():
    assert _annual_prob(_TABLE, 2016) == pytest.approx(0.10)


def test_annual_prob_at_max_boundary():
    assert _annual_prob(_TABLE, 2024) == pytest.approx(0.40)


def test_annual_prob_interpolates_exact():
    table = {2016: 0.05}
    assert _annual_prob(table, 2016) == pytest.approx(0.05)


def test_random_date_in_year_correct_year():
    rng = random.Random(42)
    result = _random_date_in_year(2022, rng)
    assert result[:4] == "2022"


def test_random_date_in_year_valid_iso_format():
    rng = random.Random(1)
    result = _random_date_in_year(2022, rng)
    parsed = date.fromisoformat(result)
    assert parsed.year == 2022


def test_random_date_in_year_deterministic_with_seed():
    result1 = _random_date_in_year(2022, random.Random(99))
    result2 = _random_date_in_year(2022, random.Random(99))
    assert result1 == result2


def test_random_date_in_year_range_jan_to_dec():
    rng = random.Random(0)
    dates = [_random_date_in_year(2022, rng) for _ in range(50)]
    months = {d[5:7] for d in dates}
    assert len(months) > 1


def test_life_event_is_frozen():
    event = LifeEvent(customer_id="C1", event_date="2022-01-01", event_type="solar_install", payload={"solar_kwp": 3.0})
    with pytest.raises((AttributeError, TypeError)):
        event.customer_id = "C2"


def test_life_event_has_expected_fields():
    event = LifeEvent(customer_id="C1", event_date="2022-06-15", event_type="ev_acquired", payload={})
    assert event.customer_id == "C1"
    assert event.event_date == "2022-06-15"
    assert event.event_type == "ev_acquired"
    assert event.payload == {}


# 13. _annual_prob returns table value for exact year
def test_annual_prob_exact_year_mid():
    table = {2016: 0.10, 2020: 0.25, 2024: 0.40}
    assert _annual_prob(table, 2020) == 0.25


# 14. _random_date_in_year returns a date string in that year
def test_random_date_in_year_returns_correct_year():
    rng = random.Random(99)
    d = _random_date_in_year(2022, rng)
    assert d.startswith("2022-")


# 15. LifeEvent event_date is stored as provided
def test_life_event_event_date_stored():
    ev = LifeEvent(customer_id="C1", event_date="2022-07-15", event_type="solar_install", payload={})
    assert ev.event_date == "2022-07-15"
