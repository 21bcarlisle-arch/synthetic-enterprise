"""The curtained validator prices each period at the TARIFF, not at the rate the bill printed.

e88b13b23 rebuilt every period of the 4ae8da9b0f book (0 of 52,782 differ), but with the printed
rate, which `generate_billing_ledger` fits to each printed line: that proves the arithmetic and
cannot see a bill charging the wrong tariff. `unit_charge_at_contract` prices the volume at the
term record's all-in rate (`account_state_log`, exported as `contracted_terms`), and the comparison
sets it against energy + network and policy + the EPG receipt.

Measured 2026-10-26 on that book, regenerated: 49,865 agree, 2,915 cross a price change and sit
inside the covering terms' rates, and 2 disagreed. The 2 were one-day ToU stubs printed "Anytime" at
the off-peak rate, and the ledger now prints that band's label.
docs/staging/SEAT_FINDING_THE_PRINTED_RATE_AGAINST_THE_CONTRACTED_TARIFF_2026-10-26.md.
"""
from __future__ import annotations

import json

import pytest

from tools import bill_validation_comparison as cmp
from tools import independent_bill_validator as v


def _term(rate, start="2023-01-01", end="2023-04-01", tariff="svt", pair=None):
    return {"tariff_effective_from": start, "tariff_effective_to": end, "tariff_type": tariff,
            "unit_rate_p_per_kwh": rate,
            "tou_unit_rates": None if pair is None else [
                {"register_label": "Peak", "unit_rate_p_per_kwh": pair[0]},
                {"register_label": "Off-peak", "unit_rate_p_per_kwh": pair[1]}]}


def _single(terms, opening=1000.0, closing=1346.4):
    return {"period_start": "2023-01-01", "period_end": "2023-01-31", "days_in_period": 31,
            "commodity": "electricity", "unit_rate_p_per_kwh": 24.37,
            "standing_charge_gbp_per_day": 0.5, "volume_basis": "reads",
            "reads": [{"register_id": "1", "register_label": "Anytime", "read_kwh": opening},
                      {"register_id": "1", "register_label": "Anytime", "read_kwh": closing}],
            "contracted_terms": terms}


def _tou(terms):
    return {"period_start": "2023-01-01", "period_end": "2023-01-31", "days_in_period": 31,
            "commodity": "electricity", "unit_rate_p_per_kwh": None,
            "standing_charge_gbp_per_day": 0.192, "volume_basis": "reads",
            "reads": [{"register_id": "1", "read_kwh": 0.0}, {"register_id": "1", "read_kwh": 30.0},
                      {"register_id": "2", "read_kwh": 0.0}, {"register_id": "2", "read_kwh": 70.0}],
            "registers": [{"register_id": "1", "register_label": "Peak", "unit_rate_p_per_kwh": 1.0},
                          {"register_id": "2", "register_label": "Off-peak",
                           "unit_rate_p_per_kwh": 1.0}],
            "contracted_terms": terms}


def _issued(energy, net, epg=0.0):
    return {"period_start": "2023-01-01", "period_end": "2023-01-31",
            "lines": [{"label": "Energy", "amount_gbp": energy,
                       "inputs": {"consumption_kwh": 346.4}},
                      {"label": "Standing charge", "amount_gbp": 15.5},
                      {"label": "Network and policy costs", "amount_gbp": net}],
            "hmt_epg_receipt_gbp": epg}


def _verdict(period, issued):
    built = v.rebuild_period(period, segment="resi")
    claims = cmp.compare_bill(built, issued, statutory_vat={}, read_volume_kwh=None)
    return next(c for c in claims if c["claim"] == "unit_charge_at_contract_gbp")


