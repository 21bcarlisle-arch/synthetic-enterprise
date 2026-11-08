import pytest
from company.crm.supply_point_register import (
    SupplyPointRegister, SupplyPointRecord, ProfileClass, FuelType
)


def _elec(mpan="1012345678900", aid="C1", pc=ProfileClass.PC1,
          start="2022-01-01", aq=3500.0):
    return SupplyPointRecord(
        identifier=mpan, account_id=aid, fuel=FuelType.ELECTRICITY,
        profile_class=pc, supplier_start_date=start, annual_quantity_kwh=aq,
    )


def _gas(mprn="1234567890", aid="C1", start="2022-01-01", aq=12_000.0):
    return SupplyPointRecord(
        identifier=mprn, account_id=aid, fuel=FuelType.GAS,
        profile_class=None, supplier_start_date=start, annual_quantity_kwh=aq,
    )


def test_is_active_no_end_date():
    r = _elec()
    assert r.is_active is True


def test_is_active_with_end_date():
    r = SupplyPointRecord(
        identifier="1234", account_id="C1", fuel=FuelType.ELECTRICITY,
        profile_class=ProfileClass.PC1, supplier_start_date="2022-01-01",
        supplier_end_date="2022-12-31",
    )
    assert r.is_active is False


def test_is_hh_pc8():
    r = _elec(pc=ProfileClass.PC8)
    assert r.is_hh is True


def test_is_hh_pc1():
    r = _elec(pc=ProfileClass.PC1)
    assert r.is_hh is False


def test_is_domestic_pc1():
    r = _elec(pc=ProfileClass.PC1)
    assert r.is_domestic is True


def test_register_and_get():
    reg = SupplyPointRegister()
    reg.register(_elec())
    assert reg.get("1012345678900") is not None


def test_deregister():
    reg = SupplyPointRegister()
    reg.register(_elec())
    reg.deregister("1012345678900", "2022-12-31")
    assert reg.get("1012345678900").is_active is False
    assert len(reg.active_points()) == 0


def test_active_points_by_fuel():
    reg = SupplyPointRegister()
    reg.register(_elec())
    reg.register(_gas())
    assert len(reg.active_points(FuelType.ELECTRICITY)) == 1
    assert len(reg.active_points(FuelType.GAS)) == 1


def test_hh_points():
    reg = SupplyPointRegister()
    reg.register(_elec(mpan="AAA", pc=ProfileClass.PC8))
    reg.register(_elec(mpan="BBB", pc=ProfileClass.PC1))
    assert len(reg.hh_points()) == 1


def test_total_aq():
    reg = SupplyPointRegister()
    reg.register(_elec(aq=3500.0))
    reg.register(_elec(mpan="X", aid="C2", aq=4000.0))
    assert abs(reg.total_aq_kwh(FuelType.ELECTRICITY) - 7500.0) < 0.01


def test_register_summary_keys():
    reg = SupplyPointRegister()
    reg.register(_elec())
    s = reg.register_summary()
    for k in ("total_registered", "active_electricity", "active_gas", "hh_points",
               "total_aq_electricity_kwh"):
        assert k in s


# --- Phase LJ depth tests ---

def test_identifier_stored():
    r = _elec(mpan="1012345678901")
    assert r.identifier == "1012345678901"


def test_account_id_stored():
    r = _elec(aid="ACCT_LJ")
    assert r.account_id == "ACCT_LJ"


def test_fuel_electricity():
    r = _elec()
    assert r.fuel == FuelType.ELECTRICITY


def test_profile_class_stored():
    r = _elec(pc=ProfileClass.PC3)
    assert r.profile_class == ProfileClass.PC3


def test_supplier_start_date_stored():
    r = _elec(start="2023-04-01")
    assert r.supplier_start_date == "2023-04-01"


def test_annual_quantity_stored():
    r = _elec(aq=5000.0)
    assert r.annual_quantity_kwh == pytest.approx(5000.0)


def test_gas_profile_class_none():
    r = _gas()
    assert r.profile_class is None


def test_points_for_account():
    reg = SupplyPointRegister()
    reg.register(_elec(mpan="A", aid="ACCT1"))
    reg.register(_elec(mpan="B", aid="ACCT1"))
    reg.register(_elec(mpan="C", aid="ACCT2"))
    pts = reg.points_for_account("ACCT1")
    assert len(pts) == 2


def test_profile_class_breakdown():
    reg = SupplyPointRegister()
    reg.register(_elec(mpan="A", pc=ProfileClass.PC1))
    reg.register(_elec(mpan="B", pc=ProfileClass.PC1))
    reg.register(_elec(mpan="C", pc=ProfileClass.PC3))
    bd = reg.profile_class_breakdown()
    assert bd.get("1") == 2
    assert bd.get("3") == 1


def test_register_returns_record():
    reg = SupplyPointRegister()
    r = _elec()
    result = reg.register(r)
    assert result is r
