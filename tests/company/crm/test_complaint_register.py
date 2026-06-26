import datetime as dt
import pytest
from company.crm.complaint_register import (
    ComplaintCategory, ComplaintStatus, Complaint, ComplaintRegister, RESOLUTION_DEADLINE_DAYS
)


def test_raise_complaint_open():
    reg = ComplaintRegister()
    c = reg.raise_complaint('CPL001', 'C001', dt.date(2022, 3, 1),
                            ComplaintCategory.BILLING, 'Overcharged on March bill')
    assert c.status == ComplaintStatus.OPEN
    assert c.days_open(dt.date(2022, 3, 10)) == 9


def test_resolution_deadline():
    reg = ComplaintRegister()
    c = reg.raise_complaint('CPL002', 'C001', dt.date(2022, 3, 1),
                            ComplaintCategory.METER_READS)
    assert c.deadline() == dt.date(2022, 3, 1) + __import__('datetime').timedelta(days=56)


def test_overdue_after_56_days():
    reg = ComplaintRegister()
    c = reg.raise_complaint('CPL003', 'C001', dt.date(2022, 1, 1),
                            ComplaintCategory.SWITCH)
    reg.get('CPL003').status = ComplaintStatus.UNDER_INVESTIGATION
    assert c.is_overdue(dt.date(2022, 3, 10))
    assert not c.is_overdue(dt.date(2022, 1, 15))


def test_resolve_upheld():
    reg = ComplaintRegister()
    c = reg.raise_complaint('CPL004', 'C001', dt.date(2022, 3, 1),
                            ComplaintCategory.BILLING)
    c.resolve(dt.date(2022, 3, 20), upheld=True, goodwill_gbp=30.0)
    assert c.status == ComplaintStatus.UPHELD
    assert c.goodwill_payment_gbp == 30.0


def test_resolve_not_upheld():
    reg = ComplaintRegister()
    c = reg.raise_complaint('CPL005', 'C002', dt.date(2022, 5, 1),
                            ComplaintCategory.CUSTOMER_SERVICE)
    c.resolve(dt.date(2022, 5, 30), upheld=False)
    assert c.status == ComplaintStatus.NOT_UPHELD
    assert c.goodwill_payment_gbp == 0.0


def test_ombudsman_eligible():
    reg = ComplaintRegister()
    c = reg.raise_complaint('CPL006', 'C001', dt.date(2022, 1, 1),
                            ComplaintCategory.TARIFF)
    assert not c.is_ombudsman_eligible(dt.date(2022, 1, 30))
    assert c.is_ombudsman_eligible(dt.date(2022, 3, 1))


def test_complaints_per_100():
    reg = ComplaintRegister()
    for i in range(5):
        reg.raise_complaint(f'CPL{i:03d}', f'C{i:03d}', dt.date(2022, 6, 1),
                            ComplaintCategory.SMART_METER)
    rate = reg.complaints_per_100_customers(100, 2022)
    assert rate == pytest.approx(5.0)


def test_upheld_rate():
    reg = ComplaintRegister()
    c1 = reg.raise_complaint('U001', 'C001', dt.date(2022, 4, 1), ComplaintCategory.BILLING)
    c2 = reg.raise_complaint('U002', 'C002', dt.date(2022, 4, 1), ComplaintCategory.BILLING)
    c1.resolve(dt.date(2022, 4, 20), upheld=True)
    c2.resolve(dt.date(2022, 4, 25), upheld=False)
    assert reg.upheld_rate_pct(2022) == pytest.approx(50.0)


def test_complaints_summary():
    reg = ComplaintRegister()
    reg.raise_complaint('S001', 'C001', dt.date(2022, 7, 1), ComplaintCategory.DEBT_COLLECTION)
    s = reg.complaints_summary(dt.date(2022, 8, 1), 200)
    assert 'open' in s
    assert 'debt_collection' in s['by_category']
