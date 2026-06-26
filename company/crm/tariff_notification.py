"""Tariff change notification system: 42-day advance notice per Ofgem SLC 25B."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


ADVANCE_NOTICE_DAYS = 42  # Ofgem SLC 25B minimum


class NotificationChannel(str, Enum):
    EMAIL = 'email'
    POST = 'post'
    SMS = 'sms'
    IN_APP = 'in_app'


class NotificationStatus(str, Enum):
    SCHEDULED = 'scheduled'
    SENT = 'sent'
    BOUNCED = 'bounced'
    CONFIRMED_READ = 'confirmed_read'


class TariffChangeReason(str, Enum):
    MARKET_PRICE_CHANGE = 'market_price_change'
    PRICE_CAP_CHANGE = 'price_cap_change'
    CONTRACT_RENEWAL = 'contract_renewal'
    REGULATORY_CHANGE = 'regulatory_change'
    PRODUCT_RESTRUCTURE = 'product_restructure'


@dataclass
class TariffNotification:
    notification_id: str
    customer_id: str
    channel: NotificationChannel
    sent_date: dt.date
    effective_date: dt.date
    reason: TariffChangeReason
    old_unit_rate_pence: float
    new_unit_rate_pence: float
    old_standing_pence: float
    new_standing_pence: float
    status: NotificationStatus = NotificationStatus.SCHEDULED

    @property
    def notice_days(self) -> int:
        return (self.effective_date - self.sent_date).days

    @property
    def meets_advance_notice(self) -> bool:
        return self.notice_days >= ADVANCE_NOTICE_DAYS

    @property
    def unit_rate_change_pct(self) -> float:
        if self.old_unit_rate_pence <= 0:
            return 0.0
        return round((self.new_unit_rate_pence - self.old_unit_rate_pence)
                      / self.old_unit_rate_pence * 100, 1)

    @property
    def is_price_increase(self) -> bool:
        return self.new_unit_rate_pence > self.old_unit_rate_pence


class TariffNotificationLog:
    def __init__(self) -> None:
        self._notifications: List[TariffNotification] = []

    def send(self, notification_id: str, customer_id: str,
               channel: NotificationChannel, sent_date: dt.date,
               effective_date: dt.date, reason: TariffChangeReason,
               old_unit_pence: float, new_unit_pence: float,
               old_standing_pence: float, new_standing_pence: float
               ) -> TariffNotification:
        n = TariffNotification(
            notification_id=notification_id, customer_id=customer_id,
            channel=channel, sent_date=sent_date, effective_date=effective_date,
            reason=reason, old_unit_rate_pence=old_unit_pence,
            new_unit_rate_pence=new_unit_pence,
            old_standing_pence=old_standing_pence,
            new_standing_pence=new_standing_pence,
            status=NotificationStatus.SENT,
        )
        self._notifications.append(n)
        return n

    def get(self, notification_id: str) -> Optional[TariffNotification]:
        return next((n for n in self._notifications
                      if n.notification_id == notification_id), None)

    def mark_confirmed(self, notification_id: str) -> None:
        n = self.get(notification_id)
        if n:
            n.status = NotificationStatus.CONFIRMED_READ

    def compliance_breaches(self) -> List[TariffNotification]:
        return [n for n in self._notifications if not n.meets_advance_notice]

    def customer_notifications(self, customer_id: str) -> List[TariffNotification]:
        return [n for n in self._notifications if n.customer_id == customer_id]

    def price_increases(self, year: int) -> List[TariffNotification]:
        return [n for n in self._notifications
                if n.sent_date.year == year and n.is_price_increase]

    def notification_summary(self, year: int) -> dict:
        yr = [n for n in self._notifications if n.sent_date.year == year]
        breaches = [n for n in yr if not n.meets_advance_notice]
        return {
            'year': year,
            'total_sent': len(yr),
            'compliance_breaches': len(breaches),
            'price_increases': len([n for n in yr if n.is_price_increase]),
            'channels': list(set(n.channel.value for n in yr)),
        }
