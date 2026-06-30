"""Customer Communication Preference Register.

UK energy suppliers must respect customer communication preferences under:
- SLC 25C: Suppliers must provide customers with option to choose contact channel
- GDPR / UK GDPR (2018): Lawful basis for processing; right to opt-out of marketing
- Privacy and Electronic Communications Regulations (PECR 2003): email/SMS marketing

Communication channels:
- EMAIL: For billing, notifications, marketing (PECR opt-in required for marketing)
- POST: Traditional; required for some statutory notices
- PHONE: Including auto-dialler rules (PECR)
- SMS: Requires PECR opt-in
- PORTAL: In-app / online account notifications
- PAPER_BILL: Default; must be maintained unless customer explicitly opts for paperless

Key constraints:
- Essential communications (bills, SLC notices) cannot be blocked
- Marketing requires positive opt-in (GDPR Article 6/PECR)
- Customers can withdraw consent at any time
- Right to erasure (GDPR Article 17) — data suppression

Epistemic: the company knows customer preferences from their own interactions.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum


class CommChannel(str, Enum):
    EMAIL = "email"
    POST = "post"
    PHONE = "phone"
    SMS = "sms"
    PORTAL = "portal"
    PAPER_BILL = "paper_bill"


class CommPurpose(str, Enum):
    BILLING = "billing"           # Essential; cannot be blocked
    SERVICE_NOTICE = "service_notice"  # Essential regulatory notices
    MARKETING = "marketing"        # Requires opt-in
    TARIFF_ALERT = "tariff_alert"  # Price change notification
    TRIAD_ALERT = "triad_alert"    # I&C triad warning


_ESSENTIAL_PURPOSES = frozenset({CommPurpose.BILLING, CommPurpose.SERVICE_NOTICE})


@dataclass(frozen=True)
class ChannelPreference:
    channel: CommChannel
    opted_in: bool
    preference_date: date
    purpose: CommPurpose = CommPurpose.BILLING


class CustomerCommPreferences:
    def __init__(self, account_id: str) -> None:
        self.account_id = account_id
        self._preferences: list[ChannelPreference] = []
        self.marketing_opt_in: bool = False
        self.marketing_opt_date: date | None = None
        self.suppressed: bool = False

    def set_preference(self, channel: CommChannel, opted_in: bool, preference_date: date, purpose: CommPurpose = CommPurpose.BILLING) -> None:
        self._preferences.append(ChannelPreference(channel=channel, opted_in=opted_in, preference_date=preference_date, purpose=purpose))

    def can_contact(self, channel: CommChannel, purpose: CommPurpose) -> bool:
        if self.suppressed:
            return purpose in _ESSENTIAL_PURPOSES
        if purpose in _ESSENTIAL_PURPOSES:
            return True
        if purpose == CommPurpose.MARKETING and not self.marketing_opt_in:
            return False
        # Find latest preference for this channel+purpose
        matching = [p for p in self._preferences if p.channel == channel and p.purpose == purpose]
        if not matching:
            return channel in (CommChannel.EMAIL, CommChannel.POST, CommChannel.PORTAL)
        latest = max(matching, key=lambda p: p.preference_date)
        return latest.opted_in

    def set_marketing_opt_in(self, opted_in: bool, preference_date: date) -> None:
        self.marketing_opt_in = opted_in
        self.marketing_opt_date = preference_date

    def suppress(self) -> None:
        self.suppressed = True


class CustomerCommPreferenceRegister:
    """GDPR/PECR-compliant communication preference management."""

    def __init__(self) -> None:
        self._accounts: dict[str, CustomerCommPreferences] = {}

    def _ensure(self, account_id: str) -> CustomerCommPreferences:
        if account_id not in self._accounts:
            self._accounts[account_id] = CustomerCommPreferences(account_id)
        return self._accounts[account_id]

    def set_preference(self, account_id: str, channel: CommChannel, opted_in: bool, preference_date: date, purpose: CommPurpose = CommPurpose.BILLING) -> None:
        self._ensure(account_id).set_preference(channel, opted_in, preference_date, purpose)

    def set_marketing_opt_in(self, account_id: str, opted_in: bool, preference_date: date) -> None:
        self._ensure(account_id).set_marketing_opt_in(opted_in, preference_date)

    def suppress_account(self, account_id: str) -> None:
        self._ensure(account_id).suppress()

    def can_contact(self, account_id: str, channel: CommChannel, purpose: CommPurpose) -> bool:
        if account_id not in self._accounts:
            if purpose in _ESSENTIAL_PURPOSES:
                return True
            if purpose == CommPurpose.MARKETING:
                return False
            return channel in (CommChannel.EMAIL, CommChannel.POST, CommChannel.PORTAL)
        return self._accounts[account_id].can_contact(channel, purpose)

    @property
    def marketing_opt_in_accounts(self) -> list[str]:
        return [aid for aid, pref in self._accounts.items() if pref.marketing_opt_in]

    @property
    def suppressed_accounts(self) -> list[str]:
        return [aid for aid, pref in self._accounts.items() if pref.suppressed]

    @property
    def paperless_accounts(self) -> list[str]:
        result = []
        for aid, pref in self._accounts.items():
            paper_prefs = [p for p in pref._preferences if p.channel == CommChannel.PAPER_BILL]
            if paper_prefs:
                latest = max(paper_prefs, key=lambda p: p.preference_date)
                if not latest.opted_in:
                    result.append(aid)
        return result

    def comm_preference_summary(self) -> str:
        n = len(self._accounts)
        n_mkt = len(self.marketing_opt_in_accounts)
        n_supp = len(self.suppressed_accounts)
        return (
            "Customer Comm Preference Register (GDPR/PECR/SLC 25C)\n"
            "Accounts: {:d} | Marketing opt-in: {:d} | Suppressed: {:d}".format(n, n_mkt, n_supp)
        )
