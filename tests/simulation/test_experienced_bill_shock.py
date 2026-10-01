"""PB4: the world's experienced bill shock, by `docs/market_research/what_bill_shock_is.md`.

WHAT EACH TEST NAMES AS ITS OWN DEFECT:

  * `test_the_partition_is_reachable_and_YEAR_ONE_can_fire` -- the defect is the old count's:
    k = 0 on 156/156 first renewals because a year-on-year window has nothing to compare in year
    one. One control over the whole partition (fires, does not fire, out of scope, cannot tell), so
    a measure that refuses everything, or fires on everything, cannot pass.
  * `test_a_FALL_is_not_a_shock` -- the old count took `abs()`, so a bill falling 15% left a
    household as likely to leave as one rising 15%.
  * `test_a_DD_household_is_shocked_by_the_PAYMENT_not_by_the_bill` -- definition A: under a
    level DD the reference is the payment the supplier set, read through its own review door.
    A rise the review absorbs (its rounding / variance band) is not a payment change.
  * `test_the_live_roll_CARRIES_the_experienced_shock` -- an unwired measure is a measure of
    nothing: the renewal event the world emits must carry it.
  * `test_a_sign_up_BEFORE_THE_CAP_is_quoted_at_the_rate_it_was_sold_at` -- the quote was
    annualised at the cap, which has no value before 2019, so year one stayed blind as a None.
  * `test_a_year_billed_EXACTLY_as_quoted_reads_NO_rise` -- the quote was inc-VAT at a 53p 2024
    standing charge and the year it was met by was ex-VAT at the world's dated charge, so a
    household billed exactly what it was quoted read as a FALL, and every year-one rise was
    under-read.
"""
from simulation.customer_events import roll_lifecycle_event
from simulation.experienced_bill_shock import (
    POPULATION_LEVEL_PAYMENT,
    POPULATION_OUT_OF_SCOPE,
    POPULATION_THE_BILL,
    experienced_bill_shock,
)


def _year(year: int, monthly: float) -> dict[str, float]:
    return {f"{year}-{m:02d}": monthly for m in range(1, 13)}


def _shock(channel, bills, first, opening=70.0):
    return experienced_bill_shock(bills=bills, payment_channel=channel, renewal_period="2023-01",
                                  first_renewal=first, opening_monthly_gbp=opening)


def test_the_partition_is_reachable_and_YEAR_ONE_can_fire():
    fired_dd = _shock("direct_debit", _year(2022, 100.0), first=True)
    fired_sc = _shock("standard_credit", _year(2022, 100.0), first=True)
    quiet = _shock("direct_debit", _year(2022, 70.0), first=True)
    out = _shock("prepayment", _year(2022, 100.0), first=True)
    unknown = _shock("direct_debit", _year(2022, 100.0), first=True, opening=None)
    assert fired_dd["shocked"] is True and fired_dd["reference"] == "quote"
    assert fired_sc["shocked"] is True and fired_sc["population"] == POPULATION_THE_BILL
    assert quiet["shocked"] is False
    assert out["shocked"] is None and out["population"] == POPULATION_OUT_OF_SCOPE and out["reason"]
    # Cannot tell is None with a reason -- never a 0 that reads as "no shock".
    assert unknown["shocked"] is None and "sign-up" in unknown["reason"]


def test_a_FALL_is_not_a_shock():
    rise = {**_year(2021, 60.0), **_year(2022, 95.0)}
    fall = {**_year(2021, 95.0), **_year(2022, 60.0)}
    for channel in ("direct_debit", "standard_credit"):
        assert _shock(channel, rise, first=False)["shocked"] is True
        r = _shock(channel, fall, first=False)
        assert r["rise_fraction"] < -0.15 and r["shocked"] is False


def test_a_DD_household_is_shocked_by_the_PAYMENT_not_by_the_bill():
    from company.interfaces.dd_review_outcome import reviewed_monthly_amount

    bills = {**_year(2021, 60.0), **_year(2022, 72.0)}
    dd = _shock("direct_debit", bills, first=False)
    sc = _shock("standard_credit", bills, first=False)
    assert dd["population"] == POPULATION_LEVEL_PAYMENT and dd["reference"] == "prior_review"
    expected = reviewed_monthly_amount(72.0 * 12) / reviewed_monthly_amount(60.0 * 12) - 1.0
    assert abs(dd["rise_fraction"] - expected) < 1e-6
    assert abs(sc["rise_fraction"] - 0.2) < 1e-6


def _year_one_records(start: str, sold_rate: float, later_rate: float) -> list[dict]:
    """Twelve monthly rows from `start`: the first six at the sold rate, the rest at `later_rate`."""
    y0, m0 = (int(x) for x in start.split("-"))
    records = []
    for i in range(12):
        ym = f"{y0 + (m0 - 1 + i) // 12}-{(m0 - 1 + i) % 12 + 1:02d}"
        rate = sold_rate if i < 6 else later_rate
        revenue = 225.0 * rate / 1000.0 + 16.0
        records.append({"customer_id": "C1", "settlement_date": f"{ym}-15", "settlement_period": 1,
                        "consumption_kwh": 225.0, "unit_rate_gbp_per_mwh": rate,
                        "revenue_gbp": revenue, "wholesale_cost_gbp": revenue * 0.7,
                        "margin_gbp": revenue * 0.3, "capital_cost_gbp": 0.1,
                        "net_margin_gbp": revenue * 0.3 - 0.1})
    return records


