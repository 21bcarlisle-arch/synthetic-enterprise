"""The decision probe compares pricing rules on ONE book, and never moves that book.

The probe re-asks the pricing door under other policies and the world's renewal roll at other
prices, mid-run. If either re-ask changed the run it is observing, the "same customer, same
moment" comparison would be comparing against a book the probe itself bent. The first control
holds the reference run byte-for-byte against a plain run.
"""
from __future__ import annotations

from tools import decision_probe as dp


def _row(**over):
    row = {"billing_account": "A", "customer_id": "A", "commodity": "electricity",
           "term_start": "2019-01-01", "annual_mwh": 3.0, "base_gbp_per_mwh": 200.0,
           "offer_gbp_per_mwh": {"flat": 202.0, "value": 230.0},
           "true_p_retain": {"flat": 0.8, "value": 0.8},
           "true_bad_debt_share": 0.0, "reference_renewals_after": 0,
           "level_grid": {"20": {"offer": 220.0, "p": 0.75}, "30": {"offer": 230.0, "p": 0.7}}}
    row.update(over)
    return row


def test_a_higher_price_kept_with_the_same_chance_earns_more():
    r = _row()
    assert dp.expected_term_margin_gbp(r, "value") > dp.expected_term_margin_gbp(r, "flat") > 0


def test_the_worlds_chance_of_staying_weights_the_earnings():
    lost = _row(true_p_retain={"flat": 0.8, "value": 0.05})
    assert dp.expected_term_margin_gbp(lost, "value") < dp.expected_term_margin_gbp(lost, "flat")


def test_a_bad_payers_bigger_bill_is_a_bigger_loss():
    payer, debtor = _row(), _row(true_bad_debt_share=0.5)
    assert (dp.expected_term_margin_gbp(debtor, "value", bad_debt=True)
            < dp.expected_term_margin_gbp(payer, "value", bad_debt=True))
    assert dp.expected_term_margin_gbp(debtor, "value", bad_debt=False) == \
        dp.expected_term_margin_gbp(payer, "value", bad_debt=False)


def test_the_level_rule_is_taken_at_the_grid_point_nearest_the_value_rules_median():
    [r] = dp.with_level([_row()], 28.0)
    assert r["offer_gbp_per_mwh"]["level"] == 230.0 and r["true_p_retain"]["level"] == 0.7


def test_the_bootstrap_resamples_accounts_not_decisions():
    rows = [_row(billing_account="A"), _row(billing_account="A", term_start="2020-01-01"),
            _row(billing_account="B")]
    s = dp.score(rows)
    assert s["decisions"] == 3 and s["accounts"] == 2


def test_the_probe_leaves_the_reference_run_exactly_as_a_plain_run_leaves_it():
    """A short window, run plain and under the probe: every renewal outcome must be identical."""
    from company.policy.decision_policy import CURRENT_POLICY, policy_scope
    from simulation.run_phase4c_on_phase2b import main as run_phase4c

    rows = dp.probe("2017-03-31")
    with policy_scope(CURRENT_POLICY):
        plain = run_phase4c(report_end="2017-03-31", policy=CURRENT_POLICY)["phase2b"]
    assert rows, "vacuous: the probe saw no renewal, so it could not have moved anything"
    plain_events = sorted((e["customer_id"], e["event_date"], e["event_type"])
                          for e in plain["customer_events"] if isinstance(e, dict))
    assert dp.LAST_REFERENCE_EVENTS == plain_events


def test_the_blind_rule_strips_arguments_the_pricing_door_really_takes():
    """`value_blind` is the value rule with payment history removed. If the door ever renamed one
    of these, stripping it would silently do nothing and the blind rule would equal the sighted
    one -- a comparison that always reads zero and looks like a result."""
    import inspect

    from company.interfaces.renewal_rate_chain import decide_renewal_rate
    params = set(inspect.signature(decide_renewal_rate).parameters)
    assert dp.PAYMENT_HISTORY_ARGS and set(dp.PAYMENT_HISTORY_ARGS) <= params


def test_a_stayer_is_scored_on_what_they_pay_not_on_what_was_offered():
    """The world's decline rule bills a stayer the default when the fix is above it; the score
    must follow the bill. Defect it names: crediting the full offer to a household that refused
    it, which overstated the value rule's margin about twice over on the 2025 probes."""
    offered = _row(stayer_pays_gbp_per_mwh={"flat": 202.0, "value": 210.0})
    billed = _row(offer_gbp_per_mwh={"flat": 202.0, "value": 210.0})
    assert dp.expected_term_margin_gbp(offered, "value") == dp.expected_term_margin_gbp(
        billed, "value")
    [r] = dp.with_level([_row(stayer_pays_gbp_per_mwh={"flat": 202.0, "value": 210.0},
                              level_grid={"30": {"offer": 230.0, "p": 0.7, "paid": 211.0}})], 30.0)
    assert r["stayer_pays_gbp_per_mwh"]["level"] == 211.0


def test_the_worlds_decline_rule_can_be_taken_and_is_the_only_thing_that_moves_the_bill():
    """Both branches over one date: an offer far above the default is billed the default, one
    below it is billed as offered, and an undeclinable decision is never repriced."""
    above, below = dp.stayer_pays(900.0, "2020-06-01", "electricity", True), \
        dp.stayer_pays(50.0, "2020-06-01", "electricity", True)
    assert above is not None and above < 900.0 and below == 50.0
    assert dp.stayer_pays(900.0, "2020-06-01", "electricity", False) == 900.0


def test_the_belief_is_read_from_the_last_priced_entry_and_is_none_where_nothing_priced():
    """The belief column is the company's own P(stay) at the offer it struck; an arm that priced
    nothing must read None, never a neighbouring arm's belief or a default."""
    from types import SimpleNamespace
    priced = SimpleNamespace(value_arm_entries=[{"believed_p_retain": 0.4},
                                                {"believed_p_retain": None},
                                                {"believed_p_retain": 0.7}])
    assert dp._believed(priced) == 0.7
    assert dp._believed(SimpleNamespace(value_arm_entries=[])) is None
