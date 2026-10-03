"""Drawn acquisitions start in the months real households switch, from the published record.

Until 2026-10-03 every drawn acquisition day was uniform through its year. Real GB domestic
switching is lowest in January and highest in October in 8 of the 10 years 2016-2025
(DESNZ QEP Table 2.7.1, `docs/market_research/gb_domestic_switching_by_calendar_month.md`).
`seasonal_dates=True` draws each day in proportion to its year's published month. The founder
draw and the trickle both turn it on.

Each control names the defect it catches:
  * the table drifting from the research file it was transcribed from;
  * the flag being ignored, i.e. a flat year (`test_the_month_shares_track_the_published_row`);
  * the flag moving anything other than the date (`test_only_the_date_moves`);
  * a caller dropping the flag (`test_the_founders_and_the_trickle_ask_for_seasonal_dates`);
  * a shape invented for a year the record does not cover.
"""
from __future__ import annotations

import collections
import datetime as dt
import re
from pathlib import Path

import pytest

import simulation.population_draw as pd

REPO = Path(__file__).resolve().parents[2]


def test_the_table_is_the_research_files_combined_column():
    research = REPO / "docs" / "market_research" / "gb_domestic_switching_by_calendar_month.md"
    text = research.read_text(encoding="utf-8")
    rows = re.findall(r"^\| (20\d\d) \| \w{3} \| [\d,]+ \| [\d,]+ \| ([\d,]+) \|", text, re.M)
    published = collections.defaultdict(list)
    for year, combined in rows:
        published[int(year)].append(int(combined.replace(",", "")) // 1000)
    assert published, "the research file's monthly table was not found, so nothing was compared"
    assert {y: tuple(v) for y, v in published.items()} == pd.GB_DOMESTIC_TRANSFERS_BY_MONTH_THOUSANDS


@pytest.mark.parametrize("year", (2016, 2021, 2022))
def test_the_month_shares_track_the_published_row(year):
    n = 40_000
    offsets = pd._seasonal_day_offsets(7, year, n)
    first = dt.date(year, 1, 1)
    counts = collections.Counter((first + dt.timedelta(days=o)).month for o in offsets)
    row = pd.GB_DOMESTIC_TRANSFERS_BY_MONTH_THOUSANDS[year]
    for month in range(1, 13):
        expected = row[month - 1] / sum(row)
        assert abs(counts[month] / n - expected) < 0.01, (year, month, counts[month] / n, expected)
    # The rare branch is real: the published peak and trough are distinguishable at this n,
    # so a flat year could not pass the loop above.
    assert max(row) / min(row) > 1.3


def test_only_the_date_moves():
    kw = dict(start_year=2016, end_year=2016, acquisitions_per_year_lambda=60.0, draw_region=True)
    flat = list(pd.iter_acquisition_events(5, **kw))
    seasonal = list(pd.iter_acquisition_events(5, seasonal_dates=True, **kw))
    assert len(flat) == len(seasonal) > 0
    moved = 0
    for a, b in zip(flat, seasonal):
        da, db = a.to_customer_dict(), b.to_customer_dict()
        moved += da.pop("acquisition_date") != db.pop("acquisition_date")
        assert da == db
    assert moved, "no date moved, so the flag did nothing"


def test_the_founders_and_the_trickle_ask_for_seasonal_dates(monkeypatch):
    from simulation import live_population

    years = []
    real = pd._seasonal_day_offsets

    def spy(base_seed, year, n):
        years.append(year)
        return real(base_seed, year, n)

    monkeypatch.setattr(pd, "_seasonal_day_offsets", spy)
    live_population._drawn_founder_pairs(61001)
    assert 2016 in years, "the founder draw did not ask for the published months"
    years.clear()
    live_population._drawn_trickle(61001)
    assert years and set(years) <= set(range(2021, 2026)), (
        "the trickle did not ask for the published months")


def test_a_year_the_record_does_not_cover_is_refused():
    with pytest.raises(ValueError, match="no published monthly switching shape for 2015"):
        pd._seasonal_day_offsets(1, 2015, 3)
