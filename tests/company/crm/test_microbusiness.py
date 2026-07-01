import pytest
from datetime import date
from company.crm.microbusiness import (
    MicrobusinessStatus, MicrobusinessProfile, classify_customer,
    MICROBUSINESS_ELEC_THRESHOLD_KWH, MICROBUSINESS_GAS_THRESHOLD_KWH,
)


def test_small_office_is_micro():
    p = classify_customer("C005", annual_elec_kwh=25000, staff_count=5)
    assert p.status == MicrobusinessStatus.MICRO
    assert p.is_micro is True


def test_large_industrial_is_non_micro():
    p = classify_customer("C_IC1", annual_elec_kwh=1_000_000)
    assert p.status == MicrobusinessStatus.NON_MICRO
    assert p.is_micro is False


def test_no_consumption_data_is_unclassified():
    p = classify_customer("C005")
    assert p.status == MicrobusinessStatus.UNCLASSIFIED


def test_at_elec_threshold_boundary_is_non_micro():
    p = classify_customer("C005", annual_elec_kwh=100_000)
    assert p.status == MicrobusinessStatus.NON_MICRO


def test_just_below_elec_threshold_is_micro():
    p = classify_customer("C005", annual_elec_kwh=99_999)
    assert p.is_micro is True


def test_large_staff_overrides_low_consumption():
    p = classify_customer("C005", annual_elec_kwh=20000, staff_count=15)
    assert p.status == MicrobusinessStatus.NON_MICRO


def test_large_turnover_overrides_low_consumption():
    p = classify_customer("C005", annual_elec_kwh=20000, annual_turnover_gbp=3_000_000)
    assert p.status == MicrobusinessStatus.NON_MICRO


def test_gas_threshold_classification():
    p = classify_customer("C005", annual_gas_kwh=150_000)
    assert p.is_micro is True
    p2 = classify_customer("C005", annual_gas_kwh=400_000)
    assert p2.is_micro is False


def test_eligible_protections_for_micro():
    p = classify_customer("C005", annual_elec_kwh=25000)
    protections = p.eligible_protections()
    assert "42_day_renewal_notice" in protections
    assert "complaints_to_ombudsman" in protections
    assert len(protections) == 5


def test_eligible_protections_empty_for_non_micro():
    p = classify_customer("C_IC1", annual_elec_kwh=1_000_000)
    assert p.eligible_protections() == []


def test_profile_is_frozen():
    p = classify_customer("C005", annual_elec_kwh=25000)
    with pytest.raises(Exception):
        p.customer_id = "C006"


def test_as_of_date_stored():
    p = classify_customer("C005", annual_elec_kwh=25000, as_of_date=date(2022, 4, 1))
    assert p.as_of_date == date(2022, 4, 1)


# --- Phase LS depth tests ---
from company.crm.microbusiness import (
    MICROBUSINESS_STAFF_MAX, MICROBUSINESS_TURNOVER_MAX_GBP,
)


def test_customer_id_stored():
    p = classify_customer('CUST_LS', annual_elec_kwh=20000)
    assert p.customer_id == 'CUST_LS'


def test_annual_elec_kwh_stored():
    p = classify_customer('C1', annual_elec_kwh=50000.0)
    import pytest
    assert p.annual_elec_kwh == pytest.approx(50000.0)


def test_annual_gas_kwh_stored():
    p = classify_customer('C1', annual_gas_kwh=120000.0)
    import pytest
    assert p.annual_gas_kwh == pytest.approx(120000.0)


def test_staff_count_stored():
    p = classify_customer('C1', annual_elec_kwh=20000, staff_count=7)
    assert p.staff_count == 7


def test_turnover_stored():
    p = classify_customer('C1', annual_elec_kwh=20000, annual_turnover_gbp=500000.0)
    import pytest
    assert p.annual_turnover_gbp == pytest.approx(500000.0)


def test_staff_max_constant():
    assert MICROBUSINESS_STAFF_MAX == 10


def test_turnover_threshold_constant():
    assert MICROBUSINESS_TURNOVER_MAX_GBP == 2_000_000


def test_eligible_protections_non_micro_empty():
    p = classify_customer('C1', annual_elec_kwh=1_000_000)
    assert p.eligible_protections() == []


def test_eligible_protections_micro_nonempty():
    p = classify_customer('C1', annual_elec_kwh=20000)
    prots = p.eligible_protections()
    assert len(prots) > 0


def test_as_of_date_stored():
    from datetime import date
    d = date(2024, 1, 1)
    p = classify_customer('C1', annual_elec_kwh=20000, as_of_date=d)
    assert p.as_of_date == d
