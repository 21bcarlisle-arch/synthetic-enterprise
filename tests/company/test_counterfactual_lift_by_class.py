"""Tests for company.analytics.counterfactual_retention Part 4 extension --
per-intervention-class lift-per-pound (docs/staging/DECISION_LOOP_AND_EVENT_LEDGER.md).
"""
import pytest

from company.analytics.counterfactual_retention import (
    classify_intervention,
    effectiveness_for_discount,
    compute_counterfactual_lift_by_class,
    compute_counterfactual_retention,
    ASSUMED_EFFECTIVENESS_PER_DISCOUNT_POINT,
    _RETENTION_EFFECTIVENESS,
)


def _make_event(cid, date, churn_prob=0.5, roll=0.9, eff_retain=0.5):
    return {
        "customer_id": cid,
        "event_date": date,
        "event_type": "churned",
        "churn_probability": churn_prob,
        "random_roll": roll,
        "effective_retention_probability": eff_retain,
    }


def _make_miss(cid, date, expected_margin=500.0, no_offer_reason=None, would_be_discount_pct=None,
               term_revenue=4000.0):
    """`term_revenue` is what a retention discount is a share of (R3, 2026-08-28).

    Defaulted so the tests below stay about lift-per-class; pass `term_revenue=None` for the
    unpriceable branch, which is asserted in its own test rather than reached by accident.
    """
    m = {
        "customer_id": cid,
        "event_date": date,
        "company_churn_estimate": 0.5,
        "expected_term_margin_gbp": expected_margin,
    }
    if term_revenue is not None:
        m["expected_term_revenue_gbp"] = term_revenue
    if no_offer_reason is not None:
        m["no_offer_reason"] = no_offer_reason
    if would_be_discount_pct is not None:
        m["would_be_discount_pct"] = would_be_discount_pct
    return m


class TestClassifyIntervention:
    def test_below_threshold_is_detection_gate(self):
        cls, pct = classify_intervention("below_threshold", None)
        assert cls == "detection_gate"
        assert pct == pytest.approx(0.03)

    def test_missing_reason_defaults_to_detection_gate(self):
        cls, pct = classify_intervention(None, None)
        assert cls == "detection_gate"

    def test_uneconomical_high_tier(self):
        cls, pct = classify_intervention("uneconomical", 0.08)
        assert cls == "uneconomical_high"
        assert pct == pytest.approx(0.08)

    def test_uneconomical_medium_tier(self):
        cls, pct = classify_intervention("uneconomical", 0.05)
        assert cls == "uneconomical_medium"

    def test_uneconomical_low_tier(self):
        cls, pct = classify_intervention("uneconomical", 0.03)
        assert cls == "uneconomical_low"

    def test_uneconomical_unknown_tier_falls_back_to_other(self):
        cls, pct = classify_intervention("uneconomical", 0.10)
        assert cls == "uneconomical_other"
        assert pct == pytest.approx(0.10)

    def test_uneconomical_without_discount_is_detection_gate(self):
        """Old-shape dicts (pre-Part-4) never had would_be_discount_pct."""
        cls, pct = classify_intervention("uneconomical", None)
        assert cls == "detection_gate"


class TestEffectivenessForDiscount:
    def test_medium_tier_matches_historical_flat_assumption(self):
        """5% tier must reproduce the original flat _RETENTION_EFFECTIVENESS=0.20
        unchanged -- Part 4 extends, does not silently recalibrate, the baseline."""
        assert effectiveness_for_discount(0.05) == pytest.approx(_RETENTION_EFFECTIVENESS)

    def test_high_tier_exceeds_medium(self):
        assert effectiveness_for_discount(0.08) > effectiveness_for_discount(0.05)

    def test_low_tier_below_medium(self):
        assert effectiveness_for_discount(0.03) < effectiveness_for_discount(0.05)

    def test_capped_at_ninety_five_percent(self):
        assert effectiveness_for_discount(1.0) == pytest.approx(0.95)

    def test_quantified_per_point(self):
        assert effectiveness_for_discount(0.08) == pytest.approx(
            ASSUMED_EFFECTIVENESS_PER_DISCOUNT_POINT * 8.0
        )


