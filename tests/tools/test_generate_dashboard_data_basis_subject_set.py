"""The R14 basis gate's SUBJECT SET is derived, and the debt it grandfathers is a ratchet.

Why this file exists (2026-08-22, E5_carbon_three_ledger FRAME control C4, R10):
the gate `_check_basis_labels_present` used to take its subjects from a two-name
tuple. R14 says every published financial figure carries its clock, but a
hand-kept allowlist inverts the rule -- a figure is checked only if somebody
remembered to name it, so every NEW headline figure is born unchecked and passes
by never being the subject. That is R15's fail-silent pattern sitting inside the
control that exists to stop an unlabelled number reaching the front door.

E5 surfaced it as a single instance (a published tCO2e figure would pass the gate
by never being checked) and its own note named the class fix: extend the SUBJECT
SET, do not append two carbon keys. These tests hold that line in all three
directions, and the null control is the real published portfolio.

The gate is currently in REPORTED_NOT_BLOCKING, so a red here does not wedge a
publish -- it changes what the cycle prints to stderr. That is stated so nobody
reads these assertions as stronger than they are.
"""

import pytest

import tools.generate_dashboard_data as gdd
from tools.generate_dashboard_data import (
    _BASIS_DECLARED_UNLABELLED,
    _BASIS_REQUIRED_SUFFIXES,
    _basis_required_portfolio_keys,
    _check_basis_labels_present,
    extract_portfolio,
)

# The allowlist this file replaced. Kept verbatim so the tests below can show
# what it was BLIND to, rather than merely asserting the new rule is nicer.
_SUPERSEDED_ALLOWLIST = ("net_margin_gbp", "enterprise_value_gbp")

_GOOD_BASIS = {"clock": "settled", "provisional": True, "note": "x"}


def _real_portfolio():
    return extract_portfolio({"total_net_gbp": 100.0, "enterprise_value_gbp": 200.0})


# --------------------------------------------------------------------------
# NULL CONTROL -- the shipped portfolio, unmutated, must pass.
# --------------------------------------------------------------------------

def test_the_real_published_portfolio_passes_the_derived_gate():
    assert _check_basis_labels_present(_real_portfolio()) is True


# --------------------------------------------------------------------------
# DIRECTION 1 -- a figure born after the rule is a subject automatically.
# This is the class defect: each of these passed the superseded allowlist.
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "new_key",
    [
        "hedge_pnl_gbp",              # a plausible future money headline
        "net_carbon_tco2e",           # E5's own instance -- the one that surfaced the class
        "cost_per_tco2e",             # the mission metric itself
    ],
)
def test_a_figure_added_tomorrow_is_a_subject_without_anyone_naming_it(new_key, capsys):
    portfolio = {
        "net_margin_gbp": 100.0,
        new_key: 42.0,
        "basis": {"net_margin_gbp": _GOOD_BASIS},
    }

    # The superseded allowlist could not see it: the key is simply not iterated.
    assert new_key not in _SUPERSEDED_ALLOWLIST
    # The derived rule does, with nobody having edited a list.
    assert new_key in _basis_required_portfolio_keys(portfolio)
    assert _check_basis_labels_present(portfolio) is False
    assert new_key in capsys.readouterr().err


def test_a_labelled_new_figure_passes_so_the_rule_is_not_a_blanket_refusal():
    portfolio = {
        "net_margin_gbp": 100.0,
        "net_carbon_tco2e": 42.0,
        "basis": {"net_margin_gbp": _GOOD_BASIS, "net_carbon_tco2e": _GOOD_BASIS},
    }
    assert _check_basis_labels_present(portfolio) is True


def test_a_key_with_no_published_quantity_suffix_is_not_a_subject():
    # bills_total / churn_count are counts, not money or carbon. Deny-by-default
    # must not mean deny-everything, or the register becomes the allowlist again.
    portfolio = {"bills_total": 12, "churn_count": 3, "basis": {}}
    assert _basis_required_portfolio_keys(portfolio) == ()
    assert _check_basis_labels_present(portfolio) is True


