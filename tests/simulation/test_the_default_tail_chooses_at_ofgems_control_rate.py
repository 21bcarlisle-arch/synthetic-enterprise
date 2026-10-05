"""The world's 3+-year default cohort chooses at the rate Ofgem's own control arm did.

Source: Ofgem, *Sustained Engagement* (October 2020), the follow-up of the 2018 Collective Switch
trial. Its 5,000-household no-letter control, all on a default for 3+ years, chose (switched, or
moved tariff internally) at 33% within 17 months, and a choice in the trial window did not predict
the next (31% vs 33%). Read and measured in
`docs/market_research/does_a_households_renewal_engagement_persist.md`.

THE DEFECT IT PREVENTS. Until 2026-10-05 the per-archetype rates were 0.65 / 0.15 / 0.02, unsourced,
which gave this cohort 0.149 and made a past choice a x2.6 predictor of the next. A world that
sticky plants a per-household spread the record does not have, and any estimate a company builds to
find the engaged then ranks better against the world than it could against the market.

Fires on: restoring the old triple (rate 0.15, ratio x2.6), or flattening the spread from the other
side, e.g. DISENGAGED back to 0.02 alone (rate ~0.22).

THE RATIO BOUND IS NOT THE SOURCE'S. The source's interval admits about x1.18; this world gives
x1.26 because the population mean is held at the sourced ~35% and that keeps ACTIVE near 0.50. The
bound here is x1.35 so the control reds on any return toward the old spread. The residual is
filed in the research note §5, not hidden in the tolerance.
"""
from __future__ import annotations

from simulation.household import household_of
from simulation.household_segments import (
    ENGAGEMENT_POPULATION_SHARE,
    active_renewal_probability,
    active_renewal_probability_for_customer,
)

_IDS = [household_of(f"SYN-{2016 + i % 10}-{i:06d}") for i in range(8000)]


def _cohort():
    """Each household's per-renewal p, weighted by the chance it rolled at three anniversaries."""
    ps = [active_renewal_probability_for_customer(c) for c in _IDS]
    return ps, [(1.0 - p) ** 3 for p in ps]


def test_the_three_year_default_cohort_chooses_within_17_months_at_about_a_third():
    ps, w = _cohort()
    # One anniversary for sure inside 17 months, a second with probability 5/12.
    rate = sum(wi * (1.0 - (1.0 - p) * (1.0 - 5.0 / 12.0 * p)) for wi, p in zip(w, ps)) / sum(w)
    assert 0.30 <= rate <= 0.37, f"17-month choose rate {rate:.3f}; Ofgem 2020 control arm: 0.33"


def test_a_past_choice_barely_predicts_the_next_inside_that_cohort():
    ps, w = _cohort()
    total = sum(w)
    e_p = sum(wi * p for wi, p in zip(w, ps)) / total
    e_p2 = sum(wi * p * p for wi, p in zip(w, ps)) / total
    after_choosing = e_p2 / e_p
    after_not = (e_p - e_p2) / (1.0 - e_p)
    # The branch the bound exists to refuse must be reachable at all: a cohort with no spread
    # cannot show persistence, so both conditionals must be real probabilities.
    assert 0.0 < after_not < after_choosing < 1.0
    ratio = after_choosing / after_not
    assert ratio <= 1.35, f"persistence x{ratio:.2f}; Ofgem 2020 control arm: x0.94 (31% vs 33%)"


def test_the_refit_moved_who_chooses_not_how_many():
    """The population mean is the sourced ~35% (`svt_rates_active_passive_2016_2025.md` §4)."""
    mean = sum(ENGAGEMENT_POPULATION_SHARE[lv] * active_renewal_probability(lv)
               for lv in ENGAGEMENT_POPULATION_SHARE)
    assert abs(mean - 0.35) < 0.01, mean
