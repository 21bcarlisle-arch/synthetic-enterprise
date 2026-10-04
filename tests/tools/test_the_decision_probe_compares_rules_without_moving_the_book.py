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


def test_a_decision_is_charged_only_the_bad_debt_of_the_term_it_priced():
    """Defect it names: a LIFETIME bad-debt share charged a 2017 renewal with arrears the household
    ran up years later, which no rule could have priced (PROS-2016-0098). The first term here is
    clean and the second goes bad; only the second decision may carry the loss."""
    # The second decision comes BEFORE a year is up, so "until the next decision" and "a year"
    # disagree: a window that ignored the next decision would pull the bad bills into the first.
    rows = [_row(customer_id="A", term_start="2017-03-31"),
            _row(customer_id="A", term_start="2017-12-31")]
    bills = [{"customer_id": "A", "commodity": "electricity", "period_end": f"2017-{m:02d}-28",
              "total_amount_gbp": 100.0} for m in range(4, 13)]
    bills += [{"customer_id": "A", "commodity": "electricity", "period_end": f"2018-{m:02d}-28",
               "total_amount_gbp": 100.0} for m in range(1, 13)]
    write_offs = {("A", f"2018-{m:02d}-28", "electricity"): {"amount_gbp": 50.0}
                  for m in range(1, 13)}
    dp.term_bad_debt_shares(rows, bills, write_offs)
    assert rows[0]["term_bad_debt_share"] == 0.0
    assert rows[1]["term_bad_debt_share"] == 0.5
    # AND A TERM IS ONE YEAR when the leg's next decision is years away: a fix priced in 2017
    # may not carry arrears from 2019 just because no decision came between.
    far = [_row(customer_id="B", term_start="2017-03-31"),
           _row(customer_id="B", term_start="2021-03-30")]
    far_bills = [{"customer_id": "B", "commodity": "electricity", "period_end": f"{y}-06-28",
                  "total_amount_gbp": 100.0} for y in (2017, 2019)]
    far_offs = {("B", "2019-06-28", "electricity"): {"amount_gbp": 100.0}}
    dp.term_bad_debt_shares(far, far_bills, far_offs)
    assert far[0]["term_bad_debt_share"] == 0.0 and len(far[0]["term_bills"]) == 1
    lifetime = {**rows[0], "true_bad_debt_share": 0.25}
    assert dp.expected_term_margin_gbp(lifetime, "value") > dp.expected_term_margin_gbp(
        lifetime, "value", bad_debt_basis="lifetime")


def _ex_ante_book():
    """A 2016 decision that prefers level 30, a 2017 one that strongly prefers 20 but has not
    CLOSED by 2018-01-01, and the 2018 decision being priced."""
    prefers_20 = {"20": {"offer": 220.0, "p": 0.9, "believed": 0.1},
                  "30": {"offer": 230.0, "p": 0.1, "believed": 0.9}}
    return [_row(term_start="2016-06-01"),
            _row(billing_account="B", customer_id="B", term_start="2017-06-01",
                 level_grid=prefers_20),
            _row(billing_account="C", customer_id="C", term_start="2018-03-01")]


def test_a_flat_level_set_in_advance_reads_only_the_decisions_closed_before_its_year():
    """The 2017 decision's term runs into 2018, so 2018's level cannot have seen it; 2016 has no
    closed book at all. Both branches are reachable on one book: a year with no book and a year
    with one."""
    levels = dp.ex_ante_levels(_ex_ante_book())
    assert levels[2016] is None and levels[2017] is None and levels[2018] is not None
    assert levels[2018] == 30.0
    # With the open 2017 decision counted, the level would have been 20: the look-ahead it refuses.
    assert dp.best_level(_ex_ante_book()[:2]) == 20.0


def test_the_runnable_chooser_scores_the_book_on_the_companys_belief_not_the_worlds():
    book = _ex_ante_book()[1:2]
    assert dp.best_level(book) == 20.0 and dp.best_level(book, p_key="believed") == 30.0
    # A decision the arm formed no belief on teaches the belief chooser nothing, and does not crash.
    blind = _row(level_grid={"20": {"offer": 220.0, "p": 0.9, "believed": None},
                             "30": {"offer": 230.0, "p": 0.1, "believed": None}})
    assert dp.best_level(book + [blind], p_key="believed") == 30.0


def test_the_ex_ante_score_drops_the_book_less_years_and_scores_the_rest_at_their_own_level():
    out = dp.ex_ante_scores(_ex_ante_book(), a="value")
    assert out["decisions_unscored_no_book"] == 2 and out["vs_ex_ante"]["decisions"] == 1
    assert out["hindsight_level"] == 30.0
    # The 2018 decision at level 30: value (230, p 0.8) against 230 at p 0.7 is 0.1 x 30 x 3.
    assert abs(out["vs_ex_ante"]["total_gbp"] - 9.0) < 1e-6
