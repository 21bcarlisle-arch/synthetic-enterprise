"""The section 14 split puts each household's money in exactly one channel, and the dice reach every roll.

Defect named: a split that files a stayer moved across the default's parity edge as a departure
(or as nothing) publishes a transfer as retention value; a dice seed that misses a by-name binding
of the renewal roll answers an offer on a different departure from the one its renewal rolled.
"""
from __future__ import annotations

import pytest

import simulation.customer_events as ce
import simulation.retention_offer as ro
import simulation.run_phase2b as rp2b
import tools.grade_per_customer_switch_seeds as g
import tools.per_customer_switch_arms as arms


def _run(events, gross, net):
    return g.reduce_run({
        "customer_events": [
            {"customer_id": c, "event_date": d, "commodity": f, "event_type": t, "departure_occasion": o}
            for c, d, f, t, o in events],
        "per_cid_pnl": {c: {"gross": v} for c, v in gross.items()},
        "provisioned_net_gbp": net, "churned_billing_accounts": [], "retention_log": []})


FIX = ("renewed", "renewal")
DECLINE = ("renewed", "declined_fix")
LEFT = ("churned", "renewal")
SVT = ("renewed", "svt_conversion")


def test_every_channel_is_reachable_and_each_household_lands_in_the_right_one():
    a = _run([("D1", "2018-01-01", "electricity", *LEFT), ("P1", "2018-02-01", "gas", *FIX),
              ("O1", "2018-03-01", "electricity", *FIX), ("S1", "2018-04-01", "electricity", *FIX)],
             {"D1": 0.0, "P1g": 50.0, "O1": 10.0, "S1": 97.0}, 1000.0)
    b = _run([("D1", "2018-01-01", "electricity", *FIX), ("P1", "2018-02-01", "gas", *DECLINE),
              ("O1", "2018-03-01", "electricity", *SVT), ("S1", "2018-04-01", "electricity", *FIX)],
             {"D1": 300.0, "P1g": 80.0, "O1": 12.0, "S1": 100.0}, 1400.0)
    r = g.split(a, b)
    got = {c: (v["households"], round(v["gross_gbp"], 2)) for c, v in r["channels"].items()}
    # The whole partition at once: a split that sends everything to one channel cannot pass.
    assert got == {"departure": (1, -300.0), "parity": (1, -30.0), "other": (1, -2.0),
                   "same_choice": (1, -3.0)}
    assert round(r["gross_gbp"], 2) == -335.0 and round(r["unattributed_gbp"], 2) == -65.0


def test_an_svt_conversion_against_a_declined_fix_is_the_parity_edge():
    # `svt_conversion` is the household taking the fix unrolled; filing it against a refusal as
    # `other` hid seed 2's whole +£2,866 parity move behind a -£25 reading.
    a = _run([("P2", "2018-02-01", "electricity", *SVT)], {"P2": 70.0}, 0.0)
    b = _run([("P2", "2018-02-01", "electricity", *DECLINE)], {"P2": 20.0}, 0.0)
    assert g.split(a, b)["channels"]["parity"] == {"households": 1, "gross_gbp": 50.0}


def test_a_run_against_itself_reads_zero_in_every_channel():
    a = _run([("P1", "2018-02-01", "gas", *FIX)], {"P1g": 50.0}, 10.0)
    r = g.split(a, a)
    assert r["net_gbp"] == 0 and all(v == {"households": 0, "gross_gbp": 0.0}
                                     for v in r["channels"].values())


def test_one_seed_has_no_interval_and_two_do():
    assert g.mean_interval([5.0]) == (5.0, None)
    m, h = g.mean_interval([1.0, 3.0])
    assert m == 2.0 and h == pytest.approx(12.706 * 1.0)


def test_the_renewal_dice_reach_every_by_name_binding_and_are_restored():
    real = ce.churn_roll_for_renewal
    with arms.renewal_dice_seeded(3) as d:
        assert {"simulation.customer_events", "simulation.retention_offer",
                "simulation.run_phase2b"} <= set(d.calls)
        rolls = {m.churn_roll_for_renewal("A", "2018-01-01") for m in (ce, ro, rp2b)}
        assert len(rolls) == 1 and rolls != {real("A", "2018-01-01")}
    assert ce.churn_roll_for_renewal is ro.churn_roll_for_renewal is rp2b.churn_roll_for_renewal is real


def test_a_seed_that_reached_no_dice_is_refused_and_one_that_did_is_not():
    ok = {"simulation.customer_events": 9, "simulation.retention_offer": 2}
    assert arms.dice_refusal(1, ok, 5, offers=2) is None
    assert arms.dice_refusal(1, {"simulation.customer_events": 9}, 5, offers=0) is None  # flat
    assert "no renewal roll" in arms.dice_refusal(1, {}, 5, offers=0)
    assert "none read the seeded roll" in arms.dice_refusal(1, {"simulation.customer_events": 9}, 5, 2)
    assert "no payment draw" in arms.dice_refusal(1, ok, 0, offers=2)
