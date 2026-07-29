"""W1_9 L3 -- the COMPANY side of the stacking triad, and the WALL.

Covers the L3 half of `company/market/flex_participation.py` that landed with
no tests: the point-in-time guard (the epistemic wall, enforced in code), what
the company can learn from its OWN observables, and the belief-vs-truth GAP.

THE POINT OF THE GAP TESTS. The company is ALLOWED to be wrong here. A party
with no evidence of contention assumes none and over-claims stacked revenue --
that over-claim is the measurement this atom exists to produce, so these tests
assert the company DOES over-claim, not that it is accurate. A test suite that
forced the belief to match the truth would be asserting a wall violation.
"""
from __future__ import annotations

import datetime as dt

import numpy as np
import pytest

from company.market.flex_participation import (
    CompanyVenueOffer,
    PointInTimeViolation,
    _allocate_by_declared_priority,
    assert_point_in_time,
    form_stacked_belief,
    learn_contention_rate,
    past_only,
)


class _Obs:
    """Minimal observable stand-in carrying the two seam-visible fields."""

    def __init__(self, window_start, window_end, venue="balancing_mechanism"):
        self.window_start = window_start
        self.window_end = window_end
        self.venue = venue


class _Undateable:
    def __init__(self):
        self.venue = "balancing_mechanism"


_T0 = dt.datetime(2024, 6, 1, 0, 0)


def _obs(hours_from_t0, venue="balancing_mechanism", length_h=1):
    start = _T0 + dt.timedelta(hours=hours_from_t0)
    return _Obs(start, start + dt.timedelta(hours=length_h), venue)


def _offers():
    return [
        CompanyVenueOffer(venue="balancing_mechanism", offered_mw=60.0, priority=1),
        CompanyVenueOffer(venue="capacity_market", offered_mw=60.0, priority=2,
                          is_availability=True,
                          availability_price_gbp_per_mw_hour=10.0),
    ]


# ---------------------------------------------------------------------------
# THE WALL -- point-in-time, enforced not intended
# ---------------------------------------------------------------------------

def test_past_only_keeps_closed_windows_and_drops_future_ones():
    items = [_obs(0), _obs(5), _obs(20)]
    kept = past_only(items, _T0 + dt.timedelta(hours=10))
    assert len(kept) == 2


def test_past_only_boundary_is_inclusive_of_a_window_that_just_closed():
    """A window ending exactly AT as_of is knowable -- settlement had closed."""
    item = _obs(0, length_h=1)
    assert past_only([item], _T0 + dt.timedelta(hours=1)) == [item]


def test_past_only_with_no_as_of_declares_no_constraint_explicitly():
    items = [_obs(0), _obs(100)]
    assert past_only(items, None) == items


def test_R15_point_in_time_guard_fires_on_a_future_observable():
    """The guard must RAISE on exactly the leak it exists to catch: learning
    from a settlement window that had not yet closed."""
    items = [_obs(0), _obs(50)]
    with pytest.raises(PointInTimeViolation, match="learning from the future"):
        assert_point_in_time(items, _T0 + dt.timedelta(hours=10))


def test_R15_point_in_time_guard_is_independent_of_the_filter():
    """TAUTOLOGY check: the guard must not be derived from `past_only`. Feed it
    UNFILTERED items and it must fire -- if it silently filtered first it would
    be checking its own output and could never fail."""
    items = [_obs(0), _obs(50)]
    assert len(past_only(items, _T0 + dt.timedelta(hours=10))) == 1   # filter drops it
    with pytest.raises(PointInTimeViolation):
        assert_point_in_time(items, _T0 + dt.timedelta(hours=10))     # guard still fires


def test_R15_point_in_time_guard_cannot_pass_without_an_as_of():
    """FAIL-SILENT: a guard with nothing to compare against is an UNAVAILABLE
    guard, which is a FAILED guard -- never a pass."""
    with pytest.raises(ValueError, match="as_of is required"):
        assert_point_in_time([_obs(0)], None)


def test_R15_point_in_time_guard_rejects_an_undateable_item():
    """FAIL-OPEN: an item with no window_end must be rejected, not skipped --
    a skipped item is an unproven observable smuggled through the wall."""
    with pytest.raises(PointInTimeViolation, match="carries no window_end"):
        assert_point_in_time([_Undateable()], _T0)


def test_point_in_time_guard_reports_how_many_it_verified():
    """'Verified nothing' must be distinguishable from 'verified 400 items',
    otherwise an empty feed looks identical to a clean one."""
    assert assert_point_in_time([], _T0) == 0
    assert assert_point_in_time([_obs(0), _obs(1)], _T0 + dt.timedelta(hours=10)) == 2


def test_company_module_never_imports_the_sim_layer():
    """The wall, checked structurally: the company may not read SIM internals."""
    src = open("company/market/flex_participation.py").read()
    for banned in ("from sim", "import sim.", "residual_mw"):
        assert banned not in src, f"company layer references {banned!r}"


# ---------------------------------------------------------------------------
# WHAT THE COMPANY CAN LEARN FROM ITS OWN FEED
# ---------------------------------------------------------------------------

