"""Tests for Social Obligation Spend Register (Phase DI)."""
import pytest
from company.regulatory.social_obligation_register import (
    SocialObligationType, ObligationStatus, SocialObligationRecord,
    SocialObligationSpendRegister, _WHD_LEVY_PER_CUSTOMER_GBP, _WHD_BENEFIT_GBP,
)


@pytest.fixture
def reg():
    return SocialObligationSpendRegister()


class TestSocialObligationRecord:
    def test_record_created(self, reg):
        rec = reg.record_obligation(
            2023, SocialObligationType.WARM_HOME_DISCOUNT,
            target_gbp=2700.0, actual_spend_gbp=2700.0,
            status=ObligationStatus.PAID, beneficiaries_count=18,
        )
        assert rec.year == 2023
        assert rec.obligation_type == SocialObligationType.WARM_HOME_DISCOUNT
        assert rec.is_compliant

    def test_variance_credit(self, reg):
        rec = reg.record_obligation(
            2023, SocialObligationType.ENERGY_EFFICIENCY,
            target_gbp=5000.0, actual_spend_gbp=5500.0,
        )
        assert rec.variance_gbp == pytest.approx(500.0)
        assert not rec.is_underspend

    def test_variance_underspend(self, reg):
        rec = reg.record_obligation(
            2023, SocialObligationType.PRIORITY_SERVICES,
            target_gbp=1000.0, actual_spend_gbp=800.0,
        )
        assert rec.variance_gbp == pytest.approx(-200.0)
        assert rec.is_underspend

    def test_spend_rate_full(self, reg):
        rec = reg.record_obligation(
            2023, SocialObligationType.CARBON_OFFSET,
            target_gbp=500.0, actual_spend_gbp=500.0,
        )
        assert rec.spend_rate == pytest.approx(1.0)

    def test_spend_rate_partial(self, reg):
        rec = reg.record_obligation(
            2023, SocialObligationType.WARM_HOME_DISCOUNT,
            target_gbp=1000.0, actual_spend_gbp=750.0,
        )
        assert rec.spend_rate == pytest.approx(0.75)

    def test_cost_per_beneficiary(self, reg):
        rec = reg.record_obligation(
            2023, SocialObligationType.WARM_HOME_DISCOUNT,
            target_gbp=2700.0, actual_spend_gbp=2700.0,
            beneficiaries_count=18,
        )
        assert rec.cost_per_beneficiary_gbp == pytest.approx(150.0)

    def test_cost_per_beneficiary_none_when_zero(self, reg):
        rec = reg.record_obligation(
            2023, SocialObligationType.CARBON_OFFSET,
            target_gbp=200.0, actual_spend_gbp=200.0,
            beneficiaries_count=0,
        )
        assert rec.cost_per_beneficiary_gbp is None

    def test_is_compliant_paid(self, reg):
        rec = reg.record_obligation(
            2023, SocialObligationType.ENERGY_EFFICIENCY,
            target_gbp=3000.0, actual_spend_gbp=3200.0,
            status=ObligationStatus.PAID,
        )
        assert rec.is_compliant

    def test_not_compliant_underperforming(self, reg):
        rec = reg.record_obligation(
            2023, SocialObligationType.ENERGY_EFFICIENCY,
            target_gbp=3000.0, actual_spend_gbp=1200.0,
            status=ObligationStatus.UNDERPERFORMING,
        )
        assert not rec.is_compliant

    def test_description_stored(self, reg):
        rec = reg.record_obligation(
            2023, SocialObligationType.FUEL_POVERTY_SUPPORT,
            target_gbp=500.0, actual_spend_gbp=500.0,
            description="Debt write-off for fuel poor customers",
        )
        assert rec.description == "Debt write-off for fuel poor customers"


