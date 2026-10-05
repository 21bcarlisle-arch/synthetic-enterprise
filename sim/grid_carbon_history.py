"""Historical half-hourly GB grid carbon intensity, 2016-2025, keyed by settlement period.

REUSE: sim/grid_carbon_history.py
CLASS: CUSTOM
INDEX: `sim/neso_carbon_intensity.py` publishes NESO's series and the settlement key, and is
       reused for both. `sim/elexon_fuel_outturn.py` holds the FUELHH caches and NESO's own factor
       tables, and is reused for both. `sim/neso_embedded_generation.py` is reused for the
       embedded wind and solar NESO counts. `sim/grid_carbon_intensity.py` is a different thing:
       it RECONSTRUCTS a dimensionless shape through a dispatch model, so that it stays an
       independent check on NESO. This module does the opposite and must never feed it. It is
       NESO's own arithmetic, used to stand in for NESO where NESO published nothing.

WHAT THIS IS (director, 2026-10-05): "For historical periods, take the published series and
align it to settlement. ... if it doesn't cover 2016, fill the gap simply from Elexon's fuel mix
and standard emission factors rather than modelling dispatch. ... a correlated estimate."

One value per settlement period, 2016-01-01 to 2025-12-31, in gCO2/kWh, each with a source:

  neso_historic_mix  NESO's Historic GB Generation Mix `CARBON_INTENSITY` (Open Data Portal,
                     `df_fuel_ckan.csv`, half-hourly from 2009). One publisher, one basis, the
                     whole decade.
  fuelmix_fill       a half hour the historic mix has no usable value for: no row
                     (`historic_mix_no_record`), or an outage signature (a null, zero or
                     above-ceiling intensity, or transmission wind and hydro both exactly 0 MW,
                     `historic_mix_outage_signature`). The fill is unscaled, as the brief requires.
  gap                neither source has a value. The value is None and the reason is given.
                     Nothing is interpolated.

THE BASIS IS GENERATION, NOT CONSUMPTION (measured 2026-10-05). Regressing the historic mix's
intensity x `GENERATION` on its fuel columns gives gas 391-403, coal 932-997 and biomass 107-133
in every year tested, on NESO's table of 394 / 937 / 120: no loss multiplier. `GENERATION` is the
sum of every fuel column, embedded wind (`WIND_EMB`), embedded solar (`SOLAR`) and `IMPORTS`
included. So a value here is CO2 at the generator per kWh GENERATED. Transmission and distribution
losses are NOT in it; a consumer that wants them adds them as a separate named line.

WHY NOT THE CARBON INTENSITY API, which was the series until 2026-10-05. The API's published
`actual` CHANGES BASIS at 2020-04-27 period 34: API / historic mix is 1.13-1.18 a year before it and
1.01-1.04 after, and our own inputs are smooth across that half hour (G14 knowledge page, "The
2020-04-27 step"). Before the step the API carried a loss uplift; after it, it does not, whatever
its methodology text says. A series that splices the two is on no basis. The API is kept as the
CROSS-CHECK (`meta["api_versus_historic_mix"]`), and that is all it is.

THE CKAN FILE IS A LATER EDITION. It is the file as NESO serves it on the day it was fetched
(`meta["historic_mix_edition"]` names its last half hour), revised in hindsight. No supplier
could have read this exact file in 2019. Every consumer of this series reads it as OUTTURN WITH
HINDSIGHT, which is how the feed already states it.

THE FILL ARITHMETIC (NESO Carbon Intensity methodology, the way `elexon_fuel_outturn` already uses
it): sum over fuels of MW x NESO's factor, divided by total MW. The total includes imports and
NESO's embedded wind and solar estimate. The factors are `NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH`
and `import_factor`, imported here and never restated. Negative readings are clamped to zero:
pumped storage while pumping and cables while exporting are demand, not generation. ElecLink
and Viking are left out because NESO's mix leaves them out (`OUTSIDE_NESO_MIX`). It reads a few
percent ABOVE the historic mix (`meta["arithmetic_versus_historic_mix"]` gives the bias by year).
Which term carries the difference is not established.

FOUR THINGS THE DATA SHOWED THAT NOTHING HAD WRITTEN DOWN
  1. FUELHH's `settlementDate` for PERIOD 48 IS THE NEXT DAY, on every day up to 2022. The row
     labelled (D, 48) has `startTime` D-1 23:30Z, and its value continues D-1's period 47. Rows
     are therefore keyed by `settlement_key(startTime)`, which also gets 46 and 50 right on
     clock-change days. The fix lives in `elexon_fuel_outturn.row_settlement_key`.
  2. FUELHH has no BIOMASS type before 2017-11-01; biomass sits inside OTHER until then. So before
     the first BIOMASS reading, OTHER is priced at NESO's BIOMASS factor
     (`PRE_SPLIT_OTHER_PRICED_AS`). The CLI prints the bracket with OTHER at its own factor.
  3. THE HISTORIC MIX'S `DATETIME` IS THE UTC START of the half hour: keyed that way, clock-change
     days carry 46 and 50 periods, and the correlation with the API peaks at lag 0.
  4. THE HISTORIC MIX HAS ITS OWN PARTIAL OUTAGE: on 20 half hours in 2016-2025 (five on
     2023-06-07, the day FUELHH reads all zeros) transmission wind and hydro both read exactly
     0 MW while gas and nuclear carry on, so its intensity is too high. GB wind and hydro are never
     both exactly zero, and the test is exact, so no threshold is picked.

Run:  python3 -m sim.grid_carbon_history            (statistics and coverage; builds on first run)
      python3 -m sim.grid_carbon_history --fetch-historic-mix
      python3 -m sim.grid_carbon_history --fetch-neso-extension   (the API cross-check's 2018/2025)
"""
from __future__ import annotations

