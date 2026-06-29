"""Tests for CustomerRetentionBook — Phase AE."""
import pytest
from company.crm.portfolio_churn_risk import (
    ChurnRiskBand,
    ChurnRiskDriver,
    CustomerChurnRisk,
)
from company.crm.customer_retention import (
    CustomerRetentionBook,
    OfferDeclineReason,
    OfferType,
    RetentionOffer,
)


# ---- Helper to create a CustomerChurnRisk fixture ----

def make_risk(
    account_id="C1",
    churn_probability=0.45,
    band=ChurnRiskBand.HIGH,
    driver=ChurnRiskDriver.RATE_SHOCK,
    revenue=900.0,
    tenure=3.0,
    segment="resi",
) -> CustomerChurnRisk:
    return CustomerChurnRisk(
        account_id=account_id,
        churn_probability=churn_probability,
        risk_band=band,
        dominant_driver=driver,
        annual_revenue_gbp=revenue,
        tenure_years=tenure,
        segment=segment,
    )


# ---- RetentionOffer property tests ----

class TestRetentionOfferProperties:
    def test_is_affordable_true(self):
        risk = make_risk()
        book = CustomerRetentionBook()
        offer = book.generate_offer(risk, 200.0, 3500.0, 25.0)
        # max_spend = 100; price-match = 3500*0.25*0.08 = 70 <= 100
        assert offer.is_affordable is True

    def test_is_offer_made_true(self):
        risk = make_risk()
        book = CustomerRetentionBook()
        offer = book.generate_offer(risk, 200.0, 3500.0, 25.0)
        assert offer.is_offer_made is True

    def test_is_offer_made_false_when_no_offer(self):
        risk = make_risk()
        book = CustomerRetentionBook()
        offer = book.generate_offer(risk, -50.0, 3500.0, 25.0)
        assert offer.is_offer_made is False

    def test_expected_retention_value_positive(self):
        risk = make_risk()
        book = CustomerRetentionBook()
        offer = book.generate_offer(risk, 200.0, 3500.0, 25.0)
        assert offer.expected_retention_value_gbp > 0.0

    def test_expected_retention_value_zero_when_no_offer(self):
        risk = make_risk()
        book = CustomerRetentionBook()
        offer = book.generate_offer(risk, -50.0, 3500.0, 25.0)
        assert offer.expected_retention_value_gbp == 0.0


# ---- Offer type selection ----

class TestOfferTypeSelection:
    def test_no_offer_net_negative(self):
        risk = make_risk()
        book = CustomerRetentionBook()
        offer = book.generate_offer(risk, -30.0, 3500.0, 25.0)
        assert offer.offer_type == OfferType.NO_OFFER
        assert offer.decline_reason == OfferDeclineReason.NET_NEGATIVE_ACCOUNT

    def test_no_offer_insufficient_margin(self):
        risk = make_risk()
        book = CustomerRetentionBook()
        # max_spend = 5.0; price-match value would be 70 > 5
        offer = book.generate_offer(risk, 10.0, 3500.0, 25.0)
        assert offer.offer_type == OfferType.NO_OFFER
        assert offer.decline_reason == OfferDeclineReason.INSUFFICIENT_MARGIN

    def test_tou_referral_ev_rate_shock(self):
        risk = make_risk(driver=ChurnRiskDriver.RATE_SHOCK)
        book = CustomerRetentionBook()
        offer = book.generate_offer(risk, 200.0, 3500.0, 25.0, has_ev=True)
        assert offer.offer_type == OfferType.TOU_REFERRAL
        assert offer.offer_value_gbp == 0.0  # no cost to company

    def test_dual_fuel_bundle_electricity_only_not_rate_shock(self):
        risk = make_risk(driver=ChurnRiskDriver.TENURE_SHORT)
        book = CustomerRetentionBook()
        offer = book.generate_offer(risk, 200.0, 3500.0, 25.0, is_electricity_only=True)
        assert offer.offer_type == OfferType.DUAL_FUEL_BUNDLE

    def test_price_match_rate_shock_no_ev(self):
        risk = make_risk(driver=ChurnRiskDriver.RATE_SHOCK)
        book = CustomerRetentionBook()
        offer = book.generate_offer(risk, 300.0, 3500.0, 25.0, has_ev=False)
        assert offer.offer_type == OfferType.PRICE_MATCH
        # value = 3500 * 0.25 * 0.08 = 70.0
        assert offer.offer_value_gbp == pytest.approx(70.0)

    def test_loyalty_discount_tenure_short_driver(self):
        risk = make_risk(driver=ChurnRiskDriver.TENURE_SHORT)
        book = CustomerRetentionBook()
        offer = book.generate_offer(risk, 200.0, 3500.0, 25.0)
        assert offer.offer_type == OfferType.LOYALTY_DISCOUNT
        # value = 3500 * 0.25 * 0.05 = 43.75
        assert offer.offer_value_gbp == pytest.approx(43.75)

    def test_account_review_bill_stress(self):
        risk = make_risk(driver=ChurnRiskDriver.BILL_STRESS)
        book = CustomerRetentionBook()
        offer = book.generate_offer(risk, 200.0, 3500.0, 25.0)
        assert offer.offer_type == OfferType.ACCOUNT_REVIEW
        assert offer.offer_value_gbp == 0.0

    def test_loyalty_discount_baseline_driver(self):
        risk = make_risk(driver=ChurnRiskDriver.BASELINE)
        book = CustomerRetentionBook()
        offer = book.generate_offer(risk, 200.0, 3500.0, 25.0)
        assert offer.offer_type == OfferType.LOYALTY_DISCOUNT


