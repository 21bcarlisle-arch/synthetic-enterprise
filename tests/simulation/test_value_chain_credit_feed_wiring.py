"""VALUE_CHAIN observation feed — run-loop wiring (2026-07-24).

Proves the two previously-inert board registers actually MOVE on a real run: run_phase2b
now marks the company's own trading book at an end-of-run OBSERVABLE forward-price snapshot
and surfaces a ``wholesale_credit_exposure`` block and a ``margin_call_book`` block.

R15 (fail-open guard): a truncated window must still open forwards and populate the register,
so an empty/None block reds these tests rather than passing vacuously.
"""
from __future__ import annotations

import pytest

from company.interfaces.sim_interface import StubSimInterface
from simulation.run_phase2b import main as run_phase2b


@pytest.fixture(scope="module")
def _fed_result():
    # SIM_FAST_MODE=1 set by the session autouse fixture; truncated window keeps it quick.
    return run_phase2b(report_end="2017-12-31", sim_interface=StubSimInterface())


def test_wholesale_credit_block_present_and_populated(_fed_result):
    block = _fed_result.get("wholesale_credit_exposure")
    assert block is not None, "credit feed did not run / mark could not be formed"
    # LOAD-BEARING: the truncated window opens attributed forwards, so counterparties > 0.
    # An unwired feed (register never fed) would leave this at 0 -> fail.
    assert block["n_counterparties"] > 0
    for k in (
        "mark_date", "total_net_exposure_gbp", "largest_counterparty",
        "largest_utilisation_pct", "is_limit_breached", "n_breach",
    ):
        assert k in block
    assert block["mark_date"] == "2017-12-31"
    # A current forward mark was actually formed from observable history.
    assert block["current_forward_price_by_commodity"].get("electricity", 0) > 0


def test_margin_call_block_present(_fed_result):
    mc = _fed_result.get("margin_call_book")
    assert mc is not None
    for k in (
        "total_calls", "outstanding_calls", "total_outstanding_gbp",
        "credit_facility_gbp", "is_liquidity_stressed", "stress_events",
    ):
        assert k in mc


def test_registers_move_on_a_real_run(_fed_result):
    """Something MUST move: with the book marked at a shifted price, some counterparty nets
    ITM (credit exposure) and/or some nets OTM (variation margin) — both being exactly zero
    would mean every netted position is precisely flat, i.e. the feed is inert."""
    credit = _fed_result["wholesale_credit_exposure"]
    margin = _fed_result["margin_call_book"]
    moved = credit["total_net_exposure_gbp"] > 0 or margin["total_outstanding_gbp"] > 0
    assert moved, (
        f"neither register moved: net_exposure={credit['total_net_exposure_gbp']} "
        f"outstanding={margin['total_outstanding_gbp']}"
    )
