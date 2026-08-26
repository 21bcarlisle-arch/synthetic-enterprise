"""Elexon's published half-hourly generation mix — the two things the dispatch model cannot know.

REUSE: sim/elexon_fuel_outturn.py
CLASS: CUSTOM
INDEX: searched "fuel", "FUELHH", "fuel mix", "generation", "outturn", "interconnector",
       "import", "coal", "elexon". Three organs came back and none of them is this.
       `sim/generation_demand_history.py` fetches the SAME API and is the fetch/cache pattern
       reused here verbatim, but it pulls exactly two series (demand outturn, wind-and-solar)
       and neither carries coal or a cross-border flow. `company/sustainability/
       carbon_intensity_register.py` holds the statutory Fuel Mix Disclosure, which is an
       ANNUAL supplier-level percentage split and shares no grain with this. `sim/
       merit_order_reconstruction.py` already knows what coal EMITS and what it COSTS; what it
       has never had is how much of it there was to run.

WHY THIS EXISTS
---------------
`sim/grid_carbon_intensity.py` reconstructs the half-hourly carbon shape of the GB grid from
residual demand through a dispatch model, and it names its own error bars. Two of them were
measured against NESO's published series on 2026-08-25 and are the reason that atom's level did
not move:

    NO COAL IS DISPATCHED ... so the shape UNDERSTATES the dirty end of coal-heavy years
    INTERCONNECTOR IMPORTS ARE NOT MODELLED ... so hours of heavy import read dirtier here

Both make the CLEAN end of the shape cleaner than GB actually was, and the measurement put a
size on it: our p95/p5 spread runs 3.27 (2019) to 18.42 (2024) where NESO's runs 2.78 to 5.06.

Neither gap can be closed from inside the dispatch model, and for two DIFFERENT reasons, which
is why this module draws a line down the middle of what it supplies:

  * CROSS-BORDER FLOW IS EXOGENOUS. Whether GB imports 3 GW from France in a given half hour is
    decided by the FRENCH day-ahead price against the GB one. Nothing about GB residual demand
    determines it, and no amount of GB merit-order modelling will produce it. So the flow is
    taken as an OBSERVABLE — the same class of input as the demand outturn and the wind-and-solar
    outturn the reconstruction already runs on, from the same publisher and the same API.
  * COAL AVAILABILITY IS STRUCTURAL. How much coal capacity GB still had in 2019 is a fleet fact,
    not a half-hourly decision. So this module supplies the CAPACITY (the fleet's demonstrated
    annual maximum, measured from the published outturn) and the reconstruction goes on deciding
    for itself, through its own merit order, how much of that capacity ran in any half hour.

THE LINE MATTERS AND IT IS NOT A STYLE PREFERENCE. The whole value of the reconstruction is that
it is an INDEPENDENT route to a quantity NESO publishes — the coupled-triad gap is the score, and
a reconstruction that reads the metered mix and applies published factors to it would not be a
second route, it would be NESO's own arithmetic with a different cache.

Half-hourly coal outturn IS in the payload this module parses, and `to_settlement_periods` keeps
it, because the annual capacity is measured from it and a parse that threw it away could not be
re-checked. What never leaves this module at half-hourly grain is coal as a DISPATCH INPUT:
`imports_by_period` — the only per-half-hour view the reconstruction is handed — carries cables
and nothing else, and `coal_capacity_by_year` collapses the coal series to one number a year
before it crosses the boundary. Two tests hold that line rather than this paragraph:
`test_the_only_half_hourly_view_handed_to_the_reconstruction_carries_no_coal`, and
`test_the_reconstruction_does_not_import_this_module` — because a shape module that can reach
in here for the metered mix is one edit away from being NESO's arithmetic with a different cache.

WHAT ELEXON PUBLISHES
---------------------
`data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH` — key-free, half-hourly, settlement-date keyed,
one row per fuel type per settlement period. Interconnector rows are SIGNED: positive is import
into GB, negative is export out of it.

CARBON INTENSITY OF AN IMPORT is not Elexon's to publish, and this module does not invent one.
The factors are NESO's OWN, from the published methodology behind the very series the
reconstruction is graded against (Carbon Intensity Forecast Methodology, Table 1, and the live
`api.carbonintensity.org.uk/intensity/factors` endpoint, which agrees with it):

    French Imports ~53   Dutch Imports ~474   Belgium Imports ~179   Irish Imports ~458

NAMED GAP, MEASURED RATHER THAN ASSERTED: that table predates three of GB's interconnectors.
North Sea Link (Norway, Oct 2021), Viking Link (Denmark, Dec 2023) and ElecLink (France, May
2022) have no published factor in it. ElecLink lands on the French border and is given the
French factor, which is the methodology's own rule applied to the same network. The other two
are NOT given a factor — a plausible one is exactly the fabricated number R10 forbids — so their
flow is reported SEPARATELY as `uncovered_import_mw` and `import_coverage()` states, as a
measured fraction of imported MWh, how much of the answer that leaves outside. A gap you can
quote in per cent is a different object from a gap you can only name.

Run:  python3 -m sim.elexon_fuel_outturn --from 2016-01-01 --to 2025-12-31
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections.abc import Iterable, Mapping
from datetime import date as date_cls
from datetime import timedelta
from pathlib import Path

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
DATASET_ENDPOINT = "/datasets/FUELHH"

#: The API refuses a wider settlement-date range on this dataset. A documented limit, not a knob.
MAX_WINDOW_DAYS = 7

CACHE_PATH = Path("sim/cache/elexon_fuelhh_carbon_relevant.json")

#: A SECOND FILE RATHER THAN TWO MORE FUEL TYPES IN THE FIRST, and the reason is operational, not
#: architectural. `CACHE_PATH` is 235 MB and the live producer re-reads the working tree every
#: cycle; rewriting it in place to widen the fuel filter means a window in which the running sim
#: sees a truncated file. Same module, same fetch pattern, same publisher — a separate path is
#: what makes adding the thermal series a create rather than a rewrite.
THERMAL_CACHE_PATH = Path("sim/cache/elexon_fuelhh_thermal.json")

#: A THIRD file, for the reason the second one exists: the two live caches are 235 MB and 63 MB
#: and the sim producer re-reads the working tree every cycle, so widening a fuel filter in place
#: is a window in which a running process sees a truncated file. A new path is a create.
ZERO_CARBON_MUST_RUN_CACHE_PATH = Path("sim/cache/elexon_fuelhh_zero_carbon_must_run.json")

#: The fuel types this module reads. EVERY OTHER ROW IS DISCARDED AT FETCH, and the discard is
#: the reduction that makes the cache 50 MB instead of 300 MB — so it is named here rather than
#: left for a reader to infer from a file listing. A cache is a reduced extract or it is raw, and
#: which one it is has to be legible from the module that wrote it.
COAL_FUEL_TYPE = "COAL"

#: The GB thermal fleet, for the FLOOR measurement only. See `thermal_floor_by_year` for the
#: single scalar per year these produce and why nothing finer than that ever crosses the
#: boundary into the reconstruction.
THERMAL_FUEL_TYPES = ("CCGT", "OCGT")

#: The ZERO-CARBON MUST-RUN fleet, and this is the one series in this module that crosses the
#: boundary at HALF-HOURLY grain. Every other half-hourly view here is held back to one scalar a
#: year, so the exception needs a reason that is checkable rather than argued.
#:
#: TWO CONDITIONS, BOTH TESTED, and it takes both. A fuel may be handed over half-hourly only if:
#:
#:   1. NESO'S OWN PUBLISHED FACTOR FOR IT IS EXACTLY ZERO, so nothing about the answer crosses.
#:      Handing this series over transfers no emissions term at all: every gram in the
#:      reconstructed number still comes from the merit order this project decides for itself.
#:      That is the whole difference from half-hourly gas or coal, which ARE the answer.
#:   2. THE PUBLISHED OUTTURN IS NEVER NEGATIVE, which is what separates an AVAILABILITY from a
#:      DISPATCH DECISION. Condition 1 alone is not enough and the counter-example is in the same
#:      table: NESO publishes PUMPED STORAGE at zero too, and pumped storage is pure arbitrage —
#:      it is the merit order, wearing a zero factor. It gives itself away by going negative when
#:      it pumps. Nuclear and run-of-river hydro cannot: their output IS their availability, set
#:      by which reactors are online and how much water is coming down the hill, and neither is
#:      answering the question the reconstruction exists to answer.
#:
#: WHY THE GRAIN IS DIFFERENT FROM COAL'S, which is handed over as one capacity per year. Coal's
#: half-hourly output is a dispatch decision, so only its AVAILABILITY may cross, and availability
#: for a fleet is an annual fact. For nuclear and hydro, availability itself moves half hour by
#: half hour — an outage is not an annual event — so the annual grain would discard the very thing
#: being handed over. Same rule, different fleet.
ZERO_CARBON_MUST_RUN_FUEL_TYPES = ("NUCLEAR", "NPSHYD")

#: NESO's OWN published generation factors, gCO2/kWh, fetched from
#: `api.carbonintensity.org.uk/intensity/factors` (the same table as the Carbon Intensity Forecast
#: Methodology). NOT this project's numbers: the reconstruction is graded against the series these
#: build, so the test that condition 1 above holds has to read NESO's figure and not ours.
#:
#: PUMPED STORAGE AND SOLAR AND WIND ARE CARRIED DELIBERATELY, at zero, even though this module
#: hands none of them over. A table containing only the fuels that pass the test could not fail
#: the test (R15 TAUTOLOGY): the entries that make it a real check are the ones sitting at zero
#: that are still refused.
NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH = {
    "BIOMASS": 120.0,
    "CCGT": 394.0,
    "COAL": 937.0,
    "NPSHYD": 0.0,      # "Hydro"
    "NUCLEAR": 0.0,
    "OCGT": 651.0,
    "OIL": 935.0,
    "OTHER": 300.0,
    "PS": 0.0,          # "Pumped Storage" -- zero-factor and still refused; see condition 2
    "SOLAR": 0.0,
    "WIND": 0.0,
}

#: Elexon fuel type -> the connected market, for every GB interconnector in the dataset.
INTERCONNECTOR_MARKETS = {
    "INTFR": "France",        # IFA, 2 GW, from 1986
    "INTIFA2": "France",      # IFA2, 1 GW, from Jan 2021
    "INTELEC": "France",      # ElecLink, 1 GW, from May 2022
    "INTIRL": "Ireland",      # Moyle (Northern Ireland), 0.5 GW
    "INTEW": "Ireland",       # EWIC (Republic of Ireland), 0.5 GW
    "INTNED": "Netherlands",  # BritNed, 1 GW
    "INTNEM": "Belgium",      # Nemo Link, 1 GW, from Jan 2019
    "INTNSL": "Norway",       # North Sea Link, 1.4 GW, from Oct 2021
    "INTVKL": "Denmark",      # Viking Link, 1.4 GW, from Dec 2023
}

#: NESO's OWN published import factors (gCO2/kWh), Carbon Intensity Forecast Methodology Table 1
#: and `api.carbonintensity.org.uk/intensity/factors`. NOT this project's numbers and not tuned:
#: the reconstruction is graded against the series these factors build, so using anything else
#: would put a factor difference into a comparison meant to measure a TIMING difference.
#:
#: Norway and Denmark are absent ON PURPOSE. See the module docstring: the published table has no
#: factor for them, and the honest handling of a missing published number is to report the hole,
#: not to fill it.
IMPORT_INTENSITY_G_CO2_PER_KWH = {
    "France": 53.0,
    "Netherlands": 474.0,
    "Belgium": 179.0,
    "Ireland": 458.0,
}


class FuelOutturnUnavailable(Exception):
    """The published mix could not be obtained or held nothing usable.

    Raised rather than returning zeros, and the direction is why: ZERO IMPORTS AND ZERO COAL IS
    A VALID-LOOKING ANSWER that reproduces exactly the pre-2026-08-25 behaviour of the shape —
    the behaviour whose error this module was written to remove. A silent revert to the known-
    wrong model is the worst available failure, so absence is raised (R15 FAIL-OPEN, FAIL-SILENT).
    """


def _fetch_window(start: date_cls, end: date_cls, *, timeout: float = 90.0) -> list[dict]:
    """One settlement-date window, already reduced to the carbon-relevant fuel types."""
    url = (
        f"{BASE_URL}{DATASET_ENDPOINT}?settlementDateFrom={start.isoformat()}"
        f"&settlementDateTo={end.isoformat()}&format=json"
    )
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        raise FuelOutturnUnavailable(f"Elexon FUELHH fetch failed for {url}: {exc}") from exc
    data = payload.get("data")
    if not isinstance(data, list):
        raise FuelOutturnUnavailable(f"Elexon returned no `data` list for {url}: {payload!r}")
    keep = {COAL_FUEL_TYPE, *INTERCONNECTOR_MARKETS}
    return [row for row in data if row.get("fuelType") in keep]


def _fetch_thermal_window(start: date_cls, end: date_cls, *, timeout: float = 90.0) -> list[dict]:
    """One settlement-date window, reduced to the thermal fuel types."""
    url = (
        f"{BASE_URL}{DATASET_ENDPOINT}?settlementDateFrom={start.isoformat()}"
        f"&settlementDateTo={end.isoformat()}&format=json"
    )
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        raise FuelOutturnUnavailable(f"Elexon FUELHH fetch failed for {url}: {exc}") from exc
    data = payload.get("data")
    if not isinstance(data, list):
        raise FuelOutturnUnavailable(f"Elexon returned no `data` list for {url}: {payload!r}")
    keep = set(THERMAL_FUEL_TYPES)
    return [row for row in data if row.get("fuelType") in keep]


def _fetch_zero_carbon_window(start: date_cls, end: date_cls, *, timeout: float = 90.0) -> list[dict]:
    """One settlement-date window, reduced to the zero-carbon must-run fuel types."""
    url = (
        f"{BASE_URL}{DATASET_ENDPOINT}?settlementDateFrom={start.isoformat()}"
        f"&settlementDateTo={end.isoformat()}&format=json"
    )
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        raise FuelOutturnUnavailable(f"Elexon FUELHH fetch failed for {url}: {exc}") from exc
    data = payload.get("data")
    if not isinstance(data, list):
        raise FuelOutturnUnavailable(f"Elexon returned no `data` list for {url}: {payload!r}")
    keep = set(ZERO_CARBON_MUST_RUN_FUEL_TYPES)
    return [row for row in data if row.get("fuelType") in keep]


def _walk(start_date: str, end_date: str, window_fetcher, pause_s: float) -> list[dict]:
    """Walk [start_date, end_date] in the API's own window size, one fetcher per fuel filter."""
    start = date_cls.fromisoformat(start_date)
    end = date_cls.fromisoformat(end_date)
    if end < start:
        raise ValueError(f"end {end_date} precedes start {start_date}")

    out: list[dict] = []
    cursor = start
    while cursor <= end:
        window_end = min(cursor + timedelta(days=MAX_WINDOW_DAYS - 1), end)
        out.extend(window_fetcher(cursor, window_end))
        cursor = window_end + timedelta(days=1)
        if cursor <= end:
            time.sleep(pause_s)
    if not out:
        raise FuelOutturnUnavailable(f"no rows returned for {start_date}..{end_date}")
    return out