def test_learn_contention_rate_from_overlapping_instructions():
    """Two venues instructed in the SAME window = an observed contention."""
    instructions = [
        _obs(0, "balancing_mechanism"), _obs(0, "capacity_market"),   # overlap
        _obs(5, "balancing_mechanism"),                              # solo
    ]
    assert learn_contention_rate(instructions) == pytest.approx(0.5)


def test_learn_contention_rate_cold_start_is_naive_by_belief_not_by_pass():
    """A cold-start company assumes NO contention and gets punished for it.
    That 0.0 is a BELIEF, and the tests below prove it produces an over-claim."""
    assert learn_contention_rate(None) == 0.0
    assert learn_contention_rate([]) == 0.0


def test_learn_contention_rate_sees_full_contention():
    instructions = [
        _obs(0, "balancing_mechanism"), _obs(0, "capacity_market"),
        _obs(5, "balancing_mechanism"), _obs(5, "capacity_market"),
    ]
    assert learn_contention_rate(instructions) == pytest.approx(1.0)


def test_company_priority_allocation_respects_its_own_declared_portfolio():
    """The company's OWN allocator (its belief about contention) still may not
    exceed the portfolio it believes it has."""
    alloc = _allocate_by_declared_priority(
        _offers(), {"balancing_mechanism": True, "capacity_market": True}, 100.0)
    assert sum(alloc.values()) <= 100.0 + 1e-9


# ---------------------------------------------------------------------------
# THE GAP -- the company is ALLOWED to be wrong, and must be
# ---------------------------------------------------------------------------

def _price_series(n=200, seed=0):
    rng = np.random.default_rng(seed)
    residual = rng.normal(30000, 4000, n)
    return 40 + 0.004 * (residual - 30000) + rng.normal(0, 15, n)


def test_a_contention_blind_company_overclaims_stacked_delivery():
    """THE HEADLINE GAP. With contention_awareness=0 the company books both
    venues' MW against one portfolio -- the double-count. An aware company
    books less. The over-claim is the measurement, not a bug."""
    price = _price_series()
    blind = form_stacked_belief(price, offers=_offers(), portfolio_mw=100.0,
                                period_hours=1.0, contention_awareness=0.0)
    aware = form_stacked_belief(price, offers=_offers(), portfolio_mw=100.0,
                                period_hours=1.0, contention_awareness=1.0)
    assert float(np.sum(blind.expected_delivered_mwh)) > float(
        np.sum(aware.expected_delivered_mwh)), (
        "a contention-blind company must over-claim -- if it does not, the "
        "stacking gap is not being modelled at all")


def test_belief_is_formed_from_price_only_never_from_residual():
    """R15 independence: the belief must move when the observable PRICE moves.
    If it did not, it would be reading something else -- i.e. leaking."""
    a = form_stacked_belief(_price_series(seed=1), offers=_offers(),
                            portfolio_mw=100.0, period_hours=1.0)
    b = form_stacked_belief(_price_series(seed=2), offers=_offers(),
                            portfolio_mw=100.0, period_hours=1.0)
    # predicted_call_mask is per-venue: compare each venue's own mask.
    assert set(a.predicted_call_mask) == set(b.predicted_call_mask)
    assert any(not np.array_equal(a.predicted_call_mask[k], b.predicted_call_mask[k])
               for k in a.predicted_call_mask), (
        "belief did not move with the observed price -- it is reading something else")


def test_belief_records_its_own_training_provenance():
    """The belief must carry how much evidence it was actually built on, so a
    cold-start claim cannot masquerade as a well-evidenced one."""
    belief = form_stacked_belief(_price_series(), offers=_offers(),
                                 portfolio_mw=100.0, period_hours=1.0)
    assert hasattr(belief, "n_train_observables")
    assert hasattr(belief, "learned_contention_rate")
    assert belief.n_train_observables == 0     # cold start, honestly reported


def test_as_of_without_a_calendar_is_refused_rather_than_ignored():
    """A point-in-time split needs the calendar it is splitting. Silently
    ignoring `as_of` would be the fail-open version of the wall."""
    with pytest.raises(ValueError, match="as_of given without observed_dates"):
        form_stacked_belief(_price_series(n=4), offers=_offers(), portfolio_mw=100.0,
                            period_hours=1.0, as_of=_T0)


def test_belief_respects_as_of_when_given_a_future_feed():
    """End-to-end wall check: passing observables that run past `as_of` must
    not silently train the belief on them."""
    n = 24
    price = _price_series(n=n)
    dates = [_T0 + dt.timedelta(hours=i) for i in range(n)]
    future_instructions = [_obs(0), _obs(5), _obs(10_000)]
    belief = form_stacked_belief(
        price, offers=_offers(), portfolio_mw=100.0, period_hours=1.0,
        observed_dates=dates, observed_instructions=future_instructions,
        as_of=_T0 + dt.timedelta(hours=10))
    assert belief.n_train_observables <= 2, (
        "belief trained on an observable whose window had not closed at as_of")
