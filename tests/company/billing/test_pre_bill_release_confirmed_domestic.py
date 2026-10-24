"""The exception queue's release of a domestic ceiling hold (`release_confirmed_domestic`).

The ceiling checks catch two defects: a business premise labelled domestic, and a wrong volume.
A council-tax listing answers the first and an actual read answers the second, so a release takes
both. Anything else stays held. Evidence and decision:
docs/staging/SEAT_FINDING_FIVE_OF_THE_EIGHT_REMAINING_HELD_BILLS_WERE_A_MONTHS_ESTIMATE_ON_A_SEVEN_DAY_STUB_2026-09-28.md
"""
from company.billing.monthly_bill_assembly import build_monthly_bills
from company.billing.pre_bill_validation import (
    ValidationOutcome,
    release_confirmed_domestic,
    validate_bill,
    validate_bills,
)


def _winter_bill_on_an_electric_heated_house(**overrides):
    """A January bill at the scale PROS-2016-0098 actually draws (5,070 kWh, 2017-01), at 5% VAT.

    Over both ceiling checks and nothing else: it foots, no line is negative, the period is sane.
    """
    subtotal = 760.50 + 0.0 + 9.30
    bill = {
        "customer_id": "PROS-2016-0098",
        "period_start": "2017-01-01",
        "period_end": "2017-01-31",
        "segment": "resi",
        "commodity": "electricity",
        "total_consumption_kwh": 5070.0,
        "commodity_amount_gbp": 760.50,
        "non_commodity_amount_gbp": 0.0,
        "standing_charge_gbp": 9.30,
        "vat_gbp": round(subtotal * 0.05, 2),
        "billing_basis": "actual",
        "premise_council_tax_listed": True,
    }
    bill.update(overrides)
    return bill


def test_every_leg_of_the_release_partition_is_reachable():
    """The release exists to be taken rarely, so assert first that it CAN be taken -- and that
    each refusal can too. A release that refused everything passes every refusal test below."""
    bills = [
        _winter_bill_on_an_electric_heated_house(),
        _winter_bill_on_an_electric_heated_house(customer_id="EST", billing_basis="estimated"),
        _winter_bill_on_an_electric_heated_house(customer_id="UNL", premise_council_tax_listed=None),
        _winter_bill_on_an_electric_heated_house(customer_id="MIX", vat_gbp=0.0),
    ]
    passing, held = validate_bills(bills)
    released = [b for b in passing if "pre_bill_release" in b]
    assert [b["customer_id"] for b in released] == ["PROS-2016-0098"]
    assert sorted(r.customer_id for r in held) == ["EST", "MIX", "UNL"]


def test_the_winter_bill_is_held_before_the_queue_sees_it():
    """Premise of the release: the gate does hold this bill, on consumption scale alone."""
    result = validate_bill(_winter_bill_on_an_electric_heated_house())
    assert result.held
    assert result.consumption_scale_only
    assert len(result.reasons) == 2


def test_a_listed_dwelling_on_an_actual_read_issues_and_says_why_it_was_held():
    bill = _winter_bill_on_an_electric_heated_house()
    released = release_confirmed_domestic(bill, validate_bill(bill))
    assert released is not None
    assert released["pre_bill_release"]["outcome"] == ValidationOutcome.RELEASED.value
    assert len(released["pre_bill_release"]["held_for"]) == 2
    assert "pre_bill_release" not in bill, "the input bill must not be mutated"


def test_an_estimate_over_the_ceiling_stays_held_because_a_listing_says_nothing_about_volume():
    """The five 2025-06 stub estimates were a month's estimate on seven days, on listed dwellings."""
    bill = _winter_bill_on_an_electric_heated_house(billing_basis="estimated")
    assert release_confirmed_domestic(bill, validate_bill(bill)) is None


