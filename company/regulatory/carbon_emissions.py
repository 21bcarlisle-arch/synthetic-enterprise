"""Scope 2 emissions intensity from supplied electricity: fuel mix reporting.

SOLE READER OF THE ANNUAL UK GRID INTENSITY (single owner since 2026-08-14; the LEVEL comes from
NESO's published series since 2026-10-05). `tools/grid_intensity_guard.py` fails if a second
year-keyed intensity table appears anywhere under `company/` or `saas/` (R10 -- the class).

WHERE THE NUMBER COMES FROM. `grid_intensity_g_co2e_per_kwh(year)` reads the per-year annual
mean that `tools/generate_grid_intensity_feed.py` publishes in
`docs/market_data/grid_intensity_feed.json` (`annual_level`). That mean is taken from the same
half-hourly history as the feed's shape: NESO's Historic GB Generation Mix carbon intensity,
2016-2025, with NESO's own arithmetic on Elexon's fuel mix only where it has no usable value. Reading a published file is the
crossing the epistemic wall sanctions; a real GB supplier reads exactly this series.

Basis, stated because every joiner must carry it: gCO2/kWh, national, DEMAND-WEIGHTED annual mean,
GENERATION basis -- per kWh generated, transmission and distribution losses NOT included -- CO2 at
the generator only: not lifecycle, and not CO2e despite this function's name, which the guard pins.
(It said "loss-corrected, consumption basis" until 2026-10-05. That was NESO's API methodology
text, which the API's own data has not matched since 2020-04-27; the series is now the historic
mix, which is generation basis throughout.) The feed's
`annual_level.basis` and `.weighting` are the full statement.

WHAT IT REPLACED, measured (2026-10-05): `UK_GRID_FUEL_MIX` x lifecycle factors, an undated
hand table, which read 196.1 for 2024 against NESO's 133.1 (the API; 131.9 on the historic mix)
and was 5-47% high in every whole year 2017-2024. The finding that made this module the owner
(`docs/staging/done/WORKER_FINDING_THREE_LIVE_GRID_INTENSITY_SERIES_DISAGREE_BY_HALF_2026-08-14.md`)
asked for "a single sourced series ... cited to a named publication and vintage"; the 08-14
repair kept the hand table only because no source had been fetched. One now has.

THE MIX TABLE STAYS, FOR DECOMPOSITION ONLY. `UK_GRID_FUEL_MIX` still renders the annual report's
`Low Carbon %` column and is reconciled against the other fuel-mix table in
`fuel_mix_reconciliation.py`. It has NO level role: nothing may multiply it by
`_EMISSION_FACTORS_G_CO2_PER_KWH` to get a national intensity. `FuelMixRecord` remains a generic
mix calculator for a mix a caller supplies.

COVERAGE, never clamped. A year the feed does not publish returns None, and a year it publishes
only in part (`complete: false` -- 2016 from 2016-03-01, 2025 through 2025-06-07, both bounded by
Elexon's demand record) returns None for an annual figure. `allow_partial=True` is for a caller
multiplying the feed's own half-hourly SHAPE inside the covered span, where shape x level is the
published value exactly. `grid_intensity_unavailable_reason(year)` says why.

POINT IN TIME. The feed is published after a run, as a whole-history record, and is never read at
a simulated date: every caller (annual report, explore carbon, R3 ceiling, footprints) is
post-run. A year mean exists only for the dates the history covers, and is marked partial
otherwise, so no caller can take a part year for the whole.
"""
from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

#: Lifecycle emission factors, gCO2eq/kWh generated, for `FuelMixRecord`'s generic calculator.
#: `inferred` citation (values match IPCC AR5 WG3 Annex III medians), unverified vintage. NOT the
#: national level: applied to `UK_GRID_FUEL_MIX` they gave 196.1 for 2024 against NESO's 133.1.
_EMISSION_FACTORS_G_CO2_PER_KWH = {
    'coal': 820.0,
    'gas': 490.0,
    'nuclear': 12.0,
    'wind': 11.0,
    'solar': 41.0,
    'hydro': 24.0,
    'biomass': 230.0,
    'imports': 300.0,
}