class TestComputeCounterfactualLiftByClass:
    def test_classes_are_kept_separate(self):
        misses = [
            _make_miss("C1", "2020-01-01", expected_margin=1000.0,
                       no_offer_reason="below_threshold"),
            _make_miss("C2", "2020-01-01", expected_margin=1000.0,
                       no_offer_reason="uneconomical", would_be_discount_pct=0.08),
        ]
        events = [
            _make_event("C1", "2020-01-01", roll=0.1, eff_retain=0.05),
            _make_event("C2", "2020-01-01", roll=0.1, eff_retain=0.05),
        ]
        result = compute_counterfactual_lift_by_class(misses, events)
        classes = {c.intervention_class for c in result.by_class}
        assert classes == {"detection_gate", "uneconomical_high"}

    def test_higher_tier_has_higher_assumed_effectiveness(self):
        misses = [
            _make_miss("C1", "2020-01-01", expected_margin=1000.0,
                       no_offer_reason="uneconomical", would_be_discount_pct=0.03),
            _make_miss("C2", "2020-01-01", expected_margin=1000.0,
                       no_offer_reason="uneconomical", would_be_discount_pct=0.08),
        ]
        events = [
            _make_event("C1", "2020-01-01", roll=0.1, eff_retain=0.05),
            _make_event("C2", "2020-01-01", roll=0.1, eff_retain=0.05),
        ]
        result = compute_counterfactual_lift_by_class(misses, events)
        by_cls = {c.intervention_class: c for c in result.by_class}
        assert (by_cls["uneconomical_high"].assumed_effectiveness
                > by_cls["uneconomical_low"].assumed_effectiveness)

    def test_lift_per_pound_computed_when_cost_positive(self):
        misses = [_make_miss("C1", "2020-01-01", expected_margin=1000.0,
                              no_offer_reason="below_threshold")]
        events = [_make_event("C1", "2020-01-01", roll=0.05, eff_retain=0.05)]
        result = compute_counterfactual_lift_by_class(misses, events)
        assert len(result.by_class) == 1
        cls = result.by_class[0]
        assert cls.lift_per_pound is not None
        assert cls.total_offer_cost_gbp > 0

    def test_old_shape_no_offer_reason_defaults_to_detection_gate(self):
        """Backward compat: a no_offer_churn_log entry with no no_offer_reason key
        at all (pre-Part-4 shape) must not raise, and classifies as detection_gate."""
        misses = [_make_miss("C1", "2020-01-01", expected_margin=1000.0)]
        events = [_make_event("C1", "2020-01-01", roll=0.05, eff_retain=0.05)]
        result = compute_counterfactual_lift_by_class(misses, events)
        assert result.by_class[0].intervention_class == "detection_gate"

    def test_empty_log_returns_no_classes(self):
        result = compute_counterfactual_lift_by_class([], [])
        assert result.by_class == []
        assert result.misses == []

    def test_miss_count_matches_class_membership(self):
        misses = [
            _make_miss("C1", "2020-01-01", no_offer_reason="uneconomical", would_be_discount_pct=0.05),
            _make_miss("C2", "2020-01-01", no_offer_reason="uneconomical", would_be_discount_pct=0.05),
            _make_miss("C3", "2020-01-01", no_offer_reason="below_threshold"),
        ]
        events = [_make_event(c, "2020-01-01") for c in ("C1", "C2", "C3")]
        result = compute_counterfactual_lift_by_class(misses, events)
        by_cls = {c.intervention_class: c for c in result.by_class}
        assert by_cls["uneconomical_medium"].miss_count == 2
        assert by_cls["detection_gate"].miss_count == 1


class TestBackwardCompatibility:
    def test_compute_counterfactual_retention_unaffected_by_new_fields(self):
        """The original Phase NO function keeps its flat-effectiveness behaviour
        even though CounterfactualMiss now carries intervention_class metadata."""
        miss = _make_miss("C1", "2020-06-30", expected_margin=500.0,
                           no_offer_reason="uneconomical", would_be_discount_pct=0.08)
        evt = _make_event("C1", "2020-06-30", roll=0.15, eff_retain=0.10)
        result = compute_counterfactual_retention([miss], [evt])
        assert result.misses[0].counterfactual_retained is True
        assert result.misses[0].intervention_class == "uneconomical_high"


class TestUnpriceableMissesAreNotFree:
    """R3, 2026-08-28: a class row must not report a cost of zero for offers it could not price.

    Summing `None` as 0.0 is the fail-open shape the price model replaced a flat £50 with. A
    class whose misses carry no term revenue would report `total_offer_cost_gbp = 0` and an
    infinite-looking lift, which is the most attractive row on the page.
    """

    def test_the_unpriceable_count_travels_on_the_row(self):
        misses = [
            _make_miss("C1", "2020-01-01", no_offer_reason="below_threshold"),
            _make_miss("C2", "2020-01-01", no_offer_reason="below_threshold",
                       term_revenue=None),
        ]
        events = [_make_event("C1", "2020-01-01", roll=0.05, eff_retain=0.05),
                  _make_event("C2", "2020-01-01", roll=0.05, eff_retain=0.05)]
        cls = compute_counterfactual_lift_by_class(misses, events).by_class[0]
        assert cls.miss_count == 2
        assert cls.misses_that_could_not_be_priced == 1

    def test_the_cost_total_excludes_what_it_could_not_price(self):
        """MUTATION: were `None` summed as zero, these two rows would report the same cost."""
        events = [_make_event("C1", "2020-01-01", roll=0.05, eff_retain=0.05)]
        priced = compute_counterfactual_lift_by_class(
            [_make_miss("C1", "2020-01-01", no_offer_reason="below_threshold")], events,
        ).by_class[0]
        unpriceable = compute_counterfactual_lift_by_class(
            [_make_miss("C1", "2020-01-01", no_offer_reason="below_threshold",
                        term_revenue=None)], events,
        ).by_class[0]
        assert priced.total_offer_cost_gbp > 0
        assert unpriceable.total_offer_cost_gbp == 0
        assert unpriceable.lift_per_pound is None, (
            "a class nobody could price must not report a lift per pound"
        )
        assert unpriceable.misses_that_could_not_be_priced == 1
