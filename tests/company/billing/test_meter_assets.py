"""Phase 128: Meter asset management tests."""

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
