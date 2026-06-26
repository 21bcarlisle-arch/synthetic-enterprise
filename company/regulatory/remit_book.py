from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MarketParticipant(str, Enum):
    SUPPLIER = "supplier"
    GENERATOR = "generator"
    BROKER = "broker"
    TRADER = "trader"


class REMITProductType(str, Enum):
    ELECTRICITY_FORWARD = "electricity_forward"
    ELECTRICITY_DAY_AHEAD = "electricity_day_ahead"
    ELECTRICITY_INTRADAY = "electricity_intraday"
    GAS_FORWARD = "gas_forward"
    GAS_DAY_AHEAD = "gas_day_ahead"
    CAPACITY_MARKET = "capacity_market"


class REMITStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"


_REPORTING_DEADLINE_HOURS = 1  # T+1 working day; using 24h for simplicity


@dataclass(frozen=True)
class REMITReport:
    report_id: str
    trade_id: str
    product_type: REMITProductType
    trade_date: str
    delivery_date: str
    volume_mwh: float
    price_gbp_per_mwh: float
    counterparty: str
    submitted_date: Optional[str] = None
    status: REMITStatus = REMITStatus.PENDING

    @property
    def notional_value_gbp(self) -> float:
        return round(self.volume_mwh * self.price_gbp_per_mwh, 2)

    @property
    def is_large_trade(self) -> bool:
        return self.volume_mwh >= 100.0

    @property
    def is_submitted(self) -> bool:
        return self.status in (REMITStatus.SUBMITTED, REMITStatus.ACKNOWLEDGED)


class REMITReportingBook:
    def __init__(self) -> None:
        self._reports: list[REMITReport] = []

    def record_report(self, report: REMITReport) -> REMITReport:
        self._reports.append(report)
        return report

    def submit_report(self, report_id: str, submitted_date: str) -> Optional[REMITReport]:
        from dataclasses import replace
        for i, r in enumerate(self._reports):
            if r.report_id == report_id:
                updated = replace(r, status=REMITStatus.SUBMITTED, submitted_date=submitted_date)
                self._reports[i] = updated
                return updated
        return None

    def acknowledge_report(self, report_id: str) -> Optional[REMITReport]:
        from dataclasses import replace
        for i, r in enumerate(self._reports):
            if r.report_id == report_id and r.status == REMITStatus.SUBMITTED:
                updated = replace(r, status=REMITStatus.ACKNOWLEDGED)
                self._reports[i] = updated
                return updated
        return None

    def pending_reports(self) -> list[REMITReport]:
        return [r for r in self._reports if r.status == REMITStatus.PENDING]

    def reports_for_product(self, product: REMITProductType) -> list[REMITReport]:
        return [r for r in self._reports if r.product_type == product]

    def large_trades(self) -> list[REMITReport]:
        return [r for r in self._reports if r.is_large_trade]

    def compliance_rate(self) -> float:
        if not self._reports:
            return 100.0
        submitted = sum(1 for r in self._reports if r.is_submitted)
        return round(submitted / len(self._reports) * 100, 2)

    def remit_summary(self) -> dict:
        return {
            "total_reports": len(self._reports),
            "pending": len(self.pending_reports()),
            "compliance_rate_pct": self.compliance_rate(),
            "large_trades": len(self.large_trades()),
        }
