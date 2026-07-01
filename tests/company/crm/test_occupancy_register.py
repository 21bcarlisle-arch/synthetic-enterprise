import datetime as dt
import pytest
from company.crm.occupancy_register import (
    TenancyEndReason, OccupancyPeriod, PremisesOccupancyRegister
)

D = dt.date


def test_record_move_in():
    reg = PremisesOccupancyRegister()
    p = reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    assert p.is_current
    assert p.customer_id == 'C001'


def test_duplicate_move_in_raises():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    with pytest.raises(ValueError):
        reg.record_move_in('MPAN001', 'C002', D(2020, 6, 1))


def test_record_move_out():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    p = reg.record_move_out('MPAN001', 'C001', D(2022, 3, 1), TenancyEndReason.MOVED_OUT)
    assert not p.is_current
    assert p.duration_days == (D(2022, 3, 1) - D(2020, 1, 1)).days


def test_current_occupant():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    assert reg.current_occupant('MPAN001').customer_id == 'C001'


def test_current_occupant_after_move_out_is_none():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    reg.record_move_out('MPAN001', 'C001', D(2021, 1, 1), TenancyEndReason.SWITCHED_SUPPLIER)
    assert reg.current_occupant('MPAN001') is None


def test_new_occupant_after_void():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    reg.record_move_out('MPAN001', 'C001', D(2021, 1, 1), TenancyEndReason.MOVED_OUT)
    reg.record_move_in('MPAN001', 'C002', D(2021, 3, 1))
    assert reg.current_occupant('MPAN001').customer_id == 'C002'


def test_void_mpans():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    reg.record_move_in('MPAN002', 'C002', D(2020, 1, 1))
    reg.record_move_out('MPAN001', 'C001', D(2021, 1, 1), TenancyEndReason.VOID)
    assert 'MPAN001' in reg.void_mpans()
    assert 'MPAN002' not in reg.void_mpans()


def test_occupancy_at_date():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    reg.record_move_out('MPAN001', 'C001', D(2022, 1, 1), TenancyEndReason.MOVED_OUT)
    reg.record_move_in('MPAN001', 'C002', D(2022, 3, 1))
    assert reg.occupancy_at_date('MPAN001', D(2021, 6, 1)).customer_id == 'C001'
    assert reg.occupancy_at_date('MPAN001', D(2023, 6, 1)).customer_id == 'C002'
    assert reg.occupancy_at_date('MPAN001', D(2022, 2, 1)) is None


def test_portfolio_summary():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    reg.record_move_in('MPAN002', 'C002', D(2020, 1, 1))
    reg.record_move_out('MPAN001', 'C001', D(2021, 1, 1), TenancyEndReason.MOVED_OUT)
    s = reg.portfolio_summary()
    assert s['total_mpans'] == 2
    assert s['occupied'] == 1
    assert s['void'] == 1


def test_occupancy_history_for_mpan():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    reg.record_move_out('MPAN001', 'C001', D(2021, 6, 1), TenancyEndReason.MOVED_OUT)
    reg.record_move_in('MPAN001', 'C002', D(2021, 7, 1))
    history = reg.occupancy_history_for_mpan('MPAN001')
    assert len(history) == 2
    assert all(h.mpan == 'MPAN001' for h in history)


def test_occupancy_history_for_customer():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    reg.record_move_out('MPAN001', 'C001', D(2021, 1, 1), TenancyEndReason.MOVED_OUT)
    reg.record_move_in('MPAN002', 'C001', D(2021, 3, 1))
    history = reg.occupancy_history_for_customer('C001')
    assert len(history) == 2
    assert all(h.customer_id == 'C001' for h in history)


def test_duration_days_none_when_current():
    reg = PremisesOccupancyRegister()
    p = reg.record_move_in('MPAN001', 'C001', D(2022, 1, 1))
    assert p.duration_days is None


def test_end_reason_stored():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    p = reg.record_move_out('MPAN001', 'C001', D(2022, 1, 1), TenancyEndReason.MOVED_OUT)
    assert p.end_reason == TenancyEndReason.MOVED_OUT


def test_move_out_not_found_raises():
    reg = PremisesOccupancyRegister()
    with pytest.raises(ValueError):
        reg.record_move_out('MPAN999', 'C001', D(2022, 1, 1), TenancyEndReason.MOVED_OUT)


def test_void_mpans_empty_when_all_occupied():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    assert reg.void_mpans() == []


def test_portfolio_summary_total_records():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    reg.record_move_out('MPAN001', 'C001', D(2021, 1, 1), TenancyEndReason.MOVED_OUT)
    reg.record_move_in('MPAN001', 'C002', D(2021, 3, 1))
    s = reg.portfolio_summary()
    assert s['total_occupancy_records'] == 2


def test_occupancy_at_date_before_move_in_is_none():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2020, 6, 1))
    assert reg.occupancy_at_date('MPAN001', D(2020, 1, 1)) is None


def test_occupancy_history_for_mpan_multiple_periods():
    reg = PremisesOccupancyRegister()
    reg.record_move_in('MPAN001', 'C001', D(2019, 1, 1))
    reg.record_move_out('MPAN001', 'C001', D(2020, 1, 1), TenancyEndReason.DECEASED)
    reg.record_move_in('MPAN001', 'C002', D(2020, 3, 1))
    reg.record_move_out('MPAN001', 'C002', D(2021, 3, 1), TenancyEndReason.SWITCHED_SUPPLIER)
    reg.record_move_in('MPAN001', 'C003', D(2021, 5, 1))
    assert len(reg.occupancy_history_for_mpan('MPAN001')) == 3


def test_void_mpans_unregistered_mpan_not_listed():
    reg = PremisesOccupancyRegister()
    # 'MPAN002' was never recorded — must not appear in void_mpans
    reg.record_move_in('MPAN001', 'C001', D(2020, 1, 1))
    void = reg.void_mpans()
    assert 'MPAN002' not in void