def fetch(start_date: str, end_date: str, *, pause_s: float = 0.1) -> list[dict]:
    """Raw rows over [start_date, end_date], walked in the API's own window size.

    Rows keep Elexon's field names and Elexon's sign convention untouched, so a cache written
    today stays re-parsable if `to_settlement_periods` is ever found wrong.
    """
    return _walk(start_date, end_date, _fetch_window, pause_s)


def fetch_thermal(start_date: str, end_date: str, *, pause_s: float = 0.1) -> list[dict]:
    """The same walk, keeping CCGT and OCGT instead of coal and the cables."""
    return _walk(start_date, end_date, _fetch_thermal_window, pause_s)


def fetch_zero_carbon_must_run(start_date: str, end_date: str, *, pause_s: float = 0.1) -> list[dict]:
    """The same walk, keeping the zero-carbon must-run fleet instead of coal and the cables."""
    return _walk(start_date, end_date, _fetch_zero_carbon_window, pause_s)


def to_settlement_periods(rows: Iterable[Mapping]) -> dict[tuple[str, int], dict[str, float]]:
    """Raw rows -> {(settlement date, period): {coal_mw, covered_import_mw, uncovered_import_mw,
    covered_import_t_per_mwh}}.

    THE SIGN IS THE SUBSTANCE. An interconnector row is negative when GB is EXPORTING, and an
    export is not a negative import: it is GB generating for somebody else. Netting the two
    together across a half hour would let an export on one cable cancel a genuinely dirty Dutch
    import on another and quietly clean up the half hour. So each cable is clamped at zero
    INDIVIDUALLY and only the importing ones contribute.

    Exports are then DROPPED rather than modelled, and that is a stated choice with a direction.
    The quantity being built is gCO2 per kWh of GB DEMAND; under that consumption basis the
    emissions of an exported MWh belong to the country that consumed it. Charging them to GB
    demand would make export hours read dirtier than they were. NAMED GAP: nothing here credits
    GB for exporting clean power either.

    A ROW WITH A NON-NUMERIC OR ABSENT `generation` IS SKIPPED, never defaulted to zero — zero
    import is a perfectly plausible reading (cables do sit idle) and would be indistinguishable
    from a hole in the feed, which is the exact failure `neso_carbon_intensity` found the hard way
    when NESO published `actual: 0` for a feed outage.

    LAST ROW WINS for a repeated (date, period, fuel): FUELHH is republished with revisions and
    a revision is the better number, the same rule `aggregate_demand` already applies to INDO.
    """
    coal: dict[tuple[str, int], float] = {}
    covered: dict[tuple[str, int], float] = {}
    covered_tonnes: dict[tuple[str, int], float] = {}
    uncovered: dict[tuple[str, int], float] = {}
    # Deduplicate per (key, fuel) FIRST, because "last row wins" has to be resolved before the
    # cables are summed — summing as we go would add a revised reading to the one it revises.
    latest: dict[tuple[tuple[str, int], str], float] = {}
    for row in rows:
        date_str = row.get("settlementDate")
        period = row.get("settlementPeriod")
        fuel = row.get("fuelType")
        value = row.get("generation")
        if date_str is None or period is None or fuel is None or value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        try:
            key = (str(date_str), int(period))
        except (TypeError, ValueError):
            continue
        latest[(key, str(fuel))] = float(value)

    for (key, fuel), value in latest.items():
        if fuel == COAL_FUEL_TYPE:
            # Coal is never negative in this dataset, but a negative reading would be a feed
            # defect and must not become negative emissions.
            coal[key] = max(0.0, value)
            continue
        market = INTERCONNECTOR_MARKETS.get(fuel)
        if market is None:
            continue
        imported = max(0.0, value)
        if imported <= 0.0:
            covered.setdefault(key, 0.0)
            uncovered.setdefault(key, 0.0)
            continue
        factor = IMPORT_INTENSITY_G_CO2_PER_KWH.get(market)
        if factor is None:
            uncovered[key] = uncovered.get(key, 0.0) + imported
            covered.setdefault(key, 0.0)
            continue
        covered[key] = covered.get(key, 0.0) + imported
        covered_tonnes[key] = covered_tonnes.get(key, 0.0) + imported * factor / 1000.0
        uncovered.setdefault(key, 0.0)

    keys = set(coal) | set(covered) | set(uncovered)
    if not keys:
        raise FuelOutturnUnavailable(
            "no half hour carried a usable coal or interconnector reading. This is an absence, "
            "not a grid without coal or cables."
        )
    out: dict[tuple[str, int], dict[str, float]] = {}
    for key in keys:
        covered_mw = covered.get(key, 0.0)
        out[key] = {
            "coal_mw": coal.get(key, 0.0),
            "covered_import_mw": covered_mw,
            "uncovered_import_mw": uncovered.get(key, 0.0),
            # The MW-weighted mean factor of the cables actually importing in THIS half hour, in
            # tonnes per MWh so the reconstruction never has to convert units at a call site.
            "covered_import_t_per_mwh": (
                (covered_tonnes.get(key, 0.0) / covered_mw) if covered_mw > 0.0 else 0.0
            ),
        }
    return out