class TestSocialObligationRegisterQueries:
    def test_for_year(self, reg):
        reg.record_obligation(2022, SocialObligationType.WARM_HOME_DISCOUNT, 2400.0, 2400.0)
        reg.record_obligation(2023, SocialObligationType.WARM_HOME_DISCOUNT, 2700.0, 2700.0)
        assert len(reg.for_year(2023)) == 1
        assert len(reg.for_year(2022)) == 1

    def test_by_type(self, reg):
        reg.record_obligation(2023, SocialObligationType.WARM_HOME_DISCOUNT, 2700.0, 2700.0)
        reg.record_obligation(2023, SocialObligationType.WARM_HOME_DISCOUNT, 100.0, 100.0)
        reg.record_obligation(2023, SocialObligationType.PRIORITY_SERVICES, 500.0, 500.0)
        whd = reg.by_type(SocialObligationType.WARM_HOME_DISCOUNT)
        assert len(whd) == 2

    def test_non_compliant(self, reg):
        reg.record_obligation(2023, SocialObligationType.ENERGY_EFFICIENCY,
                              3000.0, 1200.0, status=ObligationStatus.UNDERPERFORMING)
        reg.record_obligation(2023, SocialObligationType.WARM_HOME_DISCOUNT,
                              2700.0, 2700.0, status=ObligationStatus.PAID)
        nc = reg.non_compliant()
        assert len(nc) == 1
        assert nc[0].obligation_type == SocialObligationType.ENERGY_EFFICIENCY

    def test_non_compliant_excludes_projected(self, reg):
        reg.record_obligation(2024, SocialObligationType.ENERGY_EFFICIENCY,
                              3000.0, 0.0, status=ObligationStatus.PROJECTED)
        assert reg.non_compliant() == []

    def test_underspend_records(self, reg):
        reg.record_obligation(2023, SocialObligationType.PRIORITY_SERVICES, 1000.0, 800.0)
        reg.record_obligation(2023, SocialObligationType.WARM_HOME_DISCOUNT, 2700.0, 2700.0)
        under = reg.underspend_records()
        assert len(under) == 1

    def test_total_spend_all(self, reg):
        reg.record_obligation(2022, SocialObligationType.WARM_HOME_DISCOUNT, 2400.0, 2400.0)
        reg.record_obligation(2023, SocialObligationType.WARM_HOME_DISCOUNT, 2700.0, 2700.0)
        assert reg.total_spend_gbp() == pytest.approx(5100.0)

    def test_total_spend_by_year(self, reg):
        reg.record_obligation(2022, SocialObligationType.WARM_HOME_DISCOUNT, 2400.0, 2400.0)
        reg.record_obligation(2023, SocialObligationType.WARM_HOME_DISCOUNT, 2700.0, 2700.0)
        assert reg.total_spend_gbp(2023) == pytest.approx(2700.0)

    def test_total_target(self, reg):
        reg.record_obligation(2023, SocialObligationType.WARM_HOME_DISCOUNT, 2700.0, 2700.0)
        reg.record_obligation(2023, SocialObligationType.PRIORITY_SERVICES, 500.0, 400.0)
        assert reg.total_target_gbp(2023) == pytest.approx(3200.0)

    def test_total_beneficiaries(self, reg):
        reg.record_obligation(2023, SocialObligationType.WARM_HOME_DISCOUNT, 2700.0, 2700.0,
                              beneficiaries_count=18)
        reg.record_obligation(2023, SocialObligationType.PRIORITY_SERVICES, 500.0, 400.0,
                              beneficiaries_count=5)
        assert reg.total_beneficiaries(2023) == 23

    def test_annual_summary(self, reg):
        reg.record_obligation(2023, SocialObligationType.WARM_HOME_DISCOUNT,
                              2700.0, 2700.0, status=ObligationStatus.PAID, beneficiaries_count=18)
        reg.record_obligation(2023, SocialObligationType.PRIORITY_SERVICES,
                              500.0, 500.0, status=ObligationStatus.COMPLIANT)
        summ = reg.annual_summary(2023)
        assert summ["year"] == 2023
        assert summ["total_spend_gbp"] == pytest.approx(3200.0)
        assert summ["compliant_count"] == 2
        assert summ["non_compliant_count"] == 0
        assert SocialObligationType.WARM_HOME_DISCOUNT.value in summ["by_type"]

    def test_estimate_whd_levy(self, reg):
        levy = reg.estimate_whd_levy(100)
        assert levy == pytest.approx(100 * _WHD_LEVY_PER_CUSTOMER_GBP)

    def test_whd_constants(self, reg):
        assert reg.whd_levy_constant() == _WHD_LEVY_PER_CUSTOMER_GBP
        assert reg.whd_benefit_constant() == _WHD_BENEFIT_GBP
        assert _WHD_BENEFIT_GBP == 150.0

    def test_social_obligation_summary(self, reg):
        reg.record_obligation(2023, SocialObligationType.WARM_HOME_DISCOUNT,
                              2700.0, 2700.0, status=ObligationStatus.PAID, beneficiaries_count=18)
        s = reg.social_obligation_summary()
        assert "Social Obligation Register" in s
        assert "2023" in s

    def test_multiple_years_isolated(self, reg):
        for yr in [2020, 2021, 2022, 2023]:
            reg.record_obligation(yr, SocialObligationType.WARM_HOME_DISCOUNT,
                                  2000.0 + yr * 10, 2000.0 + yr * 10)
        for yr in [2020, 2021, 2022, 2023]:
            assert len(reg.for_year(yr)) == 1
