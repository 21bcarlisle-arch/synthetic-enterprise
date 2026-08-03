"""PRINTED_BILL_FOOTS_EXACTLY -- the R10 class extension of BILL_FOOTS to the
PRINTED representation of a bill (D_money_boundary_reconciliation, 2026-08-03).

BILL_FOOTS checks the COMPUTED bill: full-precision floats, 5p tolerance, where
footing holds trivially. Nothing checked the bill as PRINTED, and that is where
the defect lived -- 534/1603 invoices in site/state/billing_ledger.json printed
a column that did not add up to its own total.

R15: every control below is mutation-tested against its own named defect, and
the three killer patterns are attacked directly -- TAUTOLOGY (the expected sums
are written as literals a human can check, never recomputed by the code under
test), FAIL-OPEN (missing/None/zero/NaN/malformed all asserted to FAIL), and
FAIL-SILENT (an unreadable figure is a failed check, never a pass).
"""
from __future__ import annotations

import pytest

from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    PRINTED_BILL_FOOTS_EXACTLY,
    check_bill_foots,
    check_printed_bill_foots_exactly,
)
from company.billing.pre_bill_validation import validate_rendered_bill_money


def _printed_invoice(**overrides) -> dict:
    """A rendered invoice whose printed column adds up: 94.50 + 34.15 + 8.36 +
    6.85 = 143.86. Sum written out so this fixture is checkable by eye."""
    inv = {
        "customer_id": "C4",
        "period_end": "2019-01-31",
        "commodity_amount_gbp": 94.50,
        "non_commodity_amount_gbp": 34.15,
        "standing_charge_gbp": 8.36,
        "vat_gbp": 6.85,
        "total_amount_gbp": 143.86,
    }
    inv.update(overrides)
    return inv


def test_registered_in_the_library():
    assert PRINTED_BILL_FOOTS_EXACTLY in ALL_INVARIANTS
    assert PRINTED_BILL_FOOTS_EXACTLY.id == "printed_bill_foots_exactly"
    assert PRINTED_BILL_FOOTS_EXACTLY.jurisdiction == "UK"


def test_a_footing_printed_invoice_passes():
    assert check_printed_bill_foots_exactly(_printed_invoice()) is True
    assert validate_rendered_bill_money(_printed_invoice()) == []


def test_mutation_the_real_observed_defect_fires():
    """MUTATION, the atom's own named defect, taken verbatim from the live
    artefact: C4 invoice 519 printed a total of 143.88 over lines summing to
    143.86, because the components and the total were rounded independently."""
    defective = _printed_invoice(total_amount_gbp=143.88)
    assert check_printed_bill_foots_exactly(defective) is False
    reasons = validate_rendered_bill_money(defective)
    assert reasons and "do not sum exactly" in reasons[0]


def test_mutation_one_penny_out_fires():
    """The tolerance must be ZERO. The entire observed defect population was
    1-2p out; a penny-tolerant printed check would pass every instance of the
    very thing it exists to catch."""
    assert check_printed_bill_foots_exactly(_printed_invoice(total_amount_gbp=143.87)) is False
    assert check_printed_bill_foots_exactly(_printed_invoice(total_amount_gbp=143.85)) is False


def test_this_control_catches_what_bill_foots_structurally_cannot():
    """The reason this is a separate invariant and not a tightened BILL_FOOTS:
    the 2p-out printed invoice PASSES bill_foots (5p tolerance, and it is the
    right tolerance for full-precision floats). A bill can foot as computed and
    still not foot as printed -- the printed one is what the customer re-adds."""
    defective = _printed_invoice(total_amount_gbp=143.88)
    assert check_bill_foots(defective) is True            # the existing gap
    assert check_printed_bill_foots_exactly(defective) is False   # closed here


def test_mutation_line_item_altered_fires():
    """Symmetrically: the defect can be in a line rather than the total."""
    assert check_printed_bill_foots_exactly(
        _printed_invoice(commodity_amount_gbp=94.51)
    ) is False


def test_the_999999_absurdity_fires():
    """The named defect BILL_FOOTS was written for, at the print boundary."""
    assert check_printed_bill_foots_exactly(
        _printed_invoice(total_amount_gbp=999999.0)
    ) is False


