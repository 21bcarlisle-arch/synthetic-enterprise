"""Property tests for billing and payments: each property is a rule the payment lifecycle or the
law declares, not a reading of the code under test.

Director steer, 20 Nov 2026, item 2 (`docs/staging/advisor/done/DIRECTOR_STEER_GATES_JUDGE_FROM_
THE_BASE_PROPERTY_TESTS_FOR_BILLING_AND_DIFF_TRIGGERED_CHECKS_2026-11-20.md`). Where each rule
comes from:

* one balance, the sum of its parts: lifecycle invariant `one_balance` (SLC 31H.12, 27.16),
  in the 16 Nov declared lifecycle (5bf7e7c872, `company/compliance/payment_lifecycle.yaml`);
* no part-month first DD: the director's 1 Sep correction, "an annualised plan divides estimated
  annual cost by twelve whatever the start date", and lifecycle invariant `one_regular_amount`;
* a review run twice equals once: a review is a function of the year's bills and the standing DD
  (SLC 27.15 "best and most current information"), so re-reading the same bills cannot move it;
* VAT and the standing charge: VAT Notice 701/19 (domestic supply reduced-rated at any volume; a
  business supply reduced-rated at or under its fuel's de minimis, 33 kWh/day electricity and
  145 kWh/day gas) and VAT on the whole consideration, standing charge included (Notice 700);
  the standing charge accrues per day of supply whatever is consumed;
* serialisation: the committed ledger is one book in two forms (`ledger_store`'s own contract).

Generation is derandomised and the example database is off, so the gate sees the same examples on
every run: a property that fails here fails every time, never as a flake.
"""
from __future__ import annotations

import datetime as dt
import gzip
import json
import math

from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from company.billing import ledger_store
from company.billing.account_ledger import AccountLedger, LedgerEvent, LedgerEventType
from company.billing.dd_review import _recommended_monthly, review
from company.billing.dd_review_runner import run_annual_reviews
from company.billing.dual_fuel_bill import SME_VAT_DE_MINIMIS_KWH_PER_DAY, vat_rate_for_supply
from company.compliance.domain_invariants import check_vat, vat_rate_for_segment
from saas.bill_generator import generate_bill

PROPERTY = settings(max_examples=150, deadline=None, derandomize=True, database=None,
                    suppress_health_check=[HealthCheck.too_slow])

REDUCED = vat_rate_for_segment("resi")
STANDARD = vat_rate_for_segment("SME")

pennies = st.integers(min_value=0, max_value=500_000).map(lambda p: p / 100)
days_2016_2025 = st.dates(min_value=dt.date(2016, 1, 1), max_value=dt.date(2025, 12, 31))
fuels = st.sampled_from(sorted(SME_VAT_DE_MINIMIS_KWH_PER_DAY))


def _rule_rate(segment: str, fuel: str, kwh: float, days: int) -> float:
    """VAT Notice 701/19 as published, written from the notice, not from the biller."""
    if segment == "resi":
        return REDUCED
    return STANDARD if kwh / days > SME_VAT_DE_MINIMIS_KWH_PER_DAY[fuel] else REDUCED


def test_the_de_minimis_limits_are_the_published_ones():
    """The rule below reads the limits from the commons; this pins the commons to the notice."""
    assert SME_VAT_DE_MINIMIS_KWH_PER_DAY == {"electricity": 33.0, "gas": 145.0}
    assert (REDUCED, STANDARD) == (0.05, 0.20)


# --- VAT and the standing charge: one rule, every implementation -------------------------------

@PROPERTY
@example(segment="SME", fuel="electricity", kwh=33.0 * 30, days=30, on=dt.date(2020, 1, 1))
@example(segment="SME", fuel="gas", kwh=145.0 * 30, days=30, on=dt.date(2020, 1, 1))
@example(segment="SME", fuel="gas", kwh=100.0 * 30, days=30, on=dt.date(2020, 1, 1))
@example(segment="resi", fuel="electricity", kwh=500.0 * 30, days=30, on=dt.date(2020, 1, 1))
@given(segment=st.sampled_from(["resi", "SME"]), fuel=fuels,
       kwh=st.floats(min_value=0, max_value=200_000, allow_nan=False),
       days=st.integers(min_value=1, max_value=400), on=days_2016_2025)
def test_every_vat_reading_of_one_period_agrees_with_the_notice(segment, fuel, kwh, days, on):
    """Five VAT implementations was the defect; each reading of one period must give the notice's
    rate, and the checker must pass what the biller charges."""
    rule = _rule_rate(segment, fuel, kwh, days)
    billed = vat_rate_for_supply(segment, fuel, kwh, days)
    assert billed == rule
    assert check_vat(segment, billed, commodity=fuel, kwh=kwh, days=days)
    if segment == "resi":
        assert vat_rate_for_segment("resi", fuel=fuel, on=on) == rule


