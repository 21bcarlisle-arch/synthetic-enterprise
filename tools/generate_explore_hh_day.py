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

Accounts with no half-hourly READ RECORD are named in `accounts_without_half_hourly` so the page
can say WHY it is showing nothing for them. That absence is the point, not a hole.

AND "NO RECORD" IS NOT "NO SMART METER", which is what the published sentence used to say
(2026-08-24). On the book as it stands, 68 of 75 households have no half-hourly day to draw --
and three of those 68 have a SMART METER. Calling all 68 "households without a half-hourly meter"
is false for exactly those three, and false in the direction that flatters us: it presents a
consent-and-read-frequency gap as a metering-estate gap, which is a different problem with a
different fix. In GB a smart meter is only read half-hourly where the customer's read-frequency
consent allows it; the meter can measure every half-hour and the supplier still hold twelve
readings a year. The counts are therefore split at the source -- `smart_without_hh_reads` beside
`without_smart_meter` -- and the sentence names both. `smart_meter_but_no_hh_reads` carries the
accounts themselves so the number is checkable rather than merely stated.
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


#: Meter types that CAN physically report half-hourly. `Smart` is the domestic SMETS meter;
#: `HH` is the half-hourly-settled I&C metering class. `Traditional` cannot, at any consent
#: setting, which is why it is the one absence that is genuinely about the metering estate.
#: Anything unrecognised is treated as NOT smart on purpose: this count is published as
#: "we could be reading these and are not", and guessing a strange value into that sentence
#: would overstate the claim. A new meter type therefore shows up as a quiet zero, not a
#: fabricated number -- and `_METER_TYPES_SEEN` below is what makes it noisy instead.
_HALF_HOURLY_CAPABLE_METERS = frozenset({"smart", "hh"})


def _is_smart(detail: dict) -> bool:
    return str(detail.get("meter_type") or "").strip().lower() in _HALF_HOURLY_CAPABLE_METERS


def build(book: dict, details: dict, feed: dict | None,
          hh_files: dict[str, Path]) -> dict:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    accounts: dict[str, dict] = {}
    without: list[dict] = []
    # A SUBSET of `without`, not a parallel list: every entry here is also in `without`, so the
    # two counts can never disagree about how many households have no day to draw. Building it
    # as its own scan of the book is how that guarantee would be lost.
    smart_without: list[dict] = []

    def _no_reads(customer, account_id, detail, why):
        row = {
            "customer_group": customer.get("customer_group"),
            "account_id": account_id,
            "meter_type": detail.get("meter_type"),
            # WHICH of the two absences this is. `no_hh_record` means the world never wrote a
            # half-hourly file for this account; `no_usable_day` means it did and no day in it
            # survived `pick_days`. They look identical on the page and are different defects
            # -- the second is ours.
            "why": why,
        }
        without.append(row)
        if _is_smart(detail):
            smart_without.append(row)

    for customer in book.get("customers") or []:
        leg = ((customer.get("legs") or {}).get("electricity") or {})
        account_id = leg.get("cid")
        if not account_id:
            continue
        detail = details.get(account_id) or {}
        has_hh = bool((detail.get("consumption") or {}).get("has_hh_data"))
        path = hh_files.get(account_id)
        if not (has_hh and path):
            _no_reads(customer, account_id, detail, "no_hh_record")
            continue
        days = read_days(path)
        picked = pick_days(days)
        if not picked:
            _no_reads(customer, account_id, detail, "no_usable_day")
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
        # The 68 are not one group. A traditional meter CANNOT report half-hourly; a smart meter
        # can and simply is not being read that way, which is a consent/read-frequency fact, not
        # a metering-estate one. Split at the source so the page cannot re-merge them by accident.
        "smart_meter_but_no_hh_reads": smart_without,
        "counts": {
            "with_hh_reads": len(accounts),
            "smart_without_hh_reads": len(smart_without),
            "without_smart_meter": len(without) - len(smart_without),
            "households": len(accounts) + len(without),
        },
        # THE FAIL-SILENT GUARD for `_HALF_HOURLY_CAPABLE_METERS`. An unrecognised meter type is
        # counted as not-smart, which is the safe direction for the published claim but is also
        # invisible -- a whole new metering class could arrive and the smart-but-unread count
        # would simply stay flat. Publishing every value the book actually carried makes that
        # arrival readable, and `test_explore_hh_day.py` asserts each one is classified.
        "meter_types_seen": sorted({
            str((details.get(a) or {}).get("meter_type"))
            for a in (
                [r["account_id"] for r in without]
                + [v["account_id"] for v in accounts.values()]
            )
        }),
        # Said here rather than hard-coded in the page, so the sentence a reader meets moves
        # with the book instead of going stale the first time a meter is upgraded.
        "coverage_statement": _coverage_statement(
            with_reads=len(accounts),
            smart_without=len(smart_without),
            households=len(accounts) + len(without),
        ),
    }


def _coverage_statement(*, with_reads: int, smart_without: int, households: int) -> str:
    """The sentence a reader meets, and the reason it is assembled rather than formatted.

    The smart-but-unread clause must DISAPPEAR when that count is zero rather than render as
    "0 of them", because a sentence carrying a zero reads as a caveat about nothing and trains
    the reader to skip the clause on the day it is not zero.
    """
    head = (
        "{n} of {t} households on this book have a half-hourly read record, so a real day can "
        "be drawn for them. The rest report a handful of readings a year -- the curve for those "
        "homes is inferred from a profile, not measured."
    ).format(n=with_reads, t=households)
    if not smart_without:
        return head
    return head + (
        " {s} of them have a SMART METER and still no half-hourly reads: the meter can measure "
        "every half-hour, but read frequency is the customer's consent to give, and without it "
        "the supplier holds monthly figures from a meter capable of 17,520 a year."
    ).format(s=smart_without)


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
