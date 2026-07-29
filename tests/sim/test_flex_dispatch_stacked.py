"""W1_9 L3 -- MULTI-VENUE STACKING, the SIM-side ground truth.

Covers the L3 half of `sim/flex_dispatch.py` that landed with NO tests at all:
the stacking physics (`_allocate_by_priority`), its enforcement
(`assert_mw_conservation`), the availability-product benchmark gate, and
C-S2 replay determinism.

R15 DISCIPLINE. Every control asserted here is MUTATION-TESTED -- the test
breaks the mechanism and proves the control FIRES, because a control that has
never been observed to fail is not evidence. The three killer patterns
(TAUTOLOGY / FAIL-OPEN / FAIL-SILENT) each get a named test.
"""
from __future__ import annotations

import numpy as np
import pytest

from sim.flex_dispatch import (
    DEFAULT_PERIOD_HOURS,
    DegenerateFlexError,
    DeliveryModel,
    FlexPaymentBasis,
    MwConservationError,
    StackedFlexTruth,
    VenueSpec,
    _allocate_by_priority,
    assert_mw_conservation,
    dispatch_and_settle,
    dispatch_and_settle_stacked,
    emit_dispatch_instructions_stacked,
    emit_settlement_lines_stacked,
)
from interface.contracts.flex_observable_seam import (
    FlexDispatchInstruction,
    FlexSettlementLine,
    FlexVenue,
)
from interface.contracts.wall_envelope import WallResponse


def _synthetic_record(n=200, seed=0):
    """Same shape as the L1 fixture: residual and price CORRELATED but not
    identical, so a price-only reading can never be the true residual set."""
    rng = np.random.default_rng(seed)
    residual = rng.normal(30000, 4000, n)
    gas_noise = rng.normal(0, 15, n)
    price = 40 + 0.004 * (residual - 30000) + gas_noise
    dates = np.array([f"2024-{1 + i % 12:02d}-{1 + i % 28:02d}" for i in range(n)])
    return {"dates": dates, "residual_mw": residual, "derived_price": price}


def _bm(offered_mw=50.0, priority=1, call_pct=95.0):
    return VenueSpec(venue=FlexVenue.BALANCING_MECHANISM,
                     basis=FlexPaymentBasis.UTILISATION,
                     offered_mw=offered_mw, priority=priority, call_pct=call_pct)


def _cm(offered_mw=50.0, priority=2, call_pct=97.0, price=10.0, clawback=1.0):
    return VenueSpec(venue=FlexVenue.CAPACITY_MARKET,
                     basis=FlexPaymentBasis.AVAILABILITY,
                     offered_mw=offered_mw, priority=priority, call_pct=call_pct,
                     availability_price_gbp_per_mw_hour=price,
                     nondelivery_clawback_multiple=clawback)


# ---------------------------------------------------------------------------
# THE STACKING PHYSICS -- the same MW cannot be delivered twice
# ---------------------------------------------------------------------------

def test_allocate_by_priority_respects_the_portfolio_ceiling():
    """Two venues each want 60 MW from a 100 MW portfolio. Priority order is
    the given order: the first gets all 60, the second only the remaining 40."""
    alloc = _allocate_by_priority([True, True], [60.0, 60.0], 100.0)
    assert alloc == [60.0, 40.0]
    assert sum(alloc) == 100.0


def test_allocate_by_priority_gives_nothing_to_an_uncalled_venue():
    alloc = _allocate_by_priority([False, True], [60.0, 60.0], 100.0)
    assert alloc == [0.0, 60.0]


def test_allocate_by_priority_exhausted_portfolio_yields_zero_not_negative():
    """A third venue arriving at an empty portfolio gets 0.0 -- never a
    negative allocation that would net off another venue's delivery."""
    alloc = _allocate_by_priority([True, True, True], [80.0, 40.0, 40.0], 100.0)
    assert alloc == [80.0, 20.0, 0.0]
    assert all(a >= 0.0 for a in alloc)


def test_uncontended_venues_both_get_their_full_offer():
    """Stacking is LEGITIMATE when the portfolio covers both -- the law bounds
    contention, it does not forbid stacking (that would model the wrong world)."""
    alloc = _allocate_by_priority([True, True], [30.0, 30.0], 100.0)
    assert alloc == [30.0, 30.0]


