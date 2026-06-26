"""Prepayment meter (PPM) management.

UK suppliers manage ~4M prepayment meter customers who pay in advance.
Key mechanics:
- Top-up via key/card/smart: credited to meter balance
- If in debt (from prior arrears): fraction of top-up withheld for recovery
- Emergency credit: small buffer when balance hits zero (standard 5 GBP,
  10 GBP for vulnerable customers)
- Friendly hours: Ofgem prohibits supply cut between 10pm-6am or weekends
- Self-disconnection: customer has exhausted emergency credit and supply cuts
  during non-friendly hours (cannot afford to top up)

The 2022 crisis drove a self-disconnection surge as unit rates trebled --
emergency credit now lasted days not weeks for typical customers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


_STANDARD_EMERGENCY_CREDIT_GBP = 5.0
_VULNERABLE_EMERGENCY_CREDIT_GBP = 10.0
_STANDARD_DEBT_RECOVERY_RATE = 0.50   # 50p per GBP top-up goes to debt
_VULNERABLE_DEBT_RECOVERY_RATE = 0.25  # capped for vulnerable customers


@dataclass
class PPMAccount:
    customer_id: str
    meter_id: str
    balance_gbp: float = 0.0
    debt_gbp: float = 0.0          # outstanding debt being recovered
    emergency_credit_limit_gbp: float = _STANDARD_EMERGENCY_CREDIT_GBP
    debt_recovery_rate: float = _STANDARD_DEBT_RECOVERY_RATE
    is_vulnerable: bool = False

    def __post_init__(self):
        if self.is_vulnerable:
            self.emergency_credit_limit_gbp = _VULNERABLE_EMERGENCY_CREDIT_GBP
            self.debt_recovery_rate = _VULNERABLE_DEBT_RECOVERY_RATE

    @property
    def in_emergency_credit(self) -> bool:
        return self.balance_gbp < 0.0

    @property
    def emergency_credit_used_gbp(self) -> float:
        return abs(min(0.0, self.balance_gbp))

    @property
    def emergency_credit_remaining_gbp(self) -> float:
        return max(0.0, self.emergency_credit_limit_gbp - self.emergency_credit_used_gbp)


def _is_friendly_hours(dt: datetime) -> bool:
    """Ofgem rule: no disconnection between 10pm-6am or on weekends."""
    if dt.weekday() >= 5:   # Saturday=5, Sunday=6
        return True
    return dt.hour >= 22 or dt.hour < 6


class PPMBook:
    """Portfolio of prepayment meter accounts."""

    def __init__(self):
        self._accounts: dict[str, PPMAccount] = {}

    def register(self, account: PPMAccount) -> PPMAccount:
        self._accounts[account.customer_id] = account
        return account

    def get(self, customer_id: str) -> PPMAccount | None:
        return self._accounts.get(customer_id)

    def top_up(self, customer_id: str, amount_gbp: float, date: str) -> dict:
        """Credit a top-up to the account.

        If debt exists, debt_recovery_rate fraction is withheld for debt
        repayment; remainder goes to balance. Once debt is cleared, full
        top-up goes to balance.

        Returns: dict with balance_before, debt_before, debt_repaid,
                 credited_to_balance, balance_after, debt_after.
        """
        acc = self._accounts[customer_id]
        balance_before = acc.balance_gbp
        debt_before = acc.debt_gbp

        if acc.debt_gbp > 0:
            withheld = min(amount_gbp * acc.debt_recovery_rate, acc.debt_gbp)
            credited = amount_gbp - withheld
            acc.debt_gbp = round(acc.debt_gbp - withheld, 4)
        else:
            withheld = 0.0
            credited = amount_gbp

        acc.balance_gbp = round(acc.balance_gbp + credited, 4)
        return {
            "customer_id": customer_id,
            "date": date,
            "top_up_gbp": amount_gbp,
            "balance_before": round(balance_before, 4),
            "debt_before": round(debt_before, 4),
            "debt_repaid_gbp": round(withheld, 4),
            "credited_to_balance_gbp": round(credited, 4),
            "balance_after": acc.balance_gbp,
            "debt_after": acc.debt_gbp,
        }

    def consume_daily(
        self,
        customer_id: str,
        kwh: float,
        rate_gbp_per_kwh: float,
        sc_gbp_per_day: float,
        date: str,
    ) -> dict:
        """Deduct one day of consumption cost from the meter balance.

        When balance reaches zero, draws from emergency credit up to the limit.
        Returns: dict with cost, balance_before, balance_after, in_emergency_credit,
                 emergency_credit_used, emergency_credit_remaining.
        """
        acc = self._accounts[customer_id]
        cost = round(kwh * rate_gbp_per_kwh + sc_gbp_per_day, 4)
        balance_before = acc.balance_gbp
        acc.balance_gbp = round(acc.balance_gbp - cost, 4)
        return {
            "customer_id": customer_id,
            "date": date,
            "cost_gbp": cost,
            "balance_before": round(balance_before, 4),
            "balance_after": acc.balance_gbp,
            "in_emergency_credit": acc.in_emergency_credit,
            "emergency_credit_used_gbp": round(acc.emergency_credit_used_gbp, 4),
            "emergency_credit_remaining_gbp": round(acc.emergency_credit_remaining_gbp, 4),
        }

    def is_friendly_hours(self, dt: datetime) -> bool:
        """Return True if dt falls in Ofgem friendly hours (no disconnect)."""
        return _is_friendly_hours(dt)

    def is_self_disconnected(self, customer_id: str, dt: datetime) -> bool:
        """True if customer has exhausted emergency credit and is in supply cut.

        A customer is self-disconnected when:
        - Their balance is below -emergency_credit_limit (emergency credit exhausted)
        - It is NOT friendly hours (10pm-6am / weekends are protected)
        """
        acc = self._accounts.get(customer_id)
        if acc is None:
            return False
        exhausted = acc.balance_gbp < -acc.emergency_credit_limit_gbp
        return exhausted and not _is_friendly_hours(dt)

    def portfolio_summary(self, dt: datetime | None = None) -> dict:
        """Portfolio-wide PPM statistics.

        dt: used for self-disconnection check (defaults to midnight weekday
        to give a worst-case daytime snapshot).
        """
        if dt is None:
            dt = datetime(2022, 1, 10, 12, 0)   # representative weekday noon
        accounts = list(self._accounts.values())
        if not accounts:
            return {
                "total_accounts": 0,
                "self_disconnected": 0,
                "in_emergency_credit": 0,
                "avg_balance_gbp": 0.0,
                "total_debt_gbp": 0.0,
                "pct_self_disconnected": 0.0,
                "pct_in_emergency_credit": 0.0,
            }
        self_disc = sum(
            1 for a in accounts
            if a.balance_gbp < -a.emergency_credit_limit_gbp and not _is_friendly_hours(dt)
        )
        in_emerg = sum(1 for a in accounts if a.in_emergency_credit)
        avg_balance = round(sum(a.balance_gbp for a in accounts) / len(accounts), 2)
        total_debt = round(sum(a.debt_gbp for a in accounts), 2)
        n = len(accounts)
        return {
            "total_accounts": n,
            "self_disconnected": self_disc,
            "in_emergency_credit": in_emerg,
            "avg_balance_gbp": avg_balance,
            "total_debt_gbp": total_debt,
            "pct_self_disconnected": round(100 * self_disc / n, 1),
            "pct_in_emergency_credit": round(100 * in_emerg / n, 1),
        }
