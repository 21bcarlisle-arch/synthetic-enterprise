"""The electricity strike prices the levy published for its term's days, not its first day's (B12).

The defect each test names: the strike locked RO+CfD+CM+FiT at the term's first-day level while
settlement bills each day at its own, 1.73 points of unit revenue on the median 2016-19 fixed term
(`docs/staging/records/PREREG_B12_THE_PREMIUM_LOOKBACK_READS_FIXED_TERMS_ONLY_2026-10-15.md`, grade of D).
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from simulation.policy_costs import (
    get_cm_levy_per_mwh,
    get_electricity_policy_cost_per_mwh,
    get_fit_levy_per_mwh,
    published_electricity_policy_cost_over_term,
)


def _on(day):
    iso = day.isoformat()
    return get_electricity_policy_cost_per_mwh(iso) + get_cm_levy_per_mwh(iso) + get_fit_levy_per_mwh(iso)


def _hindsight(start, days=365):
    return sum(_on(start + timedelta(days=i)) for i in range(days)) / days


def test_a_term_priced_after_the_next_april_is_published_carries_it():
    """DEFECT: the first day's level. A January 2018 term spans April 2018, published October 2017."""
    start = date(2018, 1, 1)
    priced = published_electricity_policy_cost_over_term(start, 365, start - timedelta(days=42))
    assert priced > _on(start) + 1.0
    assert priced == pytest.approx(_hindsight(start))


def test_a_level_not_yet_published_is_carried_forward_never_read_ahead():
    """DEFECT: hindsight. A July 2017 term's notice (May) predates the April 2018 level's publication
    (October), so the strike may not price it, though settlement will bill it."""
    start = date(2017, 7, 1)
    priced = published_electricity_policy_cost_over_term(start, 365, start - timedelta(days=42))
    assert _hindsight(start) > priced + 1.0  # the unseen step is real: this test can fail
    assert priced == pytest.approx(_on(start))
