"""Count national GB news coverage of energy prices, per day, from GDELT's daily GKG files.

Gap G1 of the bill-shock page
(docs/market_research/how_households_respond_to_bill_shock_by_family_moment_and_payment_method_2026-11-21.md):
the world's announcement moment has no media term because nobody had counted the coverage.
This counts it. The method, its limits and the dated series are on
docs/market_research/media_coverage_of_energy_price_announcements_gdelt_2016_2025.md.

HARNESS-SIDE ONLY (W6). The series this writes is documentation. Nothing in company/ or
saas/ may read it, and the world reads it only through a build that cites the page.

Source: GDELT 1.0 Global Knowledge Graph daily files, data.gdeltproject.org/gkg/YYYYMMDD.gkg.csv.zip
(open data, free for any use with citation of the GDELT Project). Chosen over the DOC 2.0 API
because the API answered every request from this machine with HTTP 429 on 2026-11-21 and in
any case starts in 2017; the daily files start in 2013 and need no query budget. Raw files are
~25-55 MB each, are read streamed, and are deleted once counted; only per-day counts and the
matched URLs are cached, under ~/.cache/synthetic-enterprise/gdelt_energy_coverage/.

What counts as one article (all three must hold):
  1. its URL is on one of NATIONAL_OUTLETS (a fixed list, named on the page);
  2. it is about energy prices: the URL slug matches SLUG_RE, OR GDELT tagged it with an
     electricity- or gas-price theme AND named an energy supplier or Ofgem in it
     (BBC URLs carry no slug, so the second leg is the only way a BBC story can count);
  3. it is counted once, by URL, however many GKG rows carry it.
The denominator is every distinct national-outlet URL in the same day's file, so a week's
share does not move because GDELT started or stopped monitoring an outlet.
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit

GKG_URL = "https://data.gdeltproject.org/gkg/{day}.gkg.csv.zip"
CACHE_ROOT = Path.home() / ".cache" / "synthetic-enterprise" / "gdelt_energy_coverage"
FIRST_DAY = dt.date(2016, 1, 1)
LAST_DAY = dt.date(2025, 12, 31)

# UK national news outlets (print and broadcast) whose own domains GDELT monitors. A domain
# matches itself and any subdomain. thisismoney.co.uk is the Daily Mail group's money desk,
# which carries most of its energy-bill stories under its own domain.
NATIONAL_OUTLETS = (
    "bbc.co.uk", "bbc.com", "theguardian.com", "telegraph.co.uk", "independent.co.uk",
    "dailymail.co.uk", "thisismoney.co.uk", "mirror.co.uk", "express.co.uk", "thesun.co.uk",
    "thetimes.co.uk", "standard.co.uk", "inews.co.uk", "metro.co.uk", "news.sky.com",
    "itv.com", "ft.com",
)

# A slug about the price of household energy: an energy word and a price word in the
# same path segment, in either order, or the cap named outright.
_ENERGY = r"(energy|gas|electricity|power|heating|dual-fuel|fuel-bill)"
_PRICE = r"(bill|bills|price|prices|tariff|tariffs|cap)"
SLUG_RE = re.compile(
    rf"{_ENERGY}[^/]*-{_PRICE}(?![a-z])|{_PRICE}[^/]*-{_ENERGY}(?![a-z])|price-cap"
)
# A slug that says the price went UP. Reported beside the all-energy-price count, never
# instead of it: a cut, a freeze and a rise are all coverage of a price announcement.
RISE_RE = re.compile(
    r"(?<![a-z])(rise|rises|rising|hike|hikes|increase|increases|soar|soars|soaring|jump|"
    r"jumps|jumped|surge|surges|up-by|hit-by|raise|raises|raising|raised|hiking|hiked|put-up|"
    r"puts-up|increased|increasing|soared|higher)(?![a-z])"
)
PRICE_THEMES = ("ECON_ELECTRICALPRICE", "ECON_NATGASPRICE")
ENERGY_ORGS = (
    "ofgem", "british gas", "centrica", "npower", "e on", "e.on", "eon", "edf energy", "edf",
    "scottish power", "scottishpower", "sse", "ovo", "ovo energy", "octopus energy", "bulb",
    "bulb energy", "first utility", "shell energy", "big six",
)
# GKG's ORGANIZATIONS field is ';'-separated names; matched whole, so "sse" is not "assessment".


def names_energy_org(orgs: str) -> bool:
    return any(tok.strip() in ENERGY_ORGS for tok in orgs.lower().split(";"))


def national_outlet(url: str) -> str | None:
    host = urlsplit(url).netloc.lower().split(":")[0]
    for d in NATIONAL_OUTLETS:
        if host == d or host.endswith("." + d):
            return d
    return None


# Path segments that file a story under another country's news. A UK national's Australian
# edition writes about Australian power prices; that is not coverage a GB household reads.
FOREIGN_SECTIONS = frozenset(
    {"world", "australia-news", "us-news", "au", "us", "australia", "us-politics", "india",
     "africa", "asia", "americas", "europe-news", "canada", "new-zealand",
     # International wire copy a UK site republishes (dailymail.co.uk/wires/ap/...): the
     # hand-coded sample found a US petrol-price story here. /wires/pa/ is UK and stays.
     "ap", "afp"}
)


def foreign(url: str) -> bool:
    return bool(FOREIGN_SECTIONS.intersection(urlsplit(url).path.lower().split("/")))


def classify_row(themes: str, orgs: str, url: str) -> tuple[bool, bool]:
    """(is energy-price coverage, slug says a rise) for one URL of one GKG row."""
    path = urlsplit(url).path.lower()
    if foreign(url):
        return False, False
    slug_hit = bool(SLUG_RE.search(path))
    theme_hit = any(t in themes for t in PRICE_THEMES) and names_energy_org(orgs)
    hit = slug_hit or theme_hit
    return hit, hit and bool(RISE_RE.search(path))


def count_day(raw: bytes) -> dict:
    outlet_urls: dict[str, set[str]] = {}
    matched: dict[str, dict] = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as z, z.open(z.namelist()[0]) as f:
        for i, line in enumerate(io.TextIOWrapper(f, encoding="utf-8", errors="replace")):
            if i == 0:
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 11:
                continue
            for url in p[10].split("<UDIV>"):
                outlet = national_outlet(url)
                if outlet is None:
                    continue
                outlet_urls.setdefault(outlet, set()).add(url)
                if url in matched:
                    continue
                hit, rise = classify_row(p[3], p[6], url)
                if hit:
                    matched[url] = {"outlet": outlet, "rise": rise}
    return {
        "outlet_urls": {k: len(v) for k, v in sorted(outlet_urls.items())},
        "matched": matched,
    }


def fetch(day: dt.date, tries: int = 4) -> bytes | None:
    url = GKG_URL.format(day=day.strftime("%Y%m%d"))
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "poesys-research-harness"})
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            pass
        time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"{day}: GDELT daily GKG file would not download after {tries} tries")


def do_day(day: dt.date) -> str:
    out = CACHE_ROOT / f"{day:%Y%m%d}.json"
    if out.exists():
        return "cached"
    raw = fetch(day)
    rec = {"day": day.isoformat(), "source": GKG_URL.format(day=day.strftime("%Y%m%d"))}
    if raw is None:
        rec["missing"] = "GDELT has no daily GKG file for this day (HTTP 404)"
    else:
        rec.update(count_day(raw))
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec))
    tmp.replace(out)
    return "missing" if raw is None else f"{len(rec['matched'])} matched"


def day_order(first: dt.date, last: dt.date, priority: list[dt.date]) -> list[dt.date]:
    """Every day once. First the days coverage_at reads for some priority date (35 before to
    6 after), nearest first, so a pull cut short still grades every announcement it reached;
    then the rest of the decade in date order."""
    days = [first + dt.timedelta(n) for n in range((last - first).days + 1)]
    if not priority:
        return days

    def distance(d: dt.date) -> int:
        return min(abs((d - p).days) for p in priority)

    near = {p + dt.timedelta(k) for p in priority for k in range(-35, 7)}
    return sorted((d for d in days if d in near), key=lambda d: (distance(d), d)) + [
        d for d in days if d not in near
    ]


def _read_day(f: Path) -> dict:
    """A cached day, parsed as JSON at the read: it is never text to be searched."""
    with f.open(encoding="utf-8") as fh:
        return json.load(fh)


SERIES = (
    Path(__file__).resolve().parents[1]
    / "docs" / "market_research" / "media_coverage_energy_price_gdelt_weekly_2016_2025.json"
)


def aggregate(first: dt.date, last: dt.date) -> dict:
    """Weekly (Monday-start) counts from the per-day cache; a URL counts once, in its first day."""
    seen: set[str] = set()
    weeks: dict[str, dict] = {}
    day = first
    while day <= last:
        monday = day - dt.timedelta(day.weekday())
        w = weeks.setdefault(monday.isoformat(), {
            "week_start": monday.isoformat(), "days_counted": 0, "days_missing_at_source": 0,
            "national_urls": 0, "energy_price_articles": 0, "rise_articles": 0,
        })
        f = CACHE_ROOT / f"{day:%Y%m%d}.json"
        if f.exists():
            rec = _read_day(f)
            if rec.get("missing") is not None:
                w["days_missing_at_source"] += 1
            else:
                w["days_counted"] += 1
                w["national_urls"] += sum(rec["outlet_urls"].values())
                for url, v in rec["matched"].items():
                    # foreign() re-applied so a day cached before an exclusion was added
                    # is read by today's rule, not the rule of the day it was pulled.
                    if url in seen or foreign(url):
                        continue
                    seen.add(url)
                    w["energy_price_articles"] += 1
                    w["rise_articles"] += int(v["rise"])
        day += dt.timedelta(1)
    rows = []
    for w in weeks.values():
        w["per_1000_national_urls"] = (
            round(1000 * w["energy_price_articles"] / w["national_urls"], 2)
            if w["national_urls"] else None
        )
        w["complete"] = w["days_counted"] == 7
        rows.append(w)
    return {
        "what": "Weekly count of UK national news articles about household energy prices, "
                "counted over GDELT 1.0 GKG daily files. Method, limits and the announcement "
                "table: media_coverage_of_energy_price_announcements_gdelt_2016_2025.md",
        "source": "GDELT Project, Global Knowledge Graph 1.0 daily files "
                  "(data.gdeltproject.org/gkg/), open data, cited as the GDELT Project",
        "counted_by": "tools/fetch_gdelt_energy_price_coverage.py",
        "harness_only": "W6: documentation and a world input by citation; never read by "
                        "company/ or saas/",
        "outlets": list(NATIONAL_OUTLETS),
        "weeks": rows,
    }


ANNOUNCEMENTS = SERIES.with_name("energy_price_announcements_gb_2016_2025.json")


def _window(day: dt.date, start: int, stop: int) -> tuple[int, int, int] | None:
    """(articles, days counted, national URLs) over day+start .. day+stop-1; None if any day
    is not yet pulled, so an unpulled window reads as unknown, never as zero."""
    total = counted = national = 0
    for k in range(start, stop):
        f = CACHE_ROOT / f"{day + dt.timedelta(k):%Y%m%d}.json"
        if not f.exists():
            return None
        rec = _read_day(f)
        if rec.get("missing") is None:
            total += sum(1 for u in rec["matched"] if not foreign(u))
            counted += 1
            national += sum(rec["outlet_urls"].values())
    return total, counted, national


def coverage_at(day: dt.date) -> dict:
    """Coverage on `day` and in the 7 days from it, against the 28 days that end a week before.

    The baseline stops at day-8 so a leak or a trailed announcement in the days just before
    does not inflate it. Both are daily rates, so a day GDELT is missing does not bias either.
    """
    out: dict = {"day0_articles": None, "day0_per_1000_national_urls": None,
                 "week_articles": None, "baseline_per_day": None, "week_vs_baseline": None}
    d0, week, base = _window(day, 0, 1), _window(day, 0, 7), _window(day, -35, -7)
    if d0 is not None and d0[1]:
        out["day0_articles"] = d0[0]
        out["day0_per_1000_national_urls"] = round(1000 * d0[0] / d0[2], 1) if d0[2] else None
    if week is not None and week[1]:
        out["week_articles"] = week[0]
    if base is not None and base[1] and week is not None and week[1]:
        b = base[0] / base[1]
        out["baseline_per_day"] = round(b, 2)
        out["week_vs_baseline"] = round((week[0] / week[1]) / b, 1) if b else None
    return out


def announcement_table() -> list[dict]:
    rows = json.loads(ANNOUNCEMENTS.read_text())["announcements"]
    for r in rows:
        for moment in ("announced", "effective"):
            if r.get(moment):
                r[f"coverage_from_{moment}"] = coverage_at(dt.date.fromisoformat(r[moment]))
    return rows


def _one_row_per_line(series: dict) -> str:
    """JSON with each week and announcement on one line, so a re-pull diffs by the row."""
    head = {k: v for k, v in series.items() if k not in ("weeks", "announcements")}
    body = json.dumps(head, indent=1, ensure_ascii=False)[:-2]
    for key in ("weeks", "announcements"):
        if key in series:
            rows = ",\n  ".join(json.dumps(r, ensure_ascii=False) for r in series[key])
            body += f',\n "{key}": [\n  {rows}\n ]'
    return body + "\n}\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--first", type=dt.date.fromisoformat, default=FIRST_DAY)
    ap.add_argument("--last", type=dt.date.fromisoformat, default=LAST_DAY)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--priority", type=dt.date.fromisoformat, nargs="*", default=[],
                    help="dates whose surrounding weeks are pulled first")
    ap.add_argument("--aggregate", action="store_true",
                    help="write the weekly series from the cache instead of pulling")
    a = ap.parse_args(argv)
    if a.aggregate:
        series = aggregate(a.first, a.last)
        if ANNOUNCEMENTS.exists():
            series["announcements"] = announcement_table()
        SERIES.write_text(_one_row_per_line(series))
        print(SERIES)
        return 0
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    order = day_order(a.first, a.last, a.priority)
    with ThreadPoolExecutor(a.workers) as ex:
        for day, res in zip(order, ex.map(do_day, order)):
            print(day, res, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