def test_the_live_roll_CARRIES_the_experienced_shock():
    # C1 is a direct-debit household sold at 200 £/MWh in 2021-10; from April 2022 it is charged
    # 400. The quote is the rate it was SOLD at (its first bill), so the rise is the year's own.
    customers = [{"customer_id": "C1", "commodity": "electricity", "segment": "resi",
                  "epc_rating": "D", "acquisition_date": "2021-10-01", "eac_kwh": 2700}]
    event = roll_lifecycle_event("C1", "2022-10-01", "electricity",
                                 _year_one_records("2021-10", 200.0, 400.0), customers)
    assert event is not None
    shock = event["sim_experienced_bill_shock"]
    assert shock["population"] == POPULATION_LEVEL_PAYMENT
    assert shock["reference"] == "quote", shock
    assert shock["shocked"] is True, shock


def test_a_sign_up_BEFORE_THE_CAP_is_quoted_at_the_rate_it_was_sold_at():
    """The defect: the quote was annualised at the default-tariff cap, which does not exist before
    2019, so 27 of 31 in-scope first renewals on one world had no quote at all. A 2016 sign-up has a
    first bill, and the rate on it is the quote's rate; a dearer sale is a dearer quote."""
    customers = [{"customer_id": "C1", "commodity": "electricity", "segment": "resi",
                  "epc_rating": "D", "acquisition_date": "2016-03-01", "eac_kwh": 2700}]
    cheap = roll_lifecycle_event("C1", "2017-03-01", "electricity",
                                 _year_one_records("2016-03", 100.0, 160.0), customers)
    dear = roll_lifecycle_event("C1", "2017-03-01", "electricity",
                                _year_one_records("2016-03", 140.0, 160.0), customers)
    cheap, dear = cheap["sim_experienced_bill_shock"], dear["sim_experienced_bill_shock"]
    assert cheap["reference"] == "quote" and cheap["shocked"] is not None, cheap
    # Same year-one bills after month six, so a dearer sale must read as a SMALLER rise.
    assert dear["rise_fraction"] < cheap["rise_fraction"], (cheap, dear)


def test_a_year_billed_EXACTLY_as_quoted_reads_NO_rise():
    """One basis: a household that uses exactly its EAC at the rate and standing charge it was sold
    at meets, at its first review, the payment it was quoted -- up to the review's round-up to the
    pound. The defect read that household as a fall: the quote carried VAT and a 53p standing
    charge, and the year was summed ex-VAT at 20p."""
    from datetime import date, timedelta

    eac, rate, sc = 2700.0, 140.0, 0.20
    records, day = [], date(2016, 3, 1)
    while day < date(2017, 3, 1):
        kwh = eac / 365.0
        revenue = kwh * rate / 1000.0 + sc
        records.append({"customer_id": "C1", "settlement_date": day.isoformat(),
                        "settlement_period": 48, "consumption_kwh": kwh,
                        "unit_rate_gbp_per_mwh": rate, "standing_charge_gbp": sc,
                        "revenue_gbp": revenue, "wholesale_cost_gbp": revenue * 0.7,
                        "margin_gbp": revenue * 0.3, "capital_cost_gbp": 0.0,
                        "net_margin_gbp": revenue * 0.3})
        day += timedelta(days=1)
    customers = [{"customer_id": "C1", "commodity": "electricity", "segment": "resi",
                  "epc_rating": "D", "acquisition_date": "2016-03-01", "eac_kwh": eac}]
    shock = roll_lifecycle_event("C1", "2017-03-01", "electricity", records,
                                 customers)["sim_experienced_bill_shock"]
    assert shock["reference"] == "quote" and shock["population"] == POPULATION_LEVEL_PAYMENT, shock
    # The round-up to the pound is at most £1 on a ~£50 payment.
    assert 0.0 <= shock["rise_fraction"] < 0.025, shock
    assert shock["shocked"] is False


def test_the_HAZARD_BASE_counts_one_experienced_shock_a_year_and_so_moves_in_year_one():
    """The defect is the swap not having happened: the hazard read shocked MONTHS, which are 0 at
    every first renewal, so a household shocked in year one was exactly as likely to leave as one
    that was not. Both legs of the partition are asserted reachable before the ratio is read."""
    from saas.churn_model import churn_probability

    customers = [{"customer_id": "C1", "commodity": "electricity", "segment": "resi",
                  "epc_rating": "D", "acquisition_date": "2021-10-01", "eac_kwh": 2700}]
    shocked = roll_lifecycle_event("C1", "2022-10-01", "electricity",
                                   _year_one_records("2021-10", 200.0, 400.0), customers)
    quiet = roll_lifecycle_event("C1", "2022-10-01", "electricity",
                                 _year_one_records("2021-10", 200.0, 200.0), customers)
    assert shocked["sim_experienced_bill_shock"]["shocked"] is True
    assert quiet["sim_experienced_bill_shock"]["shocked"] is False
    # The retired month count cannot tell them apart in year one -- that is the blindness.
    assert shocked["sim_month_count_bill_shock_base"] == quiet["sim_month_count_bill_shock_base"]
    ratio = shocked["sim_bill_shock_base"] / quiet["sim_bill_shock_base"]
    assert abs(ratio - churn_probability(1) / churn_probability(0)) < 1e-3, ratio
