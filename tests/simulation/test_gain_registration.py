"""The world states a won switch's registration facts; it draws an erroneous transfer only where a
published rate exists. Each test names the defect it catches."""
from __future__ import annotations

from datetime import date

from interface.contracts.registration_loss_seam import CSS_GO_LIVE as SEAM_CSS_GO_LIVE
from simulation.gain_registration import (
    CSS_GO_LIVE,
    ERRONEOUS_TRANSFER_SHARE_PRE_CSS,
    draw_gain_registration,
)


def _draws(day, n=20000):
    return [draw_gain_registration(f"C{i}", day, f"seed{i}") for i in range(n)]


def test_pre_css_gains_are_erroneous_at_the_published_share():
    """Defect: the world never produces an erroneous transfer (the gap this module closed), or
    produces them at a rate nobody published."""
    share = sum(g["erroneous_transfer_agreed_on"] is not None
                for g in _draws(date(2021, 3, 1))) / 20000
    assert abs(share - ERRONEOUS_TRANSFER_SHARE_PRE_CSS) < 0.0015


def test_no_erroneous_transfer_is_drawn_after_css_and_the_gap_is_named():
    """Defect: the pre-CSS rate carried past go-live, where no rate is published."""
    after = _draws(CSS_GO_LIVE, 5000)
    assert all(g["erroneous_transfer_agreed_on"] is None for g in after)
    assert all(any("named gap 2" in r for r in g["not_drawn"]) for g in after)


def test_registration_delay_is_an_honest_none_not_a_zero():
    """Defect: an undrawn delay published as 0 working days, which reads as measured."""
    g = draw_gain_registration("C1", date(2021, 3, 1), "s")
    assert g["registration_delay_working_days"] is None
    assert any("named gap 3" in r for r in g["not_drawn"])
    assert g["data_regime"] == "synthetic"


def test_the_agreement_falls_inside_the_6a_window():
    """Defect: an agreement dated before the switch, or past reg 6A's 20 working days."""
    agreed = [date.fromisoformat(g["erroneous_transfer_agreed_on"])
              for g in _draws(date(2021, 3, 1)) if g["erroneous_transfer_agreed_on"]]
    assert agreed and all(date(2021, 3, 1) < d <= date(2021, 3, 31) for d in agreed)


def test_the_world_and_the_seam_hold_one_css_go_live_day():
    """Defect: two homes for one date drifting apart."""
    assert CSS_GO_LIVE == SEAM_CSS_GO_LIVE
