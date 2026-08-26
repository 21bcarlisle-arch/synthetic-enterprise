#!/usr/bin/env python3
"""Publish the half-hourly grid-intensity SHAPE as a market-data feed the company can read.

REUSE: tools/generate_grid_intensity_feed.py
CLASS: CUSTOM
INDEX: searched "feed", "market_data", "publish", "generate", "intensity", "carbon". The
       publishing PATTERN is reused wholesale rather than invented -- `docs/market_data/
       price_feed.json` and `consumption_feed.json` are already how a world quantity reaches
       the company layer, both `{published_at, records}`, both written by a producer on the
       world side and read by name on the company side. This is the third feed of that shape
       and it deliberately looks identical. The SHAPE itself comes from
       `sim/grid_carbon_intensity.py`; nothing is recomputed here.

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

from sim.generation_demand_history import aggregate_renewable_generation
from sim.grid_carbon_intensity import (
    SHAPE_BASIS,
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

#: Named on the face of the feed, because a consumer that does not know these cannot state them
#: and the advisor's scope brief makes stating them the condition of publishing at all
#: ("a carbon figure without its basis is not a measurement, it is a slogan").
NAMED_GAPS = [
    "the thermal stack is floored at the CCGT+OCGT fleet's demonstrated annual MINIMUM output, so "
    "no half hour is dispatched with no gas running -- but that floor is the year's single lowest "
    "reading (303 MW in 2024, against a 1st percentile of 1,720 MW), deliberately the most "
    "conservative number available, so quiet half hours still run less gas than GB actually ran",
    "the shape still knows how clean a quiet half hour is far better than it knows WHICH half "
    "hours were the quiet ones: correlation against the published series is 0.75 in 2024 and "
    "falls year by year (0.88 in 2019). Measuring the fleet GB actually ran, rather than "
    "assuming a flat one, is the first correction that moved this axis at all -- it improved "
    "correlation in all six measured years, where the thermal floor moved it by less than 0.004 "
    "in every one -- but 0.75 is still an instrument that would point a customer at some of the "
    "wrong half hours",
    "interconnector imports are counted at NESO's own published per-cable factors, but two of "
    "GB's nine cables postdate that table -- North Sea Link (Norway) and Viking Link (Denmark) -- "
    "so their flow is still dispatched as GB gas and reads dirtier than it was; that is 34% of "
    "imported MWh in 2024 and it is growing",
    "coal is dispatched from the fleet's demonstrated annual maximum, but its place in merit is "
    "fixed above the CCGT band rather than recomputed from the gas/coal spread, so the 2021-22 "
    "gas spike understates coal",
    "the must-run block is no longer a constant 8 GW -- nuclear and run-of-river hydro now come "
    "from Elexon's published half-hourly outturn (99.97% of half hours; 544 MW to 9,831 MW "
    "against the 5,600 MW this model used to assume) -- but the BIOMASS half of that block is "
    "still a flat 2,400 MW. Biomass carries 120 gCO2/kWh on NESO's own table, so its metered "
    "output is an emissions term and may not cross the wall; it is modelled, it is wrong (2024's "
    "outturn averages nearer 2.7 GW and swings 1.0-3.0 GW), and it is the next thing to build",
    "national only -- no regional series is offered, modelled or otherwise",
    "outturn, never forecast: this grades what happened and must not judge shifting advice",
    "no loss correction is applied here and none must be applied downstream either",
]

#: The one a reader should take away. The CONCLUSION is measured; the REASON is not a tidy story.
#:
#: THE REASON WAS WRONG AND CONTRADICTED THE LIST TWENTY LINES ABOVE IT (2026-08-25, Expert Hour
#: finding). This sentence used to say "no coal and no interconnector imports BOTH make quiet half
#: hours look cleaner". `NAMED_GAPS` says the opposite on both limbs, in the same module, in the
#: same feed: coal omission is a DIRTY-end error ("coal-heavy years read cleaner than GB was at
#: the dirty end"), and the import omission makes half hours read DIRTIER, not cleaner -- GB is a
#: net importer of French nuclear and Norwegian hydro, and NESO's consumption basis counts them at
#: the exporting country's intensity. So the two gaps push in OPPOSITE directions and only their
#: NET effect is knowable, which is precisely why it has to be measured rather than argued.
#:
#: It is measured, and the conclusion survives its broken reasoning: over the years both series
#: cover this shape's clean end sits near 0.06 of average against NESO's 0.19. The clean end IS
#: optimistic. What could not be asserted from the gap list -- and was -- is WHY.
#:
#: MEASURED, NOT RECALLED, AND THE DIFFERENCE COST SOMETHING (2026-08-25). This sentence used
#: to continue "measured over 2016-2025 this shape's quietest half hours sit around 0.05 of
#: average against NESO's published series bottoming out nearer 0.16". That comparison had
#: never been run: no NESO series existed in this tree and no fetch had ever happened. It was
#: a recollection written in the grammar of a measurement, in the one sentence whose job is to
#: say which way the errors point, and it was repeated as evidence in a level certification.
#: `sim/neso_carbon_intensity.py` now fetches the published series and measures it. The
#: qualitative claim survived; the SIZE did not, and the headline had never been stated at all.
#: STILL OPTIMISTIC AFTER THE TWO LARGEST GAPS WERE CLOSED (2026-08-25). Coal is now dispatched
#: and interconnector imports are now carried, and the clean end moved from 3.2x too clean to
#: 2.3x — a real improvement that does not change the sentence's direction, which is the point
#: worth publishing. The remaining cause is named and sized in `NAMED_GAPS`: this model still
#: lets the thermal stack reach exactly zero, in 16.1% of 2024's half hours.
ERROR_DIRECTION = (
    "The RANGE is overstated, and that is the sentence to carry: this shape's p95/p5 spread runs "
    "about 1.38x the published series', so any benefit computed from moving load between quiet "
    "and busy half hours is an UPPER BOUND on the real one. THAT 1.38x IS A BLEND OF TWO AXES "
    "THAT BEHAVE OPPOSITELY, and the one a household can act on is the worse of them: split "
    "day-by-day, this shape's BETWEEN-day swing matches the published series to "
    "within 8% in every year 2019-2024 (0.92-1.00x, mean 0.97), while its WITHIN-day swing is "
    "too large in every one of those years (1.35-1.54x, mean 1.45). A customer can move the "
    "washing from 6pm to 2am; they cannot move it to a windier Tuesday in March -- so the whole "
    "of this model's exaggeration sits on the only axis a time-shifting recommendation acts on, "
    "and the annual figure UNDERSTATES the correction such a claim needs by about a tenth. "
    "MEASURING THE MUST-RUN FLEET (2026-08-26) IMPROVED THAT AXIS AND WORSENED THE HEADLINE, "
    "and both halves are published because reporting only the first is how a correction becomes "
    "a claim: within-day overstatement fell from 1.48x to 1.45x (and from 1.44x to 1.35x in "
    "2024), max/min overstatement fell from 1.04x to 1.01x, correlation and mean absolute error "
    "improved in ALL SIX measured years -- while p95/p5 overstatement rose from 1.36x to 1.38x, "
    "worse in four years of six. p95/p5 and max/min are two statistics under one word 'spread' "
    "and they moved in opposite directions here, so neither is quoted alone. What "
    "is no longer true, and was "
    "until the thermal floor was measured on 2026-08-25, is that the clean END is uniformly "
    "optimistic: flooring the stack at the gas fleet's demonstrated annual minimum moved the "
    "quietest half hours from about 3.2x too clean to a MIXED picture -- still slightly cleaner "
    "than published in 2019, 2022 and 2023, and now DIRTIER than published in 2020 and 2021. "
    "That is MEASURED, year by year, in `versus_published` below and never inferred from the gap "
    "list, which is the same reason the gaps are not all pushing one way: an import's sign "
    "depends on what it displaced -- against the mid-merit gas band a Dutch import is dirtier "
    "than what it replaced, against a peaker it is cleaner -- so only the net is knowable. "
    "AND THERE IS A SECOND FACTOR ON THE SAME SIDE THAT IS NOT ABOUT THIS MODEL AT ALL, "
    "measured 2026-08-26 and carried in `published_forecast_skill` below. Every figure here is "
    "computed with hindsight; a household has to act on a FORECAST. Graded against NESO's own "
    "outturn, NESO's own published forecast picks a three-hour window that delivers about 86% "
    "of that day's achievable within-day saving on the mean day, about 55% on the worst day in "
    "twenty, and on a handful of days a window DIRTIER than simply not shifting. That ceiling "
    "cannot be built away by improving this model, so the honest reading of any timing benefit "
    "on this feed is this model's overstatement TIMES what a forecast could actually pick."
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
        from sim import neso_carbon_intensity as neso

        parsed = neso.to_settlement_periods(neso.load_cached())
        return neso.published_shape(neso.actual_by_period(parsed), demand), "", parsed
    except Exception as exc:  # noqa: BLE001 -- an absent comparison is reported, never fatal
        return None, "{}: {}".format(type(exc).__name__, exc), None


def versus_published(shape: dict, demand: dict, published: dict | None = None,
                     why_unavailable: str = "") -> dict:
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


def build(shape: dict, demand: dict, *, window_days: int = RECORD_WINDOW_DAYS,
          extra_dates: set[str] | None = None,
          import_coverage: dict | None = None,
          coal_capacity_by_year: dict | None = None,
          thermal_floor_by_year: dict | None = None,
          zero_carbon_must_run_coverage: dict | None = None,
          biomass_envelope_by_year: dict | None = None) -> dict:
    if not shape:
        raise ShapeUnavailable("no shape to publish")
    last_date = max(key[0] for key in shape)
    first_kept = (datetime.fromisoformat(last_date) - timedelta(days=window_days)).date().isoformat()
    wanted = set(extra_dates or ())

    # THE PUBLISHED SERIES TRAVELS WITH THE RECORDS, not only as a year-level summary. A reader
    # given "this model overstates the range by 3.2x" can only apply it as a hand-wave to a
    # particular household's day; the two values side by side in the same half hour let the same
    # arithmetic be done twice and the ANSWERS compared, which is the coupled-triad rung: the
    # company's belief, the world's published truth, and the gap between them for THIS meter.
    # `null` where NESO published nothing -- an absence, never a substituted 1.0, which would be
    # the flat method smuggled in and would always pull the gap toward zero.
    published, published_why, published_parsed = published_series(demand)
    records = [
        {
            "date": date_str,
            "period": period,
            "shape": round(value, 5),
            "published": (
                None if published is None or (date_str, period) not in published
                else round(published[(date_str, period)], 5)
            ),
        }
        for (date_str, period), value in sorted(shape.items())
        if date_str >= first_kept or date_str in wanted
    ]
    by_year = summarise(shape, demand)
    return {
        "published_at": datetime.now(timezone.utc).isoformat(),
        "basis": SHAPE_BASIS,
        "how_to_use": (
            "Multiply by YOUR OWN published annual grid intensity for the record's calendar "
            "year. This series is deliberately dimensionless and there is no absolute "
            "grid-intensity figure in it: this repository has exactly one annual series and "
            "company/regulatory/carbon_emissions.py owns it."
        ),
        "error_direction": ERROR_DIRECTION,
        "named_gaps": NAMED_GAPS,
        "source": (
            "Elexon Insights half-hourly demand outturn (INDO), wind+solar generation outturn "
            "(AGWS) and generation-by-fuel-type outturn (FUELHH, for coal availability and "
            "interconnector flow), through the dispatch stack in "
            "sim/merit_order_reconstruction.py (DUKES 5.10.C efficiencies, DUKES 5.14 coal "
            "emission factors, DESNZ GHG conversion factors). Import carbon intensities are "
            "NESO's own published figures (Carbon Intensity Forecast Methodology, Table 1)."
        ),
        # WHAT THE MODELLED SLICE OF IMPORTS ACTUALLY IS, as a measured fraction of imported
        # MWh rather than as an adjective. Two of GB's nine cables -- North Sea Link and Viking
        # Link -- postdate NESO's published factor table, so their flow is left modelled as GB
        # generation and this number says how much of the answer that is. A gap quoted in per
        # cent can be argued with; "some imports are not covered" cannot.
        "import_coverage": (
            None if import_coverage is None else {
                "covered_fraction": round(float(import_coverage["covered_fraction"]), 4),
                "uncovered_cables": ["INTNSL (Norway)", "INTVKL (Denmark)"],
                "what_it_means": (
                    "The share of GB's imported MWh, over the whole series, whose carbon "
                    "intensity NESO publishes a factor for. The remainder is dispatched as GB "
                    "generation exactly as it was before imports were modelled at all, which "
                    "reads DIRTIER than it was for a Norwegian hydro import."
                ),
            }
        ),
        # A CAPACITY THAT MEASURES ITSELF TO ZERO. Published so a reader can see the coal fleet
        # close in the data rather than trust that a hand-written end date was right.
        "coal_demonstrated_max_mw": (
            None if coal_capacity_by_year is None
            else {str(y): round(float(mw)) for y, mw in sorted(coal_capacity_by_year.items())}
        ),
        # WHAT THE FLEET WAS NEVER OBSERVED BELOW, and the diagnostic that says whether to
        # believe it. `floor_mw` is the year's smallest CCGT+OCGT reading and is the number the
        # dispatch uses; `p1_mw` is the 1st percentile of the same year, published ONLY so a
        # reader can see whether that minimum is a lone outlier. Using p1 instead would raise the
        # floor, narrow the modelled swing and improve this model's score against the published
        # series -- which is why the robust statistic is the one that is reported and the raw
        # minimum is the one that is consumed (R12).
        "thermal_floor_mw": (
            None if thermal_floor_by_year is None
            else {
                str(y): {
                    "floor_mw": round(float(r["floor_mw"])),
                    "p1_mw": round(float(r["p1_mw"])),
                    "half_hours": int(r["half_hours"]),
                }
                for y, r in sorted(thermal_floor_by_year.items())
            }
        ),
        # THE BIOMASS ENVELOPE, PUBLISHED AS A MEASUREMENT AND NOT AS AN INPUT. `capacity_mw`
        # and `floor_mw` are what the fleet was observed at its highest and lowest that year;
        # `mean_mw` is where it actually spent its time. NONE of them reaches the shape above --
        # see `BIOMASS_DISPATCH_WIRED` for the measurement that decided that and for why the
        # answer is an outage model rather than a tidier percentile.
        #
        # IT IS PUBLISHED ANYWAY, AND THAT IS THE POINT OF PUBLISHING IT: the basis line says
        # biomass is held at a constant 2,400 MW, and these rows are how a reader checks how
        # wrong that is without taking this project's word for it. A named gap with its size
        # beside it is a different artefact from a named gap alone.
        "biomass_envelope_mw": (
            None if biomass_envelope_by_year is None
            else {
                str(y): {
                    "floor_mw": round(float(r["floor_mw"])),
                    "capacity_mw": round(float(r["capacity_mw"])),
                    "p1_mw": round(float(r["p1_mw"])),
                    "p99_mw": round(float(r["p99_mw"])),
                    "mean_mw": round(float(r["mean_mw"])),
                    "half_hours": int(r["half_hours"]),
                }
                for y, r in sorted(biomass_envelope_by_year.items())
            }
        ),
        # HOW MUCH OF THE SERIES ACTUALLY GOT THE CORRECTION, because the shape cannot show it.
        # A half hour served from the flat 5,600 MW block and one served from a MEASURED 5,600 MW
        # produce an identical number, so without this count the nuclear-and-hydro correction
        # could quietly stop applying to most of the series and nothing downstream would read
        # differently (R15 FAIL-SILENT). `negative_half_hours` is the one to watch: it is the
        # second of the two conditions that let this series cross the wall at half-hourly grain
        # at all, and the day it stops being zero the crossing has to be re-argued.
        "zero_carbon_must_run_coverage": (
            None if zero_carbon_must_run_coverage is None else {
                "usable_fraction": round(
                    float(zero_carbon_must_run_coverage["usable_fraction"]), 4),
                "usable_half_hours": int(zero_carbon_must_run_coverage["usable_half_hours"]),
                "negative_half_hours": int(
                    zero_carbon_must_run_coverage["negative_half_hours"]),
                "min_mw": round(float(zero_carbon_must_run_coverage["min_mw"])),
                "mean_mw": round(float(zero_carbon_must_run_coverage["mean_mw"])),
                "max_mw": round(float(zero_carbon_must_run_coverage["max_mw"])),
                "what_it_means": (
                    "The share of half hours whose NUCLEAR+NPSHYD outturn Elexon published, so "
                    "the must-run block is the fleet GB actually ran rather than a flat 5,600 "
                    "MW. The remainder falls back to that flat block -- the behaviour the whole "
                    "series had before 2026-08-26 -- and never to zero. The min/mean/max are "
                    "why this mattered: a block published as constant moves between 544 MW and "
                    "9,831 MW, and every megawatt of that was made up by the gas stack on a "
                    "schedule of the model's own invention."
                ),
            }
        ),
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
        "versus_published": versus_published(shape, demand, published, published_why),
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


def fuel_mix() -> tuple[dict, dict, dict, dict]:
    """(imports by half hour, coal capacity by year, the measured import coverage, thermal floor).

    THE ONE PLACE THE NEW INPUTS CANNOT BE FORGOTTEN, and that is its job. `build_shape` takes
    them all as optional keywords whose defaults reproduce the shape exactly as it was before
    coal, cables and the thermal floor were modelled -- a fail-open signature by construction. So
    the control is here, on the path that actually publishes: an absent or unusable mix RAISES
    out of `generate()` and the feed does not get written, rather than being rewritten with a
    series that quietly lost three corrections and says nothing about it.

    THE FLOOR IS UNPACKED TO `{year: floor_mw}` HERE, so the `p1_mw` published beside it stays a
    diagnostic and has no path into the dispatch. The biomass envelope is unpacked the same way
    one layer down, in `build_shape`, and for a stronger version of the same reason: its
    `mean_mw` would fit the published series better than either honest end.
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


