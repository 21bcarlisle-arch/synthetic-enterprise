"""PRINTED_LINE_REDERIVES -- the R10 class extension of PRINTED_BILL_FOOTS_EXACTLY
from "the column adds up" to "each line can be re-derived".

The customer test one level down: a bill printing `317.9 kWh x 11.90p = GBP
37.82` foots perfectly and is still wrong on its face, because the product is
37.83. Measured before the fix on the RENDERED artefact: 86.1% of usage lines
and 243 standing-charge lines showed a multiplication that did not hold.

R15 obligations discharged here and in `test_printed_figure_rederivation_mutations`:
every control below is paired with a real source mutation that makes it fire.
Three named patterns:

* TAUTOLOGY -- `check_printed_line_rederives` must NOT ask `saas.money` (which
  PRINTS these figures) whether its own output reconciles. It re-implements the
  multiplication. `test_the_checker_does_not_consult_the_printer` pins that.
* FAIL-OPEN -- a line that shows a rate but is missing its quantity or amount,
  or carries an unreadable figure, must FAIL, not pass for want of evidence.
* NaN-BLINDNESS -- every comparison here is NaN-blind, so non-finite figures are
  tested FIRST and explicitly; a corrupt figure must never read as a tidy pass.
"""
import ast
import json
import math
from pathlib import Path

import pytest

from company.compliance import domain_invariants as di
from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    PRINTED_LINE_REDERIVES,
    check_printed_line_rederives,
)
from saas.money import (
    MoneyBoundaryError,
    RATE_DISPLAY_MAX_DP,
    RATE_DISPLAY_MIN_DP,
    display_rate_gbp_per_day,
    display_rate_p_per_kwh,
    minimal_display_rate,
)

PROJECT = Path(__file__).resolve().parents[3]
LEDGER = PROJECT / "site" / "state" / "billing_ledger.json"


def _line(**over):
    """A rendered usage line that re-derives, as the fix produces it.

    317.9 kWh at 11.897 p/kWh is 37.8206..., which prints as 37.82 -- the
    genuine figures from C1's first invoice, and the exact line the old
    2dp-rounded rate (11.90) got wrong.
    """
    base = dict(
        consumption_kwh=317.9,
        unit_rate_p_per_kwh=11.897,
        commodity_amount_gbp=37.82,
        days_in_period=31,
        standing_charge_gbp_per_day=0.24,
        standing_charge_gbp=7.44,
    )
    base.update(over)
    return base


# --------------------------------------------------------------------------
# Registration
# --------------------------------------------------------------------------
def test_the_invariant_is_registered():
    assert PRINTED_LINE_REDERIVES in ALL_INVARIANTS
    assert PRINTED_LINE_REDERIVES.id == "printed_line_rederives"


# --------------------------------------------------------------------------
# The named defect, both ways
# --------------------------------------------------------------------------
def test_the_named_defect_FIRES():
    """`317.9 kWh x 11.90p = GBP 37.82` -- the product is 37.83, so the
    arithmetic on the face of the bill does not hold."""
    assert check_printed_line_rederives(_line(unit_rate_p_per_kwh=11.90)) is False


def test_a_legitimately_rederivable_line_PASSES():
    assert check_printed_line_rederives(_line()) is True


def test_the_standing_charge_named_defect_FIRES():
    """`31 days x GBP 0.36/day` = 11.16, printed against 11.15."""
    assert check_printed_line_rederives(
        _line(standing_charge_gbp_per_day=0.36, standing_charge_gbp=11.15)
    ) is False


def test_the_industrial_line_that_no_2dp_rate_can_express_PASSES_when_printed_honestly():
    """157,128.8 kWh for GBP 17,215.01 needs 6dp; at 2dp the line is out by
    GBP 7.86. Printed at the precision that reproduces it, it passes."""
    rate, dp = display_rate_p_per_kwh(157128.8, 17215.01)
    assert dp == 6
    assert check_printed_line_rederives(
        dict(consumption_kwh=157128.8, unit_rate_p_per_kwh=rate,
             commodity_amount_gbp=17215.01)
    ) is True