def test_catchup_adjustment_counts_as_a_printed_component():
    """The omission that sank the first F6 build: a catch-up bill's adjustment
    is a genuine printed component. If it were excluded from the footing set,
    every legitimate catch-up bill would be wrongly HELD -- a control false
    positive that jams the pipeline is its own defect class."""
    catchup = _printed_invoice(
        catchup_applied=True,
        catchup_adjustment_gbp=55.00,
        total_amount_gbp=198.86,      # 143.86 + 55.00
    )
    assert check_printed_bill_foots_exactly(catchup) is True
    # ...and it is genuinely IN the sum, not merely tolerated:
    assert check_printed_bill_foots_exactly(
        _printed_invoice(catchup_applied=True, catchup_adjustment_gbp=55.00)
    ) is False   # total still 143.86, which no longer foots


def test_credit_note_foots_by_the_same_arithmetic():
    """Sign-invariant -- a catch-up overcharge correction is a legitimate
    credit note whose printed amounts are negative."""
    credit = {
        "commodity_amount_gbp": -94.50,
        "non_commodity_amount_gbp": -34.15,
        "standing_charge_gbp": -8.36,
        "vat_gbp": -6.85,
        "total_amount_gbp": -143.86,
    }
    assert check_printed_bill_foots_exactly(credit) is True
    credit["total_amount_gbp"] = -143.88
    assert check_printed_bill_foots_exactly(credit) is False


def test_a_zero_bill_foots():
    """Guarding the other false-positive edge: an all-zero bill is arithmetically
    fine and must not be held."""
    assert check_printed_bill_foots_exactly({
        "commodity_amount_gbp": 0.0,
        "non_commodity_amount_gbp": 0.0,
        "standing_charge_gbp": 0.0,
        "vat_gbp": 0.0,
        "total_amount_gbp": 0.0,
    }) is True


# --- fail-closed behaviour (R15 FAIL-OPEN / FAIL-SILENT) --------------------

def test_missing_printed_total_fails_closed():
    """Unlike check_bill_foots (where an absent total is 'nothing to disagree
    with'), a RENDERED invoice with no total is not N/A -- it is an invoice
    that cannot be paid."""
    inv = _printed_invoice()
    del inv["total_amount_gbp"]
    assert check_printed_bill_foots_exactly(inv) is False


@pytest.mark.parametrize("bad", [None, "lots", "", True, float("nan"), float("inf")])
def test_unreadable_printed_total_fails_closed(bad):
    assert check_printed_bill_foots_exactly(_printed_invoice(total_amount_gbp=bad)) is False


@pytest.mark.parametrize("bad", ["lots", True, float("nan"), float("-inf")])
def test_unreadable_printed_component_fails_closed(bad):
    assert check_printed_bill_foots_exactly(_printed_invoice(vat_gbp=bad)) is False


def test_sub_penny_precision_in_a_printed_figure_fails_closed():
    """A figure like 143.8649 cannot honestly appear on a bill. Without this
    the control would pass an unquantized column whose full-precision values
    happen to sum to a full-precision total -- footing 'exactly' on numbers no
    customer ever sees, which is the fail-open reading of this check."""
    unquantized = {
        "commodity_amount_gbp": 94.4951,
        "non_commodity_amount_gbp": 34.1531,
        "standing_charge_gbp": 8.3554,
        "vat_gbp": 6.8502,
        "total_amount_gbp": 143.8538,
    }
    assert check_printed_bill_foots_exactly(unquantized) is False
    assert check_printed_bill_foots_exactly(_printed_invoice(vat_gbp=6.8502)) is False


def test_an_absent_optional_component_is_not_treated_as_unreadable():
    """The one permissive path, kept narrow: an ordinary (non-catch-up) bill
    simply has no catchup_adjustment_gbp key, and that must not fail it."""
    inv = _printed_invoice()
    assert "catchup_adjustment_gbp" not in inv
    assert check_printed_bill_foots_exactly(inv) is True
    assert check_printed_bill_foots_exactly(
        _printed_invoice(catchup_adjustment_gbp=None)
    ) is True


def test_the_hold_reason_carries_the_diagnostic_payload():
    """R5: the reason must name the printed figures, so an operator can see the
    column that failed without re-deriving it."""
    reasons = validate_rendered_bill_money(_printed_invoice(total_amount_gbp=143.88))
    assert len(reasons) == 1
    assert reasons[0].startswith("slc_6_7_billing_accuracy")
    assert "143.88" in reasons[0]
    assert "commodity_amount_gbp=94.5" in reasons[0]
