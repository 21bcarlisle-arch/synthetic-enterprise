"""The cast prints one figure per fact about a bill: its own scheme credit and its catch-up (N1).

Fourth cold read on the 209c3350ab book (2026-10-29), N1 open for the third read running:
- PROS-2019-0246, the 2022-shock slot: "£598.04 to pay" on 31 Dec 2022, under a story that names
  the bill's £67.00 Energy Bills Support Scheme credit. The ledger posts that credit against the
  bill (invoice 15907) on 3 Jan, the day it raises the bill, so `_owed` read the bill on its date
  and the credit three days later. The household paid £531.04.
- PROS-2017-0351, the mover slot: "The final bill: electricity £-24.73 for 146 kWh". The bill is a
  credit because it carries a £74.17 correction to the estimates of 1 May 2023 to 31 Oct 2024. The
  page's printed bill shows that as a line; the cast quoted the total alone.

The records below are those two bills as the 209c pages hold them, cut to the fields the cast reads.
With EXPLORE_PAGES_DIR set to a page book (the 209c rebuild is /var/tmp/fourth-read/tree/site/data),
the last test grades every household in it.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tools import generate_explore_cast as gen

PAGES = os.environ.get("EXPLORE_PAGES_DIR")


def _shock_ev():
    """PROS-2019-0246's Nov 2022 bill (paid) and Dec 2022 bill, with the ledger as it posted them."""
    nov = {"fuel": "electricity", "invoice_number": 15906, "date": "2022-11-30", "amount_gbp": 333.13,
           "scheme_credit_gbp": 66.0, "scheme_credit_applied_gbp": 66.0, "read_type": "A",
           "consumption_kwh": 937.0}
    dec = {"fuel": "electricity", "invoice_number": 15907, "date": "2022-12-31", "amount_gbp": 598.04,
           "scheme_credit_gbp": 67.0, "scheme_credit_applied_gbp": 67.0, "read_type": "A",
           "consumption_kwh": 1715.0}
    led = [
        {"fuel": "electricity", "date": "2022-12-01", "type": "invoice_raised", "invoice_number": 15906, "amount_gbp": 333.13},
        {"fuel": "electricity", "date": "2022-12-01", "type": "scheme_credit", "invoice_number": 15906, "amount_gbp": -66.0},
        {"fuel": "electricity", "date": "2022-12-17", "type": "payment_received", "invoice_number": 15906,
         "amount_gbp": -267.13, "method": "direct_debit"},
        {"fuel": "electricity", "date": "2023-01-03", "type": "invoice_raised", "invoice_number": 15907, "amount_gbp": 598.04},
        {"fuel": "electricity", "date": "2023-01-03", "type": "scheme_credit", "invoice_number": 15907, "amount_gbp": -67.0},
        {"fuel": "electricity", "date": "2023-01-17", "type": "payment_received", "invoice_number": 15907,
         "amount_gbp": -531.04, "method": "direct_debit"},
    ]
    return {"invoice": [nov, dec], "ledger": led, "timeline": [], "reaction": []}


def test_a_bill_is_owed_net_of_its_own_scheme_credit_from_the_day_it_is_dated():
    """Red on origin: "£598.04 to pay" on 31 Dec 2022. The credit is on the bill, so it comes off with
    it, and it is not counted twice once the ledger posts it."""
    ev = _shock_ev()
    for iso, want in (("2022-12-31", 531.04), ("2023-01-03", 531.04), ("2023-01-17", 0.0)):
        got, _ = gen._owed(gen._known_by(ev["invoice"], iso), gen._known_by(ev["ledger"], iso), ev["ledger"])
        assert round(got, 2) == want, (iso, got)
    hh = {"id": "PROS-2019-0246", "legs": {"electricity": {"acquisition_date": "2019-08-18"}}}
    assert gen._portal(hh, ev, "2022-12-31", "")["balance"] == "£531.04 to pay"


def test_the_printed_bill_line_names_the_credit_it_takes_off():
    """The portal's bill list printed "£598.04" for the December bill with no credit beside it."""
    ev = _shock_ev()
    hh = {"id": "PROS-2019-0246", "legs": {"electricity": {"acquisition_date": "2019-08-18"}}}
    dec = gen._portal(hh, ev, "2022-12-31", "")["bills"][0]
    assert dec["amount"] == "£598.04, less its £67.00 Energy Bills Support Scheme credit", dec


def test_the_final_bill_names_its_catch_up_and_prints_a_credit_as_a_credit():
    """Red on origin: "electricity £-24.73 for 146 kWh" with no word of the £74.17 correction."""
    final = {"fuel": "electricity", "date": "2024-11-22", "period_end": "2024-11-22", "amount_gbp": -24.73,
             "consumption_kwh": 145.7, "read_type": "A", "catchup_applied": True,
             "catchup_adjustment_gbp": -74.17, "catchup_period_start": "2023-05-01",
             "catchup_period_end": "2024-10-31"}
    mv = {"legs": [{"fuel": "electricity", "final": final, "basis": "closing read actual"}], "fuels": "electricity"}
    hh = {"id": "PROS-2017-0351", "legs": {"electricity": {}}}
    title, story, msg, _, _ = gen._template(hh, {}, "2024-11-23", "final_bill", mv)
    assert story == ("The final bill: electricity £24.73 credit for 146 kWh to 22 Nov 2024 (closing read actual), "
                     "including a £74.17 credit correcting the estimated bills from 1 May 2023 to 31 Oct 2024."), story
    assert msg == "Your final bill is ready: electricity £24.73 credit.", msg
    # Control: a bill with no catch-up and no credit says nothing more than it did.
    plain = {**final, "amount_gbp": 49.74, "catchup_applied": False, "catchup_adjustment_gbp": None}
    assert gen._bill_extras(plain) == ""


@pytest.mark.skipif(not PAGES, reason="EXPLORE_PAGES_DIR names no page book")
def test_every_cast_moment_on_a_page_book_prints_each_bill_with_its_credit_and_catch_up():
    """Over a whole book: every balance a moment prints is net of the bills' own posted credits, and
    every catch-up or credited bill in the portal's list says so. Both partitions must be reached."""
    customers = gen._load_customers(Path(PAGES) / "customers")
    sample = json.loads((Path(PAGES) / "customer_sample.json").read_text(encoding="utf-8"))
    feed = gen.build(customers, sample, gen._cap_windows())
    by_hh = {h["id"]: h for h in gen.households(customers)}
    seen = {"credit": 0, "catch_up": 0}
    wrong = []
    for s in feed["slots"]:
        hh = by_hh.get(s.get("household"))
        if not hh:
            continue
        ev = gen._events(hh)
        for m in s.get("moments", []):
            for b in (m.get("portal") or {}).get("bills") or []:
                inv = next((i for i in ev["invoice"] if gen._day(i["date"]) == b["when"] and i["fuel"] == b["fuel"]), None)
                if not inv:
                    continue
                if inv.get("scheme_credit_applied_gbp"):
                    seen["credit"] += 1
                    if "Energy Bills Support Scheme credit" not in b["amount"]:
                        wrong.append((s["id"], m["iso"], b))
                if inv.get("catchup_applied") and inv.get("catchup_adjustment_gbp"):
                    seen["catch_up"] += 1
                    if "correcting the estimated bills" not in b["amount"]:
                        wrong.append((s["id"], m["iso"], b))
    assert not wrong, wrong[:5]
    assert all(seen.values()), "a partition was never reached, so this sweep proves nothing: {}".format(seen)
