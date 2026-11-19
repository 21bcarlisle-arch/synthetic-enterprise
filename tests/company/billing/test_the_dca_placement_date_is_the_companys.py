"""KNIFE3, 2026-11-19: when a written-off debt is placed with a debt collection agency is the
company's decision. The world asks the door for the placement date and keeps the agency's outcome
and its timing. Each test names the defect it catches."""
import datetime as dt

import simulation.arrears_engine as ae
from company.billing.collections_journey import DCA_PLACEMENT_DAYS, dca_placement_date
from company.interfaces.collections_communication import dca_placement_date as through_the_door


def test_a_debt_is_placed_thirty_days_after_its_write_off():
    # Catches: the company's placement window drifting (a 31-day mutation turns this red).
    assert dca_placement_date(dt.date(2022, 3, 1)) == dt.date(2022, 3, 31)


def test_the_world_reaches_the_rule_only_through_the_door():
    # Catches: the door forwarding a different rule from the one the company holds.
    d = dt.date(2023, 12, 15)
    assert through_the_door(d) == dca_placement_date(d)


def test_the_worlds_placement_stage_is_the_companys_date():
    # Catches: the world keeping its own placement window beside the company's (two homes free to
    # drift). Keyed to the property: the world's PLACED_WITH_DCA date is whatever the company says.
    write_off = dt.date(2021, 6, 10)
    stages = ae._post_writeoff_stages(100.0, write_off, "NEUTRAL")
    assert stages[0]["stage"] == "PLACED_WITH_DCA"
    assert stages[0]["date"] == dca_placement_date(write_off).isoformat()
    assert not hasattr(ae, "DCA_PLACEMENT_DAYS"), "the world holds its own copy of the window again"


def test_the_agency_outcome_runs_from_the_placement_the_company_chose():
    # Catches: the world dating the recovery from the write-off instead of from the placement.
    write_off = dt.date(2021, 6, 10)
    terminal = ae._post_writeoff_stages(100.0, write_off, "NEUTRAL")[-1]
    expected = write_off + dt.timedelta(days=DCA_PLACEMENT_DAYS + ae.DCA_OUTCOME_DAYS)
    assert terminal["date"] == expected.isoformat()
