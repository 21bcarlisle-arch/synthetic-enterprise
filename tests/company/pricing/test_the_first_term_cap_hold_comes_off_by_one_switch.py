"""The acquisition rule that holds a fixed first term at the published cap comes off by one switch,
and the switch is off.

`renewal_rate_chain.FIRST_TERM_CAP_HOLD_DELETED` is the deletion of `ACQUISITION_HELD_AT_CAP_TARIFF_TYPES`,
pre-registered before any book carries it
(`docs/staging/records/SEAT_PREREG_THE_FIRST_TERM_CAP_HOLD_DELETED_2026-11-24.md`).

Each test names the defect it catches.
"""

from __future__ import annotations

import pytest

from company.pricing import renewal_rate_chain as chain
from simulation import svt_rates

VAT = 1.05
ON = "2021-10-01"  # a capped day outside the EPG window, so the ceiling is the published cap
FLAT = {"metering": "NHH", "smart_meter": False}


def _cap() -> float:
    return svt_rates.get_svt_elec_rate_gbp_per_mwh(ON) / VAT


def _contracted(tariff_type: str, term_index: int, struck: float) -> float:
    return chain.decide_renewal_rate(
        customer_id="C1", billing_account="C1", commodity="electricity", term_start=ON,
        tariff_type=tariff_type, term_index=term_index, struck_unit_rate_gbp_per_mwh=struck,
        portfolio_margin_rates=[], prior_term_margin_gbp=None, prior_term_revenue_gbp=0.0,
        is_domestic=True, segment="resi", settled_records=[], customer=FLAT,
    ).unit_rate_gbp_per_mwh


def _partition() -> dict[str, bool]:
    """Which of the three terms the chain held at the cap, each struck 30% above it."""
    cap = _cap()
    return {name: _contracted(tt, ti, cap * 1.3) == pytest.approx(cap, rel=1e-9)
            for name, (tt, ti) in {"first fixed": ("fixed", 0), "renewed fixed": ("fixed", 1),
                                   "default": ("svt", 0)}.items()}


def test_the_switch_is_off_until_the_post_s12g_book_has_been_read():
    """Catches the hold deleted before its book: the pre-registration's predictions can refute
    nothing once a book already carries the change."""
    assert chain.FIRST_TERM_CAP_HOLD_DELETED is False
    assert _partition() == {"first fixed": True, "renewed fixed": False, "default": True}


def test_taking_the_switch_frees_the_first_fixed_term_and_nothing_else(monkeypatch):
    """Catches a switch that cannot be taken (the predicate never reads it, or reads a copy bound
    at import), and one that also frees the default tariff, which the law holds. The whole
    partition is asserted both ways, so a chain that clamps everything or nothing fails."""
    off = _partition()
    monkeypatch.setattr(chain, "FIRST_TERM_CAP_HOLD_DELETED", True)
    taken = _partition()
    assert off["first fixed"] and not taken["first fixed"], (off, taken)
    assert off["default"] and taken["default"], (off, taken)
    assert not off["renewed fixed"] and not taken["renewed fixed"], (off, taken)
    assert _contracted("fixed", 0, _cap() * 1.3) > _cap() * 1.2