def imports_by_period(
    series: Mapping[tuple[str, int], Mapping[str, float]],
) -> dict[tuple[str, int], tuple[float, float]]:
    """{(date, period): (covered import MW, its tonnes/MWh)} — what the reconstruction consumes.

    Only the COVERED flow is handed over. An import with no published factor is not passed with
    a guessed one and is not passed with zero either; it simply is not in this mapping's
    numbers, which leaves it modelled as GB generation exactly as it was before — the old,
    known, named behaviour — instead of a new and undocumented one.
    """
    return {
        key: (float(value.get("covered_import_mw") or 0.0),
              float(value.get("covered_import_t_per_mwh") or 0.0))
        for key, value in series.items()
    }


def import_coverage(
    series: Mapping[tuple[str, int], Mapping[str, float]], year: str | None = None
) -> dict[str, float]:
    """How much of GB's imported energy this module can actually price, as a MEASURED fraction.

    The number the NAMED GAP paragraph is allowed to quote. Reported in MWh-share rather than
    cable-count because two of the nine cables being unpriced says nothing about how much energy
    that is: Norway's 1.4 GW link runs harder than Ireland's 0.5 GW pair combined.
    """
    covered = uncovered = 0.0
    for key, value in series.items():
        if year is not None and key[0][:4] != year:
            continue
        covered += float(value.get("covered_import_mw") or 0.0)
        uncovered += float(value.get("uncovered_import_mw") or 0.0)
    total = covered + uncovered
    if total <= 0.0:
        raise FuelOutturnUnavailable(
            f"no imported MW at all in {year or 'the series'}, so coverage is undefined. "
            "GB has never gone a year without importing; this is an absence."
        )
    return {
        "covered_mw_sum": covered,
        "uncovered_mw_sum": uncovered,
        "covered_fraction": covered / total,
    }


