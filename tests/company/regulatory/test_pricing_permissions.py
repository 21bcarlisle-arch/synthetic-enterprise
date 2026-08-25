"""R15 contract for the supplier's own reading of what it may price on.

WHAT IS GUARDED: that the reading stays tied to the text. A compliance module whose constants
drift away from the register they cite is worse than none -- it produces confident verdicts from
a source nobody has re-read.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from company.regulatory import pricing_permissions as pp

REPO = Path(__file__).resolve().parents[3]


def test_the_commons_artefact_this_module_reads_actually_EXISTS():
    """The citation is the whole value. A reading with no text behind it is a recollection, which
    is what the director told me to stop producing."""
    assert pp.COMMONS_ARTEFACT.is_file(), (
        f"{pp.COMMONS_ARTEFACT} is missing -- this module's verdicts cite a register that is not "
        "in the tree"
    )
    text = pp.COMMONS_ARTEFACT.read_text(encoding="utf-8")
    for citation in ("SLC 27.2A", "SLC 7.4", "SLC 27.8", "SLC 0.3", "1998"):
        assert citation in text, f"the register does not carry {citation}"


# --------------------------------------------------------------------------- #
# SLC 27.2A -- two-sided, and the second side is the one a supplier wants      #
# --------------------------------------------------------------------------- #

def test_a_payment_method_difference_that_reflects_cost_is_PERMITTED():
    assert pp.check_payment_method_difference(
        difference_gbp_per_mwh=3.0, cost_difference_gbp_per_mwh=3.0).permitted


def test_an_UNJUSTIFIED_PREMIUM_is_refused():
    verdict = pp.check_payment_method_difference(
        difference_gbp_per_mwh=12.0, cost_difference_gbp_per_mwh=3.0)

    assert not verdict.permitted and verdict.condition == "SLC 27.2A"


def test_an_OVER_GENEROUS_DISCOUNT_is_refused_by_the_SAME_condition():
    """THE HALF A SUPPLIER FORGETS. The obvious reading of 27.2A is "do not overcharge
    prepayment". A direct-debit discount larger than the cost saving is the same breach with the
    sign flipped, and it is the one a supplier is tempted into.

    MUTATION (must fire): compare the signed difference instead of its magnitude."""
    verdict = pp.check_payment_method_difference(
        difference_gbp_per_mwh=-12.0, cost_difference_gbp_per_mwh=-3.0)

    assert not verdict.permitted, "a discount nine pounds larger than the cost saving passed"


# --------------------------------------------------------------------------- #
# SLC 7.4 -- comparative, deemed-contract only, and it fails closed            #
# --------------------------------------------------------------------------- #

def test_a_class_margin_far_above_the_book_is_UNDULY_ONEROUS_on_a_deemed_contract():
    verdict = pp.check_class_margin(class_margin_gbp_per_mwh=40.0,
                                    book_general_margin_gbp_per_mwh=2.0,
                                    is_deemed_contract=True)

    assert not verdict.permitted and "SLC 7.4" == verdict.condition
    assert "20.0x" in verdict.reason


def test_the_SAME_margin_on_a_NEGOTIATED_contract_is_not_reached_by_the_condition():
    """SLC 7.4 is about Deemed Contracts. Applying it to a negotiated one would be inventing an
    obligation -- the same error as the floor it replaced, in the other direction."""
    assert pp.check_class_margin(class_margin_gbp_per_mwh=40.0,
                                 book_general_margin_gbp_per_mwh=2.0,
                                 is_deemed_contract=False).permitted


def test_a_margin_IN_LINE_with_the_book_passes_even_when_it_is_large():
    """The test is COMPARATIVE. A supplier whose whole book earns a wide margin is not caught;
    one that singles out a class is. Without this, the condition would read as a price cap."""
    assert pp.check_class_margin(class_margin_gbp_per_mwh=40.0,
                                 book_general_margin_gbp_per_mwh=30.0,
                                 is_deemed_contract=True).permitted


def test_an_UNKNOWN_comparator_is_a_FAILED_check_and_never_a_permission():
    """R15 fail-silent with a regulator on the other end: a comparative test that cannot find its
    comparator has not been satisfied."""
    verdict = pp.check_class_margin(class_margin_gbp_per_mwh=3.0,
                                    book_general_margin_gbp_per_mwh=None,
                                    is_deemed_contract=True)

    assert not verdict.permitted and "cannot be run" in verdict.reason


def test_a_ZERO_book_margin_does_not_make_every_class_margin_lawful():
    """The divide-by-nothing case, and it fails in the direction that costs the company rather
    than the customer: with no denominator the comparison is undefined, not satisfied."""
    assert not pp.check_class_margin(class_margin_gbp_per_mwh=3.0,
                                     book_general_margin_gbp_per_mwh=0.0,
                                     is_deemed_contract=True).permitted


def test_the_significance_multiple_is_NAMED_as_a_reading_and_not_as_the_law():
    """SLC 7.4 says "significantly" and defines nothing. A number invented here and quoted later
    as though Ofgem had set it is how a reading becomes a false citation."""
    source = (REPO / "company" / "regulatory" / "pricing_permissions.py").read_text()

    assert "NOT THE LAW" in source
    verdict = pp.check_class_margin(class_margin_gbp_per_mwh=40.0,
                                    book_general_margin_gbp_per_mwh=2.0, is_deemed_contract=True)
    assert "is not itself the law" in verdict.reason


# --------------------------------------------------------------------------- #
# The 1998 Act reaches business debt and stops there                           #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("debt,expected", [(500.0, 40.0), (5_000.0, 70.0), (50_000.0, 100.0)])
def test_the_statutory_recovery_sums_match_section_5A(debt, expected):
    assert pp.statutory_recovery_sum_gbp(debt, "SME") == expected


def test_a_DOMESTIC_customer_carries_no_statutory_interest_and_no_recovery_sum():
    """The Act reaches qualifying COMMERCIAL debts. Nothing read in the supply licence gives a
    supplier an equivalent domestic entitlement, so the answer is zero for a stated reason rather
    than by omission.

    MUTATION (must fire): drop the segment check and let a domestic debt earn base + 8%."""
    assert pp.statutory_recovery_sum_gbp(5_000.0, "resi") == 0.0
    assert pp.statutory_interest_rate(0.0525, "resi") == 0.0


def test_a_commercial_debt_earns_base_plus_eight_per_cent():
    assert pp.statutory_interest_rate(0.0525, "SME") == pytest.approx(0.1325)
    assert pp.STATUTORY_INTEREST_OVER_BASE == 0.08


def test_the_module_offers_NO_way_to_set_an_instalment():
    """SLC 27.8A(a)(ii): credit management must link incentives to "successful customer outcomes
    not the value of repayment rates". An optimiser is a staff incentive with no discretion, so
    the safe design is that no function here can set a repayment amount at all.

    MUTATION (must fire): add an `instalment_amount(...)` helper."""
    exported = [n for n in dir(pp) if not n.startswith("_")]
    offenders = [n for n in exported
                 if "instalment" in n.lower() and n != "INSTALMENTS_ARE_NOT_PRICED_HERE"]

    assert offenders == [], f"this module can now set a repayment amount: {offenders}"
    assert "not the value of repayment rates" in pp.INSTALMENTS_ARE_NOT_PRICED_HERE
