"""C35: the share of an action's value the supplier asks is the one with the most expected joint value.

Cells sit at C34's own scale (a household benefit of £40-80 a year against a margin loss of £2-3 a
month over 48 months), where C34 alone chooses nothing.
"""
from company.crm.next_best_action import (
    AccountState,
    Action,
    ActionEstimate,
    SharePoint,
    ShareResponse,
    decide,
    price_share,
    value_change,
)

H = 48
SHARES = (0.0, 0.25, 0.5, 0.75, 1.0)


def _account(account_id, benefit=60.0, margin_change=-2.5, points=SHARES, take_up=lambda s: 0.6 - 0.5 * s):
    est = ActionEstimate(Action.TARIFF_ADVICE, benefit, margin_change, 0.0)
    responses = () if points is None else (
        ShareResponse(Action.TARIFF_ADVICE, tuple(SharePoint(s, take_up(s)) for s in points)),)
    return AccountState(account_id, 15.0, 0.015, 0, (est,), responses), est


def test_every_outcome_of_the_pricing_is_reachable():
    """Priced, refused at every tried share, and untried: one book takes all three branches."""
    priced = decide(_account("priced")[0], H)
    refused = decide(_account("refused", points=(0.0, 0.25))[0], H)
    untried = decide(_account("untried", points=())[0], H)
    assert priced.action is Action.TARIFF_ADVICE and priced.share is not None
    assert refused.action is Action.NOTHING and "no tried share leaves both" in refused.unscored[0][1]
    assert untried.action is Action.NOTHING and "no share has been tried" in untried.unscored[0][1]


def test_without_a_tried_share_c34_still_chooses_nothing():
    assert decide(_account("c34", points=None)[0], H).action is Action.NOTHING


def test_the_chosen_share_has_the_most_expected_joint_value_of_the_tried_shares_under_both_floors():
    # Take-up that is not monotone, so the lowest floor-clearing share is NOT the answer.
    bumps = {0.0: 0.6, 0.25: 0.5, 0.5: 0.2, 0.75: 0.45, 1.0: 0.1}
    state, est = _account("bumpy", take_up=bumps.get)
    benefit = est.customer_benefit_gbp_per_year * H / 12.0
    base = value_change(state, est, H)
    expected = {s: bumps[s] * (base + benefit) for s in SHARES
                if base + s * benefit >= 0.0 and benefit - s * benefit >= 0.0}
    price, _ = price_share(state, est, state.share_responses[0], H)
    assert price.share == max(expected, key=expected.get) == 0.75
    assert price.expected_joint_value_gbp == max(expected.values())


def test_with_falling_take_up_the_share_is_the_lowest_that_clears_our_floor():
    """The fee is a transfer: above our floor it only costs households who would have said yes."""
    for benefit, margin_change in ((40.0, -2.0), (60.0, -2.5), (80.0, -3.0)):
        state, est = _account("falling", benefit, margin_change)
        floor = -value_change(state, est, H) / (benefit * H / 12.0)
        price, _ = price_share(state, est, state.share_responses[0], H)
        assert price.share == min(s for s in SHARES if s >= floor)
        assert price.expected_value_change_gbp >= 0.0 and price.expected_customer_benefit_gbp >= 0.0


def test_a_share_that_drives_households_away_loses_to_one_that_does_not():
    est = ActionEstimate(Action.TARIFF_ADVICE, 60.0, -2.5, 0.0)
    points = (SharePoint(0.5, 0.35, hazard_change_per_month=0.02), SharePoint(0.75, 0.3))
    state = AccountState("sour", 15.0, 0.015, 0, (est,), (ShareResponse(Action.TARIFF_ADVICE, points),))
    assert decide(state, H).share.share == 0.75
