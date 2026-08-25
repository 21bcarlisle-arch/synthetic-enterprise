#!/usr/bin/env python3
"""The carbon layer on the half-hourly day Explore already shows.

REUSE: tools/generate_explore_carbon.py
CLASS: CUSTOM
INDEX: searched "explore", "carbon", "generate", "hh_day", "footprint", "intensity". Three
       organs came back and all three are called rather than copied. `tools/
       generate_explore_hh_day.py` already picks the DAYS and names which accounts have a
       half-hourly record and which do not -- this reads its output rather than re-deciding,
       so the two panels on the page can never name different days or disagree about who has a
       meter. `company/carbon/half_hourly_footprint.py` does the arithmetic.
       `docs/market_data/grid_intensity_feed.json` supplies the shape. Nothing here computes
       an emission.

WHY IT SITS ON EXPLORE. Explore stage 3 already renders C7, C8 and C9's electricity across a
real dated day, half hour by half hour. Those are the same three accounts -- the only three --
whose carbon can be measured rather than estimated. Putting the emissions beside the
consumption that produced them, on the same day, in the same place, is the shortest route from
"here is what this household drew" to "here is what that cost the atmosphere". A separate page
would have been a fourth surface saying a fifth of what this one already says, and the
five-tabs ruling of 2026-08-20 is what that costs.

WHAT IT PUBLISHES, AND WHAT IT REFUSES TO. Emissions, with their basis, their sample size and
their period. Not abatement: there is no counterfactual anywhere in this pipeline, the
advisor's scope brief of 2026-08-04 ranks the four bases that could supply one and says plainly
that at this book size none of the credible three is viable. The site's `NOT YET MEASURED` tag
on £/tCO2e abated is therefore CORRECT and stays. This is the layer underneath it.

Run:  python3 -m tools.generate_explore_carbon
"""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path

from company.carbon.half_hourly_footprint import (
    FOOTPRINT_BASIS,
    MEASURED,
    NOT_INCLUDED,
    PROFILED,
    UNCOVERED,
    BookFootprint,
    FootprintUnavailable,
    load_shape,
    measured_footprint,
)
from simulation.demand_model import HEATING_PERIOD_WEIGHTS

PROJECT = Path(__file__).resolve().parent.parent
HH_DAYS = PROJECT / "site" / "data" / "explore_hh_days.json"
CUSTOMER_DETAIL = PROJECT / "site" / "data" / "customers"
INTENSITY_FEED = PROJECT / "docs" / "market_data" / "grid_intensity_feed.json"
OUT_PATH = PROJECT / "site" / "data" / "explore_carbon.json"

PERIODS = 48


