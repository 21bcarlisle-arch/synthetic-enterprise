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
    "the floor corrects the LEVEL of the clean end and not the TIMING of it: correlation against "
    "the published series moved by less than 0.004 in every year and is still 0.73 in 2024, so "
    "this shape knows how clean a quiet half hour is far better than it knows which half hours "
    "were the quiet ones",
    "interconnector imports are counted at NESO's own published per-cable factors, but two of "
    "GB's nine cables postdate that table -- North Sea Link (Norway) and Viking Link (Denmark) -- "
    "so their flow is still dispatched as GB gas and reads dirtier than it was; that is 34% of "
    "imported MWh in 2024 and it is growing",
    "coal is dispatched from the fleet's demonstrated annual maximum, but its place in merit is "
    "fixed above the CCGT band rather than recomputed from the gas/coal spread, so the 2021-22 "
    "gas spike understates coal",
    "the must-run floor is a constant 8 GW; nuclear outages and hydro seasonality are not modelled",
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
    "about 1.36x the published series', so any benefit computed from moving load between quiet "
    "and busy half hours is an UPPER BOUND on the real one. What is no longer true, and was "
    "until the thermal floor was measured on 2026-08-25, is that the clean END is uniformly "
    "optimistic: flooring the stack at the gas fleet's demonstrated annual minimum moved the "
    "quietest half hours from about 3.2x too clean to a MIXED picture -- still slightly cleaner "
    "than published in 2019, 2022 and 2023, and now DIRTIER than published in 2020 and 2021. "
    "That is MEASURED, year by year, in `versus_published` below and never inferred from the gap "
    "list, which is the same reason the gaps are not all pushing one way: an import's sign "
    "depends on what it displaced -- against the mid-merit gas band a Dutch import is dirtier "
    "than what it replaced, against a peaker it is cleaner -- so only the net is knowable."
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


def published_series(demand: dict) -> tuple[dict | None, str]:
    """NESO's published shape on the same normalisation as ours, or (None, why).

    SPLIT OUT OF `versus_published` so it is fetched ONCE per run and used twice -- for the
    year-level comparison, and for the per-half-hour values the records carry. Building it
    twice would double the cost of the one part of this generator that reads a 12 MB cache,
    on a machine whose memory the director has named as a budget being spent.
    """
    try:
        from sim import neso_carbon_intensity as neso

        return neso.published_shape(
            neso.actual_by_period(neso.to_settlement_periods(neso.load_cached())), demand), ""
    except Exception as exc:  # noqa: BLE001 -- an absent comparison is reported, never fatal
        return None, "{}: {}".format(type(exc).__name__, exc)


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
        published, why_unavailable = published_series(demand)
    if published is None:
        return {"available": False, "why": why_unavailable}

    years = {}
    for year in sorted({k[0][:4] for k in shape}):
        try:
            measured = neso.compare_shapes(shape, published, demand, year)
        except Exception:  # noqa: BLE001 -- a year the two series do not share is simply absent
            continue
        row = {k: round(v, 4) for k, v in measured.items()}
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


def build(shape: dict, demand: dict, *, window_days: int = RECORD_WINDOW_DAYS,
          extra_dates: set[str] | None = None,
          import_coverage: dict | None = None,
          coal_capacity_by_year: dict | None = None,
          thermal_floor_by_year: dict | None = None) -> dict:
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
    published, published_why = published_series(demand)
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
        "typical_day": typical_day(shape),
        "records": records,
    }


def fuel_mix() -> tuple[dict, dict, dict, dict]:
    """(imports by half hour, coal capacity by year, the measured import coverage, thermal floor).

    THE ONE PLACE THE NEW INPUTS CANNOT BE FORGOTTEN, and that is its job. `build_shape` takes
    them all as optional keywords whose defaults reproduce the shape exactly as it was before
    coal, cables and the thermal floor were modelled -- a fail-open signature by construction. So
    the control is here, on the path that actually publishes: an absent or unusable mix RAISES
    out of `generate()` and the feed does not get written, rather than being rewritten with a
    series that quietly lost three corrections and says nothing about it.

    THE FLOOR IS UNPACKED TO `{year: floor_mw}` HERE, so the `p1_mw` published beside it stays a
    diagnostic and has no path into the dispatch.
    """
    from sim import elexon_fuel_outturn as fuel

    series = fuel.to_settlement_periods(fuel.load_cached())
    floors = fuel.thermal_floor_by_year(fuel.thermal_by_period(fuel.load_cached_thermal()))
    return (
        fuel.imports_by_period(series),
        fuel.coal_capacity_by_year(series),
        fuel.import_coverage(series),
        floors,
    )


def generate(out_path: Path | None = None) -> dict:
    demand = aggregate_demand(json.loads(DEMAND_CACHE.read_text(encoding="utf-8")))
    renewables = aggregate_renewable_generation(json.loads(AGWS_CACHE.read_text(encoding="utf-8")))
    imports, coal_capacity, coverage, thermal_floors = fuel_mix()
    shape = build_shape(
        demand,
        renewables,
        imports_by_period=imports,
        coal_capacity_by_year=coal_capacity,
        thermal_floor_by_year={y: r["floor_mw"] for y, r in thermal_floors.items()},
    )
    data = build(shape, demand, extra_dates=dates_with_reads(), import_coverage=coverage,
                 coal_capacity_by_year=coal_capacity, thermal_floor_by_year=thermal_floors)
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    d = generate()
    print("wrote {} ({} record(s) over {}..{}; {} year(s) summarised from {} half hours)".format(
        OUT_PATH, len(d["records"]), d["records_cover"]["from"], d["records_cover"]["to"],
        len(d["by_year"]), d["series_covers"]["half_hours"]))
