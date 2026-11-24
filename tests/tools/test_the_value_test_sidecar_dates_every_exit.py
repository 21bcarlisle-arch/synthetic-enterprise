"""The value test's per-account sidecar dates the end of supply whatever ended it.

`left_at` dated only a priced-renewal departure. A household that left from the default tariff or
moved out had no date, so a kept household's realised tenure could only be bracketed
(`what_a_kept_household_is_worth_beyond_one_term_2026-11-24.md` s.4-5). The defect these tests name
is an exit the run recorded that the sidecar leaves undated, or a non-exit it dates.
"""

from __future__ import annotations

from tools.run_value_cycle_ab import EXIT_ROUTES, _decisions_by_billing_account, account_exits


def _loss(household: str, day: str, fuel: str = "electricity") -> dict:
    return {"customer_id": household, "household": household, "commodity": fuel,
            "event_type": "churned", "event_date": day}


def _phase2b() -> dict:
    return {
        "customer_events": [{"customer_id": "SYN-1", "event_date": "2019-03-01",
                             "event_type": "churned", "departure_cause": "price"}],
        "svt_decisions": [
            {"customer_id": "SYN-2", "event_date": "2020-06-01", "event_type": "stayed",
             "departure_cause": None},
            {"customer_id": "SYN-2", "event_date": "2021-06-01", "event_type": "churned",
             "departure_cause": "contacted"}],
        "erroneous_gains_returned": [{"customer_id": "SYN-3", "returned_on": "2017-02-10"}],
        # SYN-1 is dual fuel: one loss, two legs.
        "leg_departures": [_loss("SYN-1", "2019-03-01"), _loss("SYN-1", "2019-03-01", "gas"),
                           _loss("SYN-2", "2021-06-01"), _loss("SYN-3", "2017-02-10"),
                           _loss("SYN-6", "2022-01-01"),
                           # moved out first, so the move is its exit
                           _loss("SYN-7", "2023-01-01")],
        "home_move_outs": [
            {"household": "SYN-4", "customer_id": "SYN-4", "move_date": "2018-08-15"},
            # followed us on its electricity leg; its gas leg could not follow
            {"household": "SYN-5", "customer_id": "SYN-5", "move_date": "2020-01-20",
             "followed_household": True},
            {"household": "SYN-5", "customer_id": "SYN-5g", "move_date": "2020-01-20",
             "followed_household": False},
            {"household": "SYN-7", "customer_id": "SYN-7", "move_date": "2022-05-05"}],
    }


def test_every_route_can_be_taken():
    """The control over the whole partition: a matcher that never names a route passes the rest."""
    routes = {e["route"] for e in account_exits(_phase2b()).values()}
    assert routes == set(EXIT_ROUTES)


def test_each_exit_carries_the_runs_own_date_route_and_cause():
    exits = account_exits(_phase2b())
    assert exits["SYN-1"] == {"date": "2019-03-01", "route": "priced_renewal", "cause": "price"}
    assert exits["SYN-2"] == {"date": "2021-06-01", "route": "default_tariff",
                              "cause": "contacted"}
    assert exits["SYN-3"]["route"] == "erroneous_gain_returned"
    assert exits["SYN-4"] == {"date": "2018-08-15", "route": "move_out", "cause": None}
    assert exits["SYN-6"]["route"] == "registration_loss_unattributed"


def test_a_household_that_moved_with_us_has_not_ceased():
    assert "SYN-5" not in account_exits(_phase2b())


def test_a_household_leaves_once_at_its_earliest_exit():
    assert account_exits(_phase2b())["SYN-7"]["date"] == "2022-05-05"


def test_a_run_without_leg_departures_still_dates_both_rolled_routes():
    p = _phase2b()
    del p["leg_departures"]
    exits = account_exits(p)
    assert exits["SYN-1"]["route"] == "priced_renewal"
    assert exits["SYN-2"]["date"] == "2021-06-01"


def test_the_sidecar_row_carries_ceased_and_a_stayer_reads_none():
    p = _phase2b()
    p["svt_decisions"].append({"customer_id": "SYN-9", "event_date": "2020-06-01",
                               "event_type": "stayed"})
    rows = _decisions_by_billing_account({"phase2b": p, "bills": []})
    assert rows["SYN-2"]["ceased"]["route"] == "default_tariff"
    assert rows["SYN-2"]["left_at"] is None, "left_at stays the priced-renewal departure alone"
    assert rows["SYN-9"]["ceased"] is None
