"""Tests for atom C11_segment_debt_policy -- the company applies the RIGHT
debt T&C per customer segment (world twin of W2_9_segment_debt_tnc).

L2 acceptance, two halves:
  (1) policy selection is CORRECT per segment on a set of test cases;
  (2) the invariant FIRES when a WRONG-segment T&C is applied -- proven by a
      MUTATION TEST (R15): a correct set passes, then each named defect is
      injected and the control must return False.
"""
from datetime import date

import pytest

from company.compliance.segment_debt_policy import (
    DebtTerms,
    LPCDCA_EFFECTIVE_FROM,
    Segment,
    STATUTORY_RATE_HISTORY_END,
    STATUTORY_RATE_HISTORY_START,
    canonical_segment,
    check_debt_terms_lawful_for_segment,
    is_business,
    select_debt_terms,
    statutory_interest_rate,
)
from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    DEBT_INTEREST_BUSINESS_ONLY,
    DEBT_NO_DOMESTIC_LATE_CHARGES,
    DEBT_TARIFF_ELIGIBILITY_PAYMENT_CONDITIONED,
    check_debt_terms_lawful_for_segment as inv_check,
    correct_debt_terms_for_segment,
)

_AS_OF = date(2023, 3, 1)  # H1 2023 -> statutory 11.50%
_H1_2023_RATE = 0.1150


# --- Segment canonicalisation (the several observed spellings) ---


@pytest.mark.parametrize("raw,expected", [
    ("resi", Segment.DOMESTIC),
    ("residential", Segment.DOMESTIC),
    ("domestic", Segment.DOMESTIC),
    ("Household", Segment.DOMESTIC),
    ("sme", Segment.SME),
    ("SME", Segment.SME),
    ("I&C", Segment.IANDC),
    ("iandc", Segment.IANDC),
    (" I&C ", Segment.IANDC),
])
def test_canonical_segment_maps_observed_spellings(raw, expected):
    assert canonical_segment(raw) == expected


def test_canonical_segment_fails_closed_on_unknown_or_missing():
    # A mislabel silently defaulting to domestic is the C6 SME-as-Household
    # class -- must raise, not guess.
    with pytest.raises(ValueError):
        canonical_segment("commercial-ish")
    with pytest.raises(ValueError):
        canonical_segment(None)


def test_is_business_binary():
    assert is_business(Segment.SME)
    assert is_business(Segment.IANDC)
    assert not is_business(Segment.DOMESTIC)


# --- (1) Policy selection is correct per segment ---


def test_domestic_terms_no_interest_no_charges():
    terms = select_debt_terms("resi", _AS_OF)
    assert isinstance(terms, DebtTerms)
    assert terms.segment == Segment.DOMESTIC
    assert terms.late_payment_interest_applies is False
    assert terms.late_payment_interest_annual_rate is None
    assert terms.late_payment_charges_permitted is False
    # DD-discount eligibility lawful for domestic too (fairness-constrained).
    assert terms.payment_conditioned_tariff_permitted is True


@pytest.mark.parametrize("seg", ["sme", "SME", "I&C", "iandc"])
def test_business_terms_statutory_interest_and_charges(seg):
    terms = select_debt_terms(seg, _AS_OF)
    assert is_business(terms.segment)
    assert terms.late_payment_interest_applies is True
    assert terms.late_payment_interest_annual_rate == pytest.approx(_H1_2023_RATE)
    assert terms.late_payment_charges_permitted is True
    assert terms.payment_conditioned_tariff_permitted is True


def test_select_debt_terms_is_deterministic_idempotent():
    # C-S2: same inputs -> identical value object, replay-safe.
    a = select_debt_terms("sme", _AS_OF)
    b = select_debt_terms("sme", _AS_OF)
    assert a == b


# --- Statutory interest rate history (base rate + 8pts across 2016-2025) ---


@pytest.mark.parametrize("as_of,expected", [
    (date(2016, 3, 1), 0.0850),   # base 0.50 + 8
    (date(2019, 9, 1), 0.0875),   # base 0.75 + 8
    (date(2020, 9, 1), 0.0810),   # base 0.10 + 8 (COVID cut)
    (date(2022, 9, 1), 0.0925),   # base 1.25 + 8
    (date(2023, 3, 1), 0.1150),   # base 3.50 + 8
    (date(2023, 9, 1), 0.1300),   # base 5.00 + 8
    (date(2024, 3, 1), 0.1325),   # base 5.25 + 8
    (date(2025, 9, 1), 0.1225),   # base 4.25 + 8
])
def test_statutory_interest_rate_history(as_of, expected):
    assert statutory_interest_rate(as_of) == pytest.approx(expected)


def test_statutory_interest_rate_fails_closed_outside_anchored_span():
    # Pre-2016 / post-2025 has no anchored base rate here -> None (do not
    # extrapolate). Consumers treat None as "cannot price, HELD".
    assert statutory_interest_rate(date(2015, 1, 1)) is None
    assert statutory_interest_rate(date(2030, 1, 1)) is None
    assert STATUTORY_RATE_HISTORY_START == date(2016, 1, 1)
    assert STATUTORY_RATE_HISTORY_END == date(2025, 12, 31)


def test_business_terms_outside_rate_history_known_due_but_unpriced():
    # applies=True (interest IS due for a business) but rate=None (can't price
    # it) -- the honest "known due, HELD" state, not a silent zero.
    terms = select_debt_terms("sme", date(2030, 6, 1))
    assert terms.late_payment_interest_applies is True
    assert terms.late_payment_interest_annual_rate is None


# --- Invariant registration + effective dates ---


