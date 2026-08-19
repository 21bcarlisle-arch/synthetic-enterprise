"""The customer book is valued on the margin the customer actually leaves behind.

Discharges `WORKER_FINDING_THE_BOOK_IS_VALUED_ON_A_MARGIN_THAT_EXCLUDES_THREE_
QUARTERS_OF_THE_COST_STACK_2026-08-17` (BLOCKING, lane B_commercial).

THE DEFECT. `build_clv` valued each account on `cost_to_serve`'s
`net_margin_gbp`, which in that module's key space meant `margin_gbp -
cost_to_serve_gbp` — revenue minus wholesale minus cost-to-serve. The policy
levies (RO/CfD/CM/FiT/CCL/mutualisation), the network charges on both fuels,
capital and bad debt — £4,890,769.21, or 75.969% of gross margin on the
published run — reached the P&L and not the valuation. Cost-to-serve, 0.36% of
gross, was the only sub-wholesale cost in it. C7 was published as a £7,771.10
asset on a believed £1,201.15/yr while the same run's P&L gave it £11.78/yr,
and -£40.13/yr once its own cost-to-serve was charged.

R15 — EACH TEST BELOW PERFORMS A NAMED DEFECT RATHER THAN ASSERTING ITS
ABSENCE. The two mutations are the two the finding specified, and both are RED
on the pre-repair code for the reason the finding gave:

  (a) `test_mutation_removing_a_levy_moves_the_valuation` — delete a levy from
      a customer's cost stack and the published value must MOVE. Before the
      repair it could not: no levy was in the number.
  (b) `test_mutation_an_account_that_loses_money_is_not_published_as_an_asset`
      — hand `build_clv` an account whose net-of-all-costs margin is negative
      and its `clv_gbp` must be negative or absent, never positive. Before the
      repair the same account published a positive CLV off its contribution
      margin.

Plus the two anti-fail-open directions the pair needs: the valuation must not
merely be *smaller* (a hardcoded haircut would pass (a) and (b) alike), and a
`cost_to_serve` view that cannot supply the declared basis must RAISE rather
than fall back to whatever line it does carry.
"""

import pytest

from saas.clv_model import CLV_MARGIN_BASIS, build_clv

# Three renewal points each, identical belief, so any difference between the
# accounts below is a MARGIN difference and never a churn one.
_CHURN_RISK = {
    "STEADY": [
        {"renewal_period": f"201{i}-01", "bill_shock_count": 0, "churn_probability": 0.08}
        for i in range(3)
    ],
    "LOSSMAKER": [
        {"renewal_period": f"201{i}-01", "bill_shock_count": 0, "churn_probability": 0.08}
        for i in range(3)
    ],
}

#: One account's cost stack, at the shape the published run actually has:
#: gross margin £1,000, of which levies and network charges take £760 (the
#: finding measured 75.969% of gross never reaching the valuation) and
#: cost-to-serve takes £4.
_GROSS_MARGIN = 1000.0
_LEVIES_AND_NETWORK = 760.0
_COST_TO_SERVE = 4.0


def _cost_to_serve_view(levies_and_network=_LEVIES_AND_NETWORK, gross=_GROSS_MARGIN):
    """A `build_cost_to_serve`-shaped view for one account, on both bases.

    Built from the cost stack rather than from the two margin lines directly,
    so a test that changes a LEVY changes only that levy — and the
    contribution line, which no levy has ever touched, stays put.
    """
    return {
        "by_customer": {
            "STEADY": {
                "cost_to_serve_gbp": _COST_TO_SERVE,
                "margin_gbp": gross,
                "contribution_margin_gbp": gross - _COST_TO_SERVE,
                "net_of_all_costs_margin_gbp": gross - levies_and_network - _COST_TO_SERVE,
            },
        }
    }


def _clv(view):
    result = build_clv(
        {"STEADY": _CHURN_RISK["STEADY"]}, view, n_draws=50
    )
    return result["STEADY"]["clv_gbp"]


# ---------------------------------------------------------------------------
# Mutation (a): the valuation must be able to feel a levy
# ---------------------------------------------------------------------------

def test_mutation_removing_a_levy_moves_the_valuation():
    """THE killer the finding named first. Delete £200 of levy from this
    account's cost stack and its published value must rise.

    Under the defect both runs returned the SAME number, because the levy was
    not in the line the valuation read. Asserts the MOVE and its DIRECTION,
    not any particular value."""
    with_levy = _clv(_cost_to_serve_view())
    without_levy = _clv(_cost_to_serve_view(levies_and_network=_LEVIES_AND_NETWORK - 200.0))

    assert without_levy != with_levy, (
        "removing £200 of levy from the account's cost stack did not move its "
        "CLV -- the valuation is not built on a line the levy reaches"
    )
    assert without_levy > with_levy, (
        "removing a COST made the account less valuable -- the basis is wired "
        "with the wrong sign"
    )


