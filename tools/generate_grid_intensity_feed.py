#!/usr/bin/env python3
"""Publish the half-hourly grid-intensity SHAPE as a market-data feed the company can read.

REUSE: tools/generate_grid_intensity_feed.py
CLASS: CUSTOM
INDEX: searched "feed", "market_data", "publish", "generate", "intensity", "carbon". The
       publishing PATTERN is reused wholesale rather than invented -- `docs/market_data/
       price_feed.json` and `consumption_feed.json` are already how a world quantity reaches
       the company layer, both `{published_at, records}`, both written by a producer on the
       world side and read by name on the company side. This is the third feed of that shape
       and it deliberately looks identical. The VALUES come from `sim/grid_carbon_history.py`;
       nothing is recomputed here except the per-year normalisation.

WHERE THE NUMBERS COME FROM (since 2026-10-05). The director's ruling: "For historical periods,
take the published series and align it to settlement." So this feed is NESO's published national
carbon intensity, aligned to settlement periods by `sim/grid_carbon_history.py`: NESO's Historic
GB Generation Mix, one GENERATION basis for 2016-2025. In the few half hours it has no usable value
the value is NESO's own arithmetic on Elexon's published fuel mix, and every record says which
(`source`). It was the Carbon Intensity API until later the same day, when the API was found to
change basis at 2020-04-27 P34; the API is now what each record's `published` value and
`versus_published` compare against, two NESO series side by side. Until 2026-10-05 this feed
published EP13's dispatch RECONSTRUCTION (`sim/grid_carbon_intensity.py`).
`reconstruction_shape()` below still builds it, for EP13 to be graded with, but it is not
published.

WHY A FEED AND NOT AN IMPORT. The company may not import `sim.*` -- that is the epistemic wall,
and `tests/architecture/test_epistemic_wall_ratchet.py` refuses a new crossing. But a GB supplier
DOES read a published half-hourly carbon-intensity series: NESO publishes one, openly licensed,
and reading it is as ordinary as reading a price feed. So the crossing is a published FILE, which
is the shape the wall already sanctions, and the company's carbon numbers become a reading of a
feed rather than a look inside the world.

WHAT IS IN IT, and the two-part structure is not padding:

  `records`      -- the most recent fortnight at half-hourly grain, PLUS every dated day that
                    an already-published company-side artefact holds half-hourly reads for.
                    A supplier pulls the history it has meter data for; NESO's own API serves
                    any half hour back to 2018, so the bound here is a file-size decision and
                    never an epistemic one, and it must not become the reason a day the company
                    CAN measure goes unmeasured.
  `typical_day`  -- per year, the mean shape of each of the 48 settlement periods. 480 numbers
                    for a decade, and it is what a profile-class customer's carbon has to be
                    computed against, since a profiled household has no half-hourly read of its
                    own to meet.
  `by_year`      -- summary statistics for EVERY year, including the ones the records do not
                    cover.

WHY THE RECORDS ARE BOUNDED AT A FORTNIGHT, and it was twelve months in the first draft. The
full 2016-2025 series is 157,125 half hours; published in this format it is 1.24 MB against
6.7 KB for the price feed and 25 KB for the consumption feed, and it is rewritten on every
publish cycle. That is 200x the rest of `docs/market_data/` put together, growing the history by
a megabyte a cycle, on a machine whose memory headroom the director has just named as a budget
being spent rather than a problem solved. A fortnight of records plus a typical day plus the
year summaries answers every question the twelve months could, at 2% of the size.

The bound is NAMED IN THE FILE (`records_cover`, `series_covers`) rather than left implicit,
because a silent bound is how "the feed starts in 2024" becomes a fact about the grid instead
of a fact about the file.

Run:  python3 -m tools.generate_grid_intensity_feed
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# `aggregate_renewable_generation` is re-exported for the EP13 instruments, which reproduce the
# pre-s19 model (wind+solar in the residual) so their recorded numbers stay reproducible.
from sim.generation_demand_history import (  # noqa: F401
    aggregate_renewable_generation,
    aggregate_solar_generation,
    aggregate_wind_generation,
)
from sim.grid_carbon_intensity import (
    ShapeUnavailable,
    aggregate_demand,
    build_shape,
    demand_weighted_mean,
)

PROJECT = Path(__file__).resolve().parent.parent
DEMAND_CACHE = PROJECT / "sim" / "cache" / "elexon_demand_full.json"
AGWS_CACHE = PROJECT / "sim" / "cache" / "elexon_agws_full.json"
OUT_PATH = PROJECT / "docs" / "market_data" / "grid_intensity_feed.json"

#: How much half-hourly detail the feed carries. See the docstring for why it is bounded and
#: why `by_year` exists so that the bound cannot be mistaken for the end of the data.
RECORD_WINDOW_DAYS = 14

#: How much of a year the two series must SHARE before that year's spread counts toward the
#: headline. A spread is a max over a min across a whole year, so a partial year's extremes are
#: whatever happened to fall inside the overlap.
#:
#: MEASURED, AND IT WAS FLATTERING US (2026-08-25). Without this guard 2018 entered the average
#: on ONE shared half hour -- NESO publishes from 2018-05-11 and the demand outturn barely
#: reaches it -- so its "spread" was that single value divided by itself, exactly 1.0, and its
#: correlation exactly 0.00. A perfect-agreement year built from one reading dragged the
#: published overstatement from 3.15x down to 2.85x, i.e. made this model look 10% closer to the
#: real grid than it is. Every vacuous row here points the same way, because a degenerate spread
#: is always 1.0 and 1.0 is the answer we would like.
#:
#: A month is the floor rather than a sufficiency claim: it is the smallest window containing
#: both weekday peaks and weekend troughs across a range of weather. Years that fall short are
#: REPORTED in `excluded_years` with their count, never dropped silently.
MIN_SHARED_HALF_HOURS = 48 * 30

#: Already-published, company-visible artefacts that name the dated days the company holds
#: half-hourly reads for. Read to SIZE the feed, never to compute anything in it.
#:
#: THIS IS NOT THE FEED COUPLING ITSELF TO ITS CONSUMERS, and the distinction is worth stating
#: because it looks like it at first glance. The first version published a flat trailing window
#: and the Explore page's two named days -- 2021-02-11 and 2022-06-24, both chosen from a
#: meter's ten-year record -- fell outside it, so the page would have shown a household's
#: half-hourly consumption beside no carbon at all. Not zero carbon: none, silently. A feed
#: whose window is chosen without reference to what anyone has meter reads for is a feed that
#: is smaller than it is useful.
READ_BEARING_ARTEFACTS = (
    PROJECT / "site" / "data" / "explore_hh_days.json",
    PROJECT / "docs" / "market_data" / "consumption_feed.json",
)


def dates_with_reads(paths=READ_BEARING_ARTEFACTS) -> set[str]:
    """Every ISO date string appearing as a `date` anywhere in the given JSON artefacts.

    Deliberately structural rather than schema-aware: the two artefacts have different shapes
    today and a third will have a third, and a walker that looks for a `date` key survives that
    where a per-file parser would quietly stop finding days. A missing or unreadable artefact
    contributes nothing and is not an error -- the trailing window still publishes.
    """
    found: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            value = node.get("date")
            if isinstance(value, str) and len(value) == 10 and value[4] == value[7] == "-":
                found.add(value)
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    for path in paths:
        try:
            walk(json.loads(Path(path).read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    return found

#: The history's source tags that are NESO's series or NESO's own arithmetic, never a model of
#: ours. A shape built only from these is compared with the API as two NESO series.
NESO_SHAPE_SOURCES = ("neso_historic_mix", "fuelmix_fill")

#: What the published numbers are. `published_shape`'s normalisation, stated so a reader can undo it.
HISTORY_BASIS = (
    "dimensionless: each half hour's gCO2/kWh from sim/grid_carbon_history.py divided by its "
    "calendar year's DEMAND-WEIGHTED mean (Elexon INDO demand), so each year averages 1.0. The "
    "gCO2/kWh is NESO's Historic GB Generation Mix CARBON_INTENSITY, national outturn, on a "
    "GENERATION basis: CO2 at the generator per kWh generated, the generation counted including "
    "embedded wind and solar and imports at NESO's import factors. Transmission and distribution "
    "losses are NOT included. Where that series has no usable value it is NESO's own methodology "
    "applied to Elexon's published half-hourly fuel mix (FUELHH) plus NESO's embedded wind and "
    "solar estimate, at NESO's published factors. Every record carries its `source`."
)

#: Named on the face of the feed, because a consumer that does not know these cannot state them
#: and the advisor's scope brief makes stating them the condition of publishing at all
#: ("a carbon figure without its basis is not a measurement, it is a slogan").
NAMED_GAPS = [
    "TRANSMISSION AND DISTRIBUTION LOSSES ARE NOT IN THIS SERIES. It is generation basis: CO2 per "
    "kWh generated, not per kWh delivered to a home. Whether a household figure adds losses is a "
    "definition the consumer must state; if it does, they are a separate named line (DESNZ "
    "publishes a T&D factor), never folded into this value",
    "NESO's Historic GB Generation Mix is the file as NESO serves it on the day it was fetched "
    "(`history.historic_mix_edition` names its last half hour), revised in hindsight. No supplier "
    "could have read this exact edition at the time; every value here is outturn with hindsight",
    "NESO's Carbon Intensity API, the `published` value on each record and the side "
    "`versus_published` compares with, CHANGES BASIS at 2020-04-27 period 34: it reads about "
    "1.14x the historic mix before that half hour and about 1.02x after "
    "(`history.api_step`). It is a cross-check, never the series",
    "before 2017-11-01 Elexon publishes no BIOMASS fuel type and biomass sits inside OTHER; in a "
    "`fuelmix_fill` half hour that OTHER is priced at NESO's biomass factor. No 2016-2017 half "
    "hour is filled today, so this reaches no published value",
    "where the historic mix has no usable value (a null, zero or above-ceiling intensity, or "
    "transmission wind and hydro both exactly 0 MW, its partial-outage signature) the value is "
    "filled from the fuel mix UNSCALED (`source: fuelmix_fill`)",
    "a half hour with neither source is ABSENT from the feed, never interpolated. Elexon's mix "
    "has its own outage signature, every fuel at 0 MW, which is refused rather than priced",
    "national only -- no regional series is offered, modelled or otherwise",
    "outturn, never forecast: this grades what happened and must not judge shifting advice",
    "imports carry NESO's fixed import factors, not the exporting country's intensity in that "
    "half hour",
    "normalised per calendar year over the half hours Elexon's demand record covers, which runs "
    "2016-03-01..2025-06-07, so 2016 and 2025 are normalised over the part of the year it covers",
]

#: The one a reader should take away, and it is no longer about a model. The feed IS the published
#: series where one exists; what remains is the estimate before it, measured, and the forecast
#: ceiling, which no series can remove. Both quoted figures are held to the feed by a test.
ERROR_DIRECTION = (
    "This shape IS NESO's published national carbon intensity -- its Historic GB Generation Mix, "
    "one generation basis for the whole decade -- aligned to settlement periods, not a model of "
    "it. NESO's other published series, the Carbon Intensity API, is measured beside it and agrees "
    "to within about 2% after 2020-04-27; before that date the API carried a loss uplift and reads "
    "about 14% higher. THE ERROR THAT REMAINS IS NOT ABOUT THIS SHAPE. Every figure here is "
    "OUTTURN, computed with hindsight, and a household has to act on a FORECAST. Graded against "
    "NESO's own outturn, NESO's own published forecast picks a three-hour window that delivers "
    "about 84% of that day's achievable within-day saving on the mean day, about 45% on the worst "
    "day in twenty, and on some days a window DIRTIER than not shifting at all. So a timing "
    "benefit read off this feed is an UPPER BOUND on what advice could have delivered, and that "
    "ceiling cannot be built away by improving any model."
)


def _percentile(sorted_values: list[float], fraction: float) -> float:
    if not sorted_values:
        raise ShapeUnavailable("no values to take a percentile of")
    index = min(int(fraction * len(sorted_values)), len(sorted_values) - 1)
    return sorted_values[index]


def summarise(shape: dict, demand: dict) -> dict:
    """Per-year statistics for the WHOLE series, records window or not.

    `p5`/`p95` lead and min/max follow, because min and max are single half hours out of
    seventeen thousand and a claim resting on either is resting on one reading of one meter.
    """
    out = {}
    for year in sorted({key[0][:4] for key in shape}):
        values = sorted(v for k, v in shape.items() if k[0][:4] == year)
        out[year] = {
            "half_hours": len(values),
            "demand_weighted_mean": round(demand_weighted_mean(shape, demand, year), 6),
            "p5": round(_percentile(values, 0.05), 4),
            "p50": round(_percentile(values, 0.50), 4),
            "p95": round(_percentile(values, 0.95), 4),
            "min": round(values[0], 4),
            "max": round(values[-1], 4),
            "p95_over_p5": round(_percentile(values, 0.95) / _percentile(values, 0.05), 2),
        }
    return out


def typical_day(shape: dict) -> dict:
    """{year: [mean shape for settlement period 1..48]}.

    THE ONLY THING A PROFILED HOUSEHOLD CAN BE MEASURED AGAINST. 249 of the 263 accounts on this
    book have a traditional meter and no half-hourly read at all, so their carbon cannot be met
    half hour by half hour with anything. What it CAN be met with is the average day -- which is
    an estimate, says so, and is the same estimate a real supplier makes for a profile-class
    customer.

    A mean, not a median: the quantity being averaged is an emissions RATE that will be
    multiplied by consumption and summed, so the arithmetic mean is the one that composes.
    """
    sums: dict[str, list[float]] = {}
    counts: dict[str, list[int]] = {}
    for (date_str, period), value in shape.items():
        year = date_str[:4]
        s = sums.setdefault(year, [0.0] * 48)
        c = counts.setdefault(year, [0] * 48)
        if 1 <= period <= 48:
            s[period - 1] += value
            c[period - 1] += 1
    return {
        year: [round(s / c, 4) if c else None
               for s, c in zip(sums[year], counts[year])]
        for year in sorted(sums)
    }


#: What `annual_level` publishes, stated so a reader can repeat it. Since 2026-10-05 this is the
#: ONLY annual grid-intensity level the company reads (`company/regulatory/carbon_emissions.py`).
ANNUAL_LEVEL_BASIS = (
    "gCO2/kWh, national, per calendar year: the DEMAND-WEIGHTED mean (Elexon INDO) of the "
    "half-hourly series this feed's shape is built from, over exactly the half hours the shape is "
    "normalised over -- so `shape x mean` gives back the published half-hourly value. It is "
    "NESO's Historic GB Generation Mix intensity, GENERATION basis: CO2 per kWh generated, "
    "transmission and distribution losses NOT included (measured: its implied fuel factors are "
    "NESO's table with no loss multiplier). CO2 at the generator from NESO's factor table (DUKES "
    "emission factors): not lifecycle, not CO2e, no upstream. `fuelmix_fill` half hours are "
    "NESO's arithmetic on Elexon's mix, unscaled; `sources` gives the mix per year. "
    "A year whose demand record does not span 1 Jan - 31 Dec is published with `complete: false` "
    "and the dates it covers; it is a mean of that span, never the year's."
)

#: Why demand weighting and not a plain time mean, said once. Kept beside the basis because it is
#: the choice a reader is most likely to undo.
ANNUAL_LEVEL_WEIGHTING = (
    "demand-weighted (Elexon INDO). Two reasons. (1) It is the divisor the shape is normalised "
    "by, so a household's half-hourly carbon, shape x level, is NESO's own number half hour by "
    "half hour; any other level would rescale every half hour by a constant that is not 1. "
    "(2) A household's annual kWh times one annual figure is only right if that figure is "
    "weighted the way consumption falls, and consumption is heaviest in the high-demand, "
    "dirtier half hours: the time-weighted mean UNDERSTATES it (2024: 124 against 132). "
    "National demand is not a domestic profile -- it includes industry and commerce -- and the "
    "domestic Profile Class 1 weighting reads within 2.5 g of it in every whole year 2017-2024 "
    "(docs/market_research/household_carbon_and_the_measures_that_save_it.md s2). The time-"
    "weighted mean is published beside it as a diagnostic and is never the level."
)


def annual_level(readings: dict, demand: dict) -> dict:
    """{year: the published annual level and what it covers}, from `{key: (grams, source)}`.

    The mean is over the half hours that have BOTH a value and a positive demand weight, which is
    the set `sim.neso_carbon_intensity.published_shape` normalises over -- held equal by a test,
    because if they drift apart `shape x level` stops being the published value. A year with no
    such half hour is ABSENT, never 0 and never a neighbour's.
    """
    acc: dict[str, dict] = {}
    for (date_str, _period), (grams, source) in readings.items():
        if grams is None:
            continue
        year = date_str[:4]
        row = acc.setdefault(year, {"num": 0.0, "den": 0.0, "n": 0, "tw": 0.0, "tw_n": 0,
                                    "from": None, "to": None, "sources": {}})
        row["tw"] += float(grams)
        row["tw_n"] += 1
        weight = demand.get((date_str, _period))
        if weight is None or float(weight) <= 0.0:
            continue
        row["num"] += float(grams) * float(weight)
        row["den"] += float(weight)
        row["n"] += 1
        row["from"] = date_str if row["from"] is None else min(row["from"], date_str)
        row["to"] = date_str if row["to"] is None else max(row["to"], date_str)
        row["sources"][str(source)] = row["sources"].get(str(source), 0) + 1
    out = {}
    for year, row in sorted(acc.items()):
        if row["den"] <= 0.0:
            continue
        complete = row["from"] == f"{year}-01-01" and row["to"] == f"{year}-12-31"
        out[year] = {
            "mean_g_co2_per_kwh": round(row["num"] / row["den"], 2),
            "complete": complete,
            "covers": {"from": row["from"], "to": row["to"]},
            "partial_from": None if row["from"] == f"{year}-01-01" else row["from"],
            "partial_through": None if row["to"] == f"{year}-12-31" else row["to"],
            "half_hours": row["n"],
            "sources": dict(sorted(row["sources"].items())),
            "time_weighted_mean_g_co2_per_kwh": round(row["tw"] / row["tw_n"], 2),
            "time_weighted_half_hours": row["tw_n"],
        }
    return out


def published_series(demand: dict) -> tuple[dict | None, str, dict | None]:
    """(NESO's published shape on our normalisation, why-not, the parsed half hours).

    SPLIT OUT OF `versus_published` so it is fetched ONCE per run and used three times -- for
    the year-level comparison, for the per-half-hour values the records carry, and for
    `published_forecast_skill`. Building it again would multiply the cost of the one part of
    this generator that reads a 12 MB cache, on a machine whose memory the director has named
    as a budget being spent.

    THE THIRD ELEMENT IS THE RAW PARSE, forecast field and all, and it is deliberately NOT the
    shape: `forecast_skill` grades grams against grams within a day and a shape normalised over
    a year would have divided both sides by the same constant and lost the units the answer is
    stated in.
    """
    try:
        from sim import grid_carbon_history as history
        from sim import neso_carbon_intensity as neso

        # The live cache plus the 2018 and 2025 windows it does not hold (`history`'s loader).
        parsed = neso.to_settlement_periods(history.load_neso_records())
        return neso.published_shape(neso.actual_by_period(parsed), demand), "", parsed
    except Exception as exc:  # noqa: BLE001 -- an absent comparison is reported, never fatal
        return None, "{}: {}".format(type(exc).__name__, exc), None


def versus_published(shape: dict, demand: dict, published: dict | None = None,
                     why_unavailable: str = "", shape_is_neso: bool = False) -> dict:
    """This shape measured against NESO's own published series, per year.

    THE POINT OF PUBLISHING IT RATHER THAN KNOWING IT. A reader given a spread of 18.6x and the
    words "so timing is worth that much at most" will take that as a fact about the GRID. It is
    a fact about this MODEL: measured over the years both series cover, this shape swings about
    32x where NESO's swings about 11.4x, so every timing figure derived from it overstates the
    range by roughly 2.8x. A caveat that lives in a module docstring is not carried by the
    number when the number is quoted, and this one gets quoted.

    UNAVAILABLE IS SAID, NEVER OMITTED. If the published series has not been fetched into the
    cache this returns `{"available": False, "why": ...}` -- because a comparison silently
    missing from a feed reads as a comparison that came out clean, which is the one thing it
    must never read as (R15 fail-silent).
    """
    try:
        from sim import neso_carbon_intensity as neso
    except Exception as exc:  # noqa: BLE001 -- an absent comparison is reported, never fatal
        return {"available": False, "why": "{}: {}".format(type(exc).__name__, exc)}

    if published is None:
        published, why_unavailable, _ = published_series(demand)
    if published is None:
        return {"available": False, "why": why_unavailable}

    years = {}
    for year in sorted({k[0][:4] for k in shape}):
        try:
            measured = neso.compare_shapes(shape, published, demand, year)
        except Exception:  # noqa: BLE001 -- a year the two series do not share is simply absent
            continue
        # `None` SURVIVES INTO THE FEED AS `null` RATHER THAN BEING ROUNDED OR DROPPED. A
        # comparison term can be genuinely undefined -- a single-day year has no between-day
        # swing to be measured against -- and `round(None)` is a TypeError that would take the
        # whole publish down for a year that is merely short. Dropping the key instead would be
        # worse: an absent key reads to every consumer as a comparison that came out clean.
        row = {k: (None if v is None else round(v, 4)) for k, v in measured.items()}
        # THE TWO DIVISORS KEEP MORE DIGITS THAN EVERYTHING ELSE IN THIS ROW, because they are
        # the only values here that are DIVIDED BY rather than read. Four places would put a
        # 0.005% error into every household figure derived downstream -- small, but a rounding
        # artefact in a number whose whole job is to make two series comparable.
        for key in ("reconstructed_renormalisation_divisor", "published_renormalisation_divisor"):
            row[key] = round(measured[key], 8)
        row["counts_toward_headline"] = measured["half_hours"] >= MIN_SHARED_HALF_HOURS
        years[year] = row
    counting = [y for y in years.values() if y["counts_toward_headline"]]
    if not counting:
        return {"available": False,
                "why": ("no year shares at least {} half hours with the published series, so no "
                        "spread comparison here would be a measurement of a year"
                        .format(MIN_SHARED_HALF_HOURS))}

    overstatement = [
        y["reconstructed_spread"] / y["published_spread"]
        for y in counting if y.get("published_spread")
    ]
    # THE SECOND FACTOR IS THE ONE THE PAGE MAY QUOTE, and it exists because the first one was
    # being quoted against a statistic it is not (2026-08-25, Expert Hour finding). The customer
    # panel prints a p95/p5 spread -- "the dirtiest 5% of half hours ran 5.1x the cleanest 5%" --
    # and then said it measured `spread_overstated_by` "wider than" NESO's. That factor is the
    # mean of six max/min ratios: two single half hours out of seventeen thousand, on both sides,
    # which `year_stats`' own docstring already refuses to rest a claim on. Comparing the two put
    # a tail statistic and a robust statistic under one word.
    #
    # BOTH ARE PUBLISHED, NOT ONE SWAPPED FOR THE OTHER. max/min is still the honest answer to
    # "how much wider is this model's whole range", and dropping it to make the page tidier would
    # be choosing the flattering statistic after seeing both -- the thing R12 exists to stop.
    p95_overstatement = [
        y["reconstructed_p95_over_p5"] / y["published_p95_over_p5"]
        for y in counting if y.get("published_p95_over_p5")
    ]
    return {
        "available": True,
        "source": neso.PUBLISHED_BASIS,
        # TRUE when the shape compared IS the published series on every shared half hour, which
        # is what the feed publishes since 2026-10-05. Then every ratio below is 1.0 and the
        # correlation 1.0 BY CONSTRUCTION. That is the control that the feed carries NESO's values
        # and not a model's; it is not evidence of a model agreeing with NESO.
        "by_construction": all(
            row["mean_abs_error"] is not None and row["mean_abs_error"] < 1e-9
            for row in years.values()
        ),
        # TRUE when the shape compared is itself a NESO series (`shape_is_neso`, handed in by
        # `build` from the records' own source tags), so this is two NESO series side by side and
        # not a model measured against NESO. A page must not call either one "the company's model".
        "shape_is_neso": shape_is_neso,
        "compared_with": "NESO Carbon Intensity API",
        "by_year": years,
        "spread_overstated_by": round(sum(overstatement) / len(overstatement), 2),
        "p95_spread_overstated_by": (
            round(sum(p95_overstatement) / len(p95_overstatement), 2) if p95_overstatement else None
        ),
        "headline_years": sorted(y for y, r in years.items() if r["counts_toward_headline"]),
        "excluded_years": {
            y: "shares only {} half hour(s) with the published series".format(int(r["half_hours"]))
            for y, r in years.items() if not r["counts_toward_headline"]
        },
        "what_it_means": (
            "Since 2026-10-05 this feed's shape is NESO's Historic GB Generation Mix and this "
            "compares it with NESO's Carbon Intensity API (`shape_is_neso`): two NESO series, "
            "not a model against NESO. Their LEVELS differ (the API carried a loss uplift until "
            "2020-04-27, `history.api_step`), and each side is normalised by its own year mean, "
            "so what is left here is the difference in SHAPE. "
            "Both series re-normalised over the half hours they share, so this is a difference "
            "in the physics and not in the coverage. `spread_overstated_by` compares max/min on "
            "both sides -- the whole range, two half hours wide. `p95_spread_overstated_by` "
            "compares the dirtiest-5%-over-cleanest-5% spread on both sides, which is the "
            "statistic the customer page prints and therefore the only one a sentence about that "
            "page's figure may use. Neither is a correction to apply to a HOUSEHOLD: how wrong "
            "this shape is for one home depends on when that home drew, and that is measured per "
            "household in the paired `published` value on each record."
        ),
    }


def published_forecast_skill(shape: dict, parsed: dict | None, why_unavailable: str = "") -> dict:
    """The CEILING every timing claim on this feed sits under, and it is not about this model.

    `versus_published` says how wrong the RECONSTRUCTION is. This says how wrong the FORECAST a
    household would actually have acted on was -- NESO's own day-ahead number graded against
    NESO's own outturn, both published by the counterparty, neither of them ours. The two
    compound, and only one of them can ever be built away: a perfect grid model, a perfect
    household model and perfect execution still cannot beat the forecast that existed at the
    time.

    WHY IT BELONGS IN THE FEED RATHER THAN IN A DOCSTRING. The page quotes a within-day spread
    and turns it into a saving. That arithmetic silently assumes the customer knew which half
    hours were the clean ones. Measured over 2019-2024, following the published forecast
    captures about 86% of the achievable within-day saving on the mean day and about 55% on the
    worst day in twenty -- so the honest reading of any shifting figure here is (this model's
    overstatement) x (what the forecast could actually pick). A ceiling that lives in a module
    nobody opens is not carried by the number when the number is quoted.

    UNAVAILABLE IS SAID, NEVER OMITTED, for the same reason `versus_published` says it: a
    missing ceiling reads as no ceiling.
    """
    if parsed is None:
        return {"available": False,
                "why": why_unavailable or "the published series was not parsed this run"}
    try:
        from sim import neso_carbon_intensity as neso
    except Exception as exc:  # noqa: BLE001 -- an absent ceiling is reported, never fatal
        return {"available": False, "why": "{}: {}".format(type(exc).__name__, exc)}

    years: dict[str, dict] = {}
    sensitivity: dict[str, list[float]] = {}
    for year in sorted({k[0][:4] for k in shape}):
        try:
            measured = neso.forecast_skill(parsed, year)
        except Exception:  # noqa: BLE001 -- a year the forecast does not cover is simply absent
            continue
        years[year] = {
            k: (round(v, 4) if isinstance(v, float) else v) for k, v in measured.items()
        }
        for window, value in neso.window_sensitivity(parsed, year).items():
            sensitivity.setdefault(window, []).append(value)
    if not years:
        return {"available": False,
                "why": ("no year in this shape has enough published forecast/outturn days to "
                        "make a distribution")}

    captures = [row["capture_mean"] for row in years.values()]
    return {
        "available": True,
        "source": neso.PUBLISHED_BASIS,
        "by_year": years,
        "shift_window_half_hours": neso.DEFAULT_SHIFT_WINDOW_HALF_HOURS,
        "capture_mean_across_years": round(sum(captures) / len(captures), 4),
        "capture_worst_year": min(years, key=lambda y: years[y]["capture_mean"]),
        # THE DIAL, PUBLISHED. The window length is a choice about how long a household runs an
        # appliance, and any choice inside a headline is somewhere the headline can be improved
        # without the world changing. The sweep is here so that cannot be done quietly.
        "window_sensitivity_capture_mean": {
            window: round(sum(values) / len(values), 4)
            for window, values in sorted(sensitivity.items(), key=lambda kv: int(kv[0]))
        },
        "what_it_means": (
            "NESO's published FORECAST graded against NESO's published OUTTURN -- the "
            "counterparty's own belief-vs-truth gap, computed from the same key-free API any "
            "supplier can read, and nothing to do with this project's reconstruction. "
            "`capture_mean` is the fraction of a day's ACHIEVABLE within-day saving that "
            "picking the cleanest window BY FORECAST actually delivered, scored on outturn, "
            "where 1.0 is as well as hindsight could have done. Reported as a distribution and "
            "never as a mean alone, because the calm days that need no advice would otherwise "
            "average away the volatile ones the advice exists for. It is a CEILING: every "
            "timing figure on this feed should be read as this model's overstatement times "
            "what the forecast could actually pick, and the second factor cannot be built away."
        ),
    }


def _history_block(meta: dict) -> dict:
    """The cross-checks and the source counts, copied from `grid_carbon_history`.

    Rounded for publishing. Every figure here is computed in `sim/grid_carbon_history.py` and only
    copied, so a sentence quoting it can be held to it.
    """
    def stats(table: dict) -> dict:
        return {
            year: {
                "half_hours": int(row["n"]),
                "correlation": round(float(row["correlation"]), 4),
                "mean_bias_g_co2_per_kwh": round(float(row["mean_bias"]), 2),
                "rmse_g_co2_per_kwh": round(float(row["rmse"]), 2),
            }
            for year, row in table.items()
        }

    step = meta["api_step"]
    return {
        "module": "sim/grid_carbon_history.py",
        "sources": {
            "neso_historic_mix": "NESO Historic GB Generation Mix `CARBON_INTENSITY`, 2016-2025",
            "fuelmix_fill": "where the historic mix has no usable value: NESO's arithmetic on "
                            "Elexon FUELHH, unscaled",
        },
        "historic_mix_edition": meta["historic_mix_edition"],
        "fill_versus_historic_mix": stats(meta["arithmetic_versus_historic_mix"]),
        "api_versus_historic_mix": stats(meta["api_versus_historic_mix"]),
        "api_step": {
            "first_half_hour_after": step["first_half_hour_after"],
            "ratio_before": round(float(step["before"]["ratio"]), 4),
            "ratio_after": round(float(step["after"]["ratio"]), 4),
            "half_hours_before": step["before"]["n"],
            "half_hours_after": step["after"]["n"],
        },
        "half_hours_by_source_and_year": meta.get("coverage_by_year"),
        "what_it_means": (
            "`fill_versus_historic_mix` is the fuel-mix arithmetic against the historic mix, by "
            "year (bias = arithmetic - historic mix): the error a `fuelmix_fill` value carries. "
            "`api_versus_historic_mix` is NESO's Carbon Intensity API against it (bias = API - "
            "historic mix), and `api_step` is the API's own basis change: API / historic mix "
            "summed either side of 2020-04-27 period 34."
        ),
    }


def build(shape: dict, demand: dict, *, window_days: int = RECORD_WINDOW_DAYS,
          extra_dates: set[str] | None = None,
          sources: dict | None = None,
          history: dict | None = None,
          levels: dict | None = None) -> dict:
    if not shape:
        raise ShapeUnavailable("no shape to publish")
    last_date = max(key[0] for key in shape)
    first_kept = (datetime.fromisoformat(last_date) - timedelta(days=window_days)).date().isoformat()
    wanted = set(extra_dates or ())
    sources = sources or {}

    # THE API TRAVELS WITH THE RECORDS as `published`: NESO's other series, beside the historic
    # mix the shape is built from. `null` where the API published nothing -- an absence, never a
    # substituted 1.0.
    published, published_why, published_parsed = published_series(demand)
    records = [
        {
            "date": date_str,
            "period": period,
            "shape": round(value, 5),
            "source": sources.get((date_str, period)),
            "published": (
                None if published is None or (date_str, period) not in published
                else round(published[(date_str, period)], 5)
            ),
        }
        for (date_str, period), value in sorted(shape.items())
        if date_str >= first_kept or date_str in wanted
    ]
    by_year = summarise(shape, demand)
    source_by_year: dict[str, dict[str, int]] = {}
    for (date_str, _period), tag in sources.items():
        if (date_str, _period) in shape:
            row = source_by_year.setdefault(date_str[:4], {})
            row[str(tag)] = row.get(str(tag), 0) + 1
    return {
        "published_at": datetime.now(timezone.utc).isoformat(),
        "basis": HISTORY_BASIS,
        "how_to_use": (
            "Multiply `shape` by `annual_level.by_year[<the record's calendar year>]."
            "mean_g_co2_per_kwh` to get the published gCO2/kWh for that half hour. The annual "
            "level is published here, beside the shape it was normalised with; the company "
            "reads it in exactly one place, company/regulatory/carbon_emissions.py, and a year "
            "with `complete: false` is a mean of the dates it covers, never the year's."
        ),
        "annual_level": {
            "unit": "gCO2/kWh",
            "basis": ANNUAL_LEVEL_BASIS,
            "weighting": ANNUAL_LEVEL_WEIGHTING,
            "by_year": levels or {},
        },
        "error_direction": ERROR_DIRECTION,
        "named_gaps": NAMED_GAPS,
        "source": (
            "NESO Data Portal, Historic GB Generation Mix (df_fuel_ckan.csv), national "
            "half-hourly CARBON_INTENSITY. In its empty or outage half hours: Elexon Insights "
            "generation by fuel type (FUELHH) and NESO's embedded wind and solar estimate "
            "(Historic Demand Data), combined at NESO's published factors (Carbon Intensity "
            "Forecast Methodology, Table 1). Cross-checked against NESO's Carbon Intensity API "
            "(api.carbonintensity.org.uk), from 2018-05-11. Normalised with Elexon's demand "
            "outturn (INDO). Built by sim/grid_carbon_history.py."
        ),
        "source_by_year": dict(sorted(source_by_year.items())),
        "history": history,
        "records_window_days": window_days,
        "records_cover": {
            "from": min((r["date"] for r in records), default=first_kept),
            "to": last_date,
            "trailing_window_from": first_kept,
            "extra_days_carried_for_meter_reads": sorted(
                d for d in wanted if d < first_kept and any(r["date"] == d for r in records)
            ),
        },
        "series_covers": {
            "from": min(key[0] for key in shape),
            "to": last_date,
            "half_hours": len(shape),
        },
        "by_year": by_year,
        "versus_published": versus_published(
            shape, demand, published, published_why,
            shape_is_neso=bool(sources) and all(
                sources.get(k) in NESO_SHAPE_SOURCES for k in shape)),
        "published_forecast_skill": published_forecast_skill(shape, published_parsed, published_why),
        "typical_day": typical_day(shape),
        "records": records,
    }


#: THE BIOMASS ENVELOPE IS MEASURED, PUBLISHED, AND DELIBERATELY NOT DISPATCHED, and this flag
#: exists so that decision is a stated one rather than a forgotten keyword. Everything the
#: dispatch needs is built and R15-proven in `sim/grid_carbon_intensity.py`; what stopped it was
#: the measurement, which said the correction makes the published series WORSE and said why.
#:
#: MEASURED 2026-08-26 over 2019-2024, one process, identical caches, the envelope as the only
#: variable. Correlation moved 0.8453 -> 0.8466 (up in four years of six) and EVERYTHING ELSE
#: went backwards: mean absolute error 0.1617 -> 0.1679, within-day overstatement 1.4496 ->
#: 1.5047, p95/p5 5.32 -> 6.33, and 2024's max/min spread 24.5 -> 83.3.
#:
#: THE MECHANISM, and it is the part worth keeping rather than the verdict. The model was
#: designed as a fleet RAMPING with the residual, and against the published outturn it is not
#: one: the residual sits ABOVE the demonstrated capacity in 96.4% of 2019's half hours and
#: 83.6% of 2024's, so what the change actually did in almost every half hour was raise a flat
#: 2,400 MW block to a flat ~3,300 MW one -- and in the remaining tenth it dropped the fleet to
#: the demonstrated minimum of 73 MW. That cliff lands exactly on the quiet half hours the clean
#: end is measured over, which is the whole of the spread blow-up.
#:
#: AND THE PREMISE ITSELF IS REFUTED, which is why the answer is not a different statistic.
#: Correlation between the residual and the published biomass outturn runs 0.16-0.58 across
#: 2018-2025 -- 2.6% to 33.5% of the fleet's variance. Biomass under a CfD is paid a strike
#: price on metered output, so it runs when it is AVAILABLE and its low readings are outages,
#: not price responses. Availability is not derivable from the residual, so closing this needs an
#: outage model and not a tidier percentile.
#:
#: WHY THE RAW MINIMUM WAS NOT SWAPPED FOR `p1_mw` WHEN THE RESULT CAME BACK BAD. It would have
#: scored better -- 2024's p1 is 550 MW against a 73 MW minimum, which lifts the clean end and
#: narrows the swing. That is choosing a statistic because of what it does to this model's grade,
#: which is exactly what R12 and R13 forbid, and it would have hidden the refuted premise behind
#: a better number. `thermal_floor_by_year` takes the raw minimum for the opposite reason and the
#: asymmetry is worth naming: for gas, a lower floor errs BACK toward the known-wrong baseline;
#: for biomass -- the only carbon-carrying term in the must-run block -- a lower floor errs PAST
#: it, into a cleaner clean end. Same doctrine, opposite fuel, opposite direction.
BIOMASS_DISPATCH_WIRED = False


def biomass_flat_at_year_mean(
    envelope_by_year: dict[int, dict[str, float]],
) -> dict[int, dict[str, float]]:
    """The flat biomass block, held at each year's MEASURED mean instead of 2,400 MW (EP13 s27).

    Both ends of the envelope are set to `mean_mw`, which `emissions_rate_t_per_mwh` collapses
    to a constant: the block is still flat, so this decides nothing about WHEN biomass ran and
    the dispatch question `BIOMASS_DISPATCH_WIRED` refuses stays refused. The mean is the one
    value of a flat block that carries the year's measured biomass energy, so it is chosen on
    definition (coal's grain: one scalar a year), not on fit. Before 2026-10-02 the docstring of
    `build_shape` warned `mean_mw` off as the number a goal-seeker would reach for; that warning
    was about using it as an envelope END, where it fits better than either honest end. A year
    with no envelope (2016) is absent here and keeps the flat 2,400 MW. 2017's mean is from
    2,887 half hours, the end of that year only, and is published beside the feed as such.
    """
    return {
        year: {"capacity_mw": float(row["mean_mw"]), "floor_mw": float(row["mean_mw"])}
        for year, row in envelope_by_year.items()
    }


def fuel_mix() -> tuple[
    dict[tuple[str, int], tuple[float, float]],  # imports: {(date, period): (MW, t/MWh)}
    dict[int, float],                            # coal capacity: {year: demonstrated max MW}
    dict[str, float],                            # import coverage: the priced fraction, measured
    dict[int, dict[str, float]],                 # thermal floor: {year: {floor_mw, p1_mw, ...}}
    dict[tuple[str, int], float],                # must-run: {(date, period): NUCLEAR+NPSHYD MW}
    dict[str, float],                            # must-run coverage: measured vs flat fallback
    dict[int, dict[str, float]],                 # biomass envelope: {year: {floor_mw, p99_mw...}}
]:
    """SEVEN members, in the order all eight callers unpack them: imports by half hour, coal
    capacity by year, the measured import coverage, the thermal floor by year, the zero-carbon
    must-run by half hour, that block's coverage, and the biomass envelope by year.

    THE ONE PLACE THE NEW INPUTS CANNOT BE FORGOTTEN, and that is its job. `build_shape` takes
    them all as optional keywords whose defaults reproduce the shape exactly as it was before
    coal, cables and the thermal floor were modelled -- a fail-open signature by construction. So
    the control is here: an absent or unusable mix RAISES out of `reconstruction_shape()` and the
    EP13 instruments, rather than returning a series that quietly lost three corrections. SINCE
    2026-10-05 THIS IS NOT ON THE PUBLISHING PATH: the feed is built from
    `sim/grid_carbon_history.py`, and this tuple reaches only EP13's reconstruction.

    THE FLOOR IS UNPACKED TO `{year: floor_mw}` HERE, so the `p1_mw` published beside it stays a
    diagnostic and has no path into the dispatch. The biomass envelope is unpacked the same way
    one layer down, in `build_shape`, and for a stronger version of the same reason: its
    `mean_mw` would fit the published series better than either honest end.

    THIS SIGNATURE IS A BATTERY ANCHOR, so it is not free to drift.
    `tools/grid_intensity_feed_contract_battery.py` holds this `def` block verbatim as its
    reachability floor and its null-round insertion point. Change the signature without changing
    it there, in the same commit, and the next run prints TARGET NOT UNIQUE -- which is
    reachability UNKNOWN for every row, not a pass. Changing it there moves the spec fingerprint,
    which is deliberate: it is what stops a stale results file being read against a spec that
    never scored it, and it means the battery has to be re-run.
    """
    from sim import elexon_fuel_outturn as fuel

    series = fuel.to_settlement_periods(fuel.load_cached())
    floors = fuel.thermal_floor_by_year(fuel.thermal_by_period(fuel.load_cached_thermal()))
    must_run_rows = fuel.load_cached_zero_carbon_must_run()
    biomass = fuel.biomass_envelope_by_year(fuel.biomass_by_period(fuel.load_cached_biomass()))
    return (
        fuel.imports_by_period(series),
        fuel.coal_capacity_by_year(series),
        fuel.import_coverage(series),
        floors,
        fuel.zero_carbon_must_run_by_period(must_run_rows),
        fuel.zero_carbon_must_run_coverage(must_run_rows),
        biomass,
    )


def exports_by_period() -> dict[tuple[str, int], float]:
    """GB's interconnector exports by half hour, from the same FUELHH cache `fuel_mix` reads.

    Kept OUT of `fuel_mix()` because that signature is a battery anchor (see its docstring).
    """
    from sim import elexon_fuel_outturn as fuel

    return fuel.exports_by_period(fuel.load_cached())


def unmixed_imports_by_period() -> dict[tuple[str, int], float]:
    """Imports on the cables NESO's mix leaves out (Viking, ElecLink), from the FUELHH cache.

    Served by the dispatch, kept out of the tonnes and the denominator (EP13 frame doc s34).
    Kept OUT of `fuel_mix()` because that signature is a battery anchor.
    """
    from sim import elexon_fuel_outturn as fuel

    return fuel.unmixed_imports_by_period(fuel.to_settlement_periods(fuel.load_cached()))


def transmission_wind_by_period(agws: list[dict]) -> dict[tuple[str, int], float]:
    """The wind the residual subtracts: FUELHH `WIND` where metered, AGWS wind where it is not.

    INDO is transmission demand, so the wind serving it is transmission-METERED wind. AGWS offshore
    reads 0.52-0.70 of DESNZ's offshore generation in every year 2016-2024 (EP13 frame doc s21), so
    it under-subtracts wind and over-burns gas. The AGWS fallback keeps a half hour with no FUELHH
    reading in the shape rather than dropping it.
    """
    from sim import elexon_fuel_outturn as fuel

    wind = aggregate_wind_generation(agws)
    wind.update(fuel.wind_by_period(fuel.load_cached_remainder()))
    return wind


def embedded_generation_by_period(agws: list[dict]) -> dict[tuple[str, int], float]:
    """The zero-carbon supply under the INDO metering point: AGWS solar plus NESO's embedded wind.

    INDO is net of both, so neither leaves the residual; both join the denominator (EP13 frame
    doc s19 for solar, s26 for wind). A half hour NESO does not cover is left OUT of the map,
    which `build_shape` reads as skip, not as zero embedded wind.
    """
    from sim import neso_embedded_generation as embedded

    series = embedded.to_settlement_periods(embedded.load_cached())
    out: dict[tuple[str, int], float] = {}
    for key, solar_mw in aggregate_solar_generation(agws).items():
        reading = series.get(key)
        if reading is not None:
            out[key] = solar_mw + float(reading["wind_mw"])
    return out


def pumped_storage_by_year() -> dict[int, dict[str, float]]:
    """Pumped storage at coal's grain, four scalars a year, from the remainder cache.

    The fleet is dispatched by the model (`grid_carbon_intensity.pumped_storage_schedule`);
    only these annual figures cross, because PS fails condition 2 (EP13 frame doc s25).
    Kept OUT of `fuel_mix()` because that signature is a battery anchor.
    """
    from sim import elexon_fuel_outturn as fuel

    return fuel.pumped_storage_by_year(fuel.load_cached_remainder())


def reconstruction_shape() -> dict:
    """EP13's dispatch reconstruction, wired exactly as this feed published it until 2026-10-05.

    NOT PUBLISHED. The feed's source is `sim/grid_carbon_history.py` since the director's ruling
    that history is the published series. This is kept so EP13's model can still be built in one
    call and graded against NESO, and so the wiring of its corrections stays under test.
    """
    demand = aggregate_demand(json.loads(DEMAND_CACHE.read_text(encoding="utf-8")))
    # WIND IN THE RESIDUAL, SOLAR IN THE DENOMINATOR: INDO is already net of embedded solar,
    # so subtracting it again hid its gas (EP13 frame doc s18-s19). EXPORTS INTO BOTH: INDO
    # excludes them, yet GB generated them (s20). The wind is TRANSMISSION-METERED (s21).
    # PUMPED STORAGE is dispatched by the model from four annual scalars (s25). EMBEDDED WIND
    # joins solar in the denominator, on NESO's definition (s26).
    # BIOMASS stays a flat block, at the year's measured mean rather than 2,400 MW (s27).
    # VIKING AND ELECLINK are served but left out of the mix, as NESO's series does (s34).
    agws = json.loads(AGWS_CACHE.read_text(encoding="utf-8"))
    renewables = transmission_wind_by_period(agws)
    (imports, coal_capacity, _coverage, thermal_floors, must_run, _must_run_coverage,
     biomass_envelope) = fuel_mix()
    return build_shape(
        demand,
        renewables,
        imports_by_period=imports,
        coal_capacity_by_year=coal_capacity,
        thermal_floor_by_year={y: r["floor_mw"] for y, r in thermal_floors.items()},
        zero_carbon_must_run_by_period=must_run,
        biomass_envelope_by_year=(
            biomass_envelope if BIOMASS_DISPATCH_WIRED else biomass_flat_at_year_mean(biomass_envelope)
        ),
        embedded_generation_by_period=embedded_generation_by_period(agws),
        exports_by_period=exports_by_period(),
        pumped_storage_by_year=pumped_storage_by_year(),
        unmixed_imports_by_period=unmixed_imports_by_period(),
    )


def history_shape(demand: dict) -> tuple[dict, dict, dict]:
    """(shape, {key: source tag}, grid_carbon_history's meta) -- what the feed publishes.

    The grams are normalised with NESO's own `published_shape`, which is the normalisation the
    published side of every comparison here already uses, so the two cannot drift apart. A half
    hour with no value (`gap`) or no demand weight is absent, never 1.0. An unusable history
    RAISES out of `generate()`, so the feed is not rewritten from nothing.
    """
    from sim import grid_carbon_history as history
    from sim import neso_carbon_intensity as neso

    series, meta = history.load_series()
    grams = {key: r.value for key, r in series.items() if r.value is not None}
    shape = neso.published_shape(grams, demand)
    return shape, {key: series[key].source for key in shape}, meta


def history_readings() -> dict:
    """{key: (gCO2/kWh, source tag)} for every half hour the published history has a value for."""
    from sim import grid_carbon_history as history

    series, _meta = history.load_series()
    return {key: (r.value, r.source) for key, r in series.items() if r.value is not None}


def generate(out_path: Path | None = None) -> dict:
    demand = aggregate_demand(json.loads(DEMAND_CACHE.read_text(encoding="utf-8")))
    shape, sources, meta = history_shape(demand)
    data = build(shape, demand, extra_dates=dates_with_reads(), sources=sources,
                 history=_history_block(meta), levels=annual_level(history_readings(), demand))
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    d = generate()
    print("wrote {} ({} record(s) over {}..{}; {} year(s) summarised from {} half hours)".format(
        OUT_PATH, len(d["records"]), d["records_cover"]["from"], d["records_cover"]["to"],
        len(d["by_year"]), d["series_covers"]["half_hours"]))
