"""Tests for Account Intelligence Report (Phase EI)."""
import datetime as dt
import pytest
from company.core.account_intelligence import (
    RecommendedAction, AccountIntelligenceRating,
    AccountIntelligenceReport, AccountIntelligenceEngine,
)

DATE = dt.date(2024, 6, 15)


def make_report(resent=0.0, burned=False, h3=None, ae=100.0, gri=1.0, max_offer=200.0):
    return AccountIntelligenceReport(
        account_id="C1",
        generated_at=DATE,
        resentment_score=resent,
        is_burned=burned,
        h3_signal=h3,
        switching_ae=ae,
        gri_multiplier=gri,
        max_retention_offer_gbp=max_offer,
    )


class TestAccountIntelligenceReport:
    def test_rating_burned(self):
        r = make_report(burned=True)
        assert r.rating == AccountIntelligenceRating.BURNED

    def test_rating_at_risk_resentment(self):
        r = make_report(resent=40.0)
        assert r.rating == AccountIntelligenceRating.AT_RISK

    def test_rating_at_risk_h3(self):
        r = make_report(h3="at_risk")
        assert r.rating == AccountIntelligenceRating.AT_RISK

    def test_rating_premium(self):
        r = make_report(resent=5.0, h3="outperforming")
        assert r.rating == AccountIntelligenceRating.PREMIUM

    def test_rating_stable_default(self):
        r = make_report(resent=10.0, h3="on_track")
        assert r.rating == AccountIntelligenceRating.STABLE

    def test_action_manage_exit_when_burned(self):
        r = make_report(burned=True)
        assert r.recommended_action == RecommendedAction.MANAGE_EXIT

    def test_action_immediate_retention(self):
        r = make_report(resent=45.0, h3="at_risk")
        assert r.recommended_action == RecommendedAction.IMMEDIATE_RETENTION

    def test_action_targeted_reprice(self):
        r = make_report(resent=5.0, h3="at_risk")
        assert r.recommended_action == RecommendedAction.TARGETED_REPRICE

    def test_action_proactive_service(self):
        r = make_report(resent=30.0, h3="on_track")
        assert r.recommended_action == RecommendedAction.PROACTIVE_SERVICE

    def test_action_upsell(self):
        r = make_report(resent=5.0, h3="outperforming")
        assert r.recommended_action == RecommendedAction.UPSELL

    def test_action_monitor(self):
        r = make_report(resent=5.0, h3="on_track")
        assert r.recommended_action == RecommendedAction.MONITOR

    def test_urgency_immediate(self):
        r = make_report(resent=45.0, h3="at_risk")
        assert r.action_urgency_days == 1

    def test_urgency_reprice_week(self):
        r = make_report(resent=5.0, h3="at_risk")
        assert r.action_urgency_days == 7

    def test_urgency_monitor_quarter(self):
        r = make_report()
        assert r.action_urgency_days == 90

    def test_intelligence_summary(self):
        r = make_report(resent=20.0, h3="on_track")
        s = r.intelligence_summary()
        assert "C1" in s
        assert "action=" in s


class TestAccountIntelligenceEngine:
    def test_generate(self):
        r = AccountIntelligenceEngine.generate(
            "C1", DATE, resentment_score=10.0, is_burned=False,
            h3_signal="on_track", switching_ae=100.0, gri_multiplier=1.0,
            max_retention_offer_gbp=200.0
        )
        assert r.account_id == "C1"

    def test_portfolio_action_counts(self):
        reports = [make_report(), make_report(resent=5.0, h3="outperforming")]
        counts = AccountIntelligenceEngine.portfolio_action_counts(reports)
        assert "monitor" in counts or "upsell" in counts

    def test_immediate_actions(self):
        r1 = make_report(resent=45.0, h3="at_risk")  # immediate
        r2 = make_report()  # monitor (90d)
        result = AccountIntelligenceEngine.immediate_actions([r1, r2])
        assert len(result) == 1

    def test_premium_accounts(self):
        r1 = make_report(resent=5.0, h3="outperforming")  # premium
        r2 = make_report()  # stable
        result = AccountIntelligenceEngine.premium_accounts([r1, r2])
        assert len(result) == 1

    def test_portfolio_summary(self):
        reports = [make_report()]
        s = AccountIntelligenceEngine.portfolio_intelligence_summary(reports, DATE)
        assert "Portfolio Intelligence" in s
