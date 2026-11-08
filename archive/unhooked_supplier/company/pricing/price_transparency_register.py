"""Price Transparency Publication Register (Phase DL).

Ofgem SLC 31 and the Energy Price Comparison Regulations 2008 require suppliers
to publish their current tariff prices in a standardised format. This enables:
- Comparison website feeds (Energy Guide, Ofgem Price Comparison)
- Annual tariff comparison tools
- Consumer information rights (SLC 25C)

Key requirements:
- Standing charge (pence per day)
- Unit rate (pence per kWh)
- Tariff name and end date
- Payment method and fuel type
- Exit fee (if any)
- Must be updated within 48 hours of any price change

Midata standard (2013): machine-readable tariff data allowing account switching.
Ofgem tariff comparison tool (TCT) feed required.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class PublicationChannel(str, Enum):
    WEBSITE = "website"              # supplier website
    OFGEM_FEED = "ofgem_feed"        # Ofgem/TCT API feed
    COMPARISON_SITE = "comparison"   # third-party comparison sites
    MIDATA = "midata"                # midata standard export


class TariffType(str, Enum):
    FIXED = "fixed"
    VARIABLE_SVT = "variable_svt"
    ECONOMY_7 = "economy_7"
    TIME_OF_USE = "time_of_use"
    PREPAYMENT = "prepayment"


class UpdateStatus(str, Enum):
    PUBLISHED = "published"
    PENDING = "pending"              # change notified, not yet published
    STALE = "stale"                  # past 48h update window
    WITHDRAWN = "withdrawn"          # tariff no longer offered


_MAX_UPDATE_HOURS = 48               # SLC 31 / TCT requirement
_MIN_NOTICE_DAYS_ON_RATE_CHANGE = 30 # SLC 22: 30 days notice of price change


@dataclass(frozen=True)
class TariffPublication:
    pub_id: str
    tariff_name: str
    fuel: str                        # ELECTRICITY / GAS / DUAL_FUEL
    tariff_type: TariffType
    standing_charge_pence_per_day: float
    unit_rate_pence_per_kwh: float
    effective_date: dt.date
    end_date: Optional[dt.date]      # None = open-ended (SVT/variable)
    exit_fee_gbp: float
    channel: PublicationChannel
    published_at: dt.datetime
    status: UpdateStatus = UpdateStatus.PUBLISHED
    previous_unit_rate: Optional[float] = None

    @property
    def is_fixed(self) -> bool:
        return self.tariff_type == TariffType.FIXED

    @property
    def rate_change_pct(self) -> Optional[float]:
        if self.previous_unit_rate is None or self.previous_unit_rate == 0:
            return None
        return (self.unit_rate_pence_per_kwh - self.previous_unit_rate) / self.previous_unit_rate

    @property
    def is_rate_increase(self) -> bool:
        change = self.rate_change_pct
        return change is not None and change > 0

    def is_stale(self, as_of: dt.datetime) -> bool:
        if self.status != UpdateStatus.PENDING:
            return False
        hours_pending = (as_of - self.published_at).total_seconds() / 3600
        return hours_pending > _MAX_UPDATE_HOURS

    @property
    def annual_cost_estimate_gbp(self) -> float:
        """Estimate annual cost for a typical domestic customer (3,100 kWh electricity)."""
        typical_kwh = 3100.0
        standing = self.standing_charge_pence_per_day * 365 / 100
        energy = self.unit_rate_pence_per_kwh * typical_kwh / 100
        return standing + energy


class PriceTransparencyRegister:
    """Tracks published tariff information across channels."""

    def __init__(self) -> None:
        self._records: List[TariffPublication] = []
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"PTP-{self._seq:04d}"

    def publish(
        self,
        tariff_name: str,
        fuel: str,
        tariff_type: TariffType,
        standing_charge_pence_per_day: float,
        unit_rate_pence_per_kwh: float,
        effective_date: dt.date,
        published_at: dt.datetime,
        channel: PublicationChannel,
        end_date: Optional[dt.date] = None,
        exit_fee_gbp: float = 0.0,
        status: UpdateStatus = UpdateStatus.PUBLISHED,
        previous_unit_rate: Optional[float] = None,
    ) -> TariffPublication:
        rec = TariffPublication(
            pub_id=self._next_id(),
            tariff_name=tariff_name,
            fuel=fuel,
            tariff_type=tariff_type,
            standing_charge_pence_per_day=standing_charge_pence_per_day,
            unit_rate_pence_per_kwh=unit_rate_pence_per_kwh,
            effective_date=effective_date,
            end_date=end_date,
            exit_fee_gbp=exit_fee_gbp,
            channel=channel,
            published_at=published_at,
            status=status,
            previous_unit_rate=previous_unit_rate,
        )
        self._records.append(rec)
        return rec

    def active_tariffs(self, as_of: dt.date) -> List[TariffPublication]:
        return [
            r for r in self._records
            if r.status == UpdateStatus.PUBLISHED
            and r.effective_date <= as_of
            and (r.end_date is None or r.end_date >= as_of)
        ]

    def stale_publications(self, as_of: dt.datetime) -> List[TariffPublication]:
        return [r for r in self._records if r.is_stale(as_of)]

    def by_channel(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for r in self._records:
            out[r.channel.value] = out.get(r.channel.value, 0) + 1
        return out

    def rate_increases(self) -> List[TariffPublication]:
        return [r for r in self._records if r.is_rate_increase]

    def withdrawn(self) -> List[TariffPublication]:
        return [r for r in self._records if r.status == UpdateStatus.WITHDRAWN]

    def cheapest_active(self, as_of: dt.date) -> Optional[TariffPublication]:
        active = self.active_tariffs(as_of)
        if not active:
            return None
        return min(active, key=lambda r: r.annual_cost_estimate_gbp)

    def price_transparency_summary(self) -> str:
        total = len(self._records)
        by_ch = self.by_channel()
        increases = len(self.rate_increases())
        return (
            f"Price Transparency Register (SLC 31/TCT): {total} publications. "
            f"By channel: {by_ch}. Rate increases: {increases}. "
            f"48h update window; 30-day notice on rate change."
        )
