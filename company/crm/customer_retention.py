"""Customer Retention Offer Book — Phase AE.

For customers flagged as at-risk by the Portfolio Churn Risk Book (Phase AD),
generates a targeted retention offer bounded by the customer's net margin
(Phase J). Offer type depends on the dominant churn driver (Phase AD) and
whether the customer has assets that suit a ToU referral (Phase X chain).

Company can observe:
  - Churn risk and dominant driver (from billing/CRM patterns — Phase AD)
  - Net margin per customer (from own billing and cost records — Phase J)
  - EV and ASHP flags (from CRM — Phase C)
  - Tenure (CRM record)

Epistemic-compliant: no SIM internals used.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from company.crm.portfolio_churn_risk import ChurnRiskBand, ChurnRiskDriver, CustomerChurnRisk


class OfferType(str, Enum):
    LOYALTY_DISCOUNT = "loyalty_discount"      # fixed-term rate reduction for long-tenure
    TOU_REFERRAL = "tou_referral"              # redirect EV customer to ToU tariff
    DUAL_FUEL_BUNDLE = "dual_fuel_bundle"      # cross-sell missing fuel leg
    PRICE_MATCH = "price_match"               # match competitor rate within margin
    ACCOUNT_REVIEW = "account_review"          # call to understand root cause
    NO_OFFER = "no_offer"                      # net-negative: let them churn


class OfferDeclineReason(str, Enum):
    NET_NEGATIVE_ACCOUNT = "net_negative_account"
    INSUFFICIENT_MARGIN = "insufficient_margin"
    LOW_CHURN_RISK = "low_churn_risk"
    ALREADY_ON_BEST_PRODUCT = "already_on_best_product"


# Maximum discount fraction of net margin we'll give up to retain
_MAX_RETENTION_SPEND_FRACTION = 0.50  # won't spend more than 50% of net margin

# Minimum net margin to make any offer worthwhile
_MIN_NET_MARGIN_FOR_OFFER_GBP = 20.0

# Loyalty discount: how many pence per kWh reduction, expressed as fraction of unit rate
_LOYALTY_DISCOUNT_FRACTION = 0.05   # 5% rate reduction
_PRICE_MATCH_FRACTION = 0.08        # match up to 8% cheaper


@dataclass(frozen=True)
class RetentionOffer:
    """Retention offer generated for one at-risk customer.

    offer_value_gbp: the annual value of the offer to the customer.
    max_spend_gbp: the maximum the company is prepared to spend (50% of net margin).
    is_affordable: offer_value <= max_spend.
    """
    account_id: str
    offer_type: OfferType
    offer_value_gbp: float
    max_spend_gbp: float
    net_margin_gbp: float
    churn_risk_band: ChurnRiskBand
    dominant_driver: ChurnRiskDriver
    decline_reason: Optional[OfferDeclineReason] = None

    @property
    def is_affordable(self) -> bool:
        return self.offer_value_gbp <= self.max_spend_gbp

    @property
    def is_offer_made(self) -> bool:
        return self.offer_type != OfferType.NO_OFFER

    @property
    def expected_retention_value_gbp(self) -> float:
        """Net benefit if customer is retained: margin saved minus cost of offer."""
        if not self.is_offer_made:
            return 0.0
        return round(self.net_margin_gbp - self.offer_value_gbp, 2)


def _choose_offer(
    risk: CustomerChurnRisk,
    net_margin_gbp: float,
    annual_consumption_kwh: float,
    unit_rate_p_per_kwh: float,
    has_ev: bool = False,
    is_electricity_only: bool = False,
) -> tuple[OfferType, float, Optional[OfferDeclineReason]]:
    """Select offer type and compute its value."""
    if net_margin_gbp <= 0.0:
        return OfferType.NO_OFFER, 0.0, OfferDeclineReason.NET_NEGATIVE_ACCOUNT

    max_spend = net_margin_gbp * _MAX_RETENTION_SPEND_FRACTION
    if max_spend < _MIN_NET_MARGIN_FOR_OFFER_GBP:
        return OfferType.NO_OFFER, 0.0, OfferDeclineReason.INSUFFICIENT_MARGIN

    driver = risk.dominant_driver
    annual_kwh = annual_consumption_kwh

    # EV customer under rate shock → ToU referral (no cost to company; saves margin via Phase Y)
    if has_ev and driver == ChurnRiskDriver.RATE_SHOCK:
        return OfferType.TOU_REFERRAL, 0.0, None

    # Electricity-only customer → dual-fuel bundle (cross-sell gas; no discount needed)
    if is_electricity_only and driver != ChurnRiskDriver.RATE_SHOCK:
        return OfferType.DUAL_FUEL_BUNDLE, 0.0, None

    if driver == ChurnRiskDriver.RATE_SHOCK:
        # Price-match: give back up to 8% of annual bill
        offer_val = round(annual_kwh * unit_rate_p_per_kwh / 100.0 * _PRICE_MATCH_FRACTION, 2)
        if offer_val <= max_spend:
            return OfferType.PRICE_MATCH, offer_val, None
        return OfferType.NO_OFFER, 0.0, OfferDeclineReason.INSUFFICIENT_MARGIN

    if driver in (ChurnRiskDriver.TENURE_SHORT, ChurnRiskDriver.BASELINE):
        # Loyalty discount: 5% rate reduction on annual bill
        offer_val = round(annual_kwh * unit_rate_p_per_kwh / 100.0 * _LOYALTY_DISCOUNT_FRACTION, 2)
        if offer_val <= max_spend:
            return OfferType.LOYALTY_DISCOUNT, offer_val, None
        return OfferType.NO_OFFER, 0.0, OfferDeclineReason.INSUFFICIENT_MARGIN

    # Bill stress or unknown: account review call (no monetary cost)
    return OfferType.ACCOUNT_REVIEW, 0.0, None


class CustomerRetentionBook:
    """Generates and tracks retention offers across the at-risk portfolio.

    Usage::
        book = CustomerRetentionBook()
        offer = book.generate_offer(
            risk=churn_risk,
            net_margin_gbp=85.0,
            annual_consumption_kwh=3500.0,
            unit_rate_p_per_kwh=25.0,
            has_ev=True,
        )
    """

    def __init__(self) -> None:
        self._offers: list[RetentionOffer] = []

    def generate_offer(
        self,
        risk: CustomerChurnRisk,
        net_margin_gbp: float,
        annual_consumption_kwh: float,
        unit_rate_p_per_kwh: float,
        has_ev: bool = False,
        is_electricity_only: bool = False,
    ) -> RetentionOffer:
        offer_type, offer_val, decline_reason = _choose_offer(
            risk=risk,
            net_margin_gbp=net_margin_gbp,
            annual_consumption_kwh=annual_consumption_kwh,
            unit_rate_p_per_kwh=unit_rate_p_per_kwh,
            has_ev=has_ev,
            is_electricity_only=is_electricity_only,
        )
        max_spend = max(0.0, net_margin_gbp * _MAX_RETENTION_SPEND_FRACTION)
        offer = RetentionOffer(
            account_id=risk.account_id,
            offer_type=offer_type,
            offer_value_gbp=offer_val,
            max_spend_gbp=round(max_spend, 2),
            net_margin_gbp=net_margin_gbp,
            churn_risk_band=risk.risk_band,
            dominant_driver=risk.dominant_driver,
            decline_reason=decline_reason,
        )
        self._offers.append(offer)
        return offer

    @property
    def all_offers(self) -> list[RetentionOffer]:
        return list(self._offers)

    def offers_made(self) -> list[RetentionOffer]:
        return [o for o in self._offers if o.is_offer_made]

    def no_offer_accounts(self) -> list[RetentionOffer]:
        return [o for o in self._offers if not o.is_offer_made]

    def by_offer_type(self, offer_type: OfferType) -> list[RetentionOffer]:
        return [o for o in self._offers if o.offer_type == offer_type]

    @property
    def total_retention_spend_gbp(self) -> float:
        return round(sum(o.offer_value_gbp for o in self.offers_made()), 2)

    @property
    def total_expected_retention_value_gbp(self) -> float:
        return round(sum(o.expected_retention_value_gbp for o in self.offers_made()), 2)

    def retention_summary(self) -> dict:
        return {
            "customers_assessed": len(self._offers),
            "offers_made": len(self.offers_made()),
            "no_offer_count": len(self.no_offer_accounts()),
            "tou_referrals": len(self.by_offer_type(OfferType.TOU_REFERRAL)),
            "price_matches": len(self.by_offer_type(OfferType.PRICE_MATCH)),
            "loyalty_discounts": len(self.by_offer_type(OfferType.LOYALTY_DISCOUNT)),
            "total_retention_spend_gbp": self.total_retention_spend_gbp,
            "total_expected_retention_value_gbp": self.total_expected_retention_value_gbp,
        }
