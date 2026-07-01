"""Phase 128: Meter asset management tests."""

import pytest
from company.billing.meter_assets import MeterAsset, MeterAssetRegister


def _reg():
    r = MeterAssetRegister()
    r.register(MeterAsset("MA001", "C1", "SMETS2", "2022-01-01"))
    r.register(MeterAsset("MA002", "C1", "AMR", "2018-06-01"))
    r.register(MeterAsset("MA003", "C2", "TRAD", "2010-01-01", status="operational"))
    r.register(MeterAsset("MA004", "C3", "PPM", "2023-06-01", status="faulty"))
    return r


def test_register_and_get():
    r = _reg()
    assert r.get("MA001") is not None
    assert r.get("ZZZZ") is None


def test_for_customer():
    r = _reg()
    c1_assets = r.for_customer("C1")
    assert len(c1_assets) == 2


def test_operational():
    r = _reg()
    # MA004 is faulty, rest operational
    assert len(r.operational()) == 3


def test_faulty():
    r = _reg()
    assert len(r.faulty()) == 1
    assert r.faulty()[0].asset_id == "MA004"


def test_cert_overdue_old_trad_meter():
    r = _reg()
    # TRAD installed 2010, cert due 2020 — should be overdue
    asset = r.get("MA003")
    assert asset.cert_overdue is True


def test_cert_not_overdue_new_smets2():
    r = _reg()
    asset = r.get("MA001")
    assert asset.cert_overdue is False


def test_by_type_counts():
    r = _reg()
    bt = r.by_type()
    assert bt.get("SMETS2") == 1
    assert bt.get("TRAD") == 1


def test_summary_structure():
    r = _reg()
    s = r.summary()
    for k in ("total", "operational", "faulty", "cert_overdue", "by_type", "smart_pct"):
        assert k in s


def test_smart_pct_includes_smets2():
    r = _reg()
    s = r.summary()
    assert s["smart_pct"] > 0


def test_cert_due_date_trad_10yr():
    asset = MeterAsset("X001", "C1", "TRAD", "2010-06-01")
    assert asset.cert_due_date == "2020-06-01"


def test_cert_due_date_smets2_15yr():
    asset = MeterAsset("X002", "C1", "SMETS2", "2022-01-15")
    assert asset.cert_due_date == "2037-01-15"


def test_amr_cert_period_7yr():
    asset = MeterAsset("X003", "C1", "AMR", "2010-03-01")
    assert asset.cert_due_date == "2017-03-01"
    assert asset.cert_overdue is True


def test_cert_overdue_old_trad():
    asset = MeterAsset("X004", "C1", "TRAD", "2010-01-01")
    assert asset.cert_overdue is True


def test_cert_not_overdue_smets2_installed_2022():
    asset = MeterAsset("X005", "C1", "SMETS2", "2022-01-01")
    assert asset.cert_overdue is False


def test_cert_overdue_list_excludes_faulty():
    r = MeterAssetRegister()
    r.register(MeterAsset("FA001", "C1", "TRAD", "2010-01-01", status="faulty"))
    # cert_overdue() only scans operational(); faulty meter must not appear
    assert len(r.cert_overdue()) == 0


def test_operational_excludes_replaced():
    r = MeterAssetRegister()
    r.register(MeterAsset("R001", "C1", "TRAD", "2020-01-01", status="replaced"))
    r.register(MeterAsset("O001", "C1", "SMETS2", "2022-01-01", status="operational"))
    assert len(r.operational()) == 1
    assert r.operational()[0].asset_id == "O001"


def test_smart_pct_smets1_and_smets2_only():
    r = MeterAssetRegister()
    r.register(MeterAsset("S1", "C1", "SMETS1", "2020-01-01"))
    r.register(MeterAsset("S2", "C2", "TRAD", "2018-01-01"))
    s = r.summary()
    assert s["smart_pct"] == pytest.approx(50.0)


def test_summary_empty_register():
    r = MeterAssetRegister()
    s = r.summary()
    assert s["total"] == 0
    assert s["smart_pct"] == 0.0


def test_manufacturer_field_stored():
    asset = MeterAsset("M001", "C1", "SMETS2", "2022-01-01",
                       manufacturer="Landis+Gyr", serial_number="SN12345")
    r = MeterAssetRegister()
    r.register(asset)
    retrieved = r.get("M001")
    assert retrieved.manufacturer == "Landis+Gyr"
    assert retrieved.serial_number == "SN12345"