def _clock(period: int) -> str:
    minutes = (period - 1) * 30
    return "{:02d}:{:02d}".format(minutes // 60, minutes % 60)


def _load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _panels(day_record: dict) -> list[tuple[str, dict]]:
    """(panel name, panel) for each dated day an account's record carries.

    `generate_explore_hh_day` keys an account's days by what each one is FOR -- `hardest_day`,
    `summer_day` -- and that naming is the point of the panel, so it is carried through rather
    than flattened into an anonymous list. Anything without a date and a period series is not a
    day and is skipped.
    """
    return [
        (str(name), panel)
        for name, panel in sorted(day_record.items())
        if isinstance(panel, dict) and panel.get("date") and panel.get("periods")
    ]


def _reads_from_day(panel: dict) -> list[dict]:
    """One panel -> half-hourly read dicts.

    Reads the SAME `periods` array the consumption chart renders, so a reader comparing the two
    panels is comparing one set of numbers rather than two that happen to agree today.
    """
    date_str = panel.get("date")
    periods = panel.get("periods") or []
    if not date_str or not periods:
        return []
    return [
        {"date": str(date_str), "period": i + 1, "kwh": float(v)}
        for i, v in enumerate(periods[:PERIODS])
        if v is not None
    ]


#: Meter types that can record a half hour at all. Same set as `generate_explore_hh_day`'s,
#: and it is the CAPABILITY that decides the ceiling on how much of the mission is measurable.
_HALF_HOURLY_CAPABLE = frozenset({"smart", "hh"})


def modelled_load_windows() -> list[int]:
    """The settlement periods the WORLD's demand model places all heating load in.

    DERIVED FROM THE PRODUCER, never restated here. `HEATING_PERIOD_WEIGHTS` is a single
    module-level constant in `simulation/demand_model.py`: uniform weight over periods 13-20
    and 34-44, zero elsewhere, identical for every premise in the country. Reading it rather
    than copying "06:00-10:00 and 16:30-22:00" into this file means that when
    `W1_11_fabric_physics_core` lands a per-home shape, the sentence this feeds follows the
    model instead of going quietly stale while still sounding measured.
    """
    return [p for p, w in enumerate(HEATING_PERIOD_WEIGHTS, start=1) if w > 0]


def shape_provenance(reads: Sequence[Mapping]) -> dict:
    """How much of this day's kWh the world MODELLED into that fixed window.

    WHY A CUSTOMER-FACING PANEL CARRIES THIS. The timing effect is a product of two series --
    the grid's shape and the household's -- and the panel attributes it to the household in as
    many words. On the days this page prices, 86-95% of the day's kWh sits inside the two
    windows above, which are also the two windows the grid is dirtiest in. So the figure is
    substantially a property of a national template that does not vary between households, and
    a page that says "when this household drew" without saying so is attributing to a home
    something a constant decided. MEASURED per day rather than asserted once, because the share
    differs by household and the honest correction is the one this home's own numbers support.
    """
    windows = set(modelled_load_windows())
    total = sum(float(r["kwh"]) for r in reads)
    if total <= 0:
        return {"available": False, "why": "The day's metered total is zero, so no share of it can be attributed."}
    inside = sum(float(r["kwh"]) for r in reads if int(r["period"]) in windows)
    return {
        "available": True,
        "modelled_window_periods": sorted(windows),
        "modelled_window_clock": _window_clock(sorted(windows)),
        "share_in_modelled_window": round(inside / total, 4),
        "periods_in_window": len(windows),
        "periods_in_day": PERIODS,
        "owning_defect": "W1_11_fabric_physics_core",
    }


def _window_clock(periods: Sequence[int]) -> list[str]:
    """Contiguous runs of settlement periods -> human clock ranges, for the page to print."""
    runs: list[list[int]] = []
    for p in periods:
        if runs and p == runs[-1][-1] + 1:
            runs[-1].append(p)
        else:
            runs.append([p])
    return [f"{_clock(r[0])}-{_clock(r[-1] + 1)}" for r in runs]


def _meter_counts(detail_dir: Path) -> dict:
    """{accounts, half_hourly_capable} from the meter types the company holds.

    COUNTED SEPARATELY FROM WHO HAS A READ TODAY, because they are two different holes and a
    single number hides one of them: 14 accounts have a meter that COULD record a half hour and
    7 have a published half-hourly day. This repo has already filed the page that told three
    households they had no smart meter when they did.
    """
    capable = total = 0
    if not detail_dir.is_dir():
        return {"half_hourly_capable": 0, "accounts": 0}
    for path in sorted(detail_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        detail = _load(path)
        if not isinstance(detail, dict) or not detail.get("account_id"):
            continue
        total += 1
        if str(detail.get("meter_type") or "").strip().lower() in _HALF_HOURLY_CAPABLE:
            capable += 1
    return {"half_hourly_capable": capable, "accounts": total}


def _why_unavailable(date_str: str, feed: dict) -> str:
    """Which KIND of absence this is, in the reader's words.

    "No data" covers two situations a reader must not have to guess between: a day before the
    published series begins at all, and a gap INSIDE it. Both produced an UNAVAILABLE on this
    page's first run -- 2016-01-01 is two months before Elexon's outturn coverage starts, and
    2022-06-24 falls in a stretch where the wind-and-solar outturn is missing so the half hour
    is skipped rather than treated as windless. Naming which is which is the difference between
    a known limit and a suspected bug.
    """
    covers = feed.get("series_covers") or {}
    first, last = covers.get("from"), covers.get("to")
    if first and last and not (first <= date_str <= last):
        return (
            "This day is outside the published grid-intensity series entirely, which runs "
            "{}..{} -- Elexon's half-hourly outturn does not go back further.".format(first, last)
        )
    return (
        "This day falls inside the published series but has no half hours in it: the "
        "wind-and-solar outturn is missing for it, and a missing renewable reading is not a "
        "windless day, so those half hours are skipped rather than counted as dirty."
    )


def published_shape_from_feed(feed: dict) -> dict:
    """{(date, period): NESO's published shape} out of the feed's own records.

    Read from the SAME records the company's shape is read from, so a half hour cannot appear on
    one side of the comparison and not the other for a reason to do with file layout.
    """
    return {
        (str(r["date"]), int(r["period"])): float(r["published"])
        for r in (feed.get("records") or [])
        if r.get("date") is not None and r.get("period") is not None
        and r.get("published") is not None
    }


def belief_versus_truth(
    reads: Sequence[Mapping],
    shape: Mapping[tuple[str, int], float],
    published: Mapping[tuple[str, int], float],
    feed: dict,
    year: str,
) -> dict:
    """THIS household's timing effect computed twice: through the company's shape, and through
    NESO's published series. The coupled-triad rung, at the grain a reader can check.

    WHY THIS IS NOT THE SPREAD RATIO ALREADY ON THE PAGE. The feed says this model overstates
    the grid's total range by about 3.2x, and until now the page asked the reader to discount
    every household figure by that factor himself. A range ratio does not translate into a
    household's answer: it depends entirely on WHEN that household drew. Measured, the two
    disagree by anything from a quarter of a percentage point to twenty-eight, and on at least
    one real household-day THE SIGN IS DIFFERENT -- the company believes the home drew dirtier
    than average and the published grid says it drew cleaner. No discount factor recovers that.

    BOTH SIDES RE-NORMALISED over the half hours the two series share in this calendar year,
    using the divisors `compare_shapes` computed, because each series arrives normalised over
    its own coverage and comparing them raw measures the coverage. Recomputing the divisors here
    from the feed's trimmed records would be a different normalisation wearing the same name.

    REFUSED, never approximated, when the year is one the headline itself excludes. 2018 shares
    exactly ONE half hour with the published series in this tree; a divisor from one half hour
    is not a year's mean, and this project has already published a figure that was wrong by 10%
    for precisely that reason. A refusal says which of the two series was missing.
    """
    year_row = ((feed.get("versus_published") or {}).get("by_year") or {}).get(year) or {}
    if not year_row.get("counts_toward_headline"):
        return {
            "available": False,
            "why": (
                "{} shares too few half hours with NESO's published series for a year mean, so "
                "there is nothing to re-normalise this household against. The comparison is "
                "absent rather than approximated.".format(year)
            ),
        }
    ours_divisor = year_row.get("reconstructed_renormalisation_divisor")
    theirs_divisor = year_row.get("published_renormalisation_divisor")
    if not ours_divisor or not theirs_divisor:
        return {"available": False,
                "why": "the feed carries no re-normalisation divisor for {}".format(year)}

    kwh = belief = truth = 0.0
    used = missing = 0
    for read in reads:
        key = (str(read.get("date") or ""), int(read.get("period") or 0))
        our_value, their_value = shape.get(key), published.get(key)
        if our_value is None or their_value is None or read.get("kwh") is None:
            missing += 1
            continue
        k = float(read["kwh"])
        kwh += k
        belief += k * (our_value / ours_divisor)
        truth += k * (their_value / theirs_divisor)
        used += 1

    if used == 0 or kwh <= 0.0:
        return {
            "available": False,
            "why": (
                "no half hour of this day appears in BOTH series, so the two answers cannot be "
                "put beside each other. NESO publishes from 2018 and the cached series is "
                "shorter still; this is an absence, not an agreement."
            ),
        }

    belief_pct = 100.0 * (belief / kwh - 1.0)
    truth_pct = 100.0 * (truth / kwh - 1.0)
    return {
        "available": True,
        "belief_pct": round(belief_pct, 2),
        "truth_pct": round(truth_pct, 2),
        "gap_pp": round(belief_pct - truth_pct, 2),
        "sign_differs": (belief_pct >= 0.0) != (truth_pct >= 0.0),
        "half_hours": used,
        "half_hours_without_published": missing,
        "basis": (
            "Both figures are this household's own metered half hours weighted by a grid shape "
            "and compared with the flat annual method. BELIEF uses the company's reconstructed "
            "shape; TRUTH uses NESO's published half-hourly carbon intensity. Both series "
            "re-normalised over the half hours they share in {}, so the difference is physics "
            "and not coverage.".format(year)
        ),
    }


def _household_gap_summary(accounts: list) -> dict:
    """The book-level reading of the per-household gaps, counts first.

    THE COUNTS LEAD because most panels cannot be compared at all: NESO's cached series starts
    in 2019 and half the days this page shows are older. A mean gap quoted without saying it is
    a mean over six panels of fourteen is the same defect as a margin quoted without its book.
    """
    measured = [
        row["belief_vs_truth"] for row in accounts
        if isinstance(row.get("belief_vs_truth"), dict) and row["belief_vs_truth"].get("available")
    ]
    total = sum(1 for row in accounts if "belief_vs_truth" in row)
    if not measured:
        return {
            "available": False,
            "panels_on_page": total,
            "why": (
                "no household-day on this page has half hours in BOTH the company's shape and "
                "NESO's published series, so the company's belief has not been measured against "
                "the published grid at this grain. Unmeasured, not agreed."
            ),
        }
    gaps = [row["gap_pp"] for row in measured]
    overstated = sum(1 for g in gaps if g > 0.0)
    flips = sum(1 for row in measured if row["sign_differs"])
    return {
        "available": True,
        "panels_measured": len(measured),
        "panels_on_page": total,
        "panels_without_published_series": total - len(measured),
        "mean_gap_pp": round(sum(gaps) / len(gaps), 2),
        "max_gap_pp": round(max(gaps, key=abs), 2),
        "belief_overstates_on": overstated,
        "sign_flips": flips,
        "statement": (
            "On {} of {} household-days this page shows, the company's own grid shape can be "
            "checked against NESO's published series. It overstates the timing effect on {} of "
            "them, by {} percentage points on average and {} at the widest{}. The company is not "
            "shown the published series and is not corrected by it: the gap IS the score."
        ).format(
            len(measured), total, overstated,
            round(sum(gaps) / len(gaps), 1), round(max(gaps, key=abs), 1),
            (", and on {} the two disagree about whether the household drew cleaner or dirtier "
             "than average at all".format(flips)) if flips else "",
        ),
    }


def build(hh_days: dict, shape: dict, feed: dict, meter: dict) -> dict:
    accounts = []
    published = published_shape_from_feed(feed)
    for account_id, day_record in sorted((hh_days.get("accounts") or {}).items()):
        if not isinstance(day_record, dict):
            continue
        for panel_name, panel in _panels(day_record):
            reads = _reads_from_day(panel)
            if not reads:
                continue
            try:
                fp = measured_footprint(account_id, reads, shape)
            except FootprintUnavailable as exc:
                # NAMED, not dropped. A day the page shows consumption for and carbon for is a
                # promise; a day it shows consumption for and silently no carbon for leaves a
                # reader deciding for himself whether the number is zero.
                accounts.append({
                    "account_id": account_id, "panel": panel_name,
                    "date": panel.get("date"),
                    "unavailable": _why_unavailable(str(panel.get("date") or ""), feed),
                    "detail": str(exc),
                })
                continue
            half_hours = [
                {
                    "period": r["period"],
                    "clock": _clock(r["period"]),
                    "kwh": round(r["kwh"], 4),
                    "shape": round(shape[(r["date"], r["period"])], 4),
                }
                for r in reads if (r["date"], r["period"]) in shape
            ]
            # THE SPREAD BELONGS TO THE PANEL'S OWN YEAR, NOT THE PAGE'S NEWEST. The first
            # version put one `year_stats` block at the top of the file, taken from the latest
            # dated day on the whole page -- so C7's panel showed a February 2021 day and the
            # sentence under it quoted 2025's spread. A figure quoted against a period that is
            # not its own is the R14 defect one level up from the clock.
            row_year = str(fp.period_from)[:4]
            accounts.append({
                "account_id": account_id,
                "panel": panel_name,
                "date": fp.period_from,
                "year": row_year,
                "belief_vs_truth": belief_versus_truth(reads, shape, published, feed, row_year),
                # THE OTHER HALF OF THE MULTIPLICATION. `belief_vs_truth` measures the GRID
                # side's error; this measures how much of the answer the CONSUMPTION side's
                # national template placed. Both, or the page corrects one of two overstatements
                # and reads as if it had corrected the figure.
                "shape_provenance": shape_provenance(reads),
                "year_stats": (feed.get("by_year") or {}).get(row_year),
                "kwh": fp.kwh,
                "co2e_kg_timed": fp.co2e_kg_timed,
                "co2e_kg_flat": fp.co2e_kg_flat,
                "timing_effect_pct": round(fp.timing_effect_pct, 2),
                "half_hours": fp.half_hours,
                "cleanest": min(half_hours, key=lambda h: h["shape"], default=None),
                "dirtiest": max(half_hours, key=lambda h: h["shape"], default=None),
                "profile": half_hours,
            })

    measured_ids = {a["account_id"] for a in accounts if "co2e_kg_timed" in a}
    total_accounts = meter.get("accounts") or 0
    counts = {
        MEASURED: len(measured_ids),
        PROFILED: max(0, total_accounts - len(measured_ids)),
        UNCOVERED: 0,
    }
    book = BookFootprint(accounts=(), counts=counts)

    year = max((a.get("date") or "0000")[:4] for a in accounts) if accounts else None
    year_stats = (feed.get("by_year") or {}).get(year) if year else None

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "basis": FOOTPRINT_BASIS,
        "not_included": NOT_INCLUDED,
        "coverage_statement": book.coverage_statement(),
        # TOP LEVEL, not inside `grid` and not per account-day: it is a property of the SHAPE
        # every panel is computed from, and the page's control refuses to render a spread
        # without it. Nested one level deeper on the first pass, which rendered as the spread
        # silently VANISHING -- the correct failure direction, and the reason the render check
        # caught it where the unit test had passed on its own skip path.
        "versus_published": (feed.get("versus_published") or {}),
        # THE SAME COMPARISON ONE GRAIN DOWN. `versus_published` is a fact about two SERIES;
        # this is a fact about the HOUSEHOLDS this page actually shows, and it is the one the
        # mission's number is made of. Published even when it is unavailable, for the same
        # reason the series-level one is: a missing gap reads as a gap of zero.
        "versus_published_households": _household_gap_summary(accounts),
        "counts": counts,
        "half_hourly_capable_meters": meter.get("half_hourly_capable", 0),
        "accounts_on_book": total_accounts,
        "grid": {
            "year": year,
            "published_at": feed.get("published_at"),
            "source": feed.get("source"),
            "error_direction": feed.get("error_direction"),
            "named_gaps": feed.get("named_gaps") or [],
            "shape_basis": feed.get("basis"),
            "year_stats": year_stats,
            "typical_day": (feed.get("typical_day") or {}).get(year),
        },
        "abatement": {
            "measured": False,
            "why": (
                "Abatement is what a household did NOT emit because of something the supplier "
                "did, which requires a claim about a world that did not happen. The credible "
                "bases for that claim are a randomised holdout, a matched comparison, or a "
                "weather-normalised before-and-after, and at three measured households none of "
                "them is viable. So the score in pounds per tonne abated stays NOT YET "
                "MEASURED, and what is published here is emissions."
            ),
        },
        "accounts": accounts,
    }


def generate(out_path: Path | None = None) -> dict:
    shape, _typical = load_shape(INTENSITY_FEED)
    feed = _load(INTENSITY_FEED) or {}
    data = build(_load(HH_DAYS) or {}, shape, feed, _meter_counts(CUSTOMER_DETAIL))
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    d = generate()
    print("wrote {} ({} measured account-day(s); {} of {} accounts have a capable meter)".format(
        OUT_PATH, len([a for a in d["accounts"] if "co2e_kg_timed" in a]),
        d["half_hourly_capable_meters"], d["accounts_on_book"]))
