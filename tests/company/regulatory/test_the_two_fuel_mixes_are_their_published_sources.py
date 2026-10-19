"""The two UK fuel-mix tables are the DESNZ series they cite, one fact each (director steer 19 Oct, item 4).

The page `docs/market_research/two_uk_electricity_fuel_mixes_generation_and_disclosure.md` holds the
fetched figures in one `fuel-mix-sources` block. `UK_GRID_FUEL_MIX` must equal its DUKES 5.6.C
generation shares, and `_FUEL_MIX_BY_YEAR` must equal its FMD UK mix. An edit to either table that
the page does not carry reds here, and so does an edit to the page that the code does not follow.

The mapping from DUKES' rows to the eight buckets is checked against DUKES' own derived row, the
"Renewable generation share": a bucket mapped wrongly (for example "Total wind", which includes wave
and tidal and reads 11.91 for 2016 against onshore plus offshore at 10.96) misses it.

Mutations, run 2026-10-19, each reds the named test:
* 2024 `wind_pct` 29.23 -> 30.23 in the code: `test_the_generation_mix_is_dukes_5_6_c` and
  `test_the_bucket_mapping_reproduces_dukes_own_renewable_share`.
* 2023 FMD `coal` 6.3 -> 1.3 in the code: `test_the_disclosure_mix_is_the_fmd_uk_mix`.
* `get_fuel_mix` clamping again (`_FUEL_MIX_BY_YEAR.get(year) or _FUEL_MIX_BY_YEAR[2019]`):
  `test_a_period_with_no_fetched_edition_is_absent`.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from company.billing.fuel_mix import _FUEL_MIX_BY_YEAR, fuel_mix_summary, get_fuel_mix
from company.regulatory.carbon_emissions import UK_GRID_FUEL_MIX

_BLOCK = re.compile(r"^```fuel-mix-sources[ \t]*\n(.*?)^```", re.M | re.S)

GENERATION_ORDER = ("coal_pct", "gas_pct", "nuclear_pct", "wind_pct", "solar_pct", "hydro_pct",
                    "biomass_pct", "other_pct")
DISCLOSURE_ORDER = ("coal", "gas", "nuclear", "renewable", "other")


@pytest.fixture(scope="module")
def sources() -> dict:
    page = (Path(__file__).resolve().parents[3] / "docs" / "market_research"
            / "two_uk_electricity_fuel_mixes_generation_and_disclosure.md")
    blocks = _BLOCK.findall(page.read_text(encoding="utf-8"))
    assert len(blocks) == 1, f"{page.name} must carry exactly one fuel-mix-sources block"
    return yaml.safe_load(blocks[0])


def test_the_page_carries_both_series_and_the_check_row(sources):
    """Control over the partition: every table this file compares is present and non-empty, so
    an emptied block cannot pass the equality tests below by comparing nothing."""
    assert sources["generation_dukes_5_6_c"] and sources["disclosure_fmd_uk_mix"]
    assert set(sources["dukes_renewable_generation_share"]) == set(sources["generation_dukes_5_6_c"])


def test_the_generation_mix_is_dukes_5_6_c(sources):
    published = sources["generation_dukes_5_6_c"]
    assert set(UK_GRID_FUEL_MIX) == set(published)
    for year, row in published.items():
        record = UK_GRID_FUEL_MIX[year]
        assert [getattr(record, f) for f in GENERATION_ORDER] == pytest.approx(row, abs=1e-9), year
        assert record.imports_pct == 0.0, f"{year}: a generation mix has no imports"


def test_the_bucket_mapping_reproduces_dukes_own_renewable_share(sources):
    for year, share in sources["dukes_renewable_generation_share"].items():
        r = UK_GRID_FUEL_MIX[year]
        ours = r.wind_pct + r.solar_pct + r.hydro_pct + r.biomass_pct
        assert ours == pytest.approx(share, abs=0.02), year
        assert r.total_pct == pytest.approx(100.0, abs=0.05), year


def test_the_disclosure_mix_is_the_fmd_uk_mix(sources):
    published = sources["disclosure_fmd_uk_mix"]
    assert set(_FUEL_MIX_BY_YEAR) == set(published)
    for year, row in published.items():
        assert [_FUEL_MIX_BY_YEAR[year][k] for k in DISCLOSURE_ORDER] == pytest.approx(row), year
        assert sum(row) == pytest.approx(100.0, abs=0.15), year


def test_a_period_with_no_fetched_edition_is_absent(sources):
    """2016/17 to 2018/19 were not found. Absent means None, not a neighbouring edition."""
    assert min(sources["disclosure_fmd_uk_mix"]) == 2019
    for year in (2010, 2016, 2018, 2026):
        assert get_fuel_mix(year) is None, year
        assert fuel_mix_summary(year) is None, year
    assert get_fuel_mix(2019) is not None
    assert fuel_mix_summary(2019)["trend_direction"] is None, "no 2018/19 edition to trend against"
    assert fuel_mix_summary(2025)["period"] == "2025/26"
