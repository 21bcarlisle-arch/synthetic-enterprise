"""JOIN 4 — the market chain: price → hedge → settlement → P&L.

Design: `docs/design/JOIN_TEST_TIER.md`. R15 cut-proofs: `test_join_cut_mutation.py`.

Asserts a price move ALONE changes the hedge decision, and that the hedge then
reaches the reported result when the spike actually arrives. Both legs settle
against the same spot prices, so the hedge the price history bought is the only
live variable downstream.

REPORT-ONLY first landing — see JOIN_TEST_TIER.md §3.
"""

import pytest

from tests.system import chains

pytestmark = pytest.mark.join_report_only


def test_the_market_chain_join_conducts():
    """Volatility reaches the hedge decision; the hedge reaches the P&L."""
    chain = chains.run_market_chain()
    chains.assert_market_join(chain)


def test_the_hedge_decision_reads_only_observable_price_history():
    """The wall at the trading seam: `decide_hedge_fraction` is a function of the
    price records handed to it and nothing else. Two identical histories must
    produce identical decisions — a decision that varied without its input
    varying would be reading something the company cannot see."""
    from company.trading import hedge_decision

    history = [
        {"settlementDate": f"2022-08-{d:02d}", "settlementPeriod": 1,
         "systemSellPrice": 55.0 * (1.12 if d % 2 else 1.0)}
        for d in range(1, 29)
    ]
    first = hedge_decision.decide_hedge_fraction(4000.0, 60.0, 90.0, history, 180)
    second = hedge_decision.decide_hedge_fraction(4000.0, 60.0, 90.0, list(history), 180)
    assert first == second, (
        f"the same observable price history produced two different decisions "
        f"({first} vs {second}) — the decision has a hidden input"
    )


def test_a_hedge_costs_money_when_the_spike_does_not_come():
    """The opposite direction, and the honest one: hedging is not free insurance.

    If the hedged book beat the unhedged book at EVERY spot price, the settlement
    would not be modelling a hedge at all — it would be modelling a discount. Run
    the same chain with spot BELOW the forward and assert the hedge now costs.
    """
    chain = chains.run_market_chain(spike_price=20.0)
    fully = chain["settled_fully_hedged"]
    unhedged = chain["settled_unhedged"]
    assert fully["wholesale_cost_gbp"] > unhedged["wholesale_cost_gbp"], (
        "with spot far BELOW the forward, the fully-hedged book still cost no more than "
        f"the unhedged one (GBP{fully['wholesale_cost_gbp']:.2f} vs "
        f"GBP{unhedged['wholesale_cost_gbp']:.2f}) — the hedge is not being settled"
    )


def test_no_wall_crossing_in_the_market_chain_participants():
    chains.assert_no_wall_crossing(
        [
            "company/trading/hedge_decision.py",
            "company/risk/hedge_policy.py",
            "company/market/hedge_performance.py",
        ]
    )
