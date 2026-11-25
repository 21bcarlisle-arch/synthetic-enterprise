"""The renewal chain's price must not hear the payment-behaviour score.

The defect this catches: forwarding `behaviour_score` from `renewal_margin_uplift` into
`decide_margin`. The score enters the churn term as a floor that does not move with price, so the
value arm prices up across it. On 2026-11-25 that meant up to GBP 30/MWh more margin for a CRITICAL
payer than for a clean one, which is cost loaded onto a household in difficulty by an unsourced
uplift. See docs/market_research/what_the_payment_score_counts_beside_the_arrears_state_2026-11-25.md.
"""
from __future__ import annotations

import ast
import inspect

import company.pricing.value_based_renewal as vbr


def _decide_margin_calls_in_the_adapter() -> list[ast.Call]:
    tree = ast.parse(inspect.getsource(vbr.renewal_margin_uplift))
    return [n for n in ast.walk(tree)
            if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "decide_margin"]


def test_the_adapter_does_not_forward_the_payment_score():
    calls = _decide_margin_calls_in_the_adapter()
    # The guard is only worth anything if it is reading the call it means to guard.
    assert len(calls) == 1, f"expected the adapter's one decide_margin call, found {len(calls)}"
    call = calls[0]
    names = {kw.arg for kw in call.keywords}
    assert None not in names, "a **mapping into decide_margin hides what reaches the price"
    assert "arrears_state" in names, "the sourced payment signal must still reach the price"
    assert "behaviour_score" not in names, (
        "the renewal price now reads the payment-behaviour score. It enters as a price-flat floor "
        "and raises distressed payers' margins; see the knowledge page named in this module."
    )
