"""The media-coverage counter counts GB energy-price stories once, and nothing else.

Each test names the defect it catches. The counter is harness-side (W6); these run offline
against a hand-built GKG day, never the network.
"""

from __future__ import annotations

import io
import json
import zipfile

from tools import fetch_gdelt_energy_price_coverage as m

HEADER = "\t".join(
    ["DATE", "NUMARTS", "COUNTS", "THEMES", "LOCATIONS", "PERSONS", "ORGANIZATIONS",
     "TONE", "CAMEOEVENTIDS", "SOURCES", "SOURCEURLS"]
)


def _day(rows: list[tuple[str, str, str]]) -> bytes:
    lines = [HEADER] + [
        "\t".join(["20170801", "1", "", themes, "", "", orgs, "", "", "", urls])
        for themes, orgs, urls in rows
    ]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("20170801.gkg.csv", "\n".join(lines) + "\n")
    return buf.getvalue()


BG = "https://www.theguardian.com/business/2017/aug/01/british-gas-hikes-electricity-prices"
BBC = "http://www.bbc.co.uk/news/business-40788016"


def test_a_slugged_rise_counts_and_reads_as_a_rise() -> None:
    # Defect: the slug leg or the rise reading stops firing, and the announcement day is empty.
    assert m.classify_row("", "", BG) == (True, True)


def test_a_bbc_story_counts_only_by_its_theme_and_a_named_supplier() -> None:
    # Defect: BBC has no slug, so without the theme leg the largest outlet never counts;
    # with the theme alone, every BBC story on any electricity price would.
    assert m.classify_row("ECON_ELECTRICALPRICE;", "british gas;centrica", BBC) == (True, False)
    assert m.classify_row("ECON_ELECTRICALPRICE;", "bank of england", BBC) == (False, False)


def test_an_org_is_matched_whole_so_sse_is_not_assessment() -> None:
    assert not m.names_energy_org("risk assessment;association of drivers")
    assert m.names_energy_org("sse;ofgem")


def test_a_foreign_edition_story_does_not_count() -> None:
    # Defect seen on the first pull: The Guardian's Australian edition's power-price stories
    # counted as GB coverage on 3 Aug 2017.
    url = "https://www.theguardian.com/australia-news/2017/aug/03/power-prices-turnbull"
    assert m.classify_row("", "", url) == (False, False)


def test_a_non_national_outlet_is_in_neither_numerator_nor_denominator() -> None:
    day = m.count_day(_day([("", "", "https://www.localpaper.co.uk/energy-price-rise")]))
    assert day == {"outlet_urls": {}, "matched": {}}


def test_a_url_on_two_rows_counts_once_and_the_denominator_holds_every_national_url() -> None:
    day = m.count_day(_day([
        ("", "", BG + "<UDIV>" + BBC),
        ("", "", BG),
    ]))
    assert list(day["matched"]) == [BG]
    assert day["outlet_urls"] == {"bbc.co.uk": 1, "theguardian.com": 1}


def test_the_week_counts_a_story_once_across_days(tmp_path, monkeypatch) -> None:
    # Defect: a story GDELT re-sees on a later day is counted again, inflating the spike.
    import datetime as dt
    monkeypatch.setattr(m, "CACHE_ROOT", tmp_path)
    rec = {"outlet_urls": {"theguardian.com": 10}, "matched": {BG: {"outlet": "x", "rise": True}}}
    for d in ("20170731", "20170801"):
        (tmp_path / f"{d}.json").write_text(json.dumps(rec))
    out = m.aggregate(dt.date(2017, 7, 31), dt.date(2017, 8, 6))
    (week,) = out["weeks"]
    assert (week["energy_price_articles"], week["rise_articles"], week["national_urls"]) == (1, 1, 20)
    assert week["days_counted"] == 2 and week["complete"] is False


def _cache_days(path, start, n, per_day, monkeypatch) -> None:
    import datetime as dt
    monkeypatch.setattr(m, "CACHE_ROOT", path)
    for k in range(n):
        d = start + dt.timedelta(k)
        matched = {f"u{d}{i}": {"outlet": "x", "rise": False} for i in range(per_day(k))}
        (path / f"{d:%Y%m%d}.json").write_text(json.dumps({"outlet_urls": {}, "matched": matched}))


def test_an_announcement_week_is_read_against_a_baseline_that_ends_a_week_before(
    tmp_path, monkeypatch
) -> None:
    # Defect: a baseline that runs up to the announcement absorbs the trailed days before it
    # (leaks, previews), shrinking the spike. Days -7..-1 carry 50 a day and must not count.
    import datetime as dt
    day = dt.date(2019, 2, 5)
    _cache_days(tmp_path, day - dt.timedelta(35), 42,
                lambda k: 2 if k < 28 else (50 if k < 35 else 10), monkeypatch)
    out = m.coverage_at(day)
    assert out == {"day0_articles": 10, "day0_per_1000_national_urls": None,
                   "week_articles": 70, "baseline_per_day": 2.0, "week_vs_baseline": 5.0}


def test_an_unpulled_baseline_reads_as_unknown_not_as_zero(tmp_path, monkeypatch) -> None:
    import datetime as dt
    day = dt.date(2019, 2, 5)
    _cache_days(tmp_path, day, 7, lambda k: 10, monkeypatch)
    out = m.coverage_at(day)
    assert out["week_articles"] == 70 and out["week_vs_baseline"] is None


def test_an_exclusion_added_after_a_day_was_pulled_still_applies_to_that_day(
    tmp_path, monkeypatch
) -> None:
    # Defect: the weekly series keeps a US wire story because its day was cached by an older rule.
    import datetime as dt
    monkeypatch.setattr(m, "CACHE_ROOT", tmp_path)
    us = "https://www.dailymail.co.uk/wires/ap/article-1/Average-US-price-gas-drops.html"
    rec = {"outlet_urls": {"dailymail.co.uk": 2},
           "matched": {us: {"outlet": "x", "rise": False}, BG: {"outlet": "x", "rise": True}}}
    (tmp_path / "20181106.json").write_text(json.dumps(rec))
    (week,) = m.aggregate(dt.date(2018, 11, 5), dt.date(2018, 11, 11))["weeks"]
    assert week["energy_price_articles"] == 1
