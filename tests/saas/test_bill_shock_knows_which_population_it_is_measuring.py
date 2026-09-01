"""THE DEFECT: `bill_shock_pct` was one arithmetic operation applied to two populations who would
describe what happened to them in completely different words, and the one attribute that decides
which of them a household is in — how it pays — was computed by the world, consumed by three other
organs, and never handed to the shock measure at all
(`WORKER_FINDING_THE_WORLD_KNOWS_HOW_EACH_HOUSEHOLD_PAYS_AND_BILL_SHOCK_IS_THE_ONE_ORGAN_NOT_TOLD_
2026-09-01`; definition in `docs/market_research/what_bill_shock_is.md`).

This step wires the attribution ONLY. It deliberately changes no arithmetic, so the first test
below is the one that would catch it doing more than it claimed, and it is as load-bearing as the
ones that check the attribution itself.

Pre-registered in `WORKER_PREREGISTRATION_WHAT_TELLING_THE_SHOCK_MEASURE_HOW_THE_HOUSEHOLD_PAYS_
MUST_SHOW_2026-09-01` (P1, P4, P5).
"""

import pytest

from saas.bill_generator import (
    BILL_SHOCK_POPULATION_BY_PAYMENT_CHANNEL,
    UNKNOWN_BILL_SHOCK_POPULATION,
    generate_bill,
)


def make_records(by_date: dict[str, float]) -> list[dict]:
    return [
        {
            "customer_id": "C1",
            "settlement_date": date,
            "consumption_kwh": kwh,
            "revenue_gbp": kwh * 0.25,
            "standing_charge_gbp": 0.5,
        }
        for date, kwh in by_date.items()
    ]


RECORDS = {"2023-02-01": 120.0, "2023-02-02": 90.0, "2023-02-03": 140.0}


@pytest.mark.parametrize("channel", [None, "direct_debit", "standard_credit", "prepayment"])
def test_the_payment_channel_moves_no_money_on_the_bill(channel):
    """P1. The whole claim of this step is that it attributes and does not calculate.

    If knowing how the household pays changes ANY figure on the bill, the change did more than it
    said and is unattributable when the definition split lands next. Every money field, the shock
    and the clarity score are compared against the bill built without a channel at all.
    """
    baseline = generate_bill("C1", make_records(RECORDS), "fixed_1yr", 40.0)
    with_channel = generate_bill(
        "C1", make_records(RECORDS), "fixed_1yr", 40.0, payment_channel=channel
    )

    for field in (
        "total_amount_gbp",
        "commodity_amount_gbp",
        "non_commodity_amount_gbp",
        "standing_charge_gbp",
        "vat_gbp",
        "average_unit_rate_gbp_per_mwh",
        "bill_shock_pct",
        "bill_shock_baseline_gbp",
        "clarity_score",
    ):
        assert with_channel[field] == baseline[field], field


def test_a_direct_debit_household_is_the_payment_population_not_the_bill_one():
    """The ~74% of GB households for whom the bill is a statement that arrives and is filed. Their
    shock is a material change in the amount COLLECTED, so a bill difference is measuring a
    different thing — and the bill has to say so before anyone can act on it."""
    bill = generate_bill(
        "C1", make_records(RECORDS), "fixed_1yr", 40.0, payment_channel="direct_debit"
    )
    assert bill["payment_channel"] == "direct_debit"
    assert bill["bill_shock_population"] == "payment"


def test_a_standard_credit_household_is_the_bill_population():
    """The ~13% who pay the bill in full. For them the shock IS the bill, and the existing
    arithmetic is the right quantity."""
    bill = generate_bill(
        "C1", make_records(RECORDS), "fixed_1yr", 40.0, payment_channel="standard_credit"
    )
    assert bill["bill_shock_population"] == "bill"


def test_prepayment_is_out_of_scope_and_never_folded_into_either_definition():
    """P5. ~13% of GB households have no bill to be shocked by and no direct debit to be changed.

    Folding them into standard credit — which is what a two-member channel enum does by omission —
    gives them an experience they do not have, in the population where affordability pressure is
    highest. The branch is unreachable in this world today; that is the point of asserting it, not
    a reason to skip it.
    """
    bill = generate_bill(
        "C1", make_records(RECORDS), "fixed_1yr", 40.0, payment_channel="prepayment"
    )
    assert bill["bill_shock_population"] == "out_of_scope"
    assert bill["bill_shock_population"] != BILL_SHOCK_POPULATION_BY_PAYMENT_CHANNEL[
        "standard_credit"
    ]


@pytest.mark.parametrize("channel", [None, "", "bacs", "chaps"])
def test_an_unsupplied_channel_is_unknown_and_never_silently_one_of_the_two(channel):
    """P4. "We were not told" is a result and it belongs on the surface.

    Defaulting an unsupplied channel to either real population would publish an attribution nobody
    measured as one that was measured — the string form of
    `a_default_zero_parameter_turns_an_unobservable_cause_into_a_published_measured_zero`. Business
    accounts (bacs/chaps) land here too, correctly: the two definitions are domestic.
    """
    bill = generate_bill(
        "C1", make_records(RECORDS), "fixed_1yr", 40.0, payment_channel=channel
    )
    assert bill["bill_shock_population"] == UNKNOWN_BILL_SHOCK_POPULATION
    assert bill["bill_shock_population"] not in ("payment", "bill")


def test_every_published_channel_has_exactly_one_population_and_they_are_distinct():
    """The map is the definition, so a channel silently sharing another's population would collapse
    the split back into the single scalar this work exists to end."""
    populations = list(BILL_SHOCK_POPULATION_BY_PAYMENT_CHANNEL.values())
    assert sorted(populations) == sorted(set(populations))
    assert UNKNOWN_BILL_SHOCK_POPULATION not in populations
