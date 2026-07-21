"""W1_9 SIM flex-dispatch tests (L1): true (residual-driven) scarcity
schedule, perfect-delivery settlement at the observed price, observables-only
seam emission, and C-S3 dispatch/settlement separability.
"""
from __future__ import annotations

import numpy as np
import pytest

from sim.flex_dispatch import (
    DegenerateFlexError,
    DeliveryModel,
    dispatch_and_settle,
    emit_dispatch_instructions,
    emit_settlement_lines,
    true_scarcity_mask,
)
from interface.contracts.flex_observable_seam import (
    FlexDispatchInstruction, FlexSettlementLine,
)


def _synthetic_record(n=200, seed=0):
    """A small deterministic record: residual and price are CORRELATED but not
    identical (price also carries a gas-like term), so the true (residual)
    scarcity set differs from any price-only set -- the honest triad."""
    rng = np.random.default_rng(seed)
    residual = rng.normal(30000, 4000, n)
    gas_noise = rng.normal(0, 15, n)                 # moves price, not residual
    price = 40 + 0.004 * (residual - 30000) + gas_noise
    dates = np.array([f"2024-{1 + i % 12:02d}-{1 + i % 28:02d}" for i in range(n)])
    return {"dates": dates, "residual_mw": residual, "derived_price": price}


def test_true_scarcity_mask_is_top_tail():
    residual = np.arange(100.0)
    mask = true_scarcity_mask(residual, percentile=95.0)
    assert mask.sum() == 5           # top 5% (>= 95th percentile)
    assert mask[-1] and not mask[0]


def test_true_scarcity_mask_empty_fails_loud():
    with pytest.raises(DegenerateFlexError):
        true_scarcity_mask(np.array([]))


def test_dispatch_only_in_scarcity_periods_and_paid_at_price():
    rec = _synthetic_record()
    truth = dispatch_and_settle(rec, enrolled_mw=2.0, period_hours=1.0)
    assert truth.n_dispatch == int(truth.dispatch_mask.sum())
    # revenue is zero outside dispatch and = enrolled*hours*price inside
    assert np.all(truth.true_utilised_revenue[~truth.dispatch_mask] == 0.0)
    inside = truth.dispatch_mask
    expected = 2.0 * 1.0 * truth.outturn_price[inside]
    assert np.allclose(truth.true_utilised_revenue[inside], expected)
    assert truth.total_true_revenue_gbp > 0.0


def test_revenue_is_linear_in_enrolled_mw():
    """Scale-invariance evidence: doubling enrolment doubles revenue (so the
    normalised triad gap is invariant -- no fabricated MW moves the score)."""
    rec = _synthetic_record()
    a = dispatch_and_settle(rec, enrolled_mw=1.0).total_true_revenue_gbp
    b = dispatch_and_settle(rec, enrolled_mw=2.0).total_true_revenue_gbp
    assert b == pytest.approx(2.0 * a)


def test_seam_emission_is_observable_only_and_async():
    rec = _synthetic_record()
    truth = dispatch_and_settle(rec)
    dispatches = emit_dispatch_instructions(truth)
    settlements = emit_settlement_lines(truth)
    assert len(dispatches) == truth.n_dispatch == len(settlements)
    # payload types are the observable seam types
    assert all(isinstance(r.payload, FlexDispatchInstruction) for r in dispatches)
    assert all(isinstance(r.payload, FlexSettlementLine) for r in settlements)
    # C-S3: matched by correlation_id, settlement observed LATER than dispatch
    dmap = {r.correlation_id: r for r in dispatches}
    for s in settlements:
        assert s.correlation_id in dmap
        assert s.observed_at > dmap[s.correlation_id].observed_at
    # no seam payload exposes residual / true need
    for r in dispatches + settlements:
        assert not hasattr(r.payload, "residual_mw")
        assert not hasattr(r.payload, "true_need")


# --- L2: stochastic portfolio delivery -------------------------------------

def test_l1_perfect_delivery_is_byte_identical():
    """delivery=None must reproduce the L1 perfect-delivery truth exactly (no
    regression: ratio all-ones, revenue unchanged)."""
    rec = _synthetic_record()
    l1 = dispatch_and_settle(rec, enrolled_mw=2.0)
    default = dispatch_and_settle(rec, enrolled_mw=2.0, delivery=None)
    assert np.array_equal(l1.true_utilised_revenue, default.true_utilised_revenue)
    assert np.all(l1.true_delivery_ratio == 1.0)
    assert l1.mean_delivery_ratio == pytest.approx(1.0)


def test_l2_delivery_reduces_delivered_below_instructed():
    """L2: a DeliveryModel makes the true delivered reduction a FRACTION of the
    instructed volume in dispatched periods (rebound/non-response)."""
    rec = _synthetic_record()
    dm = DeliveryModel(mean_ratio=0.7, dispersion=0.05, seed=3)
    truth = dispatch_and_settle(rec, enrolled_mw=2.0, delivery=dm)
    disp = truth.dispatch_mask
    # every dispatched event delivers strictly less than instructed, ratio<1
    assert np.all(truth.true_delivered_mwh[disp] < truth.true_baseline_mwh[disp])
    assert 0.0 < truth.mean_delivery_ratio < 1.0
    # true revenue is correspondingly below the perfect-delivery revenue
    perfect = dispatch_and_settle(rec, enrolled_mw=2.0)
    assert truth.total_true_revenue_gbp < perfect.total_true_revenue_gbp
    # ratios stay within [0, 1] (clipped)
    assert truth.true_delivery_ratio.min() >= 0.0
    assert truth.true_delivery_ratio.max() <= 1.0


def test_l2_delivery_is_deterministic_replay_cs2():
    """C-S2: same seed -> byte-identical delivery ratios (deterministic replay);
    a different seed changes them (genuine stochasticity)."""
    rec = _synthetic_record()
    a = dispatch_and_settle(rec, delivery=DeliveryModel(seed=11))
    b = dispatch_and_settle(rec, delivery=DeliveryModel(seed=11))
    c = dispatch_and_settle(rec, delivery=DeliveryModel(seed=12))
    assert np.array_equal(a.true_delivery_ratio, b.true_delivery_ratio)
    assert not np.array_equal(a.true_delivery_ratio, c.true_delivery_ratio)


def test_l2_settlement_meters_the_stochastic_delivery():
    """The OBSERVABLE metered delivery on the settlement line reflects the true
    (stochastic) delivered reduction, not the instructed volume."""
    rec = _synthetic_record()
    truth = dispatch_and_settle(rec, enrolled_mw=2.0, delivery=DeliveryModel(mean_ratio=0.6, seed=5))
    lines = emit_settlement_lines(truth)
    idx = np.nonzero(truth.dispatch_mask)[0]
    for r, i in zip(lines, idx):
        assert r.payload.metered_delivery_mwh == pytest.approx(float(truth.true_delivered_mwh[i]))
        # metered strictly below the instructed 2.0 MWh in a de-rated world
        assert r.payload.metered_delivery_mwh < 2.0
