"""A published figure that CLAIMS a parent must name a parent it is really on.

R10 class closure for `WORKER_FINDING_THE_BOOK_IS_VALUED_ON_A_MARGIN_THAT_
EXCLUDES_THREE_QUARTERS_OF_THE_COST_STACK_2026-08-17`.

The finding's instance was `enterprise_value_basis` saying "Derived from the
settled-clock net margin above" beside a £6,304,202.92 tile whose real parent
was a contribution margin totalling £6,414,533.34 — 4.15x the line it named.
The mislabel is what made the number look sane: £6.3m reads as ~4x a £1.55m
annual net margin, a plausible multiple for a customer book, where it was in
fact ~1.0x a margin line excluding 76% of the cost stack.

The CLASS is not "enterprise value is mislabelled". It is: a derived figure can
share its parent's CLOCK and still be a different QUANTITY, and R14's
basis-label gate — which checks a label is PRESENT — passes on that happily.
`_check_derived_basis_parentage` runs over every `derived_from` in the payload,
so a future derived figure is checked by declaring a parent at all.

R15 — the mutations below perform each named defect. The three killer patterns
are each given a test: TAUTOLOGY (the child's basis is read from the run, the
parent's is declared against the P&L — `test_the_two_sides_come_from_different
_sources`), FAIL-OPEN (missing/unknown/unpublished all fail, not pass), and
FAIL-SILENT (a run that cannot say what basis it used FAILS).
"""

import pytest

from tools.generate_dashboard_data import (
    UNKNOWN_COST_BASIS,
    _check_derived_basis_parentage,
    _cost_basis_of_valuation,
    extract_portfolio,
)


def _portfolio(child_basis="net_of_all_costs", parent_basis="net_of_all_costs", **over):
    p = {
        "net_margin_gbp": 1_547_113.39,
        "enterprise_value_gbp": 1_138_265.43,
        "basis": {
            "net_margin_gbp": {
                "clock": "settled", "provisional": True,
                "cost_basis": parent_basis,
                "note": "Settlement-derived (total_net_gbp).",
            },
            "enterprise_value_gbp": {
                "clock": "settled", "provisional": True,
                "derived_from": "net_margin_gbp",
                "cost_basis": child_basis,
                "note": "Discounted future margin of the supplied book.",
            },
        },
    }
    p.update(over)
    return p


# ---------------------------------------------------------------------------
# The gate passes on the repaired shape, and on the REAL publisher's output
# ---------------------------------------------------------------------------

def test_the_repaired_shape_passes():
    assert _check_derived_basis_parentage(_portfolio()) is True


def test_the_live_publishers_own_output_satisfies_the_gate():
    """Not a hand-built dict: `extract_portfolio` is the function that actually
    writes the site's basis block, so the gate is run against what ships.

    A gate green only on fixtures is the shape where the published artefact and
    the control drift apart — which is how the defect survived the R14
    basis-label gate that was already running over this same block."""
    portfolio = extract_portfolio({
        "total_net_gbp": 1_547_113.39,
        "enterprise_value_gbp": 1_138_265.43,
        "enterprise_value_margin_basis": "net_of_all_costs_margin_gbp",
    })
    assert _check_derived_basis_parentage(portfolio) is True


# ---------------------------------------------------------------------------
# MUTATION: the exact published defect
# ---------------------------------------------------------------------------

def test_mutation_the_published_defect_fails_the_gate(capsys):
    """THE instance. A valuation computed on the contribution basis, claiming
    to derive from a net-of-all-costs P&L line. This is the state the site was
    in when the finding was written, and it must not be publishable."""
    assert _check_derived_basis_parentage(_portfolio(child_basis="contribution")) is False
    err = capsys.readouterr().err
    assert "BASIS-PARENTAGE GATE FAILED" in err
    assert "contribution" in err and "net_margin_gbp" in err


def test_mutation_valuing_the_book_on_the_old_line_reaches_the_gate():
    """The same mutation entered where a future edit would really make it — at
    the valuation, not at the label. `_cost_basis_of_valuation` reads the run's
    own `enterprise_value_margin_basis`, which is carried out of
    `saas.clv_model.CLV_MARGIN_BASIS`, so switching the valuation back to the
    contribution line propagates to the label and the gate fails.

    This is what makes the label unforgeable rather than merely correct today."""
    portfolio = extract_portfolio({
        "total_net_gbp": 1_547_113.39,
        "enterprise_value_gbp": 6_304_202.92,
        "enterprise_value_margin_basis": "contribution_margin_gbp",
    })
    assert portfolio["basis"]["enterprise_value_gbp"]["cost_basis"] == "contribution"
    assert _check_derived_basis_parentage(portfolio) is False


