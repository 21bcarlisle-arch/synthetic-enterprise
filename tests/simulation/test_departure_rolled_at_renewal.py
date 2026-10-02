"""The renewal-point departure roll is skipped only for a household converting off the SVT.

Defect this catches: a household on the default tariff has two exit routes -- C1b's inertia hazard
on every SVT segment, and the renewal-point roll again when it converts to a fixed term at an
anniversary -- so SVT exits run above the all-cause band C1b is graded against.
"""
from simulation.customer_events import departure_rolled_at_renewal
from simulation.svt_product import SVT_TARIFF_TYPE


def test_only_an_svt_predecessor_skips_the_roll_and_every_other_predecessor_still_rolls():
    # One control over the whole partition: a gate that refuses everything fails the first two
    # legs, and a gate that refuses nothing fails the last.
    plan = {
        "first_term": departure_rolled_at_renewal(None),
        "fixed": departure_rolled_at_renewal("fixed"),
        "svt": departure_rolled_at_renewal(SVT_TARIFF_TYPE),
    }
    assert plan == {"first_term": True, "fixed": True, "svt": False}


def test_every_other_tariff_type_the_world_writes_still_rolls():
    for other in ("fixed", "deemed", "tou", "flex", "indexed"):
        assert departure_rolled_at_renewal(other) is True


def test_a_household_converting_off_the_svt_is_still_a_retention_every_counting_reader_keeps():
    # Defect: skipping the roll also dropped the ROW, so `renewed` fell 61 -> 35 in one world and
    # every retention count and renewal-rate denominator lost a household that stayed.
    from company.analytics.churn_accuracy_report import compute_churn_model_performance
    from saas.reporting.annual_report import _customer_lifecycle_events_section
    from simulation.customer_events import svt_conversion_event
    from tools.population_anchor import _churn_by_year

    row = svt_conversion_event(
        customer_id="SYN-2016-001", event_date="2019-03-01", commodity="electricity",
        company_churn_estimate=0.1,
    )
    assert row["event_type"] == "renewed" and row["departure_rolled"] is False
    # Nothing was rolled, so nothing reads as a roll; the world gave this term no exit at all.
    assert row["random_roll"] is None and row["effective_retention_probability"] is None
    assert row["realized_churn_probability"] == 0.0

    assert _churn_by_year([row])[2019]["renewals"] == 1
    assert compute_churn_model_performance([row], [], [])["true_negatives"] == 1
    section = _customer_lifecycle_events_section({"customer_events": [row]})
    assert "Retained: **1**" in section and "not rolled" in section
