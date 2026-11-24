"""The world settles a domestic supplier's electricity grossed up for losses, by one switch, and the
switch is off.

`hedged_settlement.SETTLEMENT_LOSSES_APPLIED` is pre-registered before any book carries it
(`docs/staging/records/SEAT_PREREG_THE_WORLD_SETTLES_ELECTRICITY_LOSSES_2026-11-24.md`). The
multipliers are the cap's own (`docs/domain_artefact_library/regulatory/ofgem_cap_loss_multipliers.json`).

Each test names the defect it catches.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

import pytest

from simulation import hedged_settlement as hs
from simulation import policy_costs

ARTEFACT = (Path(__file__).resolve().parents[2] / "docs" / "domain_artefact_library"
            / "regulatory" / "ofgem_cap_loss_multipliers.json")
DAYS = ["2022-06-01", "2022-06-02"]
START, END = DAYS[0], "2022-06-03"


def _prices():
    return [{"settlementDate": d, "settlementPeriod": p, "systemSellPrice": 150.0 + p}
            for d in DAYS for p in range(1, 49)]


def _shape(_date_str):
    return [0.2 + 0.01 * i for i in range(48)]


def _hedged(segment="resi", economy_7=False):
    return hs.run_hedged_term(
        customer_id="C1", term_start_date=START, term_end_date=END,
        fixed_tariff_rate_gbp_per_mwh=300.0, hedge_price_gbp_per_mwh=120.0, hedge_fraction=0.6,
        monthly_cost_of_capital_gbp=5.0, consumption_shape=_shape,
        system_price_records=_prices(), segment=segment, economy_7=economy_7)


def _deemed(commodity="electricity"):
    return hs.run_deemed_term(
        customer_id="C1", term_start_date=START, term_end_date=END, deemed_premium=0.2,
        consumption_shape=_shape, system_price_records=_prices(), commodity=commodity)


def _sum(rows, key):
    return sum(r[key] for r in rows)


def test_the_switch_is_off_until_the_first_term_hold_book_has_been_read():
    """Catches the losses switched on before their book: the pre-registration's predictions can
    refute nothing once a book already carries the change, and the hold deletion's one-variable
    book would carry two variables."""
    assert hs.SETTLEMENT_LOSSES_APPLIED is False
    assert not any("loss_cost_gbp" in r for r in _hedged() + _deemed())


def test_taking_the_switch_charges_domestic_electricity_its_losses_and_nothing_else(monkeypatch):
    """Catches a switch that cannot be taken, a loss charged on the bill rather than the energy
    bought, a loss charged to a non-domestic supply the cap's table does not describe, and a
    multiplier applied to the levies or network that are charged on the meter. The partition is
    asserted both ways, so a writer that uplifts everything or nothing fails."""
    off = {"resi": _hedged(), "sme": _hedged("SME"), "e7": _hedged(economy_7=True),
           "deemed": _deemed()}
    monkeypatch.setattr(hs, "SETTLEMENT_LOSSES_APPLIED", True)
    on = {"resi": _hedged(), "sme": _hedged("SME"), "e7": _hedged(economy_7=True),
          "deemed": _deemed()}
    single = policy_costs.get_electricity_loss_multiplier(START)
    multi = policy_costs.get_electricity_loss_multiplier(START, multi_register=True)
    assert 1.05 < multi < single < 1.15, (single, multi)

    for key, m in (("resi", single), ("e7", multi), ("deemed", single)):
        before, after = off[key], on[key]
        assert len(before) == len(after) == 96
        assert _sum(after, "wholesale_cost_gbp") == pytest.approx(
            _sum(before, "wholesale_cost_gbp") * m, rel=1e-12), key
        assert _sum(after, "loss_cost_gbp") == pytest.approx(
            _sum(before, "wholesale_cost_gbp") * (m - 1.0), rel=1e-12), key
        for field in ("revenue_gbp", "consumption_kwh", "policy_cost_gbp", "network_cost_gbp"):
            assert _sum(after, field) == _sum(before, field), (key, field)
        assert _sum(after, "margin_gbp") == pytest.approx(
            _sum(before, "margin_gbp") - _sum(after, "loss_cost_gbp"), rel=1e-12), key

    assert on["sme"] == off["sme"]


def test_a_domestic_date_no_published_column_covers_is_refused_not_settled_loss_free(monkeypatch):
    """Catches a reader that falls back to 1.0 outside the workbook: that asserts zero losses,
    the one value known to be wrong."""
    monkeypatch.setattr(hs, "SETTLEMENT_LOSSES_APPLIED", True)
    assert policy_costs.get_electricity_loss_multiplier("2015-03-31") is None
    assert policy_costs.get_electricity_loss_multiplier("2027-01-01") is None
    with pytest.raises(ValueError, match="no published loss multiplier covers 2027-01-01"):
        hs._loss_multiplier("2027-01-01", "resi", False)
    assert hs._loss_multiplier("2027-01-01", "SME", False) == 1.0
    assert not any("loss_cost_gbp" in r for r in _deemed(commodity="gas"))


def test_the_reader_is_the_artefact_s_regional_median_over_the_whole_run():
    """Catches a GB figure that is not the median of the regions it claims to summarise, a
    workbook column read from the wrong section (the TNUoS distribution-only block sits beside
    it), and a run date with no column."""
    periods = json.loads(ARTEFACT.read_text())["periods"]
    for p in periods:
        for block in ("single_rate", "multi_register"):
            regions = p[block]["by_region"]
            assert len(regions) == 14
            assert p[block]["gb_median"] == pytest.approx(statistics.median(regions.values()))
            assert all(1.0 < v < 1.2 for v in regions.values()), (p["cap_period"], block)
        assert policy_costs.get_electricity_loss_multiplier(p["starts"]) == p["single_rate"]["gb_median"]
    # Section 2 (transmission and distribution), not section 1: Eastern 2016/17 reads 1.1083 there
    # and 1.1015 in the distribution-only block.
    first = {p["starts"]: p for p in periods}["2016-04-01"]
    assert first["single_rate"]["by_region"]["Eastern"] == pytest.approx(1.1083, abs=5e-5)
    for year in range(2016, 2026):
        for month in ("01", "04", "07", "10"):
            assert policy_costs.get_electricity_loss_multiplier(f"{year}-{month}-15") is not None
