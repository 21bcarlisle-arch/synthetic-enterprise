"""W1_9 company flex-participation tests (L1): the belief consumes ONLY the
observed price (a price-derived scarcity proxy), computes expected utilisation
revenue, sums observable settlement lines, and imports no SIM internals.
"""
from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest

from company.market.flex_participation import (
    form_participation_belief,
    realised_revenue_from_settlement,
)
from interface.contracts.flex_observable_seam import (
    FlexSettlementLine, FlexVenue,
)
import datetime as dt


def test_belief_predicts_top_price_periods():
    price = np.arange(100.0)
    belief = form_participation_belief(price, enrolled_mw=1.0, period_hours=1.0,
                                       price_percentile=95.0)
    assert belief.n_predicted_dispatch == 5
    assert belief.predicted_dispatch_mask[-1]
    assert not belief.predicted_dispatch_mask[0]
    # revenue zero outside predicted dispatch, price*mw*h inside
    assert np.all(belief.expected_utilised_revenue[~belief.predicted_dispatch_mask] == 0.0)
    assert belief.total_expected_revenue_gbp > 0.0


def test_belief_empty_price_fails_loud():
    with pytest.raises(ValueError):
        form_participation_belief([], enrolled_mw=1.0, period_hours=1.0)


def test_realised_revenue_sums_settlement_lines_and_tolerates_empty():
    assert realised_revenue_from_settlement(None) == 0.0
    assert realised_revenue_from_settlement([]) == 0.0
    lines = [
        FlexSettlementLine(
            settlement_id=f"S{i}", unit_id="U1", venue=FlexVenue.BALANCING_MECHANISM,
            window_start=dt.datetime(2024, 1, i + 1), window_end=dt.datetime(2024, 1, i + 1, 1),
            metered_delivery_mwh=1.0, utilisation_price_gbp_per_mwh=100.0 + i,
            utilisation_payment_gbp=100.0 + i)
        for i in range(3)
    ]
    assert realised_revenue_from_settlement(lines) == pytest.approx(303.0)


def test_no_sim_import():
    """The company flex module reads ONLY the typed observable seam + numpy --
    never sim/simulation (the epistemic wall)."""
    src = Path("company/market/flex_participation.py").read_text()
    tree = ast.parse(src)
    mods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            mods.append(node.module)
        elif isinstance(node, ast.Import):
            mods.extend(a.name for a in node.names)
    for m in mods:
        assert not m.startswith(("sim", "simulation")), f"wall violation: imports {m}"
