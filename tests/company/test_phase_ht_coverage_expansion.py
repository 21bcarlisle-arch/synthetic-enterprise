"""Phase HT: coverage expansion for credit_rating_book, risk_appetite, renewals_book."""
import datetime as dt
import pytest

# ===== credit_rating_book =====
from company.trading.credit_rating_book import (
    CreditRating, CounterpartyCreditProfile, CreditExposure, CreditRatingBook,
    is_investment_grade
)

class TestCreditRatingBookExpanded:
    def _book_with_cp(self):
        book = CreditRatingBook()
        book.register("CP1","BankA",CreditRating.A,"Moodys",dt.date(2022,1,1),1_000_000.0)
        return book

    def test_investment_grade_A_or_above(self):
        for rating in [CreditRating.AAA, CreditRating.AA, CreditRating.A, CreditRating.BBB]:
            assert is_investment_grade(rating)

    def test_sub_investment_grade(self):
        for rating in [CreditRating.BB, CreditRating.B, CreditRating.CCC, CreditRating.D]:
            assert not is_investment_grade(rating)

    def test_profile_score_and_pd(self):
        book = self._book_with_cp()
        p = book.get("CP1")
        assert p.score == 8
        assert p.pd_pct == pytest.approx(0.09)

    def test_is_investment_grade_property(self):
        book = self._book_with_cp()
        p = book.get("CP1")
        assert p.is_investment_grade

    def test_record_exposure_and_total(self):
        book = self._book_with_cp()
        book.record_exposure("CP1", dt.date(2022,6,1), 200_000.0, "forward")
        book.record_exposure("CP1", dt.date(2022,6,2), 100_000.0, "option")
        assert book.total_exposure_gbp("CP1") == pytest.approx(300_000.0)

    def test_is_within_limit(self):
        book = self._book_with_cp()
        book.record_exposure("CP1", dt.date(2022,6,1), 500_000.0, "forward")
        assert book.is_within_limit("CP1", 400_000.0)
        assert not book.is_within_limit("CP1", 600_000.0)

    def test_sub_investment_grade_counterparties(self):
        book = self._book_with_cp()
        book.register("CP2","ShellyCo",CreditRating.BB,"S&P",dt.date(2022,1,1),100_000.0)
        subs = book.sub_investment_grade_counterparties()
        assert len(subs) == 1
        assert subs[0].counterparty_id == "CP2"

    def test_credit_summary_keys(self):
        book = self._book_with_cp()
        s = book.credit_summary()
        assert "investment_grade" in s and "sub_investment_grade" in s

    def test_get_returns_none_for_unknown(self):
        book = CreditRatingBook()
        assert book.get("MISSING") is None

    def test_d_rating_pd_100pct(self):
        book = CreditRatingBook()
        p = book.register("CP1","FailedCo",CreditRating.D,"S&P",dt.date(2022,1,1),0.0)
        assert p.pd_pct == pytest.approx(100.0)


# ===== risk_appetite =====
from company.risk.risk_appetite import (
    RiskCategory, RiskRAG, RiskLimit, RiskMeasurement, RiskAppetiteFramework
)