@st.composite
def settlement_month(draw):
    start = draw(st.dates(min_value=dt.date(2016, 1, 1), max_value=dt.date(2025, 11, 1)))
    n = draw(st.integers(min_value=1, max_value=31))
    sc_per_day = draw(st.integers(min_value=0, max_value=200).map(lambda p: p / 100))
    records = []
    for i in range(n):
        kwh = draw(st.integers(min_value=0, max_value=4_000_00).map(lambda x: x / 100))
        energy = draw(pennies)
        records.append({"settlement_date": (start + dt.timedelta(days=i)).isoformat(),
                        "consumption_kwh": kwh, "revenue_gbp": energy + sc_per_day,
                        "standing_charge_gbp": sc_per_day})
    order = draw(st.permutations(range(n)))
    return records, [records[i] for i in order], sc_per_day


@PROPERTY
@given(month=settlement_month(), segment=st.sampled_from(["resi", "SME"]), fuel=fuels)
def test_a_bill_is_its_lines_plus_vat_on_all_of_them_at_the_notices_rate(month, segment, fuel):
    records, shuffled, sc_per_day = month
    if fuel == "gas":
        records = [{**r, "gas_standing_charge_gbp": r.pop("standing_charge_gbp")} for r in
                   (dict(x) for x in records)]
        shuffled = sorted(records, key=lambda r: r["consumption_kwh"])
    bill = generate_bill("c", records, "fixed", segment=segment, commodity=fuel)
    days = len(records)
    kwh = sum(r["consumption_kwh"] for r in records)
    subtotal = bill["commodity_amount_gbp"] + bill["non_commodity_amount_gbp"] + bill["standing_charge_gbp"]
    # the standing charge is per day of supply, whatever was consumed
    assert bill["days_in_period"] == days
    assert math.isclose(bill["standing_charge_gbp"], sc_per_day * days, abs_tol=1e-9)
    # VAT is charged on the whole consideration, standing charge included, at the notice's rate
    assert math.isclose(bill["vat_gbp"], subtotal * _rule_rate(segment, fuel, kwh, days), abs_tol=1e-6)
    assert math.isclose(bill["total_amount_gbp"], subtotal + bill["vat_gbp"], abs_tol=1e-6)
    # the lines split what was received for the supply; none of them is charged on top of it
    received = sum(r["revenue_gbp"] for r in records)
    assert math.isclose(subtotal, received, abs_tol=1e-6)
    # the order settlement arrives in is not a fact about the supply
    again = generate_bill("c", shuffled, "fixed", segment=segment, commodity=fuel)
    for k in ("standing_charge_gbp", "vat_gbp", "total_amount_gbp", "total_consumption_kwh"):
        assert math.isclose(again[k], bill[k], abs_tol=1e-6), k


# --- One balance, reconciled to its parts ------------------------------------------------------

@st.composite
def ledger_events(draw):
    n = draw(st.integers(min_value=0, max_value=25))
    out = []
    for i in range(n):
        out.append(LedgerEvent(
            event_id=f"e{i}", account_id="A", event_type=draw(st.sampled_from(list(LedgerEventType))),
            amount_gbp=draw(pennies), valid_time=draw(days_2016_2025),
            transaction_time=dt.datetime(2026, 1, 1), reason="property"))
    return out


@PROPERTY
@given(events=ledger_events(), data=st.data())
def test_one_balance_is_debits_less_credits_whatever_the_order_or_repeats(events, data):
    ledger = AccountLedger("A")
    for e in events:
        assert ledger.post(e)
    replay = AccountLedger("A")
    for e in data.draw(st.permutations(events)) + events:   # every event arrives twice
        replay.post(e)
    debits = sum(e.amount_gbp for e in events if e.event_type.is_debit)
    credits = sum(e.amount_gbp for e in events if not e.event_type.is_debit)
    assert math.isclose(ledger.balance(), debits - credits, abs_tol=0.005)
    assert replay.balance() == ledger.balance()
    as_of = data.draw(days_2016_2025)
    assert replay.balance(as_of) == ledger.balance(as_of)
    s = ledger.balance_summary()
    assert math.isclose(s["balance_gbp"], s["total_debits_gbp"] - s["total_credits_gbp"], abs_tol=0.005)
    assert s["arrears_gbp"] - s["credit_gbp"] == s["balance_gbp"]
    assert not (s["in_arrears"] and s["in_credit"])
    ledger.reconcile(debits, credits)   # raises on any disagreement


# --- The first DD is never set from a part-month ----------------------------------------------

