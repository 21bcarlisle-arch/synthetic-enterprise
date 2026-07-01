"""Tests for sim/profile_class_3.py -- PC3 (non-domestic unrestricted) shape loading.

PC3 and PC1 share season/day-type logic; these tests focus on load_pc3_shape distinctives:
shape structure, PC3 non-domestic higher daytime load profile, and SME-appropriate totals.
"""

from datetime import date

from sim.profile_class_3 import (
    load_pc3_shape,
    season_for_date,
    day_type_for_date,
)


def test_load_pc3_shape_returns_48_values():
    shape = load_pc3_shape(date(2024, 1, 15))
    assert len(shape) == 48


def test_load_pc3_shape_all_nonnegative():
    shape = load_pc3_shape(date(2024, 7, 15))
    assert all(v >= 0 for v in shape)


def test_load_pc3_shape_daily_total_nonzero():
    shape = load_pc3_shape(date(2024, 1, 15))
    assert sum(shape) > 0


def test_load_pc3_shape_accepts_string_date():
    shape = load_pc3_shape("2024-01-15")
    assert len(shape) == 48


def test_load_pc3_shape_winter_higher_than_summer():
    winter = sum(load_pc3_shape(date(2024, 1, 15)))
    summer = sum(load_pc3_shape(date(2024, 7, 15)))
    assert winter > summer


def test_load_pc3_shape_weekday_differs_from_sunday():
    weekday = load_pc3_shape(date(2024, 1, 15))  # Monday
    sunday = load_pc3_shape(date(2024, 1, 21))   # Sunday
    assert weekday != sunday


def test_pc3_season_for_date_winter():
    # PC3 uses same season logic as PC1
    assert season_for_date(date(2024, 1, 15)) == "winter"


def test_pc3_day_type_for_date_saturday():
    assert day_type_for_date(date(2024, 1, 20)) == "saturday"


from datetime import date
from sim.profile_class_3 import (
    last_sunday_of_month, last_monday_of_month, season_for_date, day_type_for_date
)


def test_last_sunday_of_march_2022():
    result = last_sunday_of_month(2022, 3)
    assert result == date(2022, 3, 27)
    assert result.weekday() == 6  # Sunday


def test_last_sunday_of_october_2022():
    result = last_sunday_of_month(2022, 10)
    assert result == date(2022, 10, 30)
    assert result.weekday() == 6  # Sunday


def test_last_monday_of_august_2022():
    result = last_monday_of_month(2022, 8)
    assert result == date(2022, 8, 29)
    assert result.weekday() == 0  # Monday


def test_last_sunday_of_december():
    result = last_sunday_of_month(2022, 12)
    assert result.weekday() == 6


def test_season_for_date_january_is_winter():
    assert season_for_date(date(2022, 1, 15)) == "winter"


def test_season_for_date_april_is_spring():
    assert season_for_date(date(2022, 4, 15)) == "spring"


def test_season_for_date_september_is_autumn():
    # High summer ends on Sunday 2022-09-04; autumn starts 2022-09-05
    assert season_for_date(date(2022, 9, 5)) == "autumn"


def test_day_type_for_date_saturday():
    assert day_type_for_date(date(2022, 6, 4)) == "saturday"


def test_day_type_for_date_sunday():
    assert day_type_for_date(date(2022, 6, 5)) == "sunday"


def test_day_type_for_date_weekday():
    assert day_type_for_date(date(2022, 6, 6)) == "weekday"
