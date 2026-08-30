"""C2 schema half — a departure that is not a renewal must be expressible.

Controls for the departure-event SCHEMA in `simulation/customer_events.py`. Deliberately NOT
controls for the departure PHYSICS: nothing here reads a probability, a roll or a rate, so this
file stays green across the departure-level correction that is in flight beside it, and it cannot
contribute a second moving part to the churn series the §8 pre-registration must read.

WHY THE SCHEMA IS THE HALF THAT CAN LAND FIRST. Wiring `simulation/departure_risks.py` into the
churn chain changes numbers, and the delivery direction holds it until the level move has landed
and been read alone. The schema question is orthogonal to that: whether the event record can carry
a departure whose OCCASION is not a renewal point is a fact about shape, and it is the fact C1b
(SVT inertia) and C6 (home move) are both blocked on. A household that never leaves SVT never
reaches a renewal point, so today it cannot depart at all -- not because the world says it stays,
but because there is no record shape in which its leaving could be written down.

TWO FIELDS, BECAUSE THEY ARE TWO FACTS.
  `departure_occasion`  what brought this account to a decision -- "renewal" is the only occasion
                        this module emits today
  `departure_cause`     which risk fired -- `None` until C2's physics is wired, and `None` on
                        purpose rather than a fabricated default, because a cause invented to fill
                        the field would be indistinguishable on the page from a measured one

THE DEMONSTRATION IS RUNNING THE REAL READERS, NOT ASSERTING ABOUT THEM. `test_the_compatibility_
surface_still_counts_a_departure` feeds a mixed log to `scenario_comparison.extract_scenario_kpis`
and `churn_accuracy_report.compute_churn_model_performance` as they are actually written, because
"the twelve readers keep working" is a claim that can only be settled by calling them.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from company.analytics.churn_accuracy_report import compute_churn_model_performance
from simulation.customer_events import (
    DEPARTURE_OCCASION_RENEWAL,
    departure_event,
    roll_lifecycle_event,
)
from simulation.departure_risks import CAUSE_BILL_SHOCK
from simulation.scenario_comparison import extract_scenario_kpis
from simulation.settlement import CONTRACT_LENGTH_DAYS

#: The real producer's output, not a hand-built dict in its shape. Building the renewal event here
#: would make every assertion below a statement about this file: a fixture that fabricates the
#: observable grades a channel that does not exist, and the field being checked is exactly the one
#: a fixture author would naturally include. So the renewal side comes from `roll_lifecycle_event`
#: on the same flat-record fixture `tests/simulation/test_customer_events.py` uses.
_ACQUISITION_DATE = "2016-01-01"
#: Acquisition + one contract term. Derived rather than written down: 2016 is a leap year, so the
#: first renewal is 2016-12-31, and a hardcoded "2017-01-01" silently produces no event at all.
_FIRST_RENEWAL = (
    date.fromisoformat(_ACQUISITION_DATE) + timedelta(days=CONTRACT_LENGTH_DAYS)
).isoformat()


def _flat_year_of_records(customer_id: str) -> list[dict]:
    """One flat year — no bill shock, so the roll lands on the base rate."""
    return [
        {
            "customer_id": customer_id,
            "settlement_date": f"2016-{month:02d}-{day:02d}",
            "settlement_period": 1,
            "consumption_kwh": 50.0,
            "unit_rate_gbp_per_mwh": 150.0,
            "revenue_gbp": 7.5,
            "wholesale_cost_gbp": 5.0,
            "margin_gbp": 2.5,
            "capital_cost_gbp": 0.1,
            "net_margin_gbp": 2.4,
        }
        for month in range(1, 13)
        for day in range(1, 29)
    ]


def _real_renewal_event(customer_id: str = "C5") -> dict:
    customers = [{
        "customer_id": customer_id,
        "commodity": "electricity",
        "segment": "SME",
        "epc_rating": "D",
        "acquisition_date": _ACQUISITION_DATE,
    }]
    event = roll_lifecycle_event(
        customer_id, _FIRST_RENEWAL, "electricity",
        _flat_year_of_records(customer_id), customers,
    )
    assert event is not None, "the fixture stopped producing a renewal event at all"
    return event


def test_a_departure_that_is_not_a_renewal_can_be_written_down():
    """DEFECT: the event schema can only express a departure that happened at a renewal point.

    This is the whole C1b blocker. Before this landed, `roll_lifecycle_event` was the only producer
    of a lifecycle event and it is called only for electricity legs at `term_index >= 1`, so a
    household leaving between renewals had no record shape at all. The control fails if
    `departure_event` stops accepting a non-renewal occasion.
    """
    event = departure_event(
        customer_id="BA-0007",
        event_date="2022-04-01",
        commodity="electricity",
        occasion="home_move",
    )

    assert event["event_type"] == "churned"
    assert event["departure_occasion"] == "home_move"
    assert event["departure_occasion"] != DEPARTURE_OCCASION_RENEWAL


def test_a_departure_without_a_measured_cause_says_so_rather_than_naming_one():
    """DEFECT: the cause field carries a default that reads on the page as a measurement.

    C2's physics is not wired, so no departure in this world has a measured cause. A default of
    `bill_shock` -- the first entry in `ORDERED_CAUSES`, and the tempting one -- would put a reason
    mix of 100%/0%/0% in front of a reader with nothing to distinguish it from a result.
    """
    event = departure_event(
        customer_id="BA-0007", event_date="2022-04-01", commodity="electricity",
        occasion="home_move",
    )
    assert event["departure_cause"] is None

    renewal = _real_renewal_event()
    assert "departure_cause" in renewal, "the real producer does not carry the cause field at all"
    assert renewal["departure_cause"] is None
    assert renewal["departure_occasion"] == DEPARTURE_OCCASION_RENEWAL


def test_a_cause_the_risk_module_does_not_publish_is_refused():
    """DEFECT: the cause field accepts any string, so a typo becomes a fourth risk silently.

    `financial_stress` is the specific string this refusal exists for: the C2 design listed it as a
    fourth risk and `simulation/departure_risks.py` demotes it to a modulator, so it is exactly the
    name a later caller is most likely to pass in good faith.
    """
    with pytest.raises(ValueError, match="financial_stress"):
        departure_event(
            customer_id="BA-0007", event_date="2022-04-01", commodity="electricity",
            occasion="home_move", cause="financial_stress",
        )

    accepted = departure_event(
        customer_id="BA-0007", event_date="2022-04-01", commodity="electricity",
        occasion="home_move", cause=CAUSE_BILL_SHOCK,
    )
    assert accepted["departure_cause"] == CAUSE_BILL_SHOCK


def test_a_renewal_occasion_is_refused_by_the_non_renewal_constructor():
    """DEFECT: two producers can both emit renewal-point events, and they can disagree.

    `roll_lifecycle_event` owns the renewal point -- it is the only thing holding the roll, the
    probabilities and the factor decomposition. A second constructor able to mint a renewal event
    without any of that would put records in the log that look like renewal decisions and carry
    none of the evidence for one.
    """
    with pytest.raises(ValueError, match="roll_lifecycle_event"):
        departure_event(
            customer_id="BA-0007", event_date="2022-04-01", commodity="electricity",
            occasion=DEPARTURE_OCCASION_RENEWAL,
        )


def test_the_compatibility_surface_still_counts_a_departure():
    """DEFECT: adding an occasion field makes existing `event_type == "churned"` readers miss it.

    Run the readers as written rather than asserting about them. Both branch on `event_type`
    alone, so a non-renewal departure must present as `churned` to them or every churn count,
    recall figure and CLV denominator in this repository silently drops a class of departure.
    """
    renewal = _real_renewal_event()
    log = [
        renewal,
        departure_event(
            customer_id="BA-0003", event_date="2022-06-01", commodity="electricity",
            occasion="home_move",
        ),
    ]
    renewal_churned = renewal["event_type"] == "churned"

    expected = 1 + int(renewal_churned)

    kpis = extract_scenario_kpis({"customer_events": log, "years": {}}, "compat")
    assert kpis["total_churn"] == expected, (
        "a non-renewal departure is not counted as a departure"
    )

    perf = compute_churn_model_performance(log, [], [])
    assert perf["total_churn_events"] == expected, (
        "a non-renewal departure is invisible to the accuracy report"
    )


def test_the_renewal_point_population_is_recoverable_from_the_occasion():
    """DEFECT: once non-renewal departures exist, no reader can isolate renewal-point decisions.

    Keyed to the PROPERTY the field exists for, not to any reader's current arithmetic. A rate
    whose denominator is renewal decisions -- `tools/population_anchor._churn_by_year` computes
    exactly that, `churns / (renewals + churns)` -- has to be able to select its own population, or
    the first non-renewal departure moves it with no reader able to say which quantity changed.
    """
    renewal = _real_renewal_event()
    log = [
        renewal,
        departure_event(
            customer_id="BA-0003", event_date="2022-06-01", commodity="electricity",
            occasion="home_move",
        ),
    ]

    at_renewal = [e for e in log if e["departure_occasion"] == DEPARTURE_OCCASION_RENEWAL]
    assert len(at_renewal) == 1, "the occasion does not isolate the renewal-point population"
    assert at_renewal[0]["event_type"] == renewal["event_type"]

    unfiltered = sum(1 for e in log if e["event_type"] == "churned")
    at_renewal_churns = sum(1 for e in at_renewal if e["event_type"] == "churned")
    assert unfiltered == at_renewal_churns + 1, (
        "the non-renewal departure must be visible in the unfiltered count and absent from the "
        "renewal-point one, or the occasion field is selecting nothing and this is a tautology"
    )