import csv
import json
import math
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import date as date_cls
from datetime import datetime, timedelta, timezone
from datetime import time as time_cls
from functools import lru_cache
from pathlib import Path

from sim import elexon_fuel_outturn as efo
from sim import neso_carbon_intensity as nci
from sim import neso_embedded_generation as neg

Key = tuple[str, int]

SERIES_START = "2016-01-01"
SERIES_END = "2025-12-31"

NESO_HISTORIC_MIX = "neso_historic_mix"
FUELMIX_FILL = "fuelmix_fill"
GAP = "gap"
#: Every value here is derived from the real record, including the fills.
DATA_REGIME = "historical"
SOURCES = (NESO_HISTORIC_MIX, FUELMIX_FILL, GAP)

#: NESO Open Data Portal, "Historic GB Generation Mix", resource `df_fuel_ckan.csv`. Key-free and
#: openly licensed; it redirects to a signed download.
HISTORIC_MIX_URL = (
    "https://api.neso.energy/dataset/88313ae5-94e4-4ddc-a790-593554d8c6b9/resource/"
    "f93d1835-75bc-43e5-84ad-12472b180a98/download/df_fuel_ckan.csv"
)
HISTORIC_MIX_CACHE_PATH = Path("sim/cache/neso_historic_generation_mix.csv")
#: The API cross-check's 2018 and 2025 windows, which the live API cache does not hold.
NESO_EXTENSION_CACHE_PATH = Path("sim/cache/neso_carbon_intensity_national_extension.json")
BUILT_PATH = Path("sim/cache/grid_carbon_history.json")

#: The API's basis change (G14 knowledge page, "The 2020-04-27 step"): the first half hour on the
#: later basis. Used only to split the cross-check, never to build a value.
API_BASIS_STEP = ("2020-04-27", 34)

#: Transmission fuels whose readings all being exactly zero in one half hour is the historic mix's
#: partial-outage signature (module docstring, finding 4).
HISTORIC_MIX_OUTAGE_ZERO_COLUMNS = ("WIND", "HYDRO")