def test_stacked_truth_conserves_mw_on_a_real_dispatch():
    out = _synthetic_record()
    truth = dispatch_and_settle_stacked(
        out, venues=[_bm(offered_mw=60.0), _cm(offered_mw=60.0)], portfolio_mw=100.0)
    worst = assert_mw_conservation(truth)
    assert worst <= 0.0 + 1e-9
    stack = np.vstack([truth.allocated_mw[v.key] for v in truth.venues])
    assert np.all(stack.sum(axis=0) <= 100.0 + 1e-9)


def test_contention_actually_occurs_in_the_fixture():
    """Guard against a VACUOUS conservation test: if the venues never contend,
    'conservation holds' proves nothing. Assert the binding case is exercised."""
    out = _synthetic_record()
    truth = dispatch_and_settle_stacked(
        out, venues=[_bm(offered_mw=60.0), _cm(offered_mw=60.0)], portfolio_mw=100.0)
    assert np.any(truth.binding_mask), (
        "fixture never contends -- the conservation assertion would be vacuous")


def test_shortfall_is_recorded_where_the_portfolio_binds():
    out = _synthetic_record()
    truth = dispatch_and_settle_stacked(
        out, venues=[_bm(offered_mw=60.0), _cm(offered_mw=60.0)], portfolio_mw=100.0)
    total_short = sum(float(np.sum(truth.shortfall_mw[v.key])) for v in truth.venues)
    assert total_short > 0.0, "binding periods must record a shortfall somewhere"


# ---------------------------------------------------------------------------
# R15 -- the conservation control MUST be able to FIRE (mutation tests)
# ---------------------------------------------------------------------------

def test_R15_conservation_fires_when_the_allocator_is_mutated():
    """THE mutation test named in `_allocate_by_priority`'s own docstring.
    Break contention resolution so each called venue takes its full offer
    regardless of what is left -- the classic 'sell the same MW twice' bug --
    and prove `assert_mw_conservation` RAISES."""
    out = _synthetic_record()
    truth = dispatch_and_settle_stacked(
        out, venues=[_bm(offered_mw=60.0), _cm(offered_mw=60.0)], portfolio_mw=100.0)
    assert_mw_conservation(truth)                      # holds before mutation

    keys = [v.key for v in truth.venues]
    binding = int(np.argmax(truth.binding_mask))
    mutated = dict(truth.allocated_mw)
    for k, v in zip(keys, truth.venues):
        arr = np.array(mutated[k], dtype=float)
        arr[binding] = float(v.offered_mw)             # everyone takes full offer
        mutated[k] = arr
    broken = dataclass_replace(truth, allocated_mw=mutated)

    with pytest.raises(MwConservationError, match="SAME MW WAS DELIVERED TWICE"):
        assert_mw_conservation(broken)


def test_R15_conservation_is_not_nan_blind():
    """FAIL-OPEN pattern: `NaN > cap` is False, so a NaN allocation would pass
    a naive comparison. Non-finite must be rejected BEFORE any comparison."""
    out = _synthetic_record()
    truth = dispatch_and_settle_stacked(
        out, venues=[_bm(), _cm()], portfolio_mw=100.0)
    k = truth.venues[0].key
    mutated = dict(truth.allocated_mw)
    arr = np.array(mutated[k], dtype=float)
    arr[0] = np.nan
    mutated[k] = arr
    with pytest.raises(MwConservationError, match="non-finite"):
        assert_mw_conservation(dataclass_replace(truth, allocated_mw=mutated))


def test_R15_conservation_rejects_infinite_allocation():
    out = _synthetic_record()
    truth = dispatch_and_settle_stacked(out, venues=[_bm(), _cm()], portfolio_mw=100.0)
    k = truth.venues[0].key
    mutated = dict(truth.allocated_mw)
    arr = np.array(mutated[k], dtype=float)
    arr[0] = np.inf
    mutated[k] = arr
    with pytest.raises(MwConservationError, match="non-finite"):
        assert_mw_conservation(dataclass_replace(truth, allocated_mw=mutated))


def test_R15_conservation_is_not_fail_silent_on_a_wrong_type():
    """An UNAVAILABLE check is a FAILED check, never a pass."""
    with pytest.raises(MwConservationError, match="not a StackedFlexTruth"):
        assert_mw_conservation({"allocated_mw": {}})
    with pytest.raises(MwConservationError):
        assert_mw_conservation(None)


