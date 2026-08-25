"""NESO's PUBLISHED half-hourly carbon intensity — the independent truth series.

REUSE: sim/neso_carbon_intensity.py
CLASS: CUSTOM
INDEX: searched "carbon", "intensity", "NESO", "national grid", "gCO2", "adapter", "ingest",
       "published series". `sim/grid_carbon_intensity.py` is the nearest organ and is the
       thing this exists to be checked AGAINST, not merged with: it RECONSTRUCTS a shape from
       Elexon demand and renewable outturn through a dispatch model, and this READS the number
       NESO publishes. Two independent routes to one quantity is the entire point, so they must
       stay two modules (R15 TAUTOLOGY: a checker that derives its value from the thing it
       checks is not a checker). The fetch/cache PATTERN is reused from
       `sim/generation_demand_history.py` + `sim/cache_store.py` rather than reinvented.

WHY THIS EXISTS
---------------
`sim/grid_carbon_intensity.py` names its own error bars honestly and then says the sentence
that made this atom necessary:

    "this shape's quietest half hours sit around 0.05 of average against NESO's published
     series bottoming out nearer 0.16"

That comparison had never been made. No NESO series existed anywhere in this tree, no fetch had
ever run, and `docs/design/frame/E5_carbon_three_ledger_FRAME.md` still carries the row
"value UNVERIFIED -- needs NESO/DESNZ fetch". The number was a recollection presented in the
grammar of a measurement, in the one docstring whose job is to state which way the errors point.
This module makes it a measurement or corrects it.

It is also the COUPLED-TRIAD rung (CLAUDE.md): no world/SIM atom reaches L3 until the company
has been tested against it AND THE GAP MEASURED. The gap needs a truth series to be measured
against. This is that series, and it is genuinely independent -- NESO's number comes from its
own metered generation mix and its own methodology, and shares no input, no constant and no line
of code with the reconstruction.

WHAT NESO PUBLISHES, AND WHY IT IS NOT THE SAME QUANTITY
--------------------------------------------------------
`api.carbonintensity.org.uk` is key-free, openly licensed, half-hourly, from 2018-05-11. Each
half hour carries a FORECAST and an ACTUAL, in gCO2/kWh. The differences from the reconstruction
are not noise and must never be averaged away:

  * NESO's series is LOSS-CORRECTED to a consumed basis; the reconstruction is at Elexon's
    transmission boundary. Applying a second correction on top of either is item 2 of the
    disqualification battery -- so this module applies NONE, and the basis is carried in
    `PUBLISHED_BASIS` for anything that publishes from it.
  * NESO COUNTS INTERCONNECTOR IMPORTS at the exporting country's intensity; the reconstruction
    does not model them at all.
  * NESO COUNTS COAL; the reconstruction dispatches none.
  * NESO is ABSOLUTE gCO2/kWh; the reconstruction is deliberately DIMENSIONLESS, because there
    is exactly one absolute annual grid-intensity series in this codebase and
    `company/regulatory/carbon_emissions.py` owns it (`tools/grid_intensity_guard.py` fails a
    second one).

The last of those is why `published_shape()` exists and why the comparison happens in SHAPE
space. Comparing grams to grams would require this module to publish a second absolute series
and would fail the guard. Comparing shape to shape asks the question that actually matters for
the mission -- does the grid's carbon move within the day by as much as we think it does -- and
it asks it in a form where a level difference between the two bases cannot masquerade as a
timing difference.

WHAT THIS DOES NOT DO
---------------------
  * NO REGIONAL SERIES. NESO publishes 14 and they are MODELLED from a reduced network model
    rather than measured. The abatement ledger will eventually want them; nothing in the tree
    can use one yet, and fetching a series no consumer reads is how `docs/market_data/` grew a
    feed that was rewritten every cycle for no reader. When a consumer exists, extend here.
  * NO FORECAST-VS-OUTTURN GRADING. Both are parsed and both are kept, because they answer
    different questions -- forecast is what a customer could have acted on, outturn is what
    happened -- but grading advice against outturn is a foresight leak and this module offers
    no helper that would make it convenient.
  * NO WRITING TO `docs/market_data/`. This is world truth for the HARNESS to measure the
    company's belief against. The company reads the shape feed and must go on being wrong in
    the ways named there; handing it NESO's series would delete the gap instead of measuring it.

Run:  python3 -m sim.neso_carbon_intensity --from 2019-01-01 --to 2024-12-31
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections.abc import Iterable, Mapping
from datetime import date as date_cls
from datetime import datetime, time as time_cls, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

#: GB settlement days are defined on the LOCAL clock, so this is not a formatting preference.
LONDON = ZoneInfo("Europe/London")

API_ROOT = "https://api.carbonintensity.org.uk"

#: The API serves 30 days per request and refuses more. Not a tuning knob -- a documented limit.
MAX_WINDOW_DAYS = 30

#: 2018-05-11 is the first half hour the service holds. Asking for earlier returns an empty
#: window rather than an error, which is exactly the fail-open shape that would silently
#: shorten the comparison, so callers are refused instead.
FIRST_PUBLISHED_DATE = "2018-05-11"

CACHE_PATH = Path("sim/cache/neso_carbon_intensity_national.json")

#: R14 applied to a basis. Every consumer carries this forward verbatim; it is the half of the
#: comparison that explains why the two series may legitimately differ in LEVEL.
PUBLISHED_BASIS = (
    "gCO2/kWh, national, half-hourly, NESO/National Grid Carbon Intensity API "
    "(api.carbonintensity.org.uk, key-free, openly licensed). Consumption basis: "
    "LOSS-CORRECTED, INCLUDES interconnector imports at the exporting country's intensity, "
    "INCLUDES coal. Both forecast and actual are published; 'actual' is outturn."
)


class NesoIntensityUnavailable(Exception):
    """The published series could not be obtained or held nothing usable.

    Raised rather than returning an empty or flat series, for the same reason
    `grid_carbon_intensity.ShapeUnavailable` exists: a flat truth series would read as "the two
    series agree perfectly" -- the most flattering possible answer -- when what happened is that
    the check did not run (R15 FAIL-SILENT: an unavailable check is a FAILED check).
    """


def settlement_key(instant: datetime) -> tuple[str, int]:
    """A UTC instant -> (settlement date, settlement period), on GB's actual definition.

    THE PERIOD IS COUNTED FROM LOCAL MIDNIGHT IN ELAPSED REAL TIME, not from the local clock
    reading, and that is the whole subtlety. A clock-arithmetic version (`local.hour*2 +
    local.minute//30 + 1`) agrees on 363 days a year and is wrong on the two that matter: it
    yields two half hours both numbered 3 on the autumn transition day and silently drops one,
    and it numbers the spring day's periods 1..48 when that day has only 46. Counting elapsed
    half hours since local midnight gets 46 and 50 for free, because that is what the GB
    definition means.

    Midnight is used as the anchor precisely because it is the one local time that is never
    ambiguous and never skipped -- GB transitions happen at 01:00/02:00 local.
    """
    if instant.tzinfo is None:
        raise ValueError("a naive datetime has no settlement period; pass an aware UTC instant")
    local = instant.astimezone(LONDON)
    local_date = local.date()
    midnight = datetime.combine(local_date, time_cls(0, 0), tzinfo=LONDON)
    elapsed = (instant - midnight).total_seconds()
    if elapsed < 0:
        raise ValueError(f"{instant!r} precedes its own local midnight")
    return local_date.isoformat(), int(elapsed // 1800) + 1


def _fetch_window(start: date_cls, end: date_cls, *, timeout: float = 60.0) -> list[dict]:
    """One API window. `end` is EXCLUSIVE of its own final half hour by the API's own convention."""
    url = f"{API_ROOT}/intensity/{start.isoformat()}T00:00Z/{end.isoformat()}T00:00Z"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        raise NesoIntensityUnavailable(f"NESO carbon intensity fetch failed for {url}: {exc}") from exc
    data = payload.get("data")
    if not isinstance(data, list):
        raise NesoIntensityUnavailable(f"NESO returned no `data` list for {url}: {payload!r}")
    return data