def generate(out_path: Path | None = None) -> dict:
    demand = aggregate_demand(json.loads(DEMAND_CACHE.read_text(encoding="utf-8")))
    renewables = aggregate_renewable_generation(json.loads(AGWS_CACHE.read_text(encoding="utf-8")))
    (imports, coal_capacity, coverage, thermal_floors, must_run, must_run_coverage,
     biomass_envelope) = fuel_mix()
    shape = build_shape(
        demand,
        renewables,
        imports_by_period=imports,
        coal_capacity_by_year=coal_capacity,
        thermal_floor_by_year={y: r["floor_mw"] for y, r in thermal_floors.items()},
        zero_carbon_must_run_by_period=must_run,
        biomass_envelope_by_year=biomass_envelope if BIOMASS_DISPATCH_WIRED else None,
    )
    data = build(shape, demand, extra_dates=dates_with_reads(), import_coverage=coverage,
                 coal_capacity_by_year=coal_capacity, thermal_floor_by_year=thermal_floors,
                 zero_carbon_must_run_coverage=must_run_coverage,
                 biomass_envelope_by_year=biomass_envelope)
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    d = generate()
    print("wrote {} ({} record(s) over {}..{}; {} year(s) summarised from {} half hours)".format(
        OUT_PATH, len(d["records"]), d["records_cover"]["from"], d["records_cover"]["to"],
        len(d["by_year"]), d["series_covers"]["half_hours"]))