FUELHH_CACHE_PATHS = (
    efo.THERMAL_CACHE_PATH,
    efo.ZERO_CARBON_MUST_RUN_CACHE_PATH,
    efo.BIOMASS_CACHE_PATH,
    efo.REMAINDER_CACHE_PATH,
    efo.CACHE_PATH,
)

#: The non-interconnector fuel types FUELHH carries. A half hour missing any of them has an
#: incomplete mix. Pricing it anyway would pass off a hole as a clean or dirty half hour, so it
#: gets no estimate. BIOMASS is required only from the first date FUELHH publishes it.
REQUIRED_FUELS = (
    *efo.THERMAL_FUEL_TYPES,
    *efo.ZERO_CARBON_MUST_RUN_FUEL_TYPES,
    efo.COAL_FUEL_TYPE,
    *efo.REMAINDER_FUEL_TYPES,
    # The four cables in service for the whole series. A later cable's absence before it was
    # built is real, so only these are required.
    "INTFR", "INTIRL", "INTNED", "INTEW",
)

#: Which NESO factor OTHER carries before FUELHH splits biomass out of it (finding 2 above).
PRE_SPLIT_OTHER_PRICED_AS = efo.BIOMASS_FUEL_TYPE

#: The whole series, for the cross-check statistics.
OVERLAP_WINDOW = (SERIES_START, SERIES_END)


@dataclass(frozen=True)
class Reading:
    value: float | None
    source: str
    reason: str | None = None


# ---------------------------------------------------------------- settlement keys


