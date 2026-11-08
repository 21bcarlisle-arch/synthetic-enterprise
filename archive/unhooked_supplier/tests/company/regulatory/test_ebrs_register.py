"""Tests: Phase DD — Energy Bill Relief Scheme (EBRS) Register."""
import datetime as dt
import pytest
from company.regulatory.ebrs_register import (
    EBRSRegister, EBRSRecord, EBRSFuel, EBRSEligibilityStatus, RecoveryStatus,
    is_eligible_period, _EBRS_ELECTRICITY_BASELINE_P_KWH, _EBRS_GAS_BASELINE_P_KWH,
    _EBRS_START, _EBRS_END,
)

_OCT_2022 = dt.date(2022, 10, 1)
_NOV_2022 = dt.date(2022, 11, 1)
_MAR_2023 = dt.date(2023, 3, 1)
_APR_2023 = dt.date(2023, 4, 1)   # just outside scheme
_SEP_2022 = dt.date(2022, 9, 1)   # before scheme


def _reg():
    return EBRSRegister()


def _sme_elec(reg, rate=40.0, kwh=1000.0, month=_NOV_2022):
    return reg.record_billing_month(
        customer_id="C10", fuel=EBRSFuel.ELECTRICITY,
        billing_month=month, contract_unit_rate_p_kwh=rate,
        consumption_kwh=kwh, is_domestic=False,
    )


def _resi_elec(reg, rate=40.0, kwh=1000.0, month=_NOV_2022):
    return reg.record_billing_month(
        customer_id="C1", fuel=EBRSFuel.ELECTRICITY,
        billing_month=month, contract_unit_rate_p_kwh=rate,
        consumption_kwh=kwh, is_domestic=True,
    )


# ── is_eligible_period ───────────────────────────────────────────────────────

def test_oct_2022_eligible():
    assert is_eligible_period(_OCT_2022) is True

def test_mar_2023_eligible():
    assert is_eligible_period(_MAR_2023) is True

def test_apr_2023_not_eligible():
    assert is_eligible_period(_APR_2023) is False

def test_sep_2022_not_eligible():
    assert is_eligible_period(_SEP_2022) is False

def test_exact_start_eligible():
    assert is_eligible_period(_EBRS_START) is True

def test_exact_end_eligible():
    assert is_eligible_period(_EBRS_END) is True


# ── record_billing_month ─────────────────────────────────────────────────────

def test_sme_above_baseline_eligible():
    reg = _reg()
    r = _sme_elec(reg, rate=40.0)
    assert r.eligibility == EBRSEligibilityStatus.ELIGIBLE

def test_sme_below_baseline_ineligible():
    reg = _reg()
    r = _sme_elec(reg, rate=15.0)  # below 21.1
    assert r.eligibility == EBRSEligibilityStatus.INELIGIBLE_BELOW_BASELINE

def test_sme_at_baseline_ineligible():
    reg = _reg()
    r = _sme_elec(reg, rate=_EBRS_ELECTRICITY_BASELINE_P_KWH)
    assert r.eligibility == EBRSEligibilityStatus.INELIGIBLE_BELOW_BASELINE

def test_domestic_ineligible():
    reg = _reg()
    r = _resi_elec(reg, rate=40.0)
    assert r.eligibility == EBRSEligibilityStatus.INELIGIBLE_RESIDENTIAL

def test_outside_period_ineligible():
    reg = _reg()
    r = _sme_elec(reg, rate=40.0, month=_APR_2023)
    assert r.eligibility == EBRSEligibilityStatus.INELIGIBLE_OUTSIDE_PERIOD

def test_discount_calculation():
    reg = _reg()
    # Rate = 40p, baseline = 21.1p, discount = 18.9p per kWh
    r = _sme_elec(reg, rate=40.0, kwh=1000.0)
    expected = round((40.0 - _EBRS_ELECTRICITY_BASELINE_P_KWH) * 1000.0 / 100, 2)
    assert abs(r.discount_applied_gbp - expected) < 0.01

def test_discount_zero_for_ineligible():
    reg = _reg()
    r = _resi_elec(reg, rate=40.0)
    assert r.discount_applied_gbp == 0.0

def test_gas_baseline():
    reg = _reg()
    r = reg.record_billing_month(
        customer_id="C10g", fuel=EBRSFuel.GAS,
        billing_month=_NOV_2022, contract_unit_rate_p_kwh=12.0,
        consumption_kwh=5000.0, is_domestic=False,
    )
    expected = round((12.0 - _EBRS_GAS_BASELINE_P_KWH) * 5000.0 / 100, 2)
    assert r.eligibility == EBRSEligibilityStatus.ELIGIBLE
    assert abs(r.discount_applied_gbp - expected) < 0.01

def test_default_recovery_pending():
    reg = _reg()
    r = _sme_elec(reg)
    assert r.recovery_status == RecoveryStatus.PENDING

