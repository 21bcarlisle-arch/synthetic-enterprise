"""Phase CY: Supplier Fitness Register tests."""
import pytest
from datetime import date
from company.regulatory.supplier_fitness_register import (
    SupplierFitnessRegister, FitnessOutcome, FitnessRole, FitnessConcernCategory
)

_D = date(2022, 1, 1)


def _reg_with_director(outcome=FitnessOutcome.FIT):
    r = SupplierFitnessRegister()
    a = r.assess("P001", "Alice Smith", FitnessRole.EXECUTIVE_DIRECTOR, _D, outcome)
    return r, a


# 1. assess creates FIT record
def test_assess_fit():
    r, a = _reg_with_director()
    assert a.outcome == FitnessOutcome.FIT
    assert a.is_fit


# 2. NOT_FIT is not fit
def test_not_fit():
    r, a = _reg_with_director(FitnessOutcome.NOT_FIT)
    assert not a.is_fit


# 3. FIT_WITH_CONDITIONS is still fit
def test_fit_with_conditions():
    r = SupplierFitnessRegister()
    a = r.assess("P001", "Bob", FitnessRole.SENIOR_MANAGER, _D, FitnessOutcome.FIT_WITH_CONDITIONS, conditions=("Declare conflicts quarterly",))
    assert a.is_fit


# 4. review_due_date = assessment + 365 days
def test_review_due():
    r, a = _reg_with_director()
    assert a.review_due_date == date(2023, 1, 1)


# 5. is_review_overdue True when past due
def test_review_overdue():
    r, a = _reg_with_director()
    assert a.is_review_overdue(date(2023, 1, 2))


# 6. is_review_overdue False before due
def test_review_not_overdue():
    r, a = _reg_with_director()
    assert not a.is_review_overdue(date(2022, 12, 31))


# 7. overdue_reviews property
def test_overdue_reviews():
    r = SupplierFitnessRegister()
    r.assess("P001", "Alice", FitnessRole.EXECUTIVE_DIRECTOR, date(2021, 1, 1), FitnessOutcome.FIT)
    r.assess("P002", "Bob", FitnessRole.SENIOR_MANAGER, date(2022, 6, 1), FitnessOutcome.FIT)
    # As of 2023-01-05: P001 is overdue (due 2022-01-01), P002 not yet
    overdue = r.overdue_reviews(date(2023, 1, 5))
    assert len(overdue) == 1
    assert overdue[0].person_id == "P001"


# 8. not_fit_persons filtered correctly
def test_not_fit_persons():
    r = SupplierFitnessRegister()
    r.assess("P001", "Alice", FitnessRole.EXECUTIVE_DIRECTOR, _D, FitnessOutcome.FIT)
    r.assess("P002", "Bob", FitnessRole.NON_EXECUTIVE_DIRECTOR, _D, FitnessOutcome.NOT_FIT)
    assert len(r.not_fit_persons()) == 1


# 9. persons_with_concerns
def test_persons_with_concerns():
    r = SupplierFitnessRegister()
    r.assess("P001", "Alice", FitnessRole.EXECUTIVE_DIRECTOR, _D, FitnessOutcome.FIT, concerns=(FitnessConcernCategory.CONFLICT_OF_INTEREST,))
    r.assess("P002", "Bob", FitnessRole.SENIOR_MANAGER, _D, FitnessOutcome.FIT)
    assert len(r.persons_with_concerns()) == 1


# 10. prior_supplier_failure_risk flagged
def test_prior_failure_risk():
    r = SupplierFitnessRegister()
    r.assess("P001", "Former Director", FitnessRole.EXECUTIVE_DIRECTOR, _D, FitnessOutcome.FIT_WITH_CONDITIONS, concerns=(FitnessConcernCategory.PRIOR_SUPPLIER_FAILURE,))
    assert len(r.prior_supplier_failure_risk()) == 1


# 11. all_fit True when everyone is fit
def test_all_fit():
    r = SupplierFitnessRegister()
    r.assess("P001", "Alice", FitnessRole.EXECUTIVE_DIRECTOR, _D, FitnessOutcome.FIT)
    r.assess("P002", "Bob", FitnessRole.SENIOR_MANAGER, _D, FitnessOutcome.FIT_WITH_CONDITIONS)
    assert r.all_fit


# 12. all_fit False when someone is not fit
def test_not_all_fit():
    r, a = _reg_with_director(FitnessOutcome.NOT_FIT)
    assert not r.all_fit


# 13. fitness_summary contains LC 30A
def test_fitness_summary():
    r, a = _reg_with_director()
    summary = r.fitness_summary(_D)
    assert "LC 30A" in summary
    assert "Ofgem" in summary


# --- Phase MJ depth tests ---

def test_person_id_stored():
    r, a = _reg_with_director()
    assert a.person_id == "P001"


def test_name_stored():
    r, a = _reg_with_director()
    assert a.name == "Alice Smith"


def test_role_stored():
    r, a = _reg_with_director()
    assert a.role == FitnessRole.EXECUTIVE_DIRECTOR


def test_assessment_date_stored():
    r, a = _reg_with_director()
    assert a.assessment_date == _D


def test_outcome_stored():
    r, a = _reg_with_director(outcome=FitnessOutcome.UNDER_REVIEW)
    assert a.outcome == FitnessOutcome.UNDER_REVIEW


def test_conditions_default_empty():
    r, a = _reg_with_director()
    assert a.conditions == ()


def test_concerns_default_empty():
    r, a = _reg_with_director()
    assert a.concerns == ()


def test_is_fit_true_for_fit_with_conditions():
    r = SupplierFitnessRegister()
    a = r.assess("P001", "Bob", FitnessRole.SENIOR_MANAGER, _D, FitnessOutcome.FIT_WITH_CONDITIONS)
    assert a.is_fit is True


def test_has_concerns_true_with_concern():
    r = SupplierFitnessRegister()
    a = r.assess("P001", "Carol", FitnessRole.EXECUTIVE_DIRECTOR, _D, FitnessOutcome.FIT,
                 concerns=(FitnessConcernCategory.CONFLICT_OF_INTEREST,))
    assert a.has_concerns is True


def test_fitness_outcome_has_4_members():
    assert len(list(FitnessOutcome)) == 4