def settlement_periods_on(day: str) -> int:
    """46, 48 or 50: the half hours between this GB local midnight and the next."""
    d = date_cls.fromisoformat(day)
    start = datetime.combine(d, time_cls(0, 0), tzinfo=nci.LONDON).astimezone(timezone.utc)
    end = datetime.combine(d + timedelta(days=1), time_cls(0, 0), tzinfo=nci.LONDON)
    # Convert to UTC before subtracting. Python subtracts two datetimes that share a tzinfo as
    # wall-clock time, so without this every day comes out as 48. The first draft had that bug,
    # and it put periods 47 and 48 onto every spring clock-change day.
    return int((end.astimezone(timezone.utc) - start).total_seconds() // 1800)


def settlement_universe(start: str = SERIES_START, end: str = SERIES_END) -> list[Key]:
    """Every (settlement date, period) in [start, end], so a missing half hour is visible."""
    out: list[Key] = []
    d = date_cls.fromisoformat(start)
    last = date_cls.fromisoformat(end)
    while d <= last:
        day = d.isoformat()
        out.extend((day, p) for p in range(1, settlement_periods_on(day) + 1))
        d += timedelta(days=1)
    return out


def _key_from_start_time(text: str) -> Key:
    stamp = text.rstrip("Z").replace("T", " ")[:16]
    instant = datetime.strptime(stamp, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    return nci.settlement_key(instant)


# ---------------------------------------------------------------- inputs


def fuel_mix_by_period(rows: Iterable[Mapping]) -> dict[Key, dict[str, float]]:
    """FUELHH rows -> {key: {fuelType: MW}}, keyed by `startTime` and never by the label.

    The label is wrong for period 48 up to 2022 (finding 1), so this goes through
    `elexon_fuel_outturn.row_settlement_key`. If a row repeats for the same half
    hour and fuel, the last one wins, as in `elexon_fuel_outturn`. A non-numeric reading is
    skipped and never set to zero.
    """
    out: dict[Key, dict[str, float]] = {}
    for row in rows:
        value = row.get("generation")
        fuel = row.get("fuelType")
        key = efo.row_settlement_key(row)
        if key is None or fuel is None or value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        out.setdefault(key, {})[str(fuel)] = float(value)
    return out


def load_fuel_mix(paths: Iterable[Path] = FUELHH_CACHE_PATHS) -> dict[Key, dict[str, float]]:
    merged: dict[Key, dict[str, float]] = {}
    for path in paths:
        if not Path(path).exists():
            raise efo.FuelOutturnUnavailable(f"{path} is not cached; the fuel mix would be partial")
        for key, fuels in fuel_mix_by_period(json.loads(Path(path).read_text())).items():
            merged.setdefault(key, {}).update(fuels)
    return merged


def biomass_split(fuel_mix: Mapping[Key, Mapping[str, float]]) -> Key | None:
    """The first half hour FUELHH carries a BIOMASS reading. It is measured from the data, not
    typed in. The split is a half hour, not a date, because BIOMASS starts partway through
    2017-11-01 (period 41)."""
    keys = [key for key, fuels in fuel_mix.items() if efo.BIOMASS_FUEL_TYPE in fuels]
    return min(keys) if keys else None


def historic_mix_by_period(
    rows: Iterable[Mapping[str, str]],
) -> tuple[dict[Key, float], set[Key], str | None]:
    """CSV rows -> ({key: usable CARBON_INTENSITY}, {keys with an outage signature}, last DATETIME).

    `DATETIME` is the UTC start of the half hour (finding 3). Usable means a number above zero, not
    above `nci._physical_ceiling_g_co2_per_kwh()`, with `GENERATION` above zero, and not every
    `HISTORIC_MIX_OUTAGE_ZERO_COLUMNS` reading exactly 0 (finding 4). Anything else that has a row
    is a signature. A key with no row is in neither set.
    """
    ceiling = nci._physical_ceiling_g_co2_per_kwh()
    usable: dict[Key, float] = {}
    seen: set[Key] = set()
    last: str | None = None
    for row in rows:
        stamp = row.get("DATETIME")
        if not stamp:
            continue
        try:
            key = _key_from_start_time(stamp)
        except ValueError:
            continue
        last = stamp if last is None else max(last, stamp)
        seen.add(key)
        try:
            value = float(row["CARBON_INTENSITY"])
            generation = float(row["GENERATION"])
            zeros = all(float(row[c] or 0.0) == 0.0 for c in HISTORIC_MIX_OUTAGE_ZERO_COLUMNS)
        except (KeyError, TypeError, ValueError):
            continue
        if math.isfinite(value) and 0.0 < value <= ceiling and generation > 0.0 and not zeros:
            usable[key] = value
    return usable, seen - set(usable), last


def load_historic_mix(path: Path = HISTORIC_MIX_CACHE_PATH) -> tuple[dict[Key, float], set[Key], str | None]:
    """As `historic_mix_by_period`, over 2016-2025 plus a day either side (so every UTC row of a
    local settlement day at each end is read). The third element is the FILE's last `DATETIME`,
    which names the edition."""
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} is not cached; run --fetch-historic-mix")
    with Path(path).open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    edition = max((r.get("DATETIME") or "" for r in rows), default="") or None
    wanted = [r for r in rows
              if "2015-12-31" <= (r.get("DATETIME") or "")[:10] <= "2026-01-01"]
    usable, signatures, _ = historic_mix_by_period(wanted)
    return usable, signatures, edition


def load_neso(
    records: Iterable[Mapping],
) -> tuple[dict[Key, float], set[Key]]:
    """Raw NESO records -> ({key: usable actual}, {keys whose record carries an outage signature}).

    Usable means it survived `nci.to_settlement_periods` (null and zero `actual` are dropped
    there) and is not above `nci._physical_ceiling_g_co2_per_kwh()`. Any key that has a raw record
    but no usable value is a signature. A key with no record at all is in neither set.
    """
    records = list(records)
    try:
        parsed = nci.actual_by_period(nci.to_settlement_periods(records))
    except nci.NesoIntensityUnavailable:
        parsed = {}
    ceiling = nci._physical_ceiling_g_co2_per_kwh()
    usable = {k: v for k, v in parsed.items() if v <= ceiling}
    seen: set[Key] = set()
    for record in records:
        start = record.get("from")
        if not start:
            continue
        try:
            seen.add(_key_from_start_time(str(start)))
        except ValueError:
            continue
    return usable, seen - set(usable)


def load_neso_records() -> list[dict]:
    records = list(nci.load_cached())
    if NESO_EXTENSION_CACHE_PATH.exists():
        records.extend(json.loads(NESO_EXTENSION_CACHE_PATH.read_text()))
    return records


def load_embedded() -> dict[Key, float]:
    return neg.total_by_period(neg.to_settlement_periods(neg.load_cached()))


# ---------------------------------------------------------------- the arithmetic


def fuelmix_intensity(
    fuels: Mapping[str, float] | None,
    key: Key,
    embedded_mw: float | None,
    *,
    split: Key | None,
    factors: Mapping[str, float] | None = None,
    import_factor: Callable[[str, str], float | None] = efo.import_factor,
    other_priced_as: str = PRE_SPLIT_OTHER_PRICED_AS,
) -> tuple[float | None, str | None]:
    """(gCO2/kWh, None), or (None, reason). This is NESO's arithmetic on Elexon's mix.

    `factors` defaults to NESO's table, read when the function is called, so a change to that
    table moves this value.
    """
    if fuels is None:
        return None, "fuelhh_absent"
    table = efo.NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH if factors is None else factors
    pre_split = split is None or key < split
    required = REQUIRED_FUELS if pre_split else (*REQUIRED_FUELS, efo.BIOMASS_FUEL_TYPE)
    missing = [f for f in required if f not in fuels]
    if missing:
        return None, "fuelhh_incomplete:" + ",".join(missing)
    if embedded_mw is None:
        return None, "embedded_generation_absent"
    # FUELHH HAS ITS OWN OUTAGE SIGNATURE. On 56 half hours every GB fuel reads 0 MW, for example
    # 2023-06-07 periods 23-26, the same outage NESO publishes as zeros. GB has never generated
    # nothing, so this is a hole in the feed. Pricing it would give 0 g, or the import mix alone,
    # which is the zero the fill exists to avoid. The test is exactly zero, so no threshold is
    # picked. A PARTIAL drop (2023-06-07 p22 reads about 60% of p21 on every fuel) is NOT caught.
    # A ratio survives a uniform scale-down, so it costs little, but it is not established.
    if sum(max(0.0, float(v)) for f, v in fuels.items() if f not in efo.INTERCONNECTOR_MARKETS) <= 0.0:
        return None, "fuelhh_outage_signature"
    grams = 0.0
    mw_total = max(0.0, float(embedded_mw))
    for fuel, reading in fuels.items():
        mw = max(0.0, float(reading))
        if mw <= 0.0:
            continue
        market = efo.INTERCONNECTOR_MARKETS.get(fuel)
        if market is not None:
            if fuel in efo.OUTSIDE_NESO_MIX:
                continue
            factor = import_factor(market, key[0][:4])
            if factor is None:
                return None, f"import_unpriced:{fuel}"
        elif fuel in table:
            factor = table[other_priced_as] if (fuel == "OTHER" and pre_split) else table[fuel]
        else:
            return None, f"fuel_unpriced:{fuel}"
        grams += mw * factor
        mw_total += mw
    if mw_total <= 0.0:
        return None, "no_generation"
    return grams / mw_total, None


# ---------------------------------------------------------------- statistics


def _stats(pairs: list[tuple[float, float]]) -> dict[str, float]:
    n = len(pairs)
    mx = sum(a for a, _ in pairs) / n
    my = sum(b for _, b in pairs) / n
    vx = sum((a - mx) ** 2 for a, _ in pairs)
    vy = sum((b - my) ** 2 for _, b in pairs)
    cov = sum((a - mx) * (b - my) for a, b in pairs)
    return {
        "n": float(n),
        "correlation": cov / math.sqrt(vx * vy) if vx > 0 and vy > 0 else float("nan"),
        "mean_bias": mx - my,
        "rmse": math.sqrt(sum((a - b) ** 2 for a, b in pairs) / n),
        "mean_estimate": mx,
        "mean_published": my,
    }


def overlap_pairs(
    estimate: Mapping[Key, float],
    published: Mapping[Key, float],
    window: tuple[str, str] = OVERLAP_WINDOW,
) -> dict[Key, tuple[float, float]]:
    """{key: (raw estimate, published)}: only half hours inside `window` that have both."""
    lo, hi = window
    return {
        k: (estimate[k], v)
        for k, v in published.items()
        if lo <= k[0] <= hi and k in estimate
    }


def overlap_statistics(
    estimate: Mapping[Key, float],
    published: Mapping[Key, float],
    window: tuple[str, str] = OVERLAP_WINDOW,
) -> dict[str, dict[str, float]]:
    """Correlation, mean bias (estimate minus published) and RMSE, by year and over "ALL"."""
    pairs = overlap_pairs(estimate, published, window)
    if not pairs:
        raise ValueError(f"no half hour has both an estimate and a published value in {window}")
    by_year: dict[str, list[tuple[float, float]]] = {}
    for k, p in pairs.items():
        by_year.setdefault(k[0][:4], []).append(p)
    out = {year: _stats(ps) for year, ps in sorted(by_year.items())}
    out["ALL"] = _stats(list(pairs.values()))
    return out


# ---------------------------------------------------------------- assembly


def assemble(
    universe: Iterable[Key],
    raw_estimate: Mapping[Key, tuple[float | None, str | None]],
    historic: Mapping[Key, float],
    signatures: set[Key],
) -> dict[Key, Reading]:
    """Gives each half hour one source: the historic mix, else the unscaled fill, else a gap."""
    out: dict[Key, Reading] = {}
    for key in universe:
        if key in historic:
            out[key] = Reading(historic[key], NESO_HISTORIC_MIX)
            continue
        value, why = raw_estimate.get(key, (None, "fuelhh_absent"))
        mix_why = "historic_mix_outage_signature" if key in signatures else "historic_mix_no_record"
        if value is None:
            out[key] = Reading(None, GAP, f"{mix_why} and {why}")
        else:
            out[key] = Reading(value, FUELMIX_FILL, mix_why)
    return out


def _ratio(pairs: Iterable[tuple[float, float]]) -> float | None:
    pairs = list(pairs)
    den = sum(b for _, b in pairs)
    return sum(a for a, _ in pairs) / den if pairs and den > 0 else None


def api_step(published: Mapping[Key, float], historic: Mapping[Key, float]) -> dict:
    """API / historic mix, summed, either side of `API_BASIS_STEP`, over the whole overlap."""
    before = [(v, historic[k]) for k, v in published.items() if k in historic and k < API_BASIS_STEP]
    after = [(v, historic[k]) for k, v in published.items() if k in historic and k >= API_BASIS_STEP]
    return {"first_half_hour_after": list(API_BASIS_STEP),
            "before": {"n": len(before), "ratio": _ratio(before)},
            "after": {"n": len(after), "ratio": _ratio(after)}}


def build() -> tuple[dict[Key, Reading], dict]:
    """Builds the series from the cached inputs and returns (series, meta)."""
    fuel_mix = load_fuel_mix()
    embedded = load_embedded()
    historic, signatures, edition = load_historic_mix()
    published, _api_signatures = load_neso(load_neso_records())
    split = biomass_split(fuel_mix)
    universe = settlement_universe()
    raw = {
        k: fuelmix_intensity(fuel_mix.get(k), k, embedded.get(k), split=split)
        for k in universe
    }
    estimate = {k: v for k, (v, _) in raw.items() if v is not None}
    series = assemble(universe, raw, historic, signatures)
    meta = {
        "historic_mix_edition": edition,
        "biomass_split": list(split) if split else None,
        "data_regime": DATA_REGIME,
        # bias = arithmetic - historic mix: the error a `fuelmix_fill` value carries.
        "arithmetic_versus_historic_mix": overlap_statistics(estimate, historic),
        # bias = API - historic mix, either side of the API's own basis change.
        "api_versus_historic_mix": overlap_statistics(published, historic),
        "api_step": api_step(published, historic),
        "coverage_by_year": coverage(series),
        "pre_split_other_bracket": _other_bracket(fuel_mix, embedded, split, universe),
    }
    return series, meta


def _other_bracket(fuel_mix, embedded, split, universe) -> dict[str, float]:
    """Mean change, by year, in the pre-split estimate if OTHER kept its own factor."""
    acc: dict[str, list[float]] = {}
    for k in universe:
        if split is None or k >= split:
            continue
        a, _ = fuelmix_intensity(fuel_mix.get(k), k, embedded.get(k), split=split)
        b, _ = fuelmix_intensity(fuel_mix.get(k), k, embedded.get(k), split=split,
                                 other_priced_as="OTHER")
        if a is not None and b is not None:
            acc.setdefault(k[0][:4], []).append(b - a)
    return {y: sum(v) / len(v) for y, v in sorted(acc.items())}


def _input_fingerprint() -> list:
    paths = [*FUELHH_CACHE_PATHS, HISTORIC_MIX_CACHE_PATH, nci.CACHE_PATH, NESO_EXTENSION_CACHE_PATH,
             Path(neg.CACHE_PATH)]
    out = []
    for p in paths:
        p = Path(p)
        out.append([str(p), p.stat().st_size if p.exists() else None,
                    int(p.stat().st_mtime) if p.exists() else None])
    return out


def write_built(series: Mapping[Key, Reading], meta: dict, path: Path = BUILT_PATH) -> None:
    payload = {
        "meta": {**meta, "inputs": _input_fingerprint()},
        "series": [[k[0], k[1], r.value, r.source, r.reason] for k, r in sorted(series.items())],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":")))


