"""Tests for Switching Cost-Benefit Analyser (Phase EJ)."""
import datetime as dt
import pytest
from company.crm.switching_cba import (
    RetentionDecision, SwitchingCostBenefitAnalysis, SwitchingCBABook,
)

DATE = dt.date(2024, 1, 15)


def make_cba(ae=100.0, saving=50.0, roi_factor=1.0, remaining=3.0,
             margin=200.0, offer=None, cac=300.0):
    clv_est = margin * remaining * (1 / 1.08) ** remaining
    retention_offer = clv_est / (1.5 * roi_factor) if offer is None else offer
    return SwitchingCostBenefitAnalysis(
        account_id="C1",
        analysed_at=DATE,
        remaining_contract_years=remaining,
        annual_margin_gbp=margin,
        current_switching_ae=ae,
        perceived_saving_gbp=saving,
        retention_offer_gbp=retention_offer,
        replacement_cac_gbp=cac,
    )


class TestSwitchingCostBenefitAnalysis:
    def test_future_clv_positive(self):
        a = make_cba()
        assert a.future_clv_if_retained_gbp > 0

    def test_future_clv_shorter_tenure(self):
        a1 = make_cba(remaining=3.0)
        a2 = make_cba(remaining=1.0)
        assert a1.future_clv_if_retained_gbp > a2.future_clv_if_retained_gbp

    def test_offer_roi_finite(self):
        a = make_cba(offer=100.0)
        assert a.offer_roi == pytest.approx(a.future_clv_if_retained_gbp / 100.0)

    def test_offer_roi_zero_offer(self):
        a = make_cba(offer=0.0)
        assert a.offer_roi == float("inf")

    def test_not_likely_to_switch_when_ae_high(self):
        a = make_cba(ae=200.0, saving=50.0)
        assert not a.is_customer_likely_to_switch

    def test_likely_to_switch_when_saving_exceeds_ae(self):
        a = make_cba(ae=40.0, saving=50.0)
        assert a.is_customer_likely_to_switch

    def test_passive_friction_retains_above_floor(self):
        a = make_cba(ae=95.0)
        assert a.passive_friction_retains

    def test_passive_friction_does_not_retain_below_floor(self):
        a = make_cba(ae=85.0)
        assert not a.passive_friction_retains

    def test_decision_retain_passively_not_likely(self):
        a = make_cba(ae=200.0, saving=50.0)
        assert a.decision == RetentionDecision.RETAIN_PASSIVELY

    def test_decision_retain_passively_high_ae(self):
        a = make_cba(ae=95.0, saving=200.0)
        assert a.decision == RetentionDecision.RETAIN_PASSIVELY

    def test_decision_retain_with_offer_good_roi(self):
        # Force: customer will switch, low AE, good ROI, high CLV > CAC
        a = SwitchingCostBenefitAnalysis(
            account_id="C2",
            analysed_at=DATE,
            remaining_contract_years=5.0,
            annual_margin_gbp=500.0,
            current_switching_ae=50.0,
            perceived_saving_gbp=100.0,
            retention_offer_gbp=100.0,    # CLV ~2000, ROI=20x >> 1.5
            replacement_cac_gbp=100.0,    # CLV > CAC
        )
        assert a.decision == RetentionDecision.RETAIN_WITH_OFFER

    def test_decision_let_go_poor_roi(self):
        a = SwitchingCostBenefitAnalysis(
            account_id="C3",
            analysed_at=DATE,
            remaining_contract_years=0.5,
            annual_margin_gbp=20.0,       # CLV ~9, very small
            current_switching_ae=50.0,
            perceived_saving_gbp=100.0,
            retention_offer_gbp=200.0,    # offer > CLV -> ROI < 0.1 << 1.5, not borderline
            replacement_cac_gbp=50.0,
        )
        assert a.decision == RetentionDecision.LET_GO

    def test_net_benefit_of_offer(self):
        a = SwitchingCostBenefitAnalysis(
            account_id="C1",
            analysed_at=DATE,
            remaining_contract_years=2.0,
            annual_margin_gbp=200.0,
            current_switching_ae=50.0,
            perceived_saving_gbp=100.0,
            retention_offer_gbp=50.0,
            replacement_cac_gbp=300.0,
        )
        assert a.net_benefit_of_offer_gbp == pytest.approx(
            a.future_clv_if_retained_gbp - 50.0
        )

    def test_analysis_summary(self):
        a = make_cba()
        s = a.analysis_summary()
        assert "C1" in s


class TestSwitchingCBABook:
    def test_analyse_stores(self):
        book = SwitchingCBABook()
        a = make_cba()
        book.analyse(a)
        assert len(book.analyses_for("C1")) == 1

    def test_retain_with_offer_filter(self):
        book = SwitchingCBABook()
        a = SwitchingCostBenefitAnalysis(
            account_id="C1", analysed_at=DATE,
            remaining_contract_years=5.0, annual_margin_gbp=500.0,
            current_switching_ae=50.0, perceived_saving_gbp=100.0,
            retention_offer_gbp=100.0, replacement_cac_gbp=100.0,
        )
        book.analyse(a)
        assert len(book.retain_with_offer()) == 1

    def test_total_clv_at_stake(self):
        book = SwitchingCBABook()
        a = make_cba(ae=40.0, saving=100.0)
        book.analyse(a)
        assert book.total_clv_at_stake_gbp() > 0

    def test_portfolio_summary(self):
        book = SwitchingCBABook()
        book.analyse(make_cba())
        s = book.portfolio_summary(DATE)
        assert "Switching CBA" in s
