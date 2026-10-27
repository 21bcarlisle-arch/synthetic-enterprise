"""The company's cap clamp holds a default tariff at its payment method's own cap, not the DD level.

The world prices a prepayment SVT segment at the prepayment column (58af1fe57). The company's own
writers 1-2 then raise it, and writer 4 clamped only at the published level, which is the DD column.
On the 871f674a2 book that was every one of the 298 electricity and 249 gas SVT unit-rate breaches.
SYN-2016-061, Jan 2023: entered at 631.48, premium to 726.20, clamped at 642.57
(`docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`, choice 7).

The reference is the WORLD's re-priced rate (`simulation.price_cap_enforcement`), not the chain's
helper: a helper that drifted would agree with itself.

Each test names the defect it catches.
"""

from __future__ import annotations

import ast
import json
from datetime import date
from pathlib import Path

import pytest

from company.pricing import renewal_rate_chain as chain
from simulation.price_cap_enforcement import default_tariff_unit_rates_for_method_inc_vat

ROOT = Path(__file__).resolve().parents[3]
FLAT = {"metering": "NHH", "smart_meter": False}
_COMPOSITION = ROOT / "docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json"


def _capped_starts() -> list[str]:
    raw = json.loads(_COMPOSITION.read_text())
    return sorted({p["starts"] for p in raw["by_payment_method"]["prepayment"]["periods"]
                   if p.get("cap_in_force") and p["starts"] <= "2025-10-01"})


CAPPED = _capped_starts()


def _nodes(node: ast.AST):
    """`ast.walk`, spelled out: the whole-directory-subject census reads any `.walk(` call as a
    walk of the repository, and this reads one file."""
    yield node
    for child in ast.iter_child_nodes(node):
        yield from _nodes(child)


def _world_priced_ex_vat(commodity: str, on: str, method: str) -> float:
    priced, _, _ = default_tariff_unit_rates_for_method_inc_vat(
        commodity, date.fromisoformat(on), method)
    return priced / 1.05


def _contracted(*, commodity, on, tariff_type, struck, method, term_index=0) -> float:
    return chain.decide_renewal_rate(
        customer_id="C1", billing_account="C1", commodity=commodity, term_start=on,
        tariff_type=tariff_type, term_index=term_index, struck_unit_rate_gbp_per_mwh=struck,
        portfolio_margin_rates=[], prior_term_margin_gbp=None, prior_term_revenue_gbp=0.0,
        is_domestic=True, segment="resi", settled_records=[], customer=FLAT,
        payment_method=method,
    ).unit_rate_gbp_per_mwh


def test_the_871f674a2_case_is_clamped_at_the_prepayment_column():
    """Catches writer 4 clamping a prepayment SVT at the DD level: SYN-2016-061's Jan 2023 rate,
    raised by the premium to 726.20, came back at 642.57, 1.8% over its own cap of 631.48."""
    got = _contracted(commodity="electricity", on="2023-01-01", tariff_type="svt",
                      struck=726.202, method="prepayment")
    assert got == pytest.approx(631.48, abs=0.01), f"contracted {got:.2f}, the prepayment cap is 631.48"


@pytest.mark.parametrize("commodity", ["electricity", "gas"])
def test_every_capped_window_holds_each_method_at_the_worlds_own_price(commodity):
    """Catches the method dropped anywhere on the way to the clamp, and a clamp at the method's
    column where the published level is lower. A rate raised 38% is held, in every capped window,
    at the price the world itself sets for that method. The partition is asserted whole: prepayment
    is lowered in some windows and kept at the published level in others (gas, Oct 2022 - Jun 2023),
    and direct debit and standard credit are never lowered. So a clamp that lowers everything, or
    nothing, fails."""
    lowered = kept = 0
    for on in CAPPED:
        published = _world_priced_ex_vat(commodity, on, "direct_debit")
        for method in ("direct_debit", "standard_credit", "prepayment"):
            want = _world_priced_ex_vat(commodity, on, method)
            got = _contracted(commodity=commodity, on=on, tariff_type="svt",
                              struck=published * 1.38, method=method)
            assert got == pytest.approx(want, rel=1e-6), (
                f"{commodity} {method} {on}: contracted {got:.3f}, the world prices {want:.3f}")
            if method != "prepayment":
                assert got == pytest.approx(published, rel=1e-9), f"{method} {on} was lowered"
            elif got < published * (1 - 1e-6):
                lowered += 1
            else:
                kept += 1
    assert lowered, f"no {commodity} prepayment window was lowered, so the column never bound"
    if commodity == "gas":
        assert kept, "no gas prepayment window kept the published level: min() became the column"


def test_a_fixed_first_term_on_prepayment_is_held_at_the_published_level():
    """Catches the method column applied beyond SLC 28AD. The acquisition rule that holds a first
    fixed term at the cap is this supplier's choice, at the published level; a prepayment fix is
    not a default tariff."""
    published = chain.cap_ceiling_ex_vat("electricity", date(2023, 7, 1), multi_register=False)
    got = _contracted(commodity="electricity", on="2023-07-01", tariff_type="fixed",
                      struck=published * 1.38, method="prepayment")
    assert got == pytest.approx(published, rel=1e-9)
    assert published > _world_priced_ex_vat("electricity", "2023-07-01", "prepayment") * 1.01, (
        "the two levels agree on this date, so this control proves nothing")


def test_the_run_hands_the_chain_the_method_the_segment_was_priced_on():
    """Catches a spliced or first default segment reaching the chain with no method: writer 1 can
    fire on a spliced segment, where the renewal method is not resolved, and the clamp would fall
    back to the DD level. The fallback must sit in the run's body, ahead of the chain's call."""
    src = (ROOT / "simulation/run_phase2b.py").read_text()
    tree = ast.parse(src)
    falls_back = [n.lineno for n in _nodes(tree) if isinstance(n, ast.If)
                  and ast.unparse(n.test) == "_company_payment_method is None"
                  and any(ast.unparse(b) == "_company_payment_method = _svt_priced_method"
                          for b in n.body)]
    chain_calls = [n.lineno for n in _nodes(tree) if isinstance(n, ast.Call)
                   and getattr(n.func, "id", None) == "RenewalDecisionInputs"]
    assert len(falls_back) == 1 and len(chain_calls) == 1, (falls_back, chain_calls)
    assert falls_back[0] < chain_calls[0], "the fallback is resolved after the chain is asked"