def coal_capacity_by_year(
    series: Mapping[tuple[str, int], Mapping[str, float]],
) -> dict[int, float]:
    """{year: the coal fleet's DEMONSTRATED maximum output that year, MW}.

    A MEASUREMENT, AND THE DISTINCTION IS THE POINT. This is not installed capacity from a
    register and it is not a number chosen to make anything come out right; it is the largest
    coal output Elexon published in that calendar year, which is a fact about what the fleet was
    able to do. It falls to zero of its own accord when the last unit closes, so the atom's
    "coal was gone by Sep 2024" needs no hand-written end date and cannot be wrong about one.

    R13: nothing downstream may adjust this to move the company's numbers. It moves only if
    Elexon republishes the outturn.
    """
    out: dict[int, float] = {}
    for key, value in series.items():
        try:
            year = int(key[0][:4])
        except (TypeError, ValueError):
            continue
        mw = float(value.get("coal_mw") or 0.0)
        # THE YEAR IS ENTERED BEFORE THE MAXIMUM IS COMPARED, so a year whose coal fleet
        # generated nothing appears as 0.0 rather than not appearing. The difference matters
        # where this gets published: a missing 2025 row reads as "the series stops here", and a
        # present `0` reads as "the fleet closed" -- which is the fact.
        out.setdefault(year, 0.0)
        if mw > out[year]:
            out[year] = mw
    if not out:
        raise FuelOutturnUnavailable("no coal reading in any year, so no capacity can be measured")
    return out


