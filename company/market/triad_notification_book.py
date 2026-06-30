"""Triad Notification Book — proactive I&C demand reduction for TNUoS Triad avoidance."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional

# TNUoS Triad-related locational charge rate by year (£/kW/year) for HH I&C customers.
# Source: National Grid ESO Transmission Charges; representative midlands zone.
_TNUOS_TRIAD_RATE_GBP_PER_KW: dict[int, float] = {
    2016: 36.40, 2017: 40.20, 2018: 42.80, 2019: 44.50,
    2020: 47.20, 2021: 50.10, 2022: 60.40, 2023: 66.30,
    2024: 70.10, 2025: 73.50,
}

# Triad season is November through February (Triad windows are Nov 1 – Feb 28/29)
_TRIAD_SEASON_MONTHS = {11, 12, 1, 2}

# Triad settlement periods at risk: 16:00-19:30 (periods 33-39)
_TRIAD_RISK_PERIODS = frozenset(range(33, 40))

# Estimated demand reduction when a customer responds to an alert (fraction of peak)
_ALERT_RESPONSE_REDUCTION_FRACTION = 0.70


class AlertStatus(str, Enum):
    ISSUED = "issued"
    RESPONDED = "responded"
    NO_RESPONSE = "no_response"


@dataclass(frozen=True)
class TriadAlert:
    account_id: str
    alert_date: str          # ISO date of the suspected Triad period
    settlement_period: int   # Half-hour period flagged
    estimated_demand_kw: float  # Customer's expected demand at this period
    status: AlertStatus
    confirmed_triad: bool = False  # Updated post-settlement when NESO confirms

    @property
    def demand_reduction_kw(self) -> float:
        if self.status == AlertStatus.RESPONDED:
            return round(self.estimated_demand_kw * _ALERT_RESPONSE_REDUCTION_FRACTION, 2)
        return 0.0


@dataclass(frozen=True)
class CustomerTriadProfile:
    account_id: str
    annual_kwh: float
    peak_demand_kw: float     # Estimated peak demand at Triad periods
    zone: str = "midlands"    # Grid zone (affects locational rate)
    is_enrolled: bool = True  # Whether signed up for Triad notification

    @property
    def _triad_charge_full(self) -> float:
        """TNUoS charge without demand reduction (full Triad demand)."""
        return self.peak_demand_kw  # will be multiplied by rate in book

    def triad_charge_gbp(self, year: int) -> float:
        rate = _TNUOS_TRIAD_RATE_GBP_PER_KW.get(year, 70.0)
        return round(self.peak_demand_kw * rate, 2)

    def avoided_charge_gbp(self, year: int, reduction_kw: float) -> float:
        rate = _TNUOS_TRIAD_RATE_GBP_PER_KW.get(year, 70.0)
        return round(reduction_kw * rate, 2)


@dataclass(frozen=True)
class TriadSavingsRecord:
    account_id: str
    year: int
    alerts_issued: int
    alerts_responded: int
    total_reduction_kw: float
    estimated_saving_gbp: float
    full_triad_charge_gbp: float

    @property
    def response_rate_pct(self) -> float:
        if self.alerts_issued == 0:
            return 0.0
        return round(self.alerts_responded / self.alerts_issued * 100, 1)

    @property
    def saving_pct(self) -> float:
        if self.full_triad_charge_gbp == 0:
            return 0.0
        return round(self.estimated_saving_gbp / self.full_triad_charge_gbp * 100, 1)


class TriadNotificationBook:
    """Tracks Triad alert issuance and demand-reduction savings for I&C HH customers."""

    def __init__(self) -> None:
        self._profiles: dict[str, CustomerTriadProfile] = {}
        self._alerts: list[TriadAlert] = []

    def enrol(self, profile: CustomerTriadProfile) -> CustomerTriadProfile:
        self._profiles[profile.account_id] = profile
        return profile

    def issue_alert(self, alert: TriadAlert) -> TriadAlert:
        if alert.account_id not in self._profiles:
            raise KeyError(f"Account {alert.account_id} not enrolled")
        if not self._profiles[alert.account_id].is_enrolled:
            raise ValueError(f"Account {alert.account_id} is not enrolled in Triad notification")
        self._alerts.append(alert)
        return alert

    @staticmethod
    def is_triad_season(d: date) -> bool:
        return d.month in _TRIAD_SEASON_MONTHS

    @staticmethod
    def is_triad_risk_period(settlement_period: int) -> bool:
        return settlement_period in _TRIAD_RISK_PERIODS

    def alerts_for_account(self, account_id: str) -> list[TriadAlert]:
        return [a for a in self._alerts if a.account_id == account_id]

    def alerts_for_year(self, year: int) -> list[TriadAlert]:
        return [a for a in self._alerts if a.alert_date.startswith(str(year)) or
                a.alert_date.startswith(str(year - 1) + "-11") or
                a.alert_date.startswith(str(year - 1) + "-12")]

    def savings_for_account_year(self, account_id: str, year: int) -> TriadSavingsRecord:
        profile = self._profiles.get(account_id)
        if not profile:
            raise KeyError(account_id)
        year_alerts = [a for a in self.alerts_for_account(account_id)
                       if a.alert_date[:4] == str(year) or
                       a.alert_date[:7] in (str(year - 1) + "-11", str(year - 1) + "-12")]
        issued = len(year_alerts)
        responded = sum(1 for a in year_alerts if a.status == AlertStatus.RESPONDED)
        total_reduction = sum(a.demand_reduction_kw for a in year_alerts)
        full_charge = profile.triad_charge_gbp(year)
        saving = profile.avoided_charge_gbp(year, total_reduction)
        return TriadSavingsRecord(
            account_id=account_id,
            year=year,
            alerts_issued=issued,
            alerts_responded=responded,
            total_reduction_kw=round(total_reduction, 2),
            estimated_saving_gbp=round(saving, 2),
            full_triad_charge_gbp=round(full_charge, 2),
        )

    def enrolled_accounts(self) -> list[CustomerTriadProfile]:
        return [p for p in self._profiles.values() if p.is_enrolled]

    def total_portfolio_saving_gbp(self, year: int) -> float:
        total = 0.0
        for account_id in self._profiles:
            try:
                rec = self.savings_for_account_year(account_id, year)
                total += rec.estimated_saving_gbp
            except (KeyError, ValueError):
                pass
        return round(total, 2)

    def triad_notification_summary(self) -> str:
        if not self._profiles:
            return "No accounts enrolled in Triad notification service."
        enrolled = len(self.enrolled_accounts())
        total_alerts = len(self._alerts)
        responded = sum(1 for a in self._alerts if a.status == AlertStatus.RESPONDED)
        rate = responded / total_alerts * 100 if total_alerts else 0
        confirmed = sum(1 for a in self._alerts if a.confirmed_triad)
        lines = [
            f"Triad Notification Book: {enrolled} enrolled accounts",
            f"Total alerts issued: {total_alerts} | Responded: {responded} ({rate:.0f}%)",
            f"Confirmed Triad hits in alert set: {confirmed}",
        ]
        return "\n".join(lines)
