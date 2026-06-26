import datetime as dt
import pytest
from company.market.gas_interruption import (
    InterruptClass, InterruptionReason, InterruptionStatus,
    GasInterruption, InterruptibilityContract, GasInterruptionManager
)


def test_register_firm_contract():
    mgr = GasInterruptionManager()
    c = mgr.register_contract('IC001', 'MPRN001', InterruptClass.FIRM, 0, 0)
    assert c.discount_pct == 0.0


def test_interruptible_discount():
    c = InterruptibilityContract('IC002', 'MPRN002', InterruptClass.INTERRUPTIBLE, 5, 4)
    assert c.discount_pct == pytest.approx(8.0)


def test_issue_interruption():
    mgr = GasInterruptionManager()
    gi = mgr.issue_interruption(
        'INT001', 'IC001', 'MPRN001',
        InterruptionReason.SUPPLY_EMERGENCY,
        dt.date(2022, 2, 1), dt.date(2022, 2, 2), dt.date(2022, 2, 5)
    )
    assert gi.status == InterruptionStatus.NOTICE_GIVEN
    assert gi.notice_days == 1


def test_expected_duration():
    gi = GasInterruption(
        'INT002', 'C001', 'MPRN001',
        InterruptionReason.PLANNED_MAINTENANCE,
        dt.date(2022, 3, 1), dt.date(2022, 3, 15), dt.date(2022, 3, 20)
    )
    assert gi.expected_duration_days == 5


def test_restore():
    mgr = GasInterruptionManager()
    gi = mgr.issue_interruption(
        'INT003', 'IC003', 'MPRN003',
        InterruptionReason.NON_PAYMENT,
        dt.date(2022, 4, 1), dt.date(2022, 4, 2), dt.date(2022, 4, 9)
    )
    gi.restore(dt.date(2022, 4, 7))
    assert gi.status == InterruptionStatus.RESTORED
    assert gi.actual_duration_days == 5


def test_active_interruptions():
    mgr = GasInterruptionManager()
    mgr.issue_interruption('INT004', 'C004', 'M004',
                            InterruptionReason.NETWORK_CONSTRAINT,
                            dt.date(2022, 6, 1), dt.date(2022, 6, 2), dt.date(2022, 6, 4))
    mgr.issue_interruption('INT005', 'C005', 'M005',
                            InterruptionReason.HEALTH_SAFETY,
                            dt.date(2022, 6, 1), dt.date(2022, 6, 2), dt.date(2022, 6, 3))
    active = mgr.active_interruptions()
    assert len(active) == 2


def test_vulnerable_affected():
    mgr = GasInterruptionManager()
    mgr.issue_interruption('INT006', 'C_VULN', 'M006',
                            InterruptionReason.SUPPLY_EMERGENCY,
                            dt.date(2022, 1, 1), dt.date(2022, 1, 2), dt.date(2022, 1, 5),
                            is_vulnerable=True)
    assert 'C_VULN' in mgr.vulnerable_customers_affected()


def test_interruption_summary():
    mgr = GasInterruptionManager()
    gi = mgr.issue_interruption('INT007', 'C007', 'M007',
                                 InterruptionReason.SUPPLY_EMERGENCY,
                                 dt.date(2022, 8, 1), dt.date(2022, 8, 2), dt.date(2022, 8, 5))
    gi.restore(dt.date(2022, 8, 4))
    s = mgr.interruption_summary(2022)
    assert s['total'] == 1
    assert s['restored'] == 1