def test_assigns_ids():
    reg = _reg()
    r1 = _sme_elec(reg)
    r2 = _sme_elec(reg)
    assert r1.record_id == "EBRS-00001"
    assert r2.record_id == "EBRS-00002"


# ── claim_recovery ───────────────────────────────────────────────────────────

def test_claim_eligible():
    reg = _reg()
    r = _sme_elec(reg)
    updated = reg.claim_recovery(r.record_id, claimed_at=dt.date(2022, 12, 1),
                                  government_ref="BEIS-2022-001")
    assert updated.recovery_status == RecoveryStatus.CLAIMED
    assert updated.claimed_at == dt.date(2022, 12, 1)
    assert updated.government_ref == "BEIS-2022-001"

def test_claim_ineligible_raises():
    reg = _reg()
    r = _resi_elec(reg)
    with pytest.raises(ValueError):
        reg.claim_recovery(r.record_id, claimed_at=dt.date(2022, 12, 1))


# ── mark_paid ────────────────────────────────────────────────────────────────

def test_mark_paid():
    reg = _reg()
    r = _sme_elec(reg)
    reg.claim_recovery(r.record_id, claimed_at=dt.date(2022, 12, 1))
    updated = reg.mark_paid(r.record_id, government_ref="GOVPAY-001")
    assert updated.recovery_status == RecoveryStatus.PAID_BY_GOVERNMENT
    assert updated.is_recovered is True
    assert updated.outstanding_recovery_gbp == 0.0

def test_outstanding_recovery():
    reg = _reg()
    r = _sme_elec(reg, rate=40.0, kwh=1000.0)
    expected = r.discount_applied_gbp
    assert abs(r.outstanding_recovery_gbp - expected) < 0.01


# ── queries ──────────────────────────────────────────────────────────────────

def test_eligible_records():
    reg = _reg()
    _sme_elec(reg, rate=40.0)    # eligible
    _resi_elec(reg, rate=40.0)   # ineligible (residential)
    _sme_elec(reg, rate=15.0)    # ineligible (below baseline)
    assert len(reg.eligible_records) == 1

def test_total_discount_applied():
    reg = _reg()
    _sme_elec(reg, rate=40.0, kwh=1000.0)
    _sme_elec(reg, rate=35.0, kwh=2000.0)
    expected = (
        round((40.0 - _EBRS_ELECTRICITY_BASELINE_P_KWH) * 1000.0 / 100, 2) +
        round((35.0 - _EBRS_ELECTRICITY_BASELINE_P_KWH) * 2000.0 / 100, 2)
    )
    assert abs(reg.total_discount_applied_gbp - expected) < 0.01

def test_outstanding_recovery_sum():
    reg = _reg()
    r1 = _sme_elec(reg, rate=40.0, kwh=1000.0)
    r2 = _sme_elec(reg, rate=35.0, kwh=500.0)
    reg.claim_recovery(r1.record_id, claimed_at=dt.date(2022, 12, 1))
    reg.mark_paid(r1.record_id, government_ref="GP-001")
    # r1 paid; r2 still outstanding
    outstanding = reg.total_outstanding_recovery_gbp
    assert abs(outstanding - r2.discount_applied_gbp) < 0.01

def test_total_recovered():
    reg = _reg()
    r = _sme_elec(reg, rate=40.0, kwh=1000.0)
    reg.claim_recovery(r.record_id, claimed_at=dt.date(2022, 12, 1))
    reg.mark_paid(r.record_id, government_ref="GP-001")
    assert abs(reg.total_recovered_gbp - r.discount_applied_gbp) < 0.01

def test_records_for_customer():
    reg = _reg()
    _sme_elec(reg)
    reg.record_billing_month("C99", EBRSFuel.GAS, _NOV_2022, 12.0, 5000.0, False)
    assert len(reg.records_for_customer("C10")) == 1
    assert len(reg.records_for_customer("C99")) == 1

def test_by_fuel():
    reg = _reg()
    _sme_elec(reg, rate=40.0, kwh=1000.0)
    reg.record_billing_month("C10g", EBRSFuel.GAS, _NOV_2022, 12.0, 5000.0, False)
    by_fuel = reg.by_fuel()
    assert "electricity" in by_fuel
    assert "gas" in by_fuel

def test_pending_claims():
    reg = _reg()
    r1 = _sme_elec(reg)
    r2 = _sme_elec(reg)
    reg.claim_recovery(r1.record_id, claimed_at=dt.date(2022, 12, 1))
    pending = reg.pending_claims()
    assert len(pending) == 1
    assert pending[0].record_id == r2.record_id

def test_ebrs_summary_format():
    reg = _reg()
    _sme_elec(reg, rate=40.0, kwh=1000.0)
    s = reg.ebrs_summary()
    assert "EBRS" in s
    assert "Oct22" in s
    assert "eligible" in s
    assert "Outstanding" in s
