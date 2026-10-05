"""The company's ONE annual grid intensity is NESO's published level, read from the feed.

THE DEFECT (2026-10-05). `grid_intensity_g_co2e_per_kwh(year)` was `UK_GRID_FUEL_MIX` x lifecycle
factors -- an undated hand table -- and read 196.1 gCO2/kWh for 2024 against NESO's published
133.1, while the half-hourly SHAPE the company multiplies it by was already NESO's. Since then
`tools/generate_grid_intensity_feed.py` publishes each year's demand-weighted mean beside the
shape (`annual_level`), and the owner reads that.

The 2026-08-14 version of this file pinned the hand-table values as "unchanged by the
reconciliation". That pin was correct for a de-duplication that fetched no source, and it is
exactly the control that has to invert now a source exists: the mutation below puts the hand
table back and must red here.

MUTATION (must fire): in `carbon_emissions.grid_intensity_g_co2e_per_kwh`, return
`UK_GRID_FUEL_MIX[year].emission_intensity_g_per_kwh` (clamped to the table's window, as it was)
-> `test_the_companys_annual_level_is_the_feeds_published_mean` and
`test_a_year_the_feed_does_not_cover_returns_none_with_a_reason_not_a_clamp` red.
"""

from __future__ import annotations

import json

import pytest

from company.billing.carbon_footprint import electricity_intensity, estimate_carbon
from company.regulatory import carbon_emissions as ce
from company.regulatory.carbon_emissions import (
    GAS_EMISSION_FACTOR_G_CO2E_PER_KWH,
    GRID_INTENSITY_FEED,
    GRID_INTENSITY_PROVENANCE,
    UK_GRID_FUEL_MIX,
    grid_intensity_g_co2e_per_kwh,
    grid_intensity_level,
    grid_intensity_unavailable_reason,
)


def _published() -> dict:
    return json.loads(GRID_INTENSITY_FEED.read_text(encoding="utf-8"))["annual_level"]["by_year"]


def _write_feed(tmp_path, by_year: dict):
    path = tmp_path / "grid_intensity_feed.json"
    path.write_text(json.dumps({"annual_level": {"by_year": by_year}}))
    return path


# --------------------------------------------------------------------------- #
# The level is the published one                                               #
# --------------------------------------------------------------------------- #

def test_the_companys_annual_level_is_the_feeds_published_mean():
    """Every whole year the feed publishes, read back exactly -- and the control can be taken:
    it asserts there ARE whole years before asserting what they say."""
    published = _published()
    whole = {y: r for y, r in published.items() if r["complete"]}
    assert len(whole) >= 7, f"the feed publishes almost no whole years: {sorted(whole)}"
    for year, row in whole.items():
        assert grid_intensity_g_co2e_per_kwh(int(year)) == row["mean_g_co2_per_kwh"], year


def test_the_2024_level_is_neso_and_not_the_hand_fuel_mix():
    """The measured gap that made this a defect: 196.1 (mix x lifecycle factors) against NESO's
    133. Keyed to the property -- the level is the feed's and is far from the mix's -- not to a
    literal that a republished feed would legitimately move."""
    level = grid_intensity_g_co2e_per_kwh(2024)
    assert level == _published()["2024"]["mean_g_co2_per_kwh"]
    assert abs(level - UK_GRID_FUEL_MIX[2024].emission_intensity_g_per_kwh) > 30.0


def test_the_level_is_read_from_the_file_it_is_given(tmp_path):
    """ANTI-TAUTOLOGY: a feed written here, with a value no real year has, must come back."""
    feed = _write_feed(tmp_path, {"2021": {"mean_g_co2_per_kwh": 111.25, "complete": True,
                                           "covers": {"from": "2021-01-01", "to": "2021-12-31"}}})
    assert grid_intensity_g_co2e_per_kwh(2021, feed_path=feed) == 111.25


# --------------------------------------------------------------------------- #
# Coverage: None with a reason, never a clamp                                  #
# --------------------------------------------------------------------------- #

def test_a_year_the_feed_does_not_cover_returns_none_with_a_reason_not_a_clamp():
    published = _published()
    before, after = int(min(published)) - 1, int(max(published)) + 1
    for year in (before, after):
        assert grid_intensity_g_co2e_per_kwh(year) is None, year
        assert grid_intensity_g_co2e_per_kwh(year, allow_partial=True) is None, year
        reason = grid_intensity_unavailable_reason(year)
        assert reason and str(year) in reason and "Not clamped" in reason, reason


def test_a_part_year_is_refused_for_an_annual_figure_and_given_for_the_shape():
    """2025's published mean covers only the dates Elexon's demand record reaches. Read as the
    year's it would be a winter-heavy half year passed off as the whole one. Branch control
    first: both outcomes must be reachable on the real feed."""
    published = _published()
    partial = [y for y, r in published.items() if not r["complete"]]
    assert partial and any(r["complete"] for r in published.values()), (
        "the real feed no longer has both a whole and a part year, so this control cannot be taken")
    for year in partial:
        row = published[year]
        assert grid_intensity_g_co2e_per_kwh(int(year)) is None
        assert grid_intensity_g_co2e_per_kwh(int(year), allow_partial=True) == row["mean_g_co2_per_kwh"]
        reason = grid_intensity_unavailable_reason(int(year))
        assert row["covers"]["from"] in reason and row["covers"]["to"] in reason, reason
        assert grid_intensity_unavailable_reason(int(year), allow_partial=True) is None