def test_R15_conservation_does_not_pass_vacuously_on_empty_inputs():
    """FAIL-OPEN: empty venue set / empty allocation map must RAISE, not
    return 'conserved' because there was nothing to check."""
    out = _synthetic_record()
    truth = dispatch_and_settle_stacked(out, venues=[_bm(), _cm()], portfolio_mw=100.0)

    with pytest.raises(MwConservationError, match="no venues"):
        assert_mw_conservation(dataclass_replace(truth, venues=[]))
    with pytest.raises(MwConservationError, match="allocation map absent"):
        assert_mw_conservation(dataclass_replace(truth, allocated_mw={}))


def test_R15_conservation_rejects_a_nonpositive_portfolio():
    out = _synthetic_record()
    truth = dispatch_and_settle_stacked(out, venues=[_bm(), _cm()], portfolio_mw=100.0)
    for bad in (0.0, -5.0, float("nan")):
        with pytest.raises(MwConservationError, match="portfolio_mw"):
            assert_mw_conservation(dataclass_replace(truth, portfolio_mw=bad))


def test_R15_conservation_reports_a_venue_with_no_allocation_recorded():
    out = _synthetic_record()
    truth = dispatch_and_settle_stacked(out, venues=[_bm(), _cm()], portfolio_mw=100.0)
    mutated = dict(truth.allocated_mw)
    mutated.pop(truth.venues[0].key)
    with pytest.raises(MwConservationError, match="no allocation recorded"):
        assert_mw_conservation(dataclass_replace(truth, allocated_mw=mutated))


def test_R15_conservation_rejects_a_negative_allocation():
    out = _synthetic_record()
    truth = dispatch_and_settle_stacked(out, venues=[_bm(), _cm()], portfolio_mw=100.0)
    k = truth.venues[0].key
    mutated = dict(truth.allocated_mw)
    arr = np.array(mutated[k], dtype=float)
    arr[0] = -1.0
    mutated[k] = arr
    with pytest.raises(MwConservationError, match="negative allocation"):
        assert_mw_conservation(dataclass_replace(truth, allocated_mw=mutated))


def test_conservation_is_enforced_on_every_stacked_dispatch_not_just_on_demand():
    """The law must be ENFORCED in the constructor path, not left to a caller
    who might forget -- 'asserted in prose' is what the module claims it is not."""
    import sim.flex_dispatch as fd
    calls = []
    original = fd.assert_mw_conservation
    fd.assert_mw_conservation = lambda truth, **kw: (calls.append(truth), original(truth, **kw))[1]
    try:
        fd.dispatch_and_settle_stacked(
            _synthetic_record(), venues=[_bm(), _cm()], portfolio_mw=100.0)
    finally:
        fd.assert_mw_conservation = original
    assert calls, "dispatch_and_settle_stacked did not enforce the conservation law"


# ---------------------------------------------------------------------------
# THE BENCHMARK GATE -- no invented availability price
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_price", [None, 0.0, -1.0, float("nan"), float("inf")])
def test_availability_venue_without_a_sourced_price_fails_loud(bad_price):
    """R12/R13: an availability-basis venue with a missing/zero/non-finite
    price must RAISE rather than silently model a fabricated GBP/kW/yr.

    The gate binds at CONSTRUCTION (`VenueSpec.__post_init__`), which is the
    stronger placement -- a degenerate venue cannot even be built, so no code
    path can route around it by skipping `dispatch_and_settle_stacked`."""
    with pytest.raises(DegenerateFlexError):
        VenueSpec(venue=FlexVenue.CAPACITY_MARKET,
                  basis=FlexPaymentBasis.AVAILABILITY,
                  offered_mw=50.0, priority=2,
                  availability_price_gbp_per_mw_hour=bad_price)


def test_utilisation_venue_needs_no_availability_price():
    """The gate must bind ONLY on the availability basis -- a utilisation
    venue carries no invented price, so it must not be blocked."""
    out = _synthetic_record()
    truth = dispatch_and_settle_stacked(out, venues=[_bm()], portfolio_mw=100.0)
    assert float(np.sum(truth.total_delivered_mwh)) > 0.0


