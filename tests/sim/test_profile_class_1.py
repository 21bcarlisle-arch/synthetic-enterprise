"""Tests for sim/profile_class_1.py -- BSC season/day-type classification and PC1 shape loading.

Phase MV-pre: coverage for season_for_date (5 BSC seasons, UK clock-change boundaries),
day_type_for_date (weekday/saturday/sunday), load_pc1_shape (shape structure).
"""

import pytest
from datetime import date

from sim.profile_class_1 import (
    last_sunday_of_month,
    last_monday_of_month,
    season_for_date,
    day_type_for_date,
    load_pc1_shape,
)


# ── last_sunday_of_month ────────────────────────────────────────────────────

def test_last_sunday_oct_2024():
    # GMT/BST clock change 2024: 27 Oct
    assert last_sunday_of_month(2024, 10) == date(2024, 10, 27)


def test_last_sunday_mar_2024():
    # BST begins 2024: 31 Mar
    assert last_sunday_of_month(2024, 3) == date(2024, 3, 31)


def test_last_sunday_oct_2023():
    # GMT/BST clock change 2023: 29 Oct
    assert last_sunday_of_month(2023, 10) == date(2023, 10, 29)


def test_last_monday_aug_2024():
    # August Bank Holiday 2024: 26 Aug
    assert last_monday_of_month(2024, 8) == date(2024, 8, 26)


def test_last_monday_aug_2016():
    # August Bank Holiday 2016: 29 Aug
    assert last_monday_of_month(2016, 8) == date(2016, 8, 29)


# ── season_for_date ─────────────────────────────────────────────────────────

def test_january_is_winter():
    assert season_for_date(date(2024, 1, 15)) == "winter"


def test_december_is_winter():
    assert season_for_date(date(2024, 12, 20)) == "winter"


def test_november_is_winter():
    # After Oct clock change → winter
    assert season_for_date(date(2024, 11, 1)) == "winter"


def test_oct_clock_change_date_is_winter():
    # 27 Oct 2024 (clock change to GMT) → winter starts
    assert season_for_date(date(2024, 10, 27)) == "winter"


def test_day_before_oct_clock_change_is_autumn():
    # 26 Oct 2024 (last day before clock change) → autumn
    assert season_for_date(date(2024, 10, 26)) == "autumn"


def test_april_is_spring():
    # After BST clock change in March → spring
    assert season_for_date(date(2024, 4, 15)) == "spring"


def test_bst_clock_change_date_is_spring():
    # 31 Mar 2024 (BST begins) → spring starts
    assert season_for_date(date(2024, 3, 31)) == "spring"


def test_day_before_bst_is_winter():
    # 30 Mar 2024 → still winter
    assert season_for_date(date(2024, 3, 30)) == "winter"


def test_june_is_summer():
    assert season_for_date(date(2024, 6, 15)) == "summer"


def test_high_summer_in_august():
    # August Bank Holiday 2024 is 26 Aug.
    # high_summer starts 6th Saturday before it:
    # 26 Aug - (2 + 7*5) = 26 Aug - 37 = 20 Jul 2024
    # high_summer ends Sunday after BH: 26 Aug + 6 = 1 Sep 2024
    assert season_for_date(date(2024, 8, 1)) == "high_summer"


def test_september_after_high_summer_is_autumn():
    # After high_summer ends (1 Sep 2024) → autumn
    assert season_for_date(date(2024, 9, 5)) == "autumn"


def test_string_date_raises_type_error():
    # season_for_date takes a date, not a string
    with pytest.raises((AttributeError, TypeError)):
        season_for_date("2024-01-15")  # type: ignore


# ── day_type_for_date ───────────────────────────────────────────────────────

def test_monday_is_weekday():
    assert day_type_for_date(date(2024, 1, 15)) == "weekday"  # Monday


def test_friday_is_weekday():
    assert day_type_for_date(date(2024, 1, 19)) == "weekday"  # Friday


def test_saturday():
    assert day_type_for_date(date(2024, 1, 20)) == "saturday"


def test_sunday():
    assert day_type_for_date(date(2024, 1, 21)) == "sunday"


# ── load_pc1_shape ──────────────────────────────────────────────────────────

def test_load_pc1_shape_returns_48_values():
    shape = load_pc1_shape(date(2024, 1, 15))  # winter weekday
    assert len(shape) == 48


def test_load_pc1_shape_all_positive():
    shape = load_pc1_shape(date(2024, 7, 15))  # summer weekday
    assert all(v > 0 for v in shape)


def test_load_pc1_shape_daily_total_in_range():
    # PC1 average domestic customer: daily total 3-15 kWh/day range
    shape = load_pc1_shape(date(2024, 1, 15))  # winter (higher)
    total = sum(shape)
    assert 2.0 < total < 20.0


def test_load_pc1_shape_winter_higher_than_summer():
    winter = sum(load_pc1_shape(date(2024, 1, 15)))
    summer = sum(load_pc1_shape(date(2024, 7, 15)))
    assert winter > summer


def test_load_pc1_shape_accepts_string_date():
    shape = load_pc1_shape("2024-01-15")
    assert len(shape) == 48


def test_load_pc1_shape_saturday_differs_from_weekday():
    weekday = load_pc1_shape(date(2024, 1, 15))  # Monday
    saturday = load_pc1_shape(date(2024, 1, 20))  # Saturday
    assert weekday != saturday
