import pytest
from company.analytics.counterfactual_retention import (
    compute_counterfactual_retention, CounterfactualMiss,
)
from company.analytics.threshold_sensitivity import (
    compute_threshold_sensitivity, ThresholdPoint,
)


def _make_event(cid, date, event_type="churned", company_est=0.0, churn_prob=0.5, roll=0.9, eff_retain=0.5):
    return {
        "customer_id": cid,
        "event_date": date,
        "event_type": event_type,
        "company_churn_estimate": company_est,
        "churn_probability": churn_prob,
        "random_roll": roll,
        "effective_retention_probability": eff_retain,
    }


def _make_miss(cid, date, company_est=0.0, expected_margin=500.0, term_revenue=4000.0):
    """A miss record. `term_revenue` is what the discount is a share of (R3, 2026-08-28).

    Defaulted rather than omitted because almost every test here is about something else and
    would otherwise land in the unpriceable branch; the tests that care about that branch pass
    `term_revenue=None` explicitly.
    """
    miss = {
        "customer_id": cid,
        "event_date": date,
        "company_churn_estimate": company_est,
        "expected_term_margin_gbp": expected_margin,
    }
    if term_revenue is not None:
        miss["expected_term_revenue_gbp"] = term_revenue
    return miss


class TestComputeCounterfactualRetention:
    def test_counterfactual_retained_when_roll_within_new_threshold(self):
        miss = _make_miss("C1", "2020-06-30", expected_margin=500.0)
        evt = _make_event("C1", "2020-06-30", churn_prob=0.90, roll=0.15, eff_retain=0.10)
        result = compute_counterfactual_retention([miss], [evt])
        assert len(result.misses) == 1
        assert result.misses[0].counterfactual_retained is True

    def test_counterfactual_not_retained_when_roll_above_new_threshold(self):
        miss = _make_miss("C1", "2020-06-30", expected_margin=500.0)
        evt = _make_event("C1", "2020-06-30", churn_prob=0.99, roll=0.85, eff_retain=0.01)
        result = compute_counterfactual_retention([miss], [evt])
        m = result.misses[0]
        assert m.counterfactual_retained is False
        assert m.value_recovered_gbp == 0.0

    def test_value_recovered_when_retained(self):
        miss = _make_miss("C1", "2020-06-30", expected_margin=1000.0)
        evt = _make_event("C1", "2020-06-30", churn_prob=0.90, roll=0.15, eff_retain=0.10)
        result = compute_counterfactual_retention([miss], [evt])
        assert result.misses[0].value_recovered_gbp == 1000.0

    # ═══════════════════════════════════════════════════════════════════════════════════════
    # R3 (2026-08-28): the offer is a PRICE, not a payment.
    #
    # These four replace `test_resi_offer_cost_applied` and `test_ic_offer_cost_applied`, which
    # asserted that a retained customer cost a flat £50 (£200 for I&C). Those were not stale
    # fixtures -- they were correct assertions about a model that was wrong in kind, so they are
    # deleted rather than re-baselined. The costs are not different numbers of the same thing.
    # ═══════════════════════════════════════════════════════════════════════════════════════

    def test_the_offer_costs_a_share_of_the_customers_own_revenue(self):
        """Not a constant: the 3% detection-gate discount on £4,000 of term revenue is £120."""
        miss = _make_miss("C1", "2020-06-30", expected_margin=500.0, term_revenue=4000.0)
        evt = _make_event("C1", "2020-06-30", churn_prob=0.90, roll=0.15, eff_retain=0.10)
        result = compute_counterfactual_retention([miss], [evt])
        m = result.misses[0]
        assert m.counterfactual_retained is True
        assert m.retention_cost_gbp == pytest.approx(120.0)

    def test_a_bigger_customer_costs_more_to_keep(self):
        """The property, not the number: cost scales with the customer, which a flat sum cannot.

        Same discount, same segment, twice the consumption -- twice the revenue sacrificed. Under
        the old model both cost £50 and an I&C account cost the same as a small business.
        """
        evt = _make_event("C1", "2020-06-30", churn_prob=0.90, roll=0.15, eff_retain=0.10)
        small = compute_counterfactual_retention(
            [_make_miss("C1", "2020-06-30", term_revenue=4000.0)], [evt]).misses[0]
        big = compute_counterfactual_retention(
            [_make_miss("C1", "2020-06-30", term_revenue=8000.0)], [evt]).misses[0]
        assert big.retention_cost_gbp == pytest.approx(2 * small.retention_cost_gbp)

    def test_an_offer_that_fails_costs_nothing(self):
        """THE STRUCTURAL CHANGE, and the one a flat cash cost cannot express.

        The customer left anyway, so there is no term to discount and nothing was sacrificed. A
        £50 payment would have been spent regardless, which is why the old model made offering
        look expensive and the guard blocked tiers it should not have.
        """
        miss = _make_miss("C1", "2020-06-30", expected_margin=500.0, term_revenue=4000.0)
        evt = _make_event("C1", "2020-06-30", churn_prob=0.99, roll=0.85, eff_retain=0.01)
        m = compute_counterfactual_retention([miss], [evt]).misses[0]
        assert m.counterfactual_retained is False
        assert m.retention_cost_gbp == 0.0

    def test_a_miss_with_no_revenue_is_unpriceable_not_free(self):
        """FAIL-CLOSED. The alternative to "we cannot price this" is 0.0, which reads as the most
        attractive intervention on the page. The count is carried on the report, not buried."""
        miss = _make_miss("C1", "2020-06-30", expected_margin=500.0, term_revenue=None)
        evt = _make_event("C1", "2020-06-30", churn_prob=0.90, roll=0.15, eff_retain=0.10)
        result = compute_counterfactual_retention([miss], [evt])
        m = result.misses[0]
        assert m.retention_cost_gbp is None
        assert m.net_value_of_offer_gbp is None
        assert m.was_worth_offering is False
        assert result.misses_that_could_not_be_priced == 1

    def test_net_value_positive_when_margin_exceeds_cost(self):
        miss = _make_miss("C1", "2020-06-30", expected_margin=500.0)
        evt = _make_event("C1", "2020-06-30", churn_prob=0.90, roll=0.15, eff_retain=0.10)
        result = compute_counterfactual_retention([miss], [evt])
        m = result.misses[0]
        assert m.net_value_of_offer_gbp > 0
        assert m.was_worth_offering is True

    def test_was_worth_offering_false_when_negative_margin(self):
        miss = _make_miss("C1", "2020-06-30", expected_margin=-100.0)
        evt = _make_event("C1", "2020-06-30", churn_prob=0.90, roll=0.15, eff_retain=0.10)
        result = compute_counterfactual_retention([miss], [evt])
        assert result.misses[0].was_worth_offering is False

    def test_aggregate_totals(self):
        miss1 = _make_miss("C1", "2020-06-30", expected_margin=500.0)
        miss2 = _make_miss("C2", "2021-06-30", expected_margin=300.0)
        evt1 = _make_event("C1", "2020-06-30", churn_prob=0.90, roll=0.15, eff_retain=0.10)
        evt2 = _make_event("C2", "2021-06-30", churn_prob=0.99, roll=0.85, eff_retain=0.01)
        result = compute_counterfactual_retention([miss1, miss2], [evt1, evt2])
        assert result.total_value_at_stake_gbp == pytest.approx(800.0)
        assert result.would_have_been_retained_count == 1

    def test_empty_no_offer_log(self):
        result = compute_counterfactual_retention([], [])
        assert result.misses == []
        assert result.total_value_at_stake_gbp == 0.0
        assert result.recoverable_count == 0


