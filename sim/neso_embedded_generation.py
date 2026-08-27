"""NESO's published estimate of EMBEDDED wind and solar generation, half-hourly.

REUSE: sim/neso_embedded_generation.py
CLASS: ADAPTER
INDEX: searched "embedded", "distribution connected", "demand data", "NESO", "CKAN",
       "solar", "wind". `sim/neso_carbon_intensity.py` and `sim/elexon_fuel_outturn.py`
       are the two nearest organs and this is deliberately a THIRD file rather than a
       function inside either: it is a different PUBLISHER (NESO's CKAN datastore, not
       the Carbon Intensity API and not Elexon's BMRS), a different cache, and — the
       load-bearing difference — a different EPISTEMIC CLASS from both. Carbon intensity
       is the TRUTH SERIES this atom is graded against and may never be an input;
       FUELHH outturn is metered generation, handed over only where the line in
       `elexon_fuel_outturn` allows. This series is neither: it is a published estimate
       of generation the transmission system never sees, which a real supplier reads
       from the same public page, and it is therefore a LEGITIMATE INPUT.

WHY THIS EXISTS
---------------
`docs/design/simplifications/EP13_adapter_carbon_intensity.yaml` records seven passes of
this atom, and the seventh retired the whole remaining dispatch programme by measuring its
ceiling: the best possible function of the model's OWN INPUTS beats the shipped shape by at
most +0.0295 in any year, and in 2024 — the year holding the level — scores BELOW it out of
sample. The conclusion recorded there is the reason this file exists, quoted:

    "L3 therefore needs a NEW INPUT carrying within-day timing, not a better model of the
     inputs it has; embedded generation is the hypothesis and is DISCOVER work, unmeasured."

This is the adapter that makes the hypothesis measurable. It does not decide it — that is
`tools/ep13_embedded_generation_bound.py`, which measures the input's ceiling BEFORE any
dispatch work is built on it, exactly as the biomass pass did one term down and the input
ceiling did one level up. Two candidate builds have now been retired by measuring first.

WHY EMBEDDED GENERATION IS NOT ALREADY IN THE MODEL'S INPUTS, which is the whole question:
the reconstruction's demand series is Elexon's INDO, metered at the TRANSMISSION boundary,
and its renewable series is Elexon's AGWS, which is transmission-connected wind and solar.
Generation embedded in the distribution networks is invisible to both — it appears only as
demand that did not arrive. So the model currently reads a summer midday dip and cannot tell
a country using less electricity from a country generating it under the metering point. Those
two have OPPOSITE carbon consequences and the same signature in the inputs the model has.
That is a within-day confusion by construction, which is why it is the standing hypothesis
for the within-day axis holding L3.

WHAT THIS SERIES IS, and its limits, stated here because they bound every conclusion drawn
downstream: NESO's EMBEDDED_WIND_GENERATION and EMBEDDED_SOLAR_GENERATION are ESTIMATES, not
meter reads. Embedded plant is largely unmetered at the national level; NESO derives these
from capacity registers and a weather-driven model, and publishes the capacity alongside
(EMBEDDED_*_CAPACITY) so the estimate can be read as a load factor. An estimate built from a
weather model is a legitimate input — a real supplier reads exactly this page — but it is NOT
independent evidence about the weather, and a gain measured against it is a gain against
NESO's estimate of embedded output rather than against embedded output itself.

HISTORICAL GROUND TRUTH: this hits the real NESO CKAN datastore (api.neso.energy), key-free,
one resource per calendar year. No synthetic data. Cached to sim/cache so the measurement is
reproducible without the network, and so a rerun costs nothing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

import requests

PROJECT = Path(__file__).resolve().parent.parent
CACHE_PATH = PROJECT / "sim" / "cache" / "neso_embedded_generation.json"

CKAN_BASE = "https://api.neso.energy/api/3/action/datastore_search"

#: Resource ids for NESO's "Historic Demand Data", one CSV per calendar year, read from
#: package_show for `historic-demand-data`. Pinned rather than discovered at call time so a
#: rerun reads the SAME resources a recorded measurement read; a silently re-pointed resource
#: is how a cached comparison stops comparing what it says it compares.
RESOURCE_IDS = {
    "2016": "3bb75a28-ab44-4a0b-9b1c-9be9715d3c44",
    "2017": "2f0f75b8-39c5-46ff-a914-ae38088ed022",
    "2018": "fcb12133-0db0-4f27-a4a5-1669fd9f6d33",
    "2019": "dd9de980-d724-415a-b344-d8ae11321432",
    "2020": "33ba6857-2a55-479f-9308-e5c4c53d4381",
    "2021": "18c69c42-f20d-46f0-84e9-e279045befc6",
    "2022": "bb44a1b5-75b1-4db2-8491-257f23385006",
    "2023": "bf5ab335-9b40-4ea4-b93a-ab4af7bce003",
    "2024": "f6d02c0f-957b-48cb-82ee-09003f2ba759",
    "2025": "b2bde559-3455-4021-b179-dfe60c0337b0",
}

#: CKAN's datastore_search caps a page well below a year of half hours (17,568), so every
#: year is paged. The cap is the SERVER's and is not ours to raise.
PAGE_SIZE = 5000

FIELDS = ("SETTLEMENT_DATE", "SETTLEMENT_PERIOD",
          "EMBEDDED_WIND_GENERATION", "EMBEDDED_SOLAR_GENERATION",
          "EMBEDDED_WIND_CAPACITY", "EMBEDDED_SOLAR_CAPACITY")


class EmbeddedGenerationUnavailable(Exception):
    """Raised when the series cannot be read. NEVER swallowed into a zero.

    A missing embedded reading is not a country with no embedded generation, and the
    difference is the entire measurement — an adapter that returns 0.0 on a failed fetch
    would report the hypothesis as refuted precisely when the evidence was absent
    (R15 fail-open, the exact shape `MUST_RUN_ZERO_CARBON_MW` fell into one pass ago).
    """


_session = requests.Session()


#: THE SAME DATASET PUBLISHES ITS DATE THREE DIFFERENT WAYS, measured across the pinned
#: resources rather than assumed: '2018-01-01' (2018, 2024, 2025), '01-JAN-2019' (2019-2022)
#: and '01-Jan-23' (2023) -- a TWO-DIGIT year in the middle of a ten-year series. This was
#: found because a strict ISO-only reader silently dropped five years of eight while the
#: fetch log still reported 17,520 records for each of them: the log was counting RAW
#: records and the loss happened at PARSE time, one layer further in. A naive `[:10]` slice
#: would have been worse than the refusal -- it would have keyed 2019 half hours under
#: '01-JAN-201' and produced a full-looking series that joined to nothing.
_MONTHS = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}


def _normalise_date(raw: object, resource_year: str | None = None) -> str | None:
    """Any of NESO's three published date forms -> 'YYYY-MM-DD'. Anything else is REFUSED.

    THE TWO-DIGIT YEAR IS RESOLVED AGAINST THE RESOURCE, NOT AGAINST A CENTURY RULE. '01-Jan-23'
    is only unambiguous because it came out of the resource NESO labels 2023, so that label is
    passed in and used. A pivot-year heuristic would be a guess that happens to be right for this
    decade and silently wrong later, which is the same class of defect as the format drift it is
    trying to absorb.

    AND THE RESOURCE YEAR IS THEN USED AS A CHECK, not only as a hint: a record whose parsed year
    disagrees with the resource it was fetched from is refused rather than kept. That is the
    control which would catch NESO re-pointing a resource, or this module's pinned ids drifting
    out of step with the labels -- a failure that would otherwise look like perfectly good data.
    """
    if raw is None:
        return None
    text = str(raw).strip()
    parsed: tuple[int, int, int] | None = None

    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        try:
            parsed = (int(text[0:4]), int(text[5:7]), int(text[8:10]))
        except ValueError:
            return None
    else:
        parts = text.split("-")
        if len(parts) == 3 and parts[1][:3].upper() in _MONTHS:
            try:
                day = int(parts[0])
                month = _MONTHS[parts[1][:3].upper()]
                year_text = parts[2]
            except ValueError:
                return None
            if len(year_text) == 4 and year_text.isdigit():
                parsed = (int(year_text), month, day)
            elif len(year_text) == 2 and year_text.isdigit() and resource_year:
                # The two-digit form: take the century from the resource's own label, and only
                # accept it when the last two digits actually agree with that label.
                if year_text == resource_year[2:]:
                    parsed = (int(resource_year), month, day)

    if parsed is None:
        return None
    year, month, day = parsed
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    if resource_year is not None and str(year) != str(resource_year):
        return None
    return f"{year:04d}-{month:02d}-{day:02d}"


def fetch_year(year: str, *, timeout: float = 90.0) -> list[dict]:
    """Every half-hourly record NESO publishes for `year`, paged, in the order returned."""
    resource_id = RESOURCE_IDS.get(year)
    if resource_id is None:
        raise EmbeddedGenerationUnavailable(f"no pinned NESO resource for {year}")

    records: list[dict] = []
    offset = 0
    while True:
        response = _session.get(
            CKAN_BASE,
            params={"resource_id": resource_id, "limit": PAGE_SIZE, "offset": offset},
            timeout=timeout,
        )
        if response.status_code != 200:
            raise EmbeddedGenerationUnavailable(
                f"{year}: CKAN returned HTTP {response.status_code}"
            )
        payload = response.json()
        if not payload.get("success"):
            raise EmbeddedGenerationUnavailable(f"{year}: CKAN reported failure")
        page = payload["result"].get("records", [])
        if not page:
            break
        for record in page:
            row = {k: record.get(k) for k in FIELDS}
            # STAMPED AT FETCH, because it is knowable here and unrecoverable later: the
            # resource's own year label is what disambiguates a two-digit date and what
            # `_normalise_date` checks the parsed year against.
            row["_resource_year"] = year
            records.append(row)
        offset += len(page)
        if offset >= int(payload["result"].get("total", 0)):
            break
    return records


def to_settlement_periods(
    records: Iterable[Mapping],
) -> dict[tuple[str, int], dict[str, float]]:
    """{(date, period): {wind_mw, solar_mw, total_mw, capacity_mw}} — the LAST record wins.

    WHY A NEGATIVE READING IS CLAMPED AND A MISSING ONE IS DROPPED, and why those are
    different: NESO's estimate occasionally goes slightly negative at night, which is a
    model artefact of a quantity that cannot be negative, so it is clamped to zero. An
    ABSENT field is not a small number — it is no reading — and the half hour is dropped
    so that it cannot enter a fit as a zero. Collapsing the two would put "we did not
    look" and "nothing was generated" in the same bin, which is the fail-open shape.
    """
    out: dict[tuple[str, int], dict[str, float]] = {}
    for record in records:
        date_str = _normalise_date(
            record.get("SETTLEMENT_DATE"), record.get("_resource_year")
        )
        period = record.get("SETTLEMENT_PERIOD")
        wind = record.get("EMBEDDED_WIND_GENERATION")
        solar = record.get("EMBEDDED_SOLAR_GENERATION")
        if date_str is None or period is None or wind is None or solar is None:
            continue
        try:
            period_i = int(period)
            wind_mw = max(0.0, float(wind))
            solar_mw = max(0.0, float(solar))
        except (TypeError, ValueError):
            continue
        if not 1 <= period_i <= 50:
            continue
        capacity = 0.0
        for field in ("EMBEDDED_WIND_CAPACITY", "EMBEDDED_SOLAR_CAPACITY"):
            try:
                capacity += max(0.0, float(record.get(field) or 0.0))
            except (TypeError, ValueError):
                pass
        out[(date_str, period_i)] = {
            "wind_mw": wind_mw,
            "solar_mw": solar_mw,
            "total_mw": wind_mw + solar_mw,
            "capacity_mw": capacity,
        }
    return out


def total_by_period(
    series: Mapping[tuple[str, int], Mapping[str, float]],
) -> dict[tuple[str, int], float]:
    """{(date, period): embedded wind + solar MW} — the series the bound measures."""
    return {key: float(value["total_mw"]) for key, value in series.items()}


def load_cached(path: Path | None = None) -> list[dict]:
    """The cached records. Raises rather than returning [] when the cache is absent."""
    cache = Path(path or CACHE_PATH)
    if not cache.exists():
        raise EmbeddedGenerationUnavailable(
            f"no cache at {cache} -- run `python3 -m sim.neso_embedded_generation` first"
        )
    return json.loads(cache.read_text(encoding="utf-8"))


def write_cache(records: list[dict], path: Path | None = None) -> None:
    cache = Path(path or CACHE_PATH)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(records) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Fetch, PARSE-CHECK, then cache.

    THE COVERAGE CHECK IS ON PARSED PERIODS, NOT ON RAW RECORDS, and that is the whole lesson of
    this module's first run: it reported 17,520 records for all eight years while five of them
    parsed to nothing, because the count was taken one layer upstream of where the loss happened.
    A per-year population assertion is the cheapest control that would have caught it, so it runs
    before the cache is written, and a year that fetched rows but yielded no half hours is FATAL
    rather than a warning -- a partially-parsed cache is the input to a measurement that would
    then report a real-looking answer over whichever years happened to survive.
    """
    years = list(argv) if argv else sorted(RESOURCE_IDS)
    records: list[dict] = []
    empty: list[str] = []
    for year in years:
        try:
            got = fetch_year(year)
        except EmbeddedGenerationUnavailable as exc:
            print(f"{year}: {exc}")
            continue
        parsed = to_settlement_periods(got)
        print(f"{year}: {len(got)} records -> {len(parsed)} settlement periods")
        if got and not parsed:
            empty.append(year)
        records.extend(got)
    if not records:
        raise SystemExit("no records fetched")
    if empty:
        raise SystemExit(
            f"REFUSING TO CACHE: {', '.join(empty)} returned rows that parsed to zero "
            "settlement periods -- a date format this reader does not know"
        )
    write_cache(records)
    series = to_settlement_periods(records)
    print(f"cached {len(records)} records -> {len(series)} settlement periods at {CACHE_PATH}")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