# --------------------------------------------------------------------------
# Honest absence vs. fail-open
# --------------------------------------------------------------------------
def test_a_line_printing_NO_rate_passes():
    """An amount no single unit rate generated is honestly shown without one.
    Nothing is claimed, so nothing can be unreproducible."""
    line = _line()
    line["unit_rate_p_per_kwh"] = None
    assert check_printed_line_rederives(line) is True


@pytest.mark.parametrize("missing", ["consumption_kwh", "commodity_amount_gbp"])
def test_a_rate_with_nothing_to_multiply_FAILS_CLOSED(missing):
    """FAIL-OPEN guard: a printed rate whose quantity or amount is absent is
    the defect itself, not an absence of evidence."""
    line = _line()
    del line[missing]
    assert check_printed_line_rederives(line) is False


@pytest.mark.parametrize("field", [
    "consumption_kwh", "unit_rate_p_per_kwh", "commodity_amount_gbp",
])
@pytest.mark.parametrize("bad", [float("nan"), float("inf"), "not-a-number", True])
def test_non_finite_and_unreadable_figures_FAIL_CLOSED(field, bad):
    """NaN-BLINDNESS guard: every comparison in the checker is NaN-blind, so a
    corrupt figure must be rejected before it reaches one."""
    assert check_printed_line_rederives(_line(**{field: bad})) is False


def test_float_residue_on_a_printed_rate_FAILS_CLOSED():
    """The observed defect: 0.23983870967741938 GBP/day reached a
    customer-facing artefact. That is not a printed rate, it is an unquantized
    float -- and it fails even though it multiplies out correctly."""
    line = _line(standing_charge_gbp_per_day=0.23983870967741938,
                 standing_charge_gbp=7.44, days_in_period=31)
    assert check_printed_line_rederives(line) is False


# --------------------------------------------------------------------------
# Per-register rows -- what the portal actually renders
# --------------------------------------------------------------------------
def test_a_register_row_that_does_not_rederive_FIRES():
    """The portal renders one row PER REGISTER, so a register row is a printed
    line in its own right. Checking only the invoice summary would leave the
    rows the customer actually reads unchecked."""
    line = _line()
    line["registers"] = [dict(register_id="1", label="Anytime",
                              consumption_kwh=317.9, amount_gbp=37.82,
                              unit_rate_p_per_kwh=11.90)]
    assert check_printed_line_rederives(line) is False


def test_a_register_row_that_rederives_PASSES():
    line = _line()
    line["registers"] = [dict(register_id="1", label="Anytime",
                              consumption_kwh=317.9, amount_gbp=37.82,
                              unit_rate_p_per_kwh=11.897)]
    assert check_printed_line_rederives(line) is True


def test_an_unreadable_register_row_FAILS_CLOSED():
    line = _line()
    line["registers"] = ["not-a-row"]
    assert check_printed_line_rederives(line) is False


@pytest.mark.skipif(not LEDGER.exists(), reason="no generated ledger")
def test_the_real_ledger_actually_carries_register_rows_with_rates():
    """FAIL-OPEN guard on the register branch: it passes vacuously if no
    invoice has registers, or if no register carries a rate."""
    ledger = json.loads(LEDGER.read_text())
    rows = [r for e in ledger["customers"].values() for i in e["invoices"]
            for r in i.get("registers", [])]
    assert len(rows) > 1000
    assert sum(1 for r in rows if r.get("unit_rate_p_per_kwh") is not None) > 0.9 * len(rows)