class TestComputeThresholdSensitivity:
    def _base_events(self):
        return [
            _make_event("C1", "2020-01-01", "renewed", company_est=0.05),
            _make_event("C2", "2021-01-01", "renewed", company_est=0.10),
            _make_event("C3", "2022-01-01", "churned", company_est=0.35),
        ]

    def _base_miss(self):
        return [_make_miss("C4", "2023-01-01", company_est=0.02)]

    def test_returns_curve_with_expected_steps(self):
        result = compute_threshold_sensitivity(self._base_events(), self._base_miss())
        thresholds = [round(pt.threshold, 2) for pt in result.curve]
        assert 0.0 in thresholds
        assert 0.30 in thresholds
        assert 0.50 in thresholds

    def test_recall_at_zero_threshold_is_one(self):
        result = compute_threshold_sensitivity(self._base_events(), self._base_miss())
        pt0 = next(p for p in result.curve if p.threshold == 0.0)
        assert pt0.recall == pytest.approx(1.0)

    def test_tp_fp_fn_tn_sum_to_total(self):
        events = self._base_events()
        no_offer = self._base_miss()
        result = compute_threshold_sensitivity(events, no_offer)
        total = len(events) + 1
        for pt in result.curve:
            assert pt.tp + pt.fp + pt.fn + pt.tn == total

    def test_optimal_threshold_has_max_f1(self):
        result = compute_threshold_sensitivity(self._base_events(), self._base_miss())
        max_f1 = max(pt.f1 for pt in result.curve)
        assert result.optimal_f1 == pytest.approx(max_f1)

    def test_current_threshold_f1_reflects_30pct(self):
        result = compute_threshold_sensitivity(self._base_events(), self._base_miss(), current_threshold=0.30)
        pt30 = next(p for p in result.curve if abs(p.threshold - 0.30) < 1e-9)
        assert result.current_f1 == pytest.approx(pt30.f1)

    def test_empty_events_returns_zero_f1(self):
        result = compute_threshold_sensitivity([], [], current_threshold=0.30)
        assert result.current_f1 == 0.0
        assert result.optimal_f1 == 0.0