def test_every_verdict_can_be_reached():
    """THE PARTITION, asserted whole: a check that only ever agreed, or only ever refused, passes
    every leg test below. SYN-2016-383, Jan 2023: 346.31 kWh at the 64.2571p SVT, carved into
    84.43 energy + 27.70 levy + 110.39 EPG, printed at 346.4 kWh."""
    exact = _single([_term(64.2571)])
    seen = {
        _verdict(exact, _issued(84.43, 27.70, 110.39))["verdict"],
        _verdict(exact, _issued(85.43, 27.70, 110.39))["verdict"],
        _verdict(_single([_term(64.2571), _term(48.1905, start="2023-01-20")]),
                 _issued(70.00, 27.70, 80.00))["verdict"],
        _verdict(_single(None), _issued(84.43, 27.70, 110.39))["verdict"],
    }
    assert seen == {cmp.AGREED, cmp.DISAGREED, cmp.BOUNDED, cmp.UNCHECKABLE}


def test_the_printed_rate_does_not_enter_the_check():
    """MUTATION: price with the period's printed `unit_rate_p_per_kwh` (24.37p here, the fitted
    energy-only rate) instead of the term record and the exact bill disagrees."""
    p = _single([_term(64.2571)])
    line = v.unit_charge_at_contract(p)
    assert line["status"] == v.CONTRACT_CHECKED
    assert line["amount_gbp"] == pytest.approx(346.4 * 0.642571, abs=0.005)
    p["unit_rate_p_per_kwh"] = 99.0
    assert v.unit_charge_at_contract(p)["amount_gbp"] == line["amount_gbp"]


def test_a_one_percent_wrong_tariff_disagrees_on_an_ordinary_bill():
    """The tolerance is print rounding (0.1 kWh a register, half a penny a line), not a margin a
    mischarge can hide in: 1% of this bill is GBP 2.23 against a GBP 0.08 tolerance."""
    p = _single([_term(64.2571 * 1.01)])
    assert _verdict(p, _issued(84.43, 27.70, 110.39))["verdict"] == cmp.DISAGREED
    assert v.unit_charge_at_contract(p)["tolerance_gbp"] < 0.1


def test_each_register_is_priced_at_its_own_band_of_the_contracted_pair():
    """30 kWh Peak at 30p + 70 kWh Off-peak at 15p = 9.00 + 10.50.

    MUTATION: swap the bands (peak kWh at the off-peak rate) and the charge moves to 15.00 and
    disagrees; drop the pair and the flat 20p gives 20.00, which also disagrees."""
    tou = [_term(20.0, tariff="fixed", pair=(30.0, 15.0))]
    assert v.unit_charge_at_contract(_tou(tou))["amount_gbp"] == pytest.approx(19.50)
    assert _verdict(_tou(tou), _issued(15.00, 4.50))["verdict"] == cmp.AGREED
    assert _verdict(_tou(tou), _issued(10.50, 4.50))["verdict"] == cmp.DISAGREED
    assert _verdict(_tou([_term(20.0, tariff="fixed")]), _issued(15.00, 4.50))["verdict"] == \
        cmp.DISAGREED


def test_a_bill_across_a_price_change_is_bounded_by_every_rate_its_terms_carry():
    """SYN-2016-093, Feb 2017: a ToU fix ending on the 28th, then the SVT. The one printed register
    charged 10.57p against flats of 11.16p and 13.49p, which a flat-rate bound refused (30 of
    2,915 on the first measure); the fix's off-peak rate (8.77p) is inside the true range.

    MUTATION: bound on the flat rates alone and this agrees no longer."""
    terms = [_term(11.163, "2016-02-29", "2017-02-28", "fixed", pair=(16.745, 8.770)),
             _term(13.492, "2017-02-28", "2017-04-01")]
    p = _single(terms, opening=0.0, closing=458.3)
    assert _verdict(p, _issued(30.00, 18.45))["verdict"] == cmp.BOUNDED
    assert _verdict(p, _issued(39.00, 18.45))["verdict"] == cmp.BOUNDED
    assert _verdict(p, _issued(80.00, 18.45))["verdict"] == cmp.DISAGREED
    assert _verdict(p, _issued(20.00, 18.45))["verdict"] == cmp.DISAGREED