# --------------------------------------------------------------------------
# TAUTOLOGY guard
# --------------------------------------------------------------------------
def test_the_checker_does_not_consult_the_printer():
    """R15 TAUTOLOGY: asking `saas.money` whether its own output reconciles
    would pass by construction for any rate it chose, including a wrong one --
    the control could never fire. The checker owns its arithmetic."""
    tree = ast.parse(Path(di.__file__).read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    # AST, not a substring search: this file's PROSE necessarily names
    # saas.money to explain why it does not call it, and a grep-shaped test
    # would fail on the explanation while missing a real import added later.
    assert not [m for m in imported if m.split(".")[0] == "saas"], sorted(imported)


# --------------------------------------------------------------------------
# The rate boundary itself
# --------------------------------------------------------------------------
def test_the_coarsest_sufficient_precision_is_chosen():
    """Not merely 'a' precision that works -- the coarsest, so a domestic bill
    still looks like a bill."""
    assert display_rate_p_per_kwh(317.9, 37.82) == (11.897, 3)
    assert display_rate_gbp_per_day(31, 7.44) == (0.24, 2)


def test_the_display_floor_holds():
    """A UK bill prints '24.50p/kWh', never '24.5p'. Even where 1dp would
    reconcile, the printed rate is not coarser than the floor."""
    rate, dp = display_rate_p_per_kwh(100.0, 12.50)
    assert dp == RATE_DISPLAY_MIN_DP == 2


def test_a_line_needing_more_than_the_cap_returns_None():
    """Rather than print a rate at a precision nobody can use, print none --
    which the portal already renders, and which claims nothing."""
    assert minimal_display_rate(1e9, 1234.56, scale=0.01) is None
    assert RATE_DISPLAY_MAX_DP == 6


def test_a_zero_quantity_prints_no_rate():
    """No rate divides into nothing; printing one would invent an arithmetic."""
    assert display_rate_p_per_kwh(0, 0.0) is None


@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_the_rate_boundary_fails_CLOSED_on_non_finite(bad):
    """A broken input raises rather than returning None: None means 'this line
    cannot carry a rate', which would quietly launder a corrupt figure into a
    tidy, passing bill."""
    with pytest.raises(MoneyBoundaryError):
        display_rate_p_per_kwh(bad, 10.0)
    with pytest.raises(MoneyBoundaryError):
        display_rate_p_per_kwh(100.0, bad)


def test_the_printed_amount_is_never_moved_to_tidy_the_printout():
    """The rejected alternative (fix the rate at 2dp, DERIVE the amount) would
    change this industrial line by GBP 7.86. The boundary fits the rate to the
    amount, so the amount it is given is the amount that stands."""
    rate, _ = display_rate_p_per_kwh(157128.8, 17215.01)
    assert round(157128.8 * 11.96 / 100, 2) != 17215.01  # the 2dp alternative
    assert round(157128.8 * rate / 100, 2) == 17215.01


# --------------------------------------------------------------------------
# Population-level: the real published book
# --------------------------------------------------------------------------
@pytest.mark.skipif(not LEDGER.exists(), reason="no generated ledger")
def test_every_invoice_in_the_real_ledger_rederives():
    """The control on real data, not fixtures -- the measurement that made this
    atom (86.1% of rendered usage lines failing) must now be zero."""
    ledger = json.loads(LEDGER.read_text())
    bad = [
        (c, inv.get("period_end"))
        for c, entry in ledger["customers"].items()
        for inv in entry["invoices"]
        if not check_printed_line_rederives(inv)
    ]
    assert bad == [], f"{len(bad)} printed lines do not re-derive: {bad[:5]}"


@pytest.mark.skipif(not LEDGER.exists(), reason="no generated ledger")
def test_no_printed_daily_rate_carries_float_residue():
    ledger = json.loads(LEDGER.read_text())
    residue = [
        (c, inv["period_end"], repr(inv["standing_charge_gbp_per_day"]))
        for c, entry in ledger["customers"].items()
        for inv in entry["invoices"]
        if inv.get("standing_charge_gbp_per_day") is not None
        and len(repr(float(inv["standing_charge_gbp_per_day"])).split(".")[-1])
        > RATE_DISPLAY_MAX_DP
    ]
    assert residue == [], residue


@pytest.mark.skipif(not LEDGER.exists(), reason="no generated ledger")
def test_the_control_is_not_vacuous_on_the_real_ledger():
    """FAIL-OPEN guard on the population test above: it would also pass if
    every invoice printed no rate at all. Assert the book actually exercises
    the arithmetic."""
    ledger = json.loads(LEDGER.read_text())
    invs = [i for e in ledger["customers"].values() for i in e["invoices"]]
    with_rate = [i for i in invs if i.get("unit_rate_p_per_kwh") is not None]
    assert len(invs) > 1000
    assert len(with_rate) > 0.9 * len(invs)
