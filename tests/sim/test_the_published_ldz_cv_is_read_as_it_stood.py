"""The published daily CV per charging area is read as it stood at a moment, never as it ended.

Lake: data/lake/national_gas_ldz_cv/ (G1 of docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md).
The defects named here: a reader that hands a supplier a revision published after its bill; a series
that silently fills the years the portal does not serve; and a transcription missing a day.
"""

from __future__ import annotations

from datetime import date, timedelta

from sim import ldz_calorific_value as L


def test_every_area_has_every_gas_day_from_the_first_served_to_the_end_of_2025():
    days = (date(2025, 12, 31) - date.fromisoformat(L.FIRST_GAS_DAY)).days + 1
    for ldz in L.CHARGING_AREAS:
        missing = [d for i in range(days)
                   if L.final_cv(ldz, d := (date.fromisoformat(L.FIRST_GAS_DAY) + timedelta(i)).isoformat()) is None]
        assert not missing, f"{ldz} lacks {len(missing)} gas days, first {missing[:3]}"


def test_a_revision_published_later_is_not_seen_before_it_was_published():
    """LDZ(NO), 9 Aug 2022: 40.3 on the day, 40.4 the day after, republished as 36.0 on 7 Apr 2023."""
    assert L.published_cv("NO", "2022-08-09", "2022-08-09T12:00:00") == 40.3
    assert L.published_cv("NO", "2022-08-09", "2022-08-31") == 40.4
    assert L.published_cv("NO", "2022-08-09", "2023-04-08") == 36.0
    assert L.final_cv("NO", "2022-08-09") == 36.0
    # Before its first publication there is nothing to bill at.
    assert L.published_cv("NO", "2022-08-09", "2022-08-08") is None


def test_the_years_the_portal_does_not_serve_are_none_not_a_value():
    assert L.final_cv("EA", "2021-10-31") is None
    assert L.published_cv("EA", "2016-06-01", "2026-01-01") is None
    assert L.final_cv("EA", L.FIRST_GAS_DAY) is not None


def test_the_worlds_cv_feed_matches_the_protocol_by_name_and_order():
    """`isinstance` on a runtime_checkable Protocol checks the method is PRESENT, never its signature,
    and the feed is called positionally: a swapped `gas_day`/`ldz` would pass it and read nothing."""
    import inspect

    from company.billing.gas_volume_conversion import CalorificValueFeed

    def params(fn):
        return list(inspect.signature(fn).parameters)

    assert isinstance(L.PublishedCalorificValues(), CalorificValueFeed)
    assert params(L.PublishedCalorificValues.published_cv) == params(CalorificValueFeed.published_cv)
