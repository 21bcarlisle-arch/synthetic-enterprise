"""Which collections-desk cures were declared while the household's BILLING ACCOUNT still owed a bill past due.

The desk works one journey per billing account (`company.interfaces.dd_review_outcome.billing_account_of`:
both fuels of a home bill under one account, SLC 27.8D set-off), so the
reader grades it on the same account. The scratch reader this replaces (`/var/tmp/ld71`'s
`split.py`) clamped each LEVEL leg at zero before summing, so one fuel's credit never met the other
fuel's debt, while it netted OFF-level legs. That held 35 of 71 cures on the 87e00e1458 book that the
account itself does not owe (docs/design/LEVEL_DD_AREA_MAP_2026-11-11.md s.7, cause A).

One rule for every leg, at the cure date d:
  past_due(leg) = page running balance at d, less bills issued but not yet due at d (signed: credit < 0).
  A bill paid by direct debit is due on its next Bacs day when its due date is not one.
  A leg paying by level DD at d cannot owe more than its schedule shortfall (Ofgem 20 Sep 2011
  App. 2 para 2.8): leg = min(past_due, max(0, requested_to_d - received_to_d)). A level leg ahead of
  its schedule therefore owes 0 but its CREDIT still counts.
  account owed = sum over the account's legs. A cure is held when account owed > 0.005.

Usage: python3 -m tools.level_dd_cure_reader <ledger.json> [--legacy]
  ledger.json is `tools.generate_billing_ledger.generate(run_json, out)`'s output for the book.
  --legacy reproduces the scratch per-leg-clamp rule, kept only so a grade can show the difference.
Reads the page ledger (P) only; it moves nothing the household or the run sees.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import datetime as dt  # noqa: E402

from company.billing.collections_journey import last_day_to_pay  # noqa: E402
from company.interfaces.dd_review_outcome import billing_account_of  # noqa: E402
from tools.generate_payment_ledger_data import _book_as_of_date, build_account_ledger  # noqa: E402


def _last_day(invoice: dict, by_dd: set) -> str:
    """The last day `invoice` can be paid on time, as the desk reads it: a direct debit due on a
    weekend or bank holiday is collected, on time, the next Bacs day (`last_day_to_pay`). Read from
    the due date alone, SYN-2016-015g's gas bill due Saturday 14 Apr 2018 and collected Monday 16
    Apr held the desk's Sunday cure at GBP 71.37 (LEVEL_DD map s.9.4)."""
    due = invoice.get("due_date")
    if not due:
        return ""
    return last_day_to_pay(dt.date.fromisoformat(due),
                           by_direct_debit=invoice["invoice_number"] in by_dd).isoformat()


def leg_position(entries: list[dict], customer: dict, d: str) -> tuple[float, bool]:
    """(what this leg contributes to the account at d, whether it pays by level DD at d)."""
    rows = [e for e in entries if e["date"] <= d]
    by_dd = {p["invoice_number"] for p in customer["payments"] if p.get("method") == "direct_debit"}
    not_yet_due = sum(
        max(i["total_amount_gbp"], 0.0)
        for i in customer["invoices"]
        if not i.get("billed_to") and i["issue_date"] <= d and _last_day(i, by_dd) > d
    )
    past_due = (rows[-1]["running_balance_gbp"] if rows else 0.0) - not_yet_due
    known = [p for p in customer["payments"] if p["payment_date"] <= d]
    if not (known and max(known, key=lambda p: p["payment_date"]).get("level_dd")):
        return past_due, False
    pays = {p["invoice_number"]: p for p in customer["payments"]}
    requested = 0.0
    for i in customer["invoices"]:
        if i.get("billed_to"):
            continue
        p = pays.get(i["invoice_number"])
        if p and p.get("level_dd"):
            requested += p["amount_gbp"] if p["payment_date"] <= d else 0.0
        elif (i.get("due_date") or "9") <= d:
            requested += i["total_amount_gbp"] - (i.get("deemed_share_gbp") or 0.0)
    received = -sum(e["amount_gbp"] for e in rows if e["type"] in ("payment_received", "arrears_resolved"))
    return min(past_due, max(0.0, requested - received)), True


def account_owed(parts: list[tuple[float, bool]], legacy: bool = False) -> float:
    """What the billing account owes past due, from its legs' `leg_position`s. `legacy` is the
    scratch rule (level legs clamped at zero per leg, off-level legs netted), kept for comparison."""
    if legacy and any(lv for _, lv in parts):
        return sum(max(x, 0.0) if lv else x for x, lv in parts)
    return sum(x for x, _ in parts)


def read(customers: dict, legacy: bool = False) -> dict:
    as_of = _book_as_of_date(customers)
    legs: dict[str, list] = defaultdict(list)
    journeys: dict = {}
    for cid, c in customers.items():
        legs[billing_account_of(cid)].append((cid, build_account_ledger(c, as_of)["entries"], c))
        for j in c.get("collections_desk_journeys") or []:
            journeys[(j["account_id"], j["stages"][0]["on"])] = j
    cured, held = 0, []
    for (acc, _), j in sorted(journeys.items()):
        if j.get("exit") != "cured":
            continue
        cured += 1
        d = [s for s in j["stages"] if s["stage"] == "cured"][-1]["on"]
        account_legs = legs.get(acc.removeprefix("ACC-"), [])
        if not account_legs:
            raise SystemExit(f"journey {acc} {d}: no leg bills under billing account {acc} -- the desk and the page disagree on the account")
        parts = [leg_position(e, c, d) for _, e, c in account_legs]
        owed = account_owed(parts, legacy)
        if owed > 0.005:
            held.append({"account": acc, "cured_on": d, "owed_gbp": round(owed, 2),
                         "legs": [[cid, round(x, 2), lv] for (cid, _, _), (x, lv) in zip(account_legs, parts)]})
    return {"rule": "legacy per-leg clamp" if legacy else "billing account, one netting rule",
            "cured": cured, "held": len(held), "accounts": len({h["account"] for h in held}),
            "level_at_cure": sum(1 for h in held if any(lv for _, _, lv in h["legs"])), "holds": held}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ledger")
    ap.add_argument("--legacy", action="store_true")
    ap.add_argument("--json", action="store_true", help="print the whole result as JSON")
    a = ap.parse_args(argv)
    out = read(json.loads(Path(a.ledger).read_text())["customers"], legacy=a.legacy)
    if a.json:
        print(json.dumps(out, indent=1))
        return 0
    print(f"[{out['rule']}] cured {out['cured']}; held over a bill owed past due: {out['held']} on "
          f"{out['accounts']} accounts; level at cure: {out['level_at_cure']}")
    for h in out["holds"]:
        print(h["account"], h["cured_on"], h["owed_gbp"], h["legs"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
