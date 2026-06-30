"""Tests for Standing Charge Fairness Assessor (Phase FP)."""
import datetime as dt
import pytest
from company.pricing.standing_charge_assessor import (
    SCFairnessRating, ConsumerImpactLevel, StandingChargeAssessment,
    StandingChargeAssessor, _OFGEM_SC_CAP_ELEC_PENCE_PER_DAY,
)


def make_assessment(sc=45.0, ur=30.0, is_elec=True, tariff_id="T1"):
    return StandingChargeAssessment(
        tariff_id=tariff_id, is_electricity=is_elec,
        standing_charge_pence_per_day=sc, unit_rate_pence_per_kwh=ur,
    )


class TestStandingChargeAssessment:
    def test_annual_sc_gbp(self):
        a = make_assessment(sc=50.0)
        assert a.annual_sc_gbp == pytest.approx(365 * 50.0 / 100)

    def test_typical_annual_bill(self):
        a = make_assessment(sc=50.0, ur=30.0, is_elec=True)
        sc = 365 * 50.0 / 100
        units = 2900.0 * 30.0 / 100
        assert a.typical_annual_bill_gbp == pytest.approx(sc + units)

    def test_sc_pct_of_bill(self):
        a = make_assessment(sc=50.0, ur=30.0, is_elec=True)
        pct = a.sc_pct_of_typical_bill
        assert 0 < pct < 100

    def test_fairness_rating_fair(self):
        # Well below cap
        a = make_assessment(sc=20.0)
        assert a.fairness_rating == SCFairnessRating.FAIR

    def test_fairness_rating_excessive(self):
        # >130% of cap
        a = make_assessment(sc=_OFGEM_SC_CAP_ELEC_PENCE_PER_DAY * 1.4)
        assert a.fairness_rating == SCFairnessRating.EXCESSIVE

    def test_consumer_impact_critical(self):
        # Very high SC, very low unit rate -> SC dominates
        a = make_assessment(sc=200.0, ur=1.0)
        assert a.consumer_impact == ConsumerImpactLevel.CRITICAL

    def test_consumer_impact_low(self):
        a = make_assessment(sc=10.0, ur=30.0)
        assert a.consumer_impact == ConsumerImpactLevel.LOW

    def test_assessment_summary(self):
        s = make_assessment().assessment_summary()
        assert "SCAssessment" in s and "T1" in s


class TestStandingChargeAssessor:
    def test_unfair_or_worse(self):
        assessor = StandingChargeAssessor()
        assessor.assess(make_assessment(sc=20.0))    # FAIR
        assessor.assess(make_assessment(sc=_OFGEM_SC_CAP_ELEC_PENCE_PER_DAY * 1.15,
                                         tariff_id="T2"))  # UNFAIR
        assert len(assessor.unfair_or_worse()) == 1

    def test_high_impact(self):
        assessor = StandingChargeAssessor()
        assessor.assess(make_assessment(sc=200.0, ur=1.0))  # CRITICAL impact
        assert len(assessor.high_impact_assessments()) == 1

    def test_max_annual_sc(self):
        assessor = StandingChargeAssessor()
        assessor.assess(make_assessment(sc=40.0))
        assessor.assess(make_assessment(sc=60.0, tariff_id="T2"))
        assert assessor.max_annual_sc_gbp() == pytest.approx(365 * 60 / 100)

    def test_sc_assessor_summary(self):
        assessor = StandingChargeAssessor()
        assessor.assess(make_assessment())
        s = assessor.sc_assessor_summary()
        assert "Standing Charge Assessor" in s