def test_an_unanswered_or_negative_listing_stays_held():
    for listed in (None, False):
        bill = _winter_bill_on_an_electric_heated_house(premise_council_tax_listed=listed)
        assert release_confirmed_domestic(bill, validate_bill(bill)) is None
    bill = _winter_bill_on_an_electric_heated_house()
    del bill["premise_council_tax_listed"]
    assert release_confirmed_domestic(bill, validate_bill(bill)) is None


def test_any_reason_beyond_consumption_scale_keeps_the_bill_held():
    # 0 VAT on a resi subtotal: vat_by_segment's arithmetic leg fires alongside the scale legs.
    bill = _winter_bill_on_an_electric_heated_house(vat_gbp=0.0)
    result = validate_bill(bill)
    assert result.held and not result.consumption_scale_only
    assert release_confirmed_domestic(bill, result) is None


def test_a_passing_bill_is_not_touched():
    bill = _winter_bill_on_an_electric_heated_house(total_consumption_kwh=300.0)
    result = validate_bill(bill)
    assert not result.held
    assert release_confirmed_domestic(bill, result) is None


def test_the_billing_run_stamps_the_listing_feed_and_omitting_it_stamps_nothing():
    from simulation.meter_reads import SimulatedReadFeed

    records = [
        {
            "customer_id": "C1",
            "settlement_date": f"2023-0{m}-01",
            "settlement_period": 1,
            "consumption_kwh": 300.0,
            "unit_rate_gbp_per_mwh": 200.0,
            "revenue_gbp": 60.0,
            "wholesale_cost_gbp": 0.0,
            "margin_gbp": 0.0,
        }
        for m in (1, 2)
    ]
    asked = []

    def feed(customer):
        asked.append(customer["customer_id"])
        return True

    stamped = build_monthly_bills(records, SimulatedReadFeed(), premise_listing_feed=feed)
    assert stamped and all(b["premise_council_tax_listed"] is True for b in stamped)
    assert asked == ["C1"], "the lookup is made once per account, not once per bill"
    bare = build_monthly_bills(records, SimulatedReadFeed())
    assert all("premise_council_tax_listed" not in b for b in bare)


# --- A held estimate on a closed account (2026-10-21) -------------------------------------------
# docs/market_research/unbilled_energy_and_revenue_assurance.md, K6, "A held bill on an account that
# closes". After the exit no read reaches this supplier, so the closing run goes out on the final
# bill at the closing read, unless SLC 21BA bars it.

def _month(customer_id, start, end, basis="estimated", **overrides):
    bill = _winter_bill_on_an_electric_heated_house(
        customer_id=customer_id, period_start=start, period_end=end, billing_basis=basis,
        **overrides)
    bill["total_amount_gbp"] = round(
        bill["commodity_amount_gbp"] + bill["standing_charge_gbp"] + bill["vat_gbp"], 2)
    return bill


def _leaver(customer_id="LEAVER", final_basis="estimated", **overrides):
    """PROS-2017-0117's shape: a read in November, four held estimates, an estimated final bill."""
    return [
        _month(customer_id, "2017-11-01", "2017-11-30", "actual", total_consumption_kwh=300.0,
               **overrides),
        _month(customer_id, "2017-12-01", "2017-12-31", **overrides),
        _month(customer_id, "2018-01-01", "2018-01-31", **overrides),
        _month(customer_id, "2018-02-01", "2018-02-28", **overrides),
        _month(customer_id, "2018-03-01", "2018-03-31", **overrides),
        _month(customer_id, "2018-04-01", "2018-04-30", final_basis, final_bill=True, **overrides),
    ]