@st.composite
def a_customers_bills(draw):
    """Monthly bills from a first bill that may be any stub of a month, through 13-36 months."""
    first_end = draw(st.dates(min_value=dt.date(2016, 1, 1), max_value=dt.date(2022, 12, 28)))
    n = draw(st.integers(min_value=13, max_value=36))
    bills = []
    for m in range(n):
        y, mo = divmod(first_end.month - 1 + m, 12)
        end = first_end.replace(year=first_end.year + y, month=mo + 1, day=min(first_end.day, 28))
        bills.append({"customer_id": "c", "period_end": end.isoformat(),
                      "total_amount_gbp": draw(pennies)})
    return bills


@PROPERTY
@given(bills=a_customers_bills(), opening=st.integers(1, 50_000).map(lambda p: p / 100),
       stub=pennies)
def test_the_first_review_starts_from_the_opening_amount_not_the_first_bill(bills, opening, stub):
    """Whatever the first bill was (a half-month stub included), the DD entering the first review
    is the annualised amount set at opening."""
    a = run_annual_reviews(bills, opening_dd_gbp={"c": opening})
    stubbed = [dict(bills[0], total_amount_gbp=stub)] + bills[1:]
    b = run_annual_reviews(stubbed, opening_dd_gbp={"c": opening})
    assert a.events and b.events
    assert a.events[0].current_dd_gbp == b.events[0].current_dd_gbp == round(opening, 2)
    assert run_annual_reviews(bills).events == []   # no opening amount: refused, never invented


@PROPERTY
@example(actual=132.0)   # 11.0 a month exactly: round-half-even made it 12 until 20 Nov
@example(actual=120.0)
@given(actual=pennies | st.integers(0, 500).map(lambda n: 12.0 * n))
def test_a_reviewed_dd_collects_the_year_and_no_more_than_a_pound_a_month_over(actual):
    """One regular amount that covers the year: ceiling to the pound, as `review` declares."""
    monthly = review("c", dt.date(2020, 1, 1), 10.0, actual).recommended_monthly_gbp
    assert monthly == _recommended_monthly(actual)
    assert monthly * 12 >= actual - 1e-9
    assert monthly - actual / 12 < 1


# --- A review run twice equals a review run once -----------------------------------------------

@PROPERTY
@given(bills=a_customers_bills(), opening=st.integers(1, 50_000).map(lambda p: p / 100), data=st.data())
def test_a_review_run_twice_or_on_reordered_bills_equals_one_run(bills, opening, data):
    once = run_annual_reviews(bills, opening_dd_gbp={"c": opening})
    twice = run_annual_reviews(bills, opening_dd_gbp={"c": opening})
    shuffled = run_annual_reviews(data.draw(st.permutations(bills)), opening_dd_gbp={"c": opening})
    assert once.serialise() == twice.serialise() == shuffled.serialise()


# --- Serialisation round-trips -----------------------------------------------------------------

json_values = st.recursive(
    st.none() | st.booleans() | st.integers(-10**9, 10**9) | pennies | st.text(max_size=12),
    lambda inner: st.lists(inner, max_size=4) | st.dictionaries(st.text(max_size=6), inner, max_size=4),
    max_leaves=20)


@settings(PROPERTY, max_examples=60, suppress_health_check=list(HealthCheck))
@given(meta=st.dictionaries(st.text(min_size=1, max_size=8), st.text(max_size=8), max_size=3),
       body=json_values)
def test_the_ledger_reads_back_as_written_in_both_forms(tmp_path, meta, body):
    book = {"meta": meta, "bills": body}
    text = json.dumps(book)
    path = tmp_path / "billing_ledger.json"
    twin = ledger_store.write_ledger(text, path)
    assert ledger_store.load_ledger(path) == book
    assert ledger_store.loads_ledger(twin.read_bytes()) == book
    first = twin.read_bytes()
    ledger_store.write_ledger(text, path)
    assert twin.read_bytes() == first   # an unchanged book is an unchanged blob
    assert gzip.decompress(first) == text.encode()


@PROPERTY
@given(bills=a_customers_bills(), opening=st.integers(1, 50_000).map(lambda p: p / 100))
def test_a_review_run_survives_json(bills, opening):
    out = run_annual_reviews(bills, opening_dd_gbp={"c": opening}).serialise()
    assert json.loads(json.dumps(out)) == out


def test_the_same_book_written_at_two_times_is_the_same_blob(tmp_path, monkeypatch):
    """A gzip header carries a write time unless pinned; an unpinned one makes every publish a
    changed blob. Two writes in one second cannot show it, so the clock is moved between them."""
    text = json.dumps({"meta": {"source_json": "x"}, "bills": [1, 2]})
    first = ledger_store.write_ledger(text, tmp_path / "a" / "billing_ledger.json").read_bytes()
    monkeypatch.setattr(gzip.time, "time", lambda: 2_000_000_000.0)
    second = ledger_store.write_ledger(text, tmp_path / "b" / "billing_ledger.json").read_bytes()
    assert first == second
