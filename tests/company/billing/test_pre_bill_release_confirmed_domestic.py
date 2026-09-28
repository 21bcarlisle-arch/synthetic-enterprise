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
