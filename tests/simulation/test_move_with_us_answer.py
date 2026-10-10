"""The household's answer to a move-with-us offer: its next renewal's roll against k * P(stay)."""
from __future__ import annotations

import json

import pytest

from simulation.move_with_us_answer import (
    ACTIVATION_PATH,
    household_moves_with_us,
    move_with_us_active,
    take_up_scale,
)


def test_at_k_one_a_mover_stays_exactly_as_a_renewing_household_would():
    """Defect: a take-up rule that is not the world's renewal answer at k = 1. The taking branch is
    asserted reachable first."""
    assert household_moves_with_us(0.30, 0.60, 1.0)
    assert not household_moves_with_us(0.61, 0.60, 1.0)


def test_at_k_zero_nobody_moves_with_us_even_on_a_zero_roll():
    """Defect: k = 0 letting a roll of exactly 0.0 through, so the k = 0 arm would not equal off."""
    assert not household_moves_with_us(0.0, 0.99, 0.0)


def test_k_scales_the_world_p_stay_between_the_ends():
    """Defect: k applied anywhere but to P(stay)."""
    assert household_moves_with_us(0.29, 0.60, 0.5)
    assert not household_moves_with_us(0.31, 0.60, 0.5)


def test_the_shipped_activation_is_off_and_k_must_be_a_share(tmp_path):
    """Defect: the world answering offers before the director switches it on, or a k outside [0, 1]
    read as a number."""
    assert move_with_us_active() is False
    data = json.loads(ACTIVATION_PATH.read_text())
    data["take_up_scale"]["value"] = 1.5
    bad = tmp_path / "a.json"
    bad.write_text(json.dumps(data))
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        take_up_scale(bad)
