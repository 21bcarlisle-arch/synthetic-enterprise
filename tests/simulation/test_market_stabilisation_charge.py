"""The world's MSC lookup: the published series, the window, and the charge per win.

Each test names its own defect.
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

import pytest

from simulation.market_stabilisation_charge import (
    IN_FORCE_FROM,
    IN_FORCE_TO,
    WEEKLY_RATES_GBP_PER_MWH,
    charge_gbp,
    rate_gbp_per_mwh,
)


def _page_series() -> list[tuple[str, float, float]]:
    page = Path(__file__).resolve().parents[2] / (
        "docs/market_research/the_market_stabilisation_charge_2022_2024.md")
    text = page.read_text()
    block = text.split("published   eff_from", 1)[1].split("```", 1)[0]
    rows = re.findall(r"^\S+\s+(\d{4}-\d\d-\d\d)\s+\S+\s+(?:Yes|No)\s+([\d.]+)\s+([\d.]+)\s*$",
                      block, re.M)
    return [(d, float(g), float(e)) for d, g, e in rows]


def test_the_code_carries_the_knowledge_pages_series_exactly():
    """Defect: the table in code drifts from Ofgem's published series on the knowledge page."""
    page = _page_series()
    assert len(page) == 102
    assert list(WEEKLY_RATES_GBP_PER_MWH) == page


def test_the_charge_can_be_zero_and_positive_and_is_zero_outside_the_window():
    """Defect: a lookup that charges every week (or none) passes any one-sided test."""
    before = rate_gbp_per_mwh(IN_FORCE_FROM - dt.timedelta(days=1), "electricity")
    untriggered = rate_gbp_per_mwh(dt.date(2022, 6, 1), "electricity")
    peak = rate_gbp_per_mwh(dt.date(2023, 1, 11), "electricity")
    after = rate_gbp_per_mwh(IN_FORCE_TO + dt.timedelta(days=1), "electricity")
    assert (before, untriggered, after) == (0.0, 0.0, 0.0) and peak == 73.84


def test_the_week_is_chosen_by_its_effective_from_date():
    """Defect: an off-by-one week -- the rate effective from Wed 2023-01-11 must not apply on the 10th."""
    assert rate_gbp_per_mwh(dt.date(2023, 1, 10), "gas") == 19.61
    assert rate_gbp_per_mwh(dt.date(2023, 1, 11), "gas") == 23.37
    assert rate_gbp_per_mwh(dt.date(2023, 1, 17), "gas") == 23.37


def test_the_charge_is_rate_times_the_customers_own_volume():
    """Defect: a typical-household figure charged whatever the customer uses (page section 6)."""
    small = charge_gbp(dt.date(2023, 1, 11), "electricity", 1_450)["amount_gbp"]
    typical = charge_gbp(dt.date(2023, 1, 11), "electricity", 2_900)["amount_gbp"]
    assert typical == pytest.approx(214.14) and small == pytest.approx(typical / 2, abs=0.01)


def test_an_unknown_fuel_is_refused_not_charged_nothing():
    """Defect: a misspelt fuel silently pays no charge."""
    with pytest.raises(KeyError):
        rate_gbp_per_mwh(dt.date(2023, 1, 11), "electric")
