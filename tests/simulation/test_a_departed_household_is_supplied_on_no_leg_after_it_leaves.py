"""A household that leaves is supplied on no leg from its departure date.

A departure is dated the start of the term it is rolled on. The leg it was rolled on used to
settle that whole term anyway, so a household that left on 1 April was billed electricity to
30 June while its gas stopped on the day (SEAT_FINDING_ELECTRICITY_KEEPS_BILLING_ABOUT_THREE_
MONTHS_AFTER_A_HOUSEHOLD_LEAVES_2026-10-05). The 2016-01 .. 2017-04 window holds a departure
rolled on each fuel's leg.
"""
from __future__ import annotations

import pytest

from simulation.household import household_of


@pytest.fixture(scope="module")
def _run(tmp_path_factory):
    from simulation.run_phase2b import main

    return main(
        report_end="2017-04-30",
        gap_ledger_path=tmp_path_factory.mktemp("gap") / "coupled_gap_ledger.json",
    )


def _departed_on(result) -> dict[str, str]:
    events = [e for e in result["customer_events"] if e["event_type"] == "churned"]
    out: dict[str, str] = {}
    for e in events + list(result["svt_departures"]):
        out.setdefault(household_of(e["customer_id"]), e["event_date"])
    return out


def test_departures_on_each_fuel_are_in_the_window(_run):
    """The partition control: a household supplied on each fuel before it left, so the
    assertion below reads both legs and not an empty set."""
    departed = _departed_on(_run)
    fuels = {
        r["commodity"] for r in _run["all_records"]
        if household_of(r["customer_id"]) in departed
        and r["settlement_date"] < departed[household_of(r["customer_id"])]
    }
    assert fuels == {"electricity", "gas"}


def test_no_leg_settles_on_or_after_the_departure_date(_run):
    """Defect guarded: the leg a departure is rolled on settling the rest of its term,
    which bills a household that has gone and puts debt on an account nobody holds."""
    departed = _departed_on(_run)
    after = sorted({
        (household_of(r["customer_id"]), r["commodity"]) for r in _run["all_records"]
        if household_of(r["customer_id"]) in departed
        and r["settlement_date"] >= departed[household_of(r["customer_id"])]
    })
    assert after == []