def thermal_by_period(rows: Iterable[Mapping]) -> dict[tuple[str, int], float]:
    """{(date, period): CCGT + OCGT MW} — the raw thermal outturn, for MEASUREMENT ONLY.

    THIS MAPPING MUST NEVER REACH THE RECONSTRUCTION, and the reason is the same one that keeps
    half-hourly coal inside this module: a dispatch model handed the metered gas output of each
    half hour is not an independent route to NESO's number, it is NESO's arithmetic with a
    different cache, and the coupled-triad gap it is graded on would be measuring nothing. What
    crosses the boundary is `thermal_floor_by_year`, one scalar per year.
    `test_the_reconstruction_is_handed_no_half_hourly_gas` holds that line rather than this
    paragraph.

    BOTH FUELS MUST BE PRESENT IN A HALF HOUR or it is skipped. A missing CCGT reading is a hole
    in the feed, and a hole summed as zero would read as a half hour in which GB ran no gas —
    which is precisely the fiction the floor exists to remove, reintroduced by the measurement
    meant to remove it (R15 FAIL-OPEN).
    """
    latest: dict[tuple[tuple[str, int], str], float] = {}
    for row in rows:
        date_str = row.get("settlementDate")
        period = row.get("settlementPeriod")
        fuel = row.get("fuelType")
        value = row.get("generation")
        if date_str is None or period is None or fuel is None or value is None:
            continue
        if str(fuel) not in THERMAL_FUEL_TYPES:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        try:
            key = (str(date_str), int(period))
        except (TypeError, ValueError):
            continue
        # LAST ROW WINS, the same revision rule the coal and cable parse applies.
        latest[(key, str(fuel))] = float(value)

    out: dict[tuple[str, int], float] = {}
    for key in {k for k, _ in latest}:
        readings = [latest.get((key, fuel)) for fuel in THERMAL_FUEL_TYPES]
        if any(reading is None for reading in readings):
            continue
        out[key] = sum(max(0.0, float(reading)) for reading in readings)
    if not out:
        raise FuelOutturnUnavailable(
            "no half hour carried a reading for every thermal fuel type. This is an absence, not "
            "a grid that ran no gas."
        )
    return out