@dataclass(frozen=True)
class FuelMixRecord:
    year: int
    coal_pct: float
    gas_pct: float
    nuclear_pct: float
    wind_pct: float
    solar_pct: float
    hydro_pct: float
    biomass_pct: float
    imports_pct: float

    @property
    def total_pct(self) -> float:
        return round(self.coal_pct + self.gas_pct + self.nuclear_pct +
                      self.wind_pct + self.solar_pct + self.hydro_pct +
                      self.biomass_pct + self.imports_pct, 1)

    @property
    def renewable_pct(self) -> float:
        return round(self.wind_pct + self.solar_pct + self.hydro_pct, 1)

    @property
    def low_carbon_pct(self) -> float:
        return round(self.renewable_pct + self.nuclear_pct + self.biomass_pct, 1)

    @property
    def emission_intensity_g_per_kwh(self) -> float:
        intensity = (
            self.coal_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['coal'] +
            self.gas_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['gas'] +
            self.nuclear_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['nuclear'] +
            self.wind_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['wind'] +
            self.solar_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['solar'] +
            self.hydro_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['hydro'] +
            self.biomass_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['biomass'] +
            self.imports_pct / 100 * _EMISSION_FACTORS_G_CO2_PER_KWH['imports']
        )
        return round(intensity, 1)


#: The UK national generation fuel mix, percent by year. DECOMPOSITION ONLY since 2026-10-05: it
#: renders `Low Carbon %` and nothing else. Its `emission_intensity_g_per_kwh` is not the national
#: level and no caller may use it as one -- the level is `grid_intensity_g_co2e_per_kwh(year)`.
#: Moved here 2026-08-14 from a local inside `annual_report._section_carbon_emissions`; values
#: unsourced ("DESNZ/National Grid annual fuel mix data", no vintage), and the guard keeps it the
#: single owned mix.
UK_GRID_FUEL_MIX: Dict[int, 'FuelMixRecord'] = {
    2016: FuelMixRecord(2016, coal_pct=9.0, gas_pct=42.0, nuclear_pct=21.0, wind_pct=11.0, solar_pct=3.0, hydro_pct=2.0, biomass_pct=8.0, imports_pct=4.0),
    2017: FuelMixRecord(2017, coal_pct=7.0, gas_pct=40.0, nuclear_pct=21.0, wind_pct=15.0, solar_pct=3.0, hydro_pct=2.0, biomass_pct=8.0, imports_pct=4.0),
    2018: FuelMixRecord(2018, coal_pct=5.0, gas_pct=39.0, nuclear_pct=20.0, wind_pct=17.0, solar_pct=3.0, hydro_pct=2.0, biomass_pct=9.0, imports_pct=5.0),
    2019: FuelMixRecord(2019, coal_pct=2.0, gas_pct=37.0, nuclear_pct=19.0, wind_pct=20.0, solar_pct=4.0, hydro_pct=2.0, biomass_pct=12.0, imports_pct=4.0),
    2020: FuelMixRecord(2020, coal_pct=1.0, gas_pct=33.0, nuclear_pct=17.0, wind_pct=24.0, solar_pct=4.0, hydro_pct=2.0, biomass_pct=12.0, imports_pct=7.0),
    2021: FuelMixRecord(2021, coal_pct=2.0, gas_pct=36.0, nuclear_pct=17.0, wind_pct=22.0, solar_pct=4.0, hydro_pct=2.0, biomass_pct=11.0, imports_pct=6.0),
    2022: FuelMixRecord(2022, coal_pct=2.0, gas_pct=38.0, nuclear_pct=17.0, wind_pct=26.0, solar_pct=4.0, hydro_pct=2.0, biomass_pct=8.0, imports_pct=3.0),
    2023: FuelMixRecord(2023, coal_pct=1.0, gas_pct=32.0, nuclear_pct=14.0, wind_pct=28.0, solar_pct=5.0, hydro_pct=2.0, biomass_pct=10.0, imports_pct=8.0),
    2024: FuelMixRecord(2024, coal_pct=0.0, gas_pct=29.0, nuclear_pct=14.0, wind_pct=32.0, solar_pct=5.0, hydro_pct=2.0, biomass_pct=11.0, imports_pct=7.0),
    2025: FuelMixRecord(2025, coal_pct=0.0, gas_pct=25.0, nuclear_pct=13.0, wind_pct=36.0, solar_pct=6.0, hydro_pct=3.0, biomass_pct=10.0, imports_pct=7.0),
}

