"""A bill across a price change prints a line per contracted rate, and the validator checks each.

8523e6025 found 2,915 of 52,782 periods of 4ae8da9b0f crossing a term change and printing one
blended rate that is neither contracted rate, so the curtained validator could only bound them.
SLC 22A.3 asks for the Unit Rate(s) wherever charges are displayed, and Ofgem's 2011 letter on
apportioning price increases asks that the higher price is paid only for units used after the
change (docs/market_research/tariffs_and_the_default_tariff_2026-10-25.md, "A bill across a price
change"). The biller now splits the period by the term each settled record carries, the ledger
prints the lines with their own readings, and the validator prices each line's advance at its own
term's rate: a CONTRACT_CHECK, not a range.

The chain is driven end to end here: `generate_bill` -> `_printed_rate_lines` -> the raw export ->
the curtained validator -> the comparison.
"""
from __future__ import annotations

import pytest

from company.billing import raw_account_export as rx
from saas.bill_generator import generate_bill
from tools import bill_validation_comparison as cmp
from tools import independent_bill_validator as v
from tools.generate_billing_ledger import _contracted_terms, _printed_rate_lines

SC = 0.53


def _rows(change_day: int, before: float, after: float) -> list[dict]:
    """March 2023 settled daily: the first term to the day before `change_day`, then the next."""
    rows = []
    for d in range(1, 32):
        rate = before if d < change_day else after
        kwh = 8.0 + d % 5
        rows.append({"customer_id": "C1", "settlement_date": "2023-03-%02d" % d,
                     "term_start": "2023-01-01" if d < change_day else "2023-03-%02d" % change_day,
                     "consumption_kwh": kwh, "revenue_gbp": kwh / 1000 * rate + SC,
                     "standing_charge_gbp": SC})
    return rows


def _terms(change_day: int, before: float, after: float) -> dict:
    return {"C1": [
        {"term_start": "2023-01-01", "term_end": "2023-03-%02d" % change_day, "tariff_type": "svt",
         "unit_rate_gbp_per_mwh": before},
        {"term_start": "2023-03-%02d" % change_day, "term_end": "2023-07-01", "tariff_type": "svt",
         "unit_rate_gbp_per_mwh": after}]}


def _invoice(bill: dict, account_terms: dict, opening: float = 1000.0) -> dict:
    """The ledger's printed invoice fields this chain reads, at print precision."""
    kwh = round(bill["total_consumption_kwh"], 1)
    energy = round(bill["commodity_amount_gbp"], 2)
    net = round(bill["non_commodity_amount_gbp"], 2)
    terms = _contracted_terms(account_terms, bill, set())
    inv = {"period_start": bill["period_start"], "period_end": bill["period_end"],
           "days_in_period": bill["days_in_period"], "commodity": "electricity",
           "consumption_kwh": kwh, "opening_read_kwh": opening,
           "closing_read_kwh": round(opening + kwh, 1), "read_type": "A",
           "registers": [{"register_id": "1", "label": "Anytime"}],
           "contracted_terms": terms, "commodity_amount_gbp": energy,
           "non_commodity_amount_gbp": net}
    lines = _printed_rate_lines(bill.get("rate_lines"), kwh, round(energy + net, 2), opening, "A",
                                terms)
    if lines is not None:
        inv["rate_lines"] = lines
    return inv


def _verdict(inv: dict) -> dict:
    period = rx.raw_account("C1", {"invoices": [inv]})["periods"][0]
    built = v.rebuild_period(period, segment="resi")
    issued = {"period_start": inv["period_start"], "period_end": inv["period_end"],
              "lines": [{"label": "Energy", "amount_gbp": inv["commodity_amount_gbp"],
                         "inputs": {"consumption_kwh": inv["consumption_kwh"]}},
                        {"label": "Network and policy costs",
                         "amount_gbp": inv["non_commodity_amount_gbp"]}]}
    claims = cmp.compare_bill(built, issued, statutory_vat={}, read_volume_kwh=None)
    return next(c for c in claims if c["claim"] == "unit_charge_at_contract_gbp")


def test_every_verdict_on_a_period_across_a_change_can_be_reached():
    """THE PARTITION, whole: agreed (lines printed, right rates), disagreed (lines printed, wrong
    charge), bounded (no lines: a ledger from before them) and uncheckable (a line naming no term).
    A check that only ever agreed, or only ever fell back to the bound, passes every leg below."""
    terms = _terms(20, 340.0, 267.0)
    bill = generate_bill("C1", _rows(20, 340.0, 267.0), "svt")
    agreed = _invoice(bill, terms)
    wrong = dict(agreed, commodity_amount_gbp=round(agreed["commodity_amount_gbp"] + 2.0, 2))
    unlined = {k: val for k, val in agreed.items() if k != "rate_lines"}
    orphan = dict(agreed, rate_lines=[dict(agreed["rate_lines"][0],
                                           tariff_effective_from="2022-12-25")]
                  + agreed["rate_lines"][1:])
    seen = {_verdict(inv)["verdict"] for inv in (agreed, wrong, unlined, orphan)}
    assert seen == {cmp.AGREED, cmp.DISAGREED, cmp.BOUNDED, cmp.UNCHECKABLE}


