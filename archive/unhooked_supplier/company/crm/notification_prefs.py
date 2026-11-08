"""Customer notification and communication preferences.

UK energy suppliers must:
- Record explicit opt-in/opt-out for marketing communications (PECR/GDPR)
- Provide service notifications via at least one channel (SLC 14B)
- Maintain a preference history for audit purposes

Channel options: email, sms, post, phone, portal
Preference types:
  - service: essential notifications (bill ready, price change, switch). Always allowed if any channel active.
  - marketing: promotional and upsell. Requires explicit opt-in.
  - paper_bills: whether to issue paper statements (default True for non-digital)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


_ALL_CHANNELS = ("email", "sms", "post", "phone", "portal")
_PREF_TYPES = ("service", "marketing", "paper_bills")


@dataclass
class CommPreference:
    customer_id: str
    channel: str
    pref_type: str
    enabled: bool
    updated_date: str
    source: Literal["customer", "default", "admin"] = "default"


class NotificationPreferences:
    """Manages comms preferences for all customers."""

    def __init__(self):
        self._prefs: dict[tuple[str, str, str], CommPreference] = {}

    def set(
        self,
        customer_id: str,
        channel: str,
        pref_type: str,
        enabled: bool,
        updated_date: str,
        source: str = "customer",
    ) -> CommPreference:
        if channel not in _ALL_CHANNELS:
            raise ValueError(f"Unknown channel: {channel}")
        if pref_type not in _PREF_TYPES:
            raise ValueError(f"Unknown pref_type: {pref_type}")
        p = CommPreference(customer_id, channel, pref_type, enabled, updated_date, source)
        self._prefs[(customer_id, channel, pref_type)] = p
        return p

    def get(self, customer_id: str, channel: str, pref_type: str) -> bool | None:
        p = self._prefs.get((customer_id, channel, pref_type))
        return p.enabled if p else None

    def for_customer(self, customer_id: str) -> list[CommPreference]:
        return [p for (cid, _, _), p in self._prefs.items() if cid == customer_id]

    def enabled_channels_for(self, customer_id: str, pref_type: str) -> list[str]:
        return [
            p.channel for p in self.for_customer(customer_id)
            if p.pref_type == pref_type and p.enabled
        ]

    def can_contact(self, customer_id: str, channel: str, pref_type: str) -> bool:
        v = self.get(customer_id, channel, pref_type)
        if v is None:
            # Default: service always allowed on email/post; marketing requires explicit opt-in
            if pref_type == "service":
                return channel in ("email", "post")
            return False
        return v

    def opted_out_marketing(self, customer_id: str) -> bool:
        """True if customer has no enabled marketing channel."""
        return len(self.enabled_channels_for(customer_id, "marketing")) == 0

    def paper_bill_customers(self) -> list[str]:
        return list({
            p.customer_id for p in self._prefs.values()
            if p.pref_type == "paper_bills" and p.enabled
        })

    def summary(self, customer_id: str) -> dict:
        prefs = self.for_customer(customer_id)
        return {
            "service_channels": self.enabled_channels_for(customer_id, "service"),
            "marketing_channels": self.enabled_channels_for(customer_id, "marketing"),
            "paper_bills": any(p.pref_type == "paper_bills" and p.enabled for p in prefs),
            "marketing_opted_out": self.opted_out_marketing(customer_id),
        }