def thermal_floor_by_year(
    thermal_mw_by_period: Mapping[tuple[str, int], float],
) -> dict[int, dict[str, float]]:
    """{year: {floor_mw, p1_mw, half_hours}} — what GB's thermal fleet was never observed below.

    THE GAP THIS CLOSES. `grid_carbon_intensity` dispatches `residual - must_run` and lets the
    result reach exactly zero. GB's never does: there is always gas running for inertia, reserve
    and voltage, and the model's zero-thermal half hours are 0.1% of 2016 but 16.1% of 2024 and
    30.8% of 2025 — the share grows with renewables, which is why this was the largest remaining
    clean-end error and why it held the atom at L2 rather than being a footnote.

    A MEASUREMENT, NOT A RESERVE-MARGIN MODEL. This is the smallest CCGT+OCGT output Elexon
    published in the calendar year, which is a fact about what the fleet was never asked to go
    below. It is the same construction `coal_capacity_by_year` uses at the other end of the
    distribution, and it moves only if Elexon republishes the outturn (R13).

    WHY THE RAW MINIMUM AND NOT A LOW PERCENTILE, which is the one choice here that could have
    been goal-seeking. A minimum is fragile in a way a maximum is not: one dropped half hour sets
    it, where an outage can only ever lower a maximum. The robust answer is the 1st percentile —
    and the 1st percentile is also HIGHER, which means a dirtier clean end, a narrower modelled
    swing, and a shape that scores BETTER against the published series this model is graded on.
    Choosing the robust statistic here is indistinguishable from choosing the flattering one, so
    the minimum is used and `p1_mw` is published beside it as a DIAGNOSTIC a reader can check the
    minimum against (R12: reported, never consumed). Where the minimum is wrong it UNDERSTATES
    the floor, erring back toward the zero-thermal behaviour rather than past it — the same
    direction `emissions_rate_t_per_mwh` already argues for its coal ordering.

    A NON-POSITIVE READING IS DROPPED AS ABSENT rather than taken as the floor. GB's thermal
    fleet has never produced zero, so a zero is a feed dropout by construction — the lesson
    `neso_carbon_intensity` learned when NESO published `actual: 0` for five half hours and the
    first run reported the cleanest possible grid as fact.
    """
    by_year: dict[int, list[float]] = {}
    for key, mw in thermal_mw_by_period.items():
        try:
            year = int(key[0][:4])
        except (TypeError, ValueError):
            continue
        value = float(mw)
        if value <= 0.0:
            continue
        by_year.setdefault(year, []).append(value)

    out: dict[int, dict[str, float]] = {}
    for year, values in by_year.items():
        values.sort()
        # Nearest-rank, the same rule `neso_carbon_intensity._percentile` uses, so the two
        # percentile implementations in this tree cannot report different things about the
        # same tail.
        index = min(len(values) - 1, max(0, int(0.01 * len(values))))
        out[year] = {
            "floor_mw": values[0],
            "p1_mw": values[index],
            "half_hours": float(len(values)),
        }
    if not out:
        raise FuelOutturnUnavailable(
            "no positive thermal reading in any year, so no floor can be measured"
        )
    return out


