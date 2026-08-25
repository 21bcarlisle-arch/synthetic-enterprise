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


def build(hh_days: dict, shape: dict, feed: dict, meter: dict) -> dict:
    accounts = []
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
