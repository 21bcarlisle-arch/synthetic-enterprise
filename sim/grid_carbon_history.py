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

  neso_published    NESO's published `actual`, from 2018-05-11 (`FIRST_PUBLISHED_DATE`).
  fuelmix_estimate  before 2018-05-11. Fuel-mix arithmetic times a scale FITTED on the overlap.
  fuelmix_fill      inside NESO's coverage where NESO has no usable value: no record
                    (`neso_no_record`), or an outage signature (a null or zero `actual`, which
                    `neso_carbon_intensity.to_settlement_periods` drops, or a value above the
                    physical ceiling). The fill is unscaled, as the brief requires.
  gap               neither source has a value. The value is None and the reason is given.
                    Nothing is interpolated.

THE ARITHMETIC (NESO Carbon Intensity methodology, the way `elexon_fuel_outturn` already uses
it): sum over fuels of MW x NESO's factor, divided by total MW. The total includes imports and
NESO's embedded wind and solar estimate. The factors are `NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH`
and `import_factor`, imported here and never restated. Negative readings are clamped to zero:
pumped storage while pumping and cables while exporting are demand, not generation. ElecLink
and Viking are left out because NESO's mix leaves them out (`OUTSIDE_NESO_MIX`). We measured the
EMBEDDED term rather than assuming it. Over 2020-05..2025 the bias is +2.4 g with it and +12.6 g
without it (the no-embedded variant also has a summer dip, which is solar it cannot see).

FOUR THINGS THE DATA SHOWED THAT NOTHING HAD WRITTEN DOWN
  1. FUELHH's `settlementDate` for PERIOD 48 IS THE NEXT DAY, on every day up to 2022. The row
     labelled (D, 48) has `startTime` D-1 23:30Z, and its value continues D-1's period 47. The
     mean step to it is 1,056 MW, against 2,523 MW to D's own period 47. Rows are therefore keyed
     by `settlement_key(startTime)`, and that also gets 46 and 50 right on clock-change days. The
     fix lives in `elexon_fuel_outturn.row_settlement_key`, which every FUELHH reader there uses
     since 2026-10-05.
  2. FUELHH has no BIOMASS type before 2017-11-01; biomass sits inside OTHER until then. The
     monthly mean of OTHER is 932-1,817 MW before the split and 66-135 MW after. So before the
     first BIOMASS reading, OTHER is priced at NESO's BIOMASS factor (`PRE_SPLIT_OTHER_PRICED_AS`).
     The CLI prints the bracket with OTHER at its own factor.
  3. NESO's PUBLISHED LEVEL STEPS DOWN AROUND 2020-04-28. Published over arithmetic is about 1.10
     to 1.13 from 2018-05 to 2020-04, then about 0.94 to 1.00 from 2020-05. The cause is NOT
     ESTABLISHED. Pre-2018 values join the series at 2018-05-11, so the scale is fitted on the
     regime they join (`CALIBRATION_FIT_WINDOW`, exactly two years, seasonally balanced). The
     whole-overlap fit is printed beside it. Averaging across the step would give a basis NESO
     never published.
  4. THE NESO CACHE STARTED IN 2019, not on 2018-05-11. 2018-05-11..2018-12-31 and 2025 were
     fetched on 2026-10-05 into `NESO_EXTENSION_CACHE_PATH`, as a new file rather than a rewrite
     of the live cache. If it is missing, those half hours become `fuelmix_fill` and carry the
     reason `neso_no_record`. The coverage table shows it. Inside the cache there are 179
     `neso_no_record` half hours, across seven days in 2021-2024. For the three largest
     (2021-12-26/27, 2023-10-21/22, 2024-06-12) we re-asked the API on 2026-10-05, and NESO
     publishes nothing for them either.

Run:  python3 -m sim.grid_carbon_history            (statistics and coverage; builds on first run)
      python3 -m sim.grid_carbon_history --fetch-neso-extension
