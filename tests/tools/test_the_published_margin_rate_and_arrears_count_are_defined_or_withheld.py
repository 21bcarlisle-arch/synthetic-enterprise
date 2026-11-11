"""The two figures the 2026-11-11 Expert Hour re-read as wrong, checked on the committed feeds.

THE DEFECT. `site/data/dashboard.json` published a net margin rate of 54.91% for 2023: the
settlement P&L's net (no cost to serve) over the bill ledger's revenue, two books. And
`site/data/company.json` published 705 of 1,293 accounts "in arrears" on billed-minus-banked, which
counts the GBP 400 EBSS credit the government paid as the household's debt; on Ofgem's definition
the same ledger holds 50.

KEYED TO THE PROPERTY, NOT TODAY'S ANSWER. The margin control does not require the rate to stay
withheld: a rate may come back, but only beside a definition and inside the published plausibility
band `tools.generate_world_data` already cites. The arrears control recounts the ledger the feed
was built from, independently of the producer, and refuses a count larger than the accounts that
really hold a bill owed past Ofgem's 91 days.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from tools.generate_world_data import _MARGIN_AMBER_HI_PCT, _MARGIN_AMBER_LO_PCT

ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / "site" / "data" / "dashboard.json"
COMPANY = ROOT / "site" / "data" / "company.json"
LEDGER = ROOT / "docs" / "state" / "billing_ledger.json"


def _json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _rates(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "net_margin_pct":
                yield path + "." + k, v
            else:
                yield from _rates(v, path + "." + k)
    elif isinstance(node, list):
        for v in node:
            yield from _rates(v, path + "[]")


def margin_rate_violations(dashboard: dict) -> list[str]:
    status = (dashboard.get("financial") or {}).get("net_margin_pct_status") or {}
    bad = []
    for where, v in _rates(dashboard):
        if v is None:
            if not (status.get("withheld") and status.get("reason")):
                bad.append(f"{where}: blank with no withheld reason on financial.net_margin_pct_status")
        elif not status.get("definition"):
            bad.append(f"{where} = {v}: a rate with no definition on financial.net_margin_pct_status")
        elif not (_MARGIN_AMBER_LO_PCT <= v <= _MARGIN_AMBER_HI_PCT):
            bad.append(f"{where} = {v}: outside the published band "
                       f"[{_MARGIN_AMBER_LO_PCT}, {_MARGIN_AMBER_HI_PCT}]")
    return bad


def test_every_published_net_margin_rate_is_defined_and_plausible_or_withheld_with_a_reason():
    bad = margin_rate_violations(_json(DASHBOARD))
    assert not bad, f"{len(bad)} published net margin rate(s) fail:\n" + "\n".join(bad[:12])


def accounts_owing_past_91_days(ledger: dict) -> int:
    custs = ledger["customers"].values()
    as_of = max(i["issue_date"] for c in custs for i in c.get("invoices") or [])
    cut = date.fromisoformat(as_of) - timedelta(days=91)
    return sum(
        1 for c in custs
        if any((i.get("outstanding_gbp") or 0) > 0.005 and date.fromisoformat(i["due_date"]) < cut
               for i in c.get("invoices") or [])
    )


def arrears_violations(arrears: dict, ledger: dict) -> list[str]:
    bad = []
    if "91 days" not in (arrears.get("definition") or ""):
        bad.append(f"no Ofgem 91-day definition on the block (clock={arrears.get('clock')!r})")
    owing = accounts_owing_past_91_days(ledger)
    if arrears.get("in_arrears", 0) > owing:
        bad.append(f"in_arrears={arrears.get('in_arrears')} exceeds the {owing} ledger accounts "
                   "holding a bill owed more than 91 days past due")
    return bad


def test_the_published_arrears_count_is_ofgems_and_never_exceeds_the_ledgers_overdue_accounts():
    arrears = _json(COMPANY)["arrears"]
    assert arrears.get("available") is True, "the arrears block reads unavailable"
    bad = arrears_violations(arrears, _json(LEDGER))
    assert not bad, "\n".join(bad)


def test_both_controls_can_fail():
    """Each control refuses the shape the Expert Hour found, and passes a sound one."""
    assert margin_rate_violations({"financial": {"annual": [{"net_margin_pct": 54.91}]}})
    assert margin_rate_violations({"financial": {"annual": [{"net_margin_pct": None}]}})
    assert not margin_rate_violations({"financial": {
        "annual": [{"net_margin_pct": 2.1}], "net_margin_pct_status": {"definition": "d"}}})
    ledger = {"customers": {"A": {"invoices": [
        {"issue_date": "2023-06-30", "due_date": "2023-01-15", "outstanding_gbp": 0.0}]}}}
    assert arrears_violations({"in_arrears": 1, "definition": "more than 91 days"}, ledger)
    assert arrears_violations({"in_arrears": 0, "clock": "billed_minus_banked"}, ledger)
    assert not arrears_violations({"in_arrears": 0, "definition": "more than 91 days"}, ledger)
