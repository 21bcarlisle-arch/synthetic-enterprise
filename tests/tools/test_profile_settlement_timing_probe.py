"""The timing difference is timing alone: the profile carries the home's own volume, so only WHEN
it is used can move the result. Each test names the defect it catches."""
from tools.profile_settlement_timing_probe import overnight_share, year_delta

_DATES = ["2022-01-10", "2022-01-11"]
_PRICES = {(d, p): (300.0 if 33 <= p <= 40 else 100.0) for d in _DATES for p in range(1, 49)}
_FLAT = lambda d: [1.0] * 48  # noqa: E731


def _delta(shape, profile=_FLAT):
    _, own, prof = year_delta(shape, profile, _PRICES, _DATES)
    return own - prof


def test_a_home_whose_shape_is_the_profile_at_any_volume_has_no_timing_difference():
    """Catches dropping the annual true-up: a home using twice the profile's volume in the
    profile's own shape would read as a timing cost."""
    assert abs(_delta(lambda d: [2.0] * 48)) < 1e-9


def test_volume_moved_into_the_dear_periods_costs_more_and_into_the_cheap_ones_less():
    """Catches a sign flip, or a delta that ignores price."""
    peaky = lambda d: [3.0 if 33 <= i + 1 <= 40 else 1.0 for i in range(48)]  # noqa: E731
    night = lambda d: [3.0 if i < 14 else 1.0 for i in range(48)]  # noqa: E731
    assert _delta(peaky) > 0
    assert _delta(night) < 0


def test_unpriced_periods_are_left_out_of_both_sides():
    """Catches a profile scaled over periods the home was never priced in."""
    prices = {k: v for k, v in _PRICES.items() if k[1] != 1}
    shape = lambda d: [50.0] + [1.0] * 47  # noqa: E731
    kwh, _, _ = year_delta(shape, _FLAT, prices, _DATES)
    assert kwh == 2 * 47


def test_overnight_share_reads_periods_one_to_fourteen():
    assert overnight_share(lambda d: [1.0] * 14 + [0.0] * 34, _DATES) == 1.0
    assert overnight_share(_FLAT, _DATES) == 14 / 48
