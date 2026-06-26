import datetime as dt
import pytest
from company.market.metering_contracts import (
    MeteringServiceType, MeterType, ServiceCallType,
    MeteringContract, ServiceCall, MeteringContractManager
)


def _manager() -> MeteringContractManager:
    m = MeteringContractManager()
    m.register_contract('MOP-ABC', MeteringServiceType.MOP, MeterType.SMART,
                         'MPAN001', dt.date(2022, 1, 1))
    m.register_contract('DC-XYZ', MeteringServiceType.DC, MeterType.SMART,
                         'MPAN001', dt.date(2022, 1, 1))
    return m


def test_mop_annual_cost():
    m = _manager()
    contracts = m.active_contracts(dt.date(2022, 6, 1), MeteringServiceType.MOP)
    assert contracts[0].annual_cost_gbp == pytest.approx(28.0)


def test_dc_annual_cost():
    m = _manager()
    contracts = m.active_contracts(dt.date(2022, 6, 1), MeteringServiceType.DC)
    assert contracts[0].annual_cost_gbp == pytest.approx(16.0)


def test_is_active():
    c = MeteringContract('P', MeteringServiceType.MOP, MeterType.HH,
                          dt.date(2022, 1, 1), dt.date(2022, 12, 31), 'MPAN001')
    assert c.is_active(dt.date(2022, 6, 1))
    assert not c.is_active(dt.date(2023, 1, 1))


def test_cost_for_period():
    c = MeteringContract('P', MeteringServiceType.MOP, MeterType.SMART,
                          dt.date(2022, 1, 1), None, 'MPAN001')
    cost = c.cost_for_period_gbp(dt.date(2022, 1, 1), dt.date(2023, 1, 1))
    assert cost == pytest.approx(28.0, rel=0.01)


def test_service_call_logging():
    m = _manager()
    sc = m.log_service_call('MPAN001', ServiceCallType.FAULT_REPAIR,
                             dt.date(2022, 5, 1), 85.0)
    assert sc.call_id == 'SC-0001'
    assert m.service_call_cost_gbp(2022) == pytest.approx(85.0)


def test_annual_contract_cost():
    m = _manager()
    total = m.annual_contract_cost_gbp(2022)
    assert total == pytest.approx(28.0 + 16.0)


def test_active_contracts_filter():
    m = _manager()
    mop = m.active_contracts(dt.date(2022, 6, 1), MeteringServiceType.MOP)
    assert len(mop) == 1


def test_metering_summary():
    m = _manager()
    m.log_service_call('MPAN001', ServiceCallType.SMART_COMMISSIONING,
                         dt.date(2022, 2, 1), 120.0)
    s = m.metering_summary(2022)
    assert s['active_contracts'] == 2
    assert s['service_call_cost_gbp'] == pytest.approx(120.0)
