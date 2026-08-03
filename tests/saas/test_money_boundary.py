"""D_money_boundary_reconciliation -- the declared money boundary (saas/money.py).

Covers the [ACT] returned by docs/design/MONEY_REPRESENTATION_EVIDENCE.md:
printed line items must sum to the printed total.

R15 discipline throughout: every control here is MUTATION-tested -- the named
defect is injected and the control MUST fire. The three killer patterns are
each attacked explicitly:
  * TAUTOLOGY  -- the footing assertions recompute the sum from the PRINTED
                  values with an independent Decimal, never by re-calling the
                  function under test.
  * FAIL-OPEN  -- missing/None/zero/NaN/Inf/string inputs are asserted to
                  RAISE, not to quietly quantize to 0.00.
  * FAIL-SILENT-- a residual too large to be rounding raises rather than
                  returning the unreconciled figure.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from saas.money import (
    MAX_PENNY_ROUNDING_GBP,
    MoneyBoundaryError,
    foot_components_to_total,
    quantize_gbp,
)


def _independent_sum(printed: dict) -> Decimal:
    """Re-add the printed column the way a customer would -- exact decimal
    arithmetic on the printed figures, computed WITHOUT touching saas.money.
    An assertion that used foot_components_to_total's own sum would be the
    tautology R15 names."""
    return sum((Decimal(str(v)) for v in printed.values()), Decimal("0"))


# --- quantize_gbp -----------------------------------------------------------

def test_quantize_rounds_half_up_not_bankers():
    """The named defect this convention exists to prevent: Python's builtin
    round() does banker's rounding on the binary float, so round(2.675, 2) is
    2.67 and a customer doing the arithmetic by hand gets 2.68 and concludes
    the bill is wrong."""
    assert round(2.675, 2) == 2.67          # the defect, pinned
    assert quantize_gbp(2.675) == 2.68      # the fix
    assert quantize_gbp(0.125) == 0.13
    assert quantize_gbp(-2.675) == -2.68    # half AWAY from zero, both signs


def test_quantize_is_penny_exact_and_idempotent():
    assert quantize_gbp(143.8649) == 143.86
    assert quantize_gbp(143.86) == 143.86
    assert quantize_gbp(quantize_gbp(143.8649)) == 143.86


@pytest.mark.parametrize("bad", [None, "", "lots", object(), True, False])
def test_quantize_fails_closed_on_unreadable(bad):
    """FAIL-OPEN mutation: an unreadable money value must RAISE, never coerce
    to 0.00. A silent 0.00 would print a free bill."""
    with pytest.raises(MoneyBoundaryError):
        quantize_gbp(bad)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_quantize_fails_closed_on_non_finite(bad):
    with pytest.raises(MoneyBoundaryError):
        quantize_gbp(bad)


def test_quantize_error_names_the_field():
    """R5: the alert carries the diagnostic payload -- a failure must be
    diagnosable from the message alone."""
    with pytest.raises(MoneyBoundaryError, match="bill.vat_gbp"):
        quantize_gbp(None, field="bill.vat_gbp")


# --- foot_components_to_total ----------------------------------------------

def test_printed_parts_sum_to_printed_total_on_the_real_defect_case():
    """The exact invoice from site/state/billing_ledger.json that motivated
    this atom: C4 invoice 519, period 2019-01-31. Its printed lines summed to
    143.86 against a printed total of 143.88."""
    raw = {
        "commodity_amount_gbp": 94.4951,
        "non_commodity_amount_gbp": 34.1531,
        "standing_charge_gbp": 8.3554,
        "vat_gbp": 6.8502,
    }
    declared_total = sum(raw.values())          # 143.8538 -- rounds to 143.85
    printed, total = foot_components_to_total(raw, declared_total)

    assert printed == {
        "commodity_amount_gbp": 94.50,
        "non_commodity_amount_gbp": 34.15,
        "standing_charge_gbp": 8.36,
        "vat_gbp": 6.85,
    }
    # The invariant, checked independently: the column adds up as printed.
    assert _independent_sum(printed) == Decimal(str(total)) == Decimal("143.86")
    # And note it is NOT the independently-rounded raw total (143.85) -- the
    # total is DERIVED from the printed lines, which is the whole point.
    assert total != round(declared_total, 2)


def test_no_line_item_is_fudged_to_absorb_the_residual():
    """Each printed line must be exactly the quantization of its OWN raw value.
    A cheaper 'fix' would adjust VAT (or the largest line) to make the column
    add up; that prints a figure the customer cannot derive from their tariff."""
    raw = {
        "commodity_amount_gbp": 10.004,
        "non_commodity_amount_gbp": 20.004,
        "standing_charge_gbp": 30.004,
        "vat_gbp": 3.004,
    }
    printed, total = foot_components_to_total(raw, sum(raw.values()))
    for key, value in raw.items():
        assert printed[key] == quantize_gbp(value)
    assert _independent_sum(printed) == Decimal(str(total))


def test_catchup_adjustment_is_a_footing_component():
    """The omission that sank the first F6 build: the catch-up adjustment is a
    genuine fifth printed component, added to the total outside the four
    category fields. Dropping it from the printed set would derive a total
    that is wrong by the whole adjustment, not by a penny."""
    raw = {
        "commodity_amount_gbp": 100.0,
        "non_commodity_amount_gbp": 40.0,
        "standing_charge_gbp": 8.0,
        "vat_gbp": 7.4,
        "catchup_adjustment_gbp": 55.0,
    }
    printed, total = foot_components_to_total(raw, 210.4)
    assert total == 210.40
    assert _independent_sum(printed) == Decimal("210.40")


def test_credit_note_foots_by_the_same_arithmetic():
    """Sign-invariance: a catch-up OVERCHARGE correction is a genuine credit
    note whose amounts are legitimately negative."""
    raw = {
        "commodity_amount_gbp": -94.4951,
        "non_commodity_amount_gbp": -34.1531,
        "standing_charge_gbp": -8.3554,
        "vat_gbp": -6.8502,
    }
    printed, total = foot_components_to_total(raw, sum(raw.values()))
    assert total == -143.86
    assert _independent_sum(printed) == Decimal(str(total))


def test_missing_component_raises_rather_than_printing_an_unreconcilable_total():
    """MUTATION, the control's own named defect: a component present in the
    declared total but absent from the printed set. This is the F6 class, and
    a 999,999-on-88 absurdity is its extreme. It must RAISE -- returning the
    printed sum silently would drop real money off the invoice, and returning
    the declared total would print a column that doesn't add up."""
    raw = {
        "commodity_amount_gbp": 50.0,
        "non_commodity_amount_gbp": 20.0,
        "standing_charge_gbp": 8.0,
        "vat_gbp": 3.9,
    }
    with pytest.raises(MoneyBoundaryError, match="missing from the printed set"):
        foot_components_to_total(raw, 81.9 + 55.0)  # an unprinted catch-up line


