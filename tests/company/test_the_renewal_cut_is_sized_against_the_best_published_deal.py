"""B8 Q5: the renewal cut, under "price_match", meets the market's best published deal on the day.

The defects each test names: the renewal desk sizing its own match instead of reading the save's
(two answers to one question); a cut offered where our re-fix already sits at or below the market's
best; a cut that takes the rate below our own cost; the published gap missing for the quarters a
renewal decides in, so the match silently offers nothing before CSS.
"""
from __future__ import annotations

import pytest

from company.crm.save_offer import price_match_save_rate
from company.interfaces.growth_desk import retention_cut_share_at_price_match
from company.policy.decision_policy import CURRENT_POLICY, NAIVE_POLICY
from simulation.save_on_loss_notice import published_best_deal_gap_share

_DEFAULT = 140.0


def _cut(unit_rate, gap=0.30, floor=60.0):
    return retention_cut_share_at_price_match(
        unit_rate, published_default_rate=_DEFAULT, published_best_deal_gap_share=gap,
        cost_floor=floor)


def test_every_branch_of_the_match_can_be_taken():
    """Control over the partition: an offer at the match, an offer at the floor, and no offer."""
    at_match, at_floor, none = _cut(120.0), _cut(120.0, floor=110.0), _cut(95.0)
    assert at_match is not None and at_floor is not None and none is None
    assert at_match != at_floor


def test_the_cut_lands_the_rate_on_the_saves_own_match():
    """Defect: a second sizing rule. The offered rate is exactly the save's price match."""
    for unit_rate, gap, floor in ((120.0, 0.30, 60.0), (120.0, 0.30, 110.0), (135.0, 0.05, 90.0)):
        share = _cut(unit_rate, gap, floor)
        assert unit_rate * (1.0 - share) == pytest.approx(
            price_match_save_rate(unit_rate, _DEFAULT, gap, floor))


def test_no_cut_where_the_fix_already_meets_the_best_deal():
    """Defect: discounting a re-fix that a switcher could not beat. 140 x 0.7 = 98 >= 95."""
    assert _cut(95.0) is None
    assert _cut(98.0) is None


def test_the_cut_never_takes_the_rate_below_cost():
    share = _cut(120.0, floor=110.0)
    assert 120.0 * (1.0 - share) == pytest.approx(110.0)


@pytest.mark.parametrize("missing", ["default", "gap", "floor", "rate"])
def test_no_cut_on_a_missing_input(missing):
    kw = dict(published_default_rate=_DEFAULT, published_best_deal_gap_share=0.3, cost_floor=60.0)
    rate = 120.0
    if missing == "rate":
        rate = None
    else:
        kw[{"default": "published_default_rate", "gap": "published_best_deal_gap_share",
            "floor": "cost_floor"}[missing]] = None
    assert retention_cut_share_at_price_match(rate, **kw) is None


def test_no_cut_where_the_market_had_nothing_cheaper():
    assert _cut(139.0, gap=0.0) is None


def test_the_published_gap_covers_every_quarter_a_renewal_decides_in():
    """Defect: a gap filled only for the CSS window leaves the match offering nothing 2016-2022."""
    missing = [f"{y}-Q{q}" for y in range(2016, 2026) for q in range(1, 5)
               if published_best_deal_gap_share(f"{y}-{3 * q - 2:02d}-01") is None]
    assert missing == []


def test_no_standing_policy_sizes_by_the_match():
    """Off on every standing policy, so no standing run moves until it is chosen."""
    assert CURRENT_POLICY.retention_cut_sizing == "risk_tiers"
    assert NAIVE_POLICY.retention_cut_sizing == "risk_tiers"
