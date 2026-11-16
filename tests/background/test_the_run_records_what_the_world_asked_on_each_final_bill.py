"""The run records what the world asked on each mover's final bill, beside its face.

The defect this names (`docs/staging/records/SEAT_RESULT_THE_16_NOV_BOOK_ON_LEVEL_DD_W1_W4_2026-11-16.md`):
the 16 Nov book could not read LEVEL_DD s.9.8 W1 or W4, nor say whether 37d934286's final-bill net fired,
because nothing in the run JSON held the world's ask. The page builds a paid bill's payment from its
face, so a page-side read of "the ask" was the face and could not move. The control is keyed to the
property: the recorded ask IS the amount the world presented, on every leg, netted or not.
"""
from __future__ import annotations

import pytest

import background.live_payment_triad as lpt
import tests.background.test_a_level_leavers_final_bill_asks_its_face_less_the_schedules_surplus as base

FINAL, _leave = base.FINAL, base._leave
asked = base.asked  # the fixture: every amount the world presented, every draw collected


def _row(t):
    nets = t.final_month_nets()
    assert nets["legs"] == len(nets["rows"]) == 1
    return nets, nets["rows"][0]


def test_the_partition_is_reachable_a_netted_leg_and_a_face_leg(asked):
    """Both sides of the branch can be recorded: one leg the ledger credit netted, one it could not."""
    netted, face = _row(_leave("LVL-PART", 120.00))[1], _row(_leave("FACE", 50.00, on_level=False))[1]
    assert netted["netted_ledger_credit"] and not face["netted_ledger_credit"]


def test_the_recorded_ask_is_what_the_world_presented(asked):
    for cid, face_gbp, on_level in (("LVL-PART", 120.00, True), ("LVL-ALL", 50.00, True),
                                    ("FACE", 50.00, False)):
        _, r = _row(_leave(cid, face_gbp, on_level=on_level))
        assert r["ask_gbp"] == pytest.approx(asked[(cid, FINAL)])
        assert r["face_gbp"] == pytest.approx(face_gbp)
        assert r["ask_gbp"] == pytest.approx(r["face_gbp"] - r["credit_taken_gbp"])
        assert r["result"] == "success"


def test_a_level_leg_carries_its_ledger_balance_and_the_netted_sum(asked):
    """GBP 90 of surplus (3 x 60 collected against 3 x 30 billed) against a 120 face: 30 asked."""
    nets, r = _row(_leave("LVL-PART", 120.00))
    assert r["ever_level"] and r["ledger_balance_gbp"] == pytest.approx(-90.00)
    assert r["waiting_credit_gbp"] == pytest.approx(0.0)
    assert r["credit_taken_gbp"] == pytest.approx(90.00)
    assert nets["netted_ledger_credit_legs"] == 1
    assert nets["netted_ledger_credit_gbp"] == pytest.approx(90.00)


def test_a_never_level_leg_records_no_ledger_read(asked):
    nets, r = _row(_leave("FACE", 50.00, on_level=False))
    assert not r["ever_level"] and r["ledger_balance_gbp"] is None
    assert nets["netted_ledger_credit_legs"] == 0 and nets["netted_ledger_credit_gbp"] == 0


def test_only_the_final_month_is_recorded(asked):
    t = _leave("LVL-PART", 120.00)
    assert [r["bill_month"] for r in t.final_month_nets()["rows"]] == ["2025-04"]
    assert lpt.LivePaymentTriad().final_month_nets() == {
        "legs": 0, "ever_level_legs": 0, "netted_ledger_credit_legs": 0,
        "netted_ledger_credit_gbp": 0, "rows": []}