def zero_carbon_must_run_by_period(
    rows: Iterable[Mapping],
) -> dict[tuple[str, int], float]:
    """{(date, period): NUCLEAR + NPSHYD MW} — the fleet the reconstruction cannot infer.

    THE GAP THIS CLOSES, and it is a TIMING gap rather than a level one, which is what makes it
    different from the three corrections before it. `grid_carbon_intensity` has always served the
    must-run block from a FLAT 8,000 MW, of which 5,600 MW is nuclear and hydro. GB's is not flat
    and never was: over 2016-2025 this series moves by gigawatts within a single week as reactors
    go off for refuelling and river flow rises and falls. Every megawatt of that movement is a
    megawatt the model made the gas stack serve on a schedule of its own invention — so the
    residual it dispatches against has been wrong in a time-varying way, in exactly the axis
    (correlation, 0.726 in 2024) that the thermal floor left untouched and that holds this atom
    at L2.

    WHY THIS MAY CROSS AT HALF-HOURLY GRAIN when gas and coal may not: see the two conditions on
    `ZERO_CARBON_MUST_RUN_FUEL_TYPES`. Both are tested, and condition 2 is the load-bearing one —
    a zero published factor alone would also admit pumped storage, which is the merit order in
    disguise.

    BOTH FUELS MUST BE PRESENT IN A HALF HOUR or it is skipped, the same call
    `thermal_by_period` makes and for the same reason: a missing NUCLEAR row summed as zero would
    hand the dispatch a half hour in which GB ran no reactors, which is a fiction this series
    exists to remove, reintroduced by the parse meant to remove it (R15 FAIL-OPEN).

    A SKIPPED HALF HOUR IS NOT A ZERO ONE. The caller finds no key and falls back to the flat
    5,600 MW — the behaviour this series is correcting, which is bounded and already published,
    rather than a half hour with no baseload at all. That is the same direction-of-error argument
    `build_shape` already makes for a missing import reading.

    A NEGATIVE READING IS REFUSED as absent, and it is not a formality: condition 2 above is the
    entire reason this series is allowed across the boundary at this grain, so a negative reading
    means the claim that these fuels cannot store has stopped being true and the half hour must
    not be used. `zero_carbon_must_run_coverage` counts them so the refusal is visible rather
    than silent.

    A ZERO SUM IS A DROPOUT. GB has not had its entire nuclear and hydro fleet at zero output in
    this window, so a total of exactly zero is a feed hole — the lesson `neso_carbon_intensity`
    learned when NESO published `actual: 0` and the first run reported the cleanest possible grid
    as fact. Individual zeros are kept: one fleet at zero while the other runs is a fact.
    """
    latest: dict[tuple[tuple[str, int], str], float] = {}
    for row in rows:
        date_str = row.get("settlementDate")
        period = row.get("settlementPeriod")
        fuel = row.get("fuelType")
        value = row.get("generation")
        if date_str is None or period is None or fuel is None or value is None:
            continue
        if str(fuel) not in ZERO_CARBON_MUST_RUN_FUEL_TYPES:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        try:
            key = (str(date_str), int(period))
        except (TypeError, ValueError):
            continue
        # LAST ROW WINS, the same revision rule the coal, cable and thermal parses apply.
        latest[(key, str(fuel))] = float(value)

    out: dict[tuple[str, int], float] = {}
    for key in {k for k, _ in latest}:
        readings = [latest.get((key, fuel)) for fuel in ZERO_CARBON_MUST_RUN_FUEL_TYPES]
        if any(reading is None for reading in readings):
            continue
        if any(float(reading) < 0.0 for reading in readings):
            continue
        total = sum(float(reading) for reading in readings)
        if total <= 0.0:
            continue
        out[key] = total
    if not out:
        raise FuelOutturnUnavailable(
            "no half hour carried a usable reading for every zero-carbon must-run fuel type. "
            "This is an absence, not a grid that ran no nuclear."
        )
    return out


def zero_carbon_must_run_coverage(rows: Iterable[Mapping]) -> dict[str, float]:
    """How much of the series got a real reading, and how much fell back to the flat block.

    PUBLISHED BESIDE THE FEED, because the fallback is invisible in the shape itself: a half hour
    served from the flat 5,600 MW and a half hour served from a measured 5,600 MW produce the
    identical number, and only this count can tell a reader which happened. A correction whose
    coverage is unstated is a correction that can quietly stop applying (R15 FAIL-SILENT).

    `negative_half_hours` is the one to watch. It is zero on the published outturn today, and the
    day it is not, the second condition that lets this series cross the boundary at half-hourly
    grain has failed and the crossing has to be re-argued rather than re-clamped.
    """
    latest: dict[tuple[tuple[str, int], str], float] = {}
    for row in rows:
        date_str = row.get("settlementDate")
        period = row.get("settlementPeriod")
        fuel = row.get("fuelType")
        value = row.get("generation")
        if date_str is None or period is None or fuel is None or value is None:
            continue
        if str(fuel) not in ZERO_CARBON_MUST_RUN_FUEL_TYPES:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        try:
            latest[((str(date_str), int(period)), str(fuel))] = float(value)
        except (TypeError, ValueError):
            continue

    keys = {k for k, _ in latest}
    usable = 0
    missing_fuel = 0
    negative = 0
    zero_sum = 0
    values: list[float] = []
    for key in keys:
        readings = [latest.get((key, fuel)) for fuel in ZERO_CARBON_MUST_RUN_FUEL_TYPES]
        if any(reading is None for reading in readings):
            missing_fuel += 1
            continue
        if any(float(reading) < 0.0 for reading in readings):
            negative += 1
            continue
        total = sum(float(reading) for reading in readings)
        if total <= 0.0:
            zero_sum += 1
            continue
        usable += 1
        values.append(total)
    if not keys:
        raise FuelOutturnUnavailable("no half hour carried any zero-carbon must-run row at all")
    return {
        "half_hours_seen": float(len(keys)),
        "usable_half_hours": float(usable),
        "usable_fraction": usable / len(keys),
        "missing_fuel_half_hours": float(missing_fuel),
        "negative_half_hours": float(negative),
        "zero_sum_half_hours": float(zero_sum),
        "min_mw": min(values) if values else 0.0,
        "max_mw": max(values) if values else 0.0,
        "mean_mw": (sum(values) / len(values)) if values else 0.0,
    }


def load_cached_zero_carbon_must_run() -> list[dict]:
    """The cached zero-carbon must-run rows, or a refusal — never an empty list as a cache hit.

    Absence is raised for the reason the other two loaders raise it: a missing series silently
    restores the flat block this measurement exists to remove, and a shape that reverts to a
    known-wrong form without saying so is the worst available failure.
    """
    if not ZERO_CARBON_MUST_RUN_CACHE_PATH.exists():
        raise FuelOutturnUnavailable(
            f"{ZERO_CARBON_MUST_RUN_CACHE_PATH} does not exist. Run "
            "`python3 -m sim.elexon_fuel_outturn --zero-carbon-must-run` to build it. An absent "
            "series is a shape whose baseload is flat, not a grid whose reactors never moved."
        )
    rows = json.loads(ZERO_CARBON_MUST_RUN_CACHE_PATH.read_text())
    if not rows:
        raise FuelOutturnUnavailable(f"{ZERO_CARBON_MUST_RUN_CACHE_PATH} is empty")
    return rows