# ---------------------------------------------------------------------------
# FAIL-CLOSED: absence must never read as "fine"
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("missing_basis", [None, "", UNKNOWN_COST_BASIS])
def test_a_figure_that_cannot_state_its_basis_fails(missing_basis):
    """FAIL-SILENT (R15): an unavailable check is a FAILED check. A run that
    does not say what margin it valued the book on is exactly the state the
    finding measured — the label was absent from the code and asserted in
    prose."""
    assert _check_derived_basis_parentage(_portfolio(child_basis=missing_basis)) is False


def test_a_run_that_does_not_report_its_valuation_basis_resolves_to_unknown():
    """The upstream half of the test above, and every way the field can be
    absent or wrong-typed. None of them may resolve to a real basis."""
    assert _cost_basis_of_valuation({}) == UNKNOWN_COST_BASIS
    assert _cost_basis_of_valuation({"enterprise_value_margin_basis": None}) == UNKNOWN_COST_BASIS
    assert _cost_basis_of_valuation({"enterprise_value_margin_basis": 42}) == UNKNOWN_COST_BASIS
    assert _cost_basis_of_valuation(None) == UNKNOWN_COST_BASIS
    # A margin field this module has no vocabulary entry for: a NEW basis
    # someone added to cost_to_serve.py without teaching the publisher what it
    # means must fail loudly, not be waved through under its own name.
    assert _cost_basis_of_valuation(
        {"enterprise_value_margin_basis": "some_future_margin_gbp"}
    ) == UNKNOWN_COST_BASIS


def test_a_parent_that_states_no_basis_fails():
    assert _check_derived_basis_parentage(_portfolio(parent_basis=None)) is False


def test_a_claimed_parent_that_is_not_published_fails(capsys):
    """"Derived from" a figure the payload does not carry is unfalsifiable by
    a reader and must not ship."""
    p = _portfolio()
    p["basis"]["enterprise_value_gbp"]["derived_from"] = "some_figure_nobody_publishes"
    assert _check_derived_basis_parentage(p) is False
    assert "not a published, basis-labelled figure" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# ANTI-VACUITY and ANTI-TAUTOLOGY
# ---------------------------------------------------------------------------

def test_the_gate_is_not_vacuous_on_a_payload_with_no_derived_figures():
    """A figure claiming NO parent claims nothing, so there is nothing to
    check — but this must be true because the gate examined it and found no
    claim, not because the gate never looks. Pinned by the mutation above
    failing on the same shape once a parent IS claimed."""
    p = _portfolio()
    del p["basis"]["enterprise_value_gbp"]["derived_from"]
    assert _check_derived_basis_parentage(p) is True
    p["basis"]["enterprise_value_gbp"]["derived_from"] = "net_margin_gbp"
    p["basis"]["enterprise_value_gbp"]["cost_basis"] = "contribution"
    assert _check_derived_basis_parentage(p) is False


def test_the_two_sides_come_from_different_sources():
    """ANTI-TAUTOLOGY (R15). The child's basis must NOT be derivable from the
    parent's — if the publisher wrote both from one place the gate could never
    disagree with itself.

    Demonstrated by moving ONE side and observing the gate break: the parent
    stays exactly as the P&L declares it while the run reports a different
    valuation basis, and they diverge. A tautological gate cannot produce this
    state at all."""
    same_run = {
        "total_net_gbp": 1_547_113.39,
        "enterprise_value_gbp": 6_304_202.92,
        "enterprise_value_margin_basis": "contribution_margin_gbp",
    }
    portfolio = extract_portfolio(same_run)
    parent = portfolio["basis"]["net_margin_gbp"]["cost_basis"]
    child = portfolio["basis"]["enterprise_value_gbp"]["cost_basis"]
    assert parent == "net_of_all_costs", "the parent's basis followed the run — it must not"
    assert child == "contribution"
    assert parent != child