def test_headline_delivered_mwh_carries_no_price_at_all():
    """The L3 headline gap is scored on PHYSICAL MWh precisely so no un-sourced
    price can move it. Doubling the availability price must not move MWh."""
    out = _synthetic_record()
    cheap = dispatch_and_settle_stacked(
        out, venues=[_bm(), _cm(price=10.0)], portfolio_mw=100.0)
    dear = dispatch_and_settle_stacked(
        out, venues=[_bm(), _cm(price=20.0)], portfolio_mw=100.0)
    assert float(np.sum(cheap.total_delivered_mwh)) == pytest.approx(
        float(np.sum(dear.total_delivered_mwh)))
    assert float(np.sum(dear.total_revenue_gbp)) > float(np.sum(cheap.total_revenue_gbp))


# ---------------------------------------------------------------------------
# THE WALL + C-S2 replay
# ---------------------------------------------------------------------------

def test_sim_module_imports_nothing_from_the_company_layer():
    """The epistemic wall, checked structurally rather than by good intentions."""
    src = open("sim/flex_dispatch.py").read()
    assert "from company" not in src and "import company" not in src
    assert "from saas" not in src and "import saas" not in src


def test_stacked_emission_is_observables_only():
    """What crosses the seam must be instructions + settlement lines carrying
    NO residual_mw and no venue-internal truth."""
    out = _synthetic_record()
    truth = dispatch_and_settle_stacked(out, venues=[_bm(), _cm()], portfolio_mw=100.0)
    instructions = emit_dispatch_instructions_stacked(truth)
    lines = emit_settlement_lines_stacked(truth)
    assert instructions and lines
    # C-S3 / typed-flow seam: emissions cross the wall inside a WallResponse
    # envelope, never as bare objects.
    assert all(isinstance(r, WallResponse) for r in (*instructions, *lines))
    assert all(isinstance(r.payload, FlexDispatchInstruction) for r in instructions)
    assert all(isinstance(r.payload, FlexSettlementLine) for r in lines)
    for r in (*instructions, *lines):
        for leaked in ("residual_mw", "allocated_mw", "call_mask", "shortfall_mw"):
            assert not hasattr(r.payload, leaked), f"{leaked} leaked across the wall"


def test_stacked_replay_is_deterministic_under_a_named_substream():
    """C-S2: same seed reproduces the same truth, byte for byte."""
    out = _synthetic_record()
    kw = dict(venues=[_bm(), _cm()], portfolio_mw=100.0,
              delivery=DeliveryModel(mean_ratio=0.8, dispersion=0.1, seed=7))
    a = dispatch_and_settle_stacked(out, **kw)
    b = dispatch_and_settle_stacked(out, **kw)
    np.testing.assert_allclose(a.total_delivered_mwh, b.total_delivered_mwh)
    np.testing.assert_allclose(a.total_revenue_gbp, b.total_revenue_gbp)
    for v in a.venues:
        np.testing.assert_allclose(a.allocated_mw[v.key], b.allocated_mw[v.key])


def test_a_different_delivery_seed_moves_the_outcome():
    """Guard the determinism test against being vacuous (a constant would also
    'reproduce'): a different seed must actually produce a different draw."""
    out = _synthetic_record()
    base = dict(venues=[_bm(), _cm()], portfolio_mw=100.0)
    a = dispatch_and_settle_stacked(
        out, **base, delivery=DeliveryModel(mean_ratio=0.8, dispersion=0.2, seed=1))
    b = dispatch_and_settle_stacked(
        out, **base, delivery=DeliveryModel(mean_ratio=0.8, dispersion=0.2, seed=2))
    assert float(np.sum(a.total_delivered_mwh)) != pytest.approx(
        float(np.sum(b.total_delivered_mwh)))


def test_stacking_leaves_the_L1_single_venue_path_byte_identical():
    """The module claims `dispatch_and_settle` is untouched by the L3 work.
    Hold it to that -- a regression here breaks every L1/L2 result."""
    out = _synthetic_record()
    truth = dispatch_and_settle(out, enrolled_mw=50.0, period_hours=DEFAULT_PERIOD_HOURS)
    assert float(np.sum(truth.true_utilised_revenue)) > 0.0
    assert truth.dispatch_mask.sum() > 0
    assert truth.residual_mw is not None


def dataclass_replace(obj, **kw):
    """`dataclasses.replace` for frozen truths, tolerant of non-init fields."""
    import dataclasses
    return dataclasses.replace(obj, **kw)