#: THE ONE HOME OF THE GAS FACTOR. DESNZ, *Greenhouse gas reporting: conversion factors*, flat
#: file for each reporting year, Scope 1 > Fuels > Gaseous fuels > Natural gas, kWh (Gross CV),
#: kgCO2e -- read for docs/market_research/household_carbon_and_the_measures_that_save_it.md §2.
#: GROSS CV because GB gas meters are billed in kWh converted at the gross calorific value, so a
#: billed kWh is already on this basis. CO2e, NOT the CO2-only column beside it in the same file
#: (0.18253 for 2023, which `company/sustainability/environmental_impact.py` carried as "CO2e"
#: until 2026-10-05). Combustion at the point of use only: well-to-tank is a separate DESNZ factor
#: (0.03021 in the 2023-2025 sets) and is excluded, so this UNDERSTATES a household's full gas
#: chain by about 16.5%.
#:
#: 2022 IS ABSENT, NOT INTERPOLATED. The 2022 files could not be parsed; 2021 (0.18316) and 2023
#: (0.18293) bracket it within 0.13%, but a bracket is not the published number and a value
#: written here would be read as the published one. `gas_factor_kg_co2e_per_kwh(2022)` refuses.
DESNZ_NATURAL_GAS_KG_CO2E_PER_KWH_GROSS_CV = {
    2016: 0.18400, 2017: 0.18416, 2018: 0.18396, 2019: 0.18385, 2020: 0.18387,
    2021: 0.18316, 2023: 0.18293, 2024: 0.18290, 2025: 0.18296,
}

#: Why a year inside the record has no factor. Named so a refusal can say it.
GAS_FACTOR_GAPS = {
    2022: ("DESNZ's 2022 conversion-factor files could not be parsed when the factors were read "
           "(2026-10-05); 2021's 0.18316 and 2023's 0.18293 bracket it, and neither is it"),
}


class GasFactorUnavailable(ValueError):
    """No DESNZ gas factor is established for this year. Never a silent nearest-year."""


def gas_factor_kg_co2e_per_kwh(year: int) -> float:
    """DESNZ natural gas, kgCO2e per kWh gross CV, for that reporting year. Refuses, never clamps.

    A clamp here would be invisible in the answer (every year is within 0.7% of every other), and
    that is exactly why it must not happen silently: the value would be read as that year's.
    """
    year = int(year)
    if year in DESNZ_NATURAL_GAS_KG_CO2E_PER_KWH_GROSS_CV:
        return DESNZ_NATURAL_GAS_KG_CO2E_PER_KWH_GROSS_CV[year]
    raise GasFactorUnavailable(GAS_FACTOR_GAPS.get(
        year, f"no DESNZ natural-gas factor is held for {year}; the table covers "
              f"{min(DESNZ_NATURAL_GAS_KG_CO2E_PER_KWH_GROSS_CV)}-"
              f"{max(DESNZ_NATURAL_GAS_KG_CO2E_PER_KWH_GROSS_CV)}"))


#: Scope 1 factor for supplied gas, gCO2e/kWh, for a consumer that has no year to ask about. Also
#: the published value (the annual report's `Gas CO2 (t)` column). DERIVED from the table above --
#: the latest DESNZ set to the nearest gram, 183 -- so it is the same figure as before and cannot
#: drift from the sourced one. Within 0.7% of every year in the table.
GAS_EMISSION_FACTOR_G_CO2E_PER_KWH = float(round(
    1000.0 * DESNZ_NATURAL_GAS_KG_CO2E_PER_KWH_GROSS_CV[max(DESNZ_NATURAL_GAS_KG_CO2E_PER_KWH_GROSS_CV)]))

#: The published feed the level is read from. A path, not an import: the wall's sanctioned crossing.
GRID_INTENSITY_FEED = (
    Path(__file__).resolve().parents[2] / "docs" / "market_data" / "grid_intensity_feed.json")

#: Machine-readable provenance for anything that republishes the series. The feed's own
#: `annual_level.basis` is the long form; this is what a table footnote needs.
GRID_INTENSITY_PROVENANCE = {
    'quantity': 'GB national annual grid electricity carbon intensity',
    'unit': 'gCO2/kWh',
    'basis': 'demand-weighted annual mean of the half-hourly national series; generation basis, '
             'transmission and distribution losses not included; CO2 at the generator, not '
             'lifecycle',
    'source': 'NESO Historic GB Generation Mix CARBON_INTENSITY, 2016-2025; NESO methodology on '
              'Elexon FUELHH where it has no usable value -- read from '
              'docs/market_data/grid_intensity_feed.json',
    'status': 'published series; a part-year level is refused for an annual figure',
}


@dataclass(frozen=True)
class GridIntensityLevel:
    """One year's published level and what it covers. `g_co2_per_kwh` None: not published."""

    year: int
    g_co2_per_kwh: Optional[float]
    complete: bool
    covers_from: Optional[str]
    covers_to: Optional[str]
    reason: Optional[str]


_FEED_CACHE: Dict[tuple, dict] = {}


