"""INV_HOUSEHOLD_PAGE_NARRATED_FACT_IS_TRUE_OF_THE_ACCOUNT (N28): a sentence the Explore cast narrates
is derived from the fields the page prints, or withheld.

The fixture is the 6fe7827ab2 book's published pages (e816040ce8), cut to the three slots the tenth and
eleventh cold reads named: the EV home told "Your first electricity bill is ready" six years in (O23),
the 2022 shock's "use did not explain the change" over a 29% rise in use (O6), and the mover's GBP
916.14, the catch-up line before VAT, printed inside a VAT-inclusive total (O28).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from company.compliance.domain_invariants import (
    bill_change_split,
    catchup_on_the_bills_basis,
    narrated_fact_breaches,
    use_did_not_explain_is_true,
)
from tools import generate_explore_cast as g

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "n28_narrated_facts_on_the_6fe7827ab2_pages.json"
SLOTS = {s["id"]: s for s in json.loads(FIXTURE.read_text())["slots"]}


@pytest.mark.parametrize("slot, leg", [("ev", "first_bill"), ("shock_2022", "use_did_not_explain"),
                                       ("mover", "catchup_basis")])
def test_the_published_6fe7827ab2_pages_red_on_each_named_slot(slot, leg):
    s = SLOTS[slot]
    assert any(b["leg"] == leg for b in narrated_fact_breaches(s["moments"], s["invoices"]))


def _ev(slot):
    return {"invoice": [{**i, "fuel": i["commodity"]} for i in SLOTS[slot]["invoices"]]}


def test_the_ev_homes_bill_after_the_car_is_not_narrated_as_its_first():
    ev = _ev("ev")
    later = next(i for i in ev["invoice"] if i["date"] == "2023-06-30")
    first = next(i for i in ev["invoice"] if i["date"] == "2017-06-30")
    # Both sides of the branch: the true first bill is still called first.
    assert g._is_first_bill(ev, first) and not g._is_first_bill(ev, later)
    title, story, msg, why, _ = g._template({"legs": {"electricity": {}}}, ev, later["date"], "first_bill", later)
    moment = {"iso": later["date"], "story": story, "why": why, "portal_message": msg}
    assert narrated_fact_breaches([moment], ev["invoice"]) == []
    assert "first" not in msg.lower()


def test_the_shock_cause_is_the_split_of_its_two_bills():
    bills = {i["date"][:7]: i for i in SLOTS["shock_2022"]["invoices"]}
    split = bill_change_split(bills["2021-12"], bills["2022-12"])
    assert split["use_change"] == pytest.approx(0.291, abs=0.001)
    assert split["use_part_gbp"] + split["price_part_gbp"] == pytest.approx(split["change_gbp"], abs=0.01)
    assert use_did_not_explain_is_true(split) is False
    msg, why = g._shock_cause({"before_bill": bills["2021-12"], "now_bill": bills["2022-12"]})
    moment = {"iso": "2022-12-31", "story": "The electricity bill for December 2022", "why": why, "portal_message": msg}
    assert narrated_fact_breaches([moment], SLOTS["shock_2022"]["invoices"]) == []


def test_each_verdict_of_the_use_claim_can_be_reached():
    before = {"read_type": "A", "consumption_kwh": 1000, "commodity_amount_gbp": 100,
              "non_commodity_amount_gbp": 50, "standing_charge_gbp": 10}
    price_only = {**before, "consumption_kwh": 1020, "commodity_amount_gbp": 306, "non_commodity_amount_gbp": 102}
    use_led = {**before, "consumption_kwh": 1400, "commodity_amount_gbp": 140, "non_commodity_amount_gbp": 70}
    estimated = {**price_only, "read_type": "E"}
    assert [use_did_not_explain_is_true(bill_change_split(before, b)) for b in (price_only, use_led, estimated)] \
        == [True, False, None]
    assert g._shock_cause({"before_bill": before, "now_bill": estimated})[1].startswith("One of the two bills is estimated")


def test_a_catch_up_figure_keeps_its_vat_basis():
    final = next(i for i in SLOTS["mover"]["invoices"] if i["date"] == "2024-11-22")
    assert "catchup_vat_gbp" not in final  # the page file that printed GBP 916.14
    # Without the line's VAT on the page, the figure is the line and says so.
    assert catchup_on_the_bills_basis(final) == (-916.14, "before VAT")
    text = g._bill_extras(final)
    assert "£916.14 credit before VAT" in text
    assert narrated_fact_breaches([{"iso": "2024-11-23", "story": text}], [final]) == []
    # With it (generate_invoice_data now carries it), the figure is what the total moved by.
    with_vat = {**final, "catchup_vat_gbp": -45.81}
    assert catchup_on_the_bills_basis(with_vat) == (-961.95, "")
    text = g._bill_extras(with_vat)
    assert "£961.95 credit correcting" in text
    assert narrated_fact_breaches([{"iso": "2024-11-23", "story": text}], [with_vat]) == []
    # The defect itself, once more: the line printed bare is red.
    bare = "including a £916.14 credit correcting the estimated bills"
    assert [b["leg"] for b in narrated_fact_breaches([{"iso": "2024-11-23", "story": bare}], [with_vat])] \
        == ["catchup_basis"]


def test_a_sentence_whose_bill_is_not_on_the_page_is_unread_not_passed():
    out = narrated_fact_breaches([{"iso": "2020-01-31", "portal_message": "Your first gas bill is ready: £1.00."}], [])
    assert [b["reason"] for b in out] == ["unread"]
