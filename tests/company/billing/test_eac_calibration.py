"""Phase 87: EAC calibration from actual billing history."""

from pathlib import Path

import pytest

from company.billing.invoice import create_invoice
from company.billing.eac_calibration import calibrate_eac, calibrate_all_customers, eac_drift


def _add_invoice(db, account_id, period_start, period_end, kwh):
    bill = {
        "customer_id": account_id,
        "period_start": period_start,
        "period_end": period_end,
        "total_consumption_kwh": kwh,
        "total_amount_gbp": kwh * 0.30,
        "commodity": "electricity",
        "segment": "resi",
        "tariff_type": "fixed",
    }
    create_invoice(bill, db)


def test_calibrate_eac_no_history_returns_none(tmp_path):
    db = tmp_path / "inv.db"
    result = calibrate_eac("C1", db, lookback_years=2)
    assert result is None


def test_calibrate_eac_single_year(tmp_path):
    db = tmp_path / "inv.db"
    _add_invoice(db, "C1", "2024-01-01", "2024-12-31", 3000.0)
    result = calibrate_eac("C1", db, lookback_years=2)
    assert result is not None
    assert 2900 < result < 3200


def test_calibrate_eac_two_years_annualised(tmp_path):
    db = tmp_path / "inv.db"
    _add_invoice(db, "C1", "2023-01-01", "2023-12-31", 3600.0)
    _add_invoice(db, "C1", "2024-01-01", "2024-12-31", 3000.0)
    result = calibrate_eac("C1", db, lookback_years=2)
    assert result is not None
    assert 3000 < result < 3700


def test_calibrate_eac_lookback_filters_old_data(tmp_path):
    db = tmp_path / "inv.db"
    _add_invoice(db, "C1", "2020-01-01", "2020-12-31", 9000.0)
    _add_invoice(db, "C1", "2024-01-01", "2024-12-31", 3000.0)
    result = calibrate_eac("C1", db, lookback_years=2)
    assert result is not None
    assert result < 4000


def test_calibrate_eac_different_customers_independent(tmp_path):
    db = tmp_path / "inv.db"
    _add_invoice(db, "C1", "2024-01-01", "2024-12-31", 3000.0)
    _add_invoice(db, "C2", "2024-01-01", "2024-12-31", 6000.0)
    r1 = calibrate_eac("C1", db)
    r2 = calibrate_eac("C2", db)
    assert r2 > r1 * 1.5


def test_calibrate_all_customers(tmp_path):
    db = tmp_path / "inv.db"
    _add_invoice(db, "C1", "2024-01-01", "2024-12-31", 3000.0)
    _add_invoice(db, "C2", "2024-01-01", "2024-12-31", 5000.0)
    result = calibrate_all_customers(["C1", "C2", "C3"], db)
    assert "C1" in result
    assert "C3" in result
    assert result["C3"] is None
    assert result["C1"] is not None


def test_eac_drift_up():
    d = eac_drift(3000.0, 3500.0)
    assert d["direction"] == "up"
    assert d["drift_pct"] > 0


def test_eac_drift_down():
    d = eac_drift(3000.0, 2500.0)
    assert d["direction"] == "down"
    assert d["drift_pct"] < 0


def test_eac_drift_flat():
    d = eac_drift(3000.0, 3005.0)
    assert d["direction"] == "flat"


def test_eac_drift_returns_required_keys():
    d = eac_drift(3000.0, 3200.0)
    assert "original" in d
    assert "calibrated" in d
    assert "drift_pct" in d
    assert "direction" in d


def test_calibrate_eac_quarterly_billing(tmp_path):
    db = tmp_path / "inv.db"
    for qtr_start, qtr_end in [
        ("2024-01-01", "2024-03-31"),
        ("2024-04-01", "2024-06-30"),
        ("2024-07-01", "2024-09-30"),
        ("2024-10-01", "2024-12-31"),
    ]:
        _add_invoice(db, "C1", qtr_start, qtr_end, 750.0)
    result = calibrate_eac("C1", db)
    assert result is not None
    assert 2800 < result < 3200


def test_calibrate_eac_zero_kwh_invoices(tmp_path):
    db = tmp_path / "inv.db"
    _add_invoice(db, "C1", "2024-01-01", "2024-06-30", 0.0)
    result = calibrate_eac("C1", db)
    assert result == 0.0 or result is None


def test_eac_drift_zero_original_flat():
    d = eac_drift(0.0, 1000.0)
    assert d["direction"] == "flat"
    assert d["drift_pct"] == pytest.approx(0.0)


def test_eac_drift_calibrated_value_stored():
    d = eac_drift(3000.0, 3200.0)
    assert d["calibrated"] == pytest.approx(3200.0)


def test_eac_drift_original_value_stored():
    d = eac_drift(3000.0, 3200.0)
    assert d["original"] == pytest.approx(3000.0)


def test_eac_drift_pct_correct():
    d = eac_drift(3000.0, 4500.0)
    assert d["drift_pct"] == pytest.approx(50.0)


def test_eac_drift_flat_at_exactly_0_5pct():
    d = eac_drift(3000.0, 3015.0)
    assert d["drift_pct"] == pytest.approx(0.5)
    assert d["direction"] == "flat"


def test_eac_drift_up_just_above_0_5pct():
    # 3020-3000=20; 20/3000*100=0.667 → rounds to 0.7, direction="up"
    d = eac_drift(3000.0, 3020.0)
    assert d["drift_pct"] > 0.5
    assert d["direction"] == "up"


def test_calibrate_all_returns_all_keys(tmp_path):
    db = tmp_path / "inv.db"
    _add_invoice(db, "C1", "2024-01-01", "2024-12-31", 3000.0)
    result = calibrate_all_customers(["C1", "C2"], db)
    assert "C1" in result
    assert "C2" in result


def test_calibrate_all_empty_list_returns_empty(tmp_path):
    db = tmp_path / "inv.db"
    result = calibrate_all_customers([], db)
    assert result == {}


def test_calibrate_eac_lookback_1_year(tmp_path):
    db = tmp_path / "inv.db"
    _add_invoice(db, "C1", "2022-01-01", "2022-12-31", 9000.0)
    _add_invoice(db, "C1", "2024-01-01", "2024-12-31", 3000.0)
    result_1yr = calibrate_eac("C1", db, lookback_years=1)
    result_2yr = calibrate_eac("C1", db, lookback_years=2)
    assert result_1yr is not None
    assert result_1yr < result_2yr


def test_calibrate_eac_monthly_billing_correct(tmp_path):
    db = tmp_path / "inv.db"
    _add_invoice(db, "C1", "2024-01-01", "2024-01-31", 250.0)
    _add_invoice(db, "C1", "2024-02-01", "2024-02-29", 250.0)
    _add_invoice(db, "C1", "2024-03-01", "2024-03-31", 250.0)
    result = calibrate_eac("C1", db)
    assert result is not None
    assert result > 0