def _annual_levels(feed_path: Optional[Path] = None) -> tuple:
    """({year str: row}, why-unreadable). Re-read when the file changes, never served stale."""
    path = Path(feed_path or GRID_INTENSITY_FEED)
    try:
        stat = path.stat()
    except OSError:
        return {}, f"the grid-intensity feed {path} is not on disk"
    stamp = (str(path), stat.st_mtime_ns, stat.st_size)
    if stamp not in _FEED_CACHE:
        try:
            feed = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return {}, f"the grid-intensity feed {path} could not be read: {exc}"
        _FEED_CACHE.clear()
        _FEED_CACHE[stamp] = (feed.get("annual_level") or {}).get("by_year") or {}
    levels = _FEED_CACHE[stamp]
    if not levels:
        return {}, f"the grid-intensity feed {path} publishes no annual level"
    return levels, None


def grid_intensity_level(year: int, *, feed_path: Optional[Path] = None) -> GridIntensityLevel:
    """The published annual level for `year`, with its coverage. Never a neighbouring year's."""
    year = int(year)
    levels, why = _annual_levels(feed_path)
    row = levels.get(str(year))
    if why or row is None or row.get("mean_g_co2_per_kwh") is None:
        reason = why or (
            f"the grid-intensity feed publishes no annual level for {year}; it covers "
            f"{min(levels)}-{max(levels)}. Not clamped to a neighbouring year")
        return GridIntensityLevel(year, None, False, None, None, reason)
    covers = row.get("covers") or {}
    complete = bool(row.get("complete"))
    reason = None if complete else (
        f"the published {year} level is a mean of {covers.get('from')}..{covers.get('to')} only "
        "(Elexon's demand record bounds it), not of the year")
    return GridIntensityLevel(year, float(row["mean_g_co2_per_kwh"]), complete,
                              covers.get("from"), covers.get("to"), reason)


def grid_intensity_g_co2e_per_kwh(year: int, *, allow_partial: bool = False,
                                  feed_path: Optional[Path] = None) -> Optional[float]:
    """The ONE annual UK grid intensity in this codebase, gCO2/kWh, as NESO's series publishes it.

    None, never a clamp, when the feed has no level for the year, or only a part-year one and
    `allow_partial` is False; `grid_intensity_unavailable_reason(year)` says which. See the module
    docstring for the basis and for when `allow_partial` is right.
    """
    level = grid_intensity_level(year, feed_path=feed_path)
    if level.g_co2_per_kwh is None or (not level.complete and not allow_partial):
        return None
    return level.g_co2_per_kwh


def grid_intensity_unavailable_reason(year: int, *, allow_partial: bool = False,
                                      feed_path: Optional[Path] = None) -> Optional[str]:
    """Why `grid_intensity_g_co2e_per_kwh(year, ...)` returned None; None when it did not."""
    level = grid_intensity_level(year, feed_path=feed_path)
    if level.g_co2_per_kwh is None or (not level.complete and not allow_partial):
        return level.reason
    return None


@dataclass(frozen=True)
class CustomerCarbonFootprint:
    customer_id: str
    year: int
    electricity_kwh: float
    gas_kwh: float
    electricity_intensity_g_per_kwh: float

    _GAS_EMISSION_FACTOR_G_PER_KWH = GAS_EMISSION_FACTOR_G_CO2E_PER_KWH

    @property
    def electricity_co2_kg(self) -> float:
        return round(self.electricity_kwh * self.electricity_intensity_g_per_kwh / 1000, 1)

    @property
    def gas_co2_kg(self) -> float:
        return round(self.gas_kwh * self._GAS_EMISSION_FACTOR_G_PER_KWH / 1000, 1)

    @property
    def total_co2_kg(self) -> float:
        return round(self.electricity_co2_kg + self.gas_co2_kg, 1)

    @property
    def total_co2_tonnes(self) -> float:
        return round(self.total_co2_kg / 1000, 3)

    def summary(self) -> dict:
        return {
            'customer_id': self.customer_id,
            'year': self.year,
            'electricity_kwh': self.electricity_kwh,
            'gas_kwh': self.gas_kwh,
            'electricity_co2_kg': self.electricity_co2_kg,
            'gas_co2_kg': self.gas_co2_kg,
            'total_co2_kg': self.total_co2_kg,
            'total_co2_tonnes': self.total_co2_tonnes,
        }


def build_customer_footprint(
    customer_id: str, year: int,
    electricity_kwh: float, gas_kwh: float,
    fuel_mix: FuelMixRecord,
) -> CustomerCarbonFootprint:
    return CustomerCarbonFootprint(
        customer_id=customer_id, year=year,
        electricity_kwh=electricity_kwh, gas_kwh=gas_kwh,
        electricity_intensity_g_per_kwh=fuel_mix.emission_intensity_g_per_kwh,
    )
