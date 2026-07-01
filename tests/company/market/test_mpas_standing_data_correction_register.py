import datetime as dt
import pytest
from company.market.mpas_standing_data_correction_register import (
    MPASStandingDataCorrectionRegister, StandingDataField, CorrectionStatus,
)

DATE = dt.date(2022, 3, 1)


def _reg():
    r = MPASStandingDataCorrectionRegister()
    r.raise_correction("MPAN-111", "ACC-001", StandingDataField.PROFILE_CLASS,
                       "3", "5", DATE)
    return r


def test_correction_id_prefix():
    reg = _reg()
    assert reg._records[0].correction_id.startswith("MPAS-COR-")


def test_status_default_raised():
    reg = _reg()
    assert reg._records[0].status == CorrectionStatus.RAISED


def test_profile_class_is_settlement_impacting():
    reg = _reg()
    assert reg._records[0].is_settlement_impacting is True


def test_llfc_is_settlement_impacting():
    reg = MPASStandingDataCorrectionRegister()
    reg.raise_correction("M", "A", StandingDataField.LLFC, "A", "B", DATE)
    assert reg._records[0].is_settlement_impacting is True


def test_da_id_not_settlement_impacting():
    reg = MPASStandingDataCorrectionRegister()
    reg.raise_correction("M", "A", StandingDataField.DA_ID, "X", "Y", DATE)
    assert reg._records[0].is_settlement_impacting is False


def test_same_values_raises():
    reg = MPASStandingDataCorrectionRegister()
    with pytest.raises(ValueError):
        reg.raise_correction("M", "A", StandingDataField.PROFILE_CLASS, "3", "3", DATE)


def test_acknowledgement_due_2wd():
    reg = _reg()
    r = reg._records[0]
    due = r.acknowledgement_due
    assert (due - DATE).days >= 2


def test_acknowledge_sets_status():
    reg = _reg()
    cid = reg._records[0].correction_id
    updated = reg.acknowledge(cid, DATE + dt.timedelta(days=2))
    assert updated.status == CorrectionStatus.ACKNOWLEDGED


def test_apply_sets_applied():
    reg = _reg()
    cid = reg._records[0].correction_id
    reg.acknowledge(cid, DATE + dt.timedelta(days=2))
    updated = reg.apply(cid, DATE + dt.timedelta(days=10))
    assert updated.status == CorrectionStatus.APPLIED


def test_reject_sets_rejected():
    reg = _reg()
    cid = reg._records[0].correction_id
    updated = reg.reject(cid, "Data was correct")
    assert updated.status == CorrectionStatus.REJECTED
    assert updated.rejected_reason == "Data was correct"
