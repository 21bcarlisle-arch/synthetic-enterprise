"""Tests for the Part 4 lift-per-pound-by-intervention-class board section
(docs/staging/DECISION_LOOP_AND_EVENT_LEDGER.md), wired into
saas.reporting.annual_report._section_threshold_optimisation.
"""
from saas.reporting.annual_report import _section_threshold_optimisation


def _event(cid, date, roll=0.05, eff_retain=0.05):
    return {
        "customer_id": cid,
        "event_date": date,
        "event_type": "churned",
        "company_churn_estimate": 0.5,
        "churn_probability": 0.9,
        "random_roll": roll,
        "effective_retention_probability": eff_retain,
    }


def _miss(cid, date, no_offer_reason, would_be_discount_pct=None, expected_margin=1000.0,
          term_revenue=None):
    m = {
        "customer_id": cid,
        "event_date": date,
        "company_churn_estimate": 0.5,
        "expected_term_margin_gbp": expected_margin,
        "no_offer_reason": no_offer_reason,
    }
    if would_be_discount_pct is not None:
        m["would_be_discount_pct"] = would_be_discount_pct
    if term_revenue is not None:
        m["expected_term_revenue_gbp"] = term_revenue
    return m


def test_section_includes_lift_by_class_table_when_misses_present():
    data = {
        "no_offer_churn_log": [
            _miss("C1", "2020-01-01", "below_threshold"),
            _miss("C2", "2020-01-01", "uneconomical", would_be_discount_pct=0.08),
        ],
        "customer_events": [
            _event("C1", "2020-01-01"),
            _event("C2", "2020-01-01"),
        ],
    }
    out = _section_threshold_optimisation(data)
    assert "Lift-per-pound by intervention class" in out
    assert "Detection gate" in out
    assert "High-risk tier" in out


class TestAnUnpriceableMissSurvivesRendering:
    """DEFECT: `compute_counterfactual_retention` was made fail-closed — a miss carrying no term
    revenue gets `net_value_of_offer_gbp=None` rather than 0.0, because 0.0 "reads as the most
    attractive intervention on the page". The renderer was not moved with it and formatted the
    field unconditionally, so the FIRST unpriceable miss raised TypeError and took the whole
    annual report down. That is what wedged the publish gate for 196 minutes.

    The fixture holds one unpriceable and one priceable miss on purpose: a fixture of only
    unpriceable misses cannot see a renderer that prints "not priceable" for everything.
    """

    def _out(self):
        data = {
            "no_offer_churn_log": [
                _miss("C1", "2020-01-01", "below_threshold"),
                _miss("C2", "2020-01-01", "below_threshold", term_revenue=8000.0),
            ],
            "customer_events": [
                _event("C1", "2020-01-01"),
                _event("C2", "2020-01-01"),
            ],
        }
        return _section_threshold_optimisation(data)

    def test_the_unpriceable_miss_renders_instead_of_raising(self):
        assert "| 2020 | C1 |" in self._out()

    def test_the_unpriceable_miss_is_not_priced_at_zero(self):
        """£0 is the fail-open the producer exists to remove: it reads as a free intervention."""
        row = [ln for ln in self._out().splitlines() if ln.startswith("| 2020 | C1 |")][0]
        assert "not priceable" in row
        assert "£0" not in row

    def test_the_priceable_miss_still_carries_its_number(self):
        """Opposes the mutation above: a renderer printing "not priceable" for every row passes
        the previous test and fails this one."""
        row = [ln for ln in self._out().splitlines() if ln.startswith("| 2020 | C2 |")][0]
        assert "£760" in row
        assert "not priceable" not in row

    def test_the_unpriceable_count_is_on_the_page_beside_the_totals(self):
        """The totals are taken over the complement of this count. A reader who cannot see it
        reads "Net value recoverable" as covering all the misses."""
        out = self._out()
        assert "Could not be priced" in out
        assert "1/2" in out


def test_section_has_no_lift_table_when_no_misses():
    data = {"no_offer_churn_log": [], "customer_events": []}
    out = _section_threshold_optimisation(data)
    assert "Lift-per-pound by intervention class" not in out


def test_section_does_not_crash_on_missing_keys():
    out = _section_threshold_optimisation({})
    assert "Counterfactual Retention" in out
