import pytest
from company.finance.payroll import (
    Department, EmploymentType, HeadcountRole, HeadcountPlan
)


def test_role_total_salary():
    r = HeadcountRole('CSR01', 'CS Agent', Department.CUSTOMER_SERVICES,
                       EmploymentType.PERMANENT, 28000.0, headcount=5, fte=1.0)
    assert r.total_annual_salary_gbp == pytest.approx(140_000.0)


def test_part_time_fte():
    r = HeadcountRole('PT01', 'Admin', Department.OPERATIONS,
                       EmploymentType.PART_TIME, 24000.0, headcount=2, fte=0.5)
    assert r.total_annual_salary_gbp == pytest.approx(24_000.0)


def test_employer_ni():
    r = HeadcountRole('T01', 'Trader', Department.TRADING,
                       EmploymentType.PERMANENT, 80_000.0, headcount=1, fte=1.0)
    expected_ni = (80_000 - 9_100) * 0.138
    assert r.employer_ni_gbp == pytest.approx(expected_ni)


def test_total_employment_cost_includes_pension():
    r = HeadcountRole('F01', 'CFO', Department.FINANCE,
                       EmploymentType.PERMANENT, 120_000.0, headcount=1, fte=1.0)
    pension = 120_000 * 0.05
    ni = (120_000 - 9_100) * 0.138
    assert r.total_employment_cost_gbp == pytest.approx(120_000 + ni + pension)


def test_headcount_plan_totals():
    plan = HeadcountPlan(2022)
    plan.add_role('CSR', 'CS Agent', Department.CUSTOMER_SERVICES,
                   EmploymentType.PERMANENT, 28_000.0, headcount=10)
    plan.add_role('TRD', 'Trader', Department.TRADING,
                   EmploymentType.PERMANENT, 80_000.0, headcount=2)
    assert plan.total_headcount == 12
    assert plan.total_fte == pytest.approx(12.0)


def test_cost_by_department():
    plan = HeadcountPlan(2022)
    plan.add_role('CSR', 'CS Agent', Department.CUSTOMER_SERVICES,
                   EmploymentType.PERMANENT, 28_000.0, headcount=5)
    plan.add_role('FIN', 'Accountant', Department.FINANCE,
                   EmploymentType.PERMANENT, 45_000.0, headcount=2)
    by_dept = plan.cost_by_department()
    assert 'customer_services' in by_dept
    assert 'finance' in by_dept
    assert by_dept['customer_services'] > 0


def test_cost_per_customer():
    plan = HeadcountPlan(2022)
    plan.add_role('CSR', 'CS Agent', Department.CUSTOMER_SERVICES,
                   EmploymentType.PERMANENT, 28_000.0, headcount=10)
    cpc = plan.cost_per_customer_gbp(1000)
    assert cpc is not None
    assert cpc > 0


def test_summary_keys():
    plan = HeadcountPlan(2023)
    plan.add_role('CEO', 'CEO', Department.SENIOR_MANAGEMENT,
                   EmploymentType.PERMANENT, 200_000.0, headcount=1)
    s = plan.summary()
    assert s['year'] == 2023
    assert s['total_headcount'] == 1
    assert 'by_department' in s
