"""A dual household's gas leg is a probe row beside the electricity roll it rides on.

The world draws a dual household's renewal once, on electricity, so the gas leg is priced and never
rolled. Until 2026-10-19 the probe wrote a row only at a roll, so C34/C35 per household had no pair
to merge, and off and on read 144/546 to the digit on the dual book.
"""
from __future__ import annotations

from tools import decision_probe as dp


def _elec_row():
    return {"customer_id": "H", "billing_account": "H", "term_start": "2020-01-01",
            "commodity": "electricity",
            "true_p_retain": {"flat": 0.9, "value": 0.6},
            "level_grid": {"20": {"offer": 220.0, "p": 0.8}}}


def _held():
    return {"billing_account": "H", "base_gbp_per_mwh": 40.0,
            "offer": {"flat": 45.0, "value": 52.0}, "learned_delta": 0.0,
            "levels": {20: 60.0}, "believed_at_level": {20: 0.7},
            "believed_p_retain": 0.5, "believed_p_retain_capped": 0.5,
            "believed_p_retain_capped_learned": 0.5, "declinable": False}


def test_the_riding_leg_is_kept_exactly_when_its_household_is():
    """Its own offers and base, the world's P(stay) of the roll it rides on, rule by rule."""
    row = dp.riding_leg_row(_elec_row(), _held(), "Hg", "2020-01-01", "gas", 11.0)
    assert row["true_p_retain"] == {"flat": 0.9, "value": 0.6}
    assert row["level_grid"]["20"]["p"] == 0.8 and row["level_grid"]["20"]["offer"] == 60.0
    assert row["offer_gbp_per_mwh"] == {"flat": 45.0, "value": 52.0}
    assert (row["billing_account"], row["commodity"], row["rides_on"]) == ("H", "gas", "H")
    # Scored on its own margin and volume, at the household's chance.
    assert dp.expected_term_margin_gbp(row, "flat", bad_debt=False) == 0.9 * (45.0 - 40.0) * 11.0


def test_the_pair_is_one_decision_per_household_and_two_per_leg():
    """The merge `retention_rise_count` makes from probe rows: both ways, on the same rows."""
    from dataclasses import replace

    from company.policy.decision_policy import CURRENT_POLICY
    from tools.retention_rise_count import count

    elec = {**_elec_row(), "annual_mwh": 3.0, "base_gbp_per_mwh": 200.0,
            "offer_gbp_per_mwh": {"flat": 230.0}}
    gas = dp.riding_leg_row(_elec_row(), _held(), "Hg", "2020-01-01", "gas", 11.0)
    hazards = {(2019, "full_window"): {"H": 0.01}}
    off = count([elec, gas], hazards, 2019, "full_window",
                replace(CURRENT_POLICY, next_best_action_decides_per_household=False))
    on = count([elec, gas], hazards, 2019, "full_window",
               replace(CURRENT_POLICY, next_best_action_decides_per_household=True))
    assert (off["decisions"], on["decisions"]) == (2, 1)
