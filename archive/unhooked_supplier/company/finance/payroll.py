"""Staff headcount and payroll cost model: operational cost driver for company P&L."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Department(str, Enum):
    OPERATIONS = 'operations'
    CUSTOMER_SERVICES = 'customer_services'
    TRADING = 'trading'
    FINANCE = 'finance'
    TECHNOLOGY = 'technology'
    REGULATORY = 'regulatory'
    SALES = 'sales'
    SENIOR_MANAGEMENT = 'senior_management'


class EmploymentType(str, Enum):
    PERMANENT = 'permanent'
    CONTRACT = 'contract'
    PART_TIME = 'part_time'


@dataclass(frozen=True)
class HeadcountRole:
    role_id: str
    title: str
    department: Department
    employment_type: EmploymentType
    annual_salary_gbp: float
    headcount: int
    fte: float

    @property
    def total_annual_salary_gbp(self) -> float:
        return round(self.annual_salary_gbp * self.headcount * self.fte, 2)

    @property
    def employer_ni_gbp(self) -> float:
        ni_threshold = 9_100.0
        ni_rate = 0.138
        taxable = max(0, self.annual_salary_gbp - ni_threshold)
        return round(taxable * ni_rate * self.headcount * self.fte, 2)

    @property
    def pension_cost_gbp(self) -> float:
        return round(self.total_annual_salary_gbp * 0.05, 2)

    @property
    def total_employment_cost_gbp(self) -> float:
        return round(self.total_annual_salary_gbp + self.employer_ni_gbp + self.pension_cost_gbp, 2)


class HeadcountPlan:
    def __init__(self, year: int) -> None:
        self.year = year
        self._roles: List[HeadcountRole] = []

    def add_role(self, role_id: str, title: str, department: Department,
                  employment_type: EmploymentType, annual_salary_gbp: float,
                  headcount: int = 1, fte: float = 1.0) -> HeadcountRole:
        role = HeadcountRole(role_id=role_id, title=title, department=department,
                              employment_type=employment_type,
                              annual_salary_gbp=annual_salary_gbp,
                              headcount=headcount, fte=fte)
        self._roles.append(role)
        return role

    @property
    def total_headcount(self) -> int:
        return sum(r.headcount for r in self._roles)

    @property
    def total_fte(self) -> float:
        return round(sum(r.headcount * r.fte for r in self._roles), 2)

    @property
    def total_payroll_cost_gbp(self) -> float:
        return round(sum(r.total_employment_cost_gbp for r in self._roles), 2)

    def cost_by_department(self) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for r in self._roles:
            k = r.department.value
            result[k] = round(result.get(k, 0.0) + r.total_employment_cost_gbp, 2)
        return result

    def headcount_by_department(self) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for r in self._roles:
            k = r.department.value
            result[k] = result.get(k, 0) + r.headcount
        return result

    def cost_per_customer_gbp(self, active_customers: int) -> Optional[float]:
        if active_customers == 0:
            return None
        return round(self.total_payroll_cost_gbp / active_customers, 2)

    def summary(self) -> dict:
        return {
            'year': self.year,
            'total_headcount': self.total_headcount,
            'total_fte': self.total_fte,
            'total_payroll_cost_gbp': self.total_payroll_cost_gbp,
            'by_department': self.cost_by_department(),
        }