def fetch_national(start_date: str, end_date: str, *, pause_s: float = 0.2) -> list[dict]:
    """Raw half-hourly national records over [start_date, end_date], walked in API windows.

    Returns the API's own record shape untouched. Parsing is `to_settlement_periods`, so that a
    cache written today stays re-parsable if the parse is ever found wrong.
    """
    if start_date < FIRST_PUBLISHED_DATE:
        raise NesoIntensityUnavailable(
            f"NESO publishes from {FIRST_PUBLISHED_DATE}; {start_date} predates the series. "
            "Asking anyway returns an empty window, which would silently shorten the comparison."
        )
    start = date_cls.fromisoformat(start_date)
    end = date_cls.fromisoformat(end_date)
    if end < start:
        raise ValueError(f"end {end_date} precedes start {start_date}")

    out: list[dict] = []
    cursor = start
    while cursor <= end:
        window_end = min(cursor + timedelta(days=MAX_WINDOW_DAYS), end + timedelta(days=1))
        out.extend(_fetch_window(cursor, window_end))
        cursor = window_end
        if cursor <= end:
            time.sleep(pause_s)
    if not out:
        raise NesoIntensityUnavailable(f"no records returned for {start_date}..{end_date}")
    return out


def to_settlement_periods(records: Iterable[Mapping]) -> dict[tuple[str, int], dict[str, float]]:
    """Raw API records -> {(settlement date, period): {"actual": g, "forecast": g}}.

    A HALF HOUR WITH A NULL `actual` IS DROPPED, NOT ZEROED. NESO publishes nulls for half hours
    whose metered mix never settled, and zero grams is not merely wrong there, it is wrong in the
    direction that inflates the value of time-shifting without bound -- the same failure the
    reconstruction's must-run floor was written to avoid. `forecast` is carried alongside when
    present and never substituted for a missing actual (R15 FAIL-OPEN).

    AND A PUBLISHED ZERO IS TREATED AS THE SAME ABSENCE, which was found by this module's own
    first run against the real feed rather than reasoned about in advance. Over 2019-2024 the
    API returns `actual: 0` for exactly FIVE half hours, all in 2023, four of them CONSECUTIVE
    on 2023-06-07 -- the signature of a feed outage, not of physics. GB's grid cannot reach zero
    gCO2/kWh: biomass and gas are always running, and the lowest genuine reading in six years is
    14. Accepting those five would have been the more expensive kind of fail-open, because a
    single zero in the denominator is what the SPREAD statistic divides by: it took the measured
    2023 spread from a finite number to a ZeroDivisionError, and had the guard been placed one
    line later it would instead have reported the cleanest possible grid as fact.
    """
    out: dict[tuple[str, int], dict[str, float]] = {}
    for record in records:
        start = record.get("from")
        intensity = record.get("intensity") or {}
        if not start:
            continue
        actual = intensity.get("actual")
        if actual is None or float(actual) <= 0.0:
            continue
        try:
            instant = datetime.strptime(str(start), "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
            key = settlement_key(instant)
        except ValueError:
            continue
        entry: dict[str, float] = {"actual": float(actual)}
        forecast = intensity.get("forecast")
        if forecast is not None:
            entry["forecast"] = float(forecast)
        out[key] = entry
    if not out:
        raise NesoIntensityUnavailable(
            "no half hour carried a non-null `actual`. This is an absence, not a clean grid."
        )
    return out


def actual_by_period(series: Mapping[tuple[str, int], Mapping[str, float]]) -> dict[tuple[str, int], float]:
    """{(date, period): gCO2/kWh outturn} — the plain view most callers want."""
    return {key: float(value["actual"]) for key, value in series.items() if "actual" in value}


def published_shape(
    intensity_by_period: Mapping[tuple[str, int], float],
    demand_by_period: Mapping[tuple[str, int], float],
) -> dict[tuple[str, int], float]:
    """NESO's grams -> the SAME dimensionless shape the reconstruction produces.

    Normalised per calendar year to a DEMAND-WEIGHTED mean of 1.0, deliberately identical to
    `grid_carbon_intensity.build_shape`, because a comparison between two series normalised
    differently measures the normalisation. Demand comes from Elexon, the same weights both
    sides -- that is shared INPUT to the comparison, not shared derivation of the quantity being
    compared, so it does not make the check a tautology; it is what makes it like-for-like.

    Half hours with no demand weight are skipped rather than weighted at zero, so the mean is
    over what was actually observed on both sides.
    """
    weighted: dict[str, list[float]] = {}
    usable: dict[tuple[str, int], float] = {}
    for key, grams in intensity_by_period.items():
        weight = demand_by_period.get(key)
        if weight is None or float(weight) <= 0.0:
            continue
        usable[key] = float(grams)
        acc = weighted.setdefault(key[0][:4], [0.0, 0.0])
        acc[0] += float(grams) * float(weight)
        acc[1] += float(weight)

    if not usable:
        raise NesoIntensityUnavailable(
            "no half hour had BOTH a published intensity and a demand weight, so there is no "
            "published shape to compare against."
        )

    shape: dict[tuple[str, int], float] = {}
    for key, grams in usable.items():
        total, weight = weighted[key[0][:4]]
        if weight <= 0.0 or total <= 0.0:
            continue
        shape[key] = grams / (total / weight)
    if not shape:
        raise NesoIntensityUnavailable("every year's demand-weighted mean published intensity was zero")
    return shape


def compare_shapes(
    reconstructed: Mapping[tuple[str, int], float],
    published: Mapping[tuple[str, int], float],
    demand_by_period: Mapping[tuple[str, int], float],
    year: str,
) -> dict[str, float]:
    """The GAP, on the half hours BOTH series cover, RE-NORMALISED over that intersection.

    The re-normalisation is not tidiness. Each series arrives normalised over its own coverage;
    if one is missing a fortnight of dirty winter half hours its mean is lower and every one of
    its shape values is correspondingly higher, and the difference that shows up is the coverage,
    not the physics. Re-normalising both over the common keys removes exactly that.

    Returns the diagnostic set, never a verdict -- R12: this is a measurement, and no constant
    anywhere may be tuned to move it.
    """
    common = [
        key
        for key in reconstructed
        if key in published and key[0][:4] == year and float(demand_by_period.get(key) or 0.0) > 0.0
    ]
    if not common:
        raise NesoIntensityUnavailable(f"the two series share no demand-weighted half hour in {year}")

    def _renormalised(
        source: Mapping[tuple[str, int], float],
    ) -> tuple[dict[tuple[str, int], float], float]:
        total = sum(source[k] * float(demand_by_period[k]) for k in common)
        weight = sum(float(demand_by_period[k]) for k in common)
        mean = total / weight
        if mean <= 0.0:
            raise NesoIntensityUnavailable(f"a series had a non-positive demand-weighted mean in {year}")
        return {k: source[k] / mean for k in common}, mean

    # THE DIVISOR IS RETURNED, NOT ONLY USED. Every caller that wants to put ONE half hour of
    # the two series beside each other -- a household's meter read, say -- has to re-normalise
    # it the same way this function does, or it measures the coverage difference instead of the
    # physics. Handing back the constant is what makes that reproducible outside this function;
    # recomputing it at the call site is how the two normalisations drift apart.
    ours, ours_divisor = _renormalised(reconstructed)
    theirs, theirs_divisor = _renormalised(published)

    # A SPREAD IS max/min, SO min IS A DENOMINATOR. Guarded by name rather than left to
    # ZeroDivisionError because the traceback names the arithmetic and not the cause; the cause
    # is always a half hour that should have been dropped upstream as absent.
    for label, series in (("reconstructed", ours), ("published", theirs)):
        if min(series.values()) <= 0.0:
            raise NesoIntensityUnavailable(
                f"the {label} shape has a non-positive value in {year}, so its spread is "
                "undefined. A zero-carbon half hour is an absent reading, not a clean grid."
            )

    errors = [ours[k] - theirs[k] for k in common]
    abs_errors = [abs(e) for e in errors]
    # BOTH SERIES ALSO MEASURED ON THE STATISTIC THE PAGE ACTUALLY QUOTES (2026-08-25, Expert
    # Hour finding). max/min is a spread between two single half hours -- "one reading of one
    # meter", as this generator's own docstring says about exactly this shape of number -- and
    # it is NOT what the customer panel prints. That panel prints p95/p5. Publishing only the
    # max/min ratio meant the page compared a p95/p5 spread against a max/min-derived
    # correction factor and called the result "wider than", which is two different statistics
    # wearing one word. Both are returned so a caller can compare like with like and the
    # tail-sensitive one stays visible beside the robust one rather than being replaced by it.
    p95_ours, p5_ours = _percentile(sorted(ours.values()), 0.95), _percentile(sorted(ours.values()), 0.05)
    p95_theirs = _percentile(sorted(theirs.values()), 0.95)
    p5_theirs = _percentile(sorted(theirs.values()), 0.05)
    for label, low in (("reconstructed", p5_ours), ("published", p5_theirs)):
        if low <= 0.0:
            raise NesoIntensityUnavailable(
                f"the {label} shape's 5th percentile is non-positive in {year}, so its p95/p5 "
                "spread is undefined"
            )
    return {
        "year": float(year),
        "half_hours": float(len(common)),
        "reconstructed_min": min(ours.values()),
        "published_min": min(theirs.values()),
        "reconstructed_max": max(ours.values()),
        "published_max": max(theirs.values()),
        "reconstructed_spread": max(ours.values()) / min(ours.values()),
        "published_spread": max(theirs.values()) / min(theirs.values()),
        "reconstructed_p95_over_p5": p95_ours / p5_ours,
        "published_p95_over_p5": p95_theirs / p5_theirs,
        "mean_error": sum(errors) / len(errors),
        "mean_abs_error": sum(abs_errors) / len(abs_errors),
        "correlation": _correlation([ours[k] for k in common], [theirs[k] for k in common]),
        "reconstructed_renormalisation_divisor": ours_divisor,
        "published_renormalisation_divisor": theirs_divisor,
    }


def _percentile(sorted_values: list[float], fraction: float) -> float:
    """The nearest-rank percentile, DELIBERATELY IDENTICAL to the one the feed generator uses.

    The whole point of the p95/p5 pair returned by `compare_shapes` is that it can be set beside
    the number the customer panel prints, which `tools/generate_grid_intensity_feed.py::year_stats`
    computes with its own copy of this rule. Two percentile conventions -- nearest-rank here,
    interpolated there -- would put a few per cent of silent disagreement into a comparison whose
    only job is to be like-for-like, which is the finding this function exists to close in a
    subtler form. `test_the_two_percentile_implementations_cannot_drift_apart` fails if they part.
    """
    if not sorted_values:
        raise NesoIntensityUnavailable("no values to take a percentile of")
    index = min(int(fraction * len(sorted_values)), len(sorted_values) - 1)
    return sorted_values[index]


def _correlation(a: list[float], b: list[float]) -> float:
    n = len(a)
    mean_a, mean_b = sum(a) / n, sum(b) / n
    cov = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    var_a = sum((x - mean_a) ** 2 for x in a)
    var_b = sum((y - mean_b) ** 2 for y in b)
    if var_a <= 0.0 or var_b <= 0.0:
        return 0.0
    return cov / (var_a * var_b) ** 0.5


def load_cached() -> list[dict]:
    """The cached raw records, or a refusal. Never an empty list dressed as a cache hit."""
    if not CACHE_PATH.exists():
        raise NesoIntensityUnavailable(
            f"{CACHE_PATH} does not exist. Run `python3 -m sim.neso_carbon_intensity` to build it. "
            "An absent truth series is a failed comparison, not a passed one."
        )
    records = json.loads(CACHE_PATH.read_text())
    if not records:
        raise NesoIntensityUnavailable(f"{CACHE_PATH} is empty")
    return records


def write_cache(records: list[dict]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(records, separators=(",", ":")))


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Fetch and cache NESO's published carbon intensity.")
    parser.add_argument("--from", dest="start", default="2019-01-01")
    parser.add_argument("--to", dest="end", default="2024-12-31")
    args = parser.parse_args(argv)

    records = fetch_national(args.start, args.end)
    write_cache(records)
    series = to_settlement_periods(records)
    print(f"{len(records):,} raw records -> {len(series):,} half hours with an actual")
    print(f"cached to {CACHE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
