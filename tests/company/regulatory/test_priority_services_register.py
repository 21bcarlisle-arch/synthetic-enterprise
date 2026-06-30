"""Tests for Priority Services Register (Phase DM)."""
import datetime as dt
import pytest
from company.regulatory.priority_services_register import (
    PSRCategory, PSRService, PSRRecord, PriorityServicesRegister,
)


TODAY = dt.date(2024, 6, 1)


def make_record(
    account_id="C1",
    categories=(PSRCategory.MEDICAL_EQUIPMENT,),
    services=(PSRService.PRIORITY_RECONNECTION,),
    reg_date=dt.date(2023, 1, 1),
    review_date=dt.date(2025, 1, 1),
    shared_with_network=False,
    is_active=True,
):
    return PSRRecord(
        account_id=account_id,
        categories=tuple(categories),
        services_enrolled=tuple(services),
        registration_date=reg_date,
        review_due_date=review_date,
        shared_with_network=shared_with_network,
        is_active=is_active,
    )


@pytest.fixture
def reg():
    return PriorityServicesRegister()


class TestPSRRecord:
    def test_electricity_dependent_medical_equipment(self):
        rec = make_record(categories=(PSRCategory.MEDICAL_EQUIPMENT,))
        assert rec.is_electricity_dependent

    def test_not_electricity_dependent_pensionable_age(self):
        rec = make_record(categories=(PSRCategory.PENSIONABLE_AGE,))
        assert not rec.is_electricity_dependent

    def test_needs_priority_reconnection_medical(self):
        rec = make_record(categories=(PSRCategory.MEDICAL_EQUIPMENT,))
        assert rec.needs_priority_reconnection

    def test_needs_priority_reconnection_pensionable(self):
        rec = make_record(categories=(PSRCategory.PENSIONABLE_AGE,))
        assert rec.needs_priority_reconnection

    def test_no_priority_reconnection_language(self):
        rec = make_record(categories=(PSRCategory.LANGUAGE_SUPPORT,))
        assert not rec.needs_priority_reconnection

    def test_review_overdue(self):
        rec = make_record(review_date=dt.date(2023, 12, 31))
        assert rec.is_review_overdue(TODAY)

    def test_review_not_overdue(self):
        rec = make_record(review_date=dt.date(2025, 1, 1))
        assert not rec.is_review_overdue(TODAY)

    def test_review_exactly_on_date_not_overdue(self):
        rec = make_record(review_date=TODAY)
        assert not rec.is_review_overdue(TODAY)

    def test_has_at_least_one_service(self):
        rec = make_record(services=(PSRService.NOMINEE_SCHEME,))
        assert rec.has_at_least_one_service

    def test_no_services_non_compliant(self):
        rec = make_record(services=())
        assert not rec.has_at_least_one_service
        assert not rec.is_compliant

    def test_with_services_compliant(self):
        rec = make_record(services=(PSRService.ALTERNATIVE_FORMAT,))
        assert rec.is_compliant

    def test_multiple_categories(self):
        rec = make_record(categories=(PSRCategory.PENSIONABLE_AGE, PSRCategory.VISUAL_IMPAIRMENT))
        assert PSRCategory.PENSIONABLE_AGE in rec.categories
        assert PSRCategory.VISUAL_IMPAIRMENT in rec.categories


class TestPriorityServicesRegister:
    def test_register_and_get(self, reg):
        rec = make_record("C1")
        reg.register(rec)
        assert reg.get_record("C1") is rec

    def test_get_missing_returns_none(self, reg):
        assert reg.get_record("MISSING") is None

    def test_deregister_sets_inactive(self, reg):
        reg.register(make_record("C1"))
        reg.deregister("C1")
        record = reg.get_record("C1")
        assert record is not None
        assert not record.is_active

    def test_active_records_excludes_inactive(self, reg):
        reg.register(make_record("C1"))
        reg.register(make_record("C2", is_active=False))
        assert len(reg.active_records) == 1

    def test_electricity_dependent_list(self, reg):
        reg.register(make_record("C1", categories=(PSRCategory.MEDICAL_EQUIPMENT,)))
        reg.register(make_record("C2", categories=(PSRCategory.PENSIONABLE_AGE,)))
        assert len(reg.electricity_dependent) == 1

    def test_priority_reconnection_customers(self, reg):
        reg.register(make_record("C1", categories=(PSRCategory.MEDICAL_EQUIPMENT,)))
        reg.register(make_record("C2", categories=(PSRCategory.PENSIONABLE_AGE,)))
        reg.register(make_record("C3", categories=(PSRCategory.LANGUAGE_SUPPORT,)))
        assert len(reg.priority_reconnection_customers) == 2

    def test_non_compliant_records(self, reg):
        reg.register(make_record("C1", services=()))
        reg.register(make_record("C2", services=(PSRService.PASSWORD_SCHEME,)))
        assert len(reg.non_compliant_records) == 1

    def test_network_shared_count(self, reg):
        reg.register(make_record("C1", shared_with_network=True))
        reg.register(make_record("C2", shared_with_network=False))
        assert reg.network_shared_count == 1

    def test_overdue_reviews(self, reg):
        reg.register(make_record("C1", review_date=dt.date(2023, 12, 31)))
        reg.register(make_record("C2", review_date=dt.date(2025, 1, 1)))
        assert len(reg.overdue_reviews(TODAY)) == 1

    def test_psr_penetration_pct(self, reg):
        reg.register(make_record("C1"))
        reg.register(make_record("C2"))
        pct = reg.psr_penetration_pct(10)
        assert pct == pytest.approx(20.0)

    def test_psr_penetration_zero_customers(self, reg):
        assert reg.psr_penetration_pct(0) == pytest.approx(0.0)

    def test_uk_benchmark_constant(self):
        assert PriorityServicesRegister.UK_PSR_RATE_PCT == pytest.approx(31.0)

    def test_psr_summary_contains_key_fields(self, reg):
        reg.register(make_record("C1"))
        s = reg.psr_summary(TODAY)
        assert "Priority Services Register" in s
        assert "Active" in s