# ---- CustomerRetentionBook collection tests ----

class TestCustomerRetentionBook:
    def _populated_book(self) -> CustomerRetentionBook:
        book = CustomerRetentionBook()
        # EV rate-shock -> TOU_REFERRAL
        book.generate_offer(make_risk("C1", driver=ChurnRiskDriver.RATE_SHOCK),
                            200.0, 3500.0, 25.0, has_ev=True)
        # Net-negative -> NO_OFFER
        book.generate_offer(make_risk("C2"), -50.0, 3500.0, 25.0)
        # Tenure short, elec-only -> DUAL_FUEL_BUNDLE
        book.generate_offer(make_risk("C3", driver=ChurnRiskDriver.TENURE_SHORT),
                            200.0, 3500.0, 25.0, is_electricity_only=True)
        # Rate shock, no EV -> PRICE_MATCH
        book.generate_offer(make_risk("C4", driver=ChurnRiskDriver.RATE_SHOCK),
                            300.0, 3500.0, 25.0)
        return book

    def test_offers_made_count(self):
        book = self._populated_book()
        assert len(book.offers_made()) == 3  # C1 TOU, C3 bundle, C4 price-match

    def test_no_offer_accounts(self):
        book = self._populated_book()
        no_offer = book.no_offer_accounts()
        assert len(no_offer) == 1
        assert no_offer[0].account_id == "C2"

    def test_by_offer_type_tou(self):
        book = self._populated_book()
        tou = book.by_offer_type(OfferType.TOU_REFERRAL)
        assert len(tou) == 1
        assert tou[0].account_id == "C1"

    def test_total_retention_spend(self):
        book = self._populated_book()
        # C1 (0) + C3 (0) + C4 (70) = 70
        assert book.total_retention_spend_gbp == pytest.approx(70.0)

    def test_total_expected_retention_value(self):
        book = self._populated_book()
        assert book.total_expected_retention_value_gbp > 0.0

    def test_retention_summary_keys(self):
        book = self._populated_book()
        s = book.retention_summary()
        assert s["customers_assessed"] == 4
        assert s["offers_made"] == 3
        assert s["no_offer_count"] == 1
        assert s["tou_referrals"] == 1
        assert s["price_matches"] == 1
        assert "total_retention_spend_gbp" in s

    def test_empty_book_summary(self):
        book = CustomerRetentionBook()
        s = book.retention_summary()
        assert s["customers_assessed"] == 0
        assert s["total_retention_spend_gbp"] == 0.0

    def test_all_offers_length(self):
        book = self._populated_book()
        assert len(book.all_offers) == 4