def test_residual_bound_admits_worst_case_rounding_and_nothing_more():
    """The bound must not be a false-positive machine -- a HELD legitimate bill
    is its own defect class. Worst-case honest rounding with n components is
    n x half-a-penny on the components plus half a penny on the total; the
    control must accept exactly that and reject beyond it."""
    raw = {f"line_{i}_gbp": 10.005 for i in range(4)}   # every line rounds UP
    declared = sum(raw.values())                        # 40.02 raw
    printed, total = foot_components_to_total(raw, declared)
    # Four half-penny round-ups: the printed total is legitimately 2p above the
    # raw total, and the control accepts it rather than holding the bill.
    assert total == 40.04
    assert abs(total - round(declared, 2)) == pytest.approx(0.02)

    # Both figures being penny-quantized, the residual is always a whole number
    # of pence, so with n=4 the bound (5 x 0.005 = 0.025) means "at most 2p".
    assert 4 * MAX_PENNY_ROUNDING_GBP == pytest.approx(0.02)
    foot_components_to_total(raw, declared)             # 2p: must NOT raise

    # The rejecting edge, measured from a set that needs no rounding at all so
    # the perturbation IS the residual: 2p accepted, 3p rejected.
    exact = {f"line_{i}_gbp": 10.00 for i in range(4)}   # prints 40.00 exactly
    foot_components_to_total(exact, 40.02)              # 2p: must NOT raise
    with pytest.raises(MoneyBoundaryError):
        foot_components_to_total(exact, 40.03)          # 3p is not rounding
    with pytest.raises(MoneyBoundaryError):
        foot_components_to_total(exact, 39.97)          # and symmetrically down


def test_empty_component_set_with_a_real_total_raises():
    """FAIL-OPEN mutation: a total resting on no printed line at all. Returning
    0.00 here would be the fail-open reading of an empty input."""
    with pytest.raises(MoneyBoundaryError):
        foot_components_to_total({}, 88.0)


@pytest.mark.parametrize("bad", [None, "free", float("nan"), float("inf")])
def test_unreadable_component_fails_closed(bad):
    raw = {
        "commodity_amount_gbp": 50.0,
        "non_commodity_amount_gbp": 20.0,
        "standing_charge_gbp": 8.0,
        "vat_gbp": bad,
    }
    with pytest.raises(MoneyBoundaryError):
        foot_components_to_total(raw, 81.9)


@pytest.mark.parametrize("bad", [None, "free", float("nan")])
def test_unreadable_declared_total_fails_closed(bad):
    """An unverifiable cross-check is a FAILED cross-check (R15 fail-silent):
    the function must not skip the residual guard just because the figure it
    would check against is unreadable."""
    raw = {"commodity_amount_gbp": 50.0, "vat_gbp": 2.5}
    with pytest.raises(MoneyBoundaryError):
        foot_components_to_total(raw, bad)


def test_binary_float_noise_never_leaks_into_the_printed_total():
    """0.1 + 0.2 == 0.30000000000000004. Summing penny-exact floats in binary
    can land a fraction off, which would then not compare equal to the total a
    consumer recomputes -- the sum is done in Decimal for exactly this."""
    raw = {"a_gbp": 0.1, "b_gbp": 0.2}
    printed, total = foot_components_to_total(raw, 0.3)
    assert total == 0.30
    assert Decimal(str(total)) == Decimal("0.30")