class TestRiskAppetiteExpanded:
    def _framework(self):
        f = RiskAppetiteFramework(dt.date(2022,1,1))
        f.add_limit("VAR",RiskCategory.MARKET,"Value at Risk",5_000_000.0,"GBP")
        return f

    def test_add_limit_returns_limit(self):
        f = self._framework()
        l = f._limits["VAR"]
        assert l.limit_value == pytest.approx(5_000_000.0)
        assert l.warning_value == pytest.approx(4_000_000.0)

    def test_measurement_within_appetite(self):
        f = self._framework()
        m = f.record_measurement("VAR", 2_000_000.0, dt.date(2022,3,31))
        assert m.rag == RiskRAG.WITHIN_APPETITE
        assert not m.is_breach

    def test_measurement_approaching_limit(self):
        f = self._framework()
        m = f.record_measurement("VAR", 4_500_000.0, dt.date(2022,3,31))
        assert m.rag == RiskRAG.APPROACHING_LIMIT

    def test_measurement_limit_breach(self):
        f = self._framework()
        m = f.record_measurement("VAR", 6_000_000.0, dt.date(2022,3,31))
        assert m.rag == RiskRAG.LIMIT_BREACH
        assert m.is_breach

    def test_utilisation_pct(self):
        f = self._framework()
        m = f.record_measurement("VAR", 2_500_000.0, dt.date(2022,3,31))
        assert m.utilisation_pct == pytest.approx(50.0)

    def test_latest_measurement_most_recent(self):
        f = self._framework()
        f.record_measurement("VAR", 2_000_000.0, dt.date(2022,1,31))
        f.record_measurement("VAR", 3_500_000.0, dt.date(2022,3,31))
        latest = f.latest_measurement("VAR")
        assert latest.measured_value == pytest.approx(3_500_000.0)

    def test_active_breaches_uses_latest(self):
        f = self._framework()
        f.record_measurement("VAR", 6_000_000.0, dt.date(2022,1,31))
        f.record_measurement("VAR", 3_000_000.0, dt.date(2022,3,31))
        assert f.active_breaches() == []

    def test_risk_dashboard_keys(self):
        f = self._framework()
        f.record_measurement("VAR", 2_000_000.0, dt.date(2022,3,31))
        s = f.risk_dashboard(dt.date(2022,3,31))
        assert "breaches" in s and "items" in s

    def test_latest_measurement_none_for_unknown(self):
        f = self._framework()
        assert f.latest_measurement("MISSING") is None

    def test_multiple_categories(self):
        f = self._framework()
        f.add_limit("BAD_DEBT",RiskCategory.CREDIT,"Bad Debt",100_000.0,"GBP")
        assert len(f._limits) == 2


# ===== renewals_book =====
from company.crm.renewals_book import (
    RenewalOutcome, OfferType, RenewalRecord, RenewalsBook
)

class TestRenewalsBookExpanded:
    def _book(self):
        book = RenewalsBook()
        book.add("C1","resi",dt.date(2022,12,31),RenewalOutcome.RENEWED,
                 OfferType.BETTER_TARIFF, 28.5, 12, days_notice_given=45,
                 was_outbound_contact=True)
        book.add("C2","resi",dt.date(2022,12,31),RenewalOutcome.SWITCHED_AWAY,
                 OfferType.SAME_TARIFF, 30.0, None, days_notice_given=42)
        book.add("C3","resi",dt.date(2022,12,31),RenewalOutcome.MOVED_OUT)
        return book

    def test_add_returns_record(self):
        book = RenewalsBook()
        r = book.add("C1","resi",dt.date(2022,12,31),RenewalOutcome.RENEWED)
        assert r.accepted

    def test_renewal_rate_excludes_moved_out(self):
        book = self._book()
        rate = book.renewal_rate(2022)
        assert rate == pytest.approx(50.0)

    def test_lapse_rate_complement(self):
        book = self._book()
        assert book.lapse_rate(2022) == pytest.approx(50.0)

    def test_renewal_rate_none_when_empty(self):
        book = RenewalsBook()
        assert book.renewal_rate(2022) is None

    def test_segment_filter(self):
        book = self._book()
        book.add("C4","sme",dt.date(2022,12,31),RenewalOutcome.RENEWED)
        resi_rate = book.renewal_rate(2022, segment="resi")
        sme_rate = book.renewal_rate(2022, segment="sme")
        assert resi_rate == pytest.approx(50.0)
        assert sme_rate == pytest.approx(100.0)

    def test_outbound_lift(self):
        book = self._book()
        lift = book.outbound_lift(2022)
        assert lift is not None

    def test_by_offer_type_renewal_rate(self):
        book = self._book()
        bt = book.by_offer_type(2022)
        assert "better_tariff" in bt
        assert bt["better_tariff"]["renewed"] == 1

    def test_annual_summary_keys(self):
        book = self._book()
        s = book.annual_summary(2022)
        assert "renewal_rate_pct" in s and "total_decisions" in s

    def test_deceased_excluded_from_renewal_rate(self):
        book = RenewalsBook()
        book.add("C1","resi",dt.date(2022,12,31),RenewalOutcome.RENEWED)
        book.add("C2","resi",dt.date(2022,12,31),RenewalOutcome.DECEASED)
        rate = book.renewal_rate(2022)
        assert rate == pytest.approx(100.0)

    def test_outbound_lift_none_when_no_outbound(self):
        book = RenewalsBook()
        book.add("C1","resi",dt.date(2022,12,31),RenewalOutcome.RENEWED)
        assert book.outbound_lift(2022) is None