def _read_built(path: Path = BUILT_PATH) -> tuple[dict[Key, Reading], dict] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text())
    meta = payload["meta"]
    if meta.get("inputs") != _input_fingerprint():
        return None
    series = {(d, int(p)): Reading(v, s, r) for d, p, v, s, r in payload["series"]}
    return series, {k: v for k, v in meta.items() if k != "inputs"}


@lru_cache(maxsize=1)
def load_series() -> tuple[dict[Key, Reading], dict]:
    """(series, meta). Read from the built artefact if its inputs have not changed since it was
    written; otherwise built from the caches and written out."""
    cached = _read_built()
    if cached is not None:
        return cached
    series, meta = build()
    write_built(series, meta)
    return series, meta


def reading_at(settlement_date: str | date_cls, settlement_period: int) -> Reading:
    day = settlement_date.isoformat() if isinstance(settlement_date, date_cls) else str(settlement_date)
    series, _ = load_series()
    reading = series.get((day, int(settlement_period)))
    if reading is None:
        n = settlement_periods_on(day) if SERIES_START <= day <= SERIES_END else None
        return Reading(None, GAP, f"no such settlement period ({day}, {settlement_period}); "
                                  f"that day has {n} periods" if n else "outside 2016-2025")
    return reading


def intensity_at(settlement_date: str | date_cls, settlement_period: int) -> tuple[float | None, str]:
    """(gCO2/kWh or None, source). Call `reading_at` to get the reason for a gap."""
    r = reading_at(settlement_date, settlement_period)
    return r.value, r.source