def test_the_biller_splits_the_period_at_the_term_its_records_settled():
    """192 kWh at 34.0p to the 19th, 117 kWh at 26.7p from the 20th (a cap cut inside March)."""
    bill = generate_bill("C1", _rows(20, 340.0, 267.0), "svt")
    lines = bill["rate_lines"]
    assert [(ln["term_start"], ln["period_start"], ln["period_end"]) for ln in lines] == [
        ("2023-01-01", "2023-03-01", "2023-03-19"), ("2023-03-20", "2023-03-20", "2023-03-31")]
    assert [ln["consumption_kwh"] for ln in lines] == pytest.approx([192.0, 117.0])
    assert [ln["unit_charge_gbp"] for ln in lines] == pytest.approx([192 * 0.34, 117 * 0.267])
    assert sum(ln["unit_charge_gbp"] for ln in lines) == pytest.approx(
        bill["commodity_amount_gbp"] + bill["non_commodity_amount_gbp"])
    assert "rate_lines" not in generate_bill("C1", _rows(32, 340.0, 267.0), "svt")


def test_each_line_prints_its_contracted_rate_and_its_own_readings():
    """A two-day tail is the hard case: 9 kWh at GBP 1.00 fits 11.11p, which is not the Unit Rate
    (22A.3). The line prints 11.163p, which reproduces its penny. The change-date read is deemed."""
    terms = _terms(2, 111.63, 134.92)
    inv = _invoice(generate_bill("C1", _rows(2, 111.63, 134.92), "svt"), terms)
    first, second = inv["rate_lines"]
    assert (first["consumption_kwh"], first["unit_charge_gbp"]) == (9.0, 1.00)
    assert first["unit_rate_p_per_kwh"] == pytest.approx(11.163)
    assert second["unit_rate_p_per_kwh"] == pytest.approx(13.492)
    assert first["closing_read_type"] == "E" and second["closing_read_type"] == "A"
    assert first["closing_read_kwh"] == second["opening_read_kwh"]
    assert second["closing_read_kwh"] == inv["closing_read_kwh"]
    assert sum(ln["consumption_kwh"] for ln in inv["rate_lines"]) == pytest.approx(
        inv["consumption_kwh"])


def test_a_period_charged_whole_at_either_rate_disagrees_where_the_bound_let_it_through():
    """MUTATION: bill all 309 kWh at the old rate, or at the new one, with the true split printed.
    Both sit inside [26.7p, 34.0p] x volume, so the bound passed them; the lines refuse them."""
    terms = _terms(20, 340.0, 267.0)
    for flat in (340.0, 267.0):
        rows = [dict(r, revenue_gbp=r["consumption_kwh"] / 1000 * flat + SC)
                for r in _rows(20, 340.0, 267.0)]
        true_lines = generate_bill("C1", _rows(20, 340.0, 267.0), "svt")["rate_lines"]
        bill = dict(generate_bill("C1", rows, "svt"), rate_lines=true_lines)
        inv = _invoice(bill, terms)
        assert _verdict(inv)["verdict"] == cmp.DISAGREED
        bounded = {k: val for k, val in inv.items() if k != "rate_lines"}
        assert _verdict(bounded)["verdict"] == cmp.BOUNDED


def test_a_wrong_split_between_the_rates_disagrees():
    """MUTATION: move 50 kWh from the dear line to the cheap one in the printed readings. The total
    volume still reconciles, so only pricing each line at its own rate can see it."""
    terms = _terms(20, 340.0, 267.0)
    inv = _invoice(generate_bill("C1", _rows(20, 340.0, 267.0), "svt"), terms)
    assert _verdict(inv)["verdict"] == cmp.AGREED
    first, second = inv["rate_lines"]
    inv["rate_lines"] = [dict(first, closing_read_kwh=first["closing_read_kwh"] - 50),
                         dict(second, opening_read_kwh=second["opening_read_kwh"] - 50)]
    assert _verdict(inv)["verdict"] == cmp.DISAGREED


def test_a_time_of_use_line_stays_bounded_and_says_why():
    """The bill does not print a line's band split, so a ToU term inside the period is bounded by
    name rather than priced at its flat rate."""
    period = rx.raw_account("C1", {"invoices": [_invoice(
        generate_bill("C1", _rows(20, 340.0, 267.0), "svt"), _terms(20, 340.0, 267.0))]})[
        "periods"][0]
    period["contracted_terms"][0]["tou_unit_rates"] = [
        {"register_label": "Peak", "unit_rate_p_per_kwh": 45.0},
        {"register_label": "Off-peak", "unit_rate_p_per_kwh": 20.0}]
    line = v.unit_charge_at_contract(period)
    assert line["status"] == v.BOUNDED and "time-of-use" in line["how"]


def test_the_raw_export_carries_each_lines_readings_and_no_money():
    inv = _invoice(generate_bill("C1", _rows(20, 340.0, 267.0), "svt"), _terms(20, 340.0, 267.0))
    raw = rx.raw_account("C1", {"invoices": [inv]})
    lines = raw["periods"][0]["rate_lines"]
    assert [ln["tariff_effective_from"] for ln in lines] == ["2023-01-01", "2023-03-20"]
    assert [r["read_type"] for r in lines[0]["reads"]] == [rx.CARRIED_FORWARD, "E"]
    assert rx.derived_leaks(raw) == []
