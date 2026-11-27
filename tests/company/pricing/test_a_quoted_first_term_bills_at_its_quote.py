"""A won first fixed term contracted at its quote leaves the renewal chain at the quote, to the penny.

The defect: `renewals.contracted_first_term` set the term to the quote, then the run loop passed it
through `decide_renewal`, whose B12 bad-debt allowance re-struck it. 103/103 quoted gas first terms
billed 1.0019-1.0283x their quote, 1.0200x exactly wherever the belief was still the 2.0% prior
(`docs/staging/SEAT_FINDING_A_QUOTED_FIRST_TERM_IS_REPRICED_ABOVE_ITS_QUOTE_BY_THE_RENEWAL_CHAIN_2026-11-27.md`).
SLC 23 forms the contract on the price shown; SLC 22C forbids a rise during the fix
(cheapest_fix_against_the_default_tariff_gb_2016_2025.md §13).
"""
from __future__ import annotations

import pytest

from company.interfaces.renewal_decision_inputs import RenewalDecisionInputs
from company.interfaces.renewal_rate_chain import decide_renewal
from company.pricing import renewal_rate_chain as chain
from simulation import svt_rates

ON = "2021-10-01"  # capped, outside the EPG window: the acquisition hold binds a first fixed term
FLAT = {"metering": "NHH", "smart_meter": False}


def _cap() -> float:
    return svt_rates.get_svt_elec_rate_gbp_per_mwh(ON) / 1.05


def _billed(quote: float, *, contracted: bool, belief: float | None = 0.02) -> float:
    return decide_renewal(RenewalDecisionInputs(
        customer_id="C1", billing_account="C1", commodity="electricity", term_start=ON,
        tariff_type="fixed", term_index=0, struck_unit_rate_per_mwh=quote,
        portfolio_margin_rates=[], prior_term_margin=None, prior_term_revenue=0.0,
        is_domestic=True, segment="resi", settled_records=[], customer=FLAT,
        default_belief_rate=belief, contracted_at_quote=contracted)).unit_rate_gbp_per_mwh


def _partition() -> dict[str, bool]:
    """Which of the two writers that reach a first term moved it: the allowance (a quote under the
    cap) and the cap hold (a quote 30% over it). Each is asked with and without the contract."""
    under, over = _cap() * 0.9, _cap() * 1.3
    return {
        "allowance, not contracted": _billed(under, contracted=False) != under,
        "hold, not contracted": _billed(over, contracted=False, belief=None) != over,
        "allowance, contracted": _billed(under, contracted=True) != under,
        "hold, contracted": _billed(over, contracted=True, belief=None) != over,
    }


def test_a_contracted_quote_is_billed_at_the_quote_and_an_uncontracted_strike_still_moves():
    """Catches the re-strike (the contracted legs move), and a guard that disarms every first term
    (the uncontracted legs stop moving), in one assertion over the whole partition."""
    assert chain.FIRST_TERM_CAP_HOLD_DELETED is False  # the hold leg is live only while it stands
    assert _partition() == {"allowance, not contracted": True, "hold, not contracted": True,
                            "allowance, contracted": False, "hold, contracted": False}


def test_the_contracted_quote_is_the_exact_float():
    """Catches an approximate pass-through: done means to the penny, and the rate is a float."""
    quote = 31.626
    assert _billed(quote, contracted=True) == quote
    assert _billed(quote, contracted=False) == pytest.approx(quote * 1.02)


def test_the_run_loop_tells_the_desk_which_terms_it_contracted_at_their_quote():
    """Catches the guard released on the desk and never passed by its only caller: the record
    built in the run loop must key `contracted_at_quote` on the mark `contracted_first_term` writes."""
    import ast
    import inspect

    import simulation.renewals as renewals
    import simulation.run_phase2b as run_loop

    assert '"struck_by": "first_term_quote"' in inspect.getsource(renewals.contracted_first_term)
    passed = [ast.unparse(kw.value) for node in ast.walk(ast.parse(inspect.getsource(run_loop)))
              if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "RenewalDecisionInputs"
              for kw in node.keywords if kw.arg == "contracted_at_quote"]
    assert len(passed) == 1 and "'first_term_quote'" in passed[0], passed
