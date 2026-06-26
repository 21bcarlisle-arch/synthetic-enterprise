"""Annual regulatory obligations report packaging ECO4, WHD, GSOP and Ofgem returns."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ObligationStatus(str, Enum):
    MET = 'met'
    AT_RISK = 'at_risk'
    BREACHED = 'breached'
    NOT_APPLICABLE = 'not_applicable'


@dataclass(frozen=True)
class ObligationLineItem:
    name: str
    obligation_value: float
    delivered_value: float
    unit: str
    status: ObligationStatus
    penalty_estimate_gbp: float = 0.0
    notes: str = ''

    @property
    def delivery_pct(self) -> float:
        if self.obligation_value == 0:
            return 100.0
        return round(self.delivered_value / self.obligation_value * 100, 1)

    @property
    def shortfall(self) -> float:
        return max(0.0, self.obligation_value - self.delivered_value)


@dataclass(frozen=True)
class AnnualObligationsReport:
    year: int
    report_date: dt.date
    obligations: tuple

    @property
    def met_count(self) -> int:
        return sum(1 for o in self.obligations if o.status == ObligationStatus.MET)

    @property
    def breached_count(self) -> int:
        return sum(1 for o in self.obligations if o.status == ObligationStatus.BREACHED)

    @property
    def at_risk_count(self) -> int:
        return sum(1 for o in self.obligations if o.status == ObligationStatus.AT_RISK)

    @property
    def total_penalty_estimate_gbp(self) -> float:
        return round(sum(o.penalty_estimate_gbp for o in self.obligations), 2)

    @property
    def overall_status(self) -> ObligationStatus:
        if self.breached_count > 0:
            return ObligationStatus.BREACHED
        if self.at_risk_count > 0:
            return ObligationStatus.AT_RISK
        return ObligationStatus.MET

    def get(self, name: str) -> Optional[ObligationLineItem]:
        for o in self.obligations:
            if o.name == name:
                return o
        return None

    def summary(self) -> dict:
        return {
            'year': self.year,
            'report_date': self.report_date.isoformat(),
            'total_obligations': len(self.obligations),
            'met': self.met_count,
            'at_risk': self.at_risk_count,
            'breached': self.breached_count,
            'overall_status': self.overall_status.value,
            'total_penalty_estimate_gbp': self.total_penalty_estimate_gbp,
        }


def build_obligations_report(
    year: int,
    report_date: dt.date,
    whd_obligation_customers: int,
    whd_delivered_customers: int,
    eco4_obligation_mwh: float,
    eco4_delivered_mwh: float,
    gsop_breaches: int,
    gsop_payments_gbp: float,
    ofgem_return_submitted: bool,
    ofgem_return_due_date: Optional[dt.date] = None,
    rego_obligation_mwh: float = 0.0,
    rego_held_mwh: float = 0.0,
) -> AnnualObligationsReport:
    items: List[ObligationLineItem] = []

    # WHD: must issue correct number of £150 rebates
    if whd_obligation_customers > 0:
        whd_delivery_pct = (whd_delivered_customers / whd_obligation_customers * 100
                            if whd_obligation_customers else 100.0)
        if whd_delivery_pct >= 100.0:
            whd_status = ObligationStatus.MET
        elif whd_delivery_pct >= 90.0:
            whd_status = ObligationStatus.AT_RISK
        else:
            whd_status = ObligationStatus.BREACHED
        whd_shortfall = max(0, whd_obligation_customers - whd_delivered_customers)
        whd_penalty = round(whd_shortfall * 150.0, 2)
        items.append(ObligationLineItem(
            name='WHD', obligation_value=whd_obligation_customers,
            delivered_value=whd_delivered_customers, unit='customers',
            status=whd_status, penalty_estimate_gbp=whd_penalty,
        ))

    # ECO4: energy efficiency obligation in MWh (approximate; Ofgem issues individual targets)
    if eco4_obligation_mwh > 0:
        eco_pct = eco4_delivered_mwh / eco4_obligation_mwh * 100 if eco4_obligation_mwh else 100.0
        if eco_pct >= 100.0:
            eco_status = ObligationStatus.MET
        elif eco_pct >= 85.0:
            eco_status = ObligationStatus.AT_RISK
        else:
            eco_status = ObligationStatus.BREACHED
        eco_penalty = round(max(0.0, eco4_obligation_mwh - eco4_delivered_mwh) * 10.0, 2)
        items.append(ObligationLineItem(
            name='ECO4', obligation_value=eco4_obligation_mwh,
            delivered_value=eco4_delivered_mwh, unit='MWh',
            status=eco_status, penalty_estimate_gbp=eco_penalty,
        ))

    # GSOP: payments indicate past breaches; zero breaches = MET
    gsop_status = ObligationStatus.MET if gsop_breaches == 0 else ObligationStatus.BREACHED
    items.append(ObligationLineItem(
        name='GSOP', obligation_value=0.0, delivered_value=float(gsop_breaches),
        unit='breaches', status=gsop_status, penalty_estimate_gbp=round(gsop_payments_gbp, 2),
        notes=f'£{gsop_payments_gbp:.0f} payments made',
    ))

    # Ofgem Annual Return
    if ofgem_return_submitted:
        ret_status = ObligationStatus.MET
    elif ofgem_return_due_date and report_date > ofgem_return_due_date:
        ret_status = ObligationStatus.BREACHED
    else:
        ret_status = ObligationStatus.AT_RISK
    items.append(ObligationLineItem(
        name='Ofgem_annual_return', obligation_value=1.0,
        delivered_value=1.0 if ofgem_return_submitted else 0.0,
        unit='submission', status=ret_status,
    ))

    # REGO: coverage of green tariff obligation
    if rego_obligation_mwh > 0:
        rego_pct = rego_held_mwh / rego_obligation_mwh * 100 if rego_obligation_mwh else 100.0
        if rego_pct >= 100.0:
            rego_status = ObligationStatus.MET
        elif rego_pct >= 90.0:
            rego_status = ObligationStatus.AT_RISK
        else:
            rego_status = ObligationStatus.BREACHED
        rego_shortfall_mwh = max(0.0, rego_obligation_mwh - rego_held_mwh)
        rego_penalty = round(rego_shortfall_mwh * 50.0, 2)
        items.append(ObligationLineItem(
            name='REGO', obligation_value=rego_obligation_mwh,
            delivered_value=rego_held_mwh, unit='MWh',
            status=rego_status, penalty_estimate_gbp=rego_penalty,
        ))

    return AnnualObligationsReport(
        year=year, report_date=report_date, obligations=tuple(items),
    )
