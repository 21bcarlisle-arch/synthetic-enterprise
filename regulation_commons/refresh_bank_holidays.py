"""Rebuild the committed England & Wales bank-holiday table from GDS sources.

REQUIRES NETWORK. Never imported by simulation/company code and never run
during a sim run (`feedback_no_network_in_autonomous_runs.md`) -- this is the
IaC record of *how* ``data/bank_holidays_england_wales.json`` was produced, so
the committed table can be reconstructed from the repo alone rather than being
a hand-typed artefact nobody can re-derive.

    python3 -m regulation_commons.refresh_bank_holidays

Two independent Government Digital Service channels, both authoritative:

1. ``https://www.gov.uk/bank-holidays.json`` -- the live GOV.UK feed. Rolling
   window only; GDS drops old years, so this alone cannot cover the 2016-2018
   years the simulation replays.
2. ``https://raw.githubusercontent.com/alphagov/calendars/master/lib/data/bank-holidays.json``
   -- the GDS source repository that *serves* channel 1. Its committed table
   still carries the years GOV.UK has since dropped. Same government-published
   values, not a third-party reconstruction.

The two channels OVERLAP (2019-2021). The refresh REFUSES to write if the
overlap disagrees on a single date -- that cross-check is the reason 2016-2018
can be committed without fabricating anything, and it is an independent
agreement between two artefacts, not a self-check.

Human-readable titles for the pre-2019 years are taken from the i18n-key ->
title mapping DERIVED FROM THE OVERLAP YEARS, never invented. A key that never
appears in the overlap keeps its raw i18n key as its title; titles are
descriptive only (the arithmetic reads dates), so an unmapped key is recorded
honestly rather than guessed.
"""

from __future__ import annotations

import datetime as dt
import json
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple

LIVE_FEED_URL = "https://www.gov.uk/bank-holidays.json"
SOURCE_REPO_URL = (
    "https://raw.githubusercontent.com/alphagov/calendars/master/"
    "lib/data/bank-holidays.json"
)
DIVISION = "england-and-wales"
OUTPUT = Path(__file__).parent / "data" / "bank_holidays_england_wales.json"


def _fetch(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=30) as fh:  # noqa: S310 - fixed GDS URLs
        return json.loads(fh.read().decode("utf-8"))


def _parse_live(payload: Any) -> Dict[str, Tuple[str, str]]:
    """Live GOV.UK feed -> {ISO date: (title, notes)}."""
    out: Dict[str, Tuple[str, str]] = {}
    for event in payload[DIVISION]["events"]:
        out[event["date"]] = (event["title"], event.get("notes", ""))
    return out


def _parse_source_repo(payload: Any) -> Dict[str, Tuple[str, str]]:
    """alphagov/calendars source table -> {ISO date: (i18n key, notes key)}."""
    out: Dict[str, Tuple[str, str]] = {}
    for year, events in payload["divisions"][DIVISION].items():
        if not year.isdigit():
            continue
        for event in events:
            day, month, yyyy = event["date"].split("/")
            out[f"{yyyy}-{month}-{day}"] = (event["title"], event.get("notes", ""))
    return out


def _cross_check(live: Dict[str, Any], repo: Dict[str, Any]) -> List[str]:
    """Return the overlap years, raising if the two channels disagree."""
    overlap = sorted({d[:4] for d in live} & {d[:4] for d in repo})
    if not overlap:
        raise SystemExit("REFUSING: the two GDS channels share no year -- cannot cross-check.")
    for year in overlap:
        live_dates = {d for d in live if d[:4] == year}
        repo_dates = {d for d in repo if d[:4] == year}
        if live_dates != repo_dates:
            raise SystemExit(
                f"REFUSING: GDS channels disagree for {year}: "
                f"live-only={sorted(live_dates - repo_dates)} "
                f"repo-only={sorted(repo_dates - live_dates)}"
            )
    return overlap


def _title_map(live: Dict[str, Tuple[str, str]], repo: Dict[str, Tuple[str, str]],
               overlap: List[str]) -> Dict[str, str]:
    """i18n key -> human title, derived from dates present in BOTH channels."""
    mapping: Dict[str, str] = {}
    for iso, (key, _notes) in repo.items():
        if iso[:4] in overlap and iso in live:
            mapping.setdefault(key, live[iso][0])
    return mapping


def build() -> Dict[str, Any]:
    live_raw = _fetch(LIVE_FEED_URL)
    repo_raw = _fetch(SOURCE_REPO_URL)
    live = _parse_live(live_raw)
    repo = _parse_source_repo(repo_raw)

    overlap = _cross_check(live, repo)
    titles = _title_map(live, repo, overlap)

    events: Dict[str, Dict[str, Any]] = {}
    for iso, (title, notes) in repo.items():
        events[iso] = {
            "date": iso,
            "title": titles.get(title, title),
            "substitute_day": "substitute" in notes.lower(),
            "source": "alphagov/calendars",
        }
    # The live feed wins where both carry a date: it is the currently-served
    # artefact. The cross-check above already proved they agree on dates.
    for iso, (title, notes) in live.items():
        events[iso] = {
            "date": iso,
            "title": title,
            "substitute_day": "substitute" in notes.lower(),
            "source": "gov.uk/bank-holidays.json",
        }

    ordered = [events[k] for k in sorted(events)]
    years = sorted({e["date"][:4] for e in ordered})
    return {
        "division": DIVISION,
        "generated_by": "regulation_commons/refresh_bank_holidays.py",
        "generated_on": dt.date.today().isoformat(),
        "sources": [
            {"url": LIVE_FEED_URL, "role": "live rolling window"},
            {"url": SOURCE_REPO_URL, "role": "GDS source repo, carries dropped years"},
        ],
        "cross_checked_overlap_years": overlap,
        "coverage": {"first_year": int(years[0]), "last_year": int(years[-1])},
        "events": ordered,
    }


def main() -> int:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    cov = payload["coverage"]
    print(
        f"wrote {OUTPUT} -- {len(payload['events'])} events, "
        f"{cov['first_year']}-{cov['last_year']}, "
        f"overlap cross-checked: {', '.join(payload['cross_checked_overlap_years'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
