from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class AcquisitionChannel(str, Enum):
    PRICE_COMPARISON = 'price_comparison'   # MoneySupermarket, uSwitch
    DIRECT_WEB = 'direct_web'
    TELESALES = 'telesales'
    PARTNER_REFERRAL = 'partner_referral'
    SMART_METER_INSTALL = 'smart_meter_install'
    EXISTING_CUSTOMER_REFERRAL = 'existing_customer_referral'
    OUTBOUND_RETENTION = 'outbound_retention'


_BASE_CAC_GBP: Dict[AcquisitionChannel, float] = {
    AcquisitionChannel.PRICE_COMPARISON: 65.0,
    AcquisitionChannel.DIRECT_WEB: 28.0,
    AcquisitionChannel.TELESALES: 90.0,
    AcquisitionChannel.PARTNER_REFERRAL: 35.0,
    AcquisitionChannel.SMART_METER_INSTALL: 15.0,
    AcquisitionChannel.EXISTING_CUSTOMER_REFERRAL: 20.0,
    AcquisitionChannel.OUTBOUND_RETENTION: 12.0,
}

_CHANNEL_CHURN_FACTOR: Dict[AcquisitionChannel, float] = {
    AcquisitionChannel.PRICE_COMPARISON: 1.45,
    AcquisitionChannel.DIRECT_WEB: 0.85,
    AcquisitionChannel.TELESALES: 1.20,
    AcquisitionChannel.PARTNER_REFERRAL: 0.90,
    AcquisitionChannel.SMART_METER_INSTALL: 0.70,
    AcquisitionChannel.EXISTING_CUSTOMER_REFERRAL: 0.65,
    AcquisitionChannel.OUTBOUND_RETENTION: 0.80,
}


@dataclass(frozen=True)
class ChannelAcquisition:
    channel: AcquisitionChannel
    year: int
    customer_count: int
    total_cac_gbp: float

    @property
    def avg_cac_gbp(self) -> float:
        if self.customer_count == 0:
            return 0.0
        return round(self.total_cac_gbp / self.customer_count, 2)


@dataclass(frozen=True)
class ChannelROIResult:
    channel: AcquisitionChannel
    avg_cac_gbp: float
    avg_annual_margin_gbp: float
    base_churn_pct: float
    effective_churn_pct: float
    expected_tenure_years: float
    roi_ratio: float

    @property
    def is_profitable(self) -> bool:
        return self.roi_ratio >= 1.0


def compute_channel_roi(
    channel: AcquisitionChannel,
    avg_annual_margin_gbp: float,
    base_churn_pct: float,
    discount_rate: float = 0.10,
) -> ChannelROIResult:
    cac = _BASE_CAC_GBP[channel]
    churn_factor = _CHANNEL_CHURN_FACTOR[channel]
    effective_churn = min(base_churn_pct * churn_factor, 1.0)
    tenure_years = 1.0 / effective_churn if effective_churn > 0 else 20.0
    n = tenure_years
    r = discount_rate
    clv = avg_annual_margin_gbp * ((1 - (1 + r) ** -n) / r)
    roi = round(clv / cac, 3) if cac > 0 else 0.0
    return ChannelROIResult(
        channel=channel,
        avg_cac_gbp=round(cac, 2),
        avg_annual_margin_gbp=round(avg_annual_margin_gbp, 2),
        base_churn_pct=round(base_churn_pct, 4),
        effective_churn_pct=round(effective_churn, 4),
        expected_tenure_years=round(tenure_years, 2),
        roi_ratio=roi,
    )


def channel_roi_ranking(
    avg_annual_margin_gbp: float,
    base_churn_pct: float,
) -> List[ChannelROIResult]:
    results = [
        compute_channel_roi(ch, avg_annual_margin_gbp, base_churn_pct)
        for ch in AcquisitionChannel
    ]
    return sorted(results, key=lambda r: r.roi_ratio, reverse=True)
