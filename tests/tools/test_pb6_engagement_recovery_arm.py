"""The EH-2 arm harness plants what it says it plants, and only that.

The harness exists to say whether the company recovers a planted channel effect. An override that
silently failed to take would read as "the company recovers nothing", so the plant itself is
controlled here, on the world's own multiplier and not on the table the harness edits.
"""
from __future__ import annotations

import pytest

import simulation.household_segments as hs
from tools import _pb6_engagement_recovery_arm as arm


@pytest.fixture(autouse=True)
def _restore_world_table(monkeypatch):
    monkeypatch.setattr(hs, "CIM_SWITCH_RATE_BY_CHANNEL", dict(hs.CIM_SWITCH_RATE_BY_CHANNEL))


def test_each_arm_moves_the_worlds_prepayment_multiplier_where_it_claims():
    head = arm._plant("head")
    assert head["prepayment"] == pytest.approx(0.589, abs=0.001)


def test_the_planted_arm_halves_prepayment_and_the_null_arm_flattens_every_channel(monkeypatch):
    planted = arm._plant("planted")
    assert planted["prepayment"] == pytest.approx(0.307, abs=0.001)
    assert planted["direct_debit"] > 1.0 and planted["standard_credit"] > 1.0
    monkeypatch.setattr(hs, "CIM_SWITCH_RATE_BY_CHANNEL",
                        {c: 0.05 + 0.01 * i for i, c in enumerate(hs.PaymentChannel)})
    assert set(arm._plant("null").values()) == {1.0}


def test_an_unknown_arm_is_refused_by_name():
    with pytest.raises(SystemExit, match="unknown arm 'plantd'"):
        arm._plant("plantd")