def test_the_levy_move_is_not_merely_a_constant_haircut():
    """ANTI-FAIL-OPEN for the test above. A valuation that subtracted a fixed
    amount, or scaled the contribution line by a constant, would pass the
    move test on any input. This pins the SIZE of the response: the £200 of
    levy removed must show up as £200/yr more margin, and the CLV must move by
    that times the same annuity factor the figure is built with.

    Independence: the expected move is computed from the margin delta and the
    figure's OWN annuity factor read back out of the unmutated result, not
    from a second call to the code under test."""
    base = build_clv({"STEADY": _CHURN_RISK["STEADY"]}, _cost_to_serve_view(), n_draws=50)["STEADY"]
    moved = build_clv(
        {"STEADY": _CHURN_RISK["STEADY"]},
        _cost_to_serve_view(levies_and_network=_LEVIES_AND_NETWORK - 200.0),
        n_draws=50,
    )["STEADY"]

    # £200 of levy removed, spread over the 3 renewal points the margin is
    # averaged across.
    expected_margin_delta = 200.0 / 3
    assert moved["avg_annual_net_margin_gbp"] - base["avg_annual_net_margin_gbp"] == pytest.approx(
        expected_margin_delta
    )

    annuity_factor = base["clv_gbp"] / base["avg_annual_net_margin_gbp"]
    assert moved["clv_gbp"] - base["clv_gbp"] == pytest.approx(
        expected_margin_delta * annuity_factor
    )


# ---------------------------------------------------------------------------
# Mutation (b): a loss-making account is not an asset
# ---------------------------------------------------------------------------

def test_mutation_an_account_that_loses_money_is_not_published_as_an_asset():
    """THE second killer. An account whose margin after every attributable
    cost is NEGATIVE must not carry a positive CLV.

    This is CLAUDE.md's activity-based-pricing rule as an executable
    assertion: "flat margin makes some customers net-negative; any pricing
    model must account for cost-to-serve at the customer level". C7 met that
    rule's letter and failed its substance -- cost-to-serve WAS subtracted,
    and the levies that actually made C7 negative were not.

    The account below is positive on the contribution basis (+£996) and
    negative on the true one (-£4), so the two bases give OPPOSITE SIGNS and
    the test cannot pass by reading the wrong one."""
    view = {
        "by_customer": {
            "LOSSMAKER": {
                "cost_to_serve_gbp": _COST_TO_SERVE,
                "margin_gbp": _GROSS_MARGIN,
                "contribution_margin_gbp": _GROSS_MARGIN - _COST_TO_SERVE,
                "net_of_all_costs_margin_gbp": -4.0,
            },
        }
    }
    result = build_clv({"LOSSMAKER": _CHURN_RISK["LOSSMAKER"]}, view, n_draws=50)

    entry = result.get("LOSSMAKER")
    if entry is not None:
        assert entry["clv_gbp"] < 0, (
            "an account that loses money on every attributable cost was "
            "published as a positive asset worth £{:.2f}".format(entry["clv_gbp"])
        )
        assert entry["avg_annual_net_margin_gbp"] < 0


# ---------------------------------------------------------------------------
# The declared basis is the consumed basis, and an absent one raises
# ---------------------------------------------------------------------------

def test_the_declared_basis_is_the_field_the_valuation_actually_reads():
    """`CLV_MARGIN_BASIS` is published as the figure's cost basis all the way
    to the site's basis line. If it named a field `build_clv` did not read,
    every downstream label would be false while every test above stayed green
    -- so this pins the two together by DELETING the declared field and
    requiring the valuation to fail."""
    view = _cost_to_serve_view()
    del view["by_customer"]["STEADY"][CLV_MARGIN_BASIS]

    with pytest.raises(KeyError):
        build_clv({"STEADY": _CHURN_RISK["STEADY"]}, view, n_draws=50)


def test_a_view_carrying_only_the_old_line_raises_rather_than_valuing_on_it():
    """FAIL-CLOSED, the anti-fail-open direction of the repair. A
    `cost_to_serve` view built before this repair carries `net_margin_gbp` and
    not the basis the valuation declares. It must RAISE.

    A `.get(CLV_MARGIN_BASIS, entry["net_margin_gbp"])` would have been the
    natural compatibility shim and would have reinstated the entire defect
    silently, on exactly the inputs most likely to be stale."""
    legacy_view = {
        "by_customer": {
            "STEADY": {
                "cost_to_serve_gbp": _COST_TO_SERVE,
                "margin_gbp": _GROSS_MARGIN,
                "net_margin_gbp": _GROSS_MARGIN - _COST_TO_SERVE,
            },
        }
    }
    with pytest.raises(KeyError):
        build_clv({"STEADY": _CHURN_RISK["STEADY"]}, legacy_view, n_draws=50)