# --------------------------------------------------------------------------
# DIRECTION 2 and 3 -- the grandfathered debt cannot rot.
# --------------------------------------------------------------------------

def test_every_declared_unlabelled_figure_is_one_the_portfolio_actually_emits():
    """A declaration for a key extract_portfolio no longer produces is a stale
    excuse, and a stale excuse is how a register becomes a list of what the gate
    used to worry about."""
    portfolio = _real_portfolio()
    stale = sorted(k for k in _BASIS_DECLARED_UNLABELLED if k not in portfolio)
    assert stale == [], f"declared-unlabelled entries for figures no longer published: {stale}"


def test_no_figure_is_declared_unlabelled_once_it_has_a_real_basis_entry():
    """The repair for an entry here is a basis label. If one arrives and the
    declaration stays, the figure is checked by neither: the declaration
    suppresses the gate and the gate no longer reads the label."""
    portfolio = _real_portfolio()
    basis = portfolio.get("basis", {}) or {}
    repaired_but_still_declared = sorted(set(basis) & set(_BASIS_DECLARED_UNLABELLED))
    assert repaired_but_still_declared == [], (
        "these figures now carry a basis entry and must be removed from "
        f"_BASIS_DECLARED_UNLABELLED: {repaired_but_still_declared}"
    )


def test_every_declaration_states_a_reason():
    unreasoned = sorted(k for k, v in _BASIS_DECLARED_UNLABELLED.items() if not (v or "").strip())
    assert unreasoned == [], f"declared without a written reason: {unreasoned}"


# --------------------------------------------------------------------------
# The measurement that made this a class rather than an instance, pinned.
# --------------------------------------------------------------------------

def test_every_published_money_or_carbon_figure_is_either_labelled_or_declared():
    """The whole rule in one assertion: no suffixed key escapes BOTH the basis
    block and the declared-unlabelled register. This is what the allowlist could
    not state, because its subject set did not depend on the portfolio."""
    portfolio = _real_portfolio()
    basis = portfolio.get("basis", {}) or {}
    suffixed = {
        k for k in portfolio
        if isinstance(k, str) and k.endswith(_BASIS_REQUIRED_SUFFIXES)
    }
    escaped = sorted(suffixed - set(basis) - set(_BASIS_DECLARED_UNLABELLED))
    assert escaped == [], f"published with no clock and no declaration: {escaped}"


def test_the_superseded_allowlist_was_blind_to_five_live_figures():
    """Observed-with-evidence (R9), and the reason this was promoted to a class
    fix: on the real portfolio the old two-name tuple left five money figures
    unchecked. Pinning the count means a future pass can see the debt shrink."""
    portfolio = _real_portfolio()
    suffixed = {
        k for k in portfolio
        if isinstance(k, str) and k.endswith(_BASIS_REQUIRED_SUFFIXES)
    }
    unseen_by_old_rule = sorted(suffixed - set(_SUPERSEDED_ALLOWLIST))
    assert unseen_by_old_rule == [
        "cost_to_serve_gbp",
        "gross_margin_gbp",
        "net_after_cts_gbp",
        "treasury_end_gbp",
        "treasury_start_gbp",
    ]
    # ... and each is now visible, as declared debt rather than as silence.
    assert set(unseen_by_old_rule) == set(_BASIS_DECLARED_UNLABELLED)


def test_the_declared_debt_is_printed_not_swallowed(capsys):
    """A register nobody reads is how five figures got here. Passing the gate
    must still say what it waved through."""
    assert _check_basis_labels_present(_real_portfolio()) is True
    err = capsys.readouterr().err
    assert "BASIS-LABEL DEBT" in err
    for key in _BASIS_DECLARED_UNLABELLED:
        assert key in err


def test_the_gate_is_reported_not_blocking_so_this_files_reds_do_not_wedge_publishing():
    """Stated, not assumed: the director's 2026-08-20 rule keeps this check out
    of the publish verdict while its figures have no reader-reachable page. If
    that changes, this assertion fails and whoever moves it must re-read what
    these tests do and do not promise."""
    assert "_check_basis_labels_present" in gdd.REPORTED_NOT_BLOCKING