def write_zero_carbon_must_run_cache(rows: list[dict]) -> None:
    ZERO_CARBON_MUST_RUN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ZERO_CARBON_MUST_RUN_CACHE_PATH.write_text(json.dumps(rows, separators=(",", ":")))


def load_cached() -> list[dict]:
    """The cached rows, or a refusal. Never an empty list dressed as a cache hit."""
    if not CACHE_PATH.exists():
        raise FuelOutturnUnavailable(
            f"{CACHE_PATH} does not exist. Run `python3 -m sim.elexon_fuel_outturn` to build it. "
            "An absent mix is a shape reverted to its known-wrong form, not a shape without coal."
        )
    rows = json.loads(CACHE_PATH.read_text())
    if not rows:
        raise FuelOutturnUnavailable(f"{CACHE_PATH} is empty")
    return rows


def write_cache(rows: list[dict]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(rows, separators=(",", ":")))


def load_cached_thermal() -> list[dict]:
    """The cached thermal rows, or a refusal — never an empty list dressed as a cache hit.

    Absence is raised for the same reason `load_cached` raises it: a missing thermal series
    silently restores the exact behaviour this measurement exists to remove, and a shape that
    reverts to its known-wrong form without saying so is the worst available failure.
    """
    if not THERMAL_CACHE_PATH.exists():
        raise FuelOutturnUnavailable(
            f"{THERMAL_CACHE_PATH} does not exist. Run "
            "`python3 -m sim.elexon_fuel_outturn --thermal` to build it. An absent thermal series "
            "is a shape whose stack falls to zero, not a grid that ran no gas."
        )
    rows = json.loads(THERMAL_CACHE_PATH.read_text())
    if not rows:
        raise FuelOutturnUnavailable(f"{THERMAL_CACHE_PATH} is empty")
    return rows


def write_thermal_cache(rows: list[dict]) -> None:
    THERMAL_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    THERMAL_CACHE_PATH.write_text(json.dumps(rows, separators=(",", ":")))


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Fetch and cache Elexon's half-hourly fuel mix.")
    parser.add_argument("--from", dest="start", default="2016-01-01")
    parser.add_argument("--to", dest="end", default="2025-12-31")
    # BOTH FLAGS WERE ALREADY PROMISED BY THE LOADERS' OWN ERROR MESSAGES and neither was parsed:
    # `load_cached_thermal` has told the reader to run `--thermal` since the day it was written,
    # and that command exited 2 on an unrecognised argument. Fixed on touch rather than filed.
    parser.add_argument("--thermal", action="store_true",
                        help="fetch the CCGT+OCGT series into the thermal cache instead")
    parser.add_argument("--zero-carbon-must-run", dest="zero_carbon", action="store_true",
                        help="fetch the NUCLEAR+NPSHYD series into the must-run cache instead")
    args = parser.parse_args(argv)

    if args.thermal:
        rows = fetch_thermal(args.start, args.end)
        write_thermal_cache(rows)
        floors = thermal_floor_by_year(thermal_by_period(rows))
        print(f"{len(rows):,} rows -> {len(floors):,} year(s)")
        for year, record in sorted(floors.items()):
            print(f"  {year}  thermal floor {record['floor_mw']:>8,.0f} MW "
                  f"(p1 {record['p1_mw']:>8,.0f} MW, {record['half_hours']:>7,.0f} half hours)")
        print(f"cached to {THERMAL_CACHE_PATH}")
        return 0

    if args.zero_carbon:
        rows = fetch_zero_carbon_must_run(args.start, args.end)
        write_zero_carbon_must_run_cache(rows)
        coverage = zero_carbon_must_run_coverage(rows)
        print(f"{len(rows):,} rows -> {coverage['usable_half_hours']:,.0f} usable half hours "
              f"({coverage['usable_fraction']:.2%} of {coverage['half_hours_seen']:,.0f})")
        print(f"  nuclear+hydro  min {coverage['min_mw']:,.0f} MW  "
              f"mean {coverage['mean_mw']:,.0f} MW  max {coverage['max_mw']:,.0f} MW")
        print(f"  refused: {coverage['negative_half_hours']:,.0f} negative, "
              f"{coverage['missing_fuel_half_hours']:,.0f} missing a fuel, "
              f"{coverage['zero_sum_half_hours']:,.0f} zero-sum")
        print(f"cached to {ZERO_CARBON_MUST_RUN_CACHE_PATH}")
        return 0

    rows = fetch(args.start, args.end)
    write_cache(rows)
    series = to_settlement_periods(rows)
    print(f"{len(rows):,} rows -> {len(series):,} half hours")
    coverage = import_coverage(series)
    print(f"import coverage: {coverage['covered_fraction']:.1%} of imported MWh has a published factor")
    for year, mw in sorted(coal_capacity_by_year(series).items()):
        print(f"  {year}  coal demonstrated max {mw:>8,.0f} MW")
    print(f"cached to {CACHE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
