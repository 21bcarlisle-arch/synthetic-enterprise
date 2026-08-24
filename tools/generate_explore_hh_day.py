#!/usr/bin/env python3
"""Generate site/data/explore_hh_days.json -- the second clock Explore's stage 3 has promised.

THE GAP THIS CLOSES, and it is a gap between the page's own copy and the page.
`site/explore/index.html`'s stage 3 is titled *"Two clocks: gas across the years, electricity
across a day"* and its standfirst says electricity *"answers to the day"*. It then renders
electricity BY YEAR, in the same bar table as gas. The director's brief (§5.3) asks for the
thing the copy promises: *"Electricity across one day, half-hourly, showing the evening peak"*,
because *"the switch between them is the point"* -- a supplier reasons on both clocks at once
and bills on neither.

ONE REAL DAY, NAMED, NOT A MEAN DAY. Averaging 872 winter days would produce a smoother and
more flattering curve, and it would be a figure this project authored rather than one the run
produced (SITE_CONSTITUTION rule 3: the site is a RENDERING, never an author). So each panel is
a single dated day lifted whole out of `sim/hh_data/{account}.csv`, and every one of its 48
numbers is a metered value with a date on it. The days are chosen by a rule, stated on the page:
the household's own HIGHEST-consumption day, and the MEDIAN summer day. The first is the day
that decides what the supplier had to buy; the second is what the same meter looks like when
nothing is being heated.

WHICH SIDE OF THE WALL THIS IS ON -- checked, not assumed. For an HH-settled meter the supplier
genuinely receives these reads: `company/portal/app.py::consumption_page` calls
`company.billing.hh_consumption.recent_hh_periods` over `docs/market_data/consumption_feed.json`
for exactly the accounts whose `metering == "HH"`. So this is one of the few places where the
world's record and the company's picture are the SAME artefact -- which is the wall lesson of
stage 3 rather than an exception to it, because the profile-class household next to it reports a
handful of times a year and its curve is inferred. `corroboration` below MEASURES that agreement
against the company's own feed instead of asserting it; a divergence is reported, never hidden.

Accounts with no half-hourly meter are named in `accounts_without_half_hourly` so the page can
say WHY it is showing nothing for them. That absence is the point, not a hole.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
HH_DIR = PROJECT / "sim" / "hh_data"
BOOK_PATH = PROJECT / "site" / "data" / "customers.json"
DETAIL_DIR = PROJECT / "site" / "data" / "customers"
COMPANY_FEED = PROJECT / "docs" / "market_data" / "consumption_feed.json"
OUT_PATH = PROJECT / "site" / "data" / "explore_hh_days.json"

PERIODS = 48
#: Calendar months treated as summer for the "nothing is being heated" panel.
SUMMER_MONTHS = ("06", "07", "08")


def clock_of(period: int) -> str:
    """Settlement period (1-48) -> the local clock time it starts at."""
    minutes = (period - 1) * 30
    return "{:02d}:{:02d}".format(minutes // 60, minutes % 60)


def read_days(path: Path) -> list[dict]:
    """Every day in one account's half-hourly file, as {date, periods[48], total_kwh}.

    A row with a missing or unparseable period is DROPPED rather than zero-filled: a zero is a
    reading that says the household used nothing, and inventing 48 of them would put a flat line
    on a published page under the word "metered".
    """
    days = []
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                periods = [float(row["p{}".format(i + 1)]) for i in range(PERIODS)]
            except (KeyError, TypeError, ValueError):
                continue
            days.append({"date": row.get("date"), "periods": periods,
                         "total_kwh": round(sum(periods), 3)})
    return days


def _panel(day: dict, rule: str) -> dict:
    peak_i = max(range(PERIODS), key=lambda i: day["periods"][i])
    return {
        "date": day["date"],
        "chosen_by": rule,
        "total_kwh": day["total_kwh"],
        "periods": [round(v, 4) for v in day["periods"]],
        "peak_period": peak_i + 1,
        "peak_clock": clock_of(peak_i + 1),
        "peak_kwh": round(day["periods"][peak_i], 4),
    }


def pick_days(days: list[dict]) -> dict:
    """The two dated days a reader is shown, and the rule that chose each."""
    if not days:
        return {}
    hardest = max(days, key=lambda d: d["total_kwh"])
    summer = sorted((d for d in days if str(d["date"])[5:7] in SUMMER_MONTHS),
                    key=lambda d: d["total_kwh"])
    out = {"hardest_day": _panel(hardest, "the highest-consumption day in this meter's whole "
                                          "record -- the day that decided what the supplier "
                                          "had to buy")}
    if summer:
        out["summer_day"] = _panel(summer[len(summer) // 2],
                                   "the median summer day, when nothing is being heated")
    return out


def corroborate(account_id: str, days: list[dict], feed: dict | None) -> dict:
    """Measure the company's own feed against the world's record on the day they overlap.

    NOT a decoration and not an assertion. The page claims that for an HH meter the supplier
    sees what the world sees; this is the number that claim rests on, and a disagreement is
    published as one rather than smoothed away. `available: False` when the feed carries no day
    for this account -- an unmeasured claim must not read as a verified one.
    """
    records = (feed or {}).get("records") or []
    mine = [r for r in records if r.get("customer_id") == account_id]
    if not mine:
        return {"available": False,
                "why": "the company's published feed carries no day for this account"}
    # ONE DAY, and the newest. The feed has carried more than one date for an account, and
    # comparing every record it holds against a single day's periods produced 96 "comparisons"
    # of 48 periods and a difference that was really two different days -- a measurement that
    # would have published a divergence nobody had.
    date = max(str(r.get("date")) for r in mine)
    mine = [r for r in mine if str(r.get("date")) == date]
    world = next((d for d in days if str(d["date"]) == date), None)
    if world is None:
        return {"available": False,
                "why": "the company's feed carries {} and the world's record does not reach "
                       "that date".format(date)}
    diffs = [abs(float(r["kwh"]) - world["periods"][int(r["period"]) - 1])
             for r in mine
             if isinstance(r.get("period"), int) and 1 <= r["period"] <= PERIODS]
    return {
        "available": True,
        "date": date,
        "periods_compared": len(diffs),
        "max_abs_difference_kwh": round(max(diffs), 6) if diffs else None,
    }


def build(book: dict, details: dict, feed: dict | None,
          hh_files: dict[str, Path]) -> dict:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    accounts: dict[str, dict] = {}
    without: list[dict] = []

    for customer in book.get("customers") or []:
        leg = ((customer.get("legs") or {}).get("electricity") or {})
        account_id = leg.get("cid")
        if not account_id:
            continue
        detail = details.get(account_id) or {}
        has_hh = bool((detail.get("consumption") or {}).get("has_hh_data"))
        path = hh_files.get(account_id)
        if not (has_hh and path):
            without.append({
                "customer_group": customer.get("customer_group"),
                "account_id": account_id,
                "meter_type": detail.get("meter_type"),
            })
            continue
        days = read_days(path)
        picked = pick_days(days)
        if not picked:
            without.append({
                "customer_group": customer.get("customer_group"),
                "account_id": account_id,
                "meter_type": detail.get("meter_type"),
            })
            continue
        accounts[customer.get("customer_group")] = dict(
            picked,
            account_id=account_id,
            days_on_record=len(days),
            corroboration=corroborate(account_id, days, feed),
        )

    return {
        "generated_at": stamp,
        "available": bool(accounts),
        "source": "sim/hh_data/<account>.csv -- the world's half-hourly record, one dated day "
                  "per panel, no averaging",
        "accounts": accounts,
        "accounts_without_half_hourly": without,
        # Said here rather than hard-coded in the page, so the sentence a reader meets moves
        # with the book instead of going stale the first time a meter is upgraded.
        "coverage_statement": (
            "{n} of {t} households on this book have a half-hourly meter. The rest report a "
            "handful of readings a year, so neither the supplier nor this page can draw their "
            "day -- the curve for those homes is inferred from a profile, not measured."
        ).format(n=len(accounts), t=len(accounts) + len(without)),
    }


def _load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def generate(out_path: Path | None = None) -> dict:
    book = _load(BOOK_PATH) or {}
    details = {}
    if DETAIL_DIR.is_dir():
        for f in sorted(DETAIL_DIR.glob("*.json")):
            if f.name.startswith("_"):
                continue
            d = _load(f)
            if isinstance(d, dict) and d.get("account_id"):
                details[d["account_id"]] = d
    hh_files = {p.stem: p for p in sorted(HH_DIR.glob("*.csv"))} if HH_DIR.is_dir() else {}
    data = build(book, details, _load(COMPANY_FEED), hh_files)
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    d = generate()
    print("wrote {} ({} account(s) with a day, {} without)".format(
        OUT_PATH, len(d["accounts"]), len(d["accounts_without_half_hourly"])))