def test_a_term_sold_at_no_single_rate_is_uncheckable_and_says_so():
    line = v.unit_charge_at_contract(_single([_term(None, tariff="pass_through")]))
    assert line["status"] == v.UNCHECKABLE and "pass_through" in line["why"]
    assert v.unit_charge_at_contract(_single([]))["status"] == v.UNCHECKABLE


def test_the_ledger_takes_the_rate_from_the_term_record_and_the_pair_only_where_settled_as_tou():
    from tools.generate_billing_ledger import _contracted_terms, _tou_terms

    terms = {"A": [{"term_start": "2023-01-01", "term_end": "2023-04-01", "tariff_type": "fixed",
                    "unit_rate_gbp_per_mwh": 200.0},
                   {"term_start": "2023-04-01", "term_end": "2023-07-01", "tariff_type": "svt",
                    "unit_rate_gbp_per_mwh": 300.0}]}
    flat_bill = {"customer_id": "A", "period_start": "2023-02-01", "period_end": "2023-02-28",
                 "average_unit_rate_gbp_per_mwh": 999.0}
    out = _contracted_terms(terms, flat_bill, _tou_terms(terms, [flat_bill]))
    assert [t["unit_rate_p_per_kwh"] for t in out] == [20.0]
    assert out[0]["tou_unit_rates"] is None
    tou_bill = dict(flat_bill, registers=[{"band": "peak"}, {"band": "offpeak"}])
    out = _contracted_terms(terms, tou_bill, _tou_terms(terms, [tou_bill]))
    assert [b["unit_rate_p_per_kwh"] for b in out[0]["tou_unit_rates"]] == \
        pytest.approx([30.0, 15.714], abs=0.001)
    across = dict(flat_bill, period_start="2023-03-15", period_end="2023-04-14")
    assert [t["tariff_type"] for t in _contracted_terms(terms, across, set())] == ["fixed", "svt"]


def test_the_raw_export_carries_the_contracted_terms_and_nothing_derived():
    from company.billing import raw_account_export as rx

    inv = {"period_start": "2023-01-01", "period_end": "2023-01-31", "opening_read_kwh": 0.0,
           "closing_read_kwh": 10.0, "registers": [{"register_id": "1", "label": "Anytime"}],
           "contracted_terms": [_term(20.0, tariff="fixed", pair=(30.0, 15.0))]}
    raw = rx.raw_account("A", {"invoices": [inv]})
    assert raw["periods"][0]["contracted_terms"] == inv["contracted_terms"]
    assert rx.derived_leaks(raw) == []


def test_the_published_book_charges_its_contracted_tariff():
    """On the real ledger: no period disagrees with the tariff it was sold at. A ledger that
    predates the export carries no `contracted_terms` and is named, not passed."""
    from company.billing import raw_account_export as rx

    if not rx.LEDGER_PATH.exists():
        pytest.skip("no billing ledger on this box")
    ledger = json.loads(rx.LEDGER_PATH.read_text())
    customers = ledger.get("customers") or {}
    first = next((i for r in customers.values() for i in r.get("invoices") or []), {})
    if "contracted_terms" not in first:
        pytest.skip("the ledger at {} predates contracted_terms; it turns live at the next "
                    "publish".format(rx.LEDGER_PATH))
    counts, differ = {}, []
    for cid, rec in customers.items():
        for bill in cmp.compare_account(cid, rec)["bills"]:
            for c in bill["claims"]:
                if c["claim"] != "unit_charge_at_contract_gbp":
                    continue
                counts[c["verdict"]] = counts.get(c["verdict"], 0) + 1
                if c["verdict"] == cmp.DISAGREED:
                    differ.append((cid, bill.get("period_start"), c.get("difference")))
    assert sum(counts.values()) == ledger["meta"]["invoice_count"]
    assert counts.get(cmp.AGREED), counts
    assert not differ, "{} disagree with the contracted tariff: {}".format(len(differ), differ[:5])