def test_a_missing_or_levelless_feed_fails_closed_with_its_reason(tmp_path):
    absent = tmp_path / "absent.json"
    assert grid_intensity_g_co2e_per_kwh(2024, feed_path=absent) is None
    assert "not on disk" in grid_intensity_unavailable_reason(2024, feed_path=absent)
    old_feed = tmp_path / "old.json"
    old_feed.write_text(json.dumps({"records": [], "by_year": {"2024": {"p50": 1.0}}}))
    assert grid_intensity_g_co2e_per_kwh(2024, feed_path=old_feed) is None
    assert "no annual level" in grid_intensity_unavailable_reason(2024, feed_path=old_feed)


# --------------------------------------------------------------------------- #
# The mix stays, for decomposition only                                        #
# --------------------------------------------------------------------------- #

def test_the_mix_is_kept_whole_for_the_low_carbon_column():
    assert sorted(UK_GRID_FUEL_MIX) == list(range(2016, 2026))
    off = {y: r.total_pct for y, r in UK_GRID_FUEL_MIX.items() if abs(r.total_pct - 100.0) > 0.05}
    assert not off, f"mix years that do not sum to 100%: {off}"


def test_nothing_derives_the_national_level_from_the_mix():
    """The level role is gone from every caller that had it. A grep over code, comments
    stripped, so the docstrings that record the history cannot satisfy it."""
    import inspect

    from saas.reporting import annual_report
    from tools.python_code_text import searchable

    for fn in (ce.grid_intensity_g_co2e_per_kwh, annual_report._section_carbon_emissions):
        code = searchable(inspect.getsource(fn))
        assert "emission_intensity_g_per_kwh" not in code, fn.__name__


def test_the_provenance_names_the_published_series():
    assert GRID_INTENSITY_PROVENANCE["unit"] == "gCO2/kWh"
    assert "NESO" in GRID_INTENSITY_PROVENANCE["source"]
    assert "loss-corrected" in GRID_INTENSITY_PROVENANCE["basis"]


def test_the_published_gas_factor_is_unchanged():
    assert GAS_EMISSION_FACTOR_G_CO2E_PER_KWH == 183.0


# --------------------------------------------------------------------------- #
# The readers                                                                  #
# --------------------------------------------------------------------------- #

def test_the_two_deleted_series_are_gone_from_their_old_homes():
    import company.billing.carbon_footprint as footprint
    import company.sustainability.carbon_intensity_register as register

    assert not hasattr(footprint, "_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH")
    assert not hasattr(register, "_GRID_AVERAGE_INTENSITY")


def test_the_surviving_consumers_all_read_the_owner():
    for year in range(2015, 2027):
        assert electricity_intensity(year) == grid_intensity_g_co2e_per_kwh(year)


def test_an_estimate_for_a_year_with_no_level_has_no_kg_and_says_why():
    whole = estimate_carbon(2_700.0, "electricity", 2024)
    assert whole["kg_co2e"] == round(2_700.0 * grid_intensity_g_co2e_per_kwh(2024) / 1000.0, 1)
    refused = estimate_carbon(2_700.0, "electricity", 2030)
    assert refused["kg_co2e"] is None and "2030" in refused["unavailable"]


def _rendered():
    from saas.reporting.annual_report import _section_carbon_emissions

    accounts = {str(y): {"income_statement": {"revenue_gbp": 1_000_000.0}} for y in UK_GRID_FUEL_MIX}
    return _section_carbon_emissions({"management_accounts": accounts})


def test_the_annual_reports_intensity_column_is_the_published_level():
    rendered = _rendered()
    for year in UK_GRID_FUEL_MIX:
        row = next(ln for ln in rendered.splitlines() if ln.startswith(f"| {year} |"))
        level = grid_intensity_level(year)
        if level.complete:
            assert f"| {level.g_co2_per_kwh:.0f}g/kWh |" in row, row
        else:
            assert "| n/a |" in row, row
    assert "NESO" in rendered


def test_the_sections_closing_sentence_agrees_with_its_own_table():
    """Located by content, not position. From the first to the last WHOLE published year."""
    rendered = _rendered()
    summaries = [ln for ln in rendered.splitlines() if "Grid emission intensity declining" in ln]
    assert len(summaries) == 1, summaries
    whole = [y for y in sorted(UK_GRID_FUEL_MIX) if grid_intensity_g_co2e_per_kwh(y) is not None]
    first, last = whole[0], whole[-1]
    i0, i1 = grid_intensity_g_co2e_per_kwh(first), grid_intensity_g_co2e_per_kwh(last)
    assert f"{first} {i0:.0f}g/kWh" in summaries[0]
    assert f"{last} {i1:.0f}g/kWh" in summaries[0]
    assert f"({round((1.0 - i1 / i0) * 100.0)}% reduction)" in summaries[0]


def test_the_register_compares_against_the_published_level_and_refuses_without_one():
    from company.sustainability.carbon_intensity_register import FuelMixSnapshot, FuelSource

    mix = {FuelSource.NATURAL_GAS: 1.0}
    whole = FuelMixSnapshot(year=2024, fuel_mix=mix, total_kwh_supplied=1.0)
    assert whole.vs_grid_average == pytest.approx(394.0 - grid_intensity_g_co2e_per_kwh(2024))
    assert FuelMixSnapshot(year=2030, fuel_mix=mix, total_kwh_supplied=1.0).vs_grid_average is None
