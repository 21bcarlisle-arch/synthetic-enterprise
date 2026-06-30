"""Phase CR: Priority Services Register tests (SLC 26B)."""
import pytest
from datetime import date, timedelta
from company.regulatory.priority_services_register import (
    PriorityServicesRegister, PSRRecord, PSRCategory, PSRService
)


def _today():
    return date.today()


def _psr_rec(account_id="C1", categories=None, services=None,
             review_overdue=False, shared=False, is_active=True):
    cats = categories if categories is not None else (PSRCategory.PENSIONABLE_AGE,)
    svcs = services if services is not None else (PSRService.PRIORITY_RECONNECTION,)
    review_due = _today() - timedelta(days=10) if review_overdue else _today() + timedelta(days=365)
    return PSRRecord(
        account_id=account_id,
        categories=cats,
        services_enrolled=svcs,
        registration_date=date(2022, 1, 1),
        review_due_date=review_due,
        shared_with_network=shared,
        is_active=is_active,
    )


# 1. Register stores record
def test_register_stores():
    reg = PriorityServicesRegister()
    r = reg.register(_psr_rec())
    assert reg.get_record("C1") == r


# 2. active_records excludes deregistered
def test_deregister_deactivates():
    reg = PriorityServicesRegister()
    reg.register(_psr_rec("C1"))
    reg.deregister("C1")
    assert len(reg.active_records) == 0


# 3. electricity_dependent identifies medical equipment
def test_electricity_dependent():
    reg = PriorityServicesRegister()
    reg.register(_psr_rec("C_med", categories=(PSRCategory.MEDICAL_EQUIPMENT,)))
    reg.register(_psr_rec("C_old", categories=(PSRCategory.PENSIONABLE_AGE,)))
    assert len(reg.electricity_dependent) == 1
    assert reg.electricity_dependent[0].account_id == "C_med"


# 4. needs_priority_reconnection for pensionable age
def test_priority_reconnection_pensionable():
    r = _psr_rec(categories=(PSRCategory.PENSIONABLE_AGE,))
    assert r.needs_priority_reconnection


# 5. needs_priority_reconnection for medical equipment
def test_priority_reconnection_medical():
    r = _psr_rec(categories=(PSRCategory.MEDICAL_EQUIPMENT,))
    assert r.needs_priority_reconnection


# 6. is_review_overdue triggers correctly
def test_review_overdue():
    r = _psr_rec(review_overdue=True)
    assert r.is_review_overdue


# 7. is_review_overdue false when not due
def test_review_not_overdue():
    r = _psr_rec(review_overdue=False)
    assert not r.is_review_overdue


# 8. is_compliant false when no services enrolled
def test_not_compliant_no_services():
    r = _psr_rec(services=())
    assert not r.is_compliant


# 9. non_compliant_records filtered correctly
def test_non_compliant_filtered():
    reg = PriorityServicesRegister()
    reg.register(_psr_rec("C1", services=(PSRService.NOMINEE_SCHEME,)))
    reg.register(_psr_rec("C2", services=()))  # non-compliant
    assert len(reg.non_compliant_records) == 1
    assert reg.non_compliant_records[0].account_id == "C2"


# 10. network_shared_count counts correctly
def test_network_shared_count():
    reg = PriorityServicesRegister()
    reg.register(_psr_rec("C1", shared=True))
    reg.register(_psr_rec("C2", shared=False))
    assert reg.network_shared_count == 1


# 11. psr_penetration_pct calculation
def test_psr_penetration():
    reg = PriorityServicesRegister()
    reg.register(_psr_rec("C1"))
    reg.register(_psr_rec("C2"))
    pct = reg.psr_penetration_pct(total_domestic_accounts=10)
    assert abs(pct - 20.0) < 0.01


# 12. psr_summary contains key fields
def test_psr_summary():
    reg = PriorityServicesRegister()
    reg.register(_psr_rec("C1", categories=(PSRCategory.MEDICAL_EQUIPMENT,)))
    summary = reg.psr_summary()
    assert "Priority Services" in summary
    assert "SLC 26B" in summary
    assert "1" in summary