def test_every_leg_of_the_closing_run_release_is_reachable():
    """One partition over the whole queue. The release is taken, and each refusal is taken: an open
    account, an unlisted address, a final bill on an actual read (its catch-up carries the energy)
    and an interim 21BA bars at the final bill."""
    old = [
        _month("OLD", "2018-04-01", "2018-04-30", "actual", total_consumption_kwh=300.0),
        _month("OLD", "2018-05-01", "2018-05-31"),
        _month("OLD", "2019-05-01", "2019-05-31"),
        _month("OLD", "2019-06-01", "2019-06-30", final_bill=True),
    ]
    open_account = _leaver("OPEN")
    del open_account[-1]["final_bill"]
    bills = (_leaver() + open_account + _leaver("UNL", premise_council_tax_listed=None)
             + _leaver("READ", final_basis="actual") + old)
    passing, held = validate_bills(bills)
    at_closure = {(b["customer_id"], b["period_end"]) for b in passing
                  if b.get("pre_bill_release", {}).get("outcome")
                  == ValidationOutcome.RELEASED_AT_CLOSURE.value}
    assert at_closure == {
        ("LEAVER", "2017-12-31"), ("LEAVER", "2018-01-31"), ("LEAVER", "2018-02-28"),
        ("LEAVER", "2018-03-31"), ("LEAVER", "2018-04-30"),
        ("OLD", "2019-05-31"), ("OLD", "2019-06-30"),
    }
    still = {(r.customer_id, r.period_end) for r in held}
    assert {c for c, _ in still} == {"OPEN", "UNL", "READ", "OLD"}
    assert ("OLD", "2018-05-31") in still, "over 12 months before the final bill: barred, held"
    released = next(b for b in passing if (b["customer_id"], b["period_end"]) == ("LEAVER", "2017-12-31"))
    assert released["pre_bill_release"]["issued_with_final_bill"] == "2018-04-30"


def test_the_accrual_holds_a_closing_run_until_the_final_bills_month():
    from company.billing.billing_accuracy import unbilled_accrual
    from company.interfaces.bill_assembly import held_bills

    bills = _leaver()
    held = held_bills(bills)
    assert held == set(), "the whole closing run is released"
    before = unbilled_accrual(bills, held, "2018-03")["by_fuel"]["electricity"]
    assert before["held_estimates"] == 4
    assert before["kwh"] == 4 * 5070.0
    on_the_final = unbilled_accrual(bills, held, "2018-04")["by_fuel"]["electricity"]
    assert on_the_final["held_estimates"] == 0 and on_the_final["kwh"] == 0.0


def test_the_k1_grade_counts_a_closing_run_from_the_final_bills_month_and_never_beside_the_accrual():
    """Billed on estimate and unbilled are the two halves of unread revenue and count disjoint
    bills. Before the final bill's month the interims are the accrual's, so the grade must not
    count them; from that month they are billed on estimate and the accrual has let them go.
    The final bill is an estimate, so from that month the grade counts the run as closed on it,
    beside the position (2026-10-24: no read will end it), and never as open."""
    from company.billing.billing_accuracy import (
        estimated_billing_outstanding_grade,
        unbilled_accrual,
    )

    bills = _leaver()
    for month, grade_open, grade_closed, accrual_open in (("2018-03", 0, 0, 4),
                                                          ("2018-04", 0, 5, 0)):
        grade = estimated_billing_outstanding_grade(bills, month)
        accrual = unbilled_accrual(bills, set(), month)["by_fuel"]["electricity"]
        assert (grade["open_bills"], grade["closed_on_estimated_final_bills"],
                accrual["held_estimates"]) == (grade_open, grade_closed, accrual_open), month


def test_the_billing_run_stamps_only_a_churned_accounts_last_bill_as_final():
    from simulation.meter_reads import SimulatedReadFeed

    records = [
        {
            "customer_id": "C1",
            "settlement_date": f"2023-0{m}-01",
            "settlement_period": 1,
            "consumption_kwh": 300.0,
            "unit_rate_gbp_per_mwh": 200.0,
            "revenue_gbp": 60.0,
            "wholesale_cost_gbp": 0.0,
            "margin_gbp": 0.0,
        }
        for m in (1, 2, 3)
    ]
    churned = build_monthly_bills(records, SimulatedReadFeed(), churned_ids={"C1"})
    assert [bool(b.get("final_bill")) for b in churned] == [False, False, True]
    staying = build_monthly_bills(records, SimulatedReadFeed())
    assert not any(b.get("final_bill") for b in staying)