def test_debt_invariants_registered_uk_with_dates():
    for inv in (DEBT_INTEREST_BUSINESS_ONLY, DEBT_NO_DOMESTIC_LATE_CHARGES,
                DEBT_TARIFF_ELIGIBILITY_PAYMENT_CONDITIONED):
        assert inv in ALL_INVARIANTS
        assert inv.jurisdiction == "UK"
    # LPCDCA has a real anchored commencement date; the domestic-exclusion and
    # tariff invariants honestly carry no fabricated date (None).
    assert DEBT_INTEREST_BUSINESS_ONLY.effective_from == LPCDCA_EFFECTIVE_FROM == date(1998, 11, 1)
    assert DEBT_NO_DOMESTIC_LATE_CHARGES.effective_from is None
    assert DEBT_TARIFF_ELIGIBILITY_PAYMENT_CONDITIONED.effective_from is None


def test_correct_debt_terms_reachable_via_domain_invariants():
    # The whole segment-debt library is reachable through domain_invariants
    # (matching vat_rate_for_segment's placement).
    terms = correct_debt_terms_for_segment("resi", _AS_OF)
    assert terms.late_payment_interest_applies is False


# --- (2) MUTATION TEST (R15): the control must FIRE on its named defect ---


def _correct_applied(segment: str) -> dict:
    """A lawful applied-T&C payload for a segment (the control's PASS case),
    built independently so the mutations below are single, named changes."""
    if segment in ("resi", "residential", "domestic"):
        return {"interest_applied": False, "late_charge_applied": False}
    # business: statutory interest applied at the correct rate, late charge ok
    return {"interest_applied": True, "interest_rate": _H1_2023_RATE,
            "late_charge_applied": True}


def test_control_passes_on_correct_terms_both_segments():
    # Baseline: the control does NOT fire when terms are lawful (a control that
    # always fires is as useless as one that never does).
    assert check_debt_terms_lawful_for_segment("resi", _correct_applied("resi"), _AS_OF) is True
    assert check_debt_terms_lawful_for_segment("sme", _correct_applied("sme"), _AS_OF) is True
    # And the domain_invariants delegator agrees.
    assert inv_check("resi", _correct_applied("resi"), _AS_OF) is True


def test_mutation_domestic_late_charge_fires():
    # R15 named defect A: a residential late charge. Mutate ONLY that field.
    applied = _correct_applied("resi")
    assert check_debt_terms_lawful_for_segment("resi", applied, _AS_OF) is True  # pre-mutation
    applied["late_charge_applied"] = True  # <-- the injected defect
    assert check_debt_terms_lawful_for_segment("resi", applied, _AS_OF) is False


def test_mutation_business_interest_on_domestic_fires():
    # R15 named defect B: business statutory interest on a domestic account.
    applied = _correct_applied("resi")
    applied["interest_applied"] = True  # <-- the injected defect
    assert check_debt_terms_lawful_for_segment("resi", applied, _AS_OF) is False
    # Same defect via the domain_invariants delegator.
    assert inv_check("resi", applied, _AS_OF) is False


def test_mutation_business_wrong_statutory_rate_fires():
    # R15 named defect C: a business charged interest at the WRONG rate
    # (over-charging). Independent-of-input: the expected rate comes from the
    # LPCDCA history for the date, not from the applied payload.
    applied = _correct_applied("sme")
    assert check_debt_terms_lawful_for_segment("sme", applied, _AS_OF) is True  # pre-mutation
    applied["interest_rate"] = 0.20  # <-- 20% instead of the statutory 11.50%
    assert check_debt_terms_lawful_for_segment("sme", applied, _AS_OF) is False


def test_business_may_choose_not_to_charge_interest_does_not_fire():
    # One-directional honesty: declining to charge lawful business interest is a
    # commercial choice, not unlawful -- the control must NOT fire on it.
    applied = {"interest_applied": False, "late_charge_applied": False}
    assert check_debt_terms_lawful_for_segment("sme", applied, _AS_OF) is True


# --- Fail-closed (R15 fail-open killer) ---


def test_control_fails_closed_on_malformed_or_missing_input():
    assert check_debt_terms_lawful_for_segment("resi", None, _AS_OF) is False
    assert check_debt_terms_lawful_for_segment("resi", {}, _AS_OF) is False
    assert check_debt_terms_lawful_for_segment(
        "resi", {"interest_applied": "no", "late_charge_applied": False}, _AS_OF) is False
    assert check_debt_terms_lawful_for_segment("nonsense-seg", _correct_applied("resi"), _AS_OF) is False
    # Business interest applied but no verifiable rate -> HELD, not passed.
    assert check_debt_terms_lawful_for_segment(
        "sme", {"interest_applied": True, "late_charge_applied": False}, _AS_OF) is False
    # Business interest applied on a date with no anchored statutory rate ->
    # cannot verify -> fail closed.
    assert check_debt_terms_lawful_for_segment(
        "sme", {"interest_applied": True, "interest_rate": 0.10, "late_charge_applied": False},
        date(2030, 1, 1)) is False


def test_control_independence_not_a_tautology():
    # The expected side is derived from segment+law, NOT from the applied
    # object: a payload self-consistent with the WRONG segment is still caught.
    # A domestic account whose applied terms would be lawful FOR A BUSINESS
    # (interest at the statutory rate) must still fire, because it is domestic.
    business_shaped = {"interest_applied": True, "interest_rate": _H1_2023_RATE,
                       "late_charge_applied": True}
    assert check_debt_terms_lawful_for_segment("sme", business_shaped, _AS_OF) is True
    assert check_debt_terms_lawful_for_segment("resi", business_shaped, _AS_OF) is False
