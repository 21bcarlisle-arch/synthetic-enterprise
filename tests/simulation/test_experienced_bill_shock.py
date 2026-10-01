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


def test_the_live_roll_CARRIES_the_experienced_shock():
    # C1 is a direct-debit household; a 2021-10 sign-up was quoted before the April 2022 cap rise.
    customers = [{"customer_id": "C1", "commodity": "electricity", "segment": "resi",
                  "epc_rating": "D", "acquisition_date": "2021-10-01", "eac_kwh": 2700}]
    records = []
    for i in range(12):
        ym = f"{2021 + (9 + i) // 12}-{(9 + i) % 12 + 1:02d}"
        records.append({"customer_id": "C1", "settlement_date": f"{ym}-15", "settlement_period": 1,
                        "consumption_kwh": 225.0, "unit_rate_gbp_per_mwh": 400.0,
                        "revenue_gbp": 110.0, "wholesale_cost_gbp": 80.0, "margin_gbp": 30.0,
                        "capital_cost_gbp": 0.1, "net_margin_gbp": 29.9})
    event = roll_lifecycle_event("C1", "2022-10-01", "electricity", records, customers)
    assert event is not None
    shock = event["sim_experienced_bill_shock"]
    assert shock["population"] == POPULATION_LEVEL_PAYMENT
    assert shock["reference"] == "quote", shock
    assert shock["shocked"] is True, shock
