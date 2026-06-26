"""Tariff change notification (TCN) management.

Ofgem SLC 22 (and SLC 22A for SVT) requires suppliers to notify domestic
customers of tariff changes:
  - SVT price changes: 30 days minimum notice
  - Fixed term tariff end/renewal: 42-49 days notice before expiry
  - Price cap resets: notification before each quarterly cap period

The TCN records when notification was issued and whether the notice
period has been met. Non-compliant TCNs are escalated to the compliance
team before the change effective date.

TCNs are also required for notification of Warm Home Discount eligibility
changes and EV / off-peak tariff restructuring.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal


_SVT_NOTICE_DAYS = 30
_FIXED_TERM_NOTICE_DAYS = 42
_CAP_NOTICE_DAYS = 30


@dataclass
class TariffChangeNotice:
    notice_id: str
    customer_id: str
    change_type: Literal["svt_price_change", "fixed_term_expiry", "cap_reset", "whd_change", "other"]
    notification_date: str       # ISO date the customer was notified
    effective_date: str          # ISO date the change takes effect
    old_unit_rate_p_kwh: float
    new_unit_rate_p_kwh: float
    channel: str = "email"      # channel used for notification
    acknowledged: bool = False

    @property
    def notice_days(self) -> int:
        n = date.fromisoformat(self.notification_date)
        e = date.fromisoformat(self.effective_date)
        return (e - n).days

    @property
    def required_notice_days(self) -> int:
        if self.change_type in ("svt_price_change", "cap_reset", "whd_change", "other"):
            return _SVT_NOTICE_DAYS
        elif self.change_type == "fixed_term_expiry":
            return _FIXED_TERM_NOTICE_DAYS
        return _SVT_NOTICE_DAYS

    @property
    def is_compliant(self) -> bool:
        return self.notice_days >= self.required_notice_days

    @property
    def rate_change_pct(self) -> float:
        if self.old_unit_rate_p_kwh == 0:
            return 0.0
        return round(100.0 * (self.new_unit_rate_p_kwh - self.old_unit_rate_p_kwh) / self.old_unit_rate_p_kwh, 1)


class TariffChangeLog:
    """Log of all tariff change notifications issued."""

    def __init__(self):
        self._notices: list[TariffChangeNotice] = []

    def record(self, notice: TariffChangeNotice) -> TariffChangeNotice:
        self._notices.append(notice)
        return notice

    def for_customer(self, customer_id: str) -> list[TariffChangeNotice]:
        return [n for n in self._notices if n.customer_id == customer_id]

    def non_compliant(self) -> list[TariffChangeNotice]:
        return [n for n in self._notices if not n.is_compliant]

    def pending_effective(self, as_of_date: str) -> list[TariffChangeNotice]:
        """Notices where the effective date is in the future."""
        check = date.fromisoformat(as_of_date)
        return [n for n in self._notices if date.fromisoformat(n.effective_date) > check]

    def by_change_type(self, change_type: str) -> list[TariffChangeNotice]:
        return [n for n in self._notices if n.change_type == change_type]

    def unacknowledged(self) -> list[TariffChangeNotice]:
        return [n for n in self._notices if not n.acknowledged]

    def summary(self) -> dict:
        return {
            "total": len(self._notices),
            "non_compliant": len(self.non_compliant()),
            "unacknowledged": len(self.unacknowledged()),
            "compliance_rate_pct": round(
                100.0 * (len(self._notices) - len(self.non_compliant())) / len(self._notices), 1
            ) if self._notices else 100.0,
        }
