"""Supply licence health monitor: going-concern checks against Ofgem SLC thresholds."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class LicenceCheckStatus(str, Enum):
    PASS = 'pass'
    WATCH = 'watch'
    BREACH = 'breach'


@dataclass(frozen=True)
class LicenceCheck:
    name: str
    description: str
    value: float
    threshold: float
    status: LicenceCheckStatus
    notes: str = ''

    @property
    def headroom(self) -> float:
        return round(self.value - self.threshold, 2)


@dataclass(frozen=True)
class LicenceHealthReport:
    as_of: dt.date
    checks: tuple

    @property
    def pass_count(self) -> int:
        return sum(1 for c in self.checks if c.status == LicenceCheckStatus.PASS)

    @property
    def watch_count(self) -> int:
        return sum(1 for c in self.checks if c.status == LicenceCheckStatus.WATCH)

    @property
    def breach_count(self) -> int:
        return sum(1 for c in self.checks if c.status == LicenceCheckStatus.BREACH)

    @property
    def overall_status(self) -> LicenceCheckStatus:
        if self.breach_count > 0:
            return LicenceCheckStatus.BREACH
        if self.watch_count > 0:
            return LicenceCheckStatus.WATCH
        return LicenceCheckStatus.PASS

    @property
    def is_going_concern(self) -> bool:
        return self.breach_count == 0

    def get(self, name: str) -> Optional[LicenceCheck]:
        for c in self.checks:
            if c.name == name:
                return c
        return None

    def summary(self) -> dict:
        return {
            'as_of': self.as_of.isoformat(),
            'pass': self.pass_count,
            'watch': self.watch_count,
            'breach': self.breach_count,
            'overall_status': self.overall_status.value,
            'is_going_concern': self.is_going_concern,
        }


def _check(name: str, description: str, value: float,
            min_threshold: float, watch_pct: float = 0.20, notes: str = '') -> LicenceCheck:
    if value < min_threshold:
        status = LicenceCheckStatus.BREACH
    elif value < min_threshold * (1 + watch_pct):
        status = LicenceCheckStatus.WATCH
    else:
        status = LicenceCheckStatus.PASS
    return LicenceCheck(name=name, description=description, value=value,
                         threshold=min_threshold, status=status, notes=notes)


def build_licence_health_report(
    as_of: dt.date,
    active_customer_count: int,
    net_assets_gbp: float,
    treasury_gbp: float,
    weeks_cash_runway: float,
    bad_debt_ratio_pct: float,
    complaints_per_100: float,
) -> LicenceHealthReport:
    checks = [
        _check('customer_count', 'Minimum supply base (Ofgem viability)',
               float(active_customer_count), 50.0, watch_pct=0.5,
               notes='<50 triggers Ofgem viability review'),
        _check('net_assets_gbp', 'Net assets positive (SLC 28)',
               net_assets_gbp, 0.0, watch_pct=0.5,
               notes='Negative net assets = balance sheet insolvency'),
        _check('treasury_gbp', 'Minimum operating liquidity (SLC 4B)',
               treasury_gbp, 100_000.0, watch_pct=0.5),
        _check('cash_runway_weeks', 'Cash runway >= 8 weeks',
               weeks_cash_runway, 8.0, watch_pct=0.25,
               notes='< 8w triggers board escalation; < 4w triggers SoLR consideration'),
        LicenceCheck(
            name='bad_debt_ratio', description='Bad debt < 5% of revenue (Ofgem watch)',
            value=bad_debt_ratio_pct, threshold=5.0,
            status=(LicenceCheckStatus.BREACH if bad_debt_ratio_pct > 5.0
                    else LicenceCheckStatus.WATCH if bad_debt_ratio_pct > 3.0
                    else LicenceCheckStatus.PASS),
        ),
        LicenceCheck(
            name='complaints_per_100', description='Complaints < 1 per 100 customers (Ofgem benchmark)',
            value=complaints_per_100, threshold=1.0,
            status=(LicenceCheckStatus.BREACH if complaints_per_100 > 3.0
                    else LicenceCheckStatus.WATCH if complaints_per_100 > 1.0
                    else LicenceCheckStatus.PASS),
        ),
    ]
    return LicenceHealthReport(as_of=as_of, checks=tuple(checks))