"""
from __future__ import annotations

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

NESO_PUBLISHED = "neso_published"
FUELMIX_ESTIMATE = "fuelmix_estimate"
FUELMIX_FILL = "fuelmix_fill"
GAP = "gap"
#: Every value here is derived from the real record, including the estimates.
DATA_REGIME = "historical"
SOURCES = (NESO_PUBLISHED, FUELMIX_ESTIMATE, FUELMIX_FILL, GAP)

NESO_EXTENSION_CACHE_PATH = Path("sim/cache/neso_carbon_intensity_national_extension.json")
BUILT_PATH = Path("sim/cache/grid_carbon_history.json")

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

#: The window the pre-2018 scale is fitted on: from NESO's first published day to the day before
#: the measured level step (finding 3). The window comes from measurement and is not tuned. Daily
#: published/arithmetic ratios run 1.06-1.18 to 2020-04-27, then 0.99, 0.97, 1.00, 0.96 ...
CALIBRATION_FIT_WINDOW = (nci.FIRST_PUBLISHED_DATE, "2020-04-27")

#: The whole overlap, for the statistics and for the fit printed beside the shipped one.
OVERLAP_WINDOW = (nci.FIRST_PUBLISHED_DATE, SERIES_END)


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


def fit_scale(pairs: Iterable[tuple[float, float]]) -> float:
    """Least-squares scale s minimising sum (s*estimate - published)^2."""
    pairs = list(pairs)
    sxx = sum(a * a for a, _ in pairs)
    if not pairs or sxx <= 0.0:
        raise ValueError("no overlap pairs to fit a scale on")
    return sum(a * b for a, b in pairs) / sxx


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
    published: Mapping[Key, float],
    signatures: set[Key],
    scale: float,
    *,
    neso_from: str = nci.FIRST_PUBLISHED_DATE,
) -> dict[Key, Reading]:
    """Gives each half hour one source. `scale` is applied to `fuelmix_estimate` and to no other."""
    out: dict[Key, Reading] = {}
    for key in universe:
        value, why = raw_estimate.get(key, (None, "fuelhh_absent"))
        if key[0] < neso_from:
            if value is None:
                out[key] = Reading(None, GAP, f"before NESO coverage and {why}")
            else:
                out[key] = Reading(value * scale, FUELMIX_ESTIMATE)
            continue
        if key in published:
            out[key] = Reading(published[key], NESO_PUBLISHED)
            continue
        neso_why = "neso_outage_signature" if key in signatures else "neso_no_record"
        if value is None:
            out[key] = Reading(None, GAP, f"{neso_why} and {why}")
        else:
            out[key] = Reading(value, FUELMIX_FILL, neso_why)
    return out


def build() -> tuple[dict[Key, Reading], dict]:
    """Builds the series from the cached inputs and returns (series, meta)."""
    fuel_mix = load_fuel_mix()
    embedded = load_embedded()
    published, signatures = load_neso(load_neso_records())
    split = biomass_split(fuel_mix)
    universe = settlement_universe()
    raw = {
        k: fuelmix_intensity(fuel_mix.get(k), k, embedded.get(k), split=split)
        for k in universe
    }
    estimate = {k: v for k, (v, _) in raw.items() if v is not None}
    shipped = overlap_pairs(estimate, published, CALIBRATION_FIT_WINDOW)
    whole = overlap_pairs(estimate, published, OVERLAP_WINDOW)
    scale = fit_scale(shipped.values())
    series = assemble(universe, raw, published, signatures, scale)
    meta = {
        "scale_fitted": scale,
        "scale_fit_window": list(CALIBRATION_FIT_WINDOW),
        "scale_fit_n": len(shipped),
        "scale_whole_overlap": fit_scale(whole.values()),
        "biomass_split": list(split) if split else None,
        "data_regime": DATA_REGIME,
        "overlap_statistics": overlap_statistics(estimate, published),
        "overlap_statistics_fit_window": overlap_statistics(estimate, published, CALIBRATION_FIT_WINDOW),
        # The same window AFTER the scale: the error a `fuelmix_estimate` value carries, as far as
        # it can be measured. It is in-sample, because the scale was fitted on these half hours.
        "overlap_statistics_fit_window_scaled": overlap_statistics(
            {k: v * scale for k, v in estimate.items()}, published, CALIBRATION_FIT_WINDOW),
        "coverage_by_year": coverage(series),
        "pre_split_other_bracket": _other_bracket(fuel_mix, embedded, split, universe, scale),
    }
    return series, meta


def _other_bracket(fuel_mix, embedded, split, universe, scale) -> dict[str, float]:
    """Mean change, by year, in the pre-split estimate if OTHER kept its own factor."""
    acc: dict[str, list[float]] = {}
    for k in universe:
        if split is None or k >= split:
            continue
        a, _ = fuelmix_intensity(fuel_mix.get(k), k, embedded.get(k), split=split)
        b, _ = fuelmix_intensity(fuel_mix.get(k), k, embedded.get(k), split=split,
                                 other_priced_as="OTHER")
        if a is not None and b is not None:
            acc.setdefault(k[0][:4], []).append((b - a) * scale)
    return {y: sum(v) / len(v) for y, v in sorted(acc.items())}


def _input_fingerprint() -> list:
    paths = [*FUELHH_CACHE_PATHS, nci.CACHE_PATH, NESO_EXTENSION_CACHE_PATH, Path(neg.CACHE_PATH)]
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
    parser.add_argument("--fetch-neso-extension", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args(argv)
    if args.fetch_neso_extension:
        return fetch_neso_extension()
    if args.rebuild:
        series, meta = build()
        write_built(series, meta)
    else:
        series, meta = load_series()

    def table(title: str, stats: Mapping[str, Mapping[str, float]]) -> None:
        print(title)
        print(f"  {'year':<5} {'n':>7} {'corr':>7} {'bias g':>8} {'rmse g':>8} {'est':>7} {'neso':>7}")
        for year, s in stats.items():
            print(f"  {year:<5} {int(s['n']):>7} {s['correlation']:>7.4f} {s['mean_bias']:>+8.2f} "
                  f"{s['rmse']:>8.2f} {s['mean_estimate']:>7.1f} {s['mean_published']:>7.1f}")

    table("Overlap, raw fuel-mix arithmetic vs NESO published (bias = estimate - published):",
          meta["overlap_statistics"])
    table(f"Same, over the fit window {meta['scale_fit_window']}:", meta["overlap_statistics_fit_window"])
    print(f"Scale fitted on {meta['scale_fit_window']} (n={meta['scale_fit_n']}): "
          f"{meta['scale_fitted']:.4f}  <- applied to fuelmix_estimate only")
    print(f"Scale fitted on the whole overlap {list(OVERLAP_WINDOW)}: {meta['scale_whole_overlap']:.4f}  "
          "(not applied; spans NESO's 2020-04 level step)")
    print(f"BIOMASS first published in FUELHH: {meta['biomass_split']}; before it OTHER is "
          f"priced as {PRE_SPLIT_OTHER_PRICED_AS}. If OTHER kept its own factor instead, mean change, g:")
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