def coverage(series: Mapping[Key, Reading]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for k, r in series.items():
        row = out.setdefault(k[0][:4], {s: 0 for s in SOURCES})
        row[r.source] += 1
    return dict(sorted(out.items()))


# ---------------------------------------------------------------- CLI


def fetch_historic_mix(timeout: float = 300.0) -> int:
    """Fetches NESO's Historic GB Generation Mix into `HISTORIC_MIX_CACHE_PATH`, as served today."""
    import urllib.request

    request = urllib.request.Request(HISTORIC_MIX_URL, headers={"User-Agent": "poesys-sim/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 -- fixed https URL
        body = response.read()
    HISTORIC_MIX_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORIC_MIX_CACHE_PATH.write_bytes(body)
    print(f"{len(body):,} bytes -> {HISTORIC_MIX_CACHE_PATH}")
    return 0


def fetch_neso_extension() -> int:
    """Fetches the NESO windows the live cache does not hold into the extension file. Only
    windows the cache does not already hold are requested."""
    held = {r.get("from", "")[:10] for r in nci.load_cached()}
    windows = []
    for lo, hi in ((nci.FIRST_PUBLISHED_DATE, "2018-12-31"), ("2025-01-01", SERIES_END)):
        if not any(lo <= d <= hi for d in held):
            windows.append((lo, hi))
    records: list[dict] = []
    for lo, hi in windows:
        records.extend(nci.fetch_national(lo, hi))
    NESO_EXTENSION_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    NESO_EXTENSION_CACHE_PATH.write_text(json.dumps(records, separators=(",", ":")))
    print(f"{len(records):,} records for {windows} -> {NESO_EXTENSION_CACHE_PATH}")
    return 0


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fetch-historic-mix", action="store_true")
    parser.add_argument("--fetch-neso-extension", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args(argv)
    if args.fetch_historic_mix:
        return fetch_historic_mix()
    if args.fetch_neso_extension:
        return fetch_neso_extension()
    if args.rebuild:
        series, meta = build()
        write_built(series, meta)
    else:
        series, meta = load_series()

    def table(title: str, stats: Mapping[str, Mapping[str, float]], cols: tuple[str, str]) -> None:
        print(title)
        print(f"  {'year':<5} {'n':>7} {'corr':>7} {'bias g':>8} {'rmse g':>8} {cols[0]:>7} {cols[1]:>7}")
        for year, s in stats.items():
            print(f"  {year:<5} {int(s['n']):>7} {s['correlation']:>7.4f} {s['mean_bias']:>+8.2f} "
                  f"{s['rmse']:>8.2f} {s['mean_estimate']:>7.1f} {s['mean_published']:>7.1f}")

    print(f"Historic mix edition: last half hour {meta['historic_mix_edition']}")
    table("Fill arithmetic vs historic mix (bias = arithmetic - historic):",
          meta["arithmetic_versus_historic_mix"], ("arith", "hist"))
    table("Carbon Intensity API vs historic mix (bias = API - historic):",
          meta["api_versus_historic_mix"], ("api", "hist"))
    step = meta["api_step"]
    print(f"API / historic mix before {step['first_half_hour_after']}: {step['before']['ratio']:.4f} "
          f"(n={step['before']['n']}); from it: {step['after']['ratio']:.4f} (n={step['after']['n']})")
    print(f"BIOMASS first published in FUELHH: {meta['biomass_split']}; before it OTHER is "
          f"priced as {PRE_SPLIT_OTHER_PRICED_AS} in the fill. If OTHER kept its own factor, mean change, g:")
    for year, delta in meta["pre_split_other_bracket"].items():
        print(f"  {year}: {delta:+.2f}")
    print("Coverage by source and year (half hours):")
    print(f"  {'year':<5} " + " ".join(f"{s:>17}" for s in SOURCES))
    for year, row in coverage(series).items():
        print(f"  {year:<5} " + " ".join(f"{row[s]:>17}" for s in SOURCES))
    reasons: dict[str, int] = {}
    for r in series.values():
        if r.reason:
            reasons[r.reason] = reasons.get(r.reason, 0) + 1
    print("Reasons:", dict(sorted(reasons.items(), key=lambda kv: -kv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
