#!/usr/bin/env python3
"""A half-hourly computation may not be added downstream of the settlement fold.

THE DIRECTOR'S CONSTRAINT, 2026-08-24, and it outranks the memory saving it bounds:

    "GB settlement is half-hourly and that is not an implementation detail, it is the market.
     So the half-hourly spine stays half-hourly. Aggregate in the reporting and ledger layers
     if that's where the memory goes, but the settlement and metering record keeps its grain.
     And put a control on it that fails if anything half-hourly-dependent is added while the
     fold is live, so this can't be discovered later by a tariff that silently can't be priced."

WHERE THE LINE IS, stated so this control's subject is unambiguous.

  THE SPINE — untouched, and it must stay that way. `simulation/hedged_settlement.py` loops
  `for period in range(1, 49)`, picks the rate for THAT half-hour
  (`period_rate = peak_rate if is_peak_period(date, period) else offpeak_rate`) and settles it
  against that period's real System Sell Price. The metering record (`sim/hh_data/*.csv`, the
  company's `consumption_feed.json`) is half-hourly. `company/market/imbalance_ledger.py` keeps
  its own per-period records. None of that is folded and none of it is this control's business.

  THE RETAINED BOOK — `run_phase2b`'s `all_records`, which is what survives settlement and is
  handed to the reporting and ledger layers. `simulation/settlement_daily.py` folds THIS to
  daily rows, and only this.

WHY THE CONTROL IS NOT PARANOIA. The class it guards already existed, four times, before the
fold was written — and every instance was found by diffing a generated report, not by reading:

  * the peak/off-peak split, re-derived from the retained book with the COMPANY's band;
  * the worst settlement period of each year, a `min` over the retained book;
  * the treasury path, a re-sort of the retained book by (date, period);
  * Triad exposure, a lookup into the retained book by (date, period).

Each is now a REGISTER folded during settlement, where the half-hours still exist. A fifth
would land silently, and the director's own example — a tariff that cannot be priced — is
exactly what that looks like from the outside.

HOW IT FAILS, AND WHAT IT DOES NOT DO. This is a RATCHET over the modules that consume the
retained book: the known half-hourly reads are frozen, a NEW one FAILS, and a frozen entry that
has gone FAILS too, so the census can only shrink or be deliberately re-frozen. It does NOT try
to decide whether a given read is legitimate — a fallback for a pre-fold record is a read, and
so is a defect. What it guarantees is that no such read arrives without someone looking at it
and saying which it is.

FAIL-CLOSED (R15): a scan that reads nothing RAISES rather than reporting a clean tree, because
an under-reporting census authorises exactly what it exists to prevent.

    python3 -m tools.half_hourly_dependency_ratchet            # check
    python3 -m tools.half_hourly_dependency_ratchet --freeze   # re-record, deliberately
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
BASELINE = PROJECT / "docs" / "design" / "half_hourly_dependency_baseline.json"

#: The modules that consume the RETAINED settlement book. The spine is deliberately absent:
#: `hedged_settlement`, `hh_consumption`, `imbalance_ledger` and the meter-read path are
#: half-hourly BY DESIGN and folding never reaches them, so scanning them would be counting
#: the thing the constraint exists to protect.
CONSUMERS = (
    "saas/reporting/annual_report.py",
    "saas/reporting/segment_report.py",
    "simulation/run_phase4c_on_phase2b.py",
    "saas/cost_to_serve.py",
    "saas/ledger.py",
    "company/crm/tpi_commission_desk.py",
    "company/regulatory/statutory_obligations.py",
    "company/finance/accounting_close.py",
    "company/crm/customer_profitability.py",
    "company/billing/monthly_bill_assembly.py",
    "saas/bill_generator.py",
)

#: What makes a line half-hourly-DEPENDENT. Deliberately literal: these are the names by which
#: a half-hour is reachable at all, so a read that avoids every one of them is not reading one.
MARKERS = ("settlement_period", "is_peak_period", "settlement_periods_folded")


class ScanUnavailable(RuntimeError):
    """The census could not be taken. NOT a pass -- an unavailable check is a FAILED check."""


def scan(root: Path | None = None) -> dict[str, list[str]]:
    """`{module: [normalised source line, ...]}` for every half-hourly read in a consumer."""
    root = root or PROJECT
    found: dict[str, list[str]] = {}
    seen_any_file = False
    for rel in CONSUMERS:
        path = root / rel
        if not path.is_file():
            continue
        seen_any_file = True
        hits = []
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith("#") or not any(m in line for m in MARKERS):
                continue
            # Normalised so reformatting is not a diff, but a changed EXPRESSION is.
            hits.append(re.sub(r"\s+", " ", line))
        if hits:
            found[rel] = sorted(hits)
    if not seen_any_file:
        raise ScanUnavailable(
            "none of the {} consumer modules could be read under {} -- refusing to report a "
            "clean census rather than certify a tree this never looked at".format(
                len(CONSUMERS), root))
    return found


def load_baseline(path: Path | None = None) -> dict:
    p = path or BASELINE
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ScanUnavailable(
            "the baseline at {} is missing or unreadable ({}). A ratchet with no floor cannot "
            "fail, and a control that cannot fail is worse than none (R15).".format(p, exc)
        ) from exc


def diff(current: dict[str, list[str]], baseline: dict) -> tuple[list[str], list[str]]:
    frozen = baseline.get("reads") or {}
    added, gone = [], []
    for module in sorted(set(current) | set(frozen)):
        now = set(current.get(module, []))
        was = set(frozen.get(module, []))
        added += ["{}: {}".format(module, line) for line in sorted(now - was)]
        gone += ["{}: {}".format(module, line) for line in sorted(was - now)]
    return added, gone


def freeze(root: Path | None = None, path: Path | None = None) -> dict:
    data = {
        "_doc": ("Half-hourly reads of the RETAINED settlement book, frozen. The spine "
                 "(hedged_settlement, hh_consumption, imbalance_ledger, the meter-read path) "
                 "is half-hourly by design and deliberately NOT scanned. See "
                 "tools/half_hourly_dependency_ratchet.py."),
        "reads": scan(root),
    }
    dest = path or BASELINE
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--freeze", action="store_true",
                    help="re-record the census from the current tree, deliberately")
    args = ap.parse_args(argv)

    if args.freeze:
        data = freeze()
        total = sum(len(v) for v in data["reads"].values())
        print("half-hourly-dependency: froze {} read(s) across {} module(s) -> {}".format(
            total, len(data["reads"]), BASELINE))
        return 0

    current = scan()
    added, gone = diff(current, load_baseline())
    if not added and not gone:
        total = sum(len(v) for v in current.values())
        print("half-hourly-dependency: {} known read(s) of the retained book, unchanged."
              .format(total))
        return 0

    if added:
        print("half-hourly-dependency: A NEW HALF-HOURLY READ OF THE RETAINED BOOK.\n")
        for line in added:
            print("  {}".format(line))
        print("""
The retained settlement book is folded to DAILY rows by simulation/settlement_daily.py. A
computation here that needs the half-hour will get a day, and will be wrong in a way that
looks like an answer -- which is how a tariff that cannot be priced gets discovered by a
customer rather than by a test.

Two legitimate answers, and a third that is not:
  * COMPUTE IT DURING SETTLEMENT, where the half-hours still exist, and carry the result
    forward as a register -- the four existing ones are in settlement_daily.PeriodRegisters.
  * READ THE SPINE instead: hedged_settlement's own records, sim/hh_data, the consumption
    feed, or company/market/imbalance_ledger -- none of which is folded.
  * Not: read it off the retained book and hope the fold is never wired.

If the read is deliberate and correct, record it with
`python3 -m tools.half_hourly_dependency_ratchet --freeze` in the SAME commit, so the
decision is on the record instead of in someone's head.""")
    if gone:
        print("\nhalf-hourly-dependency: {} frozen read(s) are gone -- re-freeze to lower the "
              "floor:".format(len(gone)))
        for line in gone:
            print("  {}".format(line))
    return 1


if __name__ == "__main__":
    sys.exit(main())
