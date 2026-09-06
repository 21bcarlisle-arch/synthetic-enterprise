"""Tests for Priority Services Register (Phase DM)."""
import datetime as dt

import pytest

from company.regulatory.priority_services_register import (
    WINTER_MONTHS,
    DisconnectionDetermination,
    DisconnectionProtection,
    HouseholdComposition,
    NeedsCodeEvidence,
    PriorityServicesRegister,
    PSRCategory,
    PSRRecord,
    PSRService,
    disconnection_protection,
    needs_code_for,
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

    def test_the_published_rate_travels_with_its_date_and_is_reached(self):
        """`UK_PSR_RATE_PCT = 31.0  # UK benchmark` stood here with no citation and no date,
        and the only control on it asserted its own value back. 13% is Ofgem's registered
        share at a stated date; the point of the method is that the date cannot be dropped."""
        reg = PriorityServicesRegister()
        reg.register(make_record("C1"))
        out = reg.penetration_against_published(10)
        assert out["published_pct"] == pytest.approx(
            PriorityServicesRegister.UK_PSR_REGISTERED_PCT_2016
        )
        assert out["published_as_of"] == dt.date(2016, 10, 25)
        assert out["published_is_stale"] is True
        assert out["our_pct"] == pytest.approx(10.0)


class TestDisconnectionProtection:
    """The published rule (commons §2), and the only place in `company/` that decides it."""

    WINTER = dt.date(2024, 1, 15)
    SUMMER = dt.date(2024, 7, 15)

    def test_every_outcome_is_reachable(self):
        """REACHABILITY OVER THE WHOLE PARTITION, in one control. A leg per branch passes on
        a decider that answers CANNOT_DETERMINE to everything -- which is the shape a
        fail-closed rewrite drifts into, and it would read exactly like caution."""
        seen = {
            disconnection_protection(
                (PSRCategory.PENSIONABLE_AGE,), as_of=self.WINTER,
                household=HouseholdComposition.LIVES_ALONE,
            ).protection,
            disconnection_protection(
                (PSRCategory.PENSIONABLE_AGE,), as_of=self.WINTER,
                household=HouseholdComposition.UNKNOWN,
            ).protection,
            disconnection_protection(
                (PSRCategory.DISABILITY,), as_of=self.SUMMER,
                household=HouseholdComposition.OTHER_ADULTS_PRESENT,
            ).protection,
            disconnection_protection(
                (PSRCategory.LANGUAGE_SUPPORT,), as_of=self.SUMMER,
                household=HouseholdComposition.LIVES_ALONE,
            ).protection,
        }
        assert seen == set(DisconnectionProtection)

    def test_the_winter_is_october_to_march_not_november_to_march(self):
        """October is the month `consumer_vulnerability_register`'s docstring drops, in the
        direction that removes protection from customers who have it. Asserted at the
        boundary from both sides so a narrowed winter reds."""
        protected = disconnection_protection(
            (PSRCategory.PENSIONABLE_AGE,), as_of=dt.date(2024, 10, 1),
            household=HouseholdComposition.LIVES_ALONE,
        )
        assert protected.protection is DisconnectionProtection.PROHIBITED
        outside = disconnection_protection(
            (PSRCategory.PENSIONABLE_AGE,), as_of=dt.date(2024, 9, 30),
            household=HouseholdComposition.LIVES_ALONE,
        )
        assert outside.protection is DisconnectionProtection.REASONABLE_STEPS
        assert 10 in WINTER_MONTHS and 4 not in WINTER_MONTHS

    def test_the_composition_limb_is_load_bearing_in_winter(self):
        """Same category, same month, three compositions, three answers. Without this the
        household argument could be ignored entirely and every assertion above still pass."""
        by_composition = {
            h: disconnection_protection(
                (PSRCategory.PENSIONABLE_AGE,), as_of=self.WINTER, household=h
            ).protection
            for h in HouseholdComposition
        }
        assert by_composition[HouseholdComposition.LIVES_ALONE] is (
            DisconnectionProtection.PROHIBITED
        )
        assert by_composition[HouseholdComposition.ONLY_PENSIONABLE_OR_UNDER_18] is (
            DisconnectionProtection.PROHIBITED
        )
        assert by_composition[HouseholdComposition.OTHER_ADULTS_PRESENT] is (
            DisconnectionProtection.REASONABLE_STEPS
        )
        assert by_composition[HouseholdComposition.UNKNOWN] is (
            DisconnectionProtection.CANNOT_DETERMINE
        )

    def test_only_not_established_permits_disconnection(self):
        """`may_disconnect` must be False on CANNOT_DETERMINE. An unknown that reads as a
        permission is the fail-open form of this whole mechanism."""
        permits = {
            p for p in DisconnectionProtection
            if DisconnectionDetermination(p, "").may_disconnect
        }
        assert permits == {DisconnectionProtection.NOT_ESTABLISHED}

    def test_medical_equipment_alone_confers_neither_protection_nor_permission(self):
        """It matched neither published limb, and the deleted `no_disconnect_required` made it
        absolute year-round from a table with no date in it."""
        d = disconnection_protection(
            (PSRCategory.MEDICAL_EQUIPMENT,), as_of=self.SUMMER,
            household=HouseholdComposition.LIVES_ALONE,
        )
        assert d.protection is DisconnectionProtection.CANNOT_DETERMINE
        assert d.may_disconnect is False

    def test_every_refusal_names_its_reason(self):
        """A refusal that says why is how the refusal itself gets found wrong."""
        for categories, household in (
            ((PSRCategory.PENSIONABLE_AGE,), HouseholdComposition.UNKNOWN),
            ((PSRCategory.MEDICAL_EQUIPMENT,), HouseholdComposition.LIVES_ALONE),
            ((PSRCategory.LANGUAGE_SUPPORT,), HouseholdComposition.LIVES_ALONE),
        ):
            d = disconnection_protection(categories, as_of=self.WINTER, household=household)
            assert len(d.reason) > 40 and not d.reason.isupper()


class TestNeedsCodeMapping:
    def test_a_term_maps_only_where_it_is_the_same_concept(self):
        """The three answers, together. `elderly` sits in the middle cell because the
        published criterion is pensionable age and the term carries no age -- the invented 75
        is refuted, not merely unsourced -- and `fuel_poverty` is not a needs code at all."""
        assert needs_code_for("disabled").evidence is NeedsCodeEvidence.EVIDENCED
        assert needs_code_for("disabled").category is PSRCategory.DISABILITY
        assert needs_code_for("elderly").evidence is NeedsCodeEvidence.CANNOT_DETERMINE
        assert needs_code_for("fuel_poverty").evidence is NeedsCodeEvidence.NOT_A_NEEDS_CODE
        assert needs_code_for("fuel_poverty").category is None

    def test_no_operational_term_silently_acquires_a_needs_code(self):
        """A term nobody has graded returns NOT_A_NEEDS_CODE, so a thirteenth flag added to
        `crm/` confers nothing until someone reads the record -- rather than crashing, which
        would get it mapped in a hurry."""
        m = needs_code_for("a_flag_invented_next_tuesday")
        assert m.evidence is NeedsCodeEvidence.NOT_A_NEEDS_CODE
        assert "not a published PSR needs code" in m.reason

    def test_the_undetermined_cell_names_the_criterion_it_is_missing(self):
        for term in ("elderly", "child_dependent", "serious_illness", "mental_health"):
            m = needs_code_for(term)
            assert m.evidence is NeedsCodeEvidence.CANNOT_DETERMINE
            assert m.category is not None
            assert len(m.reason) > 40

    def test_psr_summary_contains_key_fields(self, reg):
        reg.register(make_record("C1"))
        s = reg.psr_summary(TODAY)
        assert "Priority Services Register" in s
        assert "Active" in s
