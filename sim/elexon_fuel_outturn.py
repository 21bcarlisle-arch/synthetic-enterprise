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

#: The fuel types this module reads. EVERY OTHER ROW IS DISCARDED AT FETCH, and the discard is
#: the reduction that makes the cache 50 MB instead of 300 MB — so it is named here rather than
#: left for a reader to infer from a file listing. A cache is a reduced extract or it is raw, and
#: which one it is has to be legible from the module that wrote it.
COAL_FUEL_TYPE = "COAL"

#: The GB thermal fleet, for the FLOOR measurement only. See `thermal_floor_by_year` for the
#: single scalar per year these produce and why nothing finer than that ever crosses the
#: boundary into the reconstruction.
THERMAL_FUEL_TYPES = ("CCGT", "OCGT")

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
    args = parser.parse_args(argv)

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
